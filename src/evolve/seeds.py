# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Seed derivation and pool isolation (protocol B.6).

Every random stream is a numpy SeedSequence with entropy = root_seed and a
spawn key whose first element names the stream. Distinct spawn keys give
independent streams, so the training, test, shifted and probe pools never
share a seed:

    (1, run_seed)                 initial policy draws (shared by all arms: matched starts)
    (2, run_seed, 0)              parent choice in population arms
    (2, run_seed, 1)              mutation noise in population arms
    (3, run_seed, 0, i)           training environment i of a run
    (3, run_seed, 1, j)           fresh training environment j (re-measured F_train)
    (3, run_seed, 2, j)           probe environment j (behavioural diversity)
    (4, pool, j)                  held-out test environment j  (independent of run seed and arm)
    (5, pool, j)                  shifted environment j        (independent of run seed and arm)

`pool` is 0 for the confirmatory pool and 1 for the exploratory pool, so
exploratory runs never touch the confirmatory held-out set (D-006).
"""

from __future__ import annotations

import numpy as np

from .errors import ConfigError

STREAM_INIT = 1
STREAM_SEARCH = 2
STREAM_TRAIN = 3
STREAM_TEST = 4
STREAM_SHIFT = 5

TRAIN_SUB_EVAL = 0
TRAIN_SUB_FRESH = 1
TRAIN_SUB_PROBE = 2

POOL_IDS = {"confirmatory": 0, "exploratory": 1}


def _check(*values: int) -> None:
    for v in values:
        if isinstance(v, bool) or not isinstance(v, (int, np.integer)) or v < 0:
            raise ConfigError(f"seed components must be non-negative integers, got {v!r}")


def seed_sequence(root_seed: int, *key: int) -> np.random.SeedSequence:
    _check(root_seed, *key)
    return np.random.SeedSequence(entropy=int(root_seed), spawn_key=tuple(int(k) for k in key))


def init_rng(root_seed: int, run_seed: int) -> np.random.Generator:
    return np.random.default_rng(seed_sequence(root_seed, STREAM_INIT, run_seed))


def parent_rng(root_seed: int, run_seed: int) -> np.random.Generator:
    return np.random.default_rng(seed_sequence(root_seed, STREAM_SEARCH, run_seed, 0))


def noise_rng(root_seed: int, run_seed: int) -> np.random.Generator:
    return np.random.default_rng(seed_sequence(root_seed, STREAM_SEARCH, run_seed, 1))


def train_env_seq(root_seed: int, run_seed: int, index: int) -> np.random.SeedSequence:
    return seed_sequence(root_seed, STREAM_TRAIN, run_seed, TRAIN_SUB_EVAL, index)


def fresh_env_seq(root_seed: int, run_seed: int, index: int) -> np.random.SeedSequence:
    return seed_sequence(root_seed, STREAM_TRAIN, run_seed, TRAIN_SUB_FRESH, index)


def probe_env_seq(root_seed: int, run_seed: int, index: int) -> np.random.SeedSequence:
    return seed_sequence(root_seed, STREAM_TRAIN, run_seed, TRAIN_SUB_PROBE, index)


def test_env_seq(root_seed: int, pool: str, index: int) -> np.random.SeedSequence:
    if pool not in POOL_IDS:
        raise ConfigError(f"unknown test pool {pool!r}")
    return seed_sequence(root_seed, STREAM_TEST, POOL_IDS[pool], index)


def shift_env_seq(root_seed: int, pool: str, index: int) -> np.random.SeedSequence:
    if pool not in POOL_IDS:
        raise ConfigError(f"unknown test pool {pool!r}")
    return seed_sequence(root_seed, STREAM_SHIFT, POOL_IDS[pool], index)
