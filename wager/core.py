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
from math import log as _LOG

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


def _gather(proj: dict, keys: np.ndarray, fallback: np.ndarray):
    """Vectorized per-instance gather from a {key: vector} dict with a fallback.

    fallback is either a (K,) vector (broadcast) or an (N,K) array.
    Returns (out (N,K), hit mask (N,)).
    """
    K = fallback.shape[-1]
    N = len(keys)
    if not proj:
        out = np.broadcast_to(fallback, (N, K)).copy() if fallback.ndim == 1 else fallback.copy()
        return out, np.zeros(N, dtype=bool)
    ids = np.fromiter(proj.keys(), dtype=np.int64, count=len(proj))
    order = np.argsort(ids)
    ids = ids[order]
    mat = np.stack([proj[int(k)] for k in ids])  # (Ncell, K)
    pos = np.searchsorted(ids, keys)
    pos_clip = np.clip(pos, 0, len(ids) - 1)
    hit = ids[pos_clip] == keys
    base = np.broadcast_to(fallback, (N, K)) if fallback.ndim == 1 else fallback
    out = np.where(hit[:, None], mat[pos_clip], base)
    return out, hit


def lookup_projection(cell_proj, coarse_proj, glob, phi, coarse=None):
    """Materialize the projection per instance: cell -> coarse -> global backoff."""
    K = glob.shape[0]
    phi = np.asarray(phi, dtype=np.int64)
    # start from coarse-or-global backoff, then overlay cell hits
    if coarse is not None and coarse_proj:
        coarse = np.asarray(coarse, dtype=np.int64)
        backoff, _ = _gather(coarse_proj, coarse, glob)
    else:
        backoff = np.broadcast_to(glob, (len(phi), K)).copy()
    out, _ = _gather(cell_proj, phi, backoff)
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
    corr_mat, _ = _gather(cell_corr, np.asarray(phi, dtype=np.int64), zero_corr)

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


def wealth_process(d_clip: np.ndarray, c: float, track: bool = True):
    """Run the one-sided capital process for H0: mu<=0 (Definition 3, Theorem 1).

    Bets lambda_i in [0, 1/c) (capped at 0.5/c for numerical headroom) on d~_i,
    accumulating log-wealth for numerical stability.  The ONS/aGRAPA update is
    inlined with plain-Python scalar math (no per-step numpy calls) for speed.

    Returns
    -------
    e_value : float          terminal wealth W_n (an e-value for H0: mu<=0)
    wealth  : (N,) or None    running wealth (None if track=False)
    growth  : float           (1/n) log W_n  (finite-sample growth rate, Thm 2)
    """
    d = np.asarray(d_clip, dtype=np.float64)
    n = d.size
    if n == 0:
        return 1.0, (np.empty(0) if track else None), 0.0
    lam_cap = 0.5 / c
    lam = 0.0
    A = 1.0
    logW = 0.0
    wealth = np.empty(n, dtype=np.float64) if track else None
    dlist = d.tolist()  # python floats: faster scalar loop
    z_prev = None
    for i in range(n):
        if z_prev is not None:
            denom = 1.0 + lam * z_prev + _EPS
            grad = z_prev / denom
            A += grad * grad
            lam += _ONS_C * grad / (A + _EPS)
            if lam < 0.0:
                lam = 0.0
            elif lam > lam_cap:
                lam = lam_cap
        zi = dlist[i]
        factor = 1.0 + lam * zi
        if factor < _EPS:
            factor = _EPS
        logW += _LOG(factor)
        if track:
            wealth[i] = np.exp(min(logW, 700.0))
        z_prev = zi
    # cap terminal wealth to keep it finite/serializable (logW>700 -> overflow);
    # growth rate uses the uncapped log-wealth and stays exact.
    W = float(np.exp(min(logW, 700.0)))
    growth = logW / n
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


def _fixed_lambda_keep(x, grid, c, alpha, lam):
    """Vectorized hedged confidence test of H0: mu=m over a grid, with a *fixed*
    (predictable) betting fraction lam.

    With a constant lam the wealth path is a pure cumulative sum, so the whole
    "does the hedged capital ever reach 1/alpha" check vectorizes over both data
    and grid (chunked to bound memory).  lam must be F_0-measurable -- it is
    estimated from a held-out prefix by the caller -- and < 1/(2c) for validity.
    """
    log_thresh = np.log(1.0 / alpha)
    log2 = np.log(2.0)
    G = len(grid)
    keep = np.ones(G, dtype=bool)
    step = max(1, 4_000_000 // max(len(x), 1))  # grid columns per chunk
    for j0 in range(0, G, step):
        gj = grid[j0:j0 + step]
        Z = x[:, None] - gj[None, :]            # (N, g)
        tp = np.log(np.maximum(1.0 + lam * Z, _EPS))
        tm = np.log(np.maximum(1.0 - lam * Z, _EPS))
        Sp = np.cumsum(tp, axis=0)
        Sm = np.cumsum(tm, axis=0)
        h = np.logaddexp(Sp, Sm) - log2          # hedged log-wealth path
        maxh = h.max(axis=0)
        keep[j0:j0 + step] = maxh < log_thresh
    return keep


def betting_mean_ci(x, c, alpha=0.05, n_grid=801, lo=None, hi=None, max_n=40000):
    """Anytime-valid (1-alpha) CI for E[x] of a bounded variable (WSR 2024 / Thm 4).

    Uses a hedged capital process with a predictable fixed betting fraction lam
    estimated from a held-out prefix (so lam is F_0-measurable and the sequence is
    anytime-valid).  The grid is adaptively centered on the empirical mean and
    expanded if the surviving set touches a non-clipped boundary.  Fully
    vectorized.  For very long streams the betting prefix is capped at max_n
    observations (the CI stays valid, only slightly wider) to bound cost.
    """
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    if n == 0:
        return (np.nan, np.nan)
    if max_n is not None and n > max_n:
        x = x[:max_n]
        n = max_n

    # predictable fixed bet from a held-out prefix; bet on the remainder
    n0 = min(max(200, n // 10), 5000)
    prefix, rest = x[:n0], x[n0:]
    if len(rest) < 10:
        prefix, rest = x, x
    sd0 = float(np.std(prefix)) + 1e-6
    lam = np.sqrt(2.0 * np.log(2.0 / alpha) / (max(len(rest), 1) * sd0 * sd0))
    lam = float(np.clip(lam, 1e-6, 0.49 / c))

    if lo is not None and hi is not None:
        grid = np.linspace(lo, hi, n_grid)
        keep = _fixed_lambda_keep(rest, grid, c, alpha, lam)
        return (float(grid[keep].min()), float(grid[keep].max())) if keep.any() else (np.nan, np.nan)

    mean = float(np.mean(x))
    sd = float(np.std(x)) + 1e-9
    half = max(0.02, 12.0 * sd / np.sqrt(n))
    ci_lo = ci_hi = np.nan
    keep = np.zeros(1, dtype=bool)
    for _ in range(7):
        g_lo = max(-c, mean - half)
        g_hi = min(c, mean + half)
        grid = np.linspace(g_lo, g_hi, n_grid)
        keep = _fixed_lambda_keep(rest, grid, c, alpha, lam)
        if not keep.any():
            half *= 2.0
            continue
        kept = grid[keep]
        ci_lo, ci_hi = float(kept.min()), float(kept.max())
        if (keep[0] and g_lo > -c) or (keep[-1] and g_hi < c):
            half *= 2.0
            continue
        return (ci_lo, ci_hi)
    return (ci_lo, ci_hi) if keep.any() else (np.nan, np.nan)


def betting_mean_point(x) -> float:
    """Consistent point estimate of E[x]: the empirical mean (=growth-rate limit)."""
    x = np.asarray(x, dtype=np.float64)
    return float(np.mean(x)) if len(x) else float("nan")
