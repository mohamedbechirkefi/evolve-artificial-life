# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""M4 EXPLORATORY sensitivity re-analysis of the committed confirmatory results.

Label: exploratory (M4, 2026-11-25). This script runs no simulation. It re-reads
the committed frozen analyses (`results/confirmatory/EXP-NNN/analysis/analysis.json`)
and the committed raw run files, and computes checks that the frozen plan did not
prescribe. Nothing here changes or replaces a frozen verdict; the verdicts of
record are those in the frozen `analysis.json` files.

Checks:
  1. Multiplicity: percentile bootstrap intervals at Bonferroni-adjusted levels
     for the registered F_test contrasts of EXP-002 (family of 4) and EXP-003
     (family of 3), same resamples and seed as the frozen analysis.
  2. Interval method: Student t 95 percent interval on the paired differences
     (df = n - 1), for every registered F_test contrast.
  3. Influence: range of the mean paired difference over leave-one-seed-out
     subsets, and the count of subsets whose 95 percent bootstrap interval would
     give a different reading from the frozen one.
  4. EXP-003 K1 without seed 13 (the only seed where both returned policies
     scored 0 on the test set).
  5. EXP-002 competing explanation (elite re-evaluation): share of the budget
     spent on elite re-evaluations and how often the returned policy of each
     population arm is an elite re-evaluation (descriptive).

Output: results/exploratory/m4-sensitivity-2026-11-25/sensitivity.json
Usage:  .venv/bin/python scripts/m4_sensitivity.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evolve.manifest import environment_info, utc_now  # noqa: E402
from evolve.stats import paired_bootstrap  # noqa: E402

OUT = ROOT / "results" / "exploratory" / "m4-sensitivity-2026-11-25"
RESAMPLES = 10_000
SEED = 0
# Two-sided Student t quantiles at 0.975 (tabulated; scipy is not a dependency).
T975 = {28: 2.048407, 29: 2.045230}

REGISTERED_FTEST = {
    "EXP-001": [("main", "EVO - RS")],
    "EXP-002": [("main", "EVO - SELONLY"), ("main", "EVO - NOSEL"),
                ("main", "EVO - EVO-sigma0.02"), ("main", "EVO - EVO-sigma0.5")],
    "EXP-003": [("E500", "EVO - RS"), ("E8000", "EVO - RS"), ("K1", "EVO - RS")],
}


def reading(lo: float, hi: float) -> str:
    if lo > 0:
        return "interval above 0"
    if hi <= 0:
        return "interval at or below 0"
    return "interval contains 0"


def find(contrasts: list[dict], condition: str, name: str) -> dict:
    for c in contrasts:
        if c["condition"] == condition and c["contrast"] == name and c["metric"] == "f_test":
            return c
    raise KeyError((condition, name))


def t_interval(d: np.ndarray) -> tuple[float, float]:
    n = d.size
    half = T975[n - 1] * d.std(ddof=1) / np.sqrt(n)
    return float(d.mean() - half), float(d.mean() + half)


def contrast_checks(exp: str, analysis: dict) -> list[dict]:
    family = REGISTERED_FTEST[exp]
    k = len(family)
    level = 1 - 0.05 / k
    rows = []
    for condition, name in family:
        c = find(analysis["contrasts"], condition, name)
        d = np.asarray(c["diffs"], dtype=float)
        frozen = reading(c["ci_low"], c["ci_high"])
        adj = paired_bootstrap(d, RESAMPLES, SEED, level)
        tlo, thi = t_interval(d)
        loo_means, loo_changed = [], 0
        for i in range(d.size):
            sub = np.delete(d, i)
            est = paired_bootstrap(sub, RESAMPLES, SEED, 0.95)
            loo_means.append(float(sub.mean()))
            if reading(est.ci_low, est.ci_high) != frozen:
                loo_changed += 1
        rows.append({
            "experiment_id": exp, "condition": condition, "contrast": name, "metric": "f_test",
            "n_pairs": int(d.size), "mean_diff": float(d.mean()),
            "frozen_ci_95": [c["ci_low"], c["ci_high"]], "frozen_reading": frozen,
            "frozen_verdict_of_record": c["verdict_frozen_rule"],
            "family_size": k, "bonferroni_level": level,
            "bonferroni_ci": [adj.ci_low, adj.ci_high],
            "bonferroni_reading": reading(adj.ci_low, adj.ci_high),
            "t_ci_95": [tlo, thi], "t_reading": reading(tlo, thi),
            "leave_one_out_mean_range": [min(loo_means), max(loo_means)],
            "leave_one_out_subsets_with_changed_reading": loo_changed,
        })
    return rows


def k1_without_seed13(analysis: dict) -> dict:
    c = find(analysis["contrasts"], "K1", "EVO - RS")
    seeds = list(c["seeds"])
    d = np.asarray(c["diffs"], dtype=float)
    keep = np.array([s != 13 for s in seeds])
    est = paired_bootstrap(d[keep], RESAMPLES, SEED, 0.95)
    return {"condition": "K1", "contrast": "EVO - RS", "metric": "f_test", "excluded_seed": 13,
            "diff_at_seed_13": float(d[~keep][0]), "n_pairs": est.n, "mean_diff": est.mean,
            "ci_95": [est.ci_low, est.ci_high], "reading": reading(est.ci_low, est.ci_high)}


def elite_audit() -> list[dict]:
    rows = []
    runs = sorted((ROOT / "results/confirmatory/EXP-002/runs").glob("*.json"))
    by_arm: dict[str, list[dict]] = {}
    for p in runs:
        r = json.loads(p.read_text())
        if r["config"]["arm"].get("kind") != "population":
            continue
        by_arm.setdefault(r["arm"], []).append(r)
    for arm, rs in sorted(by_arm.items()):
        spec = rs[0]["config"]["arm"]
        p, g, el = spec["population_size"], spec["generations"], spec.get("elitism", 0)
        elite_ids = {gen * p + j for gen in range(1, g) for j in range(el)}
        returned_elite = sum(1 for r in rs if r["trace"]["returned_index"] in elite_ids)
        rows.append({"experiment_id": "EXP-002", "arm": arm, "n_runs": len(rs),
                     "elite_reevaluations_per_run": len(elite_ids),
                     "evaluations_per_run": int(rs[0]["metrics"]["n_evaluations"]),
                     "elite_share_of_budget": len(elite_ids) / rs[0]["metrics"]["n_evaluations"],
                     "runs_whose_returned_policy_is_an_elite_reevaluation": returned_elite})
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    analyses = {e: json.loads((ROOT / f"results/confirmatory/{e}/analysis/analysis.json").read_text())
                for e in REGISTERED_FTEST}
    rows = []
    for e, a in analyses.items():
        rows += contrast_checks(e, a)
    out = {
        "schema": "evolve.m4_sensitivity", "schema_version": "1.0.0",
        "label": "exploratory (M4); does not change or replace any frozen verdict",
        "generated_utc": utc_now(), "generator": "scripts/m4_sensitivity.py",
        "inputs": [f"results/confirmatory/{e}/analysis/analysis.json" for e in analyses]
                  + ["results/confirmatory/EXP-002/runs/*.json"],
        "input_code_revisions": sorted({a["code_revision"] for a in analyses.values()}),
        "bootstrap_resamples": RESAMPLES, "bootstrap_seed": SEED,
        "environment": environment_info(),
        "contrast_checks": rows,
        "k1_without_seed_13": k1_without_seed13(analyses["EXP-003"]),
        "elite_audit": elite_audit(),
    }
    (OUT / "sensitivity.json").write_text(json.dumps(out, indent=1) + "\n")
    for r in rows:
        print(f"{r['experiment_id']} {r['condition']} {r['contrast']}: mean {r['mean_diff']:.3f} "
              f"frozen {r['frozen_ci_95'][0]:.3f},{r['frozen_ci_95'][1]:.3f} | "
              f"bonf({r['bonferroni_level']:.4f}) {r['bonferroni_ci'][0]:.3f},{r['bonferroni_ci'][1]:.3f} "
              f"{r['bonferroni_reading']} | t {r['t_ci_95'][0]:.3f},{r['t_ci_95'][1]:.3f} | "
              f"LOO {r['leave_one_out_mean_range'][0]:.3f}..{r['leave_one_out_mean_range'][1]:.3f} "
              f"changed {r['leave_one_out_subsets_with_changed_reading']}")
    print(json.dumps(out["k1_without_seed_13"]))
    for r in out["elite_audit"]:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
