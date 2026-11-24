# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Toroidal foraging grid world (protocol B.3).

Coordinates are (row, col) on an N x N torus. The agent starts at
(N // 2, N // 2), which never holds food. Headings: 0 north (-1, 0), 1 east
(0, +1), 2 south (+1, 0), 3 west (0, -1). Actions: 0 forward, 1 turn left,
2 turn right, 3 stay. Moving forward onto a food cell consumes it; consumed
food never reappears within the episode.

Observation: 5 x 5 egocentric window rotated to the heading, own cell
excluded, ordered by forward distance f = +2 .. -2, then rightward offset
r = -2 .. +2. Index 7 is the cell directly ahead (f = 1, r = 0).

`simulate_batch` is the vectorised engine used by experiments.
`simulate_reference` is a deliberately simple scalar implementation used only
for differential testing.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np

from .config import EnvParams
from .errors import ConfigError, InvariantError
from .policy import N_ACTIONS, N_INPUTS, act, unpack

FORWARD, LEFT, RIGHT, STAY = 0, 1, 2, 3
HEADING_DELTAS = np.array([[-1, 0], [0, 1], [1, 0], [0, -1]], dtype=np.int64)
WINDOW_CELLS = tuple((f, r) for f in (2, 1, 0, -1, -2) for r in (-2, -1, 0, 1, 2) if (f, r) != (0, 0))
MAX_PLACEMENT_ATTEMPTS = 100_000


def _offsets() -> np.ndarray:
    """(4, 24, 2) world offsets of the egocentric window cells for each heading."""
    out = np.zeros((4, len(WINDOW_CELLS), 2), dtype=np.int64)
    for h in range(4):
        fwd = HEADING_DELTAS[h]
        right = HEADING_DELTAS[(h + 1) % 4]
        for i, (f, r) in enumerate(WINDOW_CELLS):
            out[h, i] = f * fwd + r * right
    return out


OFFSETS = _offsets()


@dataclass(frozen=True)
class Layout:
    food: np.ndarray  # (N, N) bool
    heading: int

    @property
    def start(self) -> tuple[int, int]:
        n = self.food.shape[0]
        return (n // 2, n // 2)

    def digest(self) -> str:
        """SHA-256 of the layout (food grid bytes and heading)."""
        h = hashlib.sha256()
        h.update(np.ascontiguousarray(self.food, dtype=np.uint8).tobytes())
        h.update(bytes([self.heading]))
        return h.hexdigest()


def generate_layout(params: EnvParams, seq: np.random.SeedSequence) -> Layout:
    """Deterministic layout from a seed sequence."""
    rng = np.random.default_rng(seq)
    n = params.grid_size
    start = (n // 2, n // 2)
    food = np.zeros((n, n), dtype=bool)
    if params.generator == "uniform":
        cells = np.array([c for c in range(n * n) if c != start[0] * n + start[1]])
        chosen = rng.choice(cells, size=params.n_food, replace=False)
        food.flat[chosen] = True
    elif params.generator == "clustered":
        centres = rng.integers(0, n, size=(params.n_clusters, 2))
        placed = 0
        attempts = 0
        while placed < params.n_food:
            attempts += 1
            if attempts > MAX_PLACEMENT_ATTEMPTS:
                raise InvariantError("clustered placement did not converge")
            c = centres[rng.integers(0, params.n_clusters)]
            off = np.rint(rng.normal(0.0, params.cluster_spread, size=2)).astype(np.int64)
            r, col = (int(c[0] + off[0]) % n, int(c[1] + off[1]) % n)
            if (r, col) == start or food[r, col]:
                continue
            food[r, col] = True
            placed += 1
    else:  # pragma: no cover - guarded by EnvParams validation
        raise ConfigError(f"unknown generator {params.generator!r}")
    heading = int(rng.integers(0, 4))
    return Layout(food=food, heading=heading)


def observe_batch(food: np.ndarray, pos: np.ndarray, headings: np.ndarray) -> np.ndarray:
    """(B, 24) egocentric food indicators for B agents. food: (B, N, N); pos: (B, 2)."""
    n = food.shape[1]
    off = OFFSETS[headings]  # (B, 24, 2)
    rows = (pos[:, 0:1] + off[:, :, 0]) % n
    cols = (pos[:, 1:2] + off[:, :, 1]) % n
    return food[np.arange(food.shape[0])[:, None], rows, cols].astype(np.float64)


@dataclass
class BatchResult:
    eaten: np.ndarray  # (B,) int, food items consumed per episode
    n_stay: np.ndarray  # (B,) int
    n_turn: np.ndarray  # (B,) int
    actions: np.ndarray | None  # (B, T) int8 if recorded


def simulate_batch(
    thetas: np.ndarray,
    food: np.ndarray,
    headings: np.ndarray,
    steps: int,
    hidden_units: int,
    record_actions: bool = False,
) -> BatchResult:
    """Run B independent episodes in lockstep.

    thetas: (B, D) policy parameters, one per episode.
    food: (B, N, N) bool initial food grids (copied, not modified).
    headings: (B,) initial headings in {0, 1, 2, 3}.
    """
    food = np.array(food, dtype=bool, copy=True)
    if food.ndim != 3 or food.shape[1] != food.shape[2]:
        raise ConfigError(f"food must have shape (B, N, N), got {food.shape}")
    b, n, _ = food.shape
    headings = np.array(headings, dtype=np.int64, copy=True)
    if headings.shape != (b,) or np.any((headings < 0) | (headings > 3)):
        raise ConfigError("headings must be a (B,) array of values in 0..3")
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 1:
        raise ConfigError("steps must be a positive integer")
    w1, w2, b2 = unpack(thetas, hidden_units)
    if w1.shape[0] != b:
        raise ConfigError("thetas and food batch sizes differ")
    if np.any(food[:, n // 2, n // 2]):
        raise InvariantError("start cell holds food")

    initial = food.sum(axis=(1, 2))
    pos = np.full((b, 2), n // 2, dtype=np.int64)
    eaten = np.zeros(b, dtype=np.int64)
    n_stay = np.zeros(b, dtype=np.int64)
    n_turn = np.zeros(b, dtype=np.int64)
    actions_log = np.zeros((b, steps), dtype=np.int8) if record_actions else None
    bidx = np.arange(b)

    for t in range(steps):
        obs = observe_batch(food, pos, headings)
        a = act(w1, w2, b2, obs)
        if actions_log is not None:
            actions_log[:, t] = a
        fwd = a == FORWARD
        headings = np.where(a == LEFT, (headings - 1) % 4, headings)
        headings = np.where(a == RIGHT, (headings + 1) % 4, headings)
        pos = np.where(fwd[:, None], (pos + HEADING_DELTAS[headings]) % n, pos)
        here = food[bidx, pos[:, 0], pos[:, 1]] & fwd
        eaten += here
        food[bidx[here], pos[here, 0], pos[here, 1]] = False
        n_stay += a == STAY
        n_turn += (a == LEFT) | (a == RIGHT)

    remaining = food.sum(axis=(1, 2))
    if not np.array_equal(initial - remaining, eaten):
        raise InvariantError("replay check failed: consumed count differs from the decrease in food")
    if np.any(eaten < 0) or np.any(eaten > initial):
        raise InvariantError("consumed count out of bounds")
    return BatchResult(eaten=eaten, n_stay=n_stay, n_turn=n_turn, actions=actions_log)


def stack_layouts(layouts: list[Layout]) -> tuple[np.ndarray, np.ndarray]:
    food = np.stack([lay.food for lay in layouts])
    headings = np.array([lay.heading for lay in layouts], dtype=np.int64)
    return food, headings


# ---------------------------------------------------------------- reference


def observe_reference(food: list[list[bool]], pos: tuple[int, int], heading: int) -> list[float]:
    """Scalar observation for one agent (used for testing)."""
    n = len(food)
    dr, dc = HEADING_DELTAS[heading]
    rr, rc = HEADING_DELTAS[(heading + 1) % 4]
    out = []
    for f, r in WINDOW_CELLS:
        row = (pos[0] + f * int(dr) + r * int(rr)) % n
        col = (pos[1] + f * int(dc) + r * int(rc)) % n
        out.append(1.0 if food[row][col] else 0.0)
    return out


def simulate_reference(theta: list[float], layout: Layout, steps: int, hidden_units: int) -> tuple[int, list[int]]:
    """Plain-Python single-episode simulator for differential tests."""
    h = hidden_units
    n = layout.food.shape[0]
    food = [[bool(layout.food[i, j]) for j in range(n)] for i in range(n)]
    w1 = [[theta[i * h + j] for j in range(h)] for i in range(N_INPUTS)]
    base = N_INPUTS * h
    w2 = [[theta[base + j * N_ACTIONS + a] for a in range(N_ACTIONS)] for j in range(h)]
    b2 = [theta[base + h * N_ACTIONS + a] for a in range(N_ACTIONS)]
    pos = (n // 2, n // 2)
    heading = layout.heading
    eaten = 0
    actions = []
    for _ in range(steps):
        x = observe_reference(food, pos, heading) + [1.0]
        hid = [math.tanh(sum(x[i] * w1[i][j] for i in range(N_INPUTS))) for j in range(h)]
        logits = [sum(hid[j] * w2[j][a] for j in range(h)) + b2[a] for a in range(N_ACTIONS)]
        best = 0
        for a in range(1, N_ACTIONS):
            if logits[a] > logits[best]:
                best = a
        actions.append(best)
        if best == LEFT:
            heading = (heading - 1) % 4
        elif best == RIGHT:
            heading = (heading + 1) % 4
        elif best == FORWARD:
            dr, dc = HEADING_DELTAS[heading]
            pos = ((pos[0] + int(dr)) % n, (pos[1] + int(dc)) % n)
            if food[pos[0]][pos[1]]:
                food[pos[0]][pos[1]] = False
                eaten += 1
    return eaten, actions
