"""How far can any model rank within a cell on VG150? (R2-13)

Two test relations with the same image and the same subject and object boxes but
different predicates receive the same prediction from every model that sees the
image and the boxes, so every within-cell comparison between them is a tie and
contributes one half to the within-cell AUC. Their share s of the comparison weight
bounds the AUC of any such model by 1 - s/2. Reported for both weightings.

Run: python experiments/sgg_auc_ceiling.py
"""
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
m = np.load(ROOT / "data/vg_motifs/wager_sgg/meta.npz")
drop = json.loads((ROOT / "data/vg_motifs/wager_sgg/missing_pairs.json").read_text())["rows"]
keep = np.ones(len(m["pred"]), bool)
keep[drop] = False
y = m["pred"].astype(np.int64)[keep]
phi = (m["subj"].astype(np.int64) * 151 + m["obj"].astype(np.int64))[keep]
pair = np.unique(np.column_stack([m["image_index"][keep], m["sbox"][keep], m["obox"][keep]]),
                 axis=0, return_inverse=True)[1].ravel()
_, cinv, ccnt = np.unique(phi, return_inverse=True, return_counts=True)


def comparisons(key):
    """Total weight of label-differing pairs within groups of `key`, per cell."""
    _, g = np.unique(np.column_stack([cinv, key]), axis=0, return_inverse=True)
    g = g.ravel()
    n_g = np.bincount(g)
    gy = np.unique(np.column_stack([g, y]), axis=0, return_counts=True)
    same = np.bincount(gy[0][:, 0], gy[1] ** 2, len(n_g))
    diff = (n_g ** 2 - same) / 2.0                      # unordered pairs with different labels
    cell_of_g = np.zeros(len(n_g), np.int64)
    cell_of_g[g] = cinv
    return np.bincount(cell_of_g, diff, len(ccnt))


tot = comparisons(np.zeros(len(y), np.int64))           # all label-differing pairs in a cell
tie = comparisons(pair)                                  # ... with the same image and boxes
out = {}
for wt, cw in (("comparison", np.ones(len(ccnt))), ("relation", 1.0 / np.maximum(ccnt, 1))):
    s = float((tie * cw).sum() / (tot * cw).sum())
    out[wt] = {"tie_share": s, "auc_ceiling": 1 - s / 2}
out["relations_on_box_pairs_with_more_than_one_relation"] = float(
    np.mean(np.bincount(pair)[pair] > 1))
(ROOT / "results/sgg_auc_ceiling.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
