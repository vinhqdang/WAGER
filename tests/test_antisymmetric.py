"""Tests for the redesigned within-cell antisymmetric WAGER algorithm."""
from statistics import NormalDist

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


def test_log_score_bregman_covariance_identity():
    """Corollary (Bregman scores, log case): under the log score, R = sum_y
    Cov(log q1(y|X) - log q0(y|X), 1[Y=y] | phi), the direct log-odds analogue of the
    quadratic-score covariance identity checked above."""
    rng = np.random.default_rng(8)
    n, k = 500, 4
    phi = np.repeat(np.arange(20), n // 20)
    y = rng.integers(k, size=n)
    q0 = rng.dirichlet(np.ones(k), size=n)
    q1 = rng.dirichlet(np.ones(k), size=n)
    eps = 1e-6
    result = decompose_gain(q1, q0, y, phi, score="log", eps=eps)

    logdiff = np.log(np.maximum(q1, eps)) - np.log(np.maximum(q0, eps))
    cov_sum = 0.0
    for c in np.unique(phi):
        ix = np.flatnonzero(phi == c)
        nc = len(ix)
        onehot = np.eye(k)[y[ix]]
        cov = (nc / (nc - 1.0)) * np.mean(
            (logdiff[ix] - logdiff[ix].mean(0)) * (onehot - onehot.mean(0)), axis=0
        )
        cov_sum += (nc / n) * cov.sum()
    assert np.isclose(result.reasoning_gain, cov_sum, atol=1e-8)


def test_trivial_phi_total_gain_matches_diebold_mariano_statistic():
    """Corollary (relation to Diebold-Mariano/Giacomini-White): at the trivial
    (single-cell) phi, Delta_T_hat and its normal-approximation interval are exactly
    the sample mean and standard error of the paired score differential -- the
    classical (unclustered) Diebold-Mariano statistic for this score contrast."""
    rng = np.random.default_rng(9)
    n, k = 400, 5
    y = rng.integers(k, size=n)
    q0 = rng.dirichlet(np.ones(k), size=n)
    q1 = rng.dirichlet(np.ones(k), size=n)
    phi = np.zeros(n, dtype=np.int64)
    result = decompose_gain(q1, q0, y, phi)

    h = gain_matrix(q1, q0)
    paired_diff = h[np.arange(n), y]
    dm_mean = float(paired_diff.mean())
    dm_se = float(paired_diff.std(ddof=0)) / np.sqrt(n)

    z = NormalDist().inv_cdf(0.975)
    se_from_ci = (result.total_ci[1] - result.total_ci[0]) / (2.0 * z)

    assert np.isclose(result.total_gain, dm_mean)
    assert np.isclose(se_from_ci, dm_se)


def test_sensitivity_bound_ordering_crude_ge_tight_ge_exact_bias():
    """Proposition (sensitivity to an unrecorded confounder) and its worst-case
    Corollary: on an explicit discrete population with a known omitted confounder Z,
    the exact coarsening bias is dominated by the per-cell-dispersion ("tight") bound,
    which is in turn dominated by the data-free Cauchy-Schwarz/Popoviciu ("crude")
    bound KM/2 -- verifying both inequalities of Eq. (sensitivity-bound), not just
    their combination."""
    K = 2
    M = 0.40  # matches max(|H(y)|) in the atoms below
    # (phi, Z, weight, H(y) mean vector [point mass -> Var(H|phi,Z)=0], Pr(Y=y|phi,Z))
    atoms = [
        (0, 0, 1.0, np.array([0.10, -0.10]), np.array([0.9, 0.1])),
        (0, 1, 1.0, np.array([0.30, 0.10]), np.array([0.3, 0.7])),
        (1, 0, 1.0, np.array([-0.20, 0.40]), np.array([0.6, 0.4])),
        (1, 1, 1.0, np.array([0.05, 0.05]), np.array([0.2, 0.8])),
    ]
    for c in (0, 1):
        cell = [a for a in atoms if a[0] == c]
        w = np.array([a[2] for a in cell])
        w = w / w.sum()
        a_mat = np.array([a[3] for a in cell])  # (n_Z, K)
        b_mat = np.array([a[4] for a in cell])

        mean_a = (w[:, None] * a_mat).sum(0)
        mean_b = (w[:, None] * b_mat).sum(0)
        var_a = (w[:, None] * (a_mat - mean_a) ** 2).sum(0)
        var_b = (w[:, None] * (b_mat - mean_b) ** 2).sum(0)
        cov_ab = (w[:, None] * (a_mat - mean_a) * (b_mat - mean_b)).sum(0)

        exact_bias = cov_ab.sum()  # Delta_R_c(phi) - E[Delta_R_(phi,Z) | phi=c]

        # Population variance of H(y) | phi=c: atoms are point masses on H, so this
        # equals var_a exactly here (the law-of-total-variance remainder is zero),
        # which the tight bound is entitled to use directly.
        var_h = var_a
        # Population variance of the label indicator | phi=c: p_y(c)(1-p_y(c)) is an
        # upper bound on var_b (law of total variance), generally strict.
        p_y = mean_b
        var_ind = p_y * (1.0 - p_y)
        assert np.all(var_ind >= var_b - 1e-12)

        denom_a = np.sqrt(var_a.sum())
        denom_b = np.sqrt(var_b.sum())
        rho = cov_ab.sum() / (denom_a * denom_b) if denom_a > 0 and denom_b > 0 else 0.0
        assert -1.0 - 1e-9 <= rho <= 1.0 + 1e-9

        tight_bound = abs(rho) * np.sqrt(var_h.sum()) * np.sqrt(var_ind.sum())
        crude_bound = abs(rho) * K * M / 2.0

        assert abs(exact_bias) <= tight_bound + 1e-9
        assert tight_bound <= crude_bound + 1e-9


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


def test_worked_example_of_the_paper_reproduces_every_printed_value():
    """The four-point example the paper works through by hand (Section 2).

    One cell, four cases, two labels, cell label frequencies (3/4, 1/4).  The old
    model is uninformative within the cell.  Model A moves every case to the cell
    frequencies; model B moves each case towards its own correct label by the same
    amount.  Every quantity the paper prints is checked here, including the
    covariance form of the remainder and its (n_c - 1)/n_c attenuation.
    """
    y = np.array([0, 0, 0, 1])
    phi = np.zeros(4, dtype=int)
    q_old = np.tile([0.5, 0.5], (4, 1))
    q_a = np.tile([0.75, 0.25], (4, 1))
    q_b = np.array([[0.75, 0.25], [0.75, 0.25], [0.75, 0.25], [0.25, 0.75]])

    # Eq. (worked-h): the gain vector is +3/8 towards the label moved to, -5/8 away.
    for q_new in (q_a, q_b):
        h = gain_matrix(q_new, q_old)
        assert np.allclose(np.sort(np.unique(np.round(h, 12))), [-0.625, 0.375])

    # Model A: a within-cell-constant change earns prior fit and exactly no resolution.
    a = decompose_gain(q_a, q_old, y, phi)
    assert np.isclose(a.total_gain, 1 / 8)
    assert np.isclose(a.prior_gain, 1 / 8)
    assert np.isclose(a.alignment_gain, 0.0, atol=1e-15)

    # Model B: the total understates the resolution gain, because prior fit worsens.
    b = decompose_gain(q_b, q_old, y, phi)
    assert np.isclose(b.total_gain, 3 / 8)
    assert np.isclose(b.prior_gain, -1 / 8)
    assert np.isclose(b.alignment_gain, 1 / 2)
    assert np.isclose(b.total_gain, b.prior_gain + b.alignment_gain)

    # The in-sample covariance plug-in of Theorem 1 is attenuated by exactly 3/4.
    dq = q_b - q_old
    cov = sum(
        np.mean(dq[:, k] * (y == k)) - np.mean(dq[:, k]) * np.mean(y == k)
        for k in range(2)
    )
    assert np.isclose(2 * cov, 3 / 8)
    assert np.isclose(2 * cov, (4 - 1) / 4 * b.alignment_gain)


def test_transported_gain_is_not_prior_fit_but_fit_minus_dispersion():
    """Proposition 2: dP = mean-forecast-fit improvement minus dispersion increase.

    Also pins the counterexample the paper uses to retire the name "prior-fit
    gain": both models' mean forecast can sit exactly on the cell frequencies
    while the transported channel absorbs the entire observed gain.
    """
    y = np.array([0, 0, 1, 1])
    phi = np.zeros(4, dtype=int)
    # Old model is maximally sharp but carries no within-cell information.
    q_old = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
    q_new = np.tile([0.5, 0.5], (4, 1))
    p = np.array([np.mean(y == k) for k in range(2)])
    assert np.allclose(q_old.mean(0), p) and np.allclose(q_new.mean(0), p)

    r = decompose_gain(q_new, q_old, y, phi)
    assert np.isclose(r.total_gain, 0.5)
    assert np.isclose(r.prior_gain, 0.5)
    assert np.isclose(r.alignment_gain, 0.0, atol=1e-12)

    # The identity itself, against the in-sample transport law, on random inputs.
    rng = np.random.default_rng(11)
    for _ in range(25):
        n, K = int(rng.integers(4, 40)), int(rng.integers(2, 6))
        a = rng.dirichlet(np.ones(K), size=n)
        b = rng.dirichlet(np.ones(K), size=n)
        yy = rng.integers(0, K, size=n)
        pp = np.array([np.mean(yy == k) for k in range(K)])
        in_sample_dp = float(
            np.mean(2 * (a @ pp) - (a * a).sum(1))
            - np.mean(2 * (b @ pp) - (b * b).sum(1))
        )
        fit = ((pp - b.mean(0)) ** 2).sum() - ((pp - a.mean(0)) ** 2).sum()
        dispersion = a.var(0).sum() - b.var(0).sum()
        assert np.isclose(in_sample_dp, fit - dispersion, atol=1e-12)


def test_equally_fine_partitions_can_disagree_without_limit():
    """The Section 6 limitation: fineness does not determine the estimand.

    Two partitions of the same four cases, both 2x2 and both fully identified,
    disagree about whether the whole gain is case-level or wholly transported.
    Neither coarsens the other, so the coarsening proposition cannot arbitrate.
    """
    y = np.array([0, 0, 1, 1])
    q_old = np.tile([0.5, 0.5], (4, 1))
    q_new = np.array([[0.9, 0.1], [0.9, 0.1], [0.1, 0.9], [0.1, 0.9]])

    heterogeneous = decompose_gain(q_new, q_old, y, np.array([0, 1, 0, 1]))
    single = decompose_gain(q_new, q_old, y, np.zeros(4, dtype=int))
    homogeneous = decompose_gain(q_new, q_old, y, np.array([0, 0, 1, 1]))

    for r in (heterogeneous, single, homogeneous):
        assert np.isclose(r.total_gain, 0.48)
        assert r.coverage == 1.0
    assert np.isclose(heterogeneous.alignment_gain, 1.60)
    assert np.isclose(single.alignment_gain, 32 / 30)
    assert np.isclose(homogeneous.alignment_gain, 0.0, atol=1e-12)
    # Same granularity, incompatible verdicts.
    assert heterogeneous.n_cells == homogeneous.n_cells == 2


def test_only_the_covariance_channel_survives_a_label_shift():
    """Section 2.1: the decomposition predicts which advantage survives.

    Model A's gain is entirely transported and reverses sign under a shift in
    label frequencies; model B's is entirely covariance and is untouched.
    """
    y = np.array([0, 0, 0, 1])
    phi = np.zeros(4, dtype=int)
    q_old = np.tile([0.5, 0.5], (4, 1))
    q_a = np.tile([0.75, 0.25], (4, 1))
    q_b = np.array([[0.75, 0.25], [0.75, 0.25], [0.75, 0.25], [0.25, 0.75]])

    ra, rb = decompose_gain(q_a, q_old, y, phi), decompose_gain(q_b, q_old, y, phi)
    assert np.isclose(ra.alignment_gain, 0.0, atol=1e-15)
    assert np.isclose(rb.prior_gain + rb.alignment_gain, rb.total_gain)

    p_bench = np.array([0.75, 0.25])
    p_deploy = np.array([0.25, 0.75])
    w = (p_deploy / p_bench)[y]
    w = w / w.mean()
    shifted = {}
    for name, q_new in (("A", q_a), ("B", q_b)):
        h = gain_matrix(q_new, q_old)[np.arange(4), y]
        shifted[name] = float(np.average(h, weights=w))

    assert np.isclose(ra.total_gain, 1 / 8) and np.isclose(shifted["A"], -3 / 8)
    assert np.isclose(rb.total_gain, 3 / 8) and np.isclose(shifted["B"], 3 / 8)
    # A improved on the benchmark and is worse than q_old after the shift.
    assert ra.total_gain > 0 > shifted["A"]
