# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Environment: golden examples, determinism, invariants, differential tests, invalid inputs."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from evolve.config import EnvParams
from evolve.env import (
    FORWARD, LEFT, RIGHT, STAY, Layout, generate_layout, observe_batch, observe_reference,
    simulate_batch, simulate_reference,
)
from evolve.errors import ConfigError, InvariantError
from evolve.policy import n_params

H = 8
D = n_params(H)


def const_policy(action: int) -> np.ndarray:
    th = np.zeros(D)
    th[-4 + action] = 1.0
    return th


def layout_with(cells, heading=0, n=16) -> Layout:
    food = np.zeros((n, n), dtype=bool)
    for r, c in cells:
        food[r, c] = True
    return Layout(food=food, heading=heading)


def run1(theta, lay, steps, record=False):
    return simulate_batch(theta[None, :], lay.food[None], np.array([lay.heading]), steps, H, record_actions=record)


# ---------------------------------------------------------------- golden examples

def test_observation_index_7_is_cell_ahead_for_every_heading():
    ahead = {0: (7, 8), 1: (8, 9), 2: (9, 8), 3: (8, 7)}
    for h, cell in ahead.items():
        lay = layout_with([cell], heading=h)
        obs = observe_batch(lay.food[None], np.array([[8, 8]]), np.array([h]))[0]
        assert obs.sum() == 1 and obs[7] == 1, h
        assert observe_reference(lay.food.tolist(), (8, 8), h) == list(obs)


def test_observation_window_wraps_on_torus():
    lay = layout_with([(15, 0)], heading=0)  # agent at (0, 0) facing north: ahead is (15, 0)
    obs = observe_batch(lay.food[None], np.array([[0, 0]]), np.array([0]))[0]
    assert obs[7] == 1 and obs.sum() == 1


def test_forward_policy_golden():
    # Column 8 holds food at rows 7, 5 and 0; (8, 9) is off the path.
    lay = layout_with([(7, 8), (5, 8), (0, 8), (8, 9)], heading=0)
    assert run1(const_policy(FORWARD), lay, 3).eaten[0] == 2  # rows 7, 6, 5
    assert run1(const_policy(FORWARD), lay, 100).eaten[0] == 3  # loops the column, never reaches (8, 9)


def test_stay_and_turn_policies_eat_nothing():
    lay = layout_with([(7, 8), (8, 9)], heading=0)
    r = run1(const_policy(STAY), lay, 50)
    assert r.eaten[0] == 0 and r.n_stay[0] == 50 and r.n_turn[0] == 0
    r = run1(const_policy(LEFT), lay, 50)
    assert r.eaten[0] == 0 and r.n_turn[0] == 50


def test_hand_built_food_seeking_policy_golden():
    th = np.zeros(D)
    th[7 * H + 0] = 10.0  # obs[7] (food ahead) -> hidden unit 0
    th[25 * H + 0 * 4 + FORWARD] = 10.0  # hidden unit 0 -> forward logit
    th[-4 + RIGHT] = 1.0  # default: turn right
    lay = layout_with([(8, 9)], heading=0)
    r = run1(th, lay, 3, record=True)
    assert r.eaten[0] == 1
    assert list(r.actions[0]) == [RIGHT, FORWARD, RIGHT]


def test_argmax_tie_goes_to_lowest_action():
    th = np.zeros(D)  # all logits 0 -> action 0 (forward)
    lay = layout_with([(7, 8)], heading=0)
    r = run1(th, lay, 1, record=True)
    assert r.actions[0, 0] == FORWARD and r.eaten[0] == 1


# ---------------------------------------------------------------- generation and determinism

def test_layout_generation_is_deterministic_and_valid():
    p = EnvParams()
    a = generate_layout(p, np.random.SeedSequence(5, spawn_key=(3, 0, 0, 1)))
    b = generate_layout(p, np.random.SeedSequence(5, spawn_key=(3, 0, 0, 1)))
    c = generate_layout(p, np.random.SeedSequence(5, spawn_key=(3, 0, 0, 2)))
    assert a.digest() == b.digest() and np.array_equal(a.food, b.food) and a.heading == b.heading
    assert a.digest() != c.digest()
    assert a.food.sum() == 24 and not a.food[8, 8]


@settings(max_examples=60, deadline=None)
@given(seed=st.integers(0, 2**32 - 1), n_food=st.integers(0, 60), gen=st.sampled_from(["clustered", "uniform"]))
def test_layout_property_counts_and_start(seed, n_food, gen):
    p = EnvParams(n_food=n_food, generator=gen)
    lay = generate_layout(p, np.random.SeedSequence(seed))
    assert lay.food.sum() == n_food
    assert not lay.food[8, 8]
    assert lay.heading in (0, 1, 2, 3)


def test_simulation_is_deterministic():
    rng = np.random.default_rng(0)
    th = rng.standard_normal((8, D))
    lays = [generate_layout(EnvParams(), np.random.SeedSequence(i)) for i in range(8)]
    food = np.stack([l.food for l in lays])
    hd = np.array([l.heading for l in lays])
    r1 = simulate_batch(th, food, hd, 100, H, record_actions=True)
    r2 = simulate_batch(th, food, hd, 100, H, record_actions=True)
    assert np.array_equal(r1.eaten, r2.eaten) and np.array_equal(r1.actions, r2.actions)
    assert np.array_equal(food, np.stack([l.food for l in lays]))  # inputs not mutated


# ---------------------------------------------------------------- differential test

def test_batched_engine_matches_scalar_reference():
    rng = np.random.default_rng(123)
    for i in range(12):
        lay = generate_layout(EnvParams(generator="clustered" if i % 2 else "uniform"), np.random.SeedSequence(1000 + i))
        th = rng.standard_normal(D) * (0.5 + i / 4)
        r = run1(th, lay, 60, record=True)
        ref_eaten, ref_actions = simulate_reference(list(th), lay, 60, H)
        assert r.eaten[0] == ref_eaten
        assert list(r.actions[0]) == ref_actions


# ---------------------------------------------------------------- invariants

@settings(max_examples=40, deadline=None)
@given(seed=st.integers(0, 2**31), steps=st.integers(1, 120), scale=st.floats(0.01, 5.0))
def test_fitness_bounds_property(seed, steps, scale):
    rng = np.random.default_rng(seed)
    lays = [generate_layout(EnvParams(), np.random.SeedSequence([seed, j])) for j in range(4)]
    r = simulate_batch(scale * rng.standard_normal((4, D)), np.stack([l.food for l in lays]),
                       np.array([l.heading for l in lays]), steps, H)
    assert np.all(r.eaten >= 0) and np.all(r.eaten <= 24)
    assert np.all(r.eaten <= steps)  # at most one item per step
    assert np.all(r.n_stay + r.n_turn <= steps)


def test_food_on_start_cell_is_rejected():
    lay = layout_with([(8, 8)])
    with pytest.raises(InvariantError):
        run1(const_policy(STAY), lay, 1)


@pytest.mark.parametrize("bad", [
    dict(steps=0), dict(steps=1.5), dict(headings=np.array([4])), dict(thetas=np.full((1, D), np.nan)),
    dict(thetas=np.zeros((1, D + 1))), dict(food=np.zeros((1, 16, 15), dtype=bool)),
])
def test_invalid_simulation_inputs(bad):
    args = dict(thetas=np.zeros((1, D)), food=np.zeros((1, 16, 16), dtype=bool), headings=np.array([0]), steps=5)
    args.update(bad)
    with pytest.raises(ConfigError):
        simulate_batch(args["thetas"], args["food"], args["headings"], args["steps"], H)


@pytest.mark.parametrize("kw", [dict(n_food=256), dict(n_food=-1), dict(grid_size=3), dict(generator="maze"),
                                dict(cluster_spread=0.0), dict(episode_steps=0)])
def test_invalid_env_params(kw):
    with pytest.raises(ConfigError):
        EnvParams(**kw)
