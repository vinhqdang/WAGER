"""Phase 2 - real-data SGG study on Visual Genome (PredCls) with WAGER.

Builds five predicate predictors on real VG relationship annotations, then runs
WAGER with a dense, frozen self-prior projection fit on a held-out half of the
test set (image-blocked).  Reports each model's e-value + reasoning/prior
information and the Reasoning Gain Ratio (RGR) with verdicts for headline pairs.

Anchor gate: the FREQ frequency baseline must return I_reason ~ 0 and e ~ 1 --
WAGER must certify that a lookup table performs no visual reasoning.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wager.pipeline import ModelData, build_projection, run_wager_eval
from wager.core import lookup_projection
from wager.rgr import reasoning_gain_ratio
from experiments import sgg_models as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "vg", "vg_predcls.npz")
RESULTS = os.path.join(ROOT, "results")
os.makedirs(RESULTS, exist_ok=True)

R_PERM = 24
ALPHA = 0.05
PROJ_M = 0.25  # shrinkage pseudo-count for the frozen projection


def main():
    np.seterr(all="ignore")
    t0 = time.time()
    d = np.load(DATA, allow_pickle=True)
    subj, obj, pred = d["subj"], d["obj"], d["pred"]
    sbox, obox, image, phi = d["sbox"], d["obox"], d["image"], d["phi"]
    is_train = d["is_train"]
    K, n_obj = int(d["n_pred"]), int(d["n_obj"])
    pred_vocab = list(d["pred_vocab"])
    tr, te = is_train, ~is_train
    print(f"VG PredCls: {len(pred)} rels, K={K}, {n_obj} objects "
          f"({tr.sum()} train / {te.sum()} test)")

    feat_all = M.spatial_features(sbox.astype(np.float64), obox.astype(np.float64))
    overlap = (feat_all[:, 7] > 0).astype(np.int64)
    emb_all = M.class_embeddings(subj, obj, n_obj, dim=32, seed=0)
    feat_cls_sp = np.concatenate([emb_all, feat_all], axis=1)

    subj_te = subj[te].astype(np.int64)
    obj_te = obj[te]
    pred_te, phi_te, image_te, ov_te = pred[te], phi[te], image[te], overlap[te]

    print("Building model predictive distributions (test split) ...")
    dists = {}
    dists["FREQ"] = M.freq_baseline(subj[tr], obj[tr], pred[tr], subj_te, obj_te, K, n_obj)
    dists["FREQ+OVERLAP"] = M.freq_overlap_baseline(
        subj[tr], obj[tr], pred[tr], overlap[tr], subj_te, obj_te, ov_te, K, n_obj)
    dists["MLP-CLASS"] = M.train_mlp(emb_all[tr], pred[tr], emb_all[te], K,
                                     hidden=(256, 128), epochs=12, label="MLP-CLASS")
    dists["MLP-SPATIAL"] = M.train_mlp(feat_cls_sp[tr], pred[tr], feat_cls_sp[te], K,
                                       hidden=(256, 128), epochs=15, label="MLP-SPATIAL")
    dists["MLP-SPATIAL+"] = M.train_mlp(feat_cls_sp[tr], pred[tr], feat_cls_sp[te], K,
                                        hidden=(512, 256, 128), epochs=20, label="MLP-SPATIAL+")

    accs = {n: float(np.mean(q.argmax(1) == pred_te)) for n, q in dists.items()}
    print("Test top-1 accuracy:", {k: round(v, 4) for k, v in accs.items()})

    # --- split test images 50/50 -> PROJ (projection-fit) vs EVAL (betting) ---
    img_u = np.unique(image_te)
    rng = np.random.default_rng(0)
    rng.shuffle(img_u)
    proj_imgs = set(img_u[: len(img_u) // 2].tolist())
    in_proj = np.array([im in proj_imgs for im in image_te])
    ev = ~in_proj
    print(f"PROJ N={in_proj.sum()}  EVAL N={ev.sum()}  cells(EVAL)={len(np.unique(phi_te[ev]))}")

    c = float(np.log(K))
    yk, phik, imgk, coarsek = pred_te[ev], phi_te[ev], image_te[ev], subj_te[ev]

    results, rows = {}, []
    figdata = {}  # per-model betting streams + materialized projection for figures
    for name, q in dists.items():
        proj = build_projection(q[in_proj], phi_te[in_proj], K, m=PROJ_M,
                                coarse_proj=subj_te[in_proj])
        data = ModelData(name, q[ev], yk, phik, imgk, coarse=coarsek)
        res = run_wager_eval(data, proj, R=R_PERM, c=c, alpha=ALPHA, seed=0)
        results[name] = res
        row = res.as_row(); row["test_acc"] = accs[name]
        rows.append(row)
        # figure data: per-instance reasoning (d) and prior (e) scores on EVAL,
        # plus the materialized self-prior projection q_bar for projection plots.
        cell_proj, cell_corr, coarse_proj, glob, unif = proj
        qbar_ev = lookup_projection(cell_proj, coarse_proj, glob, phik, coarsek)
        figdata[f"d_{name}"] = res.d_streams[0].astype(np.float32)
        figdata[f"e_{name}"] = res.e_streams[0].astype(np.float32)
        figdata[f"qbar_{name}"] = qbar_ev.astype(np.float32)
        figdata[f"q_{name}"] = q[ev].astype(np.float32)
        print(f"  {name:14s} e={res.e_value:.3e}  I_reason={res.I_reason:.4f} "
              f"CI[{res.I_reason_ci[0]:.3f},{res.I_reason_ci[1]:.3f}]  "
              f"I_prior={res.I_prior:.3f}  I_tot={res.I_tot:.3f}")

    pairs = [
        ("FREQ+OVERLAP", "FREQ"),
        ("MLP-CLASS", "FREQ"),
        ("MLP-SPATIAL", "FREQ"),
        ("MLP-SPATIAL+", "FREQ"),
        ("MLP-SPATIAL", "MLP-CLASS"),
        ("MLP-SPATIAL+", "MLP-SPATIAL"),
    ]
    rgr_rows = []
    for fp, f in pairs:
        rgr = reasoning_gain_ratio(results[fp], results[f], c=c, alpha=ALPHA)
        rgr_rows.append(rgr.as_row())
        print(f"  RGR({fp} vs {f}): {rgr.rgr:.3f}  Fieller[{rgr.fieller_ci[0]:.3f},"
              f"{rgr.fieller_ci[1]:.3f}]  -> {rgr.verdict}")

    freq = results["FREQ"]
    anchor_pass = bool(abs(freq.I_reason) < 0.02 and freq.e_value < 20)

    out = {
        "dataset": "VisualGenome-PredCls",
        "n_rels_total": int(len(pred)), "n_eval": int(ev.sum()), "n_proj": int(in_proj.sum()),
        "K": K, "n_obj": n_obj, "predicates": pred_vocab,
        "R": R_PERM, "alpha": ALPHA, "proj_m": PROJ_M,
        "model_rows": rows, "rgr_rows": rgr_rows, "test_accuracy": accs,
        "anchor_freq_I_reason": freq.I_reason, "anchor_freq_e_value": freq.e_value,
        "anchor_pass": anchor_pass, "seconds": time.time() - t0,
    }
    with open(os.path.join(RESULTS, "sgg_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    np.savez_compressed(os.path.join(RESULTS, "sgg_dists.npz"),
                        **{n: dists[n][ev] for n in dists},
                        y=yk, phi=phik, image=imgk,
                        pred_vocab=np.array(pred_vocab, dtype=object))
    # figure data: betting streams, projection vectors, geometry of eval pairs
    np.savez_compressed(
        os.path.join(RESULTS, "sgg_figdata.npz"),
        y=yk, phi=phik, image=imgk, coarse=coarsek, obj=obj_te.astype(np.int64),
        sbox=sbox[te][ev].astype(np.float32), obox=obox[te][ev].astype(np.float32),
        pred_train=pred[tr].astype(np.int64),
        obj_vocab=np.array(list(d["obj_vocab"]), dtype=object),
        pred_vocab=np.array(pred_vocab, dtype=object),
        **figdata)
    print(f"\nAnchor gate (FREQ=>I_reason~0, e~1): {'PASS' if anchor_pass else 'FAIL'} "
          f"(I_reason={freq.I_reason:.4f}, e={freq.e_value:.3f})")
    print(f"Saved -> results/sgg_results.json  [{out['seconds']:.1f}s]")
    return out


if __name__ == "__main__":
    main()
