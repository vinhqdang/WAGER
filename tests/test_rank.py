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


def brute_relation(q, y, phi):
    """Each cell's pairwise AUCs weighted by n_c(y) n_c(z) / n_c."""
    lq = np.log(q)
    num = den = 0.0
    for c in np.unique(phi):
        idx = np.flatnonzero(phi == c)
        labs = np.unique(y[idx])
        for a in range(len(labs)):
            for b in range(a + 1, len(labs)):
                P = idx[y[idx] == labs[a]]
                N = idx[y[idx] == labs[b]]
                hit = sum(((lq[i, labs[a]] - lq[i, labs[b]]) > (lq[j, labs[a]] - lq[j, labs[b]]))
                          + 0.5 * ((lq[i, labs[a]] - lq[i, labs[b]]) == (lq[j, labs[a]] - lq[j, labs[b]]))
                          for i in P for j in N)
                num += hit / len(idx)
                den += len(P) * len(N) / len(idx)
    return num / den


def test_relation_weighting_matches_brute_force_and_differs_from_comparison():
    rng = np.random.default_rng(11)
    q, y, phi = data(rng)
    phi[:120] = 0                      # one large cell, so the two weightings differ
    r = within_cell_auc(q, y, phi, weighting="relation")
    assert r == pytest.approx(brute_relation(q, y, phi), abs=1e-12)
    assert abs(r - within_cell_auc(q, y, phi)) > 1e-4
    qt = q ** 2.0
    qt /= qt.sum(1, keepdims=True)
    assert within_cell_auc(qt, y, phi, weighting="relation") == pytest.approx(r, abs=1e-12)


def brute_pair(q, y, phi):
    """Per label pair, counts summed over cells; pair AUCs averaged with equal weight."""
    lq = np.log(q)
    num, den = {}, {}
    for c in np.unique(phi):
        idx = np.flatnonzero(phi == c)
        labs = np.unique(y[idx])
        for a in range(len(labs)):
            for b in range(a + 1, len(labs)):
                P = idx[y[idx] == labs[a]]
                N = idx[y[idx] == labs[b]]
                hit = sum(((lq[i, labs[a]] - lq[i, labs[b]]) > (lq[j, labs[a]] - lq[j, labs[b]]))
                          + 0.5 * ((lq[i, labs[a]] - lq[i, labs[b]]) == (lq[j, labs[a]] - lq[j, labs[b]]))
                          for i in P for j in N)
                key = (labs[a], labs[b])
                num[key] = num.get(key, 0.0) + hit
                den[key] = den.get(key, 0.0) + len(P) * len(N)
    return np.mean([num[k] / den[k] for k in num if den[k] > 0])


def test_pair_weighting_matches_brute_force_with_ties():
    rng = np.random.default_rng(13)
    q, y, phi = data(rng)
    assert within_cell_auc(q, y, phi, weighting="pair") == pytest.approx(
        brute_pair(q, y, phi), abs=1e-12)


def test_pair_weighting_invariant_to_temperature_and_per_cell_prior_shift():
    rng = np.random.default_rng(15)
    q, y, phi = data(rng)
    base = within_cell_auc(q, y, phi, weighting="pair")
    for T in (0.3, 2.5):
        qt = q ** (1 / T)
        qt /= qt.sum(1, keepdims=True)
        assert within_cell_auc(qt, y, phi, weighting="pair") == pytest.approx(base, abs=1e-12)
    shift = rng.normal(0, 2, size=(phi.max() + 1, q.shape[1]))
    qs = q * np.exp(shift[phi])
    qs /= qs.sum(1, keepdims=True)
    assert within_cell_auc(qs, y, phi, weighting="pair") == pytest.approx(base, abs=1e-12)


def test_contrast_draws_reproduce_the_interval():
    rng = np.random.default_rng(17)
    q, y, phi = data(rng)
    q2 = q ** 2.0
    q2 /= q2.sum(1, keepdims=True)
    r = within_cell_auc_contrast(q, q2, y, phi, groups=np.arange(len(y)) // 3,
                                 n_boot=120, weighting="pair")
    assert r.draws is not None and r.draws.shape == (120,)
    assert r.difference == pytest.approx(r.auc_new - r.auc_old, abs=1e-12)
    assert tuple(np.percentile(r.draws, [2.5, 97.5])) == pytest.approx(r.ci, abs=1e-12)


def test_label_offset_shift_leaves_contrast_exactly_zero_with_tiny_probabilities():
    """Entries down to ~1e-20 are not clipped, so a per-label log-offset is a no-op."""
    rng = np.random.default_rng(19)
    n, k = 400, 5
    logits = rng.normal(0, 12, size=(n, k))
    q = np.exp(logits - logits.max(1, keepdims=True))
    q /= q.sum(1, keepdims=True)
    q[::7] = q[3]                                  # exact ties survive the shift
    y = rng.integers(0, k, size=n)
    phi = rng.integers(0, 12, size=n)
    assert q.min() < 1e-19
    b = rng.normal(0, 1.5, size=k)
    q2 = q * np.exp(b)[None, :]
    q2 /= q2.sum(1, keepdims=True)
    groups = np.arange(n) // 3
    n_y = np.bincount(y)[y].astype(float)
    cases = [
        dict(weighting="comparison"),
        dict(weighting="relation"),
        dict(weighting="pair"),
        dict(weighting="comparison", weights=1.0 / n_y),
    ]
    for kw in cases:
        r = within_cell_auc_contrast(q2, q, y, phi, groups, n_boot=20, **kw)
        assert abs(r.difference) < 1e-12, kw
        assert abs(r.auc_new - r.auc_old) < 1e-12, kw


def test_exact_zero_probability_is_refused():
    q = np.full((4, 3), 1 / 3)
    q[0] = [0.0, 0.5, 0.5]
    y = np.array([0, 1, 0, 1])
    phi = np.zeros(4, dtype=int)
    with pytest.raises(ValueError):
        within_cell_auc(q, y, phi)
