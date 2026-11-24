<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# EXP-003 protocol: robustness to budget and training-set size

**Status: FROZEN v1.0 (owner-approved 2026-11-24).** The SHA-256 of this file is recorded in `research/freeze.json`, `research/experiment_registry.csv` and `research/decision_log.md` (D-010). Shared definitions are in `research/protocol.md` Part B. Depends on EXP-001.

## 1. Precise question
Does the EVO minus RS difference in held-out test fitness keep its sign at E = 500 and E = 8000, and when each evaluation uses one fixed training environment (K = 1) instead of five resampled ones?

## 2. Mechanism
At small budgets selection has few generations to act; at large budgets random search may find good policies by chance. With one fixed training environment, selection can exploit that layout and overfit, which held-out fitness would reveal.

## 3. Rationale from verified sources
Training on a fixed set of levels and testing on held-out levels exposes overfitting in reinforcement learning (Cobbe et al. 2019, arXiv:1912.01588). Conclusions from point estimates over few runs can change under proper interval estimation (Agarwal et al. 2021, arXiv:2108.13264); seed counts must be justified (Colas et al. 2018, arXiv:1806.08295).

## 4. Competing explanations
A sign change across budgets indicates a budget-dependent interaction, not a general advantage. A test-fitness drop under K = 1 with unchanged training fitness indicates overfitting rather than failed search.

## 5. Hypotheses
H1 (robustness): the paired difference EVO minus RS is positive in every condition. H0: in at least one condition the difference is at most 0. Contradicting result: any condition whose 95 percent interval lies at or below 0. This experiment is the planned sensitivity analysis that can invalidate the EXP-001 interpretation (`research/protocol.md` B.10 items 1 and 2).

## 6. Estimand
Paired mean differences in F_test (EVO minus RS) for each of: E = 500 (P = 25, G = 20), E = 8000 (P = 100, G = 80), and E = 2000 with K = 1. In the K = 1 condition, also the per-arm mean of `overfit_drop = F_train_fixed - F_test` and its paired EVO minus RS difference (secondary, the overfitting measure).

## 7. Experimental unit and scope
One run; the EXP-001 grid world only.

## 8. Variables
Independent: budget E, training design K. Dependent: F_test, F_train_fresh, generalisation gap; in the K = 1 condition also F_train_fixed and overfit_drop.

## 9. Treatment, control, baseline
EVO against RS in each condition; truncation keeps the top 20 percent; sigma 0.1.

## 10. Sampling and seed plan
Run seeds 0 to 29, paired across arms within each condition. For K = 1 the single training environment is the first training-pool environment for that run seed.

## 11. Sample-size rationale
As EXP-001 per condition; three conditions are interpreted jointly without a multiplicity-adjusted confirmatory claim.

## 12. Fixed compute budget
180 runs (3 conditions x 2 arms x 30 seeds); the E = 8000 runs are the most expensive (four times EXP-001) and are the first cut under `research/protocol.md` B.12.

## 13. Metric formulas and units
As EXP-001 section 13, plus, for K = 1 only: `F_train_fixed` = food consumed (items) by the returned policy in one episode on the fixed training environment (training-pool index 0 of the run seed; deterministic, so one episode suffices), and `overfit_drop = F_train_fixed - F_test` (items per episode). Both are null in the E500 and E8000 conditions. Under K = 1 the generalisation gap `F_train_fresh - F_test` is reported but is not the overfitting measure, because fresh training-pool environments are not the fixed environment.

## 14. Uncertainty method
Paired percentile bootstrap per condition, 10,000 resamples.

## 15. Exclusion and stopping rules
As `research/protocol.md` B.8.

## 16. Anticipated failure modes
Ceiling effects at E = 8000 that compress differences; K = 1 environments with too little food near the start.

## 17. Sensitivity tests
Report the E = 2000, K = 5 values from EXP-001 alongside as the reference condition.

## 18. Reproducibility commands
From the repository root, after `uv sync --frozen`: `./scripts/evolve run --config experiments/configs/EXP-003.json --workers 8` (writes `results/confirmatory/EXP-003/`; refused unless every hash in `research/freeze.json` matches), then `./scripts/evolve report --results results/confirmatory/EXP-003 --pdf`.

## Amendments before freeze (owner-approved 2026-11-24)

Applied to draft v0.1 to give v1.0, before any confirmatory run; see `research/protocol.md` Part C and D-010.

- Seeds raised from 20 to 30 (0 to 29); sections 10 and 12 updated (C.1).
- Overfitting measure for K = 1 added: `overfit_drop = F_train_fixed - F_test`; sections 6, 8 and 13 (C.2).
- Mutation sigma kept at 0.1 (C.4).
- Reproduction commands replaced with the implemented ones; section 18 (C.6).
- This file, `research/protocol.md` and `experiments/configs/EXP-003.json` are hashed in `research/freeze.json` (C.5).
