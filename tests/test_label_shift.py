"""The label-shift split: unit weights reproduce the estimator, and a gain that is
constant within every cell has no case-level part under any reweighting."""
import importlib.util
import pathlib

import numpy as np
import pytest

from wager.antisymmetric import decompose_gain, gain_matrix

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_label_shift",
                                              ROOT / "experiments/run_label_shift.py")
L = importlib.util.module_from_spec(spec)
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "experiments"))
spec.loader.exec_module(L)


def data(seed, n=2000, k=5, cells=30):
    rng = np.random.default_rng(seed)
    return (rng.dirichlet(np.ones(k), n), rng.dirichlet(np.ones(k), n),
            rng.integers(0, k, n), rng.integers(0, cells, n), rng)


def test_unit_weights_reproduce_the_estimator():
    qa, qb, y, phi, _ = data(0)
    g = decompose_gain(qa, qb, y, phi)
    T, P, R = L.weighted_split(gain_matrix(qa, qb), y, phi, np.ones(len(y)))
    assert (T, P, R) == pytest.approx((g.total_gain, g.prior_gain, g.alignment_gain), abs=1e-12)


def test_cell_constant_gain_has_no_case_level_part_under_shift():
    _, _, y, phi, rng = data(1)
    k = 5
    qa = rng.dirichlet(np.ones(k), 30)[phi]
    qb = rng.dirichlet(np.ones(k), 30)[phi]
    w = L.shift_weights(y, phi)
    T, P, R = L.weighted_split(gain_matrix(qa, qb), y, phi, w)
    assert R == pytest.approx(0.0, abs=1e-12)
    assert T == pytest.approx(P, abs=1e-12)


def test_shift_weights_equalise_labels_within_cells():
    _, _, y, phi, _ = data(2)
    w = L.shift_weights(y, phi)
    for c in np.unique(phi):
        m = phi == c
        tot = np.bincount(y[m], weights=w[m])[np.unique(y[m])]
        assert np.allclose(tot, tot[0])
