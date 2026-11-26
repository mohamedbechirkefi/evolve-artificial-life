<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# demo/

Static offline research page for EVOLVE (M5): TypeScript, React and Vite from the shared lab template, versions pinned in `package-lock.json`, charts hand-written in SVG, no chart library, no font, image or script from any other host, no analytics and nothing collected from visitors.

## What it shows

- **Overview.** The question, the status label and three findings of equal weight, each with its 95 percent interval: EXP-001 EVO minus RS 5.791, CI [4.644, 6.844] (supported); EXP-002 EVO minus EVO-sigma0.5 -1.776, CI [-2.519, -1.082] (the frozen sigma 0.1 was not the best setting tested; a contradicting result under EXP-002's rule, owner decision D-012; H1 stands); EXP-003 K1 EVO minus RS 0.751, CI [-0.533, 1.998] (inconclusive).
- **Replay (measured).** Fitness curves (median and interquartile range over 30 run seeds) and the ancestry of any committed run seed, scrubbed generation by generation, for RS, NOSEL, EVO, SELONLY and EVO-sigma0.5.
- **Sandbox (illustrative, not the research engine).** Visitors evolve RS, NOSEL and EVO organisms in a Web Worker with seed, budget, sigma and training-design controls, then watch a returned organism forage, step by step.
- **Published results, assumptions, method and limitations**, all from `public/data/results.json`.

Numbers come only from `public/data/results.json`, written by `scripts/export_demo_data.py` from committed results; `tests/test_demo_export.py` checks that the file is reproducible and that every printed number appears verbatim in the manuscript. The page fails closed: if the file is missing or malformed, no number is shown.

## Sandbox fidelity

`src/engine.ts` ports the grid, the observation window, the 25-8-4 policy, the action rules and the scoring exactly; `src/engine.test.ts` replays 24 episodes produced by the Python engine (`scripts/export_sandbox_fixture.py`) and requires identical action sequences and scores (tolerance zero). The random-number generator differs from NumPy's, so a sandbox seed never reproduces a research run; the page labels the sandbox "illustrative, not the research engine".

## Commands

Node 22 or later; Google Chrome for the checker.

    npm ci && npm run build && npm run preview
    npm test                                   # vitest: results validator, engine port against the Python fixture
    node tools/a11y_check.mjs dist [--screenshots <dir>]

The checker serves `dist/` locally and checks: only same-origin requests, results render, keyboard reach and visible focus, WCAG AA contrast in light and dark schemes, no horizontal scroll at 360 px, no running animation under reduced motion, and that the page and sandbox work with the network switched off. EVOLVE adds the same contrast, overflow and keyboard checks with the sandbox output shown.

## Hosting

The built page (`dist/`) is hosted at https://evolve-artificial-life.kefimohamedbechir.workers.dev as Cloudflare Workers static assets on the free plan, with no Worker script (`wrangler.jsonc` names the assets folder only). The deployment is made by the lab coordinator, not by any script of this repository (owner, 2026-11-26, decision sheet, B2).
