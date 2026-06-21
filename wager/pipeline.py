"""WAGER pipeline: per-model e-value / information channels with R-permutation driver.

Implements the driver of algorithm.md section 4 (lines 1-13): for each random
image-blocked permutation, fit the self-prior projection on fold A, stream the
betting process on fold B, and read off the e-value (Thm 1), reasoning info
(Thm 2/4) and prior info.  Results are aggregated over R permutations.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .core import (
    betting_mean_ci,
    betting_mean_point,
    kt_projection,
    prior_excess_logscore,
    wealth_process,
)


@dataclass
class ModelData:
    """Cached predictive distributions for one model on one benchmark."""

    name: str
    q: np.ndarray          # (N, K) predictive distributions
    y: np.ndarray          # (N,)   ground-truth labels
    phi: np.ndarray        # (N,)   prior-feature cell ids
    group: np.ndarray | None = None   # (N,) image ids for blocked permutation

    @property
    def K(self) -> int:
        return self.q.shape[1]

    @property
    def N(self) -> int:
        return self.q.shape[0]


@dataclass
class WagerResult:
    """Aggregated WAGER readouts for one model."""

    name: str
    e_value: float
    e_values_per_perm: np.ndarray
    I_reason: float
    I_reason_ci: tuple
    I_prior: float
    I_prior_ci: tuple
    I_tot: float
    growth: float
    # per-permutation per-instance scores, kept for paired RGR computation
    d_streams: list = field(default_factory=list)
    e_streams: list = field(default_factory=list)
    perm_B_index: list = field(default_factory=list)

    def as_row(self) -> dict:
        return {
            "model": self.name,
            "e_value": self.e_value,
            "I_reason": self.I_reason,
            "I_reason_lo": self.I_reason_ci[0],
            "I_reason_hi": self.I_reason_ci[1],
            "I_prior": self.I_prior,
            "I_prior_lo": self.I_prior_ci[0],
            "I_prior_hi": self.I_prior_ci[1],
            "I_tot": self.I_tot,
            "growth": self.growth,
        }


def _blocked_permutation(group: np.ndarray, rng: np.random.Generator):
    """Return an instance ordering that keeps each group (image) contiguous.

    Groups are shuffled; instances within a group keep their relative order.
    This enforces image-level exchangeability (algorithm.md section 11).
    """
    uniq = np.unique(group)
    rng.shuffle(uniq)
    order = []
    # bucket instance indices per group
    buckets = {g: [] for g in uniq}
    for idx, g in enumerate(group):
        buckets[g].append(idx)
    for g in uniq:
        order.extend(buckets[g])
    return np.asarray(order, dtype=int)


def _split_AB(order: np.ndarray, group: np.ndarray, split_frac: float):
    """Split a blocked ordering into fold A (projection) and B (eval) by group.

    Splitting is done at the group boundary so an image is wholly in A or B.
    """
    uniq_in_order = []
    seen = set()
    for idx in order:
        g = group[idx]
        if g not in seen:
            seen.add(g)
            uniq_in_order.append(g)
    n_a_groups = max(1, int(round(split_frac * len(uniq_in_order))))
    a_groups = set(uniq_in_order[:n_a_groups])
    A_idx = np.array([i for i in order if group[i] in a_groups], dtype=int)
    B_idx = np.array([i for i in order if group[i] not in a_groups], dtype=int)
    return A_idx, B_idx


def run_wager_single(
    data: ModelData,
    rng: np.random.Generator,
    c: float | None = None,
    alpha: float = 0.05,
    split_frac: float = 0.4,
    ci_grid: int = 401,
):
    """One permutation pass for one model. Returns a dict of readouts + streams."""
    K = data.K
    c = float(np.log(K)) if c is None else c
    group = data.group if data.group is not None else np.arange(data.N)

    order = _blocked_permutation(group, rng)
    A_idx, B_idx = _split_AB(order, group, split_frac)

    qbar, logcorr, unif, glob = kt_projection(data.q[A_idx], data.phi[A_idx], K)

    qB = data.q[B_idx]
    yB = data.y[B_idx]
    phiB = data.phi[B_idx]
    d, e = prior_excess_logscore(qB, yB, phiB, qbar, logcorr, glob, unif, c)

    e_value, _, growth = wealth_process(d, c)
    return {
        "e_value": e_value,
        "growth": growth,
        "d": d,
        "e": e,
        "B_idx": B_idx,
        "c": c,
    }


def run_wager_permutations(
    data: ModelData,
    R: int = 100,
    c: float | None = None,
    alpha: float = 0.05,
    split_frac: float = 0.4,
    seed: int = 0,
    ci_grid: int = 401,
) -> WagerResult:
    """Run R image-blocked permutations and aggregate (algorithm.md lines 1-13).

    Aggregation:
      * e-value : mean over permutations (a mean of e-values is an e-value).
      * I_reason, I_prior point : mean over permutations.
      * CIs : anytime-valid betting CI on the concatenated B-streams, then
        widened to the mean per-permutation interval for honesty across orders.
    """
    K = data.K
    c = float(np.log(K)) if c is None else c
    rng = np.random.default_rng(seed)

    e_vals, growths = [], []
    d_streams, e_streams, B_indices = [], [], []
    I_reason_pts, I_prior_pts = [], []
    reason_cis, prior_cis = [], []

    for r in range(R):
        out = run_wager_single(data, rng, c=c, alpha=alpha, split_frac=split_frac)
        e_vals.append(out["e_value"])
        growths.append(out["growth"])
        d, e = out["d"], out["e"]
        d_streams.append(d)
        e_streams.append(e)
        B_indices.append(out["B_idx"])
        I_reason_pts.append(betting_mean_point(d))
        I_prior_pts.append(betting_mean_point(e))
        # per-permutation anytime-valid CIs (averaged below)
        reason_cis.append(betting_mean_ci(d, c, alpha=alpha, n_grid=ci_grid))
        prior_cis.append(betting_mean_ci(e, c, alpha=alpha, n_grid=ci_grid))

    e_vals = np.asarray(e_vals)
    reason_cis = np.asarray(reason_cis)
    prior_cis = np.asarray(prior_cis)

    I_reason = float(np.mean(I_reason_pts))
    I_prior = float(np.mean(I_prior_pts))
    reason_ci = (float(np.nanmean(reason_cis[:, 0])), float(np.nanmean(reason_cis[:, 1])))
    prior_ci = (float(np.nanmean(prior_cis[:, 0])), float(np.nanmean(prior_cis[:, 1])))

    return WagerResult(
        name=data.name,
        e_value=float(np.mean(e_vals)),
        e_values_per_perm=e_vals,
        I_reason=I_reason,
        I_reason_ci=reason_ci,
        I_prior=I_prior,
        I_prior_ci=prior_ci,
        I_tot=I_reason + I_prior,
        growth=float(np.mean(growths)),
        d_streams=d_streams,
        e_streams=e_streams,
        perm_B_index=B_indices,
    )
