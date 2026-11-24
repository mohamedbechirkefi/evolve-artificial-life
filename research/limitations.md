<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Limitations (living document, M0 draft)

No results exist yet. These are limitations known from the design.

1. **Simulation only.** All environments and agents are synthetic. Results hold only within the stated generator, grid size, food distribution and policy architecture.
2. **Claims boundary.** Improved task fitness is not general intelligence and is not evidence about biological evolution.
3. **One environment family.** External validity beyond the foraging grid is not tested; the shifted-distribution set is a narrow probe, not a general generalisation test.
4. **One architecture and fixed hyperparameters.** The arms use one small fixed network and one set of P, G and truncation values (plus a sigma sweep). Conclusions may not transfer to other settings.
5. **Fixed budget unit.** Budgets are counted in policy evaluations. A different accounting (environment steps, wall-clock) could change comparisons with methods that evaluate differently.
6. **Statistical power.** 20 seeds detect only moderate-to-large paired effects (d_z of about 0.66 at 80 percent power, planning approximation). Small effects may be missed; an inconclusive result is not equivalence.
7. **No TeX compilation.** LaTeX source is generated but not compiled locally (D-003).
8. **Literature review is not systematic.** Sources were selected by targeted search; see `research/literature_review.md`.
