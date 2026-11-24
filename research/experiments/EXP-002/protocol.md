<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# EXP-002 protocol: ablations of mutation and selection

**Status: DRAFT v0.1 (2026-11-24), not frozen, awaiting owner freeze (G-FREEZE). Protocol hash: not assigned until freeze.** Shared definitions are in `research/protocol.md` Part B. Depends on EXP-001 (reuses its EVO and NOSEL runs at the same code revision; if the revision differs, those arms are rerun).

## 1. Precise question
At E = 2000, how does held-out test fitness change when mutation is removed (SELONLY, sigma = 0), when selection is removed (NOSEL), and when mutation strength is set to sigma = 0.02 or 0.5 instead of 0.1?

## 2. Mechanism
Selection without variation can only re-pick initial individuals; variation without selection is a random walk. If both components are needed, EVO should exceed both ablations. Mutation strength trades exploitation (small sigma) against exploration (large sigma).

## 3. Rationale from verified sources
Ablation of the two components is required by the master prompt (section 10). Genetic algorithms with Gaussian mutation and truncation selection are the reference design of Such et al. 2017 (arXiv:1712.06567). Large variance across seeds and hyperparameters in simple search (Mania et al. 2018, arXiv:1803.07055) motivates the sigma sweep.

## 4. Competing explanations
Gains attributed to selection may come from the elite re-evaluation (more evaluations of good candidates); the elite is present in SELONLY too, so this is partly controlled. An optimal sigma could be an artefact of the fixed budget.

## 5. Hypotheses (secondary, estimation-focused)
H1a: EVO (sigma 0.1) > SELONLY. H1b: EVO > NOSEL. H0 for each: the paired mean difference is at most 0. No multiplicity-adjusted confirmatory claim is made; intervals are reported for all contrasts. Contradicting result: an ablation whose interval for (EVO minus ablation) lies entirely at or below 0.

## 6. Estimand
Paired mean differences in F_test between EVO (sigma 0.1) and each of SELONLY, NOSEL, EVO-sigma0.02, EVO-sigma0.5, over run seeds.

## 7. Experimental unit and scope
One run; the EXP-001 grid world only.

## 8. Variables
Independent: sigma in {0, 0.02, 0.1, 0.5} with truncation selection, and selection on or off at sigma 0.1. Dependent: F_test, adaptation AUC, diversity.

## 9. Treatment, control, baseline
Reference: EVO sigma 0.1 from EXP-001. Ablations as above. RS from EXP-001 is shown for context.

## 10. Sampling and seed plan
Run seeds 0 to 19, paired with EXP-001.

## 11. Sample-size rationale
Same as EXP-001 (n = 20, d_z of about 0.66 at 80 percent power for a single contrast); four contrasts are interpreted descriptively.

## 12. Fixed compute budget
E = 2000 per run; 60 new runs.

## 13. Metric formulas and units
As EXP-001 section 13.

## 14. Uncertainty method
Paired percentile bootstrap, 10,000 resamples; per-seed plots.

## 15. Exclusion and stopping rules
As `research/protocol.md` B.8.

## 16. Anticipated failure modes
SELONLY collapses to a single genotype quickly (expected, reported as diversity); sigma 0.5 behaves like random search.

## 17. Sensitivity tests
Repeat contrasts with the truncation size changed from 10 to 5 parents only if compute allows (optional, labelled exploratory if added after freeze).

## 18. Reproducibility commands (to exist after M2)
`uv run python -m evolve.run --exp EXP-002`, `uv run python -m evolve.report --exp EXP-002`.
