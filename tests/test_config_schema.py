# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Configuration validation and the versioned result schema."""

import copy
import json
from pathlib import Path

import pytest

from evolve.config import config_hash, load_config, parse_config
from evolve.errors import ConfigError, SchemaError
from evolve.runner import run_one
from evolve.schema import dump_result, load_result, validate_result

REPO = Path(__file__).resolve().parents[1]


def test_repository_configs_parse_and_have_equal_budgets():
    for name in ("EXP-001", "EXP-002", "EXP-003", "smoke", "pilot"):
        cfg = load_config(REPO / "experiments" / "configs" / f"{name}.json")
        for c in cfg.conditions:
            assert len({a.total_evaluations for a in c.arms}) == 1


def test_confirmatory_configs_match_frozen_protocol():
    c1 = load_config(REPO / "experiments/configs/EXP-001.json")
    assert c1.label == "confirmatory" and c1.test_pool == "confirmatory" and c1.run_seeds == tuple(range(30))
    main = c1.condition("main")
    assert main.evaluations == 2000 and main.evaluation.train_episodes_per_eval == 5 and main.evaluation.n_test == 200
    evo = main.arm("EVO")
    assert (evo.population_size, evo.generations, evo.sigma, evo.n_parents, evo.elitism) == (50, 40, 0.1, 10, 1)
    assert main.arm("NOSEL").selection == "uniform"
    c3 = load_config(REPO / "experiments/configs/EXP-003.json")
    assert c3.condition("K1").evaluation.train_fixed and c3.condition("K1").evaluation.train_episodes_per_eval == 1
    assert c3.condition("E8000").arm("EVO").n_parents == 20


def test_amendment_30_seeds_and_sigma_kept():
    # Owner-approved amendments of 2026-11-24: 30 paired run seeds (0 to 29) in
    # every confirmatory config; the primary mutation sigma stays 0.1.
    for name in ("EXP-001", "EXP-002", "EXP-003"):
        cfg = load_config(REPO / "experiments/configs" / f"{name}.json")
        assert cfg.run_seeds == tuple(range(30)), name
        for c in cfg.conditions:
            if "EVO" in [a.name for a in c.arms]:
                assert c.arm("EVO").sigma == 0.1, (name, c.name)


def test_unequal_budget_rejected(tiny_raw):
    tiny_raw["conditions"][0]["arms"][0]["evaluations"] = 30
    with pytest.raises(ConfigError, match="unequal"):
        parse_config(tiny_raw)


@pytest.mark.parametrize("mutator", [
    lambda d: d.update(test_pool="confirmatory"),
    lambda d: d.update(run_seeds=[1, 2]),
    lambda d: d.update(bogus=1),
    lambda d: d.update(run_seeds=[1000, 1000]),
    lambda d: d["conditions"][0]["arms"][1].update(sigma=-1),
    lambda d: d["conditions"][0]["arms"][2].update(truncation_fraction=0.01),
    lambda d: d["conditions"][0]["arms"][2].update(elitism=6),
    lambda d: d["conditions"][0]["arms"][0].update(sigma=0.1),
    lambda d: d["env"].update(n_food=300),
    lambda d: d.update(label="final"),
])
def test_invalid_configs_rejected(tiny_raw, mutator):
    mutator(tiny_raw)
    with pytest.raises(ConfigError):
        parse_config(tiny_raw)


def test_confirmatory_label_requires_low_seeds(tiny_raw):
    tiny_raw.update(label="confirmatory", test_pool="confirmatory")
    with pytest.raises(ConfigError):
        parse_config(tiny_raw)


def test_config_hash_is_canonical(tiny_raw):
    a = config_hash(tiny_raw)
    b = config_hash(json.loads(json.dumps(tiny_raw, sort_keys=False, indent=3)))
    tiny_raw["root_seed"] = 8
    assert a == b and a != config_hash(tiny_raw) and len(a) == 64


@pytest.fixture(scope="module")
def good_doc():
    from conftest import TINY

    return run_one(parse_config(copy.deepcopy(TINY)), "main", "EVO", 1000)


def test_result_validates(good_doc):
    validate_result(good_doc)
    assert good_doc["status"] == "ok"
    assert good_doc["metrics"]["n_evaluations"] == 24
    assert good_doc["manifest"]["attempts"] == 1


@pytest.mark.parametrize("mutator", [
    lambda d: d.pop("metrics"),
    lambda d: d.update(schema_version="9.9.9"),
    lambda d: d["metrics"].update(f_test="3"),
    lambda d: d["metrics"].update(f_test=float("nan")),
    lambda d: d["metrics"].update(extra=1),
    lambda d: d["metrics"]["exploit"].update(stay_fraction=1.5),
    lambda d: d.update(config_hash="abc"),
    lambda d: d.update(label="final"),
    lambda d: d["trace"].update(returned_index=10_000),
    lambda d: d.update(status="failed", failure=None),
    lambda d: d["manifest"].update(run_id="other"),
    lambda d: d["episodes"]["test"].append(-1),
    lambda d: d["trace"]["train_fitness"].pop(),
    lambda d: d["metrics"].pop("overfit_drop"),
    lambda d: d["metrics"].update(f_train_fixed=-1.0),
])
def test_malformed_results_rejected(good_doc, mutator):
    d = copy.deepcopy(good_doc)
    mutator(d)
    with pytest.raises(SchemaError):
        validate_result(d)


def test_dump_refuses_invalid_and_load_fails_closed(good_doc, tmp_path):
    bad = copy.deepcopy(good_doc)
    bad["metrics"]["f_test"] = -1
    with pytest.raises(SchemaError):
        dump_result(bad, tmp_path / "bad.json")
    assert not (tmp_path / "bad.json").exists()
    dump_result(good_doc, tmp_path / "ok.json")
    assert load_result(tmp_path / "ok.json")["run_id"] == good_doc["run_id"]
    (tmp_path / "nan.json").write_text((tmp_path / "ok.json").read_text().replace('"f_test": ', '"f_test": NaN, "x": '))
    with pytest.raises(SchemaError):
        load_result(tmp_path / "nan.json")
    (tmp_path / "broken.json").write_text("{")
    with pytest.raises(SchemaError):
        load_result(tmp_path / "broken.json")


def test_schema_1_0_0_results_remain_readable(good_doc):
    # The M2 exploratory results were written with schema 1.0.0, before the
    # K = 1 overfitting fields existed; they must still validate.
    old = copy.deepcopy(good_doc)
    old["schema_version"] = old["manifest"]["schema_version"] = "1.0.0"
    for k in ("f_train_fixed", "overfit_drop"):
        old["metrics"].pop(k)
    validate_result(old)
    old["metrics"]["overfit_drop"] = 1.0
    with pytest.raises(SchemaError):
        validate_result(old)
