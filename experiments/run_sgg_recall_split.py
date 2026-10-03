"""Split the mean-recall change between two SGG checkpoints into group-level and
case-level parts.

Mean recall over predicates is a label-weighted hit rate. Written per relation,
the micro-averaged version is

    mR@K = sum_i w(y_i) hit_i(y_i),     w(y) = 1 / (#predicates * n_y),

where hit_i(y) says whether relation i would be recalled at K if its label were
y (from the exact first-hit ranks written by colab_sgg_rank.py). The contrast
h_i(y) = N w(y) [hit_new_i(y) - hit_old_i(y)] is then split by the same
within-cell label transport as the proper-score audit: relation i is scored
against the labels of the other relations whose subject and object share its
classes. Transport preserves each cell's label counts, hence every n_y, so the
transported part is the mean-recall change that survives when labels are
shuffled within subject-object class pairs (group-level), and the remainder is
the within-cell covariance between hit gains and labels (case-level).

The official metric averages recall per image before averaging over images; the
micro version pools relations. Both are reported so the gap is visible.

Run: python experiments/run_sgg_recall_split.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wager.antisymmetric import decompose_gain_matrix  # noqa: E402

DDIR = ROOT / "data/vg_motifs/wager_sgg"
RESULTS = ROOT / "results"
N_PRED = 50
N_OBJ = 151
KS = (20, 50, 100)
ALPHA = 0.05
# head / body / tail by training instances (>10,000 / 500-10,000 / <500)
HEAD_MIN, TAIL_MAX = 10_000, 500


def load(variant):
    z = np.load(DDIR / f"variant_{variant}.npz")
    return {"gc": z["gc_rank"], "ng": z["ng_rank"], "probs": z["probs"]}


def tiers(train_counts):
    c = np.asarray(train_counts)
    t = np.full(N_PRED + 1, "", dtype=object)
    for q in range(1, N_PRED + 1):
        t[q] = "head" if c[q] > HEAD_MIN else ("tail" if c[q] < TAIL_MAX else "body")
    return t


def micro_mean_recall(hit_own, y, mask):
    per = []
    for q in range(1, N_PRED + 1):
        m = mask & (y == q)
        per.append(hit_own[m].mean() if m.any() else 0.0)
    return float(np.mean(per)), np.asarray(per)


def official_mean_recall(hit_own, y, image):
    """Per image and predicate, then over images, then over predicates."""
    _, inv = np.unique(image, return_inverse=True)
    cell = inv * (N_PRED + 1) + y
    size = (inv.max() + 1) * (N_PRED + 1)
    ch = np.bincount(cell, hit_own.astype(float), minlength=size).reshape(-1, N_PRED + 1)
    cn = np.bincount(cell, minlength=size).reshape(-1, N_PRED + 1)
    per = []
    for q in range(1, N_PRED + 1):
        m = cn[:, q] > 0
        per.append(float((ch[m, q] / cn[m, q]).mean()) if m.any() else 0.0)
    return float(np.mean(per)), per


def split(hit_new, hit_old, y, phi, image, eligible, col_weight):
    """Decompose sum_i col_weight[y_i] * (hit change) over eligible relations."""
    n_e = int(eligible.sum())
    h = n_e * col_weight[None, :] * (hit_new.astype(float) - hit_old.astype(float))
    g = decompose_gain_matrix(h, y, phi, groups=image, alpha=ALPHA, score="hit")
    return {"total": g.total_gain, "group": g.prior_gain, "case": g.alignment_gain,
            "case_ci": list(g.alignment_ci), "group_ci": list(g.prior_ci),
            "total_ci": list(g.total_ci)}


def main(new="TDE", old="none"):
    meta = np.load(DDIR / "meta.npz")
    summary = json.loads((DDIR / "summary.json").read_text())
    y = meta["pred"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    phi = meta["subj"].astype(np.int64) * N_OBJ + meta["obj"].astype(np.int64)
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    eligible = cnt[inv] >= 2
    tier = tiers(summary["train_predicate_counts"])
    a, b = load(new), load(old)
    ix = np.arange(len(y))
    n_y = np.bincount(y[eligible], minlength=N_PRED + 1).astype(float)

    out = {"comparison": f"{new} vs {old}", "n_relations": int(len(y)),
           "n_eligible": int(eligible.sum()), "coverage": float(eligible.mean()),
           "n_cells": int((cnt >= 2).sum()),
           "tiers": {t: [int(q) for q in range(1, N_PRED + 1) if tier[q] == t]
                     for t in ("head", "body", "tail")},
           "results": {}}
    for mode in ("gc", "ng"):
        for K in KS:
            hn, ho = a[mode] < K, b[mode] < K
            res = {}
            for name, hh in ((new, hn), (old, ho)):
                own = hh[ix, y]
                res[f"official_mR_{name}"], res[f"official_per_predicate_{name}"] = \
                    official_mean_recall(own, y, image)
                res[f"micro_mR_{name}"] = micro_mean_recall(own, y, np.ones_like(eligible))[0]
                res[f"micro_mR_eligible_{name}"], per = micro_mean_recall(own, y, eligible)
                res[f"per_predicate_recall_{name}"] = per.tolist()
                res[f"micro_R_{name}"] = float(own.mean())
            w = np.zeros(N_PRED + 1)
            w[1:] = np.where(n_y[1:] > 0, 1.0 / (N_PRED * np.maximum(n_y[1:], 1)), 0.0)
            res["mean_recall"] = split(hn, ho, y, phi, image, eligible, w)
            res["recall"] = split(hn, ho, y, phi, image, eligible,
                                  np.r_[0.0, np.full(N_PRED, 1.0 / eligible.sum())])
            for t in ("head", "body", "tail"):
                wt = np.where(np.asarray([tier[q] == t for q in range(N_PRED + 1)]), w, 0.0)
                res[f"mean_recall_{t}"] = split(hn, ho, y, phi, image, eligible, wt)
            per_pred = []
            for q in range(1, N_PRED + 1):
                wq = np.zeros(N_PRED + 1)
                wq[q] = N_PRED * w[q]          # this predicate's recall change
                if n_y[q] == 0:
                    per_pred.append(None)
                    continue
                per_pred.append(split(hn, ho, y, phi, image, eligible, wq))
            res["per_predicate"] = per_pred
            out["results"][f"{mode}@{K}"] = res
            m = res["mean_recall"]
            print(f"{mode}-mR@{K}: official {res[f'official_mR_{old}']:.4f} -> "
                  f"{res[f'official_mR_{new}']:.4f} | micro(eligible) "
                  f"{res[f'micro_mR_eligible_{old}']:.4f} -> "
                  f"{res[f'micro_mR_eligible_{new}']:.4f} | change {m['total']:+.4f} = "
                  f"group {m['group']:+.4f} + case {m['case']:+.4f} "
                  f"[{m['case_ci'][0]:+.4f}, {m['case_ci'][1]:+.4f}]")
            for t in ("head", "body", "tail"):
                mt = res[f"mean_recall_{t}"]
                print(f"    {t:4s}: {mt['total']:+.4f} = group {mt['group']:+.4f} "
                      f"+ case {mt['case']:+.4f} [{mt['case_ci'][0]:+.4f}, "
                      f"{mt['case_ci'][1]:+.4f}]")
    dest = RESULTS / ("sgg_recall_split.json" if (new, old) == ("TDE", "none")
                      else f"sgg_recall_split_{new}_vs_{old}.json")
    dest.write_text(json.dumps(out, indent=1))
    print(f"wrote {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
