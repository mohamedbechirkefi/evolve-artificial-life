# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
import copy

import pytest

from evolve.config import parse_config

TINY = {
    "experiment_id": "TINY",
    "label": "exploratory",
    "root_seed": 7,
    "test_pool": "exploratory",
    "run_seeds": [1000, 1001, 1002],
    "env": {"grid_size": 16, "n_food": 24, "generator": "clustered", "n_clusters": 3, "cluster_spread": 2.0, "episode_steps": 30},
    "shift_env": {"grid_size": 16, "n_food": 16, "generator": "uniform", "n_clusters": 1, "cluster_spread": 2.0, "episode_steps": 30},
    "policy": {"hidden_units": 8, "init_std": 1.0},
    "evaluation": {"train_episodes_per_eval": 2, "train_fixed": False, "n_test": 6, "n_shift": 5, "n_train_fresh": 4, "n_probe": 3},
    "bootstrap_resamples": 200,
    "conditions": [
        {
            "name": "main",
            "arms": [
                {"name": "RS", "kind": "random_search", "evaluations": 24, "population_size": 6},
                {"name": "NOSEL", "kind": "population", "population_size": 6, "generations": 4, "sigma": 0.1, "selection": "uniform", "elitism": 1},
                {"name": "EVO", "kind": "population", "population_size": 6, "generations": 4, "sigma": 0.1, "selection": "truncation", "truncation_fraction": 0.5, "elitism": 1},
            ],
        }
    ],
}


@pytest.fixture
def tiny_raw():
    return copy.deepcopy(TINY)


@pytest.fixture
def tiny_cfg():
    return parse_config(copy.deepcopy(TINY))
