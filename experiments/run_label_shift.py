"""A label-shifted Visual Genome test: does the split predict which gains survive? (REV-8)

Each relation is reweighted so that, inside its subject-object cell, every
predicate present carries equal total weight: w_i = 1 / (L_c * p_c(y_i)), with
L_c the number of distinct predicates in cell c and p_c the cell's empirical
frequencies. This is the shift a deployment with uniform within-pair predicate
frequencies would see; no prediction changes. The split is recomputed on the
shifted distribution with the same estimator, weighting both the observed
scores and the transported labels (the transported label of case i is drawn from
the other cases of its cell in proportion to their weights).

The prediction from Sec. 3: a group-level gain is a statement about the cell's
label frequencies and moves when they move; a case-level gain is a statement about
which case carries which label and should hold. Comparisons: TDE, the logit-
adjusted baseline and IETrans against the MOTIFS baseline (temperature-matched
as in Sec. 5), and on the real-pixel study the class-only model against the
training frequency table (FREQ), and geometry and CLIP against the class-only
model (temperature-matched as in Sec. 6, on that study's own temperature grid).

Intervals: delete-a-group jackknife over images (G = 100 random groups of test images),
normal around the full-sample estimate. An image bootstrap is biased here: a
resampled image's same-label pairs have kernel zero and get weight E[w^2] = 2, which
pulls the case-level part towards zero.

Besides the uniform mix (alpha = 1), the split is reported along the path of mixes with
weights w_i^alpha, alpha in {0, 0.25, 0.5, 0.75, 1}, which moves from the benchmark's
label mix to uniform within-cell frequencies, with the Kish effective sample size of
each mix.

Run: python experiments/run_label_shift.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import gain_matrix  # noqa: E402
from wager.rank import _auc, _blocks  # noqa: E402
from sgg_variants import load_variant  # noqa: E402
import run_sgg_audit_wager as AU  # noqa: E402

OUT = ROOT / "results/label_shift.json"
N_GROUPS = 100
ALPHAS = (0.0, 0.25, 0.5, 0.75, 1.0)


def shift_weights(y, phi):
    _, cinv = np.unique(phi, return_inverse=True)
    key = cinv.astype(np.int64) * (y.max() + 1) + y
    _, kinv, kcnt = np.unique(key, return_inverse=True, return_counts=True)
    cell_n = np.bincount(cinv)
    labels_in_cell = np.bincount(cinv, weights=1.0 / kcnt[kinv])   # distinct labels per cell
    return cell_n[cinv] / (labels_in_cell[cinv] * kcnt[kinv])        # 1 / (L_c p_c(y))


def weighted_split(h, y, phi, w, img_w=None):
    """Weighted split: pairs (i, j) of a cell are weighted by w_i w_j.

    R_c = sum_{i!=j} w_i w_j A_ij / sum_{i!=j} w_i w_j with the antisymmetric kernel
    A_ij, so a gain constant within a cell has R_c = 0 exactly for any weights, and
    unit weights give the paper's estimator. T_c is the weighted mean observed gain,
    P_c = T_c - R_c, and cells are combined with weight W_c = sum of their weights.
    """
    w = w if img_w is None else w * img_w
    _, cinv = np.unique(phi, return_inverse=True)
    n, k = h.shape
    nc = cinv.max() + 1
    obs = h[np.arange(n), y]
    W = np.bincount(cinv, w, nc)
    W2 = np.bincount(cinv, w * w, nc)
    cnt = np.bincount(cinv, minlength=nc)
    pair_w = W * W - W2
    ok = (cnt >= 2) & (W > 0) & (pair_w > 0)
    wl = np.zeros((nc, k))
    np.add.at(wl, (cinv, y), w)
    # sum_{i!=j} w_i w_j (h_i(y_i) - h_i(y_j)) = sum_i w_i (W_c h_i(y_i) - h_i . wl_c)
    r_i = w * (W[cinv] * obs - np.einsum("ik,ik->i", h, wl[cinv]))
    r_sum = np.bincount(cinv, r_i, nc)
    t_sum = np.bincount(cinv, w * obs, nc)
    W_tot = W[ok].sum()
    T = t_sum[ok].sum() / W_tot
    R = (W[ok] * r_sum[ok] / pair_w[ok]).sum() / W_tot
    return T, T - R, R


def jackknife(stat, image):
    """Delete-a-group jackknife over images: (point, standard errors) of stat(mask)."""
    imgs = np.unique(image)
    grp_of = np.random.default_rng(0).permutation(len(imgs)) % N_GROUPS
    grp = grp_of[np.searchsorted(imgs, image)]
    point = np.asarray(stat(np.ones(len(image), bool)))
    jk = np.asarray([stat(grp != g) for g in range(N_GROUPS)])
    se = np.sqrt((N_GROUPS - 1) / N_GROUPS * ((jk - jk.mean(0)) ** 2).sum(0))
    return point, se


def compare(name, q_new, q_old, y, phi, image, rng=None):
    h = gain_matrix(q_new, q_old, score="brier")
    ws = shift_weights(y, phi)
    res = {}
    for a in ALPHAS:
        w = ws ** a
        pt, se = jackknife(lambda m: weighted_split(h[m], y[m], phi[m], w[m]), image)
        tag = {0.0: "original", 1.0: "shifted"}.get(a, f"alpha={a:g}")
        res[tag] = {"total": float(pt[0]), "group": float(pt[1]), "case": float(pt[2]),
                    "total_ci": [float(pt[0] - 1.96 * se[0]), float(pt[0] + 1.96 * se[0])],
                    "group_ci": [float(pt[1] - 1.96 * se[1]), float(pt[1] + 1.96 * se[1])],
                    "case_ci": [float(pt[2] - 1.96 * se[2]), float(pt[2] + 1.96 * se[2])],
                    "kish_n": float(w.sum() ** 2 / (w * w).sum())}
    o, s_ = res["original"], res["shifted"]
    print(f"{name:34s} T {o['total']:+.5f} -> {s_['total']:+.5f} | P {o['group']:+.5f} -> "
          f"{s_['group']:+.5f} | R {o['case']:+.5f} -> {s_['case']:+.5f} "
          f"[{s_['case_ci'][0]:+.5f},{s_['case_ci'][1]:+.5f}] | path R " +
          " ".join(f"{res[k]['case']:+.5f}" for k in res), flush=True)
    return {"comparison": name, **res}


def sgg_rows(rng):
    base = AU.load("none")
    y, image = base["y"], base["image"]
    phi = base["subj"] * AU.N_OBJ + base["obj"]
    g = np.random.default_rng(20260811)                 # the audit's calibration split
    imgs = np.unique(image)
    cal_imgs = set(imgs[g.permutation(len(imgs))[: len(imgs) // 2]].tolist())
    cal = np.array([i in cal_imgs for i in image])
    aud = ~cal
    q = {"none": base["q"], **{v: AU.load(v)["q"] for v in ("TDE", "la1", "ietrans")}}
    q = {v: AU.temp_scale(x, AU.fit_temperature(x[cal], y[cal]))[aud] for v, x in q.items()}
    lab = {"TDE": "TDE vs MOTIFS", "la1": "logit-adjusted vs MOTIFS", "ietrans": "IETrans vs MOTIFS"}
    rows = [compare(lab[v], q[v], q["none"], y[aud], phi[aud], image[aud], rng)
            for v in ("TDE", "la1", "ietrans")]
    rows.append(compare("TDE vs logit-adjusted", q["TDE"], q["la1"], y[aud], phi[aud], image[aud], rng))
    return rows


def shifted_auc(n_boot=100, seed=0):
    """Within-cell AUC change on all identified relations, each relation weighted by
    its shift weight (comparison weights become w_i w_j); image bootstrap."""
    meta = np.load(ROOT / "data/vg_motifs/wager_sgg/meta.npz")
    drop = json.loads((ROOT / "data/vg_motifs/wager_sgg/missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    y = meta["pred"].astype(np.int64)[keep] - 1
    phi = (meta["subj"].astype(np.int64) * 151 + meta["obj"].astype(np.int64))[keep]
    image = meta["image_index"].astype(np.int64)[keep]
    ws = shift_weights(y, phi)
    _, ginv = np.unique(image, return_inverse=True)
    n_g = ginv.max() + 1

    def blocks(v):
        q = load_variant(v)["probs"][keep][:, 1:].astype(np.float64)
        return _blocks(np.log(np.maximum(q, 1e-12)), y, phi)

    base = blocks("none")
    out = {}
    for v in ("TDE", "la1", "ietrans"):
        bn = blocks(v)
        rng = np.random.default_rng(seed)
        res = {}
        for tag, w in (("original", np.ones(len(y))), ("shifted", ws)):
            d = _auc(bn, w) - _auc(base, w)
            draws = []
            for _ in range(n_boot):
                iw = rng.multinomial(n_g, np.full(n_g, 1.0 / n_g)).astype(float)[ginv] * w
                draws.append(_auc(bn, iw) - _auc(base, iw))
            res[tag] = {"difference": float(d), "ci": list(np.percentile(draws, [2.5, 97.5]))}
        out[v] = res
        print(f"AUC {v:8s} original {res['original']['difference']:+.4f} {res['original']['ci']}  "
              f"shifted {res['shifted']['difference']:+.4f} {res['shifted']['ci']}", flush=True)
    return out


def pixel_rows(rng):
    raw = np.load(ROOT / "data/vg/vg_predcls.npz")
    vis = np.load(ROOT / "data/vg_visual/vg_visual_models.npz")
    y, phi, image = vis["y"].astype(np.int64), vis["phi"].astype(np.int64), vis["image"]
    K = 50
    tr = raw["is_train"]
    n_cells = int(max(raw["phi"].max(), phi.max())) + 1
    counts = np.zeros((n_cells, K))
    np.add.at(counts, (raw["phi"][tr].astype(np.int64), raw["pred"][tr].astype(np.int64)), 1.0)
    glob = counts.sum(0) / counts.sum()
    freq = (counts + 0.1) / (counts + 0.1).sum(1, keepdims=True)    # as in vg_prior_consequence
    freq[counts.sum(1) == 0] = glob
    q = {"FREQ": freq[phi],
         **{k: vis[k].astype(np.float64) / vis[k].sum(1, keepdims=True)
            for k in ("MLP-CLASS-S", "MLP-SPATIAL-S", "MLP-VISUAL-S")}}
    g = np.random.default_rng(20260810)                 # Sec. 6's calibration split
    imgs = np.unique(image)
    cal_imgs = set(imgs[g.permutation(len(imgs))[: len(imgs) // 2]].tolist())
    cal = np.array([i in cal_imgs for i in image])
    aud = ~cal
    import vg_visual_seed_stats as VS                    # the grid Sec. 6 uses
    q = {v: AU.temp_scale(x, VS.fit_temperature(x[cal], y[cal]))[aud] for v, x in q.items()}
    pairs = [("MLP-CLASS-S", "FREQ", "class-only vs FREQ"),
             ("MLP-SPATIAL-S", "MLP-CLASS-S", "geometry vs class-only"),
             ("MLP-VISUAL-S", "MLP-CLASS-S", "CLIP vs class-only"),
             ("MLP-VISUAL-S", "MLP-SPATIAL-S", "CLIP vs geometry")]
    return [compare(lab, q[a], q[b], y[aud], phi[aud], image[aud], rng) for a, b, lab in pairs]


def main():
    rng = np.random.default_rng(0)
    rows = sgg_rows(rng) + pixel_rows(rng)
    auc = shifted_auc()
    OUT.write_text(json.dumps({"n_groups": N_GROUPS, "alphas": list(ALPHAS),
                               "interval": "delete-a-group jackknife over images",
                               "score": "quadratic, temperature-matched",
                               "rows": rows, "auc_sgg": auc}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
