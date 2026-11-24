<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# experiments/

`configs/` holds run configurations. `EXP-001.json` to `EXP-003.json` encode the frozen protocol v1.0 (owner-approved 2026-11-24; label `confirmatory`, 30 run seeds). Their SHA-256 is recorded in `research/freeze.json`; `run` accepts them only while every recorded hash matches and refuses any edited copy. `smoke.json` (protocol B.9 smoke matrix) and `pilot.json` (all planned arms at planned budgets, 10 seeds) are exploratory and use the exploratory test pool (D-006). The registered experiments, their protocols and reports live in `research/experiments/EXP-NNN/`.
