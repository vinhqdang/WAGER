"""Audit a zero-shot CLIP predicate scorer on the canonical VG150 PredCls relations.

Frozen CLIP ViT-B/32 scores the union crop of each test relation against one prompt
per predicate ("a photo of a {subject} {predicate} a {object}";
colab_clip_zeroshot.py). It never saw a Visual Genome label, so it has no
predicate prior: whatever it knows within an object pair comes from pretraining.

Against the MOTIFS frequency branch (FREQ, constant within every subject-object
cell), a model's case-level part is its own within-cell information, so the
comparisons ask: how much within-cell information does a zero-shot model carry
next to the trained MOTIFS baseline, and what does adding the training prior to it
buy? "CLIP0+FREQ" multiplies the zero-shot distribution by the frequency branch's
and renormalises; within a cell that adds the same log-odds to every relation, so
its within-cell AUC equals the zero-shot model's.

Temperature-matched on the audit's calibration half (seed 20260811), split on the
other half under the quadratic and log scores; within-cell AUC on all identified
relations with an image bootstrap.

Run: python experiments/run_clip_zeroshot_audit.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain  # noqa: E402
from wager.rank import within_cell_auc, within_cell_auc_contrast  # noqa: E402
import run_sgg_audit_wager as AU  # noqa: E402

DDIR = ROOT / "data/vg_motifs/wager_sgg"
OUT = ROOT / "results/clip_zeroshot_audit.json"


def probs(v, keep):
    q = np.load(DDIR / f"variant_{v}.npz")["probs"][keep][:, 1:].astype(np.float64)
    return q / q.sum(1, keepdims=True)


def main():
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    y = meta["pred"].astype(np.int64)[keep] - 1
    phi = (meta["subj"].astype(np.int64) * 151 + meta["obj"].astype(np.int64))[keep]
    image = meta["image_index"].astype(np.int64)[keep]

    Q = {"CLIP0": probs("clip_zs", keep), "FREQ": probs("frq", keep),
         "MOTIFS": probs("none", keep), "TDE": probs("TDE", keep)}
    comb = np.log(np.clip(Q["CLIP0"], 1e-12, None)) + np.log(np.clip(Q["FREQ"], 1e-12, None))
    comb = np.exp(comb - comb.max(1, keepdims=True))
    Q["CLIP0+FREQ"] = comb / comb.sum(1, keepdims=True)
    acc = {k: float((q.argmax(1) == y).mean()) for k, q in Q.items()}

    rng = np.random.default_rng(20260811)               # the audit's calibration split
    imgs = np.unique(image)
    cal_imgs = set(imgs[rng.permutation(len(imgs))[: len(imgs) // 2]].tolist())
    cal = np.array([i in cal_imgs for i in image])
    aud = ~cal
    T = {k: AU.fit_temperature(q[cal], y[cal]) for k, q in Q.items()}
    M = {k: AU.temp_scale(q, T[k])[aud] for k, q in Q.items()}

    pairs = [("CLIP0", "FREQ"), ("MOTIFS", "FREQ"), ("CLIP0", "MOTIFS"),
             ("CLIP0+FREQ", "FREQ"), ("CLIP0+FREQ", "MOTIFS"), ("TDE", "FREQ")]
    rows = []
    for new, old in pairs:
        row = {"new": new, "old": old}
        for sc in ("brier", "log"):
            with np.errstate(all="ignore"):
                g = decompose_gain(M[new], M[old], y[aud], phi[aud], groups=image[aud], score=sc)
            row[sc] = {"total": g.total_gain, "group": g.prior_gain, "case": g.alignment_gain,
                       "case_ci": list(g.alignment_ci)}
        rows.append(row)
        b, l_ = row["brier"], row["log"]
        print(f"{new:11s} vs {old:7s} quad T {b['total']:+.5f} P {b['group']:+.5f} R {b['case']:+.5f} "
              f"[{b['case_ci'][0]:+.5f},{b['case_ci'][1]:+.5f}] | log R {l_['case']:+.5f} "
              f"[{l_['case_ci'][0]:+.5f},{l_['case_ci'][1]:+.5f}]", flush=True)

    auc = {k: within_cell_auc(Q[k], y, phi) for k in ("CLIP0", "MOTIFS", "TDE", "FREQ")}
    a = within_cell_auc_contrast(Q["CLIP0"], Q["MOTIFS"], y, phi, image, n_boot=200)
    auc_diff = {"difference": a.difference, "ci": list(a.ci), "ci_new": list(a.ci_new),
                "ci_old": list(a.ci_old)}
    print("AUC", {k: round(v, 4) for k, v in auc.items()},
          f"CLIP0 - MOTIFS {a.difference:+.4f} [{a.ci[0]:+.4f},{a.ci[1]:+.4f}]")
    print("accuracy", {k: round(v, 4) for k, v in acc.items()}, "T", {k: round(v, 3) for k, v in T.items()})
    OUT.write_text(json.dumps({"accuracy": acc, "temperatures": T, "rows": rows, "auc": auc,
                               "auc_clip0_minus_motifs": auc_diff,
                               "n_relations": int(keep.sum())}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
