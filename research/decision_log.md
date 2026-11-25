<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Decision log

Append-only. Each entry: id, date, decision, decided by, rationale, alternatives, consequences.

## D-001 (2026-11-24): licence is the owner's custom non-commercial licence

- **Decided by:** the owner.
- **Decision:** all original material is licensed under the EVOLVE Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-EVOLVE-NC-Research-1.0`), with a CLA for contributions. Files: `LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CONTRIBUTING.md`, `.github/`.
- **Rationale:** the master prompt (section 2) asks for an "owner-approved permissive code license". On 2026-11-24 the owner chose this protective licence instead, for their own protection.
- **Consequences:** the code is source-available, not OSI open source; README and CITATION.cff say so. Data licences are recorded separately in `data/manifest.json`. Sessions do not change the licence files.

## D-002 (2026-11-24): no external dataset; synthetic procedurally generated environments

- **Decided by:** AI assistant (M0 proposal), subject to owner review.
- **Decision:** all environments are generated locally from recorded seeds by our own generator. Farama Minigrid (Apache-2.0, verified) was considered and not used.
- **Rationale:** the master prompt asks to build the grid environment; no licence or redistribution risk; full control of determinism and seed isolation tests.
- **Consequences:** results hold only within the synthetic environment family (external-validity limit recorded in `research/limitations.md`).

## D-003 (2026-11-24): zero-cost publication toolchain without TeX

- **Decided by:** AI assistant per the M0 brief, subject to owner review.
- **Decision:** Markdown is canonical. PDFs are built by pandoc 3.6.3 (`-t typst`) and compiled with the `typst` 0.15.0 Python package. `manuscript.tex` is generated from Markdown by pandoc and not compiled locally.
- **Rationale:** no TeX distribution is installed (`tex`, `pdflatex`, `xelatex` not found); installing one is not needed and Typst is free and local.
- **Consequences:** LaTeX output is unverified by compilation until a TeX toolchain is available; this is disclosed in the reproducibility report.

## D-004 (2026-11-24): dependency pinning by date cutoff

- **Decided by:** AI assistant per the M0 brief.
- **Decision:** `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-09T00:00:00Z"`, so `uv.lock` resolves only releases published at least two weeks before 2026-11-24. Runtime: numpy, matplotlib. Dev: pytest, hypothesis.
- **Consequences:** resolved versions are recorded in `uv.lock` (numpy 2.5.4, matplotlib 3.11.2, pytest 9.2.0, hypothesis 6.170.15).

## D-005 (2026-11-24): draft protocol v0.1 proposed, not frozen

- **Decided by:** AI assistant (proposal only).
- **Decision:** `research/protocol.md` Part B and EXP-001 to EXP-003 protocols are drafts. Primary comparator RS, primary metric held-out test fitness, 20 paired run seeds.
- **Consequences:** no confirmatory run until the owner freezes the protocols and records their SHA-256 here (G-FREEZE).

## D-006 (2026-11-24): exploratory runs never touch the confirmatory pools or seeds

- **Decided by:** AI assistant (M2), subject to owner review.
- **Decision:** test and shifted environments come from a pool selected by the config field `test_pool` (`confirmatory` = spawn pool 0, `exploratory` = spawn pool 1). Exploratory configs must use the exploratory pool and run seeds of at least 1000; confirmatory configs must use run seeds below 1000. Both rules are enforced by `evolve.config` and tested.
- **Rationale:** the smoke and pilot runs needed before the freeze must not consume or reveal the confirmatory held-out set (master prompt section 3: never tune on held-out evaluation data).
- **Consequences:** the pilot estimates seed spread on a statistically equivalent but disjoint set of environments. The confirmatory held-out layouts have not been evaluated by any policy.

## D-007 (2026-11-24): implementation choices where the draft protocol is silent

- **Decided by:** AI assistant (M2). Each item is a proposal for the owner to confirm or amend at freeze.
- **Decision:**
  1. NOSEL copies one uniformly random individual unchanged (mirror of the EVO elite slot, without selection) and draws its 49 parents uniformly from the whole population.
  2. Truncation ranks by training fitness with ties broken by evaluation order (stable sort). The returned policy is the first evaluation with maximal training fitness.
  3. Training environment of evaluation `i`, episode `k` is training-pool index `i*K + k` for that run seed (common random numbers across arms); with `train_fixed` (EXP-003 K = 1) every evaluation uses index 0.
  4. Mutation is unbounded Gaussian, `theta + sigma * N(0, I)`. Noise is drawn even for sigma = 0 so that all population arms of a run seed share one noise stream; parent choice uses a separate stream.
  5. Fresh training (`F_train_fresh`) and probe environments are per run seed; test and shifted environments are shared by all runs and arms.
  6. Argmax ties go to the lowest action index (forward). Hidden units have no separate bias (bias input only), giving 236 parameters.
  7. Shifted environments use the uniform generator with 16 food items on the same 16 x 16 grid and 100 steps.
- **Consequences:** the "project-specific verification" tests pin these behaviours (`tests/`).

## D-008 (2026-11-24): code layout, CLI and result format

- **Decided by:** AI assistant (M2).
- **Decision:** package `src/evolve/` (not installed; `pyproject.toml` keeps `package = false` and adds `pythonpath = ["src"]` for pytest). CLI entry `./scripts/evolve {smoke|run|report|test}` (equivalently `PYTHONPATH=src uv run python -m evolve ...`). Result schema `evolve.run_result` 1.0.0 (`src/evolve/schemas/run_result-1.0.0.json`), validated before any write and at every read; a self-contained validator avoids a new dependency. `run` refuses a confirmatory config unless the registry holds a 64-hex protocol hash equal to the protocol file's SHA-256 and a status containing "frozen". Exploratory per-run JSON files are git-ignored and regenerated deterministically; reports, manifests and configs are committed.
- **Consequences:** no dependency was added. The protocol drafts still cite `python -m evolve.run --exp ...`; that text is left unchanged for the owner (see D-009 item 6).

## D-009 (2026-11-24): proposed protocol amendments from the exploratory pilot (owner decision, not applied)

- **Decided by:** nobody yet. Proposals by the AI assistant, for the owner to accept or reject before the freeze. The analysis plan in `research/protocol.md` and the EXP protocols was not edited.
- **Evidence:** exploratory pilot J-0004 (`results/exploratory/pilot-2026-11-24/report/report.md`), exploratory pool, 10 seeds. Not a finding.
- **Proposals:**
  1. **Seed count.** Protocol B.6 says n rises to 30 if the full matrix fits in under 4 hours. The projection is 0.53 serial hours for 280 runs (contended machine). Proposal: n = 30 run seeds (0 to 29) for every experiment. Observed SD of paired F_test differences was 1.85 to 3.7 items; at n = 30 the normal-approximation MDE is about 0.9 to 1.9 items.
  2. **Generalisation gap under K = 1.** In the K1 condition the returned EVO policies scored 19.4 items on average on their single fixed training environment but 5.4 on the test set, while the protocol's gap (`F_train_fresh - F_test`, fresh environments from the training pool) was only 0.13, because fresh training-pool environments are not the fixed environment. Proposal: for K = 1 also report `F_train_fixed - F_test`, where `F_train_fixed` is the deterministic score on the fixed environment, as the overfitting measure of EXP-003.
  3. **NOSEL is weaker than RS.** NOSEL - RS was negative (mean -1.1 items) in the pilot: 50 starts plus small drift explore less than 2000 independent draws. The protocol's interpretation of EVO - NOSEL ("selection versus drift") stands, but the owner may want to state in advance that NOSEL is not expected to match RS, so this is not read post hoc.
  4. **Sigma.** EVO with sigma 0.5 exceeded sigma 0.1 by about 1.3 items in the pilot. sigma = 0.1 is a pre-registered choice and must not be re-tuned on held-out data; if the owner wishes to change the primary sigma, the choice must be recorded as informed by the exploratory pilot (exploratory pool, D-006), or kept at 0.1 with EXP-002 reporting the sweep.
  5. **Elitism in E500 and E8000.** Implemented as 1 elite with top 20 percent parents (5 of 25, 20 of 100). Confirm.
  6. **Reproducibility commands.** EXP protocol section 18 cites `python -m evolve.run --exp EXP-NNN`; the implemented commands are `./scripts/evolve run --config experiments/configs/EXP-NNN.json` and `./scripts/evolve report --results <dir>`.
  7. **Freeze record.** `evolve.freeze` checks the EXP protocol file's hash only. Proposal: the owner also records the SHA-256 of `research/protocol.md` and of each `experiments/configs/EXP-NNN.json` in this log at freeze.

## D-010 (2026-11-24): owner-approved amendments applied; protocol v1.0 frozen

- **Decided by:** the owner (G-FREEZE). The owner answered the M2 decision list on 2026-11-24 ("2. yes 3. yes 4. yes", "yes for all others"); the approved EVOLVE amendments, quoted from the coordinator's approvals file, are: "30 seeds."; "Add an overfitting measure for the K=1 condition: held-out drop against training fitness."; "Predeclare that NOSEL is expected below RS."; "Keep mutation sigma = 0.1."; "Also hash the main protocol and the configs at freeze."; "Fix the reproduction commands." Applied by the AI assistant.
- **Common decisions:** C1 synthetic data only; C2 PDFs with pandoc and Typst (Libertinus Serif), no LaTeX; C3 authorship "Mohamed Bechir Kefi", no affiliation, the AI disclosed as a research and development assistant, not an author; C4 exploratory values of the primary contrast seen before the freeze are disclosed (below).
- **Decision:** D-009 items 1, 2, 3, 4, 6 and 7 applied as amendments C.1 to C.6 (`research/protocol.md` Part C and each EXP protocol's "Amendments before freeze" section). Item 5 (elitism and parent counts in E500 and E8000) and the D-007 implementation choices were not listed among the approved amendments and stand as implemented and tested; no protocol text was changed for them. Code: result schema 1.1.0 with `f_train_fixed` and `overfit_drop` (null outside K = 1); report generator shows the K = 1 measure; the freeze guard now requires `research/freeze.json` and checks the SHA-256 of the main protocol, every EXP protocol and every confirmatory config, plus the canonical hash of the config being run.
- **Frozen files (SHA-256, at git revision ae69f92eb852f37d095e1b67dc27a926caf4c2a5):**
  - `research/protocol.md`: 3543a6fdf886c3c6fa0588344353eeb715e7706800884b165c2fe6378daa1e85
  - `research/experiments/EXP-001/protocol.md`: 21e0a7400c4b5b660937e416d6bb7a454c1e3f9f822bd6232f2381586a36253f
  - `research/experiments/EXP-002/protocol.md`: 40003226ba2ce3fbb3d8aac219a1028aee5a00e7d9dc0381b133aeedb3c419d4
  - `research/experiments/EXP-003/protocol.md`: 4e4d36f307a2c68ffd74ede9de6d8fa311f83b3348d68a50529ba1499cc7e76a
  - `experiments/configs/EXP-001.json`: aaaf6e09d7dbe223ae29e890f4ec74ec0d50219608594ce3b5aa78634999fdae
  - `experiments/configs/EXP-002.json`: 21c40e42e10e6fd482dfb813f65fbe1e3cdb6aa5492752005cdbaeb8e54d9248
  - `experiments/configs/EXP-003.json`: 5ed71f8434acaefd82a8bfe8e414d84782e3b87771bee3946d464075aca253b8
- **C4 disclosure:** exploratory values of the primary contrast EVO minus RS were seen before the freeze, on the exploratory pools and seeds only (D-006): pilot J-0004, main, 7.923 items, 95 percent CI [6.462, 9.529], n = 10; smoke J-0003, E = 200, 1.600 items, CI [-0.400, 3.600], n = 2. Also seen: NOSEL minus RS -1.121 items (informed C.3), EVO minus EVO-sigma0.5 -1.255 items (sigma nevertheless kept at 0.1), EVO minus RS at E500 4.361, E8000 8.801, K1 2.497, and the K1 fixed-environment score 19.4 against F_test 5.4 (informed C.2). Stored in `results/exploratory/{pilot,smoke}-2026-11-24/report/` (report.md TAB-2, contrasts_f_test.json) and `progress.md`. No policy has been evaluated on the confirmatory pools.
- **Record:** `research/freeze.json` (approval quote, C1 to C4, hashes, canonical config hashes, git revision). Registry statuses: "frozen (owner-approved 2026-11-24), not yet run".
- **Consequences:** `./scripts/evolve run` accepts the three frozen confirmatory configs and refuses any edited one (exit 3, tested). Confirmatory runs (M3) are scheduled by the coordinator on a quiet machine; none was run in this session. Any later change to a frozen file is a dated amendment analysed separately.

## D-011 (2026-11-25): M3 confirmatory runs; tooling added before the runs; items for the owner

- **Decided by:** the AI assistant under the coordinator's M3 brief (the owner said "Start next" on 2026-11-25). No protocol, config, seed, exclusion rule or frozen analysis was changed.
- **Before any confirmatory output (commit 5d39c9b):** added `scripts/run_confirmatory.sh` (runs the freeze-guarded CLI at `nice 10` and records run-time provenance: revision, config, freeze-record and data-manifest SHA-256, hardware, load, start and end times, exit status) and `scripts/analyse_frozen.py` (calls only the frozen `evolve.stats` functions with the frozen resamples and analysis seed; applies the frozen decision rule; orients contrasts as the protocols state them, EVO minus comparator; computes the EXP-003 K = 1 `overfit_drop` paired contrast named in the EXP-003 estimand; adds FIG-3 with the bootstrap intervals; writes SHA-256 manifests). Tests: `tests/test_analyse_frozen.py`. `scripts/validate_results.py` (metric identities, read-only checks) was added after the smoke run and was not used to compute any reported estimate.
- **Execution:** EXP-001 90/90, EXP-002 150/150 (as committed; its 60 EVO and NOSEL runs are identical to EXP-001's), EXP-003 180/180 runs ok, 0 failed, 0 retried, all at revision 5d39c9b with a clean tree. No deviation from the frozen protocol.
- **Outcomes under the frozen rules:** EXP-001 H1 supported (EVO minus RS 5.791 items, CI [4.644, 6.844]). EXP-002 H1a and H1b supported as estimates. EXP-003 robustness hypothesis not supported and not contradicted: E500 and E8000 positive, K1 inconclusive (0.751, CI [-0.533, 1.998]); by B.10 item 2 the main interpretation depends on resampled training.
- **For the owner:** (1) EXP-002's contradicting-result clause says "an ablation whose interval for (EVO minus ablation) lies entirely at or below 0". EVO minus EVO-sigma0.5 is -1.776, CI [-2.519, -1.082]. The records treat sigma 0.5 as a sweep level, not an ablation, so H1a and H1b stand; read literally, the clause would mark the sweep as contradicting. The owner decides the reading. (2) The 11.3 experiment reports (`research/experiments/EXP-NNN/report.md`) and `reproduction.md` files were not written in this session: the file-writing tool refused the report file and the coordinator instructed that the refusal must not be worked around. Drafts written earlier through the shell were deleted the same session. The reports remain owed (M3 acceptance item).

## D-012 (2026-11-25): owner decisions on the M3 items (D-011)

- **Decided by:** the owner, 2026-11-25, "approve all recommendations, RIGGED A" (coordinator file `labs/_shared/owner-approvals-2026-11-25.md`, items 4 and 10, outside this repository). Recorded by the AI assistant.
- **Item 10, EXP-002 sigma result (conservative reading).** Quoted from the approvals file: "The frozen sigma 0.1 was not the best setting tested: sigma 0.5 beat it by 1.78 [1.08, 2.52]." and "This is a finding against EXP-002's assumption about the setting, under the contradicting-result rule. H1 (EXP-001) stands." Consequence: the EVO minus EVO-sigma0.5 contrast (-1.776, CI [-2.519, -1.082]) is classified as a contradicting result under EXP-002's rule; H1a and H1b (SELONLY and NOSEL) are unaffected; EXP-001's H1 stands. Claims register C-006 and limitation 10 updated. No protocol, config, seed or analysis changed; no rerun.
- **Item 4, experiment reports.** Quoted: "The owner approves writing the missing 11.3/11.6 experiment reports (`report.md`, and `reproduction.md` where the repo uses it). They are written from the committed results, tables and figures only." and "Nothing is recomputed and no numbers change." The Write tool refused `research/experiments/EXP-001/report.md` again, and no other route was used. Following the coordinator's report-return note (report files are written by the coordinator, never by subagents), the AI assistant composed the three `report.md` and three `reproduction.md` files from committed results only and returned them as text to the coordinator, who writes and commits them. Three `reproduction.md` files briefly written with the Write tool before that note arrived were deleted in the same session. The M3 status line in `progress.md` is left to the coordinator.
- **Freeze record.** `research/freeze.json` has no deviation list and no frozen file or run changed, so it was not edited.

## D-013 (2026-11-25): M4 interpretation, evidence audit and manuscript synthesis

- **Authority:** the owner, 2026-11-25, "Approve all recommendations, push then next" (coordinator file `labs/_shared/owner-approvals-2026-11-25b.md`, item 5: M4 for each project that has finished M3). There is no EVOLVE-specific follow-up in that file. Recorded by the AI assistant.
- **Exploratory re-analysis (J-0012).** Cheap, labelled exploratory checks of the committed results only, no simulation: Bonferroni-level bootstrap intervals (EXP-002 family of 4, EXP-003 family of 3), Student t intervals, leave-one-seed-out readings, K1 without seed 13 and elite re-evaluation counts (`scripts/m4_sensitivity.py`, `results/exploratory/m4-sensitivity-2026-11-25/sensitivity.json`). Outcome: no registered reading changes. It never replaces a frozen verdict.
- **Evidence audit (J-0013).** `scripts/audit_numbers.py` recomputes summary tables and frozen contrasts from the 420 raw run files (0 mismatches) and scans every decimal in the reports, manuscript, supplementary, claims register and limitations against committed results (only Bonferroni level labels unmatched). Findings A1 to A11 in `research/publication/claims_audit.md`: malformed C-001 row repaired; stale registry status updated; four citation sentences in the reports corrected to abstract-level content (report version 1.1, no number changed); frozen protocols left unchanged and the wording disclosed.
- **Claims register restructured.** Columns `result_id`, `config_hash`, `figure_or_table` and `section` added; C-011 to C-017 (results) and C-020 to C-029 (external, abstract-level) added.
- **Manuscript.** Synthesised to 11.4 as v0.9, challenged by `research/publication/review_pass_2.md`, revised to v1.0 (nine changes, listed there). Supplementary file completed. `artifact_manifest.json` built by `scripts/build_artifact_manifest.py`.
- **Verdicts.** Unchanged: EXP-001 H1 supported; EXP-002 H1a and H1b supported as estimates, sigma 0.5 contradicting result for the setting (D-012); EXP-003 robustness not supported and not contradicted. The interpretation is narrowed: the result compares this genetic algorithm with independent sampling under resampled training, and no arm isolates single-lineage local search (limitations 15 to 21).
- **Not done:** manuscript and report PDFs (M6); no push.
