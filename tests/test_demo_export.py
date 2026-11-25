# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""M5 consistency checks (master prompt 11.6 M5): the demo shows the same
verified numbers as the manuscript.

1. Re-running the export in memory gives exactly the committed
   demo/public/data/results.json (deterministic, no timestamps).
2. Every `display` and `interval_display` string appears verbatim in
   research/paper/manuscript.md. Documented exceptions:
   - arm SDs (`sd_display`) are printed in the experiment reports' TAB-1, not
     in the manuscript; each must appear verbatim in its named report;
   - per-run values in `replay` (held-out F_test of single runs, training
     fitness traces) and the `curves` quartiles are raw or derived data drawn
     on the page with a note, not printed numbers; they are checked against
     the committed run files instead.
3. The sandbox fixture regenerates identically from the Python engine.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "demo" / "public" / "data" / "results.json"
MANUSCRIPT = (ROOT / "research" / "paper" / "manuscript.md").read_text(encoding="utf-8")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def export():
    return _load("export_demo_data")


@pytest.fixture(scope="module")
def committed():
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def test_export_reproduces_committed_results_json(export):
    assert export.render(export.build()) == RESULTS.read_text(encoding="utf-8")


def test_schema_and_revision(committed):
    assert committed["schema"] == "lab-demo-results"
    assert committed["schema_version"] == "1.0.0"
    assert committed["code_revision"] == "5d39c9bf1eae7356b1fa837642e02e4bde68e186"
    assert "generated" not in json.dumps(committed)  # no timestamps


def test_every_registered_experiment_is_exported(committed):
    import csv

    reg = {r["experiment_id"] for r in csv.DictReader((ROOT / "research" / "experiment_registry.csv").open())}
    ids = {e["id"] for e in committed["experiments"]}
    assert reg <= ids
    for e in committed["experiments"]:
        assert e["status"] and e["verdict"] and e["estimates"]


def test_display_strings_are_verbatim_in_manuscript(committed):
    missing = []
    for e in committed["experiments"]:
        for x in e["estimates"]:
            for key in ("display", "interval_display", "dz_display"):
                s = x.get(key)
                if s is not None and s not in MANUSCRIPT:
                    missing.append((e["id"], x["label"], key, s))
    for m in committed["arm_means"]:
        if m["display"] not in MANUSCRIPT:
            missing.append((m["experiment_id"], m["arm"], "display", m["display"]))
    assert missing == []


def test_documented_exception_arm_sds_are_in_their_reports(committed):
    for m in committed["arm_means"]:
        report = (ROOT / m["sd_source"]).read_text(encoding="utf-8")
        assert f"{m['display']} ({m['sd_display']})" in report, m


def test_headline_contradicting_result_is_exported_with_equal_weight(committed):
    heads = [(e["id"], x["kind"]) for e in committed["experiments"] for x in e["estimates"] if x["headline"]]
    assert heads == [("EXP-001", "supported"), ("EXP-002", "contradicting"), ("EXP-003", "inconclusive")]
    sigma = next(x for e in committed["experiments"] for x in e["estimates"] if x["label"].startswith("EVO - EVO-sigma0.5, F_test"))
    assert (sigma["display"], sigma["interval_display"]) == ("-1.776", "[-2.519, -1.082]")


def test_sources_hashes_match_files(committed):
    import hashlib

    for s in committed["sources"]:
        assert hashlib.sha256((ROOT / s["path"]).read_bytes()).hexdigest() == s["sha256"], s["path"]


def test_replay_values_match_run_files(committed):
    arm = next(a for a in committed["replay"]["arms"] if a["arm"] == "EVO")
    run = arm["runs"][3]
    raw = json.loads((ROOT / "results" / "confirmatory" / "EXP-001" / "runs" / f"{run['run_id']}.json").read_text())
    assert run["f_test"] == raw["metrics"]["f_test"]
    assert run["returned_index"] == raw["trace"]["returned_index"]
    decoded = [int(run["fitness_hex"][2 * i : 2 * i + 2], 16) / 5 for i in range(2000)]
    assert decoded == pytest.approx(raw["trace"]["train_fitness"], abs=1e-12)


def test_sandbox_fixture_regenerates():
    fx = _load("export_sandbox_fixture")
    assert json.dumps(fx.build(), separators=(",", ":")) + "\n" == fx.OUT.read_text()
