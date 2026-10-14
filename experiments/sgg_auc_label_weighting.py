"""Within-cell AUC change under weightings aligned with mean recall.

The within-cell AUC of run_sgg_rank_robustness.py weights each relation by its cell and
label pair. Mean recall instead gives every predicate equal total weight. This script
asks whether TDE's (and the other comparisons') within-cell ranking change depends on
that choice. Four weightings:

  comparison  library default, n_c(y) n_c(z) per cell and label pair
  relation    library relation weighting, n_c(y) n_c(z) / n_c
  pair        library pair weighting: each unordered label pair equal, cells by n_c(y) n_c(z)
  predicate   comparison weighting with element weight 1/N[y], so each predicate's
              relations sum to weight 1 (mean recall's footing)

Outputs, in results/sgg_auc_label_weighting.json:
  reference       geometry-vs-class AUC gain on the real-pixel study (all relations) under
                  each weighting; equivalence margins are fractions of it
  auc             within-cell AUC change per comparison and weighting: 95% and 90% image
                  bootstrap percentile intervals, the largest change a 90% interval
                  excludes, and TOST verdicts
  weight_share    each predicate-tier pair's share of the total weight under each weighting
  tier_pair_predicate  TDE vs none, predicate weighting: the AUC change by predicate-tier
                  pair with its 95% interval and weight share

Run: python experiments/sgg_auc_label_weighting.py
     WAGER_N_BOOT=20 python experiments/sgg_auc_label_weighting.py   (quick check)
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.rank import AUC_EPS, _blocks, within_cell_auc_contrast  # noqa: E402
from sgg_equivalence import verdicts  # noqa: E402
import run_sgg_rank_robustness as RR  # noqa: E402

RES = ROOT / "results"
OUT = RES / "sgg_auc_label_weighting.json"
N_BOOT = int(os.environ.get("WAGER_N_BOOT", "1000"))
SEED = 0
COMPARISONS = (("TDE", "none"), ("la1", "none"), ("TDE", "la1"),
               ("ietrans", "none"), ("dlfe", "dlfe_base"))
REF_PAIR = ("MLP-SPATIAL-S", "MLP-CLASS-S")
WEIGHTINGS = {
    "comparison": "library comparison weighting, n_c(y) n_c(z) per cell and label pair",
    "relation": "library relation weighting, n_c(y) n_c(z) / n_c",
    "pair": "library pair weighting, each unordered label pair equal, cells by n_c(y) n_c(z)",
    "predicate": "comparison weighting with element weight 1/N[y], so each predicate's "
                 "relations sum to 1",
}
TIER_NAMES = {0: "head-head", 1: "head-body", 2: "head-tail",
              4: "body-body", 5: "body-tail", 8: "tail-tail"}


def weighting_args(name, y, k):
    """Library weighting and element weights for one of the four weightings."""
    if name == "predicate":
        N = np.bincount(y, minlength=k)
        return "comparison", 1.0 / N[y]
    return name, None


def contrast(q_new, q_old, y, phi, groups, name, k):
    lib, w = weighting_args(name, y, k)
    return within_cell_auc_contrast(q_new, q_old, y, phi, groups, n_boot=N_BOOT,
                                    alpha=0.05, seed=SEED, weighting=lib, weights=w)


def per_block(bl, w):
    """Per-block weighted numerator and denominator, as _auc computes them."""
    we = w[bl.elem]
    wn = np.where(bl.pos, 0.0, we)
    wp = np.where(bl.pos, we, 0.0)
    cum = np.cumsum(wn)
    tie_neg = np.bincount(bl.tie, wn)
    tie_end = np.cumsum(np.bincount(bl.tie))
    below_tie = cum[tie_end - 1] - tie_neg
    blk_start = np.r_[0, np.flatnonzero(np.diff(bl.block)) + 1]
    below = below_tie[bl.tie] - np.r_[0.0, cum][blk_start][bl.block]
    num = np.bincount(bl.block, wp * (below + 0.5 * tie_neg[bl.tie]), bl.n_blocks)
    den = np.bincount(bl.block, wp, bl.n_blocks) * np.bincount(bl.block, wn, bl.n_blocks)
    return num, den


def block_tier_pair(bl, y, tier_of):
    """Tier pair code (a * 3 + b, a <= b) of each block, from its two labels."""
    ylab = y[bl.elem]
    pos_lab = np.zeros(bl.n_blocks, dtype=np.int64)
    neg_lab = np.zeros(bl.n_blocks, dtype=np.int64)
    pos_lab[bl.block[bl.pos]] = ylab[bl.pos]
    neg_lab[bl.block[~bl.pos]] = ylab[~bl.pos]
    a, b = tier_of[pos_lab], tier_of[neg_lab]
    return np.where(a <= b, a * 3 + b, b * 3 + a)


def share_by_tier(bl, name, y, k, tier_of):
    """Each tier pair's share of the total weight under one weighting (point estimate)."""
    lib, w = weighting_args(name, y, k)
    w = np.ones(len(y)) if w is None else w
    _, den = per_block(bl, w)
    if lib == "relation":
        n_cell = np.bincount(bl.row_cell, w, bl.n_cells)[bl.blk_cell]
        den = den / n_cell
    elif lib == "pair":
        _, pidx = np.unique(bl.blk_pair, return_inverse=True)
        den_p = np.bincount(pidx, den)
        den = den / den_p[pidx] / len(den_p)           # each pair 1/(#pairs), split by den
    tp = block_tier_pair(bl, y, tier_of)
    total = den.sum()
    return {TIER_NAMES[g]: float(den[tp == g].sum() / total) for g in TIER_NAMES}


def tier_pair_predicate(q_new, q_old, y, phi, image, tier_of, w):
    """AUC change by tier pair under element weights w, with the image bootstrap of
    run_sgg_rank_robustness.tier_pair_auc (same seed and draw order as the library)."""
    bn = _blocks(np.log(np.maximum(q_new, AUC_EPS)), y, phi)
    bo = _blocks(np.log(np.maximum(q_old, AUC_EPS)), y, phi)
    tp = block_tier_pair(bn, y, tier_of)
    assert np.array_equal(tp, block_tier_pair(bo, y, tier_of))

    def stats(wt):
        nn, dn = per_block(bn, wt)
        no, _ = per_block(bo, wt)
        out = {}
        for g in TIER_NAMES:
            m = tp == g
            out[g] = (float(nn[m].sum() - no[m].sum()), float(dn[m].sum()))
        out["all"] = (float(nn.sum() - no.sum()), float(dn.sum()))
        return out

    point = stats(w)
    _, ginv = np.unique(image, return_inverse=True)
    n_g = ginv.max() + 1
    rng = np.random.default_rng(SEED)
    draws = {g: np.empty(N_BOOT) for g in TIER_NAMES}
    for r in range(N_BOOT):
        wt = rng.multinomial(n_g, np.full(n_g, 1.0 / n_g)).astype(float)[ginv] * w
        st = stats(wt)
        for g in TIER_NAMES:
            draws[g][r] = (st[g][0] / st[g][1] if st[g][1] > 0 else float("nan"))
    total_den = point["all"][1]
    res = {}
    for g, name in TIER_NAMES.items():
        num, den = point[g]
        lo, hi = np.nanpercentile(draws[g], [2.5, 97.5])
        res[name] = {"difference": num / den, "ci95": [float(lo), float(hi)],
                     "weight_share": den / total_den}
        print(f"tier pair TDE vs none predicate {name:10s} d {num / den:+.5f} "
              f"ci95 [{lo:+.5f},{hi:+.5f}] w={den / total_den:.4f}", flush=True)
    return res, point["all"][0] / total_den


def main():
    t0 = time.time()
    print(f"N_BOOT={N_BOOT} seed={SEED}", flush=True)
    Q, raw, y, phi, image, cal = RR.sgg_data(extra=("dlfe", "dlfe_base"))
    kS = raw["none"].shape[1]
    counts = np.asarray(json.loads((RR.DDIR / "summary.json").read_text())
                        ["train_predicate_counts"])[1:]
    tier_of = np.where(counts > RR.HEAD_MIN, 0, np.where(counts < RR.TAIL_MAX, 2, 1))

    # reference: the real-pixel geometry-vs-class gain under each weighting
    P, py, pphi, pimage, pcal = RR.pixel_data()
    kP = P[REF_PAIR[0]].shape[1]
    reference = {}
    for wt in WEIGHTINGS:
        c = contrast(P[REF_PAIR[0]], P[REF_PAIR[1]], py, pphi, pimage, wt, kP)
        reference[wt] = float(c.difference)
        print(f"reference pixel {REF_PAIR[0]} vs {REF_PAIR[1]} {wt:10s} "
              f"d {c.difference:+.5f}  ({time.time() - t0:.0f}s)", flush=True)

    # within-cell AUC change on the SGG data, all relations
    auc = {}
    for new, old in COMPARISONS:
        key = f"{new} vs {old}"
        auc[key] = {}
        for wt in WEIGHTINGS:
            c = contrast(raw[new], raw[old], y, phi, image, wt, kS)
            d = c.draws
            lo95, hi95 = np.nanpercentile(d, [2.5, 97.5])
            lo90, hi90 = np.nanpercentile(d, [5, 95])
            largest = float(max(abs(lo90), abs(hi90)))
            b = {"auc_new": float(c.auc_new), "auc_old": float(c.auc_old),
                 "difference": float(c.difference),
                 "ci95": [float(lo95), float(hi95)], "ci90": [float(lo90), float(hi90)],
                 "largest_change_excluded": largest,
                 "reference_gain": reference[wt],
                 "tost": verdicts(float(lo90), float(hi90), reference[wt])}
            auc[key][wt] = b
            print(f"AUC {key:14s} {wt:10s} d {b['difference']:+.5f} "
                  f"ci95 [{lo95:+.5f},{hi95:+.5f}] ci90 [{lo90:+.5f},{hi90:+.5f}] "
                  f"largest {largest:.5f} ref {reference[wt]:.5f} "
                  + " ".join(f"{k} {v['equivalent']}" for k, v in b["tost"].items()),
                  flush=True)

    # weight shares by predicate-tier pair (TDE-vs-none blocks; the blocks depend only on
    # y and phi, so the same shares hold for any model pair)
    bl0 = _blocks(np.log(np.maximum(raw["none"], AUC_EPS)), y, phi)
    weight_share = {}
    for wt in WEIGHTINGS:
        weight_share[wt] = share_by_tier(bl0, wt, y, kS, tier_of)
        print("share " + f"{wt:10s} " + "  ".join(
            f"{k} {v:.4f}" for k, v in weight_share[wt].items()), flush=True)

    # AUC change by predicate-tier pair under predicate weighting
    _, w_pred = weighting_args("predicate", y, kS)
    tpp, overall = tier_pair_predicate(raw["TDE"], raw["none"], y, phi, image, tier_of, w_pred)
    assert abs(overall - auc["TDE vs none"]["predicate"]["difference"]) < 1e-9
    print(f"check: tier-pair predicate total {overall:+.5f} equals library predicate "
          f"contrast {auc['TDE vs none']['predicate']['difference']:+.5f}", flush=True)

    out = {"n_boot": N_BOOT, "seed": SEED, "weightings": WEIGHTINGS,
           "reference": reference, "auc": auc, "weight_share": weight_share,
           "tier_pair_predicate": {"TDE vs none": tpp}}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}  total {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
