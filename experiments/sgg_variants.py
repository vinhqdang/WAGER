"""Locate a re-scored SGG model's per-relation outputs, across checkpoints.

Each Colab rerun writes one directory under data/vg_motifs/ (wager_sgg for the
causal MOTIFS checkpoint, wager_ietrans for IETrans) holding meta.npz and one
variant_<name>.npz per model. Variant names are unique across directories, so a
comparison can pair models from different checkpoints -- but only if both runs
scored the same relations in the same order, which load_variant enforces against
the reference run's meta.
"""
from __future__ import annotations

import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
MDIR = ROOT / "data/vg_motifs"
REFERENCE = MDIR / "wager_sgg"
RUNS = (REFERENCE, MDIR / "wager_ietrans")
ALIGN_KEYS = ("image_index", "pred", "subj", "obj", "sbox", "obox")
_checked: set[pathlib.Path] = set()


def run_of(variant: str) -> pathlib.Path:
    hits = [d for d in RUNS if (d / f"variant_{variant}.npz").exists()]
    if len(hits) != 1:
        raise FileNotFoundError(f"variant {variant!r} found in {len(hits)} runs: {hits}")
    return hits[0]


def check_alignment(run: pathlib.Path) -> None:
    """Every run must list exactly the reference run's relations, in its order."""
    if run in _checked or run == REFERENCE:
        return
    ref, other = np.load(REFERENCE / "meta.npz"), np.load(run / "meta.npz")
    for k in ALIGN_KEYS:
        if not np.array_equal(ref[k], other[k]):
            raise ValueError(f"{run.name} is not aligned with {REFERENCE.name} on {k}")
    _checked.add(run)


def load_variant(variant: str) -> np.lib.npyio.NpzFile:
    run = run_of(variant)
    check_alignment(run)
    return np.load(run / f"variant_{variant}.npz")
