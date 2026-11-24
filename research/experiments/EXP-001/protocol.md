<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# EXP-001 protocol: evolutionary selection versus random search at equal evaluations

**Status: FROZEN v1.0 (owner-approved 2026-11-24).** The SHA-256 of this file is recorded in `research/freeze.json`, `research/experiment_registry.csv` and `research/decision_log.md` (D-010). Shared definitions (environment, policy, fitness, seeds) are in `research/protocol.md` Part B; this file states what is specific to EXP-001.

## 1. Precise question
At a fixed budget of E = 2000 policy evaluations, does evolutionary selection (EVO) return a foraging policy with higher held-out test fitness than independent random search (RS)?

## 2. Mechanism
Selection retains parents with high training fitness; mutation produces offspring near them. If fitness is locally correlated in parameter space, offspring of good parents are better than independent samples on average, so search concentrates budget in productive regions.

## 3. Rationale from verified sources
Simple genetic algorithms trained deep policies competitively on reinforcement learning tasks (Such et al. 2017, arXiv:1712.06567), and evolution strategies scale as a black-box alternative (Salimans et al. 2017, arXiv:1703.03864). Simple random search is itself a competitive baseline (Mania et al. 2018, arXiv:1803.07055; Bergstra and Bengio 2012, JMLR 13), so an evolutionary method must be compared with it at equal budget. Gap addressed: a small, fully reproducible, paired, held-out comparison of selection against random search and against a no-selection control in one grid world, with the uncertainty reported at the run level.

## 4. Competing explanations
(a) The advantage comes from local mutation search, not from selection (tested by NOSEL). (b) The advantage reflects overfitting to training environments (tested by the held-out and shifted sets and by EXP-003). (c) The advantage reflects a scoring exploit (exploit audit). (d) The advantage reflects the winner's curse in the returned-policy rule (all arms share the rule, and test fitness is measured on fresh environments). (e) NOSEL is a control for selection, not a competitor to RS: it is expected to score below RS (predeclared, see section 5), so a gap between EVO and NOSEL alone does not establish an advantage over independent sampling; the primary contrast is EVO minus RS.

## 5. Hypotheses
H0: `delta = E_s[F_test(EVO, s) - F_test(RS, s)] <= 0`. H1: `delta > 0`.

**Contradicting result:** the 95 percent paired bootstrap interval for `delta` has an upper bound at or below 0. An interval containing 0 is inconclusive, not equivalence.

**Predeclared expectation (not a tested hypothesis):** NOSEL is expected to score below RS on F_test, because a neutral random walk from 50 starts explores less than 2000 independent draws. The NOSEL minus RS difference is reported as a secondary estimate; NOSEL below RS is not evidence against the design. This expectation was informed by the exploratory pilot (J-0004, exploratory pool; NOSEL minus RS = -1.121 items, n = 10), disclosed in `research/freeze.json`.

## 6. Estimand
The mean over run seeds of the paired difference in held-out test fitness (food items per episode) of the returned policies, EVO minus RS, at E = 2000.

## 7. Experimental unit and simulation scope
Unit: one run (one run seed). Scope: the synthetic 16 x 16 toroidal foraging grid of `research/protocol.md` B.3 only.

## 8. Variables
Independent: search arm (RS, NOSEL, EVO). Dependent: F_test (primary); adaptation AUC, generalisation gap, F_shift, diversity, exploit-audit indicators (secondary). Fixed: E, K, M, T, architecture, test set.

## 9. Treatment, control, baseline
Treatment EVO (P = 50, G = 40, truncation top 10, elitism 1, sigma = 0.1). Control NOSEL (same, parents uniform at random). Baseline RS (2000 independent draws). Generation 0 matched to the first 50 RS draws.

## 10. Sampling and seed plan
Run seeds 0 to 29, paired across arms. Search, training-pool, test-pool and shifted-pool seeds come from separate `SeedSequence` spawn keys; disjointness is tested.

## 11. Sample-size rationale
n = 30 pairs gives about 80 percent power to detect d_z of about 0.53 at two-sided alpha 0.05 (planning approximation with the t correction, `research/protocol.md` B.6).

## 12. Fixed compute budget
2000 evaluations per run, each 5 episodes of 100 steps (1,000,000 environment steps), plus 200 test, 200 re-measured training and 200 shifted episodes for the returned policy. 90 runs (3 arms x 30 seeds). Wall-clock is recorded, not budgeted.

## 13. Metric formulas and units
`f(theta, e)` = food consumed in one episode (items). `F_test = mean over 200 test environments of f` (items per episode). Adaptation AUC = `(1/E) sum_{i=1..E} max_{j<=i} F_train(theta_j)` (items per episode). Generalisation gap = `F_train_fresh - F_test` (items per episode). Genotypic diversity = mean pairwise L2 distance in the final population (parameter units). Behavioural diversity = mean pairwise Hamming distance of action sequences on 20 probe environments divided by 2000 steps (fraction).

## 14. Uncertainty method
Paired percentile bootstrap over run seeds, 10,000 resamples, fixed analysis seed; d_z with bootstrap interval; per-seed values plotted; Wilcoxon signed-rank as robustness only.

## 15. Exclusion and stopping rules
As `research/protocol.md` B.8: rerun once on crash or failed invariant; persistent failures reported, pair dropped, worst-value sensitivity. Fixed n, no optional stopping.

## 16. Anticipated failure modes
Fitness plateau at 0 for all arms (task too hard: detected in smoke, fixed before freeze by changing food density, never after); ceiling at 24 (task too easy); argmax ties; non-determinism across processes; seed leakage between pools.

## 17. Sensitivity tests
Wilcoxon versus bootstrap agreement; worst-value imputation for failures; EXP-002 and EXP-003 conditions (budget, K, sigma).

## 18. Reproducibility commands
From the repository root, after `uv sync --frozen`: exploratory smoke check `./scripts/evolve smoke` (exploratory pool and seeds only); confirmatory run `./scripts/evolve run --config experiments/configs/EXP-001.json --workers 8` (writes `results/confirmatory/EXP-001/`; refused unless every hash in `research/freeze.json` matches); report `./scripts/evolve report --results results/confirmatory/EXP-001 --pdf`. Equivalent: `PYTHONPATH=src uv run python -m evolve <subcommand> ...`.

## Amendments before freeze (owner-approved 2026-11-24)

Applied to draft v0.1 to give v1.0, before any confirmatory run; see `research/protocol.md` Part C and D-010.

- Seeds raised from 20 (0 to 19) to 30 (0 to 29); sections 10, 11 and 12 updated (C.1).
- NOSEL expected below RS predeclared; sections 4 and 5 (C.3).
- Mutation sigma kept at 0.1 (C.4); no text change.
- Reproduction commands replaced with the implemented ones; section 18 (C.6).
- This file, `research/protocol.md` and `experiments/configs/EXP-001.json` are hashed in `research/freeze.json` (C.5).
