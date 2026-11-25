<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# LinkedIn draft (not published; publication is the owner's decision)

Does a simple evolutionary process beat random guessing when both get the same budget?

I built a small, preregistered simulation to check. Tiny neural networks forage in a 16 x 16 grid. Random search and a simple genetic algorithm each got 2,000 evaluations, with the protocol frozen before any confirmatory run and all 420 planned runs completed.

One defensible finding: on 200 held-out layouts, the genetic algorithm's foragers collected 5.791 more food items per episode than random search's (95 percent CI [4.644, 6.844], 30 paired seeds).

Two results cut the other way, and they matter as much. The mutation strength I froze (0.1) was not the best tested: 0.5 beat it by 1.776 items. And with a single fixed training layout, the advantage was inconclusive (0.751, CI [-0.533, 1.998]).

Caveat: a toy simulation with one environment family and an untuned random-search baseline. It says nothing about biological evolution or general intelligence. Independent preprint draft, not peer-reviewed.

Repository: [placeholder, not published]. Interactive demo: [placeholder, not published].
