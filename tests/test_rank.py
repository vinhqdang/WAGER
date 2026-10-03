"""Within-cell AUC: brute-force agreement and the two invariances it claims."""
import numpy as np
import pytest

from wager.rank import _auc, _blocks, within_cell_auc, within_cell_auc_contrast


def brute(q, y, phi, w=None):
    w = np.ones(len(y)) if w is None else w
    lq = np.log(q)
    num = den = 0.0
    for c in np.unique(phi):
        idx = np.flatnonzero(phi == c)
        labs = np.unique(y[idx])
        for a in range(len(labs)):
            for b in range(a + 1, len(labs)):
                P = idx[y[idx] == labs[a]]
                N = idx[y[idx] == labs[b]]
                for i in P:
                    for j in N:
                        si = lq[i, labs[a]] - lq[i, labs[b]]
                        sj = lq[j, labs[a]] - lq[j, labs[b]]
                        num += w[i] * w[j] * ((si > sj) + 0.5 * (si == sj))
                        den += w[i] * w[j]
    return num / den


def data(rng, n=300, k=5):
    q = rng.dirichlet(np.ones(k), size=n)
    q[::7] = q[3]                      # exact ties
    y = rng.integers(0, k, size=n)
    phi = rng.integers(0, 12, size=n)
    return q, y, phi


def test_matches_brute_force_with_ties_and_weights():
    rng = np.random.default_rng(3)
    q, y, phi = data(rng)
    assert within_cell_auc(q, y, phi) == pytest.approx(brute(q, y, phi), abs=1e-12)
    w = rng.integers(0, 4, size=len(y)).astype(float)
    bl = _blocks(np.log(q), y, phi)
    assert _auc(bl, w) == pytest.approx(brute(q, y, phi, w), abs=1e-12)


def test_invariant_to_temperature_and_per_cell_prior_shift():
    rng = np.random.default_rng(5)
    q, y, phi = data(rng)
    base = within_cell_auc(q, y, phi)
    for T in (0.3, 2.5):
        qt = q ** (1 / T)
        qt /= qt.sum(1, keepdims=True)
        assert within_cell_auc(qt, y, phi) == pytest.approx(base, abs=1e-12)
    shift = rng.normal(0, 2, size=(phi.max() + 1, q.shape[1]))
    qs = q * np.exp(shift[phi])
    qs /= qs.sum(1, keepdims=True)
    assert within_cell_auc(qs, y, phi) == pytest.approx(base, abs=1e-12)


def test_contrast_of_a_model_with_itself_is_zero():
    rng = np.random.default_rng(9)
    q, y, phi = data(rng)
    r = within_cell_auc_contrast(q, q, y, phi, groups=np.arange(len(y)) // 3,
                                 n_boot=50)
    assert r.difference == 0.0 and r.ci == (0.0, 0.0)
