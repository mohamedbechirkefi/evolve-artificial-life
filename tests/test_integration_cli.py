# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Integration: config -> runs -> validated results -> report; determinism across
processes; the freeze gate; the CLI."""

import csv
import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from evolve.cli import EXIT_REFUSED, check_runnable, main
from evolve.config import load_config, parse_config
from evolve.errors import ProtocolNotFrozenError
from evolve.freeze import freeze_status, sha256_file
from evolve.report import build_report, load_results
from evolve.runner import run_matrix, run_one
from evolve.schema import load_result

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def matrix_dir(tmp_path_factory):
    from conftest import TINY
    import copy

    out = tmp_path_factory.mktemp("tiny")
    run_matrix(parse_config(copy.deepcopy(TINY)), out, workers=0)
    return out


def test_matrix_writes_every_run(matrix_dir):
    runs = sorted((matrix_dir / "runs").glob("*.json"))
    assert len(runs) == 9
    for p in runs:
        d = load_result(p)
        assert d["label"] == "exploratory" and d["status"] == "ok"
    mm = json.loads((matrix_dir / "matrix_manifest.json").read_text())
    assert mm["n_runs"] == 9 and len(list((matrix_dir / "manifests").glob("*.json"))) == 9


def test_matched_generation_zero_across_arms(matrix_dir):
    docs = {(d["arm"], d["run_seed"]): d for d in load_results(matrix_dir)}
    for s in (1000, 1001, 1002):
        rs = docs[("RS", s)]["trace"]["train_fitness"][:6]
        assert rs == docs[("EVO", s)]["trace"]["train_fitness"][:6] == docs[("NOSEL", s)]["trace"]["train_fitness"][:6]


def test_shared_test_set_across_arms(matrix_dir):
    # Same test environments for all runs: a policy's score is a pure function of the policy.
    docs = load_results(matrix_dir)
    assert {len(d["episodes"]["test"]) for d in docs} == {6}


def test_report_from_results(matrix_dir, tmp_path):
    m = build_report(matrix_dir, tmp_path / "rep", planned_configs=[REPO / "experiments/configs/EXP-001.json"])
    rep = tmp_path / "rep"
    assert (rep / "report.md").exists() and (rep / "figures" / "FIG-1_f_test_by_arm.png").exists()
    text = (rep / "report.md").read_text()
    assert "EXPLORATORY. NOT A FINDING." in text
    with (rep / "metrics.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 9
    # Report numbers equal raw result numbers.
    raw = {d["run_id"]: d["metrics"]["f_test"] for d in load_results(matrix_dir)}
    for r in rows:
        assert float(r["f_test"]) == raw[r["run_id"]]
    contrasts = json.loads((rep / "contrasts_f_test.json").read_text())
    evo_rs = [c for c in contrasts if c["contrast"] == "EVO - RS"][0]
    assert evo_rs["n_pairs"] == 3
    assert np.isclose(evo_rs["mean_diff"], np.mean(evo_rs["diffs"]))
    assert {a["id"] for a in m["artifacts"]} >= {"TAB-1", "TAB-2", "FIG-1", "FIG-2"}
    assert m["runtime_projection"]["total_runs"] == 60


def test_report_fails_closed_on_corrupt_result(matrix_dir, tmp_path):
    bad = tmp_path / "bad"
    shutil.copytree(matrix_dir, bad)
    p = sorted((bad / "runs").glob("*.json"))[0]
    d = json.loads(p.read_text())
    d["metrics"]["f_test"] = -5
    p.write_text(json.dumps(d))
    with pytest.raises(Exception):
        build_report(bad, tmp_path / "rep")


def test_runs_are_deterministic_across_processes(tmp_path):
    from conftest import TINY
    import copy

    raw = copy.deepcopy(TINY)
    raw["run_seeds"] = [1000, 1001]
    cfg = parse_config(raw)
    run_matrix(cfg, tmp_path / "a", workers=0)
    run_matrix(cfg, tmp_path / "b", workers=2)
    for pa in sorted((tmp_path / "a" / "runs").glob("*.json")):
        da, db = load_result(pa), load_result(tmp_path / "b" / "runs" / pa.name)
        for k in ("metrics", "episodes", "trace", "config_hash"):
            assert da[k] == db[k], (pa.name, k)


def test_retry_then_failure_is_recorded(tiny_cfg, monkeypatch):
    import evolve.runner as r

    calls = []

    def boom(*a, **k):
        calls.append(1)
        raise RuntimeError("injected")

    monkeypatch.setattr(r, "_compute", boom)
    d = run_one(tiny_cfg, "main", "RS", 1000)
    assert d["status"] == "failed" and "injected" in d["failure"] and len(calls) == 2
    assert d["manifest"]["attempts"] == 2 and d["metrics"] is None


# ---------------------------------------------------------------- freeze gate

def test_current_protocols_are_not_frozen():
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        frozen, reason = freeze_status(exp)
        assert not frozen, reason


def test_run_refuses_confirmatory_config():
    cfg = load_config(REPO / "experiments/configs/EXP-001.json")
    with pytest.raises(ProtocolNotFrozenError):
        check_runnable(cfg)
    assert main(["run", "--config", str(REPO / "experiments/configs/EXP-001.json"), "--out", "/nonexistent/never"]) == EXIT_REFUSED


def _fake_repo(tmp_path, status, hash_value=None, edit_after=False):
    (tmp_path / "research/experiments/EXP-001").mkdir(parents=True)
    proto = tmp_path / "research/experiments/EXP-001/protocol.md"
    proto.write_text("frozen protocol text\n")
    h = hash_value or sha256_file(proto)
    (tmp_path / "research/experiment_registry.csv").write_text(
        "experiment_id,protocol_path,protocol_hash,status\n"
        f"EXP-001,research/experiments/EXP-001/protocol.md,{h},{status}\n"
    )
    if edit_after:
        proto.write_text("edited after freeze\n")
    return tmp_path


def test_freeze_detected_only_with_matching_hash(tmp_path):
    assert freeze_status("EXP-001", _fake_repo(tmp_path / "a", "frozen v1.0"))[0]
    assert not freeze_status("EXP-001", _fake_repo(tmp_path / "b", "frozen v1.0", edit_after=True))[0]
    assert not freeze_status("EXP-001", _fake_repo(tmp_path / "c", "planned (awaiting owner freeze)"))[0]
    assert not freeze_status("EXP-001", _fake_repo(tmp_path / "d", "frozen", hash_value="not assigned"))[0]
    assert not freeze_status("EXP-404", _fake_repo(tmp_path / "e", "frozen"))[0]


def test_smoke_refuses_confirmatory_config(capsys):
    assert main(["smoke", "--config", str(REPO / "experiments/configs/EXP-001.json"), "--out", "/nonexistent/never"]) == 2


def test_cli_run_and_report_exploratory(tmp_path, tiny_raw):
    tiny_raw["run_seeds"] = [1000]
    cfgp = tmp_path / "c.json"
    cfgp.write_text(json.dumps(tiny_raw))
    assert main(["run", "--config", str(cfgp), "--out", str(tmp_path / "out"), "--workers", "0"]) == 0
    assert len(list((tmp_path / "out" / "runs").glob("*.json"))) == 3
    # Raw results are never overwritten.
    assert main(["run", "--config", str(cfgp), "--out", str(tmp_path / "out"), "--workers", "0"]) == 2
    assert main(["report", "--results", str(tmp_path / "out")]) == 0
    assert (tmp_path / "out" / "report" / "report.md").exists()
