# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Evidence audit of reported numbers against the committed raw outputs (11.5, M4).

Runs no simulation and changes no result. Checks:

  A. Raw run files: count, status, run seeds 0..29 per (condition, arm), SHA-256
     against `sha256_manifest.json`, code revision and git_dirty flag.
  B. Summary tables: n_ok, mean, SD, min and max of every metric column in
     `report/summary.csv` recomputed from the raw run files.
  C. Frozen analysis: paired differences, means, SDs and 95 percent bootstrap
     intervals in `analysis/analysis.json` recomputed from the raw run files with
     the frozen statistics, resamples and seed.
  E. The EVO and NOSEL runs shared by EXP-001 and EXP-002 have identical metrics.
  D. Number scan: every decimal number printed in the reports, the manuscript,
     the supplementary file, the claims register and the limitations must equal,
     at its printed precision, a value present in a committed machine-readable
     result (confirmatory JSON/CSV, the freeze record, the exploratory pilot and
     the M4 exploratory sensitivity file). Unmatched numbers are listed for
     manual review (some are definitions, versions or planning values).

Output: research/publication/number_audit.json
Usage:  .venv/bin/python scripts/audit_numbers.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evolve.stats import paired_bootstrap  # noqa: E402

EXPS = ["EXP-001", "EXP-002", "EXP-003"]
TOL = 1e-9
SCAN = [
    "research/experiments/EXP-001/report.md", "research/experiments/EXP-002/report.md",
    "research/experiments/EXP-003/report.md", "research/paper/manuscript.md",
    "research/paper/supplementary.md", "research/claims_register.csv", "research/limitations.md",
]


def metric_value(r: dict, col: str):
    m = r["metrics"]
    if col == "stay_fraction":
        return m["exploit"]["stay_fraction"]
    if col == "wall_seconds":
        return r["manifest"]["wall_seconds"]
    return m.get(col)


def load_runs(exp: str) -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted((ROOT / f"results/confirmatory/{exp}/runs").glob("*.json"))]


def check_runs(exp: str, runs: list[dict], problems: list[str]) -> dict:
    man = json.loads((ROOT / f"results/confirmatory/{exp}/sha256_manifest.json").read_text())["files"]
    bad_hash = 0
    for p in sorted((ROOT / f"results/confirmatory/{exp}/runs").glob("*.json")):
        key = f"runs/{p.name}"
        if man.get(key) != hashlib.sha256(p.read_bytes()).hexdigest():
            bad_hash += 1
    cells = defaultdict(list)
    for r in runs:
        cells[(r["condition"], r["arm"])].append(r["run_seed"])
        if r["status"] != "ok":
            problems.append(f"{r['run_id']}: status {r['status']}")
        if r["manifest"]["git_dirty"] or r["manifest"]["git_revision"] != runs[0]["manifest"]["git_revision"]:
            problems.append(f"{r['run_id']}: revision or dirty flag differs")
    for cell, seeds in cells.items():
        if sorted(seeds) != list(range(30)):
            problems.append(f"{exp} {cell}: seeds {sorted(seeds)}")
    if bad_hash:
        problems.append(f"{exp}: {bad_hash} run files differ from sha256_manifest.json")
    return {"n_runs": len(runs), "cells": {f"{c}/{a}": len(s) for (c, a), s in sorted(cells.items())},
            "sha256_mismatches": bad_hash, "revision": runs[0]["manifest"]["git_revision"]}


def check_summary(exp: str, runs: list[dict], problems: list[str]) -> int:
    rows = list(csv.DictReader(open(ROOT / f"results/confirmatory/{exp}/report/summary.csv")))
    checked = 0
    for row in rows:
        rs = [r for r in runs if r["condition"] == row["condition"] and r["arm"] == row["arm"]]
        if int(row["n_ok"]) != sum(r["status"] == "ok" for r in rs):
            problems.append(f"{exp} {row['condition']}/{row['arm']}: n_ok")
        for col, txt in row.items():
            if txt in ("", None) or col in ("condition", "arm", "n_ok", "n_failed"):
                continue
            base, _, stat = col.rpartition("_")
            if stat not in ("mean", "sd", "min", "max"):
                continue
            vals = np.array([metric_value(r, base) for r in rs], dtype=float)
            ref = {"mean": vals.mean(), "sd": vals.std(ddof=1), "min": vals.min(), "max": vals.max()}[stat]
            checked += 1
            if not math.isclose(float(txt), ref, rel_tol=1e-9, abs_tol=TOL):
                problems.append(f"{exp} {row['condition']}/{row['arm']} {col}: csv {txt} raw {ref}")
    return checked


def check_analysis(exp: str, runs: list[dict], problems: list[str]) -> int:
    a = json.loads((ROOT / f"results/confirmatory/{exp}/analysis/analysis.json").read_text())
    idx = {(r["condition"], r["arm"], r["run_seed"]): r for r in runs}
    checked = 0
    for c in a["contrasts"]:
        ta, tb = c["contrast"].split(" - ")
        d = np.array([metric_value(idx[(c["condition"], ta, s)], c["metric"])
                      - metric_value(idx[(c["condition"], tb, s)], c["metric"]) for s in c["seeds"]])
        est = paired_bootstrap(d, a["bootstrap_resamples"], a["analysis_seed"], 0.95)
        pairs = [(np.asarray(c["diffs"]), d), (c["mean_diff"], est.mean), (c["ci_low"], est.ci_low),
                 (c["ci_high"], est.ci_high), (c["sd_diff"], est.sd), (c["n_pairs"], est.n)]
        for stored, raw in pairs:
            checked += 1
            if not np.allclose(stored, raw, rtol=1e-9, atol=TOL):
                problems.append(f"{exp} {c['condition']} {c['contrast']} {c['metric']}: stored {stored} raw {raw}")
    return checked


def known_values() -> list[float]:
    vals: list[float] = []

    def walk(o):
        if isinstance(o, bool):
            return
        if isinstance(o, (int, float)):
            vals.append(float(o))
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            for tok in o.split():
                try:
                    vals.append(float(tok))
                except ValueError:
                    pass

    files = []
    for exp in EXPS:
        base = ROOT / f"results/confirmatory/{exp}"
        files += [base / "analysis/analysis.json", base / "report/contrasts_f_test.json",
                  base / "matrix_manifest.json", base / "run_provenance.json"]
        files += sorted((base / "manifests").glob("*.json"))
    files += [ROOT / "research/freeze.json",
              ROOT / "results/exploratory/m4-sensitivity-2026-11-25/sensitivity.json",
              ROOT / "results/exploratory/pilot-2026-11-24/report/contrasts_f_test.json"]
    for f in files:
        if f.exists():
            walk(json.loads(f.read_text()))
    csvs = [ROOT / f"results/confirmatory/{e}/report/{n}" for e in EXPS for n in ("summary.csv", "metrics.csv")]
    csvs += [ROOT / "results/exploratory/pilot-2026-11-24/report/summary.csv"]
    for f in csvs:
        for row in csv.DictReader(open(f)):
            walk(list(row.values()))
    # derived quantities printed in the documents
    for exp in EXPS:
        a = json.loads((ROOT / f"results/confirmatory/{exp}/analysis/analysis.json").read_text())
        for c in a["contrasts"]:
            vals += [-c["mean_diff"], -c["ci_low"], -c["ci_high"]]
    return vals


NUM = re.compile(r"(?<![\w.])-?\d+\.\d+(?:e-?\d+)?(?![\w.])")


def matches(txt: str, known: np.ndarray) -> bool:
    x = float(txt)
    if "e" in txt:
        mant = txt.split("e")[0]
        dp = len(mant.split(".")[1])
        with np.errstate(divide="ignore", invalid="ignore"):
            k = known[known != 0]
            exp = np.floor(np.log10(np.abs(k)))
            m = np.round(k / 10 ** exp, dp)
            return bool(np.any((np.abs(m - float(mant)) < 1e-9) & (exp == int(txt.split("e")[1]))))
    dp = len(txt.split(".")[1])
    half = 0.5 * 10 ** (-dp) + 1e-12
    return bool(np.any(np.abs(known - x) <= half))


def scan(known: np.ndarray) -> dict:
    out = {}
    for rel in SCAN:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text()
        text = re.sub(r"[0-9a-f]{40,64}", "", text)  # hashes and revisions
        text = re.sub(r"arXiv:\s?\d{4}\.\d{4,5}|https?://\S+", "", text)  # identifiers, links
        found = NUM.findall(text)
        unmatched = sorted({t for t in found if not matches(t, known)}, key=float)
        out[rel] = {"decimal_numbers": len(found), "unmatched": unmatched}
    return out


def main() -> None:
    problems: list[str] = []
    report = {"schema": "evolve.number_audit", "schema_version": "1.0.0",
              "generator": "scripts/audit_numbers.py", "experiments": {}}
    for exp in EXPS:
        runs = load_runs(exp)
        info = check_runs(exp, runs, problems)
        info["summary_values_checked"] = check_summary(exp, runs, problems)
        info["analysis_values_checked"] = check_analysis(exp, runs, problems)
        report["experiments"][exp] = info
    # E. EXP-002 reuses EVO and NOSEL at the same revision: metrics must be identical.
    one = {(r["arm"], r["run_seed"]): r["metrics"] for r in load_runs("EXP-001")}
    two = {(r["arm"], r["run_seed"]): r["metrics"] for r in load_runs("EXP-002")}
    shared = [k for k in two if k in one]
    identical = sum(one[k] == two[k] for k in shared)
    report["exp001_exp002_shared_runs"] = {"shared": len(shared), "identical_metrics": identical}
    if identical != len(shared):
        problems.append(f"EXP-001/EXP-002 shared runs: {identical}/{len(shared)} identical")
    report["raw_check_problems"] = problems
    report["number_scan"] = scan(np.array(known_values()))
    out = ROOT / "research/publication/number_audit.json"
    out.write_text(json.dumps(report, indent=1) + "\n")
    for e, i in report["experiments"].items():
        print(e, i["n_runs"], "runs; sha mismatches", i["sha256_mismatches"], "; summary values",
              i["summary_values_checked"], "; analysis values", i["analysis_values_checked"])
    print("shared EXP-001/EXP-002 runs:", report["exp001_exp002_shared_runs"])
    print("raw problems:", len(problems))
    for p in problems[:20]:
        print("  ", p)
    for f, s in report["number_scan"].items():
        print(f, s["decimal_numbers"], "numbers; unmatched:", s["unmatched"])


if __name__ == "__main__":
    main()
