"""Cross-domain WAGER study: long-tailed image classification (CIFAR-100-LT).

The Visual Genome study audits a relation-prediction gain against the ordered
object-class pair.  This driver applies the *same* estimator, unchanged, to a
structurally different task -- single-image classification -- to test the
broader-applicability claim empirically rather than by analogy.

Compared models (all ResNet-32 trained on CIFAR-100-LT, imbalance ratio 100, by the
companion Colab script; this driver consumes only their cached test probabilities):

  CE    vanilla cross-entropy baseline
  CB    class-balanced effective-number re-weighting (Cui et al. 2019) from scratch
  DRW   plain cross-entropy, class-balanced weights deferred to the final epochs
        (Cao et al. 2019) -- the schedule that actually improves balanced accuracy

Choice of the prior feature ``phi``
-----------------------------------
``phi`` must be a declared feature that *predicts* the label without *determining*
it.  Using the fine class label itself would make every cell label-homogeneous, so
within-cell label transport would be vacuous and the alignment gain identically zero
by construction -- a meaningless number rather than a null finding.  We therefore use
CIFAR-100's own 20 coarse superclasses as the primary ``phi``: each cell holds five
fine labels, mirroring the SGG setup where a class-pair cell holds several predicates.
The audited question becomes: does a long-tail method improve per-instance
discrimination *within* a superclass, or merely re-fit the within-superclass
fine-class frequency distribution?

Two further declared priors are reported: ``global`` (a single cell -- the trivial
coarsening of any ``phi``, instantiating Proposition 2 in a second domain) and
``tier`` (head/mid/tail training-frequency tiers, the prior most directly associated
with the long-tail literature).
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
DATA = os.path.join(ROOT, "data", "cifar_lt", "cifar_lt_results.npz")
RESULTS = os.path.join(ROOT, "results")
os.makedirs(RESULTS, exist_ok=True)

ALPHA = 0.05
N_RANDOMIZATIONS = 499

# Standard long-tail tier convention (Liu et al. 2019): many-shot > 100 training
# images, medium-shot 20-100, few-shot < 20.
TIER_EDGES = (20, 100)

TIER_NAMES = {0: "few-shot (<20)", 1: "medium-shot (20-100)", 2: "many-shot (>100)"}


def _json_safe(value):
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def frequency_tier(per_class_n: np.ndarray) -> np.ndarray:
    """Map each class id to 0=few-shot, 1=medium-shot, 2=many-shot."""
    lo, hi = TIER_EDGES
    tier = np.full(len(per_class_n), 1, dtype=np.int64)
    tier[per_class_n < lo] = 0
    tier[per_class_n > hi] = 2
    return tier


def _normalize(q):
    """float32 softmax rows do not sum to exactly 1; the estimator requires that."""
    q = q.astype(np.float64)
    return q / q.sum(axis=1, keepdims=True)


def compare(q_new, q_old, new_name, old_name, y, priors, tier_of_class, seed0):
    """Decompose one model pair's gain under every declared prior feature."""
    rows, per_tier = [], []
    for k, (phi_name, phi) in enumerate(priors.items()):
        res = decompose_gain(q_new, q_old, y, phi, score="brier", alpha=ALPHA)
        p_value, _ = cyclic_randomization_test(
            q_new, q_old, y, phi, score="brier",
            n_randomizations=N_RANDOMIZATIONS, seed=seed0 + k,
        )
        rows.append({
            "prior_feature": phi_name, "new": new_name, "old": old_name,
            **res.as_row(), "randomization_p": p_value,
        })
        print(f"  phi={phi_name:11s} total={res.total_gain:+.5f}  "
              f"prior={res.prior_gain:+.5f}  align={res.reasoning_gain:+.5f} "
              f"CI=[{res.reasoning_ci[0]:+.5f},{res.reasoning_ci[1]:+.5f}] "
              f"p={p_value:.4g} cells={res.n_cells}", flush=True)

    primary = decompose_gain(q_new, q_old, y, priors["superclass"],
                             score="brier", alpha=ALPHA)
    for t, tname in TIER_NAMES.items():
        mask = (tier_of_class[y] == t) & primary.eligible
        if not mask.any():
            continue
        per_tier.append({
            "new": new_name, "old": old_name, "tier": tname, "n": int(mask.sum()),
            "total_gain": float(primary.observed[mask].mean()),
            "prior_gain": float(primary.transported[mask].mean()),
            "alignment_gain": float(primary.alignment[mask].mean()),
        })
        print(f"    tier {tname:22s} n={mask.sum():5d} "
              f"total={per_tier[-1]['total_gain']:+.5f} "
              f"align={per_tier[-1]['alignment_gain']:+.5f}", flush=True)
    return rows, per_tier


def main():
    t0 = time.time()
    if not os.path.exists(DATA):
        raise SystemExit(
            f"missing {DATA}\nRun the Colab training job first and download its "
            "cifar_lt_results.npz into data/cifar_lt/."
        )
    d = np.load(DATA, allow_pickle=True)
    y = d["y_test"].astype(np.int64)
    per_class_n = d["per_class_train_n"].astype(np.int64)
    if "coarse_of_class" in d:
        coarse_of_class = d["coarse_of_class"].astype(np.int64)
    else:
        # CIFAR-100's fine->coarse superclass map, derived once from the dataset's
        # own coarse_label column (see data/cifar_lt/coarse_of_class.npy).
        coarse_of_class = np.load(
            os.path.join(os.path.dirname(DATA), "coarse_of_class.npy")).astype(np.int64)

    models = {"CE": _normalize(d["probs_baseline"]), "CB": _normalize(d["probs_cb"])}
    if "probs_drw" in d:
        models["DRW"] = _normalize(d["probs_drw"])

    tier_of_class = frequency_tier(per_class_n)
    priors = {
        "superclass": coarse_of_class[y],
        "global": np.zeros(len(y), dtype=np.int64),
        "tier": tier_of_class[y],
    }

    accuracy = {name: float(np.mean(q.argmax(1) == y)) for name, q in models.items()}
    print("Test accuracy: " + "  ".join(f"{k}={v:.4f}" for k, v in accuracy.items()),
          flush=True)

    pairs = [("CB", "CE")] + ([("DRW", "CE")] if "DRW" in models else [])
    rows, per_tier = [], []
    # NumPy 1.26 on Apple's Accelerate BLAS raises spurious "divide by zero / overflow /
    # invalid value encountered in matmul" RuntimeWarnings: Accelerate leaves FP exception
    # flags set from vectorized padding lanes and NumPy surfaces them even though the
    # result is correct.  Verified on this data -- the matmul output is finite and agrees
    # with both an einsum and an explicit broadcast-and-sum to 5.7e-14 (float64 rounding).
    # Suppressed here rather than in wager/antisymmetric.py so the estimator stays untouched.
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        for i, (new, old) in enumerate(pairs):
            print(f"\n{new} vs {old}:", flush=True)
            r, pt = compare(models[new], models[old], f"ResNet32-{new}",
                            f"ResNet32-{old}", y, priors, tier_of_class, seed0=10 * i)
            rows += r
            per_tier += pt

    out = {
        "algorithm": "WAGER-within-cell-antisymmetric",
        "dataset": "CIFAR-100-LT (imbalance ratio 100)",
        "score": "quadratic/Brier",
        "alpha": ALPHA,
        "n_randomizations": N_RANDOMIZATIONS,
        "n_test": int(len(y)),
        "n_classes": int(models["CE"].shape[1]),
        "imbalance_ratio": float(d["imbalance_ratio"]),
        "epochs": int(d["epochs"]),
        "drw_start_epoch": int(d["drw_start_epoch"]) if "drw_start_epoch" in d else None,
        "accuracy": accuracy,
        "comparisons": rows,
        "per_tier_at_superclass_phi": per_tier,
        "seconds": time.time() - t0,
    }
    path = os.path.join(RESULTS, "cifar_lt_results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_json_safe(out), f, indent=2, allow_nan=False)
    print(f"\nSaved {path} in {time.time() - t0:.1f}s", flush=True)
    return out


if __name__ == "__main__":
    main()
