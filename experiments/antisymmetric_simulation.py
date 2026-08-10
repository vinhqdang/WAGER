"""Controlled validation for within-cell antisymmetric WAGER."""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wager.antisymmetric import cyclic_randomization_test, decompose_gain

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "antisymmetric_simulation.json")


def generate(seed: int, beta: float, ncell: int = 24, per: int = 50, k: int = 5):
    """Generate a prior-only baseline and an oracle-mixture upgraded model."""
    rng = np.random.default_rng(seed)
    phi = np.repeat(np.arange(ncell), per)
    priors = rng.dirichlet(np.full(k, 0.8), size=ncell)
    y = np.array([rng.choice(k, p=priors[c]) for c in phi], dtype=np.int64)
    q_old = priors[phi]
    oracle = np.full((len(y), k), 0.02 / (k - 1))
    oracle[np.arange(len(y)), y] = 0.98
    q_new = (1.0 - beta) * q_old + beta * oracle
    return q_new, q_old, y, phi


def _softmax_power(q: np.ndarray, inv_t: float, eps: float = 1e-12) -> np.ndarray:
    z = np.clip(q, eps, None) ** inv_t
    return z / z.sum(axis=1, keepdims=True)


def generate_clustered(seed: int, n_images: int = 800, n_cells: int = 1500,
                       k: int = 5, beta0: float = 0.3, sigma: float = 1.0):
    """VG-like regime: relations cluster within images, cell sizes are Zipf-skewed
    (most identified cells have n_c = 2), and the oracle weight shares a latent
    per-image effect so relations from one image are dependent."""
    rng = np.random.default_rng(seed)
    priors = np.random.default_rng(7).dirichlet(np.full(k, 0.8), size=n_cells)
    n_per_image = 1 + rng.poisson(1.8, size=n_images)
    image = np.repeat(np.arange(n_images), n_per_image)
    n = len(image)
    cell_weights = 1.0 / np.arange(1, n_cells + 1) ** 1.1
    cell_weights /= cell_weights.sum()
    phi = rng.choice(n_cells, size=n, p=cell_weights)
    y = np.empty(n, dtype=np.int64)
    for c in np.unique(phi):
        ix = np.flatnonzero(phi == c)
        y[ix] = rng.choice(k, size=len(ix), p=priors[c])
    q_old = priors[phi]
    oracle = np.full((n, k), 0.02 / (k - 1))
    oracle[np.arange(n), y] = 0.98
    u = rng.normal(0.0, sigma, size=n_images)
    beta_i = beta0 / (1.0 + np.exp(-u[image]))          # shared within image
    q_new = (1.0 - beta_i)[:, None] * q_old + beta_i[:, None] * oracle
    return q_new, q_old, y, phi, image


def coverage_arm(n_reps: int = 500, n_truth_reps: int = 4000):
    """Empirical coverage of the cluster-robust Hajek interval in the VG-like
    regime. Truth is the design expectation of the estimator at this N,
    estimated to high precision from independent replications."""
    ests = [decompose_gain(*generate_clustered(20_000 + r)[:4]).reasoning_gain
            for r in range(n_truth_reps)]
    truth = float(np.mean(ests))
    cover_cl, cover_iid, widths = [], [], []
    for r in range(n_reps):
        q1, q0, y, phi, image = generate_clustered(50_000 + r)
        g_cl = decompose_gain(q1, q0, y, phi, groups=image)
        g_iid = decompose_gain(q1, q0, y, phi)
        lo, hi = g_cl.reasoning_ci
        cover_cl.append(lo <= truth <= hi)
        widths.append(hi - lo)
        lo2, hi2 = g_iid.reasoning_ci
        cover_iid.append(lo2 <= truth <= hi2)
    return {
        "truth": truth, "n_reps": n_reps,
        "coverage_clustered": float(np.mean(cover_cl)),
        "coverage_iid_naive": float(np.mean(cover_iid)),
        "mean_width_clustered": float(np.mean(widths)),
    }


def _fit_temperature(q: np.ndarray, y: np.ndarray) -> float:
    grid = np.geomspace(0.05, 20.0, 240)
    nlls = [float(-np.mean(np.log(np.clip(
        _softmax_power(q, 1.0 / t)[np.arange(len(y)), y], 1e-12, None))))
        for t in grid]
    return float(grid[int(np.argmin(nlls))])


def calibration_only_arm(n_reps: int = 200):
    """Discriminant validity: the 'new' model is a temperature-softened copy of
    an overconfident informative model -- identical instance information. The
    raw decomposition moves both channels; the calibration-matched protocol of
    Sec. cifarlt (per-model temperature fitted by held-out likelihood, audit on
    the disjoint half) should leave alignment ~0."""
    raw_r, cal_r, raw_p = [], [], []
    for r in range(n_reps):
        rng = np.random.default_rng(70_000 + r)
        q_mix, _q_prior, y, phi = generate(70_000 + r, beta=0.35, per=100)
        q_old = _softmax_power(q_mix, 3.0)                # overconfident base
        q_new = _softmax_power(q_old, 1.0 / 3.0)          # softened: same info
        half = rng.permutation(len(y))
        cal, aud = half[: len(y) // 2], half[len(y) // 2:]
        t_old = _fit_temperature(q_old[cal], y[cal])
        t_new = _fit_temperature(q_new[cal], y[cal])
        g_raw = decompose_gain(q_new[aud], q_old[aud], y[aud], phi[aud])
        g_cal = decompose_gain(_softmax_power(q_new, 1.0 / t_new)[aud],
                               _softmax_power(q_old, 1.0 / t_old)[aud],
                               y[aud], phi[aud])
        raw_r.append(g_raw.reasoning_gain)
        raw_p.append(g_raw.prior_gain)
        cal_r.append(g_cal.reasoning_gain)
    return {
        "raw_reasoning_mean": float(np.mean(raw_r)),
        "raw_prior_mean": float(np.mean(raw_p)),
        "calibration_matched_reasoning_mean": float(np.mean(cal_r)),
        "calibration_matched_reasoning_sd": float(np.std(cal_r, ddof=1)),
        "n_reps": n_reps,
    }


def hidden_shortcut_arm(n_reps: int = 200):
    """An unrecorded binary feature s varies inside each cell and shifts the
    label distribution; the new model uses s and nothing else beyond the cell
    prior. WAGER must credit this to alignment (documented property: Delta R
    counts any within-cell predictive signal, shortcut or not)."""
    vals = []
    for r in range(n_reps):
        rng = np.random.default_rng(90_000 + r)
        ncell, per, k = 24, 50, 5
        phi = np.repeat(np.arange(ncell), per)
        n = len(phi)
        base = np.random.default_rng(11).dirichlet(np.full(k, 0.8), size=ncell)
        s = rng.integers(0, 2, size=n)                    # unrecorded, within-cell
        tilt = np.where(s[:, None] == 1,
                        np.linspace(0.5, 1.5, k)[None, :],
                        np.linspace(1.5, 0.5, k)[None, :])
        cond = base[phi] * tilt
        cond /= cond.sum(axis=1, keepdims=True)
        y = np.array([rng.choice(k, p=cond[i]) for i in range(n)], dtype=np.int64)
        q_old = base[phi]
        q_new = cond                                      # uses only phi and s
        vals.append(decompose_gain(q_new, q_old, y, phi).reasoning_gain)
    return {"reasoning_mean": float(np.mean(vals)),
            "reasoning_sd": float(np.std(vals, ddof=1)), "n_reps": n_reps}


def prior_only_arm(n_reps: int = 200):
    """No-leakage check: the new model improves ONLY the prior fit (exact cell
    prior vs a miscalibrated one) with heteroscedastic per-example noise in the
    old model; alignment must stay centered at zero while the prior channel is
    clearly positive."""
    r_vals, p_vals = [], []
    for r in range(n_reps):
        rng = np.random.default_rng(110_000 + r)
        q_mix, q_prior, y, phi = generate(110_000 + r, beta=0.0)
        scale = rng.uniform(0.01, 0.12, size=len(y))      # heteroscedastic
        noisy = np.maximum(q_prior + rng.normal(0, 1, q_prior.shape)
                           * scale[:, None], 1e-4)
        noisy /= noisy.sum(axis=1, keepdims=True)
        for c in np.unique(phi):                          # kill accidental alignment
            ix = np.flatnonzero(phi == c)
            noisy[ix] = noisy[rng.permutation(ix)]
        g = decompose_gain(q_prior, noisy, y, phi)        # new = exact prior
        r_vals.append(g.reasoning_gain)
        p_vals.append(g.prior_gain)
    return {"reasoning_mean": float(np.mean(r_vals)),
            "reasoning_sd": float(np.std(r_vals, ddof=1)),
            "prior_mean": float(np.mean(p_vals)), "n_reps": n_reps}


def main():
    betas = np.linspace(0, 0.8, 9)
    recovery = []
    for beta in betas:
        vals = []
        for rep in range(40):
            q1, q0, y, phi = generate(1000 + rep, float(beta))
            vals.append(decompose_gain(q1, q0, y, phi).reasoning_gain)
        recovery.append({
            "beta": float(beta),
            "mean": float(np.mean(vals)),
            "sd": float(np.std(vals, ddof=1)),
        })

    # At beta=0 both models are identical.  Use a randomized, prediction-noise
    # null so p-values are not degenerate at one.
    rng = np.random.default_rng(17)
    null_p = []
    null_r = []
    for rep in range(200):
        q1, q0, y, phi = generate(5000 + rep, 0.0, ncell=16, per=30)
        noise = rng.normal(0, 0.03, size=q1.shape)
        q1 = np.maximum(q1 + noise, 1e-4)
        q1 /= q1.sum(1, keepdims=True)
        # Break any accidental noise-label alignment while preserving phi.
        for c in np.unique(phi):
            ix = np.flatnonzero(phi == c)
            q1[ix] = q1[rng.permutation(ix)]
        res = decompose_gain(q1, q0, y, phi)
        p, _ = cyclic_randomization_test(
            q1, q0, y, phi, n_randomizations=99, seed=9000 + rep
        )
        null_r.append(res.reasoning_gain)
        null_p.append(p)

    out = {
        "recovery": recovery,
        "coverage": coverage_arm(),
        "calibration_only": calibration_only_arm(),
        "hidden_shortcut": hidden_shortcut_arm(),
        "prior_only": prior_only_arm(),
        "null_runs": len(null_p),
        "null_type1_alpha_005": float(np.mean(np.asarray(null_p) <= 0.05)),
        "null_reasoning_mean": float(np.mean(null_r)),
        "null_p_values": null_p,
        "null_reasoning": null_r,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: v for k, v in out.items() if not isinstance(v, list)}, indent=2))
    return out


if __name__ == "__main__":
    main()
