"""Unit tests for WAGER core math (algorithm.md sections 3-4)."""
import numpy as np
import pytest

from wager.core import (
    kt_projection,
    prior_excess_logscore,
    wealth_process,
    betting_mean_ci,
    betting_mean_point,
)
from wager.pipeline import ModelData, run_wager_permutations
from wager.rgr import reasoning_gain_ratio, fieller_ratio_ci


def _rng(seed=0):
    return np.random.default_rng(seed)


def test_kt_projection_normalized_and_smoothed():
    K = 4
    q = np.array([[0.7, 0.1, 0.1, 0.1], [0.6, 0.2, 0.1, 0.1]])
    phi = np.array([0, 0])
    cell_proj, cell_corr, coarse_proj, glob, unif = kt_projection(q, phi, K, m=1.0)
    assert np.isclose(cell_proj[0].sum(), 1.0)
    assert np.allclose(unif, 0.25)
    # single cell -> global == cell mean -> shrinkage is a no-op here
    raw = q.mean(0)
    assert np.allclose(cell_proj[0], raw)


def test_kt_projection_unseen_cell_backs_off_to_uniform():
    K = 3
    q = np.array([[0.8, 0.1, 0.1]])
    cell_proj, cell_corr, coarse_proj, glob, unif = kt_projection(q, np.array([5]), K)
    d, e = prior_excess_logscore(
        np.array([[0.5, 0.3, 0.2]]), np.array([0]), np.array([99]),
        cell_proj, cell_corr, coarse_proj, glob, unif, c=np.log(K)
    )
    # unseen cell -> projection = global backoff -> scores finite
    assert np.isfinite(d[0]) and np.isfinite(e[0])


def test_wealth_nonneg_and_evalue_under_null_is_controlled():
    # Under H0 (mu<=0): feed mean-zero / negative-mean clipped scores.
    rng = _rng(1)
    exceed = 0
    runs = 400
    alpha = 0.1
    for _ in range(runs):
        d = rng.normal(-0.0, 0.5, size=300)
        d = np.clip(d, -1, 1)
        d = d - d.mean()  # exactly mean zero -> boundary null
        e_value, wealth, _ = wealth_process(d, c=1.0)
        if wealth.max() >= 1 / alpha:
            exceed += 1
    # Ville: P(ever exceed 1/alpha) <= alpha. Allow Monte-Carlo slack.
    assert exceed / runs <= alpha + 0.05


def test_wealth_grows_under_alternative():
    rng = _rng(2)
    d = rng.normal(0.3, 0.3, size=2000)
    d = np.clip(d, -1, 1)
    e_value, wealth, growth = wealth_process(d, c=1.0)
    assert e_value > 100  # strong evidence accumulates
    assert growth > 0


def test_betting_ci_covers_true_mean():
    rng = _rng(3)
    covered = 0
    trials = 200
    true_mu = 0.2
    for _ in range(trials):
        x = np.clip(rng.normal(true_mu, 0.4, size=500), -1, 1)
        lo, hi = betting_mean_ci(x, c=1.0, alpha=0.1, n_grid=201)
        if lo <= true_mu <= hi:
            covered += 1
    # anytime-valid -> coverage at least 1-alpha (typically conservative)
    assert covered / trials >= 0.90


def test_betting_ci_brackets_empirical_mean():
    rng = _rng(4)
    x = np.clip(rng.normal(0.25, 0.3, size=400), -1, 1)
    lo, hi = betting_mean_ci(x, c=1.0, alpha=0.05, n_grid=201)
    assert lo <= betting_mean_point(x) <= hi


def test_model_equals_prior_gives_zero_reasoning():
    # If q_f is constant within each phi cell, q_bar_f == q_f -> d == 0.
    rng = _rng(5)
    K, ncell, per = 5, 20, 60
    phi = np.repeat(np.arange(ncell), per)
    # one fixed distribution per cell
    cell_dist = rng.dirichlet(np.ones(K), size=ncell)
    q = cell_dist[phi]
    y = np.array([rng.choice(K, p=cell_dist[c]) for c in phi])
    group = np.arange(len(y))
    data = ModelData("prior", q, y, phi, group)
    res = run_wager_permutations(data, R=20, seed=0)
    assert abs(res.I_reason) < 0.05
    assert res.e_value < 5.0  # no sustained evidence of reasoning


def test_rgr_fieller_runs():
    rng = _rng(6)
    num = rng.normal(0.2, 0.3, 500)
    den = rng.normal(0.5, 0.3, 500)
    lo, hi = fieller_ratio_ci(num, den, alpha=0.05)
    assert lo < hi
    assert lo < 0.4 < hi  # true ratio ~0.4 inside
