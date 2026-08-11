"""Guard the conventions the SGG checkpoint audit depends on.

The evaluation dumps encode predicates and object classes 1-indexed and carry a
background column at index 0 that PredCls does not score. Getting either wrong
would silently shift every label by one and produce a plausible but meaningless
audit, so this builds a dump-shaped fixture whose correct answer is known and
checks the driver's loader against it.
"""
from __future__ import annotations

import importlib.util
import pathlib

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DRIVER = ROOT / "experiments/run_sgg_audit_wager.py"


def _load_driver(tmp_path, mdir):
    """Import the driver module with its data directory pointed at a fixture."""
    src = DRIVER.read_text().replace(
        'MDIR = ROOT / "data/vg_motifs"', f'MDIR = pathlib.Path({str(mdir)!r})')
    mod_path = tmp_path / "driver_under_test.py"
    mod_path.write_text(src)
    spec = importlib.util.spec_from_file_location("driver_under_test", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def fixture_dir(tmp_path):
    d = tmp_path / "vg_motifs"
    d.mkdir()
    rng = np.random.default_rng(0)
    n = 400
    # background column is deliberately large so a failure to drop it would show
    probs = np.concatenate([np.full((n, 1), 50.0), rng.random((n, 50))], axis=1)
    probs /= probs.sum(axis=1, keepdims=True)
    pred = rng.integers(1, 51, n)          # 1..50 as the dump stores them
    subj = rng.integers(1, 151, n)         # 1..150
    obj = rng.integers(1, 151, n)
    for eff in ("none", "TDE"):
        np.savez_compressed(
            d / f"motifs_{eff}_predcls.npz",
            image_index=np.repeat(np.arange(n // 4), 4).astype(np.int32),
            sbox=rng.random((n, 4)).astype(np.float32),
            obox=rng.random((n, 4)).astype(np.float32),
            img_wh=np.full((n, 2), 500.0, dtype=np.float32),
            subj=subj.astype(np.int32), obj=obj.astype(np.int32),
            pred=pred.astype(np.int32),
            probs=probs.astype(np.float32), n_missing_pairs=0)
    return d, pred, subj, obj


def test_loader_drops_background_and_reindexes(tmp_path, fixture_dir):
    d, pred, subj, obj = fixture_dir
    mod = _load_driver(tmp_path, d)
    got = mod.load("none")

    assert got["q"].shape[1] == 50, "background column must be dropped"
    assert np.allclose(got["q"].sum(axis=1), 1.0), "rows must renormalize"
    # labels and classes must land in 0-based ranges the estimator expects
    assert np.array_equal(got["y"], pred - 1)
    assert got["y"].min() >= 0 and got["y"].max() <= 49
    assert np.array_equal(got["subj"], subj - 1)
    assert got["subj"].max() <= 149 and got["obj"].max() <= 149


def test_audit_cell_is_the_ordered_class_pair(tmp_path, fixture_dir):
    d, _pred, subj, obj = fixture_dir
    mod = _load_driver(tmp_path, d)
    got = mod.load("none")
    phi = got["subj"] * mod.N_OBJ + got["obj"]
    # the cell must separate (a,b) from (b,a): the estimand is order-sensitive
    same = (got["subj"] == got["obj"])
    if (~same).any():
        i = int(np.flatnonzero(~same)[0])
        swapped = got["obj"][i] * mod.N_OBJ + got["subj"][i]
        assert phi[i] != swapped


def test_temperature_fit_recovers_a_known_scaling(tmp_path, fixture_dir):
    d, _p, _s, _o = fixture_dir
    mod = _load_driver(tmp_path, d)
    rng = np.random.default_rng(1)
    n, k = 4000, 10
    logits = rng.normal(size=(n, k)) * 2.0
    p = np.exp(logits) / np.exp(logits).sum(1, keepdims=True)
    y = np.array([rng.choice(k, p=row) for row in p])
    # sharpen by a known factor; the fitted temperature should undo it
    sharp = mod.temp_scale(p, 0.5)
    t = mod.fit_temperature(sharp, y)
    assert 1.6 < t < 2.5, f"expected ~2.0 to undo the 0.5 sharpening, got {t}"
