"""Reasoning Gain Ratio (RGR) with anytime-valid and Fieller confidence intervals.

algorithm.md section 3.6:

    RGR(f', f) = (I_reason_f' - I_reason_f) / (I_tot_f' - I_tot_f)

the fraction of an information gain attributable to better *reasoning* rather
than better *prior-fitting*.  Verdict: upper-CI(RGR) < 0.5  =>  "non-substantive".

Two CI routines are provided:
  * fieller_ratio_ci  -- classical Fieller (1954) on paired per-instance scores,
    tight, fixed-n normal approximation; computed per permutation and averaged.
  * anytime_ratio_ci  -- combines the anytime-valid betting CIs of numerator and
    denominator under a Bonferroni split (level 2*alpha); conservative but
    distribution-free and anytime-valid (the property the paper claims).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats

from .core import betting_mean_ci


@dataclass
class RgrResult:
    f_prime: str
    f: str
    rgr: float
    fieller_ci: tuple
    anytime_ci: tuple
    d_reason: float       # Delta I_reason (numerator)
    d_tot: float          # Delta I_tot (denominator)
    verdict: str

    def as_row(self) -> dict:
        return {
            "f_prime": self.f_prime,
            "f": self.f,
            "RGR": self.rgr,
            "fieller_lo": self.fieller_ci[0],
            "fieller_hi": self.fieller_ci[1],
            "anytime_lo": self.anytime_ci[0],
            "anytime_hi": self.anytime_ci[1],
            "dI_reason": self.d_reason,
            "dI_tot": self.d_tot,
            "verdict": self.verdict,
        }


def fieller_ratio_ci(num: np.ndarray, den: np.ndarray, alpha: float = 0.05):
    """Classical Fieller (1954) CI for E[num]/E[den] from paired samples.

    Returns (lo, hi).  If the denominator is not significantly different from
    zero the interval is unbounded -> (-inf, inf).
    """
    num = np.asarray(num, dtype=np.float64)
    den = np.asarray(den, dtype=np.float64)
    n = len(num)
    if n < 3:
        return (-np.inf, np.inf)

    nbar = num.mean()
    dbar = den.mean()
    s_nn = num.var(ddof=1) / n
    s_dd = den.var(ddof=1) / n
    s_nd = np.cov(num, den, ddof=1)[0, 1] / n

    t = stats.t.ppf(1.0 - alpha / 2.0, df=n - 1)
    t2 = t * t

    a = dbar * dbar - t2 * s_dd
    b = nbar * dbar - t2 * s_nd
    cc = nbar * nbar - t2 * s_nn

    if a <= 0:  # denominator indistinguishable from 0 -> unbounded ratio CI
        return (-np.inf, np.inf)

    disc = b * b - a * cc
    if disc < 0:
        return (np.nan, np.nan)
    root = np.sqrt(disc)
    lo = (b - root) / a
    hi = (b + root) / a
    return (float(min(lo, hi)), float(max(lo, hi)))


def anytime_ratio_ci(num: np.ndarray, den: np.ndarray, c: float, alpha: float = 0.05,
                     n_grid: int = 401):
    """Anytime-valid CI for E[num]/E[den] via Bonferroni combination (level 2*alpha).

    Build anytime-valid betting CIs for the numerator and denominator means each
    at level alpha; the joint event holds w.p. >= 1 - 2*alpha.  If the
    denominator interval is strictly positive (or strictly negative), the ratio
    range over the rectangle is finite and is returned; otherwise unbounded.
    """
    num = np.asarray(num, dtype=np.float64)
    den = np.asarray(den, dtype=np.float64)
    # numerator/denominator are differences of clipped scores in [-2c, 2c]
    n_lo, n_hi = betting_mean_ci(num, 2 * c, alpha=alpha, n_grid=n_grid)
    d_lo, d_hi = betting_mean_ci(den, 2 * c, alpha=alpha, n_grid=n_grid)
    if np.isnan(n_lo) or np.isnan(d_lo):
        return (-np.inf, np.inf)
    if d_lo <= 0 <= d_hi:  # denominator straddles zero -> ratio unbounded
        return (-np.inf, np.inf)
    candidates = [n_lo / d_lo, n_lo / d_hi, n_hi / d_lo, n_hi / d_hi]
    return (float(min(candidates)), float(max(candidates)))


def _paired_streams(res_fprime, res_f):
    """Concatenate paired (num, den) per-instance scores across shared permutations.

    Requires both results were produced with the *same* seed/data so each
    permutation's evaluation fold B is identical across the two models.
    """
    nums, dens = [], []
    R = min(len(res_fprime.d_streams), len(res_f.d_streams))
    for r in range(R):
        bp = res_fprime.perm_B_index[r]
        bf = res_f.perm_B_index[r]
        if len(bp) != len(bf) or not np.array_equal(bp, bf):
            # permutations not aligned; skip (caller should use identical seed)
            continue
        dprime, eprime = res_fprime.d_streams[r], res_fprime.e_streams[r]
        d, e = res_f.d_streams[r], res_f.e_streams[r]
        nums.append(dprime - d)                       # Delta I_reason contribution
        dens.append((dprime + eprime) - (d + e))      # Delta I_tot contribution
    if not nums:
        return np.array([]), np.array([])
    return np.concatenate(nums), np.concatenate(dens)


def reasoning_gain_ratio(res_fprime, res_f, c: float, alpha: float = 0.05,
                         decision_threshold: float = 0.5):
    """Compute RGR(f', f) with Fieller and anytime-valid CIs and a verdict.

    Parameters use the WagerResult objects of two models (f' the claimed
    improvement over f).  Both must have been run with the same seed so the
    evaluation streams pair up instance-by-instance.
    """
    d_reason = res_fprime.I_reason - res_f.I_reason
    d_tot = res_fprime.I_tot - res_f.I_tot
    rgr = d_reason / d_tot if abs(d_tot) > 1e-12 else float("nan")

    num, den = _paired_streams(res_fprime, res_f)
    if len(num):
        # average Fieller across the pooled paired stream
        fieller = fieller_ratio_ci(num, den, alpha=alpha)
        anytime = anytime_ratio_ci(num, den, c, alpha=alpha)
    else:
        fieller = (np.nan, np.nan)
        anytime = (-np.inf, np.inf)

    upper = anytime[1] if np.isfinite(anytime[1]) else fieller[1]
    if np.isfinite(upper) and upper < decision_threshold:
        verdict = "non-substantive"
    elif d_tot <= 0:
        verdict = "no-gain"
    else:
        verdict = "reasoning-supported"

    return RgrResult(
        f_prime=res_fprime.name,
        f=res_f.name,
        rgr=rgr,
        fieller_ci=fieller,
        anytime_ci=anytime,
        d_reason=d_reason,
        d_tot=d_tot,
        verdict=verdict,
    )
