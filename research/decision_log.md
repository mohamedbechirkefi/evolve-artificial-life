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
