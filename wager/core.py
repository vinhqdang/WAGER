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
def kt_projection(q_A: np.ndarray, phi_A: np.ndarray, K: int, m: float = 1.0):
    """Estimate the self-prior projection q_bar_f on fold A (Definition 1).

    The projection is the model's own predictions averaged within each prior
    cell.  Because long-tail cells are sparse, the cell mean is shrunk toward the
    model's *global* mean prediction (empirical-Bayes / hierarchical backoff)
    rather than toward uniform: this keeps the projection an honest estimate of
    E[q_f | phi] without the large upward reasoning bias that uniform-directed
    KT smoothing introduces for sharp frequency priors.

      q_bar(y|phi=c) = ( sum_{A,c} q_f(y|x) + m * g(y) ) / ( n_c + m )
      g(y) = global mean prediction = mean over all of fold A.

    Parameters
    ----------
    q_A : (Na, K) model predictive distributions on the projection-fit fold.
    phi_A : (Na,) prior-feature cell id for each instance in fold A.
    K : int   number of classes.
    m : float pseudo-count toward the global backoff (default 1; m=0 -> raw mean).

    Returns
    -------
    qbar : dict[int, np.ndarray]   cell-id -> shrunk averaged distribution.
    unif : (K,) uniform reference 1/K (the I_prior reference).
    glob : (K,) global mean prediction (backoff for unseen cells).
    """
    q_A = np.asarray(q_A, dtype=np.float64)
    phi_A = np.asarray(phi_A)
    if q_A.ndim != 2 or q_A.shape[1] != K:
        raise ValueError(f"q_A must be (Na,{K}); got {q_A.shape}")

    glob = q_A.mean(axis=0) if len(q_A) else np.full(K, 1.0 / K)

    uniq, inv = np.unique(phi_A, return_inverse=True)
    sums = np.zeros((len(uniq), K), dtype=np.float64)
    sumsq = np.zeros((len(uniq), K), dtype=np.float64)
    np.add.at(sums, inv, q_A)
    np.add.at(sumsq, inv, q_A * q_A)
    counts = np.bincount(inv, minlength=len(uniq)).astype(np.float64)
    nc = counts[:, None]

    smoothed = (sums + m * glob) / (nc + m)

    # Second-order (Jensen) bias correction for log of an estimated cell-mean:
    #   E[log mhat(y)] ~= log m(y) - Var(mhat(y)) / (2 m(y)^2),
    # with Var(mhat) = within-cell variance / n_c.  We add the correction back to
    # log-projection so reasoning is not inflated by projection-estimation noise.
    raw_mean = sums / np.maximum(nc, 1.0)
    within_var = np.maximum(sumsq / np.maximum(nc, 1.0) - raw_mean ** 2, 0.0)
    var_mean = within_var / np.maximum(nc, 1.0)
    logcorr_arr = var_mean / (2.0 * np.maximum(smoothed, _EPS) ** 2)
    # cap the correction so a near-zero projection cannot explode it
    logcorr_arr = np.minimum(logcorr_arr, np.log(K))

    qbar = {int(c): smoothed[i] for i, c in enumerate(uniq)}
    logcorr = {int(c): logcorr_arr[i] for i, c in enumerate(uniq)}
    unif = np.full(K, 1.0 / K, dtype=np.float64)
    return qbar, logcorr, unif, glob


def lookup_projection(qbar: dict, backoff: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """Materialize the projected distribution for every instance (backoff if unseen)."""
    K = backoff.shape[0]
    out = np.empty((len(phi), K), dtype=np.float64)
    for i, c in enumerate(phi):
        out[i] = qbar.get(int(c), backoff)
    return out


# --------------------------------------------------------------------------- #
# Definition 2 - prior-excess log score                                       #
# --------------------------------------------------------------------------- #
def prior_excess_logscore(q_f, y, phi, qbar, logcorr, backoff, unif, c):
    """Compute clipped per-instance reasoning score d~ and prior score e~.

    Parameters
    ----------
    qbar : dict cell -> shrunk projected distribution.
    logcorr : dict cell -> additive bias correction to the log-projection.
    backoff : (K,) distribution used for cells unseen on fold A (global mean).
    unif : (K,) uniform reference for the prior-information channel.

    Returns
    -------
    d_clip : (N,) reasoning score  log q_f(y|x) - log~q_bar(y|phi), clipped to [-c,c]
    e_clip : (N,) prior score      log~q_bar(y|phi) - log u(y),     clipped to [-c,c]

    Note the bias correction shifts log-projection up; it cancels in d+e (=I_tot)
    so it only reallocates mis-credited reasoning back into the prior channel.
    """
    q_f = np.asarray(q_f, dtype=np.float64)
    y = np.asarray(y).astype(int)
    phi = np.asarray(phi)
    N = len(y)
    K = unif.shape[0]
    zero_corr = np.zeros(K)
    idx = np.arange(N)

    qbar_mat = lookup_projection(qbar, backoff, phi)
    corr_mat = np.empty((N, K))
    for i, cc in enumerate(phi):
        corr_mat[i] = logcorr.get(int(cc), zero_corr)

    log_qf = np.log(q_f[idx, y] + _EPS)
    log_qb = np.log(qbar_mat[idx, y] + _EPS) + corr_mat[idx, y]
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
