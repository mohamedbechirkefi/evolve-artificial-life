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
