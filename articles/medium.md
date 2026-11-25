<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Can useful behaviour emerge without hand-coding it? A preregistered test in a toy world

*Draft for Medium. Not published; publication is the owner's decision. Simulation study; the underlying manuscript is an independent preprint draft, not peer-reviewed.*

Nobody tells the small foraging agents in this study what to do. Each one is a tiny neural network that sees a 5 x 5 patch of a 16 x 16 grid and chooses to step forward, turn or stay. Some patches hold food. The question is whether a simple evolutionary process, copying the better networks with small random changes, finds better foragers than simply drawing networks at random, when both get exactly the same number of tries.

## The question

Within a fixed budget of policy evaluations, does evolutionary selection with inherited, mutated policies find foraging policies with higher fitness on held-out grid environments than independent random search, and does any advantage survive changes in budget, mutation strength and training-set size?

Random search is a serious baseline. It is the natural yardstick for adaptive search methods, and results in this area are known to vary with seeds and evaluation details. So the comparison has to be fair: same budget, same network, same held-out test layouts, paired seeds and intervals rather than single runs.

## How it was tested

Three ways of searching each got 2,000 evaluations, where one evaluation scores one network on five training layouts:

- **RS**: 2,000 independent random networks.
- **EVO**: a population of 50 over 40 generations; the best 10 become parents, children get Gaussian mutations (sigma 0.1), one elite is kept.
- **NOSEL**: the same population, but parents are chosen at random, so there is mutation without selection.

Each method returns the network with the best training score, which is then scored on 200 held-out layouts it never saw. The protocol, including the decision rule, was frozen before any confirmatory run, and all 420 planned runs completed. Two further experiments removed mutation or selection, changed the mutation strength, and changed the budget and the training design.

*Figure suggestion (from the demo page, `docs/demo.png`): the three findings with their 95 percent intervals on a shared axis. Alt text: three interval plots; EVO minus RS 5.791 with interval [4.644, 6.844] well right of zero; EVO minus EVO-sigma0.5 -1.776 with interval [-2.519, -1.082] left of zero; K1 EVO minus RS 0.751 with interval [-0.533, 1.998] crossing zero.*

## What was measured

All numbers are food items per episode on the held-out layouts, as mean paired differences over 30 run seeds with 95 percent bootstrap intervals.

- **Selection beat random search.** EVO exceeded RS by 5.791 items, CI [4.644, 6.844], in 29 of 30 paired seeds. Under the frozen rule the primary hypothesis is supported.
- **Both ingredients matter.** Without mutation (SELONLY) EVO's advantage was 8.297, CI [7.608, 8.956]; without selection (NOSEL), 8.046, CI [7.173, 8.874]. Neither part alone reproduces the result.
- **The setting I froze was not the best one.** The frozen mutation strength of 0.1 lost to 0.5: EVO minus EVO-sigma0.5 was -1.776, CI [-2.519, -1.082]. This is a finding against the experiment's assumption about the setting, classified as a contradicting result under its rule. The primary result stands, but its size is specific to sigma 0.1 and is not an upper bound.
- **The advantage depends on how training works.** It held at 500 evaluations (2.368, CI [1.627, 3.128]) and at 8,000 (8.374, CI [7.418, 9.287]). With one fixed training layout instead of five fresh ones, it was inconclusive (0.751, CI [-0.533, 1.998]), and EVO overfit that layout more than RS. Inconclusive is not the same as "no difference".

## Limitations

This is a toy world chosen for reproducibility. One grid family, one network size, fixed population settings. The baseline is independent sampling, not a tuned or local random search, and no arm isolates a single-lineage hill climber, so the study does not show that population-based selection beats local search in general. Budgets are counted in evaluations. Improved task fitness here is not general intelligence and is not evidence about biological evolution. The full list is in the manuscript's limitations section.

## Reproduce it

Every number above is mapped to its result file in the artifact manifest; the frozen protocols, raw runs and analysis script are in the repository. An interactive page lets you replay the committed runs generation by generation and evolve your own organisms in a labelled sandbox.

Repository: [placeholder, not published; release requires the owner's approval]. Demo: [placeholder, not published].

*AI assistance: an AI system was used as a research and development assistant for code, analysis and drafting, under the author's direction; it is not an author.*
