# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Build research/publication/artifact_manifest.json (11.5, M4).

Maps every quantitative table, figure and claim of the manuscript, the
supplementary file and the experiment reports to its experiment id, run ids,
metric definition, result path, generator script, config or protocol hash and
code revision. Hashes and revisions are read from the committed files, not typed.
Claims are taken from research/claims_register.csv.

Usage: .venv/bin/python scripts/build_artifact_manifest.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = json.loads((ROOT / "research/freeze.json").read_text())

METRICS = {
    "f_test": "F_test = mean food items consumed per 100-step episode over the 200 fixed confirmatory test environments (items per episode)",
    "paired": "paired difference per run seed of F_test (treatment minus comparator); mean with 95 percent percentile bootstrap CI over run seeds, 10,000 resamples, seed 0; d_z; Wilcoxon signed-rank (robustness)",
    "summary": "per-arm mean, SD, min and max over 30 run seeds of F_test, F_train_fresh, F_shift, generalisation gap, adaptation AUC, best training fitness, F_train_fixed, overfit_drop, diversity and stay fraction",
    "adaptation": "best-so-far training fitness (mean of K training episodes) against evaluations",
    "sensitivity": "EXPLORATORY: Bonferroni-level and Student t intervals, leave-one-seed-out readings, K1 without seed 13, elite re-evaluation counts",
}


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def exp_info(exp: str) -> dict:
    a = json.loads((ROOT / f"results/confirmatory/{exp}/analysis/analysis.json").read_text())
    return {
        "protocol_sha256": FREEZE["files"][f"research/experiments/{exp}/protocol.md"],
        "config_canonical_hash": FREEZE["experiments"][exp]["config_canonical_hash"],
        "code_revision": a["code_revision"],
        "run_ids": f"{exp}.<condition>.<arm>.s0000-s0029 ({a['n_runs']} runs)",
    }


def entry(aid, kind, exp, run_ids, metric, path, gen, used_in, info=None):
    info = info or exp_info(exp)
    return {
        "artifact_id": aid, "kind": kind, "experiment_id": exp, "run_ids": run_ids or info["run_ids"],
        "metric_definition": metric, "result_path": path, "result_sha256": sha(path.split(" ")[0]),
        "generator_script": gen, "config_or_protocol_hash": {
            "config_canonical_hash": info["config_canonical_hash"],
            "experiment_protocol_sha256": info["protocol_sha256"],
            "main_protocol_sha256": FREEZE["files"]["research/protocol.md"]},
        "code_revision": info["code_revision"], "used_in": used_in,
    }


def main() -> None:
    arts = []
    rep = "src/evolve/report.py via `evolve report --results results/confirmatory/{e}`"
    ana = "scripts/analyse_frozen.py {e}"
    for e in ("EXP-001", "EXP-002", "EXP-003"):
        base = f"results/confirmatory/{e}"
        arts += [
            entry(f"{e}/TAB-1", "table", e, None, METRICS["summary"], f"{base}/report/summary.csv", rep.format(e=e),
                  [f"research/experiments/{e}/report.md section 8"]),
            entry(f"{e}/TAB-2", "table", e, None, METRICS["paired"], f"{base}/analysis/analysis.json", ana.format(e=e),
                  [f"research/experiments/{e}/report.md section 8"]),
            entry(f"{e}/FIG-1", "figure", e, None, METRICS["f_test"] + " per run seed (strip plot)",
                  f"{base}/report/figures/FIG-1_f_test_by_arm.svg", rep.format(e=e),
                  [f"research/experiments/{e}/report.md (copy in figures/)"]),
            entry(f"{e}/FIG-2", "figure", e, None, METRICS["adaptation"],
                  f"{base}/report/figures/FIG-2_adaptation.svg", rep.format(e=e),
                  [f"research/experiments/{e}/report.md (copy in figures/)"]),
            entry(f"{e}/FIG-3", "figure", e, None, METRICS["paired"],
                  f"{base}/analysis/FIG-3_paired_differences.svg", ana.format(e=e),
                  [f"research/experiments/{e}/report.md (copy in figures/)"]),
            entry(f"{e}/per-run-metrics", "table", e, None, "per-run metrics of every arm and seed",
                  f"{base}/report/metrics.csv", rep.format(e=e),
                  [f"research/experiments/{e}/metrics.csv (byte-identical copy)", "supplementary S2"]),
        ]
    m = "research/paper/manuscript.md"
    arts += [
        entry("MS/Table-1", "table", "EXP-001", None, METRICS["summary"], "results/confirmatory/EXP-001/report/summary.csv",
              rep.format(e="EXP-001"), [m + " section 5.1"]),
        entry("MS/Table-2", "table", "EXP-001", "EXP-001.main.{RS,NOSEL,EVO}.s0000-s0029", METRICS["paired"],
              "results/confirmatory/EXP-001/analysis/analysis.json", ana.format(e="EXP-001"), [m + " section 5.1"]),
        entry("MS/Figure-1", "figure", "EXP-001", None, METRICS["paired"],
              "results/confirmatory/EXP-001/analysis/FIG-3_paired_differences.svg", ana.format(e="EXP-001"), [m + " section 5.1"]),
        entry("MS/Table-3", "table", "EXP-002", None, METRICS["paired"] + "; arm means from summary.csv",
              "results/confirmatory/EXP-002/analysis/analysis.json", ana.format(e="EXP-002"), [m + " section 5.2"]),
        entry("MS/Figure-2", "figure", "EXP-002", None, METRICS["paired"],
              "results/confirmatory/EXP-002/analysis/FIG-3_paired_differences.svg", ana.format(e="EXP-002"), [m + " section 5.2"]),
        entry("MS/Table-4", "table", "EXP-003", None, METRICS["paired"] + "; arm means from summary.csv; E2000 row from EXP-001",
              "results/confirmatory/EXP-003/analysis/analysis.json", ana.format(e="EXP-003"), [m + " section 5.3"]),
        entry("MS/Figure-3", "figure", "EXP-003", None, METRICS["paired"],
              "results/confirmatory/EXP-003/analysis/FIG-3_paired_differences.svg", ana.format(e="EXP-003"), [m + " section 5.3"]),
        entry("MS/Table-5", "table", "EXP-001;EXP-002;EXP-003", "all registered contrasts", METRICS["paired"],
              "results/confirmatory/EXP-001/analysis/analysis.json (and EXP-002, EXP-003)", "scripts/analyse_frozen.py",
              [m + " section 6"], exp_info("EXP-001") | {"config_canonical_hash": {e: FREEZE["experiments"][e]["config_canonical_hash"] for e in FREEZE["experiments"]}}),
        entry("SUP/S4", "table (exploratory)", "EXP-001;EXP-002;EXP-003", "registered F_test contrasts of all three experiments",
              METRICS["sensitivity"], "results/exploratory/m4-sensitivity-2026-11-25/sensitivity.json", "scripts/m4_sensitivity.py",
              ["research/paper/supplementary.md S4", m + " section 5.5", "EXP-002 and EXP-003 reports section 9"],
              exp_info("EXP-001") | {"config_canonical_hash": {e: FREEZE["experiments"][e]["config_canonical_hash"] for e in FREEZE["experiments"]}}),
    ]
    claims = []
    for r in csv.DictReader(open(ROOT / "research/claims_register.csv")):
        claims.append({k: r[k] for k in ("claim_id", "type", "result_id", "config_hash", "figure_or_table", "section",
                                          "evidence_path_or_source", "status")})
    rev = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {
        "schema_version": "1.0",
        "updated": "2026-11-25",
        "status": "M4: every table, figure and claim of the manuscript, supplementary file and experiment reports is mapped",
        "generator": "scripts/build_artifact_manifest.py",
        "repository_head_when_built": rev,
        "number_audit": "research/publication/number_audit.json (scripts/audit_numbers.py)",
        "fields_per_entry": ["artifact_id", "kind", "experiment_id", "run_ids", "metric_definition", "result_path",
                             "result_sha256", "generator_script", "config_or_protocol_hash", "code_revision", "used_in"],
        "artifacts": arts,
        "claims": claims,
    }
    (ROOT / "research/publication/artifact_manifest.json").write_text(json.dumps(out, indent=1) + "\n")
    print(len(arts), "artifacts;", len(claims), "claims")


if __name__ == "__main__":
    main()
