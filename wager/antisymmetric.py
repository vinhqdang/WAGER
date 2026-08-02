"""Within-cell Antisymmetric Gain Evaluation of Reasoning (WAGER).

This module implements the redesigned WAGER estimator.  Given two frozen
probabilistic classifiers, it decomposes their observed proper-score gain as

    total gain = prior-transported gain + instance-alignment gain.

The prior term evaluates every prediction contrast against labels transported
from *other* examples in the same prior-feature cell.  The alignment term is
the corresponding within-cell order-two U-statistic.  No prior model,
projection fold, smoothing rule, or learned nuisance distribution is needed.

The default score is the (higher-is-better) quadratic/Brier score

    S(q, y) = 2 q_y - ||q||_2^2,

which is strictly proper and bounded.  Log score is also supported when an
explicit probability floor is desired.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

_EPS = 1e-12


@dataclass(frozen=True)
class GainDecomposition:
    """Result of the WAGER gain decomposition for one model comparison."""

    total_gain: float
    prior_gain: float
    reasoning_gain: float
    reasoning_share: float
    reasoning_ci: tuple[float, float]
    prior_ci: tuple[float, float]
    total_ci: tuple[float, float]
    share_ci: tuple[float, float]
    standard_error: float
    n_total: int
    n_identified: int
    n_cells: int
    n_singletons: int
    score: str
    observed: np.ndarray
    transported: np.ndarray
    alignment: np.ndarray
    influence_reasoning: np.ndarray
    eligible: np.ndarray

    @property
    def coverage(self) -> float:
        return self.n_identified / self.n_total if self.n_total else float("nan")

    def as_row(self) -> dict:
        return {
            "total_gain": self.total_gain,
            "prior_gain": self.prior_gain,
            "reasoning_gain": self.reasoning_gain,
            "reasoning_share": self.reasoning_share,
            "reasoning_ci": list(self.reasoning_ci),
            "prior_ci": list(self.prior_ci),
            "total_ci": list(self.total_ci),
            "share_ci": list(self.share_ci),
            "standard_error": self.standard_error,
            "n_total": self.n_total,
            "n_identified": self.n_identified,
            "coverage": self.coverage,
            "n_cells": self.n_cells,
            "n_singletons": self.n_singletons,
            "score": self.score,
        }


def score_matrix(q: np.ndarray, score: str = "brier", eps: float = 1e-6) -> np.ndarray:
    """Return S(q_i, y) for every example ``i`` and possible label ``y``.

    Scores are oriented so larger is better.  The Brier form omits the
    label-only constant, which cancels from all model comparisons.
    """
    q = np.asarray(q, dtype=np.float64)
    if q.ndim != 2:
        raise ValueError(f"q must be a 2-D probability matrix; got {q.shape}")
    if not np.all(np.isfinite(q)) or np.any(q < 0):
        raise ValueError("q must contain finite, non-negative probabilities")
    rowsum = q.sum(axis=1)
    if not np.allclose(rowsum, 1.0, atol=1e-6):
        raise ValueError("rows of q must sum to one")
    if score == "brier":
        return 2.0 * q - np.sum(q * q, axis=1, keepdims=True)
    if score == "log":
        if not 0 < eps < 1:
            raise ValueError("eps must be in (0,1)")
        return np.log(np.maximum(q, eps))
    raise ValueError("score must be 'brier' or 'log'")


def gain_matrix(
    q_new: np.ndarray,
    q_old: np.ndarray,
    score: str = "brier",
    eps: float = 1e-6,
) -> np.ndarray:
    """Per-example, per-label proper-score contrast new minus old."""
    q_new = np.asarray(q_new)
    q_old = np.asarray(q_old)
    if q_new.shape != q_old.shape:
        raise ValueError(f"model matrices must have equal shape; got {q_new.shape} and {q_old.shape}")
    return score_matrix(q_new, score=score, eps=eps) - score_matrix(q_old, score=score, eps=eps)


def _normal_interval(estimate: float, influence: np.ndarray, alpha: float) -> tuple[float, float, float]:
    """Asymptotic interval from a mean-zero influence vector."""
    n = len(influence)
    if n < 2:
        return float("nan"), float("nan"), float("nan")
    z = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    se = float(np.sqrt(np.sum(influence * influence)) / n)
    return estimate - z * se, estimate + z * se, se


def _cluster_interval(
    estimate: float,
    influence: np.ndarray,
    groups: np.ndarray,
    alpha: float,
) -> tuple[float, float, float]:
    """One-way cluster-robust interval for an asymptotically linear estimator."""
    groups = np.asarray(groups)
    if len(groups) != len(influence):
        raise ValueError("groups and influence must have the same length")
    _, inv = np.unique(groups, return_inverse=True)
    g = int(inv.max()) + 1 if len(inv) else 0
    if g < 2:
        return float("nan"), float("nan"), float("nan")
    sums = np.bincount(inv, weights=influence, minlength=g)
    n = len(influence)
    se = float(np.sqrt((g / (g - 1.0)) * np.sum(sums * sums)) / n)
    z = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    return estimate - z * se, estimate + z * se, se


def decompose_gain(
    q_new: np.ndarray,
    q_old: np.ndarray,
    y: np.ndarray,
    phi: np.ndarray,
    *,
    groups: np.ndarray | None = None,
    score: str = "brier",
    eps: float = 1e-6,
    alpha: float = 0.05,
) -> GainDecomposition:
    """Decompose a model improvement using within-cell counterfactual transport.

    For example ``i`` in a cell containing ``n`` observations, let

        h_i(y) = S(q_new_i, y) - S(q_old_i, y).

    Its transported score is the mean of ``h_i(y_j)`` over every other label
    ``j`` in the same cell.  Averaging gives the prior-recoverable gain.  The
    difference from the observed score is exactly the antisymmetric U-statistic

        1/2 [h_i(y_i)+h_j(y_j)-h_i(y_j)-h_j(y_i)].

    Cells with one observation cannot identify a within-cell counterfactual and
    are excluded transparently.  Confidence intervals use the Hájek influence
    function of the U-statistic; when ``groups`` is supplied (e.g. image ids),
    influence contributions are aggregated for cluster-robust inference.
    """
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0,1)")
    h = gain_matrix(q_new, q_old, score=score, eps=eps)
    n, k = h.shape
    y = np.asarray(y, dtype=np.int64)
    phi = np.asarray(phi)
    if y.shape != (n,) or phi.shape != (n,):
        raise ValueError("y and phi must be length-N vectors")
    if np.any((y < 0) | (y >= k)):
        raise ValueError("y contains a label outside the prediction vocabulary")
    if groups is not None and np.asarray(groups).shape != (n,):
        raise ValueError("groups must be a length-N vector")

    observed = h[np.arange(n), y]
    transported = np.full(n, np.nan, dtype=np.float64)
    alignment = np.full(n, np.nan, dtype=np.float64)
    pair_mean = np.full(n, np.nan, dtype=np.float64)
    cell_theta = np.full(n, np.nan, dtype=np.float64)

    _, inv, counts_all = np.unique(phi, return_inverse=True, return_counts=True)
    eligible = counts_all[inv] >= 2
    n_singletons = int(np.sum(counts_all == 1))

    # Work cell by cell.  The expensive operation is one (n_cell,K) matrix by
    # a K-vector, so total complexity is O(NK), not O(sum n_cell^2).
    for c in np.flatnonzero(counts_all >= 2):
        idx = np.flatnonzero(inv == c)
        hc = h[idx]
        yc = y[idx]
        nc = len(idx)
        label_counts = np.bincount(yc, minlength=k).astype(np.float64)
        obs = observed[idx]
        score_sum_by_label = hc.sum(axis=0)

        trans = (hc @ label_counts - obs) / (nc - 1.0)
        align = obs - trans
        transported[idx] = trans
        alignment[idx] = align

        # Per-observation average of the antisymmetric pair kernel.  This is
        # needed for the order-two U-statistic's Hájek projection.
        other_obs = (obs.sum() - obs) / (nc - 1.0)
        other_predictors_on_yi = (score_sum_by_label[yc] - obs) / (nc - 1.0)
        pm = 0.5 * (obs + other_obs - trans - other_predictors_on_yi)
        theta = float(pm.mean())
        pair_mean[idx] = pm
        cell_theta[idx] = theta

    idx = np.flatnonzero(eligible)
    if len(idx) == 0:
        raise ValueError("no prior-feature cell contains at least two observations")
    obs_e = observed[idx]
    trans_e = transported[idx]
    total = float(obs_e.mean())
    prior = float(trans_e.mean())
    reasoning = float(alignment[idx].mean())
    if not np.isclose(total, prior + reasoning, atol=1e-12):
        raise RuntimeError("internal decomposition identity failed")

    # Influence functions.  The U-statistic term includes variation in the
    # empirical distribution of phi; prior follows from the exact identity.
    psi_total = obs_e - total
    psi_reason = 2.0 * pair_mean[idx] - cell_theta[idx] - reasoning
    psi_prior = psi_total - psi_reason

    if groups is None:
        ci_fun = lambda est, psi: _normal_interval(est, psi, alpha)
    else:
        groups_e = np.asarray(groups)[idx]
        ci_fun = lambda est, psi: _cluster_interval(est, psi, groups_e, alpha)
    rlo, rhi, rse = ci_fun(reasoning, psi_reason)
    plo, phi_hi, _ = ci_fun(prior, psi_prior)
    tlo, thi, _ = ci_fun(total, psi_total)

    share = reasoning / total if total > 0 else float("nan")
    if total > 0:
        psi_share = (psi_reason - share * psi_total) / total
        slo, shi, _ = ci_fun(share, psi_share)
    else:
        slo, shi = float("nan"), float("nan")

    full_psi = np.full(n, np.nan, dtype=np.float64)
    full_psi[idx] = psi_reason
    return GainDecomposition(
        total_gain=total,
        prior_gain=prior,
        reasoning_gain=reasoning,
        reasoning_share=share,
        reasoning_ci=(rlo, rhi),
        prior_ci=(plo, phi_hi),
        total_ci=(tlo, thi),
        share_ci=(slo, shi),
        standard_error=rse,
        n_total=n,
        n_identified=len(idx),
        n_cells=int(np.sum(counts_all >= 2)),
        n_singletons=n_singletons,
        score=score,
        observed=observed,
        transported=transported,
        alignment=alignment,
        influence_reasoning=full_psi,
        eligible=eligible,
    )


def cyclic_randomization_test(
    q_new: np.ndarray,
    q_old: np.ndarray,
    y: np.ndarray,
    phi: np.ndarray,
    *,
    score: str = "brier",
    eps: float = 1e-6,
    n_randomizations: int = 999,
    seed: int = 0,
) -> tuple[float, np.ndarray]:
    """Cell-stratified randomization test of zero instance alignment.

    Each randomization independently applies a uniformly random cyclic shift to
    the labels inside every prior cell.  This is an exact finite-group test under
    the sharp null that labels are exchangeable relative to model outputs within
    each cell.  Cyclic shifts form a computationally cheap subgroup of the full
    within-cell permutation group and preserve every cell's label histogram.

    Returns the one-sided p-value for positive reasoning gain and the randomized
    statistics.  The observed statistic is not included in the returned array.
    """
    if n_randomizations < 1:
        raise ValueError("n_randomizations must be positive")
    h = gain_matrix(q_new, q_old, score=score, eps=eps)
    n, k = h.shape
    y = np.asarray(y, dtype=np.int64)
    phi = np.asarray(phi)
    if y.shape != (n,) or phi.shape != (n,):
        raise ValueError("y and phi must be length-N vectors")

    order = np.argsort(phi, kind="stable")
    hs = h[order]
    ys = y[order]
    phis = phi[order]
    _, starts, counts = np.unique(phis, return_index=True, return_counts=True)
    eligible_cells = counts >= 2
    cell_id = np.repeat(np.arange(len(counts)), counts)
    eligible = eligible_cells[cell_id]
    rank = np.arange(n) - starts[cell_id]

    label_counts = np.zeros((len(counts), k), dtype=np.float64)
    np.add.at(label_counts, (cell_id, ys), 1.0)
    mass = np.einsum("nk,nk->n", hs, label_counts[cell_id])
    nc = counts[cell_id].astype(np.float64)

    obs_score = hs[np.arange(n), ys]
    obs_alignment = (nc * obs_score - mass) / np.maximum(nc - 1.0, 1.0)
    observed_stat = float(obs_alignment[eligible].mean())

    rng = np.random.default_rng(seed)
    stats = np.empty(n_randomizations, dtype=np.float64)
    for b in range(n_randomizations):
        offsets = np.array([rng.integers(int(c)) if c >= 2 else 0 for c in counts])
        source = starts[cell_id] + (rank + offsets[cell_id]) % counts[cell_id]
        yp = ys[source]
        perm_score = hs[np.arange(n), yp]
        perm_alignment = (nc * perm_score - mass) / np.maximum(nc - 1.0, 1.0)
        stats[b] = perm_alignment[eligible].mean()
    p = (1.0 + float(np.sum(stats >= observed_stat))) / (n_randomizations + 1.0)
    return p, stats

