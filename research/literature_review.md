<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Literature review (M0, targeted, not systematic)

Method: targeted web searches and direct retrieval of arXiv abstract pages and publisher pages on 2026-11-24. "Opened" means the abstract or landing page was retrieved and read in this session; full texts were not read, so only abstract-level statements are supported. This is not a systematic review.

## Verified (opened 2026-11-24)

| Key | Source | What it supports in this project |
|---|---|---|
| such2017deep | Such, Madhavan, Conti, Lehman, Stanley, Clune. "Deep Neuroevolution: Genetic Algorithms Are a Competitive Alternative for Training Deep Neural Networks for Reinforcement Learning". arXiv:1712.06567 (v1 18 Dec 2017). https://arxiv.org/abs/1712.06567 | A simple gradient-free genetic algorithm (mutation plus selection on network weights) is competitive on RL tasks. Reference design for the EVO arm. |
| salimans2017evolution | Salimans, Ho, Chen, Sidor, Sutskever. "Evolution Strategies as a Scalable Alternative to Reinforcement Learning". arXiv:1703.03864 (v1 10 Mar 2017). https://arxiv.org/abs/1703.03864 | Black-box evolutionary optimisation as an alternative to RL. Context, not replicated. |
| mania2018simple | Mania, Guy, Recht. "Simple random search provides a competitive approach to reinforcement learning". arXiv:1803.07055 (19 Mar 2018). https://arxiv.org/abs/1803.07055 | Random search is a strong baseline; large variability across seeds and hyperparameters. Motivates RS as primary comparator and many seeds. |
| bergstra2012random | Bergstra, Bengio. "Random Search for Hyper-Parameter Optimization". JMLR 13(10):281-305, 2012. https://www.jmlr.org/papers/v13/bergstra12a.html | Random search as a baseline for adaptive methods. |
| lehman2018surprising | Lehman, Clune, Misevic and 50 others. "The Surprising Creativity of Digital Evolution". arXiv:1803.03453 (v1 9 Mar 2018). https://arxiv.org/abs/1803.03453 | Evolving systems often exploit bugs and unintended scoring routes. Motivates the exploit audit. |
| krakovna2020specification | Krakovna, Uesato, Mikulik, Rahtz, Everitt, Kumar, Kenton, Leike, Legg. "Specification gaming: the flip side of AI ingenuity". DeepMind blog, 21 Apr 2020. https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/ | Definition of specification gaming; reward-exploit guard. |
| cobbe2019procgen | Cobbe, Hesse, Hilton, Schulman. "Leveraging Procedural Generation to Benchmark Reinforcement Learning". arXiv:1912.01588 (v1 3 Dec 2019). https://arxiv.org/abs/1912.01588 | Train/test split over procedurally generated levels to measure generalisation. Motivates disjoint seed pools. |
| agarwal2021precipice | Agarwal, Schwarzer, Castro, Courville, Bellemare. "Deep Reinforcement Learning at the Edge of the Statistical Precipice". arXiv:2108.13264 (v1 30 Aug 2021). https://arxiv.org/abs/2108.13264 | Interval estimates over runs rather than point estimates. |
| colas2018seeds | Colas, Sigaud, Oudeyer. "How Many Random Seeds?". arXiv:1806.08295 (v1 21 Jun 2018). https://arxiv.org/abs/1806.08295 | Seed-count and power reasoning; bootstrap and t-test assumptions. |
| henderson2017matters | Henderson, Islam, Bachman, Pineau, Precup, Meger. "Deep Reinforcement Learning that Matters". arXiv:1709.06560 (v1 19 Sep 2017). https://arxiv.org/abs/1709.06560 | Reproducibility and reporting practice; variance across seeds. |

## Unverified (not opened; must not be cited as read)

- Stanley and Miikkulainen, "Evolving Neural Networks through Augmenting Topologies", Evolutionary Computation 10(2):99-127, 2002, DOI 10.1162/106365602320169811. The DOI resolved to the MIT Press page, which returned HTTP 403. Metadata unverified.
- Lehman and Stanley, novelty search (2011). Not retrieved.

## Positioning (provisional)

Known: genetic algorithms and random search are both competitive black-box policy search methods, and evaluation with few seeds is unreliable. Narrow contribution proposed: a small, fully reproducible, preregistered paired comparison of selection, no-selection drift and random search at equal evaluation budget in one grid world, with held-out and shifted test sets, mutation and selection ablations, and a sensitivity analysis designed to be able to overturn the main reading. No novelty claim is made beyond this reproducible, transparently reported design.

## M4 re-check (2026-11-25, evidence audit)

Every verified source above was re-opened on 2026-11-25 (arXiv abstract pages, the JMLR landing page and the DeepMind blog post), and each citing sentence in the reports and the manuscript was compared with what the abstract states. All sources remain abstract-level (the blog post was read in full). Findings:

| Key | Abstract states | Wording corrected |
|---|---|---|
| such2017deep | a simple, gradient-free, population-based genetic algorithm evolves DNN weights and is competitive on hard deep RL tasks | The abstract does not name Gaussian mutation or truncation selection. EXP-001 and EXP-002 reports now say these operators are this project's choice. The "reference design" row above should be read in that sense. |
| mania2018simple | a random search method for static, linear policies in continuous control; large variability across seeds and hyperparameters | The abstract does not describe the method as local or as using a step rule. The EXP-001 report and limitation 12 no longer say so. |
| cobbe2019procgen | procedurally generated environments to measure sample efficiency and generalisation | The abstract does not describe a train and test level split. The EXP-003 report now says the split is this project's design. The "Motivates disjoint seed pools" row above is a motivation, not a statement of the source. |
| henderson2017matters | difficulty of reproduction from environment randomness and variance intrinsic to the methods; call for significance metrics and stricter reporting | The abstract does not mention seeds by name; the EXP-002 report now paraphrases the abstract. |
| salimans2017evolution, bergstra2012random, lehman2018surprising, krakovna2020specification, colas2018seeds, agarwal2021precipice | as in the table above | none needed |

The frozen EXP protocols (sections 3) keep their original wording, which cannot change after the freeze; the corrections are recorded here and in `research/publication/claims_audit.md`.
