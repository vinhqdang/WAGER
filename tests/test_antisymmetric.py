"""Tests for the redesigned within-cell antisymmetric WAGER algorithm."""
import numpy as np

from wager.antisymmetric import (
    cyclic_randomization_test,
    decompose_gain,
    gain_matrix,
    score_matrix,
)


def test_brier_score_is_higher_for_truthful_one_hot_prediction():
    q = np.array([[0.9, 0.1], [0.1, 0.9]])
    s = score_matrix(q)
    assert s[0, 0] > s[0, 1]
    assert s[1, 1] > s[1, 0]


def test_exact_gain_identity_and_quadratic_covariance_identity():
    rng = np.random.default_rng(1)
    n, k = 600, 4
    phi = np.repeat(np.arange(12), n // 12)
    y = rng.integers(k, size=n)
    q0 = np.full((n, k), 1 / k)
    q1 = 0.7 * q0
    q1[np.arange(n), y] += 0.3
    result = decompose_gain(q1, q0, y, phi)

    assert np.isclose(result.total_gain, result.prior_gain + result.reasoning_gain)

    # For quadratic score, R = 2 sum_y Cov(q1-q0, 1[Y=y] | phi),
    # with finite-cell covariance defined by the independent cross-coupling.
    delta = q1 - q0
    cov_sum = 0.0
    for c in np.unique(phi):
        ix = np.flatnonzero(phi == c)
        nc = len(ix)
        onehot = np.eye(k)[y[ix]]
        # The U-statistic normalization n/(n-1) makes this equal to the
        # observed-minus-crossed estimator used by WAGER.
        cov = (nc / (nc - 1.0)) * np.mean(
            (delta[ix] - delta[ix].mean(0)) * (onehot - onehot.mean(0)), axis=0
        )
        cov_sum += (nc / n) * 2.0 * cov.sum()
    assert np.isclose(result.reasoning_gain, cov_sum)


def test_cell_constant_model_change_has_zero_reasoning_gain():
    rng = np.random.default_rng(2)
    k, ncell, per = 5, 20, 30
    phi = np.repeat(np.arange(ncell), per)
    y = rng.integers(k, size=len(phi))
    q0_cell = rng.dirichlet(np.ones(k), size=ncell)
    q1_cell = rng.dirichlet(np.ones(k), size=ncell)
    result = decompose_gain(q1_cell[phi], q0_cell[phi], y, phi)
    assert abs(result.reasoning_gain) < 1e-12
    # Individual labels can be easier or harder under a cell-constant change,
    # but their within-cell antisymmetric mean is identically zero.
    for c in np.unique(phi):
        assert abs(result.alignment[phi == c].mean()) < 1e-12


def test_instance_alignment_is_detected_even_when_cell_marginals_are_fixed():
    rng = np.random.default_rng(3)
    k, ncell, per = 4, 25, 40
    phi = np.repeat(np.arange(ncell), per)
    y = rng.integers(k, size=len(phi))
    q0 = np.full((len(phi), k), 1 / k)
    q1 = np.full((len(phi), k), 0.1 / (k - 1))
    q1[np.arange(len(phi)), y] = 0.9
    result = decompose_gain(q1, q0, y, phi)
    assert result.reasoning_gain > 0.8
    assert result.reasoning_ci[0] > 0


def test_singletons_are_reported_and_excluded():
    q0 = np.full((5, 3), 1 / 3)
    q1 = q0.copy()
    q1[:, 0] += 0.1
    q1[:, 1:] -= 0.05
    y = np.array([0, 1, 0, 2, 1])
    phi = np.array([0, 0, 1, 2, 2])
    result = decompose_gain(q1, q0, y, phi)
    assert result.n_total == 5
    assert result.n_identified == 4
    assert result.n_singletons == 1
    assert np.isnan(result.alignment[2])


def test_cluster_robust_interval_runs():
    rng = np.random.default_rng(4)
    n, k = 800, 3
    phi = np.repeat(np.arange(20), 40)
    groups = np.repeat(np.arange(100), 8)
    y = rng.integers(k, size=n)
    q0 = np.full((n, k), 1 / k)
    logits = rng.normal(size=(n, k))
    logits[np.arange(n), y] += 0.8
    q1 = np.exp(logits - logits.max(1, keepdims=True))
    q1 /= q1.sum(1, keepdims=True)
    result = decompose_gain(q1, q0, y, phi, groups=groups)
    assert np.isfinite(result.standard_error)
    assert result.reasoning_ci[0] < result.reasoning_gain < result.reasoning_ci[1]


def test_cyclic_randomization_separates_aligned_from_null():
    rng = np.random.default_rng(5)
    n, k = 600, 3
    phi = np.repeat(np.arange(15), 40)
    y = rng.integers(k, size=n)
    q0 = np.full((n, k), 1 / k)
    q1 = np.full((n, k), 0.05)
    q1[np.arange(n), y] = 0.9
    q1 /= q1.sum(1, keepdims=True)
    p, null = cyclic_randomization_test(
        q1, q0, y, phi, n_randomizations=199, seed=0
    )
    result = decompose_gain(q1, q0, y, phi)
    assert p <= 0.01
    assert result.reasoning_gain > np.quantile(null, 0.99)


def test_gain_matrix_supports_floored_log_score():
    q0 = np.array([[0.5, 0.5]])
    q1 = np.array([[1.0, 0.0]])
    h = gain_matrix(q1, q0, score="log", eps=1e-4)
    assert np.all(np.isfinite(h))
    assert h[0, 0] > 0 and h[0, 1] < 0
