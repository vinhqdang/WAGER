"""Headroom reference for the split (review item): the baseline-to-oracle gain.

An oracle puts all its mass on each relation's own predicate. Its quadratic-score gain over
the MOTIFS baseline on the audited PredCls relations splits into a group-level and a
case-level part like any other model's, so it shows how much of a gain there is to find at
the case level and that the split can return a case-level reading when there is one.

Run: python experiments/sgg_oracle_headroom.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wager.antisymmetric import decompose_gain  # noqa: E402

D = ROOT / "data/vg_motifs/wager_sgg"
OUT = ROOT / "results/sgg_oracle_headroom.json"


def main():
    m = np.load(D / "meta.npz")
    keep = np.ones(len(m["pred"]), bool)
    keep[json.loads((D / "missing_pairs.json").read_text())["rows"]] = False
    y = m["pred"].astype(int)[keep] - 1
    phi = (m["subj"].astype(np.int64) * 151 + m["obj"].astype(np.int64))[keep]
    img = m["image_index"].astype(int)[keep]

    def q(v):
        x = np.load(D / f"variant_{v}.npz")["probs"][keep][:, 1:].astype(float)
        return x / x.sum(1, keepdims=True)
    res = {}
    for name, new in (("oracle", np.eye(50)[y]), ("TDE", q("TDE"))):
        g = decompose_gain(new, q("none"), y, phi, groups=img, score="brier")
        res[name] = {"total": g.total_gain, "group": g.prior_gain, "case": g.alignment_gain,
                     "case_ci": list(g.alignment_ci)}
        print(name, {k: (round(v, 4) if not isinstance(v, list) else [round(x, 4) for x in v])
                     for k, v in res[name].items()})
    OUT.write_text(json.dumps(res, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
