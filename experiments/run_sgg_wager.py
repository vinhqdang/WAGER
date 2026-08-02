"""Visual Genome study for within-cell antisymmetric WAGER.

The redesigned algorithm compares two frozen models directly.  It transports
labels among examples with the same ordered object-class pair and decomposes the
proper-score improvement into prior-recoverable and instance-alignment gains.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wager.antisymmetric import cyclic_randomization_test, decompose_gain
from experiments import sgg_models as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "vg", "vg_predcls.npz")
RESULTS = os.path.join(ROOT, "results")
os.makedirs(RESULTS, exist_ok=True)

ALPHA = 0.05
N_RANDOMIZATIONS = 499


def _build_models(d):
    subj, obj, pred = d["subj"], d["obj"], d["pred"]
    sbox, obox = d["sbox"], d["obox"]
    is_train = d["is_train"]
    k, n_obj = int(d["n_pred"]), int(d["n_obj"])
    tr, te = is_train, ~is_train

    feat_all = M.spatial_features(sbox.astype(np.float64), obox.astype(np.float64))
    overlap = (feat_all[:, 7] > 0).astype(np.int64)
    emb_all = M.class_embeddings(subj, obj, n_obj, dim=32, seed=0)
    feat_cls_sp = np.concatenate([emb_all, feat_all], axis=1)
    subj_te, obj_te = subj[te].astype(np.int64), obj[te]

    print("Building frozen model predictions ...", flush=True)
    models = {
        "FREQ": M.freq_baseline(subj[tr], obj[tr], pred[tr], subj_te, obj_te, k, n_obj),
        "FREQ+OVERLAP": M.freq_overlap_baseline(
            subj[tr], obj[tr], pred[tr], overlap[tr], subj_te, obj_te, overlap[te], k, n_obj
        ),
        "MLP-CLASS": M.train_mlp(
            emb_all[tr], pred[tr], emb_all[te], k,
            hidden=(256, 128), epochs=12, label="MLP-CLASS"
        ),
        "MLP-SPATIAL": M.train_mlp(
            feat_cls_sp[tr], pred[tr], feat_cls_sp[te], k,
            hidden=(256, 128), epochs=15, label="MLP-SPATIAL"
        ),
        "MLP-SPATIAL+": M.train_mlp(
            feat_cls_sp[tr], pred[tr], feat_cls_sp[te], k,
            hidden=(512, 256, 128), epochs=20, label="MLP-SPATIAL+"
        ),
    }
    return models


def main():
    t0 = time.time()
    d = np.load(DATA, allow_pickle=True)
    pred, phi, image = d["pred"][~d["is_train"]], d["phi"][~d["is_train"]], d["image"][~d["is_train"]]
    models = _build_models(d)
    accuracy = {name: float(np.mean(q.argmax(1) == pred)) for name, q in models.items()}

    pairs = [
        ("FREQ+OVERLAP", "FREQ"),
        ("MLP-CLASS", "FREQ"),
        ("MLP-SPATIAL", "FREQ"),
        ("MLP-SPATIAL+", "FREQ"),
        ("MLP-SPATIAL", "MLP-CLASS"),
        ("MLP-SPATIAL+", "MLP-SPATIAL"),
    ]
    rows = []
    arrays = {"y": pred, "phi": phi, "image": image}
    for seed, (new, old) in enumerate(pairs):
        result = decompose_gain(
            models[new], models[old], pred, phi,
            groups=image, score="brier", alpha=ALPHA,
        )
        p_value, null = cyclic_randomization_test(
            models[new], models[old], pred, phi,
            score="brier", n_randomizations=N_RANDOMIZATIONS, seed=seed,
        )
        row = {"new": new, "old": old, **result.as_row(), "randomization_p": p_value}
        rows.append(row)
        key = f"{new}_vs_{old}".replace("+", "plus").replace("-", "_")
        arrays[f"alignment_{key}"] = result.alignment.astype(np.float32)
        arrays[f"null_{key}"] = null.astype(np.float32)
        print(
            f"{new:14s} vs {old:14s}: total={result.total_gain:+.5f}  "
            f"prior={result.prior_gain:+.5f}  align={result.reasoning_gain:+.5f} "
            f"CI=[{result.reasoning_ci[0]:+.5f},{result.reasoning_ci[1]:+.5f}] "
            f"p={p_value:.4g} coverage={result.coverage:.3f}",
            flush=True,
        )

    out = {
        "algorithm": "WAGER-within-cell-antisymmetric",
        "dataset": "VisualGenome-PredCls",
        "score": "quadratic/Brier",
        "alpha": ALPHA,
        "n_randomizations": N_RANDOMIZATIONS,
        "n_test": int(len(pred)),
        "n_images": int(len(np.unique(image))),
        "n_prior_cells": int(len(np.unique(phi))),
        "accuracy": accuracy,
        "comparisons": rows,
        "seconds": time.time() - t0,
    }
    with open(os.path.join(RESULTS, "antisymmetric_results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    np.savez_compressed(os.path.join(RESULTS, "antisymmetric_arrays.npz"), **arrays)
    np.savez_compressed(
        os.path.join(RESULTS, "sgg_dists.npz"),
        **models, y=pred, phi=phi, image=image,
        pred_vocab=np.array(list(d["pred_vocab"]), dtype=object),
    )
    print(f"Saved redesigned results in {time.time() - t0:.1f}s", flush=True)
    return out


if __name__ == "__main__":
    main()
