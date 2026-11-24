# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Validated, hashable experiment configurations.

A configuration is a JSON document. Unknown keys, wrong types and design
violations raise ConfigError. Equal evaluation budgets across the arms of a
condition are enforced here (fair-baseline rule, protocol B.11).
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .errors import ConfigError

LABELS = ("exploratory", "confirmatory")
TEST_POOLS = ("confirmatory", "exploratory")
GENERATORS = ("clustered", "uniform")
ARM_KINDS = ("random_search", "population")
SELECTIONS = ("truncation", "uniform")


def _check_keys(d: dict, allowed: set[str], where: str) -> None:
    if not isinstance(d, dict):
        raise ConfigError(f"{where}: expected an object, got {type(d).__name__}")
    unknown = set(d) - allowed
    if unknown:
        raise ConfigError(f"{where}: unknown keys {sorted(unknown)}")


def _int(v: Any, where: str, lo: int | None = None, hi: int | None = None) -> int:
    if isinstance(v, bool) or not isinstance(v, int):
        raise ConfigError(f"{where}: expected an integer, got {v!r}")
    if lo is not None and v < lo:
        raise ConfigError(f"{where}: {v} < minimum {lo}")
    if hi is not None and v > hi:
        raise ConfigError(f"{where}: {v} > maximum {hi}")
    return v


def _float(v: Any, where: str, lo: float | None = None, hi: float | None = None) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ConfigError(f"{where}: expected a number, got {v!r}")
    v = float(v)
    if not math.isfinite(v):
        raise ConfigError(f"{where}: non-finite value {v}")
    if lo is not None and v < lo:
        raise ConfigError(f"{where}: {v} < minimum {lo}")
    if hi is not None and v > hi:
        raise ConfigError(f"{where}: {v} > maximum {hi}")
    return v


def _choice(v: Any, options: tuple[str, ...], where: str) -> str:
    if v not in options:
        raise ConfigError(f"{where}: {v!r} not in {options}")
    return v


@dataclass(frozen=True)
class EnvParams:
    """Grid world parameters. Units: cells, items, steps."""

    grid_size: int = 16
    n_food: int = 24
    generator: str = "clustered"
    n_clusters: int = 3
    cluster_spread: float = 2.0
    episode_steps: int = 100

    def __post_init__(self) -> None:
        _int(self.grid_size, "env.grid_size", 5, 64)
        _int(self.n_food, "env.n_food", 0)
        if self.n_food > self.grid_size**2 - 1:
            raise ConfigError("env.n_food exceeds the number of non-start cells")
        _choice(self.generator, GENERATORS, "env.generator")
        _int(self.n_clusters, "env.n_clusters", 1)
        _float(self.cluster_spread, "env.cluster_spread", 0.1)
        _int(self.episode_steps, "env.episode_steps", 1, 10_000)

    @classmethod
    def from_dict(cls, d: dict, where: str = "env") -> "EnvParams":
        _check_keys(d, set(cls.__dataclass_fields__), where)
        return cls(**d)


@dataclass(frozen=True)
class PolicyParams:
    hidden_units: int = 8
    init_std: float = 1.0

    def __post_init__(self) -> None:
        _int(self.hidden_units, "policy.hidden_units", 1, 256)
        _float(self.init_std, "policy.init_std", 0.0)
        if self.init_std <= 0:
            raise ConfigError("policy.init_std must be > 0")

    @classmethod
    def from_dict(cls, d: dict) -> "PolicyParams":
        _check_keys(d, set(cls.__dataclass_fields__), "policy")
        return cls(**d)


@dataclass(frozen=True)
class EvalParams:
    """K training episodes per evaluation; M-sized held-out sets."""

    train_episodes_per_eval: int = 5
    train_fixed: bool = False
    n_test: int = 200
    n_shift: int = 200
    n_train_fresh: int = 200
    n_probe: int = 20

    def __post_init__(self) -> None:
        _int(self.train_episodes_per_eval, "evaluation.train_episodes_per_eval", 1, 1000)
        if not isinstance(self.train_fixed, bool):
            raise ConfigError("evaluation.train_fixed: expected a boolean")
        for name in ("n_test", "n_shift", "n_train_fresh", "n_probe"):
            _int(getattr(self, name), f"evaluation.{name}", 1, 100_000)

    @classmethod
    def from_dict(cls, d: dict, where: str = "evaluation") -> "EvalParams":
        _check_keys(d, set(cls.__dataclass_fields__), where)
        return cls(**d)


@dataclass(frozen=True)
class ArmSpec:
    """One search arm.

    random_search: `evaluations` independent draws; `population_size` is the
    chunk size used to match generation 0 of population arms and to define the
    diversity window (last `population_size` samples).
    population: `population_size` x `generations` evaluations.
    """

    name: str
    kind: str
    population_size: int
    evaluations: int | None = None
    generations: int | None = None
    sigma: float | None = None
    selection: str | None = None
    truncation_fraction: float | None = None
    elitism: int | None = None

    def __post_init__(self) -> None:
        w = f"arm {self.name!r}"
        if not isinstance(self.name, str) or not self.name:
            raise ConfigError("arm.name must be a non-empty string")
        _choice(self.kind, ARM_KINDS, f"{w}.kind")
        _int(self.population_size, f"{w}.population_size", 2)
        if self.kind == "random_search":
            _int(self.evaluations, f"{w}.evaluations", 1)
            for k in ("generations", "sigma", "selection", "truncation_fraction", "elitism"):
                if getattr(self, k) is not None:
                    raise ConfigError(f"{w}: random_search does not take {k}")
            if self.evaluations < self.population_size:
                raise ConfigError(f"{w}: evaluations < population_size")
        else:
            _int(self.generations, f"{w}.generations", 1)
            _float(self.sigma, f"{w}.sigma", 0.0)
            _choice(self.selection, SELECTIONS, f"{w}.selection")
            _int(self.elitism, f"{w}.elitism", 0)
            if self.elitism >= self.population_size:
                raise ConfigError(f"{w}: elitism must be < population_size")
            if self.selection == "truncation":
                _float(self.truncation_fraction, f"{w}.truncation_fraction", 0.0, 1.0)
                if self.n_parents < 1:
                    raise ConfigError(f"{w}: truncation keeps no parent")
            elif self.truncation_fraction is not None:
                raise ConfigError(f"{w}: uniform selection does not take truncation_fraction")
            if self.evaluations is not None and self.evaluations != self.total_evaluations:
                raise ConfigError(f"{w}: evaluations must equal population_size * generations")

    @property
    def total_evaluations(self) -> int:
        if self.kind == "random_search":
            return int(self.evaluations)
        return int(self.population_size * self.generations)

    @property
    def n_parents(self) -> int:
        """Number of parents eligible for reproduction in each generation."""
        if self.kind != "population":
            raise ConfigError("n_parents is defined for population arms only")
        if self.selection == "uniform":
            return self.population_size
        return int(round(self.truncation_fraction * self.population_size))

    @classmethod
    def from_dict(cls, d: dict) -> "ArmSpec":
        _check_keys(d, set(cls.__dataclass_fields__), "arm")
        return cls(**d)


@dataclass(frozen=True)
class Condition:
    name: str
    arms: tuple[ArmSpec, ...]
    evaluation: EvalParams

    def __post_init__(self) -> None:
        if not self.arms:
            raise ConfigError(f"condition {self.name!r}: no arms")
        names = [a.name for a in self.arms]
        if len(set(names)) != len(names):
            raise ConfigError(f"condition {self.name!r}: duplicate arm names")
        budgets = {a.total_evaluations for a in self.arms}
        if len(budgets) != 1:
            raise ConfigError(
                f"condition {self.name!r}: unequal evaluation budgets {sorted(budgets)} "
                "(equal evaluations are required across arms)"
            )

    @property
    def evaluations(self) -> int:
        return self.arms[0].total_evaluations

    def arm(self, name: str) -> ArmSpec:
        for a in self.arms:
            if a.name == name:
                return a
        raise ConfigError(f"condition {self.name!r}: no arm {name!r}")


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str
    label: str
    description: str
    root_seed: int
    test_pool: str
    run_seeds: tuple[int, ...]
    env: EnvParams
    shift_env: EnvParams
    policy: PolicyParams
    conditions: tuple[Condition, ...]
    analysis_seed: int = 0
    bootstrap_resamples: int = 10_000
    raw: dict = field(default_factory=dict, compare=False, repr=False)

    def __post_init__(self) -> None:
        _choice(self.label, LABELS, "label")
        _choice(self.test_pool, TEST_POOLS, "test_pool")
        _int(self.root_seed, "root_seed", 0)
        if not self.run_seeds:
            raise ConfigError("run_seeds is empty")
        for s in self.run_seeds:
            _int(s, "run_seeds[]", 0)
        if len(set(self.run_seeds)) != len(self.run_seeds):
            raise ConfigError("run_seeds contains duplicates")
        if self.label == "exploratory" and self.test_pool != "exploratory":
            raise ConfigError(
                "exploratory configs must use the exploratory test pool "
                "(the confirmatory held-out set is never touched before the freeze, D-006)"
            )
        if self.label == "exploratory" and min(self.run_seeds) < 1000:
            raise ConfigError("exploratory configs must use run seeds >= 1000 (D-006)")
        if self.label == "confirmatory" and max(self.run_seeds) >= 1000:
            raise ConfigError("confirmatory run seeds must be < 1000 (D-006)")
        names = [c.name for c in self.conditions]
        if len(set(names)) != len(names):
            raise ConfigError("duplicate condition names")
        _int(self.bootstrap_resamples, "bootstrap_resamples", 100)
        _int(self.analysis_seed, "analysis_seed", 0)

    def condition(self, name: str) -> Condition:
        for c in self.conditions:
            if c.name == name:
                return c
        raise ConfigError(f"no condition {name!r}")

    @property
    def n_runs(self) -> int:
        return sum(len(c.arms) for c in self.conditions) * len(self.run_seeds)

    def to_dict(self) -> dict:
        return copy.deepcopy(self.raw)


_TOP_KEYS = {
    "experiment_id", "label", "description", "root_seed", "test_pool", "run_seeds", "env",
    "shift_env", "policy", "evaluation", "conditions", "analysis_seed", "bootstrap_resamples",
}


def parse_config(d: dict) -> ExperimentConfig:
    """Parse and validate a configuration dictionary."""
    _check_keys(d, _TOP_KEYS, "config")
    for k in ("experiment_id", "label", "root_seed", "test_pool", "run_seeds", "conditions"):
        if k not in d:
            raise ConfigError(f"config: missing key {k!r}")
    env = EnvParams.from_dict(d.get("env", {}))
    shift_env = EnvParams.from_dict(d.get("shift_env", {"generator": "uniform", "n_food": 16}), "shift_env")
    if shift_env.grid_size != env.grid_size or shift_env.episode_steps != env.episode_steps:
        raise ConfigError("shift_env must share grid_size and episode_steps with env")
    policy = PolicyParams.from_dict(d.get("policy", {}))
    base_eval = d.get("evaluation", {})
    _check_keys(base_eval, set(EvalParams.__dataclass_fields__), "evaluation")
    conditions = []
    if not isinstance(d["conditions"], list) or not d["conditions"]:
        raise ConfigError("conditions must be a non-empty list")
    for c in d["conditions"]:
        _check_keys(c, {"name", "arms", "evaluation"}, "condition")
        merged = {**base_eval, **c.get("evaluation", {})}
        ev = EvalParams.from_dict(merged, f"condition {c.get('name')!r}.evaluation")
        if not isinstance(c.get("arms"), list):
            raise ConfigError("condition.arms must be a list")
        arms = tuple(ArmSpec.from_dict(a) for a in c["arms"])
        conditions.append(Condition(name=c["name"], arms=arms, evaluation=ev))
    if not isinstance(d["run_seeds"], list):
        raise ConfigError("run_seeds must be a list")
    return ExperimentConfig(
        experiment_id=str(d["experiment_id"]),
        label=d["label"],
        description=str(d.get("description", "")),
        root_seed=d["root_seed"],
        test_pool=d["test_pool"],
        run_seeds=tuple(d["run_seeds"]),
        env=env,
        shift_env=shift_env,
        policy=policy,
        conditions=tuple(conditions),
        analysis_seed=d.get("analysis_seed", 0),
        bootstrap_resamples=d.get("bootstrap_resamples", 10_000),
        raw=copy.deepcopy(d),
    )


def load_config(path: str | Path) -> ExperimentConfig:
    p = Path(path)
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigError(f"{p}: invalid JSON ({e})") from e
    return parse_config(d)


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def config_hash(obj: Any) -> str:
    """SHA-256 of the canonical JSON form of a configuration (or any JSON value)."""
    if hasattr(obj, "to_dict"):
        obj = obj.to_dict()
    return hashlib.sha256(canonical_json(obj).encode("ascii")).hexdigest()


def run_config_dict(cfg: ExperimentConfig, condition: Condition, arm: ArmSpec, run_seed: int) -> dict:
    """The fully resolved configuration of one run (what its config hash covers)."""
    return {
        "experiment_id": cfg.experiment_id,
        "label": cfg.label,
        "root_seed": cfg.root_seed,
        "test_pool": cfg.test_pool,
        "condition": condition.name,
        "run_seed": run_seed,
        "env": asdict(cfg.env),
        "shift_env": asdict(cfg.shift_env),
        "policy": asdict(cfg.policy),
        "evaluation": asdict(condition.evaluation),
        "arm": {k: v for k, v in asdict(arm).items() if v is not None},
    }
