"""WAGER core: self-prior projection, ONS betting, wealth process, anytime-valid CIs.

All routines are pure NumPy and operate on cached predictive distributions.
The math follows algorithm.md sections 3-4:

  * kt_projection            -> Definition 1 (self-prior projection q_bar_f)
  * prior_excess_logscore    -> Definition 2 (d_i, clipped)
  * wealth_process / OnsBettor -> Definition 3 + Theorem 1 (e-value)
  * betting_mean_ci          -> Theorem 4 (anytime-valid CI for a bounded mean)

The ONS / aGRAPA betting rule is the closed-form predictable update of
Waudby-Smith & Ramdas (2024, JRSS-B 86(1):1-27).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# ONS step constant: 2 / (2 - ln 3).  WSR (2024) Online-Newton-Step betting.
_ONS_C = 2.0 / (2.0 - np.log(3.0))
_EPS = 1e-12


# --------------------------------------------------------------------------- #
# Definition 1 - self-prior projection                                        #
# --------------------------------------------------------------------------- #
def kt_projection(q_A: np.ndarray, phi_A: np.ndarray, K: int):
    """Estimate the self-prior projection q_bar_f on fold A (Definition 1).

    Parameters
    ----------
    q_A : (Na, K) float array
        Model predictive distributions on the projection-fit fold.
    phi_A : (Na,) integer array
        Prior-feature cell id for each instance in fold A.
    K : int
        Number of label classes.

    Returns
    -------
    qbar : dict[int, np.ndarray]
        Cell-id -> KT-smoothed (add-1/2) averaged distribution.
    unif : (K,) float array
        Uniform reference 1/K (backoff for unseen cells).

    Notes
    -----
    KT smoothing:  q_bar(y|phi) = (1/2 + sum_A q_f(y|x)) / (K/2 + n_phi)
    """
    q_A = np.asarray(q_A, dtype=np.float64)
    phi_A = np.asarray(phi_A)
    if q_A.ndim != 2 or q_A.shape[1] != K:
        raise ValueError(f"q_A must be (Na,{K}); got {q_A.shape}")

    # Group-sum predictive vectors per cell, vectorized.
    uniq, inv = np.unique(phi_A, return_inverse=True)
    sums = np.zeros((len(uniq), K), dtype=np.float64)
    np.add.at(sums, inv, q_A)
    counts = np.bincount(inv, minlength=len(uniq)).astype(np.float64)

    smoothed = (0.5 + sums) / (0.5 * K + counts[:, None])
    qbar = {int(c): smoothed[i] for i, c in enumerate(uniq)}
    unif = np.full(K, 1.0 / K, dtype=np.float64)
    return qbar, unif


def lookup_projection(qbar: dict, unif: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """Materialize the projected distribution for every instance (backoff to unif)."""
    K = unif.shape[0]
    out = np.empty((len(phi), K), dtype=np.float64)
    for i, c in enumerate(phi):
        out[i] = qbar.get(int(c), unif)
    return out


# --------------------------------------------------------------------------- #
# Definition 2 - prior-excess log score                                       #
# --------------------------------------------------------------------------- #
def prior_excess_logscore(q_f, y, phi, qbar, unif, c):
    """Compute clipped per-instance reasoning score d~ and prior score e~.

    Returns
    -------
    d_clip : (N,) reasoning score  log q_f(y|x) - log q_bar(y|phi), clipped to [-c,c]
    e_clip : (N,) prior score      log q_bar(y|phi) - log u(y),     clipped to [-c,c]
    """
    q_f = np.asarray(q_f, dtype=np.float64)
    y = np.asarray(y).astype(int)
    phi = np.asarray(phi)
    N = len(y)
    qbar_mat = lookup_projection(qbar, unif, phi)
    idx = np.arange(N)

    log_qf = np.log(q_f[idx, y] + _EPS)
    log_qb = np.log(qbar_mat[idx, y] + _EPS)
    log_u = np.log(unif[y] + _EPS)

    d = np.clip(log_qf - log_qb, -c, c)
    e = np.clip(log_qb - log_u, -c, c)
    return d, e


# --------------------------------------------------------------------------- #
# Definition 3 + Theorem 1 - ONS betting + wealth process                     #
# --------------------------------------------------------------------------- #
@dataclass
class OnsBettor:
    """Stateful Online-Newton-Step predictable betting fraction (WSR 2024).

    Bets lambda_i in [0, lam_cap] on the value z_i.  The fraction is updated
    *after* observing z_i so that lambda_i is F_{i-1}-measurable (predictable).
    """

    lam_cap: float
    lam: float = 0.0
    A: float = 1.0  # sum of squared gradients (+1 init for stability)

    def step(self, z_prev: float) -> float:
        """Update lambda using the most recent observation, return new fraction."""
        grad = z_prev / (1.0 + self.lam * z_prev + _EPS)
        self.A += grad * grad
        self.lam = self.lam + _ONS_C * grad / (self.A + _EPS)
        self.lam = float(np.clip(self.lam, 0.0, self.lam_cap))
        return self.lam


def wealth_process(d_clip: np.ndarray, c: float):
    """Run the one-sided capital process for H0: mu<=0 (Definition 3, Theorem 1).

    Bets lambda_i in [0, 1/c) (capped at 0.5/c for numerical headroom) on d~_i.

    Returns
    -------
    e_value : float          terminal wealth W_n (an e-value for H0: mu<=0)
    wealth  : (N,) float      running wealth W_1..W_n
    growth  : float           (1/n) log W_n  (finite-sample growth rate, Thm 2)
    """
    d_clip = np.asarray(d_clip, dtype=np.float64)
    n = len(d_clip)
    lam_cap = 0.5 / c
    bettor = OnsBettor(lam_cap=lam_cap)
    W = 1.0
    wealth = np.empty(n, dtype=np.float64)
    for i in range(n):
        lam = bettor.step(d_clip[i - 1]) if i > 0 else 0.0
        W *= (1.0 + lam * d_clip[i])
        W = max(W, _EPS)  # guard against pathological underflow
        wealth[i] = W
    growth = np.log(W) / n if n > 0 else 0.0
    return W, wealth, growth


# --------------------------------------------------------------------------- #
# Theorem 4 - anytime-valid confidence interval for a bounded mean            #
# --------------------------------------------------------------------------- #
def _hedged_capital_grid(x: np.ndarray, grid: np.ndarray, c: float, alpha: float):
    """Vectorized hedged betting test of H0: mu = m for every m in grid.

    For each candidate mean m we run two predictable ONS capital processes on
    (x - m): W+ bets the centered residual is positive, W- bets it is negative.
    The *hedged* capital W = (W+ + W-)/2 is itself a non-negative martingale with
    E[W]<=1 under H0, so by Ville P(sup_n W >= 1/alpha) <= alpha.  Candidate m is
    kept iff the hedged capital never reaches 1/alpha -> coverage >= 1 - alpha.

    The betting variable (x - m) lies in [-2c, 2c]; the fraction is capped below
    1/(2c) to keep 1 + lam*(x-m) >= 0.  Vectorized across the grid (G x N work).
    """
    x = np.asarray(x, dtype=np.float64)
    G = len(grid)
    lam_cap = 0.5 / c  # = 1/(2c): keeps 1 + lam*z >= 0 for z in [-2c, 2c]
    log_thresh = np.log(1.0 / alpha)
    log2 = np.log(2.0)

    lam_p = np.zeros(G); A_p = np.ones(G); logW_p = np.zeros(G)
    lam_m = np.zeros(G); A_m = np.ones(G); logW_m = np.zeros(G)
    rejected = np.zeros(G, dtype=bool)
    z_prev = None

    for t in range(len(x)):
        z = x[t] - grid  # (G,) centered residual for each candidate mean
        if z_prev is not None:
            gp = z_prev / (1.0 + lam_p * z_prev + _EPS)
            A_p += gp * gp
            lam_p = np.clip(lam_p + _ONS_C * gp / (A_p + _EPS), 0.0, lam_cap)
            gm = (-z_prev) / (1.0 + lam_m * (-z_prev) + _EPS)
            A_m += gm * gm
            lam_m = np.clip(lam_m + _ONS_C * gm / (A_m + _EPS), 0.0, lam_cap)

        logW_p += np.log(np.maximum(1.0 + lam_p * z, _EPS))
        logW_m += np.log(np.maximum(1.0 + lam_m * (-z), _EPS))
        # hedged capital W = (W+ + W-)/2  ->  logW = logaddexp(logW_p, logW_m) - log 2
        logW = np.logaddexp(logW_p, logW_m) - log2
        rejected |= logW >= log_thresh
        z_prev = z

    return ~rejected  # boolean keep-mask over grid


def betting_mean_ci(x, c, alpha=0.05, n_grid=801, lo=None, hi=None):
    """Anytime-valid (1-alpha) CI for E[x] of a bounded variable (WSR 2024 / Thm 4).

    Returns (lower, upper).  The grid spans [-c, c] by default (the support of a
    clipped score) but can be narrowed with lo/hi for resolution.
    """
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0:
        return (np.nan, np.nan)
    lo = -c if lo is None else lo
    hi = c if hi is None else hi
    grid = np.linspace(lo, hi, n_grid)
    keep = _hedged_capital_grid(x, grid, c, alpha)
    if not keep.any():
        return (np.nan, np.nan)
    kept = grid[keep]
    return (float(kept.min()), float(kept.max()))


def betting_mean_point(x) -> float:
    """Consistent point estimate of E[x]: the empirical mean (=growth-rate limit)."""
    x = np.asarray(x, dtype=np.float64)
    return float(np.mean(x)) if len(x) else float("nan")
