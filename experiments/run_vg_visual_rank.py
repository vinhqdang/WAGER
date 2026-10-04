"""Calibration-free within-cell discrimination for the real-pixel study (REV-7).

Section 6 compares three models trained on the same relation subsample: class
embeddings only (MLP-CLASS-S), plus box geometry (MLP-SPATIAL-S), plus frozen
CLIP crops (MLP-VISUAL-S). The CLIP model carries more case-level covariance than
the geometry model yet ranks the correct predicate first less often, and the paper
left open which of the two describes recognition among relations sharing an
object pair. The within-cell AUC (wager/rank.py) is unchanged by temperature and by
any change constant within a cell, so it answers that without a calibration
protocol. The class-only model predicts the same distribution for every relation
in a cell, so its AUC is exactly one half: a built-in check.

Run: python experiments/run_vg_visual_rank.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wager.rank import within_cell_auc, within_cell_auc_contrast  # noqa: E402

DATA = ROOT / "data/vg_visual/vg_visual_models.npz"
OUT = ROOT / "results/vg_visual_rank.json"
PAIRS = [("MLP-VISUAL-S", "MLP-SPATIAL-S"), ("MLP-VISUAL-S", "MLP-CLASS-S"),
         ("MLP-SPATIAL-S", "MLP-CLASS-S")]


def main():
    d = np.load(DATA)
    y, phi, image = d["y"].astype(np.int64), d["phi"], d["image"]
    auc_class = within_cell_auc(d["MLP-CLASS-S"], y, phi)
    assert abs(auc_class - 0.5) < 1e-12, auc_class
    rows = []
    for new, old in PAIRS:
        r = within_cell_auc_contrast(d[new], d[old], y, phi, image, n_boot=200)
        rows.append({"new": new, "old": old, "auc_new": r.auc_new, "auc_old": r.auc_old,
                     "difference": r.difference, "ci": list(r.ci),
                     "ci_new": list(r.ci_new), "ci_old": list(r.ci_old),
                     "n_blocks": r.n_blocks, "n_boot": r.n_boot})
        print(f"{new} vs {old}: AUC {r.auc_new:.4f} vs {r.auc_old:.4f}  "
              f"diff {r.difference:+.4f} [{r.ci[0]:+.4f}, {r.ci[1]:+.4f}]")
    OUT.write_text(json.dumps({"n_relations": int(len(y)), "auc_class_only": auc_class,
                               "rows": rows}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
