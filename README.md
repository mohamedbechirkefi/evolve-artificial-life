<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# EVOLVE

**Question.** Can simple inherited policies improve performance under selection, and how robust is that improvement?

**Status: M2 (core implementation), 2026-11-24.** The simulation engine, search arms, metrics, result schema, runner, report generator and tests exist. Only exploratory smoke and pilot runs have been executed (on a separate exploratory test pool); no finding exists. The protocol is a draft awaiting the owner's freeze. All future results will be simulations in a synthetic grid world; improved task fitness is not general intelligence and not evidence about biological evolution.

## What is planned

A small foraging grid world, agents with a small neural policy, and a paired comparison at equal evaluation budget of random search (primary baseline), a no-selection mutation control and evolutionary selection, with mutation and selection ablations and robustness checks. See `research/protocol.md`.

## Experiments

| ID | Title | Status |
|---|---|---|
| EXP-001 | Evolutionary selection vs random search at equal evaluations | planned (protocol draft, awaiting owner freeze) |
| EXP-002 | Ablations of mutation and selection | planned (protocol draft, awaiting owner freeze) |
| EXP-003 | Robustness to budget and training-set size | planned (protocol draft, awaiting owner freeze) |

## Navigation

`master_prompt.md` (authority), `CLAUDE.md` (session rules), `roadmap.md`, `progress.md`, `research/` (protocol, registry, claims, literature, limitations, paper, experiments, publication checklists), `data/manifest.json`.

## Quick start

    uv sync
    ./scripts/evolve test            # pytest suite
    ./scripts/evolve smoke           # exploratory smoke matrix and report (results/exploratory/)
    ./scripts/evolve report --results <dir> [--pdf]

`./scripts/evolve run --config experiments/configs/EXP-001.json` refuses to run until the owner freezes the protocol.

## Data

No external dataset; environments are generated locally from recorded seeds. See `data/manifest.json`.

## Licence

EVOLVE Source-Available Non-Commercial Research License v1.0 (`LicenseRef-EVOLVE-NC-Research-1.0`). This is a custom source-available licence, not an OSI-approved open-source licence. See `LICENSE` and `NOTICE.md`.

## Citation

See `CITATION.cff`.
