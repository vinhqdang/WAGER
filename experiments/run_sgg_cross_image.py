"""Cross-image variant of the within-cell split, on the scene-graph audit.

Many PredCls relations in a cell come from the same image and can share identical
subject and object boxes, so their outputs are not exchangeable draws.  This script
compares the standard within-cell split (every pair in the cell, grouped by image)
with ``cross_image_split`` (only pairs from different images) on

  1. the duplicate structure of the canonical PredCls relations;
  2. proper-score rows (quadratic score) on the audit half, under per-model
     temperature and temperature + per-class bias, for TDE, la1 and ietrans vs none;
  3. mean recall@50 with graph constraint (mode "gc") for TDE vs none, la1 vs none
     and TDE vs la1, on all relations in eligible cells.

Loaders are those of run_sgg_rank_robustness (sgg_data, fit_family, apply_family),
run_sgg_audit_wager (fit_temperature, temp_scale) and run_sgg_recall_split (load,
split), so every number is built exactly as in those scripts.

Writes results/sgg_cross_image.json.

Run: python experiments/run_sgg_cross_image.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import (  # noqa: E402
    cross_image_split,
    decompose_gain,
    gain_matrix,
)
import run_sgg_audit_wager as AU  # noqa: E402
import run_sgg_rank_robustness as RR  # noqa: E402
import run_sgg_recall_split as RS  # noqa: E402

OUT = ROOT / "results/sgg_cross_image.json"
N_JACK = 100
SEED = 0
ALPHA = 0.05
K_RECALL = 50
N_OBJ = 151
PROPER_PAIRS = (("TDE", "none"), ("la1", "none"), ("ietrans", "none"))
RECALL_PAIRS = (("TDE", "none"), ("la1", "none"), ("TDE", "la1"))


def _cross_row(r: dict) -> dict:
    return {
        "total": float(r["total"]),
        "group": float(r["group"]),
        "case": float(r["case"]),
        "case_ci": [float(r["case_ci"][0]), float(r["case_ci"][1])],
        "case_se": float(r["case_se"]),
        "n_eligible_cells": int(r["n_eligible_cells"]),
        "n_cases_in_eligible_cells": int(r["n_cases_in_eligible_cells"]),
        "frac_pairs_within_image": float(r["frac_pairs_within_image"]),
        "n_images": int(r["n_images"]),
        "n_jack_groups": int(r["n_jack_groups"]),
    }


def _std_row(g) -> dict:
    return {
        "total": float(g.total_gain),
        "group": float(g.prior_gain),
        "case": float(g.alignment_gain),
        "case_ci": [float(g.alignment_ci[0]), float(g.alignment_ci[1])],
        "case_se": float(g.standard_error),
        "n_identified": int(g.n_identified),
    }


def duplicate_stats(keep: np.ndarray, mask: np.ndarray) -> dict:
    """Relations sharing image, subject/object class and both boxes with another relation.

    ``keep`` is the audit's drop of unscored pairs (length = all relations) and
    ``mask`` selects rows of the kept relations (the audit half, or all kept).
    """
    meta = np.load(RS.DDIR / "meta.npz")
    subj = meta["subj"].astype(np.int64)
    obj = meta["obj"].astype(np.int64)
    phi = subj * N_OBJ + obj
    feats = np.column_stack([
        meta["image_index"].astype(np.float64), subj, obj,
        meta["sbox"].astype(np.float64), meta["obox"].astype(np.float64),
    ])[keep][mask]
    phi = phi[keep][mask]
    _, inv, counts = np.unique(feats, axis=0, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1)
    dup = counts[inv] >= 2
    _, pc, pcnt = np.unique(phi, return_inverse=True, return_counts=True)
    multi_cell = pcnt[pc.reshape(-1)] >= 2
    return {
        "n_relations": int(mask.sum()),
        "n_duplicated_relations": int(dup.sum()),
        "fraction_duplicated": float(dup.mean()),
        "fraction_duplicated_in_cells_with_2_plus": float(dup[multi_cell].mean()),
        "n_identical_groups_size_2_plus": int((counts >= 2).sum()),
        "max_identical_group_size": int(counts.max()),
    }


def proper_rows(Q, y, phi, image, cal) -> list[dict]:
    aud = ~cal
    log_q = {v: np.log(np.clip(q, RR.EPS, None)) for v, q in Q.items()}
    families = {"temperature": {}, "temperature + class bias": {}}
    for v in Q:
        t = AU.fit_temperature(Q[v][cal], y[cal])
        families["temperature"][v] = AU.temp_scale(Q[v], t)[aud]
        p = RR.fit_family(log_q[v][cal], y[cal], bias=True)
        families["temperature + class bias"][v] = RR.apply_family(log_q[v], p, True)[aud]

    rows = []
    for fam, probs in families.items():
        for new, old in PROPER_PAIRS:
            qn, qo = probs[new], probs[old]
            with np.errstate(all="ignore"):
                g = decompose_gain(qn, qo, y[aud], phi[aud], groups=image[aud], score="brier")
            h = gain_matrix(qn, qo, score="brier")
            r = cross_image_split(h, y[aud], phi[aud], image[aud],
                                  n_jack=N_JACK, seed=SEED, alpha=ALPHA)
            row = {"family": fam, "new": new, "old": old, "score": "brier",
                   "standard": _std_row(g), "cross_image": _cross_row(r)}
            rows.append(row)
            print(f"[{fam:24s}] {new:>7s} vs {old:<4s} std  total {row['standard']['total']:+.5f} "
                  f"group {row['standard']['group']:+.5f} case {row['standard']['case']:+.5f} "
                  f"[{row['standard']['case_ci'][0]:+.5f},{row['standard']['case_ci'][1]:+.5f}]")
            print(f"{'':31s} cross total {row['cross_image']['total']:+.5f} "
                  f"group {row['cross_image']['group']:+.5f} case {row['cross_image']['case']:+.5f} "
                  f"[{row['cross_image']['case_ci'][0]:+.5f},{row['cross_image']['case_ci'][1]:+.5f}] "
                  f"cells {row['cross_image']['n_eligible_cells']} "
                  f"within {row['cross_image']['frac_pairs_within_image']:.3f}", flush=True)
    return rows


def recall_rows() -> list[dict]:
    meta = np.load(RS.DDIR / "meta.npz")
    y = meta["pred"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    phi = meta["subj"].astype(np.int64) * RS.N_OBJ + meta["obj"].astype(np.int64)
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    eligible = cnt[inv.reshape(-1)] >= 2
    idx = np.flatnonzero(eligible)
    n_e = int(eligible.sum())
    n_y = np.bincount(y[eligible], minlength=RS.N_PRED + 1).astype(float)
    w = np.zeros(RS.N_PRED + 1)
    w[1:] = np.where(n_y[1:] > 0, 1.0 / (RS.N_PRED * np.maximum(n_y[1:], 1)), 0.0)

    hits = {}
    for v in ("none", "TDE", "la1"):
        hits[v] = RS.load(v)["gc"] < K_RECALL

    rows = []
    for new, old in RECALL_PAIRS:
        std = RS.split(hits[new], hits[old], y, phi, image, eligible, w)
        h_e = n_e * w[None, :] * (hits[new][idx].astype(np.float64) - hits[old][idx])
        r = cross_image_split(h_e, y[idx], phi[idx], image[idx],
                              n_jack=N_JACK, seed=SEED, alpha=ALPHA)
        row = {"new": new, "old": old, "metric": f"mean recall@{K_RECALL} (gc)",
               "n_eligible_relations": n_e,
               "standard": {k: (list(v) if isinstance(v, tuple) else v) for k, v in std.items()},
               "cross_image": _cross_row(r)}
        rows.append(row)
        s, c = row["standard"], row["cross_image"]
        print(f"mR@{K_RECALL} gc {new:>4s} vs {old:<4s} std   total {s['total']:+.5f} "
              f"group {s['group']:+.5f} case {s['case']:+.5f} "
              f"[{s['case_ci'][0]:+.5f},{s['case_ci'][1]:+.5f}]")
        print(f"{'':24s} cross total {c['total']:+.5f} group {c['group']:+.5f} "
              f"case {c['case']:+.5f} [{c['case_ci'][0]:+.5f},{c['case_ci'][1]:+.5f}] "
              f"cells {c['n_eligible_cells']} within {c['frac_pairs_within_image']:.3f}", flush=True)
    return rows


def main():
    Q, _raw, y, phi, image, cal = RR.sgg_data()
    aud = ~cal
    drop = json.loads((RS.DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(np.load(RS.DDIR / "meta.npz")["pred"]), dtype=bool)
    keep[drop] = False
    dup = {"all_scored_relations": duplicate_stats(keep, np.ones(int(keep.sum()), dtype=bool)),
           "audit_half": duplicate_stats(keep, aud)}
    print(f"duplicates (all scored): {dup['all_scored_relations']['fraction_duplicated']:.4f} "
          f"of {dup['all_scored_relations']['n_relations']} relations; "
          f"audit half: {dup['audit_half']['fraction_duplicated']:.4f}")

    proper = proper_rows(Q, y, phi, image, cal)
    recall = recall_rows()

    out = {
        "n_jack": N_JACK,
        "seed": SEED,
        "alpha": ALPHA,
        "duplicates": dup,
        "audit_half_relations": int(aud.sum()),
        "proper_score_rows": proper,
        "mean_recall_rows": recall,
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
