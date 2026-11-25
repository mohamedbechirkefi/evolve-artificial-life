<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Limitations (living document; M0 draft, updated M3 and M4)

Items 1 to 8 were written at M0 from the design; items 9 onwards follow the confirmatory runs.

1. **Simulation only.** All environments and agents are synthetic. Results hold only within the stated generator, grid size, food distribution and policy architecture.
2. **Claims boundary.** Improved task fitness is not general intelligence and is not evidence about biological evolution.
3. **One environment family.** External validity beyond the foraging grid is not tested; the shifted-distribution set is a narrow probe, not a general generalisation test.
4. **One architecture and fixed hyperparameters.** The arms use one small fixed network and one set of P, G and truncation values (plus a sigma sweep). Conclusions may not transfer to other settings.
5. **Fixed budget unit.** Budgets are counted in policy evaluations. A different accounting (environment steps, wall-clock) could change comparisons with methods that evaluate differently.
6. **Statistical power.** 20 seeds detect only moderate-to-large paired effects (d_z of about 0.66 at 80 percent power, planning approximation). Small effects may be missed; an inconclusive result is not equivalence.
7. **No TeX compilation.** LaTeX source is generated but not compiled locally (D-003).
8. **Literature review is not systematic.** Sources were selected by targeted search; see `research/literature_review.md`.

## Added after the confirmatory runs (M3, 2026-11-25)

Item 6 is superseded: the frozen design uses 30 seeds (d_z of about 0.53 at 80 percent power).

9. **The EVO advantage depends on the training design.** With K = 1 fixed training environment (EXP-003), the EVO minus RS held-out difference was inconclusive (0.751 items, CI [-0.533, 1.998]) while EVO's fixed-environment score and its overfitting drop exceeded RS's (C-009, C-010). The primary result (C-001) holds for resampled training environments (K = 5) and for E = 500, 2000 and 8000 only.
10. **The frozen primary sigma is not the best level tested.** Sigma 0.5 exceeded sigma 0.1 by 1.776 items (C-006). By the owner's decision of 2026-11-25 (D-012) this is a contradicting result under EXP-002's rule, a finding against EXP-002's assumption about the setting; H1 of EXP-001 stands. The EXP-001 effect size is specific to sigma 0.1 and is not an upper bound for evolutionary search in this task.
11. **Directions seen before the freeze.** The exploratory pilot (J-0004, separate pool) had shown the same direction for the primary contrast, the sigma 0.5 contrast and the budget conditions (C4 disclosure, `research/freeze.json`). The confirmatory pools and seeds were never used before the freeze.
12. **RS is independent sampling.** The baseline is not a tuned or local random search; conclusions do not extend to such methods. (M4 audit: the earlier attribution of local random search to Mania et al. 2018 was removed, because the abstract, the only part read, does not describe the method that way.)
13. **Contended wall-clock.** The confirmatory runs shared the machine with other workloads (load average up to about 89). Wall-clock and per-run timings are informational only; results are deterministic and unaffected.
14. **Optional sensitivity not run.** EXP-002's optional truncation-size test has no frozen config and was not run.

## Added in M4 (interpretation and evidence audit, 2026-11-25)

15. **No single-lineage local search comparator.** EVO differs from RS both by searching locally around good policies and by using a population under truncation selection. NOSEL removes selection and SELONLY removes local steps, but no arm is a hill climber or local random search that keeps the best policy. The results show that this genetic algorithm beats independent sampling, not that population-based selection beats local search in general (second review pass, R5).
16. **Budget confounded with population shape.** In EXP-003 the population size and generation count scale with the budget (E500: 25 x 20; E8000: 100 x 80; D-009 item 5). The larger EVO minus RS difference at larger budgets (C-015) is not an effect of the budget alone, and no trend test was frozen.
17. **Two readings of the K1 result.** The design cannot separate "selection fits a single layout" from "resampled, noisy training is what makes selected policies transfer", because each condition pairs selection with one training design. Intermediate K was not tested.
18. **Pilot-informed predeclarations.** The NOSEL expectation (C.3) and the seed count (C.1) were set after the exploratory pilot. NOSEL below RS is therefore not an independent prediction.
19. **No multiplicity adjustment in the frozen plan.** The exploratory M4 check with Bonferroni levels changed no reading (J-0012, C-017); it is not a substitute for a frozen adjustment.
20. **Targeted literature.** In M4 only the abstract or landing page of each cited source was read (re-opened 2026-11-25). In M6 (2026-11-25) the free full texts were consulted for the passages that support each citing sentence, not read cover to cover (`research/literature_review.md`, M6 section). Three report sentences that went beyond the abstracts (Such et al. operators, Mania et al. method, Cobbe et al. split) were corrected in the M4 audit; the frozen protocols keep their original wording, which cannot be edited after the freeze.
21. **Exploit audit coverage.** The audit checks stay-in-place behaviour, turns and the replay invariant. Other unintended scoring routes are not enumerated.
