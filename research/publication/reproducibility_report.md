<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Reproducibility report (M6, 2026-11-25)

Every command below was run in the M6 session on the development machine (Apple M1 Pro, macOS 15.3.1, at most 2 workers). Outputs are quoted as printed. `<scratch>` stands for the session's scratch folder outside the repository; the clones were deleted at the end of the session.

## Checklist

- [x] Clean clone into a separate directory: `git clone -q <repository> <scratch>/clone`, HEAD 720d5f0 (local clone, no network).
- [x] `uv sync` from `uv.lock`: `uv sync --frozen --all-groups --all-extras` installed 17 packages (numpy 2.5.4, matplotlib 3.11.2, pytest 9.2.0, hypothesis 6.170.15 and their dependencies).
- [x] Test suite run: `.venv/bin/python -m pytest -q`: "146 passed in 42.96s".
- [x] Smoke reproduction, compared with the committed values: identical on every scientific field (details below).
- [x] Demo built offline and checked: `A11Y-CHECK PASS`.
- [x] Demo export determinism: re-export left `git status` clean.
- [x] Data manifest, artifact manifest, raw-result hashes and links verified (below).
- [x] Secret and licence scan (below; `research/publication/dependency_licences.md`).
- [ ] Known limitation, not a check: `manuscript.tex` is generated but not compiled locally (no TeX, D-003).

## 1. Clean clone at HEAD 720d5f0 (before the M6 changes)

| Step | Command (in the clone) | Actual output |
|---|---|---|
| Install | `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` (absolute path to the shared uv) | 17 packages installed; a second run printed "Audited 17 packages" |
| Tests | `.venv/bin/python -m pytest -q` | "146 passed in 42.96s" |
| Smoke | `PYTHONPATH=src .venv/bin/python -m evolve smoke --out <scratch>/smoke --workers 2` | "6 runs written", "report written" |
| Smoke comparison | `metrics.csv`, `summary.csv`, `contrasts_f_test.json` against `results/exploratory/smoke-2026-11-25/report/` | `contrasts_f_test.json` byte-identical. `metrics.csv` (6 rows, 29 columns): only `wall_seconds`, `peak_rss_bytes`, `git_revision` and `result_path` differ. `summary.csv` (3 rows, 47 columns): only `wall_seconds_mean` and `wall_seconds_max` differ. Every fitness, diversity, action-fraction, evaluation-count and replay value is identical (tolerance 0). |
| Raw-result validation | `.venv/bin/python scripts/validate_results.py results/confirmatory/EXP-00N` | "90 runs, 11 checks each, 0 failures"; "150 runs, ... 0 failures"; "180 runs, ... 0 failures" |
| Number audit | `.venv/bin/python scripts/audit_numbers.py` | sha mismatches 0 for EXP-001 (90 runs), EXP-002 (150), EXP-003 (180); 60 of 60 shared runs identical; raw problems 0; unmatched text values only 98.33 and 98.75 (Bonferroni levels, documented in `claims_audit.md`) |
| Demo install | `cd demo && npm ci --prefer-offline` | "added 53 packages in 1s" |
| Demo tests | `npm test` | "Test Files 2 passed (2)", "Tests 20 passed (20)" |
| Demo build | `npm run build` | index.html 0.77 kB, sandbox worker 5.03 kB, CSS 9.88 kB, JS 262.90 kB (82.52 kB gzip), "built in 463ms" |
| Accessibility and offline check | `node tools/a11y_check.mjs dist` (Google Chrome available) | 15 PASS lines, then "A11Y-CHECK PASS" (27 of 27 focusable elements, 12 of 12 sandbox controls, no request leaves the local origin, offline after first load) |
| Export determinism | `.venv/bin/python scripts/export_demo_data.py`; `.venv/bin/python scripts/export_sandbox_fixture.py`; `git status --short` | "wrote demo/public/data/results.json (1040882 bytes)", "wrote demo/src/engine.fixture.json (28987 bytes)"; `git status` printed nothing (0 lines) |

## 2. Findings in M6 and fixes

1. **Manuscript PDF could not be built** (finding). `build_pdf` used the Markdown folder as the Typst root, so the manuscript's figures under `research/experiments/` were outside it and the compile failed. Fix: `build_pdf(md_path, root=None)` in `src/evolve/report.py`, and `scripts/build_pdfs.py` builds all five PDFs with the right roots.
2. **Report and supplementary PDFs had no title metadata** (finding, pypdf). Fix: the builder sets the PDF title from the first level-1 heading when the Markdown has no YAML title.
3. **Table layout** (finding, visual inspection). Tables were justified with equal fixed column widths, so cells had wide gaps and one cell overlapped its neighbour ("generalisation" in EXP-001 TAB-2); "Table N." and "TAB-N." captions were left at the foot of a page while the table moved to the next. Fix in the builder: content-sized columns, unjustified and hyphenated table text at 0.88 em, and captions kept with their table. In the supplementary file the S1 run-id column and the S3 hash table overflowed; S1 now states the run-id pattern below the table and S3 lists the hashes (values unchanged and checked against `research/freeze.json`).
4. **Stale text** (finding). The supplementary S5 said "Report PDFs are not yet built (M6)"; it now names the PDFs and the build script.
5. **Absolute home-directory paths in code and reproduction files** (finding, scan). `src/evolve/report.py` and `scripts/evolve` now default to the shared `.tools` folder next to the repository (overridable by `EVOLVE_PANDOC`, `EVOLVE_TYPST_PYTHON` and `UV`); the three `reproduction.md` files say `uv sync ...`. The frozen `research/protocol.md`, `CLAUDE.md` (session instructions) and the append-only journals keep theirs (section 5).

## 3. PDFs (built with `.venv/bin/python scripts/build_pdfs.py`)

| PDF | Pages | Size | Title metadata | E-mail or local path in text or metadata |
|---|---|---|---|---|
| `research/paper/manuscript.pdf` | 17 | 0.40 MB | manuscript title | none |
| `research/paper/supplementary.pdf` | 4 | 0.10 MB | "Supplementary material" | none |
| `research/experiments/EXP-001/report.pdf` | 10 | 0.31 MB | report heading | none |
| `research/experiments/EXP-002/report.pdf` | 8 | 0.34 MB | report heading | none |
| `research/experiments/EXP-003/report.pdf` | 8 | 0.44 MB | report heading | none |

Every page of all five PDFs was rendered to PNG at 60 ppi (table pages also at 110 ppi) from the intermediate Typst files and inspected: no clipped figure, no raw Markdown, no missing glyph (minus signs, brackets and subscripts render), equations are written as inline code by design. `research/paper/manuscript.tex` was regenerated with pandoc and is not compiled (D-003).

## 4. References, links and manifests

- Citations: 10 in-text author-year citations, 10 bib entries, all resolved and all cited. Labels: read in full 1, full text consulted for the cited passage 9, abstract only 0, unverified 0 (`research/literature_review.md`, M6 section).
- Links: `.venv/bin/python scripts/check_links.py`: "29 relative links checked; 0 broken" (tested by `tests/test_check_links.py`). An extra scan of 169 backticked repository paths in the README, manuscript, supplementary, reports, reproduction files, articles and demo README found 16 short names (for example `analysis/analysis.json`) that are relative to a results folder named in the same sentence; none is broken.
- Numbers: `tests/test_text_numbers.py` checks that every decimal in `README.md`, the articles, `demo/README.md` and the `CITATION.cff` abstract appears in the manuscript (6 files, pass); the demo data are checked by `tests/test_demo_export.py`.
- `data/manifest.json`: no external or downloaded file to hash (synthetic data only, D-002); its own SHA-256 0d1dad1989d1a6d8013a974902d831b570e9f121a622acd782367d501a230f99 equals the value quoted in the supplementary file and the reports.
- `research/publication/artifact_manifest.json` (regenerated in M6 by `scripts/build_artifact_manifest.py`: "27 artifacts; 27 claims"): every referenced path exists, and all 27 `result_sha256` values match their files.
- `results/confirmatory/EXP-00N/sha256_manifest.json`: 184, 304 and 364 files hashed, 0 mismatches.

## 5. Secret, identifier and licence scan (tracked files, `git ls-files`, 1206 files before M6)

- E-mail addresses: 1 hit, the co-author commit-trailer address in `CLAUDE.md` (an instruction, not a personal address); 0 in `demo/package-lock.json`; 0 elsewhere.
- Tokens, keys and private-key headers: 0. `.env` files: 0.
- Absolute home-directory paths: 19 lines in 9 files before M6. Removed from `src/evolve/report.py` (2), `scripts/evolve` (1) and the three `reproduction.md` files (3). Kept: `research/protocol.md` (3, frozen file whose hash is in `research/freeze.json`), `CLAUDE.md` (7, the local toolchain instructions for sessions), `progress.md` (2) and `research/decision_log.md` (1), both append-only; a note is appended to each.
- Licences: `research/publication/dependency_licences.md`; no dependency flagged.
- SPDX headers: every text file added since M0 carries the header, except the raw `results/confirmatory/EXP-00N/run.log` files (raw outputs, not edited) and `demo/.npmrc`, which received the header in M6. JSON and CSV files are covered by `NOTICE.md`.
