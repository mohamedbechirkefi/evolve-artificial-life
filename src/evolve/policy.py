# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Fixed-topology feed-forward policy (protocol B.3).

Inputs: 24 egocentric food indicators plus a constant bias input (25).
Hidden: `H` tanh units, no separate hidden bias (folded into the bias input).
Outputs: 4 action logits with an output bias; action = argmax, ties broken
towards the lowest action index (numpy argmax semantics).

Parameter layout of theta (length 25*H + H*4 + 4; 236 for H = 8):
    theta[0 : 25H]          W1, row-major (25, H)
    theta[25H : 25H + 4H]   W2, row-major (H, 4)
    theta[-4:]              b2
"""

from __future__ import annotations

import numpy as np

from .errors import ConfigError

N_OBS = 24
N_INPUTS = N_OBS + 1
N_ACTIONS = 4


def n_params(hidden_units: int) -> int:
    if isinstance(hidden_units, bool) or not isinstance(hidden_units, int) or hidden_units < 1:
        raise ConfigError(f"hidden_units must be a positive integer, got {hidden_units!r}")
    return N_INPUTS * hidden_units + hidden_units * N_ACTIONS + N_ACTIONS


def unpack(thetas: np.ndarray, hidden_units: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Split a (B, D) parameter batch into W1 (B,25,H), W2 (B,H,4), b2 (B,4)."""
    thetas = np.asarray(thetas, dtype=np.float64)
    if thetas.ndim != 2 or thetas.shape[1] != n_params(hidden_units):
        raise ConfigError(
            f"thetas must have shape (B, {n_params(hidden_units)}), got {thetas.shape}"
        )
    if not np.all(np.isfinite(thetas)):
        raise ConfigError("thetas contain non-finite values")
    h = hidden_units
    b = thetas.shape[0]
    w1 = thetas[:, : N_INPUTS * h].reshape(b, N_INPUTS, h)
    w2 = thetas[:, N_INPUTS * h : N_INPUTS * h + h * N_ACTIONS].reshape(b, h, N_ACTIONS)
    b2 = thetas[:, -N_ACTIONS:]
    return w1, w2, b2


def act(w1: np.ndarray, w2: np.ndarray, b2: np.ndarray, obs: np.ndarray) -> np.ndarray:
    """Batched forward pass. obs: (B, 24) in {0, 1}. Returns int actions (B,)."""
    x = np.concatenate([obs, np.ones((obs.shape[0], 1))], axis=1)
    hid = np.tanh(np.einsum("bi,bih->bh", x, w1))
    logits = np.einsum("bh,bha->ba", hid, w2) + b2
    return np.argmax(logits, axis=1)


def sample_initial(rng: np.random.Generator, n: int, hidden_units: int, init_std: float) -> np.ndarray:
    """n parameter vectors with independent N(0, init_std^2) components."""
    return init_std * rng.standard_normal((n, n_params(hidden_units)))
