"""Phase 2 - real-data SGG study on Visual Genome (PredCls) with WAGER.

Trains / builds five predicate predictors on real VG relationship annotations,
caches their test-split predictive distributions, then runs the full WAGER
analysis: per-model e-value + reasoning/prior information, and the Reasoning
Gain Ratio (RGR) with anytime-valid verdicts for the headline model pairs.

Anchor gate: the FREQ frequency baseline should return I_reason ~ 0 and an
e-value ~ 1 -- WAGER must certify that a lookup table does no visual reasoning.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wager.pipeline import ModelData, run_wager_permutations
from wager.rgr import reasoning_gain_ratio
from experiments import sgg_models as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "vg", "vg_predcls.npz")
RESULTS = os.path.join(ROOT, "results")
os.makedirs(RESULTS, exist_ok=True)

R_PERM = 40
ALPHA = 0.05
MAX_TEST = 60000   # image-blocked subsample of the test split for WAGER compute


def subsample_test(image_te, rng, max_n):
    """Image-blocked subsample: keep whole images until ~max_n instances."""
    if len(image_te) <= max_n:
        return np.ones(len(image_te), dtype=bool)
    uniq = np.unique(image_te)
    rng.shuffle(uniq)
    keep_imgs, count = set(), 0
    for im in uniq:
        keep_imgs.add(im)
        count += int(np.sum(image_te == im))
        if count >= max_n:
            break
    return np.array([im in keep_imgs for im in image_te], dtype=bool)


def main():
    np.seterr(all="ignore")
    t0 = time.time()
    d = np.load(DATA, allow_pickle=True)
    subj, obj, pred = d["subj"], d["obj"], d["pred"]
    sbox, obox, image, phi = d["sbox"], d["obox"], d["image"], d["phi"]
    is_train = d["is_train"]
    K, n_obj = int(d["n_pred"]), int(d["n_obj"])
    pred_vocab = list(d["pred_vocab"])
    print(f"Loaded VG PredCls: {len(pred)} rels, K={K} predicates, {n_obj} objects "
          f"({is_train.sum()} train / {(~is_train).sum()} test)")

    tr = is_train
    te = ~is_train
    # spatial + overlap features
    feat_all = M.spatial_features(sbox.astype(np.float64), obox.astype(np.float64))
    overlap = (feat_all[:, 7] > 0).astype(np.int64)  # IoU column
    emb_all = M.class_embeddings(subj, obj, n_obj, dim=32, seed=0)

    subj_te, obj_te, pred_te = subj[te], obj[te], pred[te]
    phi_te, image_te = phi[te], image[te]
    ov_te = overlap[te]
    coarse_te = subj_te.astype(np.int64)  # subject class = coarse backoff key

    print("Building model predictive distributions ...")
    dists = {}
    # --- FREQ (anchor) ---
    dists["FREQ"] = M.freq_baseline(subj[tr], obj[tr], pred[tr], subj_te, obj_te, K, n_obj)
    # --- FREQ + OVERLAP ---
    dists["FREQ+OVERLAP"] = M.freq_overlap_baseline(
        subj[tr], obj[tr], pred[tr], overlap[tr], subj_te, obj_te, ov_te, K, n_obj)
    # --- MLP on class embeddings only (phi-measurable) ---
    dists["MLP-CLASS"] = M.train_mlp(emb_all[tr], pred[tr], emb_all[te], K,
                                     hidden=(256, 128), epochs=12, label="MLP-CLASS")
    # --- MLP on class + spatial geometry (reasoning) ---
    feat_cls_sp = np.concatenate([emb_all, feat_all], axis=1)
    dists["MLP-SPATIAL"] = M.train_mlp(feat_cls_sp[tr], pred[tr], feat_cls_sp[te], K,
                                       hidden=(256, 128), epochs=15, label="MLP-SPATIAL")
    # --- larger spatial MLP ---
    dists["MLP-SPATIAL+"] = M.train_mlp(feat_cls_sp[tr], pred[tr], feat_cls_sp[te], K,
                                        hidden=(512, 256, 128), epochs=20, label="MLP-SPATIAL+")

    # report test accuracy for context
    accs = {name: float(np.mean(q.argmax(1) == pred_te)) for name, q in dists.items()}
    print("Test top-1 accuracy:", {k: round(v, 4) for k, v in accs.items()})

    # --- image-blocked subsample for WAGER ---
    rng = np.random.default_rng(0)
    keep = subsample_test(image_te, rng, MAX_TEST)
    print(f"WAGER on {keep.sum()} test instances (image-blocked subsample)")

    yk, phik, imgk, coarsek = pred_te[keep], phi_te[keep], image_te[keep], coarse_te[keep]
    c = float(np.log(K))

    results = {}
    rows = []
    for name, q in dists.items():
        data = ModelData(name, q[keep], yk, phik, imgk, coarse=coarsek)
        res = run_wager_permutations(data, R=R_PERM, c=c, alpha=ALPHA, seed=0)
        results[name] = res
        row = res.as_row()
        row["test_acc"] = accs[name]
        rows.append(row)
        print(f"  {name:14s} e={res.e_value:.3e}  I_reason={res.I_reason:.4f} "
              f"CI[{res.I_reason_ci[0]:.3f},{res.I_reason_ci[1]:.3f}]  "
              f"I_prior={res.I_prior:.3f}  I_tot={res.I_tot:.3f}")

    # --- RGR for headline pairs ---
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
              f"{rgr.fieller_ci[1]:.3f}]  anytime[{rgr.anytime_ci[0]:.3f},"
              f"{rgr.anytime_ci[1]:.3f}]  -> {rgr.verdict}")

    # anchor gate
    freq = results["FREQ"]
    anchor_pass = bool(abs(freq.I_reason) < 0.05 and freq.e_value < 20)

    out = {
        "dataset": "VisualGenome-PredCls",
        "n_rels_total": int(len(pred)),
        "n_test_used": int(keep.sum()),
        "K": K, "n_obj": n_obj,
        "predicates": pred_vocab,
        "R": R_PERM, "alpha": ALPHA,
        "model_rows": rows,
        "rgr_rows": rgr_rows,
        "test_accuracy": accs,
        "anchor_freq_I_reason": freq.I_reason,
        "anchor_freq_e_value": freq.e_value,
        "anchor_pass": anchor_pass,
        "seconds": time.time() - t0,
    }
    path = os.path.join(RESULTS, "sgg_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    # also cache distributions for stratified analysis / figures
    np.savez_compressed(os.path.join(RESULTS, "sgg_dists.npz"),
                        **{n: dists[n][keep] for n in dists},
                        y=yk, phi=phik, image=imgk, pred_vocab=np.array(pred_vocab, dtype=object))
    print(f"\nAnchor gate (FREQ=>I_reason~0): {'PASS' if anchor_pass else 'FAIL'} "
          f"(I_reason={freq.I_reason:.4f}, e={freq.e_value:.2f})")
    print(f"Saved -> {path}  [{out['seconds']:.1f}s]")
    return out


if __name__ == "__main__":
    main()
