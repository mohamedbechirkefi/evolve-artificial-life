# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""scripts/analyse_frozen.py: decision rule, contrast orientation, worst-value
sensitivity and outputs, on a tiny matrix relabelled confirmatory in a temporary
root (never the repository's results)."""

import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from evolve.config import parse_config
from evolve.report import build_report
from evolve.runner import run_matrix
from evolve.stats import paired_bootstrap

REPO = Path(__file__).resolve().parents[1]


def _load_module():
    spec = importlib.util.spec_from_file_location("analyse_frozen", REPO / "scripts" / "analyse_frozen.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_verdict_rule():
    af = _load_module()
    assert af.verdict(0.1, 2.0) == "supported"
    assert af.verdict(-2.0, 0.0) == "contradicted"
    assert af.verdict(-2.0, -0.1) == "contradicted"
    assert af.verdict(0.0, 1.0) == "inconclusive"
    assert af.verdict(-1.0, 1.0) == "inconclusive"


def test_contrast_matches_frozen_bootstrap_and_orientation():
    af = _load_module()
    by = {("c", "EVO"): {0: 5.0, 1: 7.0, 2: 6.5}, ("c", "RS"): {0: 4.0, 1: 4.5, 2: 6.0}}
    r = af.contrast(by, "c", "EVO", "RS", "f_test", 500, 0, {})
    est = paired_bootstrap(np.array([1.0, 2.5, 0.5]), resamples=500, seed=0)
    assert r["mean_diff"] == pytest.approx(est.mean) and r["ci_low"] == est.ci_low and r["ci_high"] == est.ci_high
    assert r["n_positive"] == 3 and "worst_value_sensitivity" not in r


def test_worst_value_sensitivity_on_failure():
    af = _load_module()
    by = {("c", "EVO"): {0: 5.0, 1: 7.0, 2: 6.5}, ("c", "RS"): {0: 4.0, 1: 4.5}}
    r = af.contrast(by, "c", "EVO", "RS", "f_test", 500, 0, {("c", "RS"): [2]})
    assert r["n_pairs"] == 2
    w = r["worst_value_sensitivity"]
    assert w["n_pairs"] == 3 and w["mean_diff"] == pytest.approx(np.mean([1.0, 2.5, 6.5 - 4.0]))


def test_analyse_writes_outputs(tmp_path, monkeypatch):
    from conftest import TINY

    af = _load_module()
    raw = copy.deepcopy(TINY)
    raw["experiment_id"] = "EXP-T"
    raw["label"] = "confirmatory"
    raw["test_pool"] = "confirmatory"
    raw["run_seeds"] = [0, 1, 2]
    raw["analysis_seed"] = 0
    res = tmp_path / "results" / "confirmatory" / "EXP-T"
    run_matrix(parse_config(raw), res, workers=0)
    build_report(res)
    monkeypatch.setattr(af, "ROOT", tmp_path)
    monkeypatch.setitem(af.PLAN, "EXP-T", [("main", "EVO", "RS", "f_test", "registered primary", "test")])
    a = af.analyse("EXP-T")
    row = a["contrasts"][0]
    assert row["n_pairs"] == 3 and row["verdict_frozen_rule"] in {"supported", "contradicted", "inconclusive"}
    assert (res / "analysis" / "FIG-3_paired_differences.png").exists()
    man = json.loads((res / "sha256_manifest.json").read_text())
    assert len([k for k in man["files"] if k.startswith("runs/")]) == 9
    pub = tmp_path / "research" / "experiments" / "EXP-T"
    assert (pub / "metrics.csv").exists() and (pub / "run_manifest.json").exists() and (pub / "config.json").exists()
