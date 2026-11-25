<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Limitations (living document; M0 draft, updated M3)

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
12. **RS is independent sampling.** The baseline is not a tuned local random search (Mania et al. 2018); conclusions do not extend to such methods.
13. **Contended wall-clock.** The confirmatory runs shared the machine with other workloads (load average up to about 89). Wall-clock and per-run timings are informational only; results are deterministic and unaffected.
14. **Optional sensitivity not run.** EXP-002's optional truncation-size test has no frozen config and was not run.
