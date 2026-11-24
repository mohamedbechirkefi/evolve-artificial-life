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
from evolve.config import config_hash, load_config, parse_config
from evolve.errors import ProtocolNotFrozenError
from evolve.freeze import check_config_frozen, freeze_status, sha256_file
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
    assert m["runtime_projection"]["total_runs"] == 90  # 3 arms x 30 seeds


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

def _fake_repo(tmp_path, status, hash_value=None, edit_after=None, record=True, record_status="frozen"):
    """A minimal repository with one frozen experiment.

    edit_after: None, or one of "protocol", "main", "config" (edited after the
    freeze record was written).
    """
    (tmp_path / "research/experiments/EXP-001").mkdir(parents=True)
    (tmp_path / "experiments/configs").mkdir(parents=True)
    proto = tmp_path / "research/experiments/EXP-001/protocol.md"
    proto.write_text("frozen protocol text\n")
    main_p = tmp_path / "research/protocol.md"
    main_p.write_text("main protocol text\n")
    cfg_raw = json.loads((REPO / "experiments/configs/EXP-001.json").read_text())
    cfgp = tmp_path / "experiments/configs/EXP-001.json"
    cfgp.write_text(json.dumps(cfg_raw, indent=1) + "\n")
    h = hash_value or sha256_file(proto)
    (tmp_path / "research/experiment_registry.csv").write_text(
        "experiment_id,protocol_path,protocol_hash,status\n"
        f"EXP-001,research/experiments/EXP-001/protocol.md,{h},{status}\n"
    )
    if record:
        rec = {
            "schema": "evolve.freeze_record",
            "status": record_status,
            "files": {
                "research/protocol.md": sha256_file(main_p),
                "research/experiments/EXP-001/protocol.md": sha256_file(proto),
                "experiments/configs/EXP-001.json": sha256_file(cfgp),
            },
            "experiments": {
                "EXP-001": {
                    "protocol": "research/experiments/EXP-001/protocol.md",
                    "config": "experiments/configs/EXP-001.json",
                    "config_canonical_hash": config_hash(parse_config(cfg_raw)),
                }
            },
        }
        (tmp_path / "research/freeze.json").write_text(json.dumps(rec))
    if edit_after == "protocol":
        proto.write_text("edited after freeze\n")
    elif edit_after == "main":
        main_p.write_text("main protocol edited after freeze\n")
    elif edit_after == "config":
        cfg_raw["run_seeds"] = list(range(20))
        cfgp.write_text(json.dumps(cfg_raw, indent=1) + "\n")
    return tmp_path


def test_freeze_detected_only_with_matching_hash(tmp_path):
    assert freeze_status("EXP-001", _fake_repo(tmp_path / "a", "frozen v1.0"))[0]
    assert not freeze_status("EXP-001", _fake_repo(tmp_path / "b", "frozen v1.0", edit_after="protocol"))[0]
    assert not freeze_status("EXP-001", _fake_repo(tmp_path / "c", "planned (awaiting owner freeze)"))[0]
    assert not freeze_status("EXP-001", _fake_repo(tmp_path / "d", "frozen", hash_value="not assigned"))[0]
    assert not freeze_status("EXP-404", _fake_repo(tmp_path / "e", "frozen"))[0]


def test_freeze_requires_record_and_unchanged_main_protocol_and_configs(tmp_path):
    # Amendment 2026-11-24: the main protocol and the configs are hashed at freeze.
    ok, why = freeze_status("EXP-001", _fake_repo(tmp_path / "a", "frozen", record=False))
    assert not ok and "freeze record not found" in why
    ok, why = freeze_status("EXP-001", _fake_repo(tmp_path / "b", "frozen", edit_after="main"))
    assert not ok and "research/protocol.md changed" in why
    ok, why = freeze_status("EXP-001", _fake_repo(tmp_path / "c", "frozen", edit_after="config"))
    assert not ok and "EXP-001.json changed" in why
    ok, why = freeze_status("EXP-001", _fake_repo(tmp_path / "d", "frozen", record_status="draft"))
    assert not ok


def test_check_config_frozen_compares_canonical_config(tmp_path):
    repo = _fake_repo(tmp_path / "a", "frozen v1.0")
    raw = json.loads((repo / "experiments/configs/EXP-001.json").read_text())
    assert check_config_frozen(parse_config(raw), repo)[0]
    raw["conditions"][0]["arms"][2]["sigma"] = 0.5
    ok, why = check_config_frozen(parse_config(raw), repo)
    assert not ok and "differs from the frozen config" in why


# The repository itself (after the owner-approved freeze of 2026-11-24).

def test_repository_protocols_are_frozen():
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        frozen, reason = freeze_status(exp)
        assert frozen, reason


def test_run_accepts_frozen_confirmatory_configs():
    # Only the gate is exercised; no confirmatory run is started.
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        check_runnable(load_config(REPO / f"experiments/configs/{exp}.json"))


def test_run_refuses_changed_confirmatory_config(tmp_path):
    raw = json.loads((REPO / "experiments/configs/EXP-001.json").read_text())
    raw["run_seeds"] = list(range(20))
    with pytest.raises(ProtocolNotFrozenError, match="differs from the frozen config"):
        check_runnable(parse_config(raw))
    cfgp = tmp_path / "EXP-001-edited.json"
    cfgp.write_text(json.dumps(raw))
    assert main(["run", "--config", str(cfgp), "--out", str(tmp_path / "never")]) == EXIT_REFUSED
    assert not (tmp_path / "never").exists()


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
