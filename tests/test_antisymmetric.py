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


def test_attenuation_proposition_matches_insample_plugin():
    """Proposition (exact attenuation): the naive in-sample plug-in transported
    score P_tilde_i = mean_j H_i(y_j) over the WHOLE cell (including i) equals
    WAGER's leave-one-out P_i plus R_i / n_c, so the plug-in's implied alignment
    is shrunk by exactly (n_c - 1) / n_c relative to WAGER's."""
    rng = np.random.default_rng(7)
    n, k = 500, 5
    phi = rng.integers(0, 40, size=n)
    y = rng.integers(k, size=n)
    q0 = rng.dirichlet(np.ones(k), size=n)
    q1 = rng.dirichlet(np.ones(k), size=n)
    result = decompose_gain(q1, q0, y, phi)

    h = gain_matrix(q1, q0)
    _, inv, counts = np.unique(phi, return_inverse=True, return_counts=True)
    nc = counts[inv].astype(np.float64)
    idx = np.flatnonzero(counts[inv] >= 2)

    label_counts_by_cell = np.zeros((len(counts), k))
    np.add.at(label_counts_by_cell, (inv, y), 1.0)
    m_cy = label_counts_by_cell[inv]
    p_tilde = (h * m_cy).sum(axis=1) / nc
    r_tilde = h[np.arange(n), y] - p_tilde

    hat_p, hat_r = result.transported, result.alignment
    assert np.allclose(p_tilde[idx], hat_p[idx] + hat_r[idx] / nc[idx], atol=1e-9)
    assert np.allclose(r_tilde[idx], (nc[idx] - 1.0) / nc[idx] * hat_r[idx], atol=1e-9)


def test_coarsening_proposition_law_of_total_covariance():
    """Proposition (coarsening decomposition): merging two prior cells changes
    the population alignment gain by exactly the between-cell covariance term
    predicted by the law of total covariance. Verified on an explicit discrete
    population (exact expectations, no sampling noise)."""
    atoms = [
        (0, 1.0, np.array([0.10, -0.10]), np.array([0.9, 0.1])),
        (0, 1.0, np.array([0.30, 0.10]), np.array([0.3, 0.7])),
        (1, 1.0, np.array([-0.20, 0.40]), np.array([0.6, 0.4])),
        (1, 1.0, np.array([0.05, 0.05]), np.array([0.2, 0.8])),
    ]
    fine_cells = sorted({a[0] for a in atoms})

    def cell_stats(atom_list):
        w_raw = np.array([a[1] for a in atom_list], dtype=float)
        wtot = w_raw.sum()
        w = w_raw / wtot
        H = np.array([a[2] for a in atom_list])
        pY = np.array([a[3] for a in atom_list])
        e_h = (w[:, None] * H).sum(0)
        p_y = (w[:, None] * pY).sum(0)
        e_hy = (w[:, None] * H * pY).sum(0)
        delta_r = (e_hy - e_h * p_y).sum()
        return wtot, e_h, p_y, delta_r

    fine_stats = {c: cell_stats([a for a in atoms if a[0] == c]) for c in fine_cells}
    total_w = sum(v[0] for v in fine_stats.values())
    e_delta_r = sum(v[0] / total_w * v[3] for v in fine_stats.values())

    probs_c = np.array([fine_stats[c][0] / total_w for c in fine_cells])
    e_h_mat = np.array([fine_stats[c][1] for c in fine_cells])
    p_y_mat = np.array([fine_stats[c][2] for c in fine_cells])
    mean_e_h = (probs_c[:, None] * e_h_mat).sum(0)
    mean_p_y = (probs_c[:, None] * p_y_mat).sum(0)
    cov_between = (probs_c[:, None] * (e_h_mat - mean_e_h) * (p_y_mat - mean_p_y)).sum()

    _, _, _, delta_r_coarse = cell_stats(atoms)
    assert np.isclose(delta_r_coarse, e_delta_r + cov_between, atol=1e-12)
