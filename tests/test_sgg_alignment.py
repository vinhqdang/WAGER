"""Validate the SGG dump aligner against synthetic dumps built from real rows.

The aligner has to match evaluation-dump images to the repository's canonical
VG150 test rows without a shared image identifier: the two pipelines filter and
order the test split differently, boxes arrive in a resized frame, and classes
and predicates are 1-indexed with a background column. This test constructs a
dump with exactly those distortions from real rows whose correct answer is
known, so a regression in the matching logic fails here rather than silently
producing a misaligned audit.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
VG = ROOT / "data/vg/vg_predcls.npz"

pytestmark = pytest.mark.skipif(not VG.exists(), reason="VG cache not present")


def _build_synthetic(tmp: pathlib.Path, n_images: int = 40, drop: int = 3,
                     seed: int = 0):
    """Make dump npzs + image_data.json from real rows, applying the distortions
    the real pipeline introduces. Returns the ground-truth row indices used."""
    raw = np.load(VG)
    te = np.flatnonzero(~raw["is_train"])
    image = raw["image"][te]
    uniq = np.unique(image)
    rng = np.random.default_rng(seed)
    chosen = rng.choice(uniq, size=n_images, replace=False)
    chosen = chosen[drop:]                     # dump covers fewer images than we hold

    order = rng.permutation(len(chosen))       # dump image order differs from ours
    rows_img, rows_sb, rows_ob, rows_wh = [], [], [], []
    rows_sc, rows_oc, rows_y, truth = [], [], [], []
    sizes = {}
    for new_idx, k in enumerate(order):
        img_id = int(chosen[k])
        sel = np.flatnonzero(image == img_id)
        w, h = 800.0 + (img_id % 97), 600.0 + (img_id % 61)
        sizes[img_id] = (w, h)
        scale = 1000.0 / max(w, h)             # dump boxes live in a resized frame
        for r in sel:
            gi = te[r]
            sb, ob = raw["sbox"][gi], raw["obox"][gi]
            rows_img.append(new_idx)
            # ours is xywh in original frame; dump is xyxy in resized frame
            rows_sb.append([sb[0] * scale, sb[1] * scale,
                            (sb[0] + sb[2]) * scale, (sb[1] + sb[3]) * scale])
            rows_ob.append([ob[0] * scale, ob[1] * scale,
                            (ob[0] + ob[2]) * scale, (ob[1] + ob[3]) * scale])
            rows_wh.append((w * scale, h * scale))
            rows_sc.append(int(raw["subj"][gi]) + 1)     # dumps are 1-indexed
            rows_oc.append(int(raw["obj"][gi]) + 1)
            rows_y.append(int(raw["pred"][gi]) + 1)
            truth.append(int(r))
    n = len(truth)
    probs = rng.random((n, 51)) + 0.01          # 51 = background + 50 predicates
    probs /= probs.sum(axis=1, keepdims=True)

    dest = tmp / "data/vg_motifs"
    dest.mkdir(parents=True, exist_ok=True)
    for eff in ("none", "TDE"):
        p = rng.random((n, 51)) + 0.01 if eff == "TDE" else probs
        p = p / p.sum(axis=1, keepdims=True)
        np.savez_compressed(
            dest / f"motifs_{eff}_predcls.npz",
            image_index=np.asarray(rows_img, dtype=np.int32),
            sbox=np.asarray(rows_sb, dtype=np.float32),
            obox=np.asarray(rows_ob, dtype=np.float32),
            img_wh=np.asarray(rows_wh, dtype=np.float32),
            subj=np.asarray(rows_sc, dtype=np.int32),
            obj=np.asarray(rows_oc, dtype=np.int32),
            pred=np.asarray(rows_y, dtype=np.int32),
            probs=p.astype(np.float32), n_missing_pairs=0)
    (dest / "image_data.json").write_text(json.dumps(
        [{"image_id": i, "width": w, "height": h} for i, (w, h) in sizes.items()]))
    return np.asarray(truth)


def test_aligner_recovers_known_rows(tmp_path):
    truth = _build_synthetic(tmp_path)
    # run the driver against a tree whose data/vg_motifs is synthetic
    link = tmp_path / "data/vg"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.mkdir(exist_ok=True)
    (link / "vg_predcls.npz").symlink_to(VG)
    (tmp_path / "results").mkdir(exist_ok=True)

    src = (ROOT / "experiments/run_sgg_audit_wager.py").read_text()
    src = src.replace('ROOT = pathlib.Path(__file__).resolve().parents[1]',
                      f'ROOT = pathlib.Path({str(tmp_path)!r})')
    src = src.replace("sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))",
                      f"sys.path.insert(0, {str(ROOT)!r})")
    src = src.replace("N_RANDOMIZATIONS = 999", "N_RANDOMIZATIONS = 9")
    runner = tmp_path / "run_align.py"
    runner.write_text(src)

    r = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True)
    assert r.returncode == 0, f"aligner failed:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}"

    out = json.loads((tmp_path / "results/sgg_audit_motifs.json").read_text())
    # every dump relation should have been matched to one of our rows
    assert out["aligned_relations"] == len(truth), (
        f"aligned {out['aligned_relations']} of {len(truth)} dump relations")
    assert out["images_unmatched"] == 0
    # and the decomposition must satisfy the exact identity
    d = out["decomposition"]
    assert abs(d["total"] - (d["prior"] + d["reasoning"])) < 1e-9
