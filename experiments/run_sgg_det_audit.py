"""The TDE audit beyond PredCls: SGCls and SGDet (R2-5).

Input: the inline-replay parts of colab_sgg_det_stage2.py, downloaded to
data/vg_motifs/wager_<proto>/parts/part_*.npz. This merges them into meta.npz and
variant_{none,TDE,la1}.npz (the layout of data/vg_motifs/wager_sgg), checks the
replayed official-style recall against the released numbers, and reports for TDE and
the logit-adjusted control against the baseline, and TDE against the control:

  - the mean-recall@50 split (graph constraint, micro-averaged over identified
    relations; grouping: the ground-truth subject-object class pair, as in PredCls);
  - the within-cell AUC under both weightings, on relations with a matched pair;
  - the temperature-matched quadratic split on relations with a matched pair.

In SGCls and SGDet the baseline and TDE share every object prediction (one pass, the
factual object branch), so a relation whose objects are mis-detected is a miss for
both under any predicate label and contributes nothing to either part.

Run: python experiments/run_sgg_det_audit.py sgcls|sgdet
"""
from __future__ import annotations

import glob
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain, decompose_gain_matrix  # noqa: E402
from wager.rank import within_cell_auc_contrast  # noqa: E402
import run_sgg_audit_wager as AU  # noqa: E402

N_PRED, N_OBJ, K = 50, 151, 50
VARIANTS = ("none", "TDE", "la1")
RELEASED = {  # Scene-Graph-Benchmark.pytorch README, causal MOTIFS-SUM, this checkpoint
    "sgcls": {"none": {"R@50": 0.3925, "mR@50": 0.0802}, "TDE": {"R@50": 0.2631, "mR@50": 0.1321}},
    "sgdet": {"none": {"R@50": 0.3245, "mR@50": 0.0583}, "TDE": {"R@50": 0.1656, "mR@50": 0.0894}},
}


def merge(proto):
    d = ROOT / f"data/vg_motifs/wager_{proto}"
    parts = sorted(glob.glob(str(d / "parts/part_*.npz")))
    if not parts:
        raise SystemExit(f"no parts under {d}/parts")
    Z = [np.load(p) for p in parts]
    order = np.argsort([int(z["image_index"][0]) for z in Z])
    Z = [Z[i] for i in order]
    img = np.concatenate([z["image_index"] for z in Z])
    assert np.all(np.diff(img) >= 0), "parts overlap or are out of order"
    meta = {k: np.concatenate([z[k] for z in Z])
            for k in ("image_index", "sbox", "obox", "img_wh", "subj", "obj", "pred", "matched")}
    np.savez_compressed(d / "meta.npz", **meta)
    for v in VARIANTS:
        np.savez_compressed(d / f"variant_{v}.npz",
                            probs=np.concatenate([z[f"{v}_probs"] for z in Z]),
                            gc_rank=np.concatenate([z[f"{v}_gc"] for z in Z]),
                            ng_rank=np.concatenate([z[f"{v}_ng"] for z in Z]))
    return d, len(np.unique(img))


def official_recall(own_hit, y, image):
    _, inv = np.unique(image, return_inverse=True)
    r = float((np.bincount(inv, own_hit) / np.bincount(inv)).mean())
    cell = inv * (N_PRED + 1) + y
    size = (inv.max() + 1) * (N_PRED + 1)
    ch = np.bincount(cell, own_hit.astype(float), minlength=size).reshape(-1, N_PRED + 1)
    cn = np.bincount(cell, minlength=size).reshape(-1, N_PRED + 1)
    per = [float((ch[cn[:, q] > 0, q] / cn[cn[:, q] > 0, q]).mean()) if (cn[:, q] > 0).any() else 0.0
           for q in range(1, N_PRED + 1)]
    return r, float(np.mean(per))


def mr_split(hn, ho, y, phi, image):
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    elig = cnt[inv] >= 2
    n_y = np.bincount(y[elig], minlength=N_PRED + 1).astype(float)
    w = np.zeros(N_PRED + 1)
    w[1:] = np.where(n_y[1:] > 0, 1.0 / (N_PRED * np.maximum(n_y[1:], 1)), 0.0)
    h = elig.sum() * w[None, :] * (hn.astype(float) - ho.astype(float))
    g = decompose_gain_matrix(h, y, phi, groups=image, score="hit")
    return {"total": g.total_gain, "group": g.prior_gain, "case": g.alignment_gain,
            "case_ci": list(g.alignment_ci), "share_group": g.prior_gain / g.total_gain}


def main(proto):
    d, n_img = merge(proto)
    meta = np.load(d / "meta.npz")
    V = {v: np.load(d / f"variant_{v}.npz") for v in VARIANTS}
    y = meta["pred"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    phi = meta["subj"].astype(np.int64) * N_OBJ + meta["obj"].astype(np.int64)
    matched = meta["matched"].astype(bool)
    ix = np.arange(len(y))
    out = {"protocol": proto, "n_images": n_img, "n_relations": int(len(y)),
           "matched_fraction": float(matched.mean()), "recall": {}, "released": RELEASED[proto]}
    for v in VARIANTS:
        r, mr = official_recall((V[v]["gc_rank"][ix, y] < K).astype(float), y, image)
        out["recall"][v] = {"R@50": r, "mR@50": mr}
    print(proto, "recall", {v: {k: round(x, 4) for k, x in r.items()} for v, r in out["recall"].items()},
          "released", RELEASED[proto], flush=True)

    hit = {v: V[v]["gc_rank"] < K for v in VARIANTS}
    out["mR_split"] = {f"{a} vs {b}": mr_split(hit[a], hit[b], y, phi, image)
                       for a, b in (("TDE", "none"), ("la1", "none"), ("TDE", "la1"))}
    for k, r in out["mR_split"].items():
        print(f"  mR@50 {k}: {r['total']:+.4f} = {r['group']:+.4f} + {r['case']:+.4f} "
              f"[{r['case_ci'][0]:+.4f},{r['case_ci'][1]:+.4f}]  share {r['share_group']:.3f}", flush=True)

    m = matched
    Q = {v: V[v]["probs"][m][:, 1:].astype(np.float64) for v in VARIANTS}
    Q = {v: q / q.sum(1, keepdims=True) for v, q in Q.items()}
    ym, phim, imgm = y[m] - 1, phi[m], image[m]
    out["auc"] = {}
    for a, b in (("TDE", "none"), ("la1", "none"), ("TDE", "la1")):
        out["auc"][f"{a} vs {b}"] = {}
        for wt in ("comparison", "relation"):
            r = within_cell_auc_contrast(Q[a], Q[b], ym, phim, imgm, n_boot=200, weighting=wt)
            out["auc"][f"{a} vs {b}"][wt] = {"difference": r.difference, "ci": list(r.ci),
                                            "auc_new": r.auc_new, "auc_old": r.auc_old}
        print(f"  AUC {a} vs {b}: " + "  ".join(
            f"{wt} {x['difference']:+.4f} [{x['ci'][0]:+.4f},{x['ci'][1]:+.4f}]"
            for wt, x in out["auc"][f"{a} vs {b}"].items()), flush=True)

    rng = np.random.default_rng(20260811)
    imgs = np.unique(imgm)
    cal = np.isin(imgm, imgs[rng.permutation(len(imgs))[: len(imgs) // 2]])
    T = {v: AU.fit_temperature(Q[v][cal], ym[cal]) for v in VARIANTS}
    M = {v: AU.temp_scale(Q[v], T[v])[~cal] for v in VARIANTS}
    out["temperatures"] = T
    out["matched_split"] = {}
    for a, b in (("TDE", "none"), ("la1", "none"), ("TDE", "la1")):
        g = decompose_gain(M[a], M[b], ym[~cal], phim[~cal], groups=imgm[~cal], score="brier")
        out["matched_split"][f"{a} vs {b}"] = {"total": g.total_gain, "group": g.prior_gain,
                                               "case": g.alignment_gain,
                                               "case_ci": list(g.alignment_ci)}
        print(f"  matched quad {a} vs {b}: case {g.alignment_gain:+.5f} "
              f"[{g.alignment_ci[0]:+.5f},{g.alignment_ci[1]:+.5f}]", flush=True)
    (ROOT / f"results/sgg_{proto}_audit.json").write_text(json.dumps(out, indent=1))
    print(f"wrote results/sgg_{proto}_audit.json")


if __name__ == "__main__":
    main(sys.argv[1])
