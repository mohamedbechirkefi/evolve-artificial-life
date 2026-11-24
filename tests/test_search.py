# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Search arms: mutation bounds, budgets, matched starts, selection invariants."""

import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from evolve.config import ArmSpec, PolicyParams
from evolve.errors import ConfigError, InvariantError
from evolve.policy import n_params
from evolve.search import mutate, population_search, random_search

POL = PolicyParams()
D = n_params(8)


def evo(sigma=0.1, P=10, G=5, sel="truncation", frac=0.2, elit=1, name="EVO"):
    kw = dict(name=name, kind="population", population_size=P, generations=G, sigma=sigma, selection=sel, elitism=elit)
    if sel == "truncation":
        kw["truncation_fraction"] = frac
    return ArmSpec(**kw)


def linear_fitness(w):
    """Deterministic surrogate evaluator: fitness = clip(theta . w + 10, 0, 24)."""
    def f(thetas, ids):
        return np.clip(thetas @ w + 10, 0, 24)
    return f


def rngs(seed=0):
    return (np.random.default_rng([seed, 1]), np.random.default_rng([seed, 2]), np.random.default_rng([seed, 3]))


# ---------------------------------------------------------------- mutation bounds

def test_mutation_sigma_zero_is_identity_and_parents_untouched():
    p = np.random.default_rng(0).standard_normal((5, D))
    keep = p.copy()
    c = mutate(p, 0.0, np.random.default_rng(1))
    assert np.array_equal(c, p) and np.array_equal(p, keep)


@pytest.mark.parametrize("sigma", [-0.1, float("nan"), float("inf"), True, "0.1", None])
def test_mutation_rejects_invalid_sigma(sigma):
    with pytest.raises(ConfigError):
        mutate(np.zeros((2, D)), sigma, np.random.default_rng(0))


def test_mutation_rejects_non_finite_result():
    with pytest.raises(InvariantError):
        mutate(np.full((1, D), 1e308), 1e308, np.random.default_rng(0))


@settings(max_examples=30, deadline=None)
@given(sigma=st.floats(0.001, 2.0), seed=st.integers(0, 2**31))
def test_mutation_step_scale_property(sigma, seed):
    p = np.zeros((200, D))
    c = mutate(p, sigma, np.random.default_rng(seed))
    step = c - p
    assert np.all(np.isfinite(c))
    # 47,200 N(0, sigma^2) draws: the sample SD is within 3 percent of sigma.
    assert abs(step.std() / sigma - 1) < 0.03
    # Bound: no component moves more than 7 sigma (probability below 1e-7 for this sample size).
    assert np.abs(step).max() <= 7 * sigma


def test_mutation_noise_is_aligned_across_sigma():
    p = np.zeros((3, D))
    a = mutate(p, 0.1, np.random.default_rng(9))
    b = mutate(p, 0.5, np.random.default_rng(9))
    assert np.allclose(a * 5, b)


# ---------------------------------------------------------------- budgets and matched starts

@pytest.mark.parametrize("arm", [evo(), evo(sel="uniform", frac=None), evo(sigma=0.0)])
def test_population_budget_is_exact(arm):
    w = np.random.default_rng(0).standard_normal(D)
    calls = []

    def f(th, ids):
        calls.append(len(ids))
        return linear_fitness(w)(th, ids)

    tr = population_search(arm, POL, *rngs(), f)
    assert tr.n_evaluations == arm.total_evaluations == sum(calls) == 50
    assert sorted(set(np.concatenate([np.arange(50)]))) == list(range(50))


def test_rs_budget_and_matched_generation_zero():
    w = np.random.default_rng(0).standard_normal(D)
    rs = ArmSpec(name="RS", kind="random_search", evaluations=50, population_size=10)
    t_rs = random_search(rs, POL, np.random.default_rng([4, 1]), linear_fitness(w))
    t_ev = population_search(evo(), POL, np.random.default_rng([4, 1]), np.random.default_rng(2), np.random.default_rng(3), linear_fitness(w))
    assert t_rs.n_evaluations == 50
    assert np.array_equal(t_rs.thetas[:10], t_ev.thetas[:10])
    assert np.array_equal(t_rs.train_fitness[:10], t_ev.train_fitness[:10])
    assert np.all(t_rs.parent_index == -1)
    assert list(t_rs.final_population) == list(range(40, 50))


# ---------------------------------------------------------------- selection invariants

def test_truncation_parents_are_top_fraction_and_elite_is_exact_copy():
    w = np.random.default_rng(1).standard_normal(D)
    arm = evo(P=10, G=6, frac=0.3)
    tr = population_search(arm, POL, *rngs(3), linear_fitness(w))
    for g in range(1, 6):
        prev = np.arange((g - 1) * 10, g * 10)
        order = prev[np.argsort(-tr.train_fitness[prev], kind="stable")]
        new = np.arange(g * 10, (g + 1) * 10)
        assert tr.parent_index[new[0]] == order[0]
        assert np.array_equal(tr.thetas[new[0]], tr.thetas[order[0]])  # elite unchanged
        assert set(tr.parent_index[new[1:]]) <= set(order[:3])  # parents from top 3
        assert np.all(np.isin(tr.parent_index[new], prev))


def test_nosel_parents_ignore_fitness():
    # With a strongly informative fitness, NOSEL parents still cover the whole population.
    w = np.random.default_rng(1).standard_normal(D)
    arm = evo(P=20, G=30, sel="uniform", frac=None, name="NOSEL")
    tr = population_search(arm, POL, *rngs(5), linear_fitness(w))
    ranks = []
    for g in range(1, 30):
        prev = np.arange((g - 1) * 20, g * 20)
        rank = {int(i): r for r, i in enumerate(prev[np.argsort(-tr.train_fitness[prev], kind="stable")])}
        ranks += [rank[int(p)] for p in tr.parent_index[g * 20:(g + 1) * 20]]
    ranks = np.array(ranks)
    # Uniform ranks have mean 9.5; truncation at 20 percent would give mean below 2.
    assert abs(ranks.mean() - 9.5) < 1.0
    assert (ranks >= 10).mean() > 0.4


def test_selonly_never_creates_new_genotypes():
    w = np.random.default_rng(2).standard_normal(D)
    tr = population_search(evo(sigma=0.0), POL, *rngs(), linear_fitness(w))
    gen0 = {tuple(x) for x in tr.thetas[:10]}
    assert all(tuple(x) in gen0 for x in tr.thetas)


def test_evo_improves_on_smooth_surrogate():
    # Sanity check of the optimiser on a smooth deterministic surrogate (not a research result).
    w = np.random.default_rng(3).standard_normal(D) * 0.05
    tr = population_search(evo(P=20, G=30, sigma=0.5), POL, *rngs(), linear_fitness(w))
    assert tr.train_fitness[-20:].mean() > tr.train_fitness[:20].mean()


def test_returned_policy_is_first_argmax():
    def f(th, ids):
        return np.where(ids % 7 == 3, 5.0, 1.0)

    rs = ArmSpec(name="RS", kind="random_search", evaluations=30, population_size=10)
    tr = random_search(rs, POL, np.random.default_rng(0), f)
    assert tr.returned_index == 3


def test_population_search_is_deterministic():
    w = np.random.default_rng(1).standard_normal(D)
    a = population_search(evo(), POL, *rngs(8), linear_fitness(w))
    b = population_search(evo(), POL, *rngs(8), linear_fitness(w))
    assert np.array_equal(a.thetas, b.thetas) and np.array_equal(a.parent_index, b.parent_index)


def test_evaluator_returning_nan_is_rejected():
    rs = ArmSpec(name="RS", kind="random_search", evaluations=10, population_size=5)
    with pytest.raises(InvariantError):
        random_search(rs, POL, np.random.default_rng(0), lambda th, ids: np.full(len(ids), math.nan))


def test_wrong_arm_kind_is_rejected():
    with pytest.raises(ConfigError):
        random_search(evo(), POL, np.random.default_rng(0), lambda th, ids: np.zeros(len(ids)))
