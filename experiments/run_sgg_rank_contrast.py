"""Calibration-free case-level contrast for the SGG checkpoints (REV-3).

Within every subject-object cell, does a model rank the relations labelled y
above those labelled z on log q(y) - log q(z)? The comparison-weighted AUC is
unchanged by temperature and by any per-cell prior shift (wager/rank.py), so a
difference between two models is case-level discrimination with calibration
and every group-level adjustment held out by construction. Intervals: image
cluster bootstrap.

Run: python experiments/run_sgg_rank_contrast.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.rank import within_cell_auc_contrast  # noqa: E402
from sgg_variants import load_variant  # noqa: E402

DDIR = ROOT / "data/vg_motifs/wager_sgg"
OUT = ROOT / "results/sgg_rank_contrast.json"
N_OBJ = 151
N_BOOT = 200
COMPARISONS = [("TDE", "none"), ("la1", "none"), ("la0.5", "none"),
               ("TDE", "la1"), ("TDE", "ctx"), ("vis_ctx", "none"),
               ("ctx", "none"), ("vis", "none")]
# the released IETrans checkpoint, when its rerun is present (REV-2)
IETRANS = [("ietrans", "none"), ("ietrans", "la1"), ("ietrans", "TDE"),
           ("ietrans", "ietrans_ctx")]
if (ROOT / "data/vg_motifs/wager_ietrans/variant_ietrans.npz").exists():
    COMPARISONS += IETRANS


def main():
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    y = meta["pred"][keep].astype(np.int64)
    phi = (meta["subj"][keep].astype(np.int64) * N_OBJ
           + meta["obj"][keep].astype(np.int64))
    image = meta["image_index"][keep]
    cache = {}

    def q(v):
        if v not in cache:
            cache[v] = load_variant(v)["probs"][keep].astype(np.float64)
        return cache[v]

    rows = []
    for new, old in COMPARISONS:
        r = within_cell_auc_contrast(q(new), q(old), y, phi, image, n_boot=N_BOOT)
        rows.append({"new": new, "old": old, "auc_new": r.auc_new,
                     "auc_old": r.auc_old, "difference": r.difference,
                     "ci": list(r.ci), "ci_new": list(r.ci_new),
                     "ci_old": list(r.ci_old), "n_blocks": r.n_blocks,
                     "n_boot": r.n_boot})
        print(f"{new:>8s} vs {old:<5s} AUC {r.auc_new:.4f} vs {r.auc_old:.4f}  "
              f"diff {r.difference:+.4f} [{r.ci[0]:+.4f}, {r.ci[1]:+.4f}]", flush=True)
    OUT.write_text(json.dumps({"n_relations": int(keep.sum()), "rows": rows}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
