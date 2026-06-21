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
def _shrunk_means(q_A, key_A, K, parent_lookup, m):
    """Per-key shrunk mean of q_A toward a per-key parent distribution.

    Returns (means dict, logcorr dict).  Shrinkage:
        mean(k) = (sum_{A,k} q + m * parent(k)) / (n_k + m).
    The Jensen bias correction is computed from within-key variance.
    """
    uniq, inv = np.unique(key_A, return_inverse=True)
    sums = np.zeros((len(uniq), K))
    sumsq = np.zeros((len(uniq), K))
    np.add.at(sums, inv, q_A)
    np.add.at(sumsq, inv, q_A * q_A)
    counts = np.bincount(inv, minlength=len(uniq)).astype(np.float64)
    nc = counts[:, None]
    parents = np.stack([parent_lookup(int(k)) for k in uniq])
    smoothed = (sums + m * parents) / (nc + m)

    raw_mean = sums / np.maximum(nc, 1.0)
    within_var = np.maximum(sumsq / np.maximum(nc, 1.0) - raw_mean ** 2, 0.0)
    var_mean = within_var / np.maximum(nc, 1.0)
    logcorr_arr = np.minimum(var_mean / (2.0 * np.maximum(smoothed, _EPS) ** 2), np.log(K))

    means = {int(k): smoothed[i] for i, k in enumerate(uniq)}
    corr = {int(k): logcorr_arr[i] for i, k in enumerate(uniq)}
    return means, corr


def kt_projection(q_A, phi_A, K, m=1.0, coarse_A=None):
    """Estimate the self-prior projection q_bar_f on fold A (Definition 1).

    The projection is the model's own predictions averaged within each prior
    cell.  On heavy-tailed benchmarks most cells are sparse, so the cell mean is
    shrunk through an empirical-Bayes *hierarchical backoff* rather than toward
    uniform.  With a coarse key (e.g. subject class) the hierarchy is

        cell (subj,obj)  ->  coarse (subj)  ->  global mean.

    A model whose prediction is a function of phi only (FREQ, a class-only MLP)
    uses the same backoff, so its out-of-fold reasoning score collapses to ~0 --
    this is what makes the FREQ anchor (I_reason ~ 0) hold on real data.

    Parameters
    ----------
    q_A : (Na, K) model predictive distributions on the projection-fit fold.
    phi_A : (Na,) fine prior-feature cell id.
    coarse_A : (Na,) optional coarser backoff key (e.g. subject class id).
    m : float pseudo-count toward the parent in each shrinkage level.

    Returns
    -------
    cell_proj, cell_corr : dict cell -> shrunk distribution / log-bias-correction.
    coarse_proj : dict coarse-key -> shrunk distribution (or {} if no coarse key).
    glob : (K,) global mean prediction (final backoff).
    unif : (K,) uniform reference 1/K (the I_prior reference).
    """
    q_A = np.asarray(q_A, dtype=np.float64)
    phi_A = np.asarray(phi_A)
    if q_A.ndim != 2 or q_A.shape[1] != K:
        raise ValueError(f"q_A must be (Na,{K}); got {q_A.shape}")

    glob = q_A.mean(axis=0) if len(q_A) else np.full(K, 1.0 / K)

    if coarse_A is None:
        cell_proj, cell_corr = _shrunk_means(q_A, phi_A, K, lambda k: glob, m)
        coarse_proj = {}
    else:
        coarse_A = np.asarray(coarse_A)
        # level 1: coarse keys shrink toward global
        coarse_proj, _ = _shrunk_means(q_A, coarse_A, K, lambda k: glob, m)
        # map each fine cell to its (unique) coarse parent
        cell_to_coarse = {}
        for cphi, ccoarse in zip(phi_A, coarse_A):
            cell_to_coarse.setdefault(int(cphi), int(ccoarse))

        def parent(cell):
            return coarse_proj.get(cell_to_coarse.get(cell, -1), glob)

        # level 2: cells shrink toward their coarse parent
        cell_proj, cell_corr = _shrunk_means(q_A, phi_A, K, parent, m)

    unif = np.full(K, 1.0 / K, dtype=np.float64)
    return cell_proj, cell_corr, coarse_proj, glob, unif


def lookup_projection(cell_proj, coarse_proj, glob, phi, coarse=None):
    """Materialize the projection per instance: cell -> coarse -> global backoff."""
    K = glob.shape[0]
    N = len(phi)
    out = np.empty((N, K), dtype=np.float64)
    for i in range(N):
        c = int(phi[i])
        if c in cell_proj:
            out[i] = cell_proj[c]
        elif coarse is not None and int(coarse[i]) in coarse_proj:
            out[i] = coarse_proj[int(coarse[i])]
        else:
            out[i] = glob
    return out


# --------------------------------------------------------------------------- #
# Definition 2 - prior-excess log score                                       #
# --------------------------------------------------------------------------- #
def prior_excess_logscore(q_f, y, phi, cell_proj, cell_corr, coarse_proj, glob, unif,
                          c, coarse=None):
    """Compute clipped per-instance reasoning score d~ and prior score e~.

    Projection lookup is hierarchical: cell -> coarse -> global backoff.  The
    Jensen log-bias correction is applied for cells estimated on fold A; it shifts
    the log-projection up and cancels in d+e (=I_tot), so it only reallocates
    mis-credited reasoning back into the prior channel.

    Returns
    -------
    d_clip : (N,) reasoning score  log q_f(y|x) - log~q_bar(y|phi), clipped to [-c,c]
    e_clip : (N,) prior score      log~q_bar(y|phi) - log u(y),     clipped to [-c,c]
    """
    q_f = np.asarray(q_f, dtype=np.float64)
    y = np.asarray(y).astype(int)
    phi = np.asarray(phi)
    N = len(y)
    K = unif.shape[0]
    zero_corr = np.zeros(K)
    idx = np.arange(N)

    qbar_mat = lookup_projection(cell_proj, coarse_proj, glob, phi, coarse)
    corr_mat = np.empty((N, K))
    for i in range(N):
        corr_mat[i] = cell_corr.get(int(phi[i]), zero_corr)

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
