# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Experiment runner: one run, and a matrix of runs, with provenance.

A run is (experiment, condition, arm, run seed). Its result document is
validated against the versioned schema before it is written. A run that
raises is retried once with the same seed (protocol B.8); a second failure is
recorded as a failed run, never dropped silently.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import seeds
from .config import ArmSpec, Condition, EnvParams, ExperimentConfig, config_hash, run_config_dict
from .env import Layout, generate_layout, simulate_batch, stack_layouts
from .errors import EvolveError
from .manifest import environment_info, peak_rss_bytes, utc_now
from .metrics import adaptation_auc, behavioural_diversity, episode_fitness_mean, genotypic_diversity
from .schema import SCHEMA_NAME, SCHEMA_VERSION, dump_result, validate_manifest
from .search import SearchTrace, population_search, random_search


def run_id(experiment_id: str, condition: str, arm: str, run_seed: int) -> str:
    return f"{experiment_id}.{condition}.{arm}.s{run_seed:04d}"


class LayoutCache:
    """Lazily generated layouts, keyed by (kind, index)."""

    def __init__(self, cfg: ExperimentConfig, run_seed: int):
        self.cfg = cfg
        self.run_seed = run_seed
        self._cache: dict[tuple[str, int], Layout] = {}

    def get(self, kind: str, index: int) -> Layout:
        key = (kind, int(index))
        lay = self._cache.get(key)
        if lay is None:
            c = self.cfg
            if kind == "train":
                lay = generate_layout(c.env, seeds.train_env_seq(c.root_seed, self.run_seed, index))
            elif kind == "fresh":
                lay = generate_layout(c.env, seeds.fresh_env_seq(c.root_seed, self.run_seed, index))
            elif kind == "probe":
                lay = generate_layout(c.env, seeds.probe_env_seq(c.root_seed, self.run_seed, index))
            elif kind == "test":
                lay = generate_layout(c.env, seeds.test_env_seq(c.root_seed, c.test_pool, index))
            elif kind == "shift":
                lay = generate_layout(c.shift_env, seeds.shift_env_seq(c.root_seed, c.test_pool, index))
            else:
                raise EvolveError(f"unknown layout kind {kind!r}")
            self._cache[key] = lay
        return lay

    def many(self, kind: str, indices) -> list[Layout]:
        return [self.get(kind, i) for i in indices]


def train_env_indices(eval_ids: np.ndarray, k: int, fixed: bool) -> np.ndarray:
    """Training environment index of each (evaluation, episode) pair, evaluation-major.

    Resampled design: evaluation i uses environments i*K .. i*K + K - 1, so every
    arm of a run seed sees the same environments at the same evaluation index.
    Fixed design (K = 1 in EXP-003): every evaluation uses environment 0.
    """
    eval_ids = np.asarray(eval_ids, dtype=np.int64)
    if fixed:
        return np.zeros(eval_ids.size * k, dtype=np.int64)
    return (eval_ids[:, None] * k + np.arange(k)[None, :]).ravel()


def make_evaluator(cache: LayoutCache, env: EnvParams, k: int, fixed: bool, hidden: int):
    def evaluate(thetas: np.ndarray, eval_ids: np.ndarray) -> np.ndarray:
        idx = train_env_indices(eval_ids, k, fixed)
        food, headings = stack_layouts(cache.many("train", idx))
        res = simulate_batch(np.repeat(thetas, k, axis=0), food, headings, env.episode_steps, hidden)
        return episode_fitness_mean(res.eaten, k)

    return evaluate


def _score(theta: np.ndarray, layouts: list[Layout], steps: int, hidden: int):
    food, headings = stack_layouts(layouts)
    return simulate_batch(np.repeat(theta[None, :], len(layouts), axis=0), food, headings, steps, hidden)


def search_for(cfg: ExperimentConfig, condition: Condition, arm: ArmSpec, run_seed: int, cache: LayoutCache) -> SearchTrace:
    ev = condition.evaluation
    evaluate = make_evaluator(cache, cfg.env, ev.train_episodes_per_eval, ev.train_fixed, cfg.policy.hidden_units)
    init = seeds.init_rng(cfg.root_seed, run_seed)
    if arm.kind == "random_search":
        return random_search(arm, cfg.policy, init, evaluate)
    return population_search(
        arm, cfg.policy, init, seeds.parent_rng(cfg.root_seed, run_seed), seeds.noise_rng(cfg.root_seed, run_seed), evaluate
    )


def _compute(cfg: ExperimentConfig, condition: Condition, arm: ArmSpec, run_seed: int) -> dict:
    cache = LayoutCache(cfg, run_seed)
    ev = condition.evaluation
    h = cfg.policy.hidden_units
    steps = cfg.env.episode_steps
    trace = search_for(cfg, condition, arm, run_seed, cache)
    theta = trace.thetas[trace.returned_index]

    test = _score(theta, cache.many("test", range(ev.n_test)), steps, h)
    shift = _score(theta, cache.many("shift", range(ev.n_shift)), steps, h)
    fresh = _score(theta, cache.many("fresh", range(ev.n_train_fresh)), steps, h)

    pop = trace.thetas[trace.final_population]
    probe_layouts = cache.many("probe", range(ev.n_probe))
    food, headings = stack_layouts(probe_layouts)
    p = pop.shape[0]
    probe = simulate_batch(
        np.repeat(pop, ev.n_probe, axis=0), np.tile(food, (p, 1, 1)), np.tile(headings, p), steps, h, record_actions=True
    )
    actions = probe.actions.reshape(p, ev.n_probe, steps)

    total_steps = ev.n_test * steps
    stay = float(test.n_stay.sum() / total_steps)
    turn = float(test.n_turn.sum() / total_steps)
    f_test = float(test.eaten.mean())
    f_fresh = float(fresh.eaten.mean())
    return {
        "metrics": {
            "f_test": f_test,
            "f_train_fresh": f_fresh,
            "f_shift": float(shift.eaten.mean()),
            "generalisation_gap": f_fresh - f_test,
            "adaptation_auc": adaptation_auc(trace.train_fitness),
            "best_train_fitness": float(trace.train_fitness[trace.returned_index]),
            "genotypic_diversity": genotypic_diversity(pop),
            "behavioural_diversity": behavioural_diversity(actions),
            "n_evaluations": trace.n_evaluations,
            "exploit": {
                "forward_fraction": max(0.0, 1.0 - stay - turn),
                "stay_fraction": stay,
                "turn_fraction": turn,
                # simulate_batch raises InvariantError if the replay check fails,
                # so reaching this line means it passed for every scored episode.
                "replay_check_passed": True,
            },
        },
        "episodes": {
            "test": [int(x) for x in test.eaten],
            "shift": [int(x) for x in shift.eaten],
            "train_fresh": [int(x) for x in fresh.eaten],
        },
        "trace": {
            "train_fitness": [float(x) for x in trace.train_fitness],
            "parent_index": [int(x) for x in trace.parent_index],
            "returned_index": trace.returned_index,
            "final_population": [int(x) for x in trace.final_population],
        },
    }


def run_one(cfg: ExperimentConfig, condition_name: str, arm_name: str, run_seed: int, rss_note: str = "") -> dict:
    """Execute one run and return its validated result document (not written)."""
    condition = cfg.condition(condition_name)
    arm = condition.arm(arm_name)
    rcfg = run_config_dict(cfg, condition, arm, run_seed)
    chash = config_hash(rcfg)
    rid = run_id(cfg.experiment_id, condition.name, arm.name, run_seed)
    started = utc_now()
    t0, c0 = time.perf_counter(), time.process_time()
    body, failure, attempts = None, None, 0
    for attempts in (1, 2):
        try:
            body = _compute(cfg, condition, arm, run_seed)
            failure = None
            break
        except Exception as exc:  # recorded, retried once, then reported as a failed run
            failure = f"attempt {attempts}: {type(exc).__name__}: {exc}\n{traceback.format_exc(limit=5)}"
    wall, cpu = time.perf_counter() - t0, time.process_time() - c0
    manifest = {
        "schema": "evolve.run_manifest",
        "schema_version": SCHEMA_VERSION,
        "run_id": rid,
        "label": cfg.label,
        "config_hash": chash,
        "root_seed": cfg.root_seed,
        "run_seed": run_seed,
        **environment_info(),
        "started_utc": started,
        "finished_utc": utc_now(),
        "attempts": attempts,
        "wall_seconds": wall,
        "cpu_seconds": cpu,
        "peak_rss_bytes": peak_rss_bytes(),
        "peak_rss_note": rss_note or "process high-water mark (ru_maxrss); includes interpreter and earlier work in the same process",
    }
    validate_manifest(manifest)
    doc = {
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "label": cfg.label,
        "experiment_id": cfg.experiment_id,
        "condition": condition.name,
        "arm": arm.name,
        "run_id": rid,
        "run_seed": run_seed,
        "config": rcfg,
        "config_hash": chash,
        "status": "ok" if body is not None else "failed",
        "failure": failure,
        "metrics": body["metrics"] if body else None,
        "episodes": body["episodes"] if body else None,
        "trace": body["trace"] if body else None,
        "manifest": manifest,
    }
    return doc


@dataclass(frozen=True)
class Task:
    config_raw: dict
    condition: str
    arm: str
    run_seed: int
    out_dir: str


def _worker(task: Task) -> str:
    from .config import parse_config

    cfg = parse_config(task.config_raw)
    doc = run_one(cfg, task.condition, task.arm, task.run_seed,
                  rss_note="fresh worker process per run (max_tasks_per_child=1): ru_maxrss of that process, includes interpreter and numpy import")
    out = Path(task.out_dir)
    path = out / "runs" / f"{doc['run_id']}.json"
    dump_result(doc, path)
    (out / "manifests").mkdir(parents=True, exist_ok=True)
    (out / "manifests" / f"{doc['run_id']}.json").write_text(
        json.dumps(doc["manifest"], indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    return str(path)


def tasks_for(cfg: ExperimentConfig, out_dir: Path) -> list[Task]:
    return [
        Task(cfg.to_dict(), c.name, a.name, s, str(out_dir))
        for c in cfg.conditions
        for a in c.arms
        for s in cfg.run_seeds
    ]


def run_matrix(cfg: ExperimentConfig, out_dir: str | Path, workers: int = 1) -> list[str]:
    """Run every (condition, arm, seed) of a config. workers = 0 runs in-process."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps(cfg.to_dict(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    tasks = tasks_for(cfg, out)
    started = utc_now()
    t0 = time.perf_counter()
    if workers <= 0:
        paths = [_worker(t) for t in tasks]
    else:
        ctx = mp.get_context("spawn")
        with ProcessPoolExecutor(max_workers=workers, mp_context=ctx, max_tasks_per_child=1) as ex:
            paths = list(ex.map(_worker, tasks))
    matrix = {
        "schema": "evolve.matrix_manifest",
        "schema_version": SCHEMA_VERSION,
        "experiment_id": cfg.experiment_id,
        "label": cfg.label,
        "config_hash": config_hash(cfg),
        "n_runs": len(paths),
        "workers": workers,
        "started_utc": started,
        "finished_utc": utc_now(),
        "wall_seconds_total": time.perf_counter() - t0,
        "runs": [Path(p).relative_to(out).as_posix() for p in paths],
        **environment_info(),
    }
    (out / "matrix_manifest.json").write_text(json.dumps(matrix, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return paths
