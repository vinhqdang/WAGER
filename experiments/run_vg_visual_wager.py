"""Real-pixel WAGER study on Visual Genome (matched training subsample).

Audits whether a model that consumes actual image content adds instance alignment
beyond one that sees only annotation-derived box geometry.

All three compared predictors are trained on the *same* relation subsample and differ
only in their feature set, so a difference between them isolates feature content rather
than training-set size:

  MLP-CLASS-S    subject/object class embeddings only (a function of phi alone)
  MLP-SPATIAL-S  class embeddings + 12 box-geometry features
  MLP-VISUAL-S   class embeddings + frozen CLIP ViT-B/32 embeddings of the subject and
                 object crops taken from the real image

This is deliberately kept separate from the full-data comparison in the main VG table:
mixing models trained on different amounts of data into one comparison would confound
the very gain being attributed. The audit itself uses the complete test split.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wager.antisymmetric import cyclic_randomization_test, decompose_gain

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "vg_visual", "vg_visual_models.npz")
RESULTS = os.path.join(ROOT, "results")
os.makedirs(RESULTS, exist_ok=True)

ALPHA = 0.05
N_RANDOMIZATIONS = 499

PAIRS = [
    ("MLP-SPATIAL-S", "MLP-CLASS-S"),   # geometry beyond the class pair (reference point)
    ("MLP-VISUAL-S", "MLP-CLASS-S"),    # pixels beyond the class pair
    ("MLP-VISUAL-S", "MLP-SPATIAL-S"),  # pixels beyond geometry -- the decisive comparison
]


def _json_safe(v):
    if isinstance(v, dict):
        return {k: _json_safe(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_json_safe(x) for x in v]
    if isinstance(v, float) and not np.isfinite(v):
        return None
    return v


def main():
    t0 = time.time()
    if not os.path.exists(DATA):
        raise SystemExit(f"missing {DATA}\nRun the Colab job and download "
                         "vg_visual_models.npz into data/vg_visual/.")
    d = np.load(DATA, allow_pickle=True)
    y, phi, image = d["y"].astype(np.int64), d["phi"], d["image"]
    models = {}
    for name in ("MLP-CLASS-S", "MLP-SPATIAL-S", "MLP-VISUAL-S"):
        q = d[name].astype(np.float64)
        models[name] = q / q.sum(axis=1, keepdims=True)   # float32 rows need renormalizing

    accuracy = {k: float(np.mean(q.argmax(1) == y)) for k, q in models.items()}
    print("Test accuracy: " + "  ".join(f"{k}={v:.4f}" for k, v in accuracy.items()),
          flush=True)

    rows = []
    # NumPy 1.26 on Apple's Accelerate BLAS emits spurious matmul FP warnings; the
    # results are exact (verified against einsum elsewhere in this repo).
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        for seed, (new, old) in enumerate(PAIRS):
            r = decompose_gain(models[new], models[old], y, phi,
                               groups=image, score="brier", alpha=ALPHA)
            p, _ = cyclic_randomization_test(models[new], models[old], y, phi,
                                             score="brier",
                                             n_randomizations=N_RANDOMIZATIONS, seed=seed)
            rows.append({"new": new, "old": old, **r.as_row(), "randomization_p": p})
            print(f"{new:14s} vs {old:14s} T={r.total_gain:+.5f} P={r.prior_gain:+.5f} "
                  f"R={r.reasoning_gain:+.5f} CI=[{r.reasoning_ci[0]:+.5f},"
                  f"{r.reasoning_ci[1]:+.5f}] p={p:.4g} coverage={r.coverage:.3f}",
                  flush=True)

    out = {
        "algorithm": "WAGER-within-cell-antisymmetric",
        "dataset": "VisualGenome-PredCls (matched training subsample)",
        "score": "quadratic/Brier",
        "alpha": ALPHA,
        "n_randomizations": N_RANDOMIZATIONS,
        "n_test": int(len(y)),
        "n_images": int(len(np.unique(image))),
        "n_train_relations": int(d["n_train_relations"]),
        "n_unique_crops": int(d["n_unique_crops"]),
        "n_images_fetched": int(d["n_images_fetched"]),
        "n_missing_images": int(d["n_missing_images"]),
        "accuracy": accuracy,
        "comparisons": rows,
        "seconds": time.time() - t0,
    }
    path = os.path.join(RESULTS, "vg_visual_results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_json_safe(out), f, indent=2, allow_nan=False)
    print(f"Saved {path} in {time.time()-t0:.1f}s", flush=True)
    return out


if __name__ == "__main__":
    main()
