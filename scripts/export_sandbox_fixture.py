# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Small fixture from the Python engine for the demo sandbox port (M5).

Generates a handful of layouts, hand-built and random policies with a dedicated seed
(entropy 5005, never used by any experiment pool), runs them through
`evolve.env.simulate_batch` with recorded actions, and writes
demo/src/engine.fixture.json. The vitest in demo/src/engine.test.ts replays
each episode in the TypeScript port and requires identical actions and
scores (tolerance: zero action mismatches, zero score difference).

Compute: 24 recorded episodes of 100 steps, well under one second on one
core. Labelled exploratory; it produces no research result.

Usage: .venv/bin/python scripts/export_sandbox_fixture.py [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evolve.config import EnvParams  # noqa: E402
from evolve.env import generate_layout, simulate_batch  # noqa: E402
from evolve.policy import n_params  # noqa: E402

OUT = ROOT / "demo" / "src" / "engine.fixture.json"
ENTROPY = 5005
HIDDEN = 8
STEPS = 100
N_LAYOUTS = 4
N_POLICIES = 6


def build() -> dict:
    params = EnvParams(grid_size=16, n_food=24, generator="clustered", n_clusters=3, cluster_spread=2.0, episode_steps=STEPS)
    root = np.random.SeedSequence(ENTROPY)
    layout_seqs = root.spawn(N_LAYOUTS + 1)
    layouts = [generate_layout(params, s) for s in layout_seqs[:N_LAYOUTS]]
    rng = np.random.default_rng(layout_seqs[N_LAYOUTS])
    d = n_params(HIDDEN)
    thetas = rng.standard_normal((N_POLICIES, d))
    # Half of the policies are a hand-built food seeker (with and without
    # small parameter noise), so the fixture covers eating, turning towards
    # food and wrapping on the torus, not only idle random policies.
    seeker = np.zeros(d)
    for cell, unit in ((7, 0), (2, 0), (6, 1), (11, 1), (1, 1), (8, 2), (12, 2), (3, 2)):
        seeker[cell * HIDDEN + unit] = 3.0
    base = 25 * HIDDEN
    seeker[base + 0 * 4 + 0] = 10.0  # unit 0 -> forward
    seeker[base + 1 * 4 + 1] = 6.0  # unit 1 -> turn left
    seeker[base + 2 * 4 + 2] = 6.0  # unit 2 -> turn right
    seeker[-4 + 0] = 0.5  # default: forward
    thetas[0] = seeker
    thetas[1] = seeker + 0.3 * rng.standard_normal(d)
    thetas[2] = seeker + 1.0 * rng.standard_normal(d)
    episodes = []
    for li, lay in enumerate(layouts):
        food = np.stack([lay.food] * N_POLICIES)
        heads = np.full(N_POLICIES, lay.heading, dtype=np.int64)
        res = simulate_batch(thetas, food, heads, STEPS, HIDDEN, record_actions=True)
        for pi in range(N_POLICIES):
            episodes.append({
                "layout": li, "policy": pi, "eaten": int(res.eaten[pi]),
                "n_stay": int(res.n_stay[pi]), "n_turn": int(res.n_turn[pi]),
                "actions": "".join(str(int(a)) for a in res.actions[pi]),
            })
    return {
        "generator": "scripts/export_sandbox_fixture.py",
        "engine": "src/evolve/env.py simulate_batch, src/evolve/policy.py",
        "label": "exploratory fixture for the sandbox port; not a research result",
        "grid_size": 16, "steps": STEPS, "hidden_units": HIDDEN,
        "layouts": [{"food": [int(i) for i in np.flatnonzero(lay.food)], "heading": int(lay.heading)} for lay in layouts],
        "thetas": [[float(x) for x in t] for t in thetas],
        "episodes": episodes,
    }


def main(argv: list[str]) -> int:
    text = json.dumps(build(), separators=(",", ":")) + "\n"
    if "--check" in argv:
        ok = OUT.exists() and OUT.read_text() == text
        print("fixture up to date" if ok else "fixture is stale")
        return 0 if ok else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
