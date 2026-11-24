# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Search arms at equal evaluation budgets (protocol B.4).

RS       E independent draws theta ~ N(0, init_std^2 I).
NOSEL    population search; parents and the copied individual chosen uniformly
         at random (no selection, neutral drift).
EVO      population search; truncation selection, top fraction are parents,
         `elitism` best individuals copied unchanged (and re-evaluated).
SELONLY  EVO with sigma = 0.

One evaluation = one policy scored on K training episodes. Every evaluation,
including the re-evaluation of a copied elite, counts towards the budget.
Generation 0 of population arms equals the first P draws of RS for the same
run seed (matched starts). Mutation noise comes from a stream shared by all
population arms of a run seed (common random numbers).

The returned policy of every arm is the evaluated policy with the highest
training fitness; ties go to the earliest evaluation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

from .config import ArmSpec, PolicyParams
from .errors import ConfigError, InvariantError
from .policy import n_params, sample_initial

# evaluate(thetas (B, D), evaluation_ids (B,)) -> training fitness (B,)
Evaluator = Callable[[np.ndarray, np.ndarray], np.ndarray]


@dataclass
class SearchTrace:
    thetas: np.ndarray  # (E, D) every evaluated parameter vector, in evaluation order
    train_fitness: np.ndarray  # (E,) items per episode, mean over K episodes
    parent_index: np.ndarray  # (E,) evaluation id of the parent, -1 if none
    generation: np.ndarray  # (E,) generation (RS: chunk) index
    final_population: np.ndarray  # (P,) evaluation ids of the last generation / last P RS draws

    @property
    def n_evaluations(self) -> int:
        return int(self.train_fitness.shape[0])

    @property
    def returned_index(self) -> int:
        return int(np.argmax(self.train_fitness))

    def best_so_far(self) -> np.ndarray:
        return np.maximum.accumulate(self.train_fitness)


def mutate(parents: np.ndarray, sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Gaussian mutation theta' = theta + sigma * N(0, I).

    The noise is always drawn (even for sigma = 0) so that the noise stream
    stays aligned across arms with different sigma. Parents are not modified.
    """
    if isinstance(sigma, bool) or not isinstance(sigma, (int, float)) or not math.isfinite(sigma) or sigma < 0:
        raise ConfigError(f"sigma must be a finite number >= 0, got {sigma!r}")
    parents = np.asarray(parents, dtype=np.float64)
    if parents.ndim != 2:
        raise ConfigError("parents must be a 2-D array")
    noise = rng.standard_normal(parents.shape)
    with np.errstate(over="ignore", invalid="ignore"):
        children = parents + float(sigma) * noise
    if not np.all(np.isfinite(children)):
        raise InvariantError("mutation produced non-finite parameters")
    return children


def _check_fitness(f: np.ndarray, n: int) -> np.ndarray:
    f = np.asarray(f, dtype=np.float64)
    if f.shape != (n,) or not np.all(np.isfinite(f)):
        raise InvariantError("evaluator returned malformed or non-finite fitness")
    return f


def random_search(
    arm: ArmSpec,
    policy: PolicyParams,
    init_rng: np.random.Generator,
    evaluate: Evaluator,
) -> SearchTrace:
    if arm.kind != "random_search":
        raise ConfigError(f"arm {arm.name!r} is not a random_search arm")
    e, p = arm.total_evaluations, arm.population_size
    thetas = sample_initial(init_rng, e, policy.hidden_units, policy.init_std)
    fitness = np.empty(e)
    for start in range(0, e, p):
        ids = np.arange(start, min(start + p, e))
        fitness[ids] = _check_fitness(evaluate(thetas[ids], ids), ids.size)
    return SearchTrace(
        thetas=thetas,
        train_fitness=fitness,
        parent_index=np.full(e, -1, dtype=np.int64),
        generation=np.arange(e, dtype=np.int64) // p,
        final_population=np.arange(e - p, e, dtype=np.int64),
    )


def population_search(
    arm: ArmSpec,
    policy: PolicyParams,
    init_rng: np.random.Generator,
    parent_rng: np.random.Generator,
    noise_rng: np.random.Generator,
    evaluate: Evaluator,
) -> SearchTrace:
    if arm.kind != "population":
        raise ConfigError(f"arm {arm.name!r} is not a population arm")
    p, g_total = arm.population_size, arm.generations
    e = arm.total_evaluations
    d = n_params(policy.hidden_units)
    thetas = np.empty((e, d))
    fitness = np.empty(e)
    parent_index = np.full(e, -1, dtype=np.int64)
    generation = np.repeat(np.arange(g_total, dtype=np.int64), p)

    ids = np.arange(p)
    thetas[ids] = sample_initial(init_rng, p, policy.hidden_units, policy.init_std)
    fitness[ids] = _check_fitness(evaluate(thetas[ids], ids), p)
    current = ids
    n_children = p - arm.elitism

    for g in range(1, g_total):
        fit = fitness[current]
        order = np.argsort(-fit, kind="stable")
        if arm.selection == "truncation":
            pool = current[order[: arm.n_parents]]
            copied = current[order[: arm.elitism]]
        else:
            pool = current
            copied = current[parent_rng.choice(p, size=arm.elitism, replace=False)] if arm.elitism else current[:0]
        choice = parent_rng.integers(0, pool.size, size=n_children)
        parents = pool[choice]
        children = mutate(thetas[parents], arm.sigma, noise_rng)
        new_ids = np.arange(g * p, (g + 1) * p)
        thetas[new_ids[: arm.elitism]] = thetas[copied]
        thetas[new_ids[arm.elitism :]] = children
        parent_index[new_ids[: arm.elitism]] = copied
        parent_index[new_ids[arm.elitism :]] = parents
        fitness[new_ids] = _check_fitness(evaluate(thetas[new_ids], new_ids), p)
        current = new_ids

    return SearchTrace(
        thetas=thetas,
        train_fitness=fitness,
        parent_index=parent_index,
        generation=generation,
        final_population=current,
    )
