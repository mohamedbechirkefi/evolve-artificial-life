# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Train/test seed isolation (master prompt section 10, project-specific verification)."""

import numpy as np
import pytest

from evolve import seeds
from evolve.config import EnvParams
from evolve.env import generate_layout
from evolve.errors import ConfigError
from evolve.runner import LayoutCache, train_env_indices

ROOT = 20261124


def _state(seq):
    return tuple(seq.generate_state(4))


def test_pool_streams_are_disjoint():
    train = {_state(seeds.train_env_seq(ROOT, s, i)) for s in range(20) for i in range(200)}
    fresh = {_state(seeds.fresh_env_seq(ROOT, s, i)) for s in range(20) for i in range(50)}
    probe = {_state(seeds.probe_env_seq(ROOT, s, i)) for s in range(20) for i in range(20)}
    test = {_state(seeds.test_env_seq(ROOT, "confirmatory", i)) for i in range(200)}
    shift = {_state(seeds.shift_env_seq(ROOT, "confirmatory", i)) for i in range(200)}
    xtest = {_state(seeds.test_env_seq(ROOT, "exploratory", i)) for i in range(200)}
    pools = [train, fresh, probe, test, shift, xtest]
    assert [len(p) for p in pools] == [4000, 1000, 400, 200, 200, 200]
    for i in range(len(pools)):
        for j in range(i + 1, len(pools)):
            assert not pools[i] & pools[j], (i, j)


def test_no_test_layout_appears_among_training_layouts():
    p = EnvParams()
    train = {generate_layout(p, seeds.train_env_seq(ROOT, s, i)).digest() for s in range(20) for i in range(100)}
    test = {generate_layout(p, seeds.test_env_seq(ROOT, "confirmatory", i)).digest() for i in range(200)}
    xtest = {generate_layout(p, seeds.test_env_seq(ROOT, "exploratory", i)).digest() for i in range(200)}
    assert len(test) == 200
    assert not train & test
    assert not train & xtest
    assert not test & xtest


def test_test_pool_is_independent_of_run_seed(tiny_cfg):
    a = LayoutCache(tiny_cfg, 1000)
    b = LayoutCache(tiny_cfg, 1001)
    assert a.get("test", 3).digest() == b.get("test", 3).digest()
    assert a.get("shift", 2).digest() == b.get("shift", 2).digest()
    assert a.get("train", 3).digest() != b.get("train", 3).digest()


def test_training_index_layout():
    assert list(train_env_indices(np.array([0, 1, 3]), 2, False)) == [0, 1, 2, 3, 6, 7]
    assert list(train_env_indices(np.array([5, 9]), 1, True)) == [0, 0]


def test_training_indices_never_overlap_between_evaluations():
    idx = train_env_indices(np.arange(2000), 5, False)
    assert len(set(idx.tolist())) == 10_000


def test_shift_pool_uses_shift_generator(tiny_cfg):
    lay = LayoutCache(tiny_cfg, 1000).get("shift", 0)
    assert lay.food.sum() == 16


@pytest.mark.parametrize("bad", [-1, 1.5, True])
def test_invalid_seed_components(bad):
    with pytest.raises(ConfigError):
        seeds.seed_sequence(ROOT, 3, bad)


def test_unknown_pool_rejected():
    with pytest.raises(ConfigError):
        seeds.test_env_seq(ROOT, "public", 0)
