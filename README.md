<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# EVOLVE

**Question.** Within a fixed budget of policy evaluations, does evolutionary selection with inherited, mutated policies find foraging policies with higher fitness on held-out grid environments than independent random search, and does any advantage survive changes in budget, mutation strength and training-set size?

**Why it matters.** Simple genetic algorithms and random search are both used as black-box methods for finding neural-network policies, and comparisons between them depend on budgets, seeds and evaluation details. A claim that selection helps needs an equal budget, a control that removes selection, held-out evaluation and run-level uncertainty.

**Status (M6, 2026-11-25).** Independent research manuscript / preprint draft, not peer-reviewed. Simulation study. The protocol v1.0 was frozen by the owner before any confirmatory run (`research/freeze.json`); all 420 planned confirmatory runs completed. Manuscript v1.0 (`research/paper/manuscript.md`) is written; the owner approved its funding, competing-interest and AI-use wording on 2026-11-25 (D-014). The owner approved the manuscript title on 2026-11-26 (decision sheet, B6); the owner's full-text review of the manuscript is pending. M6 prepared a release candidate (version 0.1.0-rc1) for the owner's review: the manuscript, supplementary and report PDFs are built and inspected, and a clean clone reproduces the tests, the smoke run and the demo (`research/publication/reproducibility_report.md`). The repository is public at https://github.com/mohamedbechirkefi/evolve-artificial-life since 2026-11-25; no tag, release, DOI or preprint exists. All results are simulations of a synthetic grid world; improved task fitness is not general intelligence and not evidence about biological evolution.

![The EVOLVE demo page: the overview with three findings of equal weight (EVO minus RS 5.791, 95 percent CI [4.644, 6.844], supported; EVO minus EVO-sigma0.5 -1.776, CI [-2.519, -1.082], a contradicting result for the frozen sigma; K1 EVO minus RS 0.751, CI [-0.533, 1.998], inconclusive), each with its interval on a shared axis.](docs/demo.png)

## Key findings (verified; numbers identical to the manuscript)

All in food items per episode on 200 held-out layouts, mean paired difference over n = 30 run seeds with a 95 percent percentile bootstrap interval.

- **Primary (EXP-001, supported under the frozen rule).** At 2,000 evaluations, EVO exceeded RS by 5.791, CI [4.644, 6.844] (C-001).
- **Against an assumption (EXP-002).** The frozen sigma 0.1 was not the best setting tested: EVO minus EVO-sigma0.5 was -1.776, CI [-2.519, -1.082], so sigma 0.5 exceeded it by 1.776. The owner classified this as a contradicting result under EXP-002's rule, a finding against EXP-002's assumption about the setting; H1 of EXP-001 stands (D-012, C-006).
- **Ablations (EXP-002).** Removing mutation (EVO minus SELONLY 8.297, CI [7.608, 8.956]) or selection (EVO minus NOSEL 8.046, CI [7.173, 8.874]) lowered held-out fitness by about 8 items.
- **Sensitivity (EXP-003).** The advantage held at E = 500 (2.368, CI [1.627, 3.128]) and E = 8,000 (8.374, CI [7.418, 9.287]), but with one fixed training environment it was inconclusive (0.751, CI [-0.533, 1.998]) while EVO overfit that environment more than RS. The result is specific to resampled training.

What this does not show: that population-based selection beats local search methods in general (no arm isolates single-lineage local search), anything about other environments or architectures, or anything about biological evolution. See `research/limitations.md`.

## Experiments

| ID | Title | Status | Report |
|---|---|---|---|
| EXP-001 | Evolutionary selection vs random search at equal evaluations | confirmatory, 90/90 runs ok; H1 supported | `research/experiments/EXP-001/report.md` |
| EXP-002 | Ablations of mutation and selection | confirmatory, 150/150 runs ok; H1a and H1b supported (estimates); sigma 0.5 above the frozen sigma 0.1 (contradicting result for the setting) | `research/experiments/EXP-002/report.md` |
| EXP-003 | Robustness to budget and training-set size | confirmatory, 180/180 runs ok; robustness not supported and not contradicted (K1 inconclusive) | `research/experiments/EXP-003/report.md` |

Exploratory work (pilot J-0004, M4 re-analysis J-0012) is labelled as such in `results/exploratory/` and never replaces a frozen verdict.

## Navigation

- Manuscript: `research/paper/manuscript.md` and `manuscript.pdf` (with `supplementary.md` and `supplementary.pdf`); report PDFs `research/experiments/EXP-00N/report.pdf` (built by `scripts/build_pdfs.py`); claims register `research/claims_register.csv`; evidence audit `research/publication/claims_audit.md`; artifact manifest `research/publication/artifact_manifest.json`.
- Control files: `master_prompt.md` (authority), `CLAUDE.md`, `roadmap.md`, `progress.md`, `research/decision_log.md`.
- Demo: `demo/` (static page; see below). Articles: `articles/medium.md`, `articles/linkedin.md` (drafts).

## Demo quick start

The page shows the published results with their intervals, a replay of the committed runs (fitness curves and ancestry, generation by generation) and a sandbox in which visitors evolve and watch their own organisms. It runs offline after the first load, sends nothing anywhere and collects nothing. Node 22 or later:

    cd demo && npm ci && npm run build && npm run preview

`npm test` runs the vitest suite (results validator and the sandbox port against a Python fixture). `node tools/a11y_check.mjs dist` runs the offline and accessibility check (needs Google Chrome). The page's data file is regenerated with `.venv/bin/python scripts/export_demo_data.py`.

Demo: https://evolve-artificial-life.kefimohamedbechir.workers.dev (Cloudflare Workers static assets, free plan; see `demo/README.md`).

## Quick start (research code)

    uv sync
    ./scripts/evolve test            # pytest suite
    ./scripts/evolve smoke           # exploratory smoke matrix and report (results/exploratory/)
    ./scripts/evolve report --results <dir> [--pdf]

## Full reproduction

`./scripts/evolve run --config experiments/configs/EXP-NNN.json` reruns a confirmatory matrix; it runs only while every hash in `research/freeze.json` matches and refuses an edited protocol or config. Then `./scripts/evolve report --results results/confirmatory/EXP-NNN` and `.venv/bin/python scripts/analyse_frozen.py EXP-NNN`. `scripts/audit_numbers.py` re-checks every reported number against the raw run files.

## Architecture

`src/evolve/`: environment, policy, search arms, metrics, seeds, runner, schema, report generator and CLI (NumPy). `scripts/`: frozen analysis, audits, manifest builder, demo export. `demo/`: TypeScript, React and Vite static page with hand-written SVG charts and a Web Worker sandbox.

## Data

No external dataset; environments are generated locally from recorded seeds. See `data/manifest.json`.

## Licence

EVOLVE Source-Available Non-Commercial Research License v1.0 (`LicenseRef-EVOLVE-NC-Research-1.0`). This is a custom source-available licence, not an OSI-approved open-source licence. See `LICENSE` and `NOTICE.md`.

## Citation

Mohamed Bechir Kefi, independent researcher. See `CITATION.cff`. Repository: https://github.com/mohamedbechirkefi/evolve-artificial-life.
