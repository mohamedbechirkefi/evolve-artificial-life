<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Progress journal (append-only)

## 2026-11-24: Session M0 (bootstrap and feasibility, with M1 drafts)

**Milestone:** M0. **Next bounded task at start:** create the control files, audit feasibility, draft the protocol.

### Starting state
`git status`: on branch main, nothing to commit, working tree clean. One commit (146c0d1) with `master_prompt.md` and the owner's licence package. `master_prompt.md` was not modified.

### Commands and actual outputs
- `sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize`: `Apple M1 Pro`, `10`, `17179869184`.
- `sw_vers`: macOS 15.3.1, build 24D70.
- `df -h /Users/bechir/research/labs`: 460Gi size, 311Gi used, 128Gi available.
- `/usr/local/bin/python3 --version`: `Python 3.12.1`.
- `.tools/py/bin/uv --version`: `uv 0.9.5 (d5f39331a 2025-10-21)`.
- `.tools/pandoc --version`: `pandoc 3.6.3`.
- `.tools/py/bin/python -c "import typst, pypdf, PIL"`: typst 0.15.0, pypdf 6.20.0, pillow 11.3.0. Note: there is no `typst` executable in `.tools/py/bin/`; typst is available as a Python package only.
- `node --version` (helix tools, read-only): `v22.23.3`.
- `git --version`: `git version 2.42.1`.
- `which tex pdflatex xelatex`: all three not found.
- `uv lock`: `Using CPython 3.12.1 interpreter at: /Library/Frameworks/Python.framework/Versions/3.12/bin/python3`, `Resolved 19 packages in 1.16s`. Locked: numpy 2.5.4, matplotlib 3.11.2, pytest 9.2.0, hypothesis 6.170.15 (cutoff `exclude-newer = 2026-11-09`).
- Exploratory toolchain smoke check (J-0001, not an experiment):
  - `pandoc research/paper/manuscript.md -s -o research/paper/manuscript.tex`: exit 0, 127 lines (SPDX comment lines prepended afterwards).
  - `pandoc ... -t typst` then `typst.compile(...)`: first attempt failed with `typst.TypstError: font fallback list must not be empty`. Second attempt with `-V mainfont="Libertinus Serif"`: exit 0, 3-page PDF; first-page text extracted by pypdf showed the title, status line and author placeholder. The PDF was written to the session scratchpad only and is not committed (skeleton, no content).
- Literature: arXiv abstract pages for 1712.06567, 1803.07055, 1703.03864, 1803.03453, 1912.01588, 2108.13264, 1806.08295, 1709.06560, the JMLR page for Bergstra and Bengio 2012 and the DeepMind specification-gaming post were opened. The NEAT DOI page returned HTTP 403 (unverified). The Minigrid LICENSE file was opened (Apache License 2.0).

### Decisions
D-001 (owner's licence), D-002 (synthetic environments, no external data), D-003 (pandoc to Typst toolchain, no TeX), D-004 (date-cutoff lockfile), D-005 (draft protocol v0.1, not frozen). See `research/decision_log.md`.

### Changed files
Created: `CLAUDE.md`, `roadmap.md`, `progress.md`, `README.md`, `CITATION.cff`, `pyproject.toml`, `uv.lock`, `research/{protocol.md, decision_log.md, literature_review.md, limitations.md, claims_register.csv, experiment_journal.jsonl, experiment_registry.csv}`, `research/paper/{manuscript.md, manuscript.tex, references.bib, supplementary.md, figures/README.md}`, `research/experiments/EXP-00{1,2,3}/protocol.md`, `research/publication/{artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md}`, `data/{manifest.json, README.md}`, READMEs in `results/`, `src/`, `tests/`, `experiments/`, `demo/`, `articles/`. Modified: `CONTRIBUTING.md` (appended section 6, development commands only).

### Not done, and why
- No code, tests or experiments: M2 work, and confirmatory runs need the owner's freeze. No test has been run because none exists.
- `manuscript.pdf` not produced: there is no manuscript content yet.
- `manuscript.tex` is not compiled: no TeX distribution (D-003).
- EXP-NNN folders contain only `protocol.md`; report, config, manifest and metrics files are not created as placeholders (master prompt 11.1).

### Outstanding risks
Runtime per run is an estimate until the M3 smoke measurement. Task difficulty (food density) may need adjustment from smoke results before freeze. Literature support is abstract-level only.

### Next action
Owner: review and freeze (or amend) `research/protocol.md` and the three EXP protocols. Assistant: start M2 (environment, policy, arms, tests, schemas), which does not require the freeze.

## 2026-11-24: Session M2 (core implementation while the freeze is pending)

**Milestone:** M2. **Next bounded task at start:** implement the engine, arms, metrics, schema, manifests, runner, report generator, CLI and tests; run an exploratory smoke run and pilot to measure what the owner needs before the freeze.

### Starting state
`git status`: on branch main, clean, HEAD 3db3556. Protocol v0.1 and EXP-001..003 protocols unfrozen (registry hashes "not assigned").

### What was built
- `src/evolve/`: `config` (strict validation, equal-budget rule, canonical SHA-256 config hash), `seeds` (SeedSequence streams; confirmatory and exploratory pools), `env` (layout generator, vectorised batch engine with a replay invariant, scalar reference engine), `policy` (25-8-4, 236 parameters), `search` (RS, NOSEL, EVO, SELONLY with matched generation 0 and shared noise stream), `metrics`, `stats` (paired percentile bootstrap, d_z, Wilcoxon, MDE and required-n formulas), `runner` (retry once, failed runs recorded; per-run and matrix manifests with git revision, versions, OS, CPU, wall and CPU time, peak RSS), `schema` with `schemas/run_result-1.0.0.json`, `freeze` (read-only), `report` (CSV and Markdown tables, FIG-1 and FIG-2 as PNG and SVG, report manifest, PDF via pandoc to Typst with Libertinus Serif), `cli`.
- `scripts/evolve` wrapper; `experiments/configs/` with EXP-001..003 (draft, label confirmatory), `smoke.json` and `pilot.json` (exploratory).
- Implementation choices where the protocol is silent: D-007. Exploratory isolation: D-006. Layout and CLI: D-008.

### Commands and actual outputs
- `uv sync`: environment created from `uv.lock` (no dependency added).
- First full `uv run pytest -q -x`: `1 failed, 78 passed`. The failure was my own hand-computed golden value in `test_behavioural_diversity_golden` (I summed pairwise Hamming distances as 1 + 4 + 3; the correct sum is 1 + 4 + 4 = 9). The code returned 0.75 = 9/12, which is correct; the test was corrected.
- `uv run pytest -q`: `121 passed, 2 warnings` (overflow RuntimeWarnings from the deliberate non-finite mutation test; silenced with `np.errstate`). Then `./scripts/evolve test -q`: `121 passed in 5.77s`.
- Commit d06c290 (code and tests). Then `./scripts/evolve smoke --workers 0 --out results/exploratory/smoke-2026-11-24 --pdf`: `6 runs written`, report and 3-page PDF built (J-0003).
- `./scripts/evolve run --config experiments/configs/pilot.json --out results/exploratory/pilot-2026-11-24 --workers 8`: `120 runs written`, `1:40.17 total` (J-0004). `uptime` before the run: load averages 68.69 29.32 13.57 (the machine was shared with other work; all timings below are contended).
- Determinism re-check in a new process (J-0005): RS and EVO seed 1000 metrics identical to the stored pilot results (`True`, `True`); serial wall 3.91 s and 7.52 s at load average about 66.
- Report regenerated after the FIG-1 label fix (commit c84a46a): smoke PDF 3 pages, pilot PDF 5 pages, 2 embedded images each (pypdf). FIG-1 was inspected visually.
- `./scripts/evolve run --config experiments/configs/EXP-001.json` is refused with exit code 3 (tested in `tests/test_integration_cli.py`).
- J-0002: a development timing check before the tests existed (inline config, root seed 1, exploratory pool): RS 2.69 s, EVO 1.59 s per run; metrics printed to the terminal only.

### Exploratory measurements (pilot J-0004; exploratory pool, 10 seeds; NOT findings)
- Runtime per run (8 workers, load about 66): about 4 s at E = 2000 (3.9 to 4.4 s mean per arm), 1.3 to 1.5 s at E = 500, 20 to 21 s at E = 8000. Peak RSS per worker process 45 to 105 MB.
- Projected full matrix (EXP-001 60 runs, EXP-002 100 runs as configured, EXP-003 120 runs): 0.53 serial hours at about 2.5 ms per evaluation, about 0.07 hours on 8 workers if scaling were perfect. Well under the 4-hour threshold of protocol B.6.
- Seed spread: SD of paired F_test differences across the 12 pilot contrasts ranged from 1.85 to 3.68 items per episode (EVO - RS at E = 2000: 2.59). Normal-approximation MDE at 80 percent power: about 1.6 items at n = 20 and 1.3 items at n = 30 for EVO - RS. Within-arm SD of F_test: 0.9 to 2.9 items.
- Degenerate cases: no run failed or retried; no returned policy scored 0 on the test set; no run reached the 24-item ceiling (highest mean best training fitness 21.0, EVO at E = 8000); SELONLY final populations had zero genotypic and behavioural diversity in all 10 seeds (expected: no mutation); 3 returned policies stayed in place on more than half of the test steps (one K1 RS, one NOSEL, one SELONLY).
- Measure gap: under K = 1, EVO's best training fitness on its fixed environment averaged 19.4 items against 5.4 on the test set, while the protocol's generalisation gap (fresh training-pool environments) averaged 0.13. See D-009 item 2.
- Direction of the pilot contrasts is visible in `results/exploratory/pilot-2026-11-24/report/report.md`. These are exploratory planning numbers on a separate pool and must not be cited as evidence.

### Proposed amendments for the owner
D-009: n = 30 seeds; an `F_train_fixed - F_test` overfitting measure for K = 1; state in advance that NOSEL is expected to be weaker than RS; keep sigma = 0.1 unless the owner records a pilot-informed change; confirm elitism and parent counts for E500/E8000; update the reproducibility commands in EXP protocol section 18; also hash `research/protocol.md` and the EXP configs at freeze.

### Not done, and why
- No confirmatory run and no freeze (G-FREEZE). Protocol files were not edited.
- Per-experiment `report.md`, `config.json`, `run_manifest.json`, `metrics.csv` in `research/experiments/EXP-NNN/` are not created: they need confirmatory runs (M3); no placeholders.
- Typst PDF tables of the run reports wrap narrow columns (readable, not polished).
- No demo UI (M5). Nothing pushed.

### Changed files
New: `src/evolve/*` (14 modules and the schema), `tests/*` (7 files), `scripts/evolve`, `experiments/configs/*.json` (5), `results/exploratory/{smoke,pilot}-2026-11-24/` (configs, manifests, reports; per-run JSON git-ignored). Modified: `pyproject.toml` (pytest pythonpath), `.gitignore`, `README.md`, `roadmap.md`, `progress.md`, `CONTRIBUTING.md` (section 6 appended), `data/manifest.json`, `research/{decision_log.md, experiment_journal.jsonl, experiment_registry.csv}`, READMEs of `src/`, `tests/`, `results/`, `experiments/`.

### Outstanding risks
Timings were measured on a heavily loaded machine; the projection is still two orders of magnitude below the budget. The pilot shows large planning effects in the main contrast, so the informative uncertainty sits in EXP-003 and the ablations; the owner should decide amendments knowing that the pilot direction has been seen (exploratory pool only).

### Next action
Owner: review D-007 and D-009, amend if wished, then freeze `research/protocol.md`, the EXP protocols and the configs, recording hashes in the registry and decision log. Assistant (after freeze): M3, run EXP-001..003 with `./scripts/evolve run`, and write the 11.3 reports.
