"""How much does the headline share depend on the declared grouping? (review item R3-8)

The mean-recall@50 split of TDE against the baseline (graph constraint, micro-pooled,
run_sgg_recall_split.split) is recomputed with the cell declared differently:

  class pair            the paper's grouping (ordered subject, object classes);
  subject class         coarser: the object is not part of the cell;
  pair x position       finer: class pair split by where the object lies relative to the
                        subject (four quadrants of the centre offset);
  pair x subject size   finer: class pair split by the subject box's area tercile.

Cells with a single relation carry no within-cell comparison and drop out of each version,
as in the paper.

Run: python experiments/run_sgg_grouping_share.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import run_sgg_recall_split as RS  # noqa: E402

OUT = ROOT / "results/sgg_grouping_share.json"


def main():
    meta = np.load(RS.DDIR / "meta.npz")
    y = meta["pred"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    subj, obj = meta["subj"].astype(np.int64), meta["obj"].astype(np.int64)
    sb, ob = meta["sbox"].astype(np.float64), meta["obox"].astype(np.float64)
    cs = np.stack([(sb[:, 0] + sb[:, 2]) / 2, (sb[:, 1] + sb[:, 3]) / 2], 1)
    co = np.stack([(ob[:, 0] + ob[:, 2]) / 2, (ob[:, 1] + ob[:, 3]) / 2], 1)
    quad = (co[:, 0] > cs[:, 0]).astype(int) * 2 + (co[:, 1] > cs[:, 1]).astype(int)
    area = (sb[:, 2] - sb[:, 0]) * (sb[:, 3] - sb[:, 1])
    tert = np.digitize(area, np.quantile(area, [1 / 3, 2 / 3]))
    pair = subj * RS.N_OBJ + obj
    groupings = {"class pair (paper)": pair, "subject class": subj,
                 "class pair x position": pair * 4 + quad, "class pair x subject size": pair * 3 + tert}
    a, b = RS.load("TDE"), RS.load("none")
    ix = np.arange(len(y))
    hn, ho = a["gc"] < 50, b["gc"] < 50
    res = {}
    for name, phi in groupings.items():
        _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
        elig = cnt[inv] >= 2
        n_y = np.bincount(y[elig], minlength=RS.N_PRED + 1).astype(float)
        w = np.zeros(RS.N_PRED + 1)
        w[1:] = np.where(n_y[1:] > 0, 1.0 / (RS.N_PRED * np.maximum(n_y[1:], 1)), 0.0)
        r = RS.split(hn, ho, y, phi, image, elig, w)
        res[name] = {**r, "n_cells": int((cnt >= 2).sum()), "coverage": float(elig.mean())}
        print(f"{name:28s} cells {res[name]['n_cells']:6d} cov {res[name]['coverage']:.3f}  total {r['total']:+.4f} "
              f"group {r['group']:+.4f} case {r['case']:+.4f} [{r['case_ci'][0]:+.4f},{r['case_ci'][1]:+.4f}]  "
              f"share {100 * r['group'] / r['total']:.1f}%", flush=True)
    OUT.write_text(json.dumps(res, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
