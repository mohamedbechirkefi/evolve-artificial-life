# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Paired analysis over run seeds (protocol B.7). The unit is the run seed."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .errors import ConfigError


def _diffs(d: np.ndarray) -> np.ndarray:
    d = np.asarray(d, dtype=np.float64)
    if d.ndim != 1 or d.size < 2:
        raise ConfigError("need a 1-D array of at least two paired differences")
    if not np.all(np.isfinite(d)):
        raise ConfigError("paired differences contain non-finite values")
    return d


def cohen_dz(d: np.ndarray) -> float:
    """Mean paired difference divided by its sample SD (ddof=1); nan if the SD is 0."""
    d = _diffs(d)
    sd = d.std(ddof=1)
    return float(d.mean() / sd) if sd > 0 else float("nan")


@dataclass(frozen=True)
class PairedEstimate:
    n: int
    mean: float
    ci_low: float
    ci_high: float
    sd: float
    dz: float
    dz_ci_low: float
    dz_ci_high: float
    resamples: int
    seed: int


def paired_bootstrap(d: np.ndarray, resamples: int = 10_000, seed: int = 0, level: float = 0.95) -> PairedEstimate:
    """Percentile bootstrap over run seeds for the mean difference and d_z."""
    d = _diffs(d)
    if resamples < 100 or not (0 < level < 1):
        raise ConfigError("resamples must be >= 100 and level in (0, 1)")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, d.size, size=(resamples, d.size))
    samples = d[idx]
    means = samples.mean(axis=1)
    sds = samples.std(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        dzs = np.where(sds > 0, means / sds, np.nan)
    a = (1 - level) / 2 * 100
    lo, hi = np.percentile(means, [a, 100 - a])
    finite = dzs[np.isfinite(dzs)]
    if finite.size:
        dlo, dhi = np.percentile(finite, [a, 100 - a])
    else:
        dlo = dhi = float("nan")
    return PairedEstimate(
        n=int(d.size), mean=float(d.mean()), ci_low=float(lo), ci_high=float(hi),
        sd=float(d.std(ddof=1)), dz=cohen_dz(d), dz_ci_low=float(dlo), dz_ci_high=float(dhi),
        resamples=resamples, seed=seed,
    )


@dataclass(frozen=True)
class WilcoxonResult:
    n_nonzero: int
    w_plus: float
    z: float
    p_two_sided: float


def wilcoxon_signed_rank(d: np.ndarray) -> WilcoxonResult:
    """Wilcoxon signed-rank test, normal approximation, zeros dropped, tie-corrected
    variance, no continuity correction. Robustness check only (protocol B.7)."""
    d = _diffs(d)
    d = d[d != 0]
    n = d.size
    if n == 0:
        return WilcoxonResult(0, 0.0, float("nan"), float("nan"))
    absd = np.abs(d)
    order = np.argsort(absd, kind="stable")
    ranks = np.empty(n)
    sorted_abs = absd[order]
    i = 0
    tie_term = 0.0
    while i < n:
        j = i
        while j + 1 < n and sorted_abs[j + 1] == sorted_abs[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2 + 1
        t = j - i + 1
        tie_term += t**3 - t
        i = j + 1
    w_plus = float(ranks[d > 0].sum())
    mean = n * (n + 1) / 4
    var = n * (n + 1) * (2 * n + 1) / 24 - tie_term / 48
    if var <= 0:
        return WilcoxonResult(n, w_plus, float("nan"), float("nan"))
    z = (w_plus - mean) / math.sqrt(var)
    p = math.erfc(abs(z) / math.sqrt(2))
    return WilcoxonResult(n, w_plus, float(z), float(p))


def required_pairs(sd_diff: float, halfwidth: float, z: float = 1.96) -> int:
    """Run seeds needed for a normal-approximation CI half-width on the mean difference."""
    if sd_diff < 0 or halfwidth <= 0:
        raise ConfigError("sd_diff must be >= 0 and halfwidth > 0")
    return max(2, math.ceil((z * sd_diff / halfwidth) ** 2))


def minimum_detectable_difference(sd_diff: float, n: int, z_alpha: float = 1.96, z_beta: float = 0.8416) -> float:
    """Normal-approximation MDE of the mean paired difference at 80 percent power."""
    if n < 2 or sd_diff < 0:
        raise ConfigError("n must be >= 2 and sd_diff >= 0")
    return (z_alpha + z_beta) * sd_diff / math.sqrt(n)
