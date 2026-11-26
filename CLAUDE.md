<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# EVOLVE: how every session works

`master_prompt.md` is the authority for this repository. It is never edited. If this file and the master prompt conflict, the master prompt wins; record the conflict in `progress.md` and `research/decision_log.md`.

## 1. Reading order (before modifying anything)

1. `master_prompt.md`
2. `roadmap.md`
3. `progress.md`
4. `research/protocol.md`
5. `research/claims_register.csv`

Then run `git status` and inspect existing files. Do not overwrite changes made by the owner. State the current milestone and the next bounded task before starting work.

## 2. Mandatory requirements (master prompt section 11, made binding by 11.6)

- **Publication tree (11.1).** Maintain `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical, manuscript.tex and manuscript.pdf generated), `research/experiments/EXP-NNN/` (protocol.md, report.md, report.pdf, config.json, run_manifest.json, metrics.csv, figures/, reproduction.md) and `research/publication/` (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md).
- **Stable identifiers.** EXP-NNN for experiments, RUN ids for runs within an experiment, FIG ids for figures, C-NNN for claims. A seed is a run, not a new experiment. A new question or a materially different protocol gets a new EXP id.
- **Before each experiment (11.2).** A complete `EXP-NNN/protocol.md`, frozen with a version and SHA-256 hash and approved by the owner before held-out results are evaluated. Post-hoc changes are exploratory, dated and justified.
- **Every experiment gets a standalone report (11.3)** with the twelve mandatory sections, including failed, null, abandoned and exploratory experiments, each visibly labelled.
- **One integrated manuscript (11.4)**, 3,000 to 6,000 words where the evidence justifies it, status "independent research manuscript / preprint draft, not peer-reviewed". The abstract is drafted after analysis.
- **Evidence-to-publication pipeline (11.5).** Tables and figures are generated once from versioned results and reused everywhere. A manifest maps every number, table and figure to EXP id, run ids, metric definition, result path, generator script, config or protocol hash and code revision. A second review pass challenges the preferred hypothesis.
- **Milestone additions (11.6).** M0/M1: registry, manuscript skeleton, experiment protocols, zero-cost toolchain, freeze before execution. M2: versioned output schemas, reproducibility manifests and report generators alongside the core. M3: reports written as experiments finish; provenance captured at run time. M4: reports and evidence audit finished, synthesis into the manuscript, contradictory results and sensitivity included. M5: demo, paper, reports and articles use identical verified results. M6: compile and inspect PDFs, verify references and links, reproduce smoke results in a clean clone, complete the owner review checklist.
- **Publication gate.** Satisfied only when every registered experiment has a truthful standalone report, the manuscript is complete, all artifacts are traceable and remaining blockers are disclosed.
- **Toolchain (D-003).** There is no TeX distribution. PDFs are built as pandoc Markdown to Typst, compiled with the `typst` Python package in `../.tools/py/bin/` (the shared `.tools` folder next to this repository). `manuscript.tex` is generated from Markdown with pandoc and is not compiled locally. Never claim a PDF exists unless it was built and inspected.

## 3. Gates and rules

- **G-PUBLIC.** Never push, add a remote, create a GitHub repository or publish anything. Publication is the owner's decision. (The repository is public at https://github.com/mohamedbechirkefi/evolve-artificial-life since 2026-11-25; pushes and the demo deployment are made by the lab coordinator on the owner's word, never by a session in this repository.)
- **No paid service of any kind.** No paid API, inference, dataset, compute or hosting. The AI coding subscription is never an inference backend.
- **G-FREEZE.** Never freeze a protocol yourself. Freezing is the owner's decision. Until the owner records approval, every run is exploratory and labelled so.
- **No confirmatory experiments without a frozen, owner-approved protocol.** Tiny exploratory smoke checks are allowed and labelled exploratory.
- **Scope.** Work only inside this repository. Tools outside it are used read-only: `/usr/local/bin/python3`, `../.tools/py/bin/` (the shared `.tools` folder next to this repository) (uv, typst, pypdf, pillow), `../.tools/pandoc`, Node at `../../helix/.tools/node/bin` (relative to this repository) (never modify that folder), and git. Do not touch any other folder under the research root (the folder two levels above this repository). Never kill processes you did not start. Never delete anything you did not create in the current session.
- **Truthfulness.** Never fabricate results, citations, test counts or PDFs. Record commands and their actual outputs. Anything not verified is labelled unverified. Never mark incomplete work done.
- **Files and style.** New text and code files start with `SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0` as a comment where the format allows; JSON and CSV files are covered by `NOTICE.md`. English only. No em dashes. Plain, formal register. No e-mail address, personal identifier or secret in any committed file (git author metadata excepted). Refer to the owner as "the owner" (they/them).
- **Licence.** The licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `.github/`) are the owner's decision (D-001) and are not changed. Development commands may be appended to `CONTRIBUTING.md`.
- **Commits.** Local only, with the owner's git identity passed as `git -c user.name=<owner login> -c user.email=<owner address> commit` (the address is supplied by the session brief and is never written into a committed file), message ending with a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Run `git status` before and after.
- **Claims boundary.** Improved task fitness is never described as general intelligence or as evidence about biological evolution. All results are simulations and are labelled as such.

## 4. Session end

Append a dated entry to `progress.md` (decisions, commands, actual outputs, failures, changed files, risks, next action), update `roadmap.md` statuses, append decisions to `research/decision_log.md`, and append journal records to `research/experiment_journal.jsonl` for anything executed.

## 5. Commands

Run from the repository root; `../.tools/` is the shared toolchain folder next to it.

- Lock dependencies: `../.tools/py/bin/uv lock`
- Create the environment: `../.tools/py/bin/uv sync`
- Tests (from M2): `../.tools/py/bin/uv run pytest`
- Manuscript to LaTeX: `../.tools/pandoc research/paper/manuscript.md -s -o research/paper/manuscript.tex`, then prepend the line `% SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0`
- Manuscript to PDF: pandoc to Typst (`-t typst -V mainfont="Libertinus Serif"`; without a font the compile fails with "font fallback list must not be empty"), then `typst.compile(...)` with `../.tools/py/bin/python`
