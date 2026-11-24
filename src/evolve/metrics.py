# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Per-run metrics (protocol B.5 and EXP-001 section 13). Pure functions."""

from __future__ import annotations

import numpy as np

from .errors import ConfigError


def episode_fitness_mean(eaten: np.ndarray, episodes_per_eval: int) -> np.ndarray:
    """Training fitness F_train per evaluation: mean food items over K episodes.

    eaten: flat (B * K,) array ordered evaluation-major. Returns (B,).
    Unit: food items per episode.
    """
    eaten = np.asarray(eaten)
    if episodes_per_eval < 1 or eaten.ndim != 1 or eaten.size % episodes_per_eval:
        raise ConfigError("eaten size must be a positive multiple of episodes_per_eval")
    if np.any(eaten < 0):
        raise ConfigError("negative food count")
    return eaten.reshape(-1, episodes_per_eval).mean(axis=1)


def adaptation_auc(train_fitness: np.ndarray) -> float:
    """(1/E) sum_i max_{j<=i} F_train(theta_j). Unit: items per episode."""
    f = np.asarray(train_fitness, dtype=np.float64)
    if f.ndim != 1 or f.size == 0:
        raise ConfigError("train_fitness must be a non-empty 1-D array")
    return float(np.maximum.accumulate(f).mean())


def genotypic_diversity(thetas: np.ndarray) -> float:
    """Mean pairwise Euclidean distance between parameter vectors (parameter units)."""
    x = np.asarray(thetas, dtype=np.float64)
    if x.ndim != 2 or x.shape[0] < 2:
        raise ConfigError("need at least two parameter vectors")
    sq = np.sum(x * x, axis=1)
    d2 = np.maximum(sq[:, None] + sq[None, :] - 2.0 * x @ x.T, 0.0)
    iu = np.triu_indices(x.shape[0], k=1)
    return float(np.sqrt(d2[iu]).mean())


def behavioural_diversity(actions: np.ndarray) -> float:
    """Mean pairwise Hamming distance of action sequences, as a fraction of steps.

    actions: (P, n_probe, T) or (P, L). Returns a value in [0, 1].
    """
    a = np.asarray(actions)
    if a.ndim < 2 or a.shape[0] < 2:
        raise ConfigError("need at least two action sequences")
    a = a.reshape(a.shape[0], -1)
    p, length = a.shape
    total = 0
    for i in range(p - 1):
        total += int(np.sum(a[i + 1 :] != a[i]))
    pairs = p * (p - 1) // 2
    return float(total / (pairs * length))
