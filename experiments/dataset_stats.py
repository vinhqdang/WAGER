"""Compute Visual Genome PredCls dataset statistics and a head/body/tail
stratified reasoning analysis for the WAGER manuscript.

Outputs:
  results/dataset_stats.json   -- corpus statistics for the dataset table
  results/stratified.json      -- per-tier mean reasoning score per model
"""
from __future__ import annotations

import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "vg", "vg_predcls.npz")
RES = os.path.join(ROOT, "results")

MODELS = ["FREQ", "FREQ+OVERLAP", "MLP-CLASS", "MLP-SPATIAL", "MLP-SPATIAL+"]


def dataset_stats():
    d = np.load(DATA, allow_pickle=True)
    subj, obj, pred = d["subj"], d["obj"], d["pred"]
    image, is_train = d["image"], d["is_train"]
    K = int(d["n_pred"]); n_obj = int(d["n_obj"])
    N = len(pred)
    tr = is_train; te = ~is_train

    phi = subj.astype(np.int64) * n_obj + obj
    cells, ccnt = np.unique(phi[tr], return_counts=True)

    def img_rel_stats(mask):
        imgs, c = np.unique(image[mask], return_counts=True)
        return int(len(imgs)), float(c.mean()), int(np.median(c))

    n_img_tr, rel_per_tr, med_tr = img_rel_stats(tr)
    n_img_te, rel_per_te, med_te = img_rel_stats(te)

    counts = np.bincount(pred, minlength=K).astype(float)
    order = np.argsort(counts)[::-1]
    cs = counts[order]
    frac = cs / cs.sum()
    head = max(1, K // 10); body = max(2, K // 3)
    tiers = {
        "head": (0, head), "body": (head, body), "tail": (body, K),
    }
    tier_share = {t: float(frac[a:b].sum()) for t, (a, b) in tiers.items()}
    tier_npred = {t: int(b - a) for t, (a, b) in tiers.items()}

    stats = {
        "n_relations_total": int(N),
        "n_relations_train": int(tr.sum()),
        "n_relations_test": int(te.sum()),
        "n_images_train": n_img_tr,
        "n_images_test": n_img_te,
        "rel_per_image_train": round(rel_per_tr, 2),
        "rel_per_image_test": round(rel_per_te, 2),
        "median_rel_per_image_test": med_te,
        "n_predicates": K,
        "n_object_classes": n_obj,
        "n_phi_cells_possible": n_obj * n_obj,
        "n_phi_cells_observed_train": int(len(cells)),
        "phi_cell_occupancy_pct": round(100 * len(cells) / (n_obj * n_obj), 2),
        "phi_cells_sparse_lt5_pct": round(100 * float(np.mean(ccnt < 5)), 2),
        "top5_predicate_share_pct": round(100 * float(frac[:5].sum()), 1),
        "top1_predicate": str(d["pred_vocab"][order[0]]),
        "top1_predicate_share_pct": round(100 * float(frac[0]), 1),
        "tier_share_pct": {t: round(100 * v, 1) for t, v in tier_share.items()},
        "tier_npredicates": tier_npred,
    }
    with open(os.path.join(RES, "dataset_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    print(json.dumps(stats, indent=2))
    return stats, order, tiers


def stratified(order, tiers):
    """Per-tier mean reasoning score d_i for each model on the eval stream."""
    fd = np.load(os.path.join(RES, "sgg_figdata.npz"), allow_pickle=True)
    y = fd["y"]
    # rank of each predicate by global frequency
    rank = np.empty(len(order), dtype=int)
    rank[order] = np.arange(len(order))
    yr = rank[y]
    tier_of = np.full(len(y), "tail", dtype=object)
    for t, (a, b) in tiers.items():
        tier_of[(yr >= a) & (yr < b)] = t

    out = {"tiers": list(tiers.keys()), "models": {}}
    for m in MODELS:
        dd = fd[f"d_{m}"]
        row = {}
        for t in tiers:
            mask = tier_of == t
            row[t] = {
                "mean_d": float(dd[mask].mean()),
                "n": int(mask.sum()),
                "frac_positive": float(np.mean(dd[mask] > 0)),
            }
        out["models"][m] = row
    with open(os.path.join(RES, "stratified.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nStratified mean d_i (reasoning) by predicate tier:")
    for m in MODELS:
        r = out["models"][m]
        print(f"  {m:14s} head={r['head']['mean_d']:+.4f} "
              f"body={r['body']['mean_d']:+.4f} tail={r['tail']['mean_d']:+.4f}")
    return out


if __name__ == "__main__":
    stats, order, tiers = dataset_stats()
    stratified(order, tiers)
