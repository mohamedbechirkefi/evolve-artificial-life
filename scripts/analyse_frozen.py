# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Frozen analysis of a confirmatory experiment (protocol v1.0, B.2, B.7, B.8, B.10).

Written before any confirmatory output existed (M3, 2026-11-25). It only calls the
frozen statistics in `evolve.stats` (paired percentile bootstrap over run seeds,
d_z, Wilcoxon signed-rank as robustness) with the frozen resamples and analysis
seed of the config, and applies the frozen decision rules:

- supported:    lower bound of the 95 percent interval above 0;
- contradicted: upper bound at or below 0;
- inconclusive: the interval contains 0 (never read as equivalence).

Contrasts are oriented as the protocols state them (EVO minus comparator).
Estimands named by the protocols are labelled "registered"; everything else is
labelled "secondary, descriptive" (B.7: estimate with interval, no claim).

Outputs (all regenerated from the raw run files):
  results/confirmatory/EXP-NNN/analysis/analysis.json
  results/confirmatory/EXP-NNN/analysis/FIG-3_paired_differences.{png,svg}
  results/confirmatory/EXP-NNN/sha256_manifest.json
  research/experiments/EXP-NNN/{config.json, metrics.csv, run_manifest.json, figures/}

Usage: .venv/bin/python scripts/analyse_frozen.py EXP-001 [EXP-002 ...]
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evolve.manifest import environment_info, utc_now  # noqa: E402
from evolve.report import load_results  # noqa: E402
from evolve.stats import paired_bootstrap, wilcoxon_signed_rank  # noqa: E402

GENERATOR = "scripts/analyse_frozen.py"

# (condition, treatment, comparator, metric, role, hypothesis label)
PLAN: dict[str, list[tuple[str, str, str, str, str, str]]] = {
    "EXP-001": [
        ("main", "EVO", "RS", "f_test", "registered primary", "H1 (B.2): delta > 0"),
        ("main", "EVO", "NOSEL", "f_test", "registered secondary", "competing explanation (a), B.10 item 3"),
        ("main", "NOSEL", "RS", "f_test", "registered secondary", "predeclared expectation: NOSEL below RS (C.3)"),
        ("main", "EVO", "RS", "f_shift", "secondary, descriptive", "B.5 item 3"),
        ("main", "EVO", "RS", "generalisation_gap", "secondary, descriptive", "B.5 item 2"),
        ("main", "EVO", "RS", "adaptation_auc", "secondary, descriptive", "B.5 item 1"),
    ],
    "EXP-002": [
        ("main", "EVO", "SELONLY", "f_test", "registered secondary", "H1a: EVO > SELONLY"),
        ("main", "EVO", "NOSEL", "f_test", "registered secondary", "H1b: EVO > NOSEL"),
        ("main", "EVO", "EVO-sigma0.02", "f_test", "registered secondary", "estimand (sigma sweep)"),
        ("main", "EVO", "EVO-sigma0.5", "f_test", "registered secondary", "estimand (sigma sweep)"),
    ],
    "EXP-003": [
        ("E500", "EVO", "RS", "f_test", "registered", "H1 (robustness): E = 500"),
        ("E8000", "EVO", "RS", "f_test", "registered", "H1 (robustness): E = 8000"),
        ("K1", "EVO", "RS", "f_test", "registered", "H1 (robustness): K = 1"),
        ("K1", "EVO", "RS", "overfit_drop", "registered secondary", "overfitting measure (B.5 item 6, B.10 item 2)"),
        ("K1", "EVO", "RS", "f_train_fixed", "secondary, descriptive", "B.10 item 2: training-fitness side"),
        ("K1", "EVO", "RS", "generalisation_gap", "secondary, descriptive", "B.5 item 2 (not the K = 1 overfitting measure)"),
        ("E500", "EVO", "RS", "f_shift", "secondary, descriptive", "B.5 item 3"),
        ("E8000", "EVO", "RS", "f_shift", "secondary, descriptive", "B.5 item 3"),
        ("K1", "EVO", "RS", "f_shift", "secondary, descriptive", "B.5 item 3"),
    ],
}

# Contrasts whose verdict the frozen rule decides (others are estimates only).
DECIDED = {"registered primary", "registered"}


def verdict(lo: float, hi: float) -> str:
    if lo > 0:
        return "supported"
    if hi <= 0:
        return "contradicted"
    return "inconclusive"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def contrast(by: dict, cond: str, a: str, b: str, metric: str, resamples: int, seed: int, worst: dict) -> dict:
    va, vb = by[(cond, a)], by[(cond, b)]
    common = sorted(s for s in set(va) & set(vb) if va[s] is not None and vb[s] is not None)
    row = {"condition": cond, "contrast": f"{a} - {b}", "metric": metric, "n_pairs": len(common), "seeds": common}
    if len(common) < 2:
        row["note"] = "fewer than two complete pairs"
        return row
    d = np.array([va[s] - vb[s] for s in common], dtype=float)
    est = paired_bootstrap(d, resamples=resamples, seed=seed)
    wx = wilcoxon_signed_rank(d)
    row.update({
        "mean_diff": est.mean, "ci_low": est.ci_low, "ci_high": est.ci_high, "sd_diff": est.sd,
        "dz": est.dz, "dz_ci_low": est.dz_ci_low, "dz_ci_high": est.dz_ci_high,
        "wilcoxon_w_plus": wx.w_plus, "wilcoxon_z": wx.z, "wilcoxon_p": wx.p_two_sided, "wilcoxon_n_nonzero": wx.n_nonzero,
        "mean_a": float(np.mean([va[s] for s in common])), "mean_b": float(np.mean([vb[s] for s in common])),
        "n_positive": int((d > 0).sum()), "n_negative": int((d < 0).sum()), "n_zero": int((d == 0).sum()),
        "diffs": [float(x) for x in d],
    })
    # B.8 worst-value sensitivity: only when a run of either arm failed.
    if worst.get((cond, a)) or worst.get((cond, b)):
        row["worst_value_sensitivity"] = worst_value(by, worst, cond, a, b, metric, resamples, seed)
    return row


def worst_value(by, worst, cond, a, b, metric, resamples, seed) -> dict:
    va, vb = dict(by[(cond, a)]), dict(by[(cond, b)])
    for arm, v in ((a, va), (b, vb)):
        obs = [x for x in v.values() if x is not None]
        # "worst observed value of its arm": the minimum for fitness-type metrics.
        fill = min(obs) if obs else None
        for s in worst.get((cond, arm), []):
            v[s] = fill
    common = sorted(s for s in set(va) & set(vb) if va[s] is not None and vb[s] is not None)
    d = np.array([va[s] - vb[s] for s in common], dtype=float)
    est = paired_bootstrap(d, resamples=resamples, seed=seed)
    return {"n_pairs": len(common), "mean_diff": est.mean, "ci_low": est.ci_low, "ci_high": est.ci_high,
            "rule": "failed run assigned the worst (minimum) observed value of its arm (B.8)"}


def figure(rows: list[dict], path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [r for r in rows if "mean_diff" in r]
    fig, ax = plt.subplots(figsize=(7.5, 0.75 * len(rows) + 1.6))
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i
        d = np.array(r["diffs"])
        ax.scatter(d, np.full(d.size, y) + np.linspace(-0.18, 0.18, d.size), s=10, color="0.55", zorder=2)
        ax.hlines(y, r["ci_low"], r["ci_high"], color="black", lw=2.4, zorder=3)
        ax.plot(r["mean_diff"], y, "o", color="tab:red", ms=7, zorder=4)
    ax.axvline(0, color="0.3", lw=1, ls="--")
    ax.set_yticks(range(len(rows)), [f"{r['condition']}: {r['contrast']}\n{r['metric']} (n={r['n_pairs']})" for r in reversed(rows)], fontsize=8)
    ax.set_xlabel("paired difference per run seed (items per episode)")
    ax.set_title(title, fontsize=10)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path.with_suffix(".png"), dpi=150)
    fig.savefig(path.with_suffix(".svg"))
    plt.close(fig)


def analyse(exp: str) -> dict:
    res = ROOT / "results" / "confirmatory" / exp
    docs = load_results(res)
    cfg = json.loads((res / "config.json").read_text())
    if cfg.get("label") != "confirmatory" or {d["label"] for d in docs} != {"confirmatory"}:
        raise SystemExit(f"{exp}: not a confirmatory result set")
    resamples, aseed = int(cfg["bootstrap_resamples"]), int(cfg["analysis_seed"])

    by: dict = defaultdict(dict)
    worst: dict = defaultdict(list)
    status_counts: dict = defaultdict(lambda: {"ok": 0, "failed": 0, "retried": 0})
    for d in docs:
        key = (d["condition"], d["arm"])
        status_counts[f"{d['condition']}/{d['arm']}"][d["status"]] += 1
        if d["manifest"]["attempts"] > 1:
            status_counts[f"{d['condition']}/{d['arm']}"]["retried"] += 1
        if d["status"] != "ok":
            worst[key].append(d["run_seed"])
    for d in docs:
        if d["status"] == "ok":
            for m in ("f_test", "f_shift", "generalisation_gap", "adaptation_auc", "f_train_fixed", "overfit_drop", "f_train_fresh"):
                by[(d["condition"], d["arm"], m)][d["run_seed"]] = d["metrics"].get(m)

    rows = []
    for cond, a, b, metric, role, hyp in PLAN[exp]:
        sub = {(cond, a): by[(cond, a, metric)], (cond, b): by[(cond, b, metric)]}
        r = contrast(sub, cond, a, b, metric, resamples, aseed, worst)
        r["role"], r["hypothesis"] = role, hyp
        if "mean_diff" in r:
            r["verdict_frozen_rule"] = verdict(r["ci_low"], r["ci_high"]) if role in DECIDED else None
            r["interval_reading"] = verdict(r["ci_low"], r["ci_high"])
        rows.append(r)

    out = res / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    figure(rows, out / "FIG-3_paired_differences", f"{exp}: paired differences, mean (red) and 95% percentile bootstrap CI (black)")

    files = sorted(p for p in res.rglob("*") if p.is_file() and p.name != "sha256_manifest.json")
    manifest = {
        "schema": "evolve.sha256_manifest", "schema_version": "1.0.0", "experiment_id": exp,
        "generated_utc": utc_now(), "generator": GENERATOR,
        "files": {p.relative_to(res).as_posix(): sha256(p) for p in files if "analysis" not in p.parts and "report" not in p.parts},
    }
    analysis = {
        "schema": "evolve.frozen_analysis", "schema_version": "1.0.0", "experiment_id": exp,
        "generated_utc": utc_now(), "generator": GENERATOR, "code_revision": environment_info()["git_revision"],
        "run_revisions": sorted({d["manifest"]["git_revision"] for d in docs}),
        "run_git_dirty": sorted({str(d["manifest"]["git_dirty"]) for d in docs}),
        "config_canonical_hash_runs": sorted({d["config_hash"] for d in docs}),
        "bootstrap_resamples": resamples, "analysis_seed": aseed,
        "decision_rule": "supported if 95% CI lower bound > 0; contradicted if upper bound <= 0; otherwise inconclusive (not equivalence)",
        "n_runs": len(docs), "status_counts": status_counts,
        "failed_runs": sorted(d["run_id"] for d in docs if d["status"] != "ok"),
        "contrasts": rows,
        "figure": "analysis/FIG-3_paired_differences.png",
    }
    (out / "analysis.json").write_text(json.dumps(analysis, indent=1) + "\n", encoding="utf-8")
    (res / "sha256_manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    # Publication tree (master prompt 11.1): copies generated from the raw outputs.
    pub = ROOT / "research" / "experiments" / exp
    (pub / "figures").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(res / "config.json", pub / "config.json")
    if (res / "report" / "metrics.csv").exists():
        shutil.copyfile(res / "report" / "metrics.csv", pub / "metrics.csv")
        for f in sorted((res / "report" / "figures").glob("FIG-*")):
            shutil.copyfile(f, pub / "figures" / f.name)
    for f in sorted(out.glob("FIG-3*")):
        shutil.copyfile(f, pub / "figures" / f.name)
    matrix = json.loads((res / "matrix_manifest.json").read_text())
    prov_path = res / "run_provenance.json"
    run_manifest = {
        "schema": "evolve.experiment_run_manifest", "schema_version": "1.0.0", "experiment_id": exp,
        "generator": GENERATOR, "matrix_manifest": matrix,
        "run_provenance": json.loads(prov_path.read_text()) if prov_path.exists() else None,
        "raw_results": f"results/confirmatory/{exp}/runs/",
        "sha256_manifest": f"results/confirmatory/{exp}/sha256_manifest.json",
        "sha256_manifest_sha256": sha256(res / "sha256_manifest.json"),
    }
    (pub / "run_manifest.json").write_text(json.dumps(run_manifest, indent=1) + "\n", encoding="utf-8")
    return analysis


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    for exp in argv:
        a = analyse(exp)
        for r in a["contrasts"]:
            if "mean_diff" in r:
                print(f"{exp} {r['condition']:6s} {r['contrast']:22s} {r['metric']:18s} n={r['n_pairs']:2d} "
                      f"mean={r['mean_diff']:+.3f} CI=[{r['ci_low']:+.3f}, {r['ci_high']:+.3f}] "
                      f"{r['role']}: {r['verdict_frozen_rule'] or r['interval_reading'] + ' (estimate only)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
