# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Metrics and statistics: hand-computed golden values, edge cases, invalid inputs."""

import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from evolve.errors import ConfigError
from evolve.metrics import adaptation_auc, behavioural_diversity, episode_fitness_mean, genotypic_diversity
from evolve.policy import n_params, unpack
from evolve.stats import (
    cohen_dz, minimum_detectable_difference, paired_bootstrap, required_pairs, wilcoxon_signed_rank,
)


def test_parameter_count_is_236_for_8_hidden_units():
    assert n_params(8) == 25 * 8 + 8 * 4 + 4 == 236


def test_unpack_layout():
    th = np.arange(236, dtype=float)[None]
    w1, w2, b2 = unpack(th, 8)
    assert w1[0, 1, 0] == 8 and w1[0, 24, 7] == 199
    assert w2[0, 0, 0] == 200 and w2[0, 7, 3] == 231
    assert list(b2[0]) == [232, 233, 234, 235]


@pytest.mark.parametrize("h", [0, -1, 1.5, True])
def test_invalid_hidden_units(h):
    with pytest.raises(ConfigError):
        n_params(h)


def test_fitness_scoring_golden():
    # Two evaluations with K = 3 episodes each: (2 + 4 + 0) / 3 and (24 + 24 + 21) / 3.
    f = episode_fitness_mean(np.array([2, 4, 0, 24, 24, 21]), 3)
    assert np.allclose(f, [2.0, 23.0])


@pytest.mark.parametrize("eaten,k", [(np.array([1, 2, 3]), 2), (np.array([1, -1]), 1), (np.array([1]), 0)])
def test_fitness_scoring_invalid(eaten, k):
    with pytest.raises(ConfigError):
        episode_fitness_mean(eaten, k)


def test_adaptation_auc_golden():
    # best-so-far of [1, 3, 2, 5] is [1, 3, 3, 5]; mean 3.0
    assert adaptation_auc(np.array([1.0, 3.0, 2.0, 5.0])) == 3.0
    with pytest.raises(ConfigError):
        adaptation_auc(np.array([]))


def test_genotypic_diversity_golden():
    # Points (0,0), (3,4), (0,4): distances 5, 4, 3 -> mean 4.
    assert math.isclose(genotypic_diversity(np.array([[0.0, 0], [3, 4], [0, 4]])), 4.0)
    assert genotypic_diversity(np.zeros((4, 3))) == 0.0
    with pytest.raises(ConfigError):
        genotypic_diversity(np.zeros((1, 3)))


def test_behavioural_diversity_golden():
    # Sequences [0,0,1,1], [0,1,1,1], [2,2,2,2]: Hamming 1, 4, 4 -> 9 / (3 pairs * 4 steps)
    a = np.array([[0, 0, 1, 1], [0, 1, 1, 1], [2, 2, 2, 2]])
    assert math.isclose(behavioural_diversity(a), 9 / 12)
    assert behavioural_diversity(np.zeros((5, 2, 3))) == 0.0


def test_cohen_dz_golden():
    # d = [1, 2, 3]: mean 2, sd 1 -> 2
    assert cohen_dz(np.array([1.0, 2.0, 3.0])) == 2.0
    assert math.isnan(cohen_dz(np.array([1.0, 1.0])))


def test_bootstrap_constant_differences_has_degenerate_interval():
    e = paired_bootstrap(np.full(10, 1.5), resamples=500, seed=0)
    assert e.mean == e.ci_low == e.ci_high == 1.5 and e.sd == 0


def test_bootstrap_is_seeded_and_brackets_mean():
    d = np.random.default_rng(0).normal(1.0, 2.0, 20)
    a = paired_bootstrap(d, 2000, seed=4)
    b = paired_bootstrap(d, 2000, seed=4)
    assert a == b and a.ci_low < a.mean < a.ci_high


@pytest.mark.parametrize("d", [np.array([1.0]), np.array([1.0, np.nan]), np.ones((2, 2))])
def test_bootstrap_invalid(d):
    with pytest.raises(ConfigError):
        paired_bootstrap(d)


def test_wilcoxon_golden():
    # d = [1..5], all positive: W+ = 15, mean 7.5, var 13.75, z = 2.0226, p = 0.0431
    r = wilcoxon_signed_rank(np.array([1.0, 2, 3, 4, 5]))
    assert r.w_plus == 15 and r.n_nonzero == 5
    assert math.isclose(r.z, 7.5 / math.sqrt(13.75))
    assert math.isclose(r.p_two_sided, 0.0431, abs_tol=1e-4)


def test_wilcoxon_ties_and_zeros():
    # d = [0, 1, -1, 2]: zero dropped; |d| ranks 1.5, 1.5, 3; W+ = 4.5
    r = wilcoxon_signed_rank(np.array([0.0, 1, -1, 2]))
    assert r.n_nonzero == 3 and r.w_plus == 4.5
    assert math.isnan(wilcoxon_signed_rank(np.zeros(4)).p_two_sided)


@settings(max_examples=30, deadline=None)
@given(st.lists(st.floats(-10, 10, allow_nan=False), min_size=2, max_size=30))
def test_wilcoxon_p_in_unit_interval(xs):
    r = wilcoxon_signed_rank(np.array(xs))
    assert math.isnan(r.p_two_sided) or 0 <= r.p_two_sided <= 1


def test_planning_formulas_golden():
    # (1.96 + 0.8416) * 2 / sqrt(20) = 2.5055
    assert math.isclose(minimum_detectable_difference(2.0, 20), 2.8016 * 2 / math.sqrt(20))
    # (1.96 * 2 / 0.5)^2 = 61.47 -> 62
    assert required_pairs(2.0, 0.5) == 62
    with pytest.raises(ConfigError):
        required_pairs(1.0, 0.0)
