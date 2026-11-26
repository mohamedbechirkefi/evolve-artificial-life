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


## D-014 (2026-11-25): Funding, competing-interest and AI-use statements approved by the owner (post-M4 item 2)

- **Date:** 2026-11-25
- **Decided by:** the owner: owner, 2026-11-25, "Approve all" (post-M4), item 2 (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-25c.md`): "The wording drafted in each manuscript is approved. Where a draft still has a placeholder that needs a fact only the owner knows, it stays a placeholder. M5 lists any such placeholder for the owner." Recorded by the AI assistant under the coordinator brief `/Users/bechir/research/labs/_shared/POST-M4-brief.md`.
- **Decision:** the funding, competing-interest and AI-use wording in manuscript section 11 (`research/paper/manuscript.md` as of commit `6ca17dd`) is owner-approved. No wording was changed. Placeholders that need a fact only the owner knows stay as placeholders and are listed in `progress.md` under "Owner placeholders for M5".
- **Consequences:** no change to the manuscript, protocols, configs, seeds or results; no computation; `research/freeze.json` untouched. The unticked boxes in `research/publication/author_review.md` are left for the owner.

## D-015 (2026-11-25): M5 interactive experience

- **Authority:** the owner, 2026-11-25, "Next" (coordinator record `labs/_shared/owner-approvals-2026-11-25d.md`), which starts M5 in this repository with the stack it names: "The master prompt's default stack is used: TypeScript, React and Vite. Versions are pinned and come from the shared template, `labs/_shared/demo-template/`, which was verified on 2026-11-25." It decides no push, no freeze and no owner-only fact. Recorded by the AI assistant under the coordinator brief `labs/_shared/M5-brief.md`.
- **Stack and dependencies.** `demo/` is a copy of the template (React 19.3.1, Vite 8.3.5, Vitest 4.1.12, TypeScript 5.9.3, as pinned there) installed with `npm ci --prefer-offline`. No pinned version was changed and no dependency was added. Charts are hand-written SVG.
- **Exported results.** `scripts/export_demo_data.py` writes `demo/public/data/results.json` (`lab-demo-results` 1.0.0) from committed results only, with the SHA-256 of all 432 source files, `code_revision` 5d39c9bf (the commit of the confirmatory runs) and no timestamp. Entries: EXP-001 to EXP-003 (all registered experiments) and the exploratory pilot J-0004 and M4 re-analysis J-0012, labelled exploratory. Each estimate carries the manuscript's exact text, its interval, d_z and seed counts where the manuscript prints them, and its reading under the frozen rule. Project keys `arm_means`, `curves` and `replay` hold the arm means and SDs, best-so-far training-fitness quartiles over 30 seeds, and per-run training-fitness and parent traces for the replay; `validateResults` checks each of them and fails closed.
- **Documented exceptions to "verbatim in the manuscript".** (a) Arm SDs are printed in the experiment reports' TAB-1, not in the manuscript; the test checks each one verbatim there. (b) The replay shows single-run values (best-so-far training fitness, held-out F_test of one run) taken unrounded from committed run files; the page labels them "raw per-run value, not a manuscript number". (c) Curve quartiles are drawn, not printed, except in hover tooltips, which say what they are.
- **Equal weight for the sigma result.** The overview shows three findings as cards of identical size and mark weight: EXP-001 H1 supported (5.791, CI [4.644, 6.844]); EXP-002 "the frozen sigma 0.1 was not the best setting tested" (EVO minus EVO-sigma0.5 -1.776, CI [-2.519, -1.082]; sigma 0.5 exceeded it by 1.776; a contradicting result under EXP-002's rule, a finding against EXP-002's assumption about the setting; H1 of EXP-001 stands, per D-012); EXP-003 K1 inconclusive (0.751, CI [-0.533, 1.998]). The coordinator's brief called the owner decision "D-011"; in this repository it is D-012 (D-011 is the M3 record that raised it).
- **Project visual.** The master prompt (section 10) and roadmap name "animated organisms, ancestry and fitness curves with replay". Fitness curves and ancestry with generation-by-generation replay are drawn from the committed traces (measured). Animated organisms need policy parameters, which the committed results do not store, so they appear only in the sandbox, labelled as sandbox output.
- **Sandbox: illustrative, not the research engine.** `demo/src/engine.ts` ports the grid, observation, policy, action rules and scoring exactly; `demo/src/engine.test.ts` replays 24 episodes from the Python engine (fixture `demo/src/engine.fixture.json`, `scripts/export_sandbox_fixture.py`, J-0014) and requires identical actions and scores (tolerance zero; it passed with zero mismatches). The random streams (mulberry32 with Box-Muller instead of NumPy PCG64) and therefore layouts, initial policies and mutation noise differ, so the sandbox is labelled "illustrative, not the research engine" on the page. Budgets 500 or 2,000, sigma 0.02, 0.1 or 0.5, K = 5 resampled or K = 1 fixed, seed, run, cancel (terminates the worker) and reset.
- **Accessibility checker extended, not weakened.** `demo/tools/a11y_check.mjs` keeps every template check and adds step 8: with the sandbox output shown, contrast in both schemes, no overflow at 360 px, keyboard reach and visible focus. Verified to FAIL on a malformed `results.json`.
- **Owner review checklist.** The box "Author and affiliation metadata approved" in `research/publication/author_review.md` had been ticked by the AI assistant (commit fc69607). It was unticked: only the owner ticks these boxes. The recorded decision C3 is kept beside it.
- **Titles.** The owner's title approval of 2026-11-25 (post-M4, item 1) names SWARM, PULSE, CHAOS, STREAK, MATCH, FARE, HERD and VIRAL, not EVOLVE. The EVOLVE manuscript title therefore awaits the owner's decision; README says so.
- **Text consistency.** README rewritten for the actual state (it still described M2), `CITATION.cff` status and abstract, `articles/medium.md` and `articles/linkedin.md` drafted (none existed), `demo/README.md`, `articles/README.md`. Every decimal in these files appears in the manuscript (checked by script). Owner-only facts stay placeholders: repository URL, demo URL, funding and competing-interest facts ("none declared [to be confirmed by the owner]").
- **No change** to protocols, configs, seeds, results, the manuscript, the claims register or `research/freeze.json`; no confirmatory run; no push.

## D-016 (2026-11-25): M6 release candidate

- **Authority:** owner, 2026-11-25, "Next" (second) (coordinator record `labs/_shared/owner-approvals-2026-11-25e.md`), which starts "M6 (release candidate) in the 19 repositories whose M5 is done", including evolve: "M6 is local work: a clean clone, PDFs, checks, and a release candidate prepared for the owner's review." The same record says what it does not decide: no push, release, licence change or publication (G-PUBLIC), no ticking of any `author_review.md` box, no manuscript title beyond those approved on 2026-11-25, and no owner-only fact (repository and demo URL, funding, competing interests, author line, affiliation).
- **Coordinator default applied:** `CITATION.cff` has no `date-released` (it had none at the start of M6, so nothing was removed); re-adding it is part of the owner's publication step.
- **CITATION.cff choices:** version `0.1.0-rc1` (release candidate, no release made); title set to the manuscript title so that the two agree. The manuscript title itself still awaits the owner's decision (D-015), so both may change together. Structural CFF 1.2.0 check in `tests/test_citation_cff.py` (no YAML library is installed; the test parses the file's flat layout).
- **PDF builder (finding and fix).** The manuscript PDF failed to compile because the Typst root was the Markdown folder; `build_pdf` gained a `root` argument and `scripts/build_pdfs.py` builds the manuscript, supplementary file and three reports. Report PDFs had no title metadata; the builder now takes it from the first heading. After visual inspection: content-sized table columns, unjustified and hyphenated table text, captions kept with their tables. The builder's toolchain paths now default to the `.tools` folder next to the repository (no home-directory path in code).
- **PDFs committed.** No `.gitignore` rule or decision excludes them; each is under 0.5 MB. Typst intermediates are not committed.
- **Supplementary layout.** S1 run ids moved below the table, S3 hashes listed instead of tabled (values unchanged and checked against `research/freeze.json`), stale S5 sentence on PDFs replaced. No number changed.
- **Full texts consulted.** The free full texts of the nine cited papers (arXiv; JMLR open access) were consulted for the passages behind each citing sentence; the papers were not read cover to cover, and the labels say so. All cited claims hold. Two passages say more than the abstracts: Such et al. (2017, Section 3) describe truncation selection, Gaussian mutation and one elite, and Cobbe et al. (2019, pp. 3-5) train on a finite set of levels and test on held-out ones. The M4 sentences that stated what the abstracts lacked were updated in the manuscript (Section 2, Discussion, limitations), the three reports (version 1.2) and `research/limitations.md` item 20; the claims register, artifact manifest and demo data (source hashes and the literature limitation) were regenerated. No claim was strengthened beyond its passage; the frozen protocols keep their wording.
- **Checks added:** `scripts/check_links.py` with `tests/test_check_links.py`; `tests/test_text_numbers.py` (README, articles, demo README and CITATION abstract against the manuscript); `tests/test_pdf_builder.py`.
- **Home-directory paths in append-only and frozen files (note).** `progress.md` (2 lines) and this log (1 line, D-014) quote absolute paths to coordinator files, and the frozen `research/protocol.md` lists absolute tool paths (3 lines). They are left as written because these files are append-only or frozen; any public release should be read with this note.
- **Owner review checklist.** No box ticked; a "Prepared for the owner (M6, 2026-11-25)" section lists what to read, the open decisions and the remaining placeholders with file and line.
- **No change** to protocols, configs, seeds, raw results, frozen analyses, `research/freeze.json` or the licence files; no confirmatory run; no push, tag or release.

## D-017 (2026-11-26): owner answers to the decision sheet applied

- **Authority:** owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md`; answers in `labs/_shared/owner-approvals-2026-11-26.md`), applied under the coordinator brief `labs/_shared/OWNER-ANSWERS-brief.md`.
- **Applied (wording and configuration only):** A1 out-of-date "nothing is published" sentences corrected in `README.md`, `release_checklist.md` and `author_review.md` (the repository is public since 2026-11-25); B1 repository URL https://github.com/mohamedbechirkefi/evolve-artificial-life in `CITATION.cff` (`repository-code`, placeholder comment removed), `README.md`, manuscript section 10, articles and demo footer; B2 demo URL https://evolve-artificial-life.kefimohamedbechir.workers.dev in `README.md`, articles and demo footer, `demo/wrangler.jsonc` added (assets from `./dist`, no Worker script), hosting sentence in `demo/README.md`; B3 author line "Mohamed Bechir Kefi, independent researcher" in the manuscript, supplementary file, the three reports (version 1.3, identification table only), `CITATION.cff` (`affiliation: "Independent researcher"`), `README.md`, articles and demo footer, replacing the C3 form without affiliation (the frozen `research/freeze.json` keeps C3); B4 "No funding was received." and "The author declares no competing interests." in manuscript section 11, "[to be confirmed by the owner]" removed; B6 and B7 title approved, `CITATION.cff` already carries it; B8 version and date rule recorded in `release_checklist.md`; B9 home paths removed from `CLAUDE.md` (relative paths, tested), remainder listed in `reproducibility_report.md` section 7; B11 and B13 "Release notes (draft)" in `release_checklist.md`; B14 source labels accepted (recorded). B5 (AI-use statement), B10 (PDFs kept) and B12 (not applicable) need no change.
- **Generated files:** `manuscript.tex` regenerated with pandoc; the five PDFs rebuilt with `scripts/build_pdfs.py` (all five sources changed); `demo/public/data/results.json` re-exported (only the manuscript's source hash changed).
- **Not decided here:** B15 articles, B16 full-text review and sign-off (including R-EVOLVE-1), B18 release. No box in `research/publication/author_review.md` is ticked.
- **No change** to results, figures, configs, seeds, frozen protocols, `research/freeze.json`, checksummed outputs or licence files; no push and no deploy from this session.
