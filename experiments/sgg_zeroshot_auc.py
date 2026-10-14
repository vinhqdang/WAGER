"""Within-cell AUC contrasts restricted to zero-shot and seen comparison blocks.

The zero-shot split (results/sgg_zeroshot_split.json) finds a case-level part of TDE's
zero-shot recall@50 gain against the logit-adjusted control la1. Hits are thresholded,
so that part may be operating-point movement. This script asks the threshold-free
question: how much of each within-cell AUC contrast comes from zero-shot comparison
blocks, and how much from seen ones?

A comparison block is (cell c, unordered label pair {y, z}) as built by wager.rank._blocks.
It is zero-shot if (c, y) or (c, z) is a zero-shot triplet (subject class, predicate,
object class absent from training, read from the benchmark list via
sgg_interval_and_diagnostics.zero_shot_mask); otherwise it is seen. The two sets partition
the blocks, so the per-block numerator and denominator sums split exactly.

For each comparison (TDE vs none, la1 vs none, TDE vs la1) and each weighting (comparison,
relation as in wager.rank._auc), the script reports:
  - the AUC change over all blocks, and restricted to zero-shot and to seen blocks;
  - each block type's weight share and the baseline AUC level on it;
  - a 95% image-cluster bootstrap interval (1,000 replicates, seed 0; the same draws as
    wager.rank.within_cell_auc_contrast, so the overall intervals are cross-checked
    against the library).

Probabilities are the stored, unrenormalised `raw` values from run_sgg_rank_robustness.sgg_data().

Run: python experiments/sgg_zeroshot_auc.py
     (set WAGER_ZS_TRIPLETS to zeroshot_triplet.pytorch if it is not at the default path)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.rank import AUC_EPS, _auc, _blocks, _logq, within_cell_auc, within_cell_auc_contrast  # noqa: E402
from run_sgg_rank_robustness import sgg_data  # noqa: E402
from run_sgg_recall_split import DDIR  # noqa: E402
import sgg_interval_and_diagnostics as D  # noqa: E402

OUT = ROOT / "results/sgg_zeroshot_auc.json"
N_BOOT = 1000
SEED = 0
TOL = 1e-9
MODELS = ("none", "TDE", "la1")
COMPARISONS = [("TDE", "none"), ("la1", "none"), ("TDE", "la1")]
WEIGHTINGS = ("comparison", "relation")
SUBSETS = ("overall", "zero_shot", "seen")
N_SUB = 151             # object classes per subject index in phi = subj * 151 + obj
N_PRED1 = 51            # predicate index range used in the triplet codes (1-indexed, < 51)


def log(msg):
    print(msg, flush=True)


def zs_cell_label(cells, labels, trip):
    """Is (cell's subject, label + 1, cell's object) a zero-shot triplet? Labels are 0-indexed."""
    subj, obj = cells // N_SUB, cells % N_SUB
    code = (subj * N_SUB + obj) * N_PRED1 + labels + 1
    tcode = (trip[:, 0] * N_SUB + trip[:, 1]) * N_PRED1 + trip[:, 2]
    return np.isin(code, tcode)


def block_sums(bl, w, weighting):
    """Per-block numerator and denominator of the within-cell AUC for element weights w.

    Same algebra as wager.rank._auc; the relation weighting scales each block by 1 / n_cell
    of its cell, exactly as _auc does. Returns arrays aligned with the blocks of bl.
    """
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
    if weighting == "comparison":
        return num, den
    n_cell = np.bincount(bl.row_cell, w, bl.n_cells)[bl.blk_cell]
    ok = n_cell > 0
    scale = np.where(ok, 1.0 / np.where(ok, n_cell, 1.0), 0.0)
    return num * scale, den * scale


def subset_stats(num, den, zs_b):
    """AUC levels and changes on all, zero-shot and seen blocks, plus each subset's weight share.

    num: dict model -> per-block numerator; den: per-block denominator (identical across models).
    """
    vals = {}
    dt = den.sum()
    masks = {"overall": np.ones(len(den), bool), "zero_shot": zs_b, "seen": ~zs_b}
    for name, mk in masks.items():
        dS = den[mk].sum()
        lev = {m: (num[m][mk].sum() / dS if dS > 0 else np.nan) for m in MODELS}
        for m in MODELS:
            vals[(name, "level", m)] = lev[m]
        vals[(name, "share")] = dS / dt
        for new, old in COMPARISONS:
            vals[(name, "change", new, old)] = lev[new] - lev[old]
    return vals


def main():
    t0 = time.perf_counter()
    Q, raw, y, phi, image, cal = sgg_data()
    n = len(y)
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    _, trip = D.zero_shot_mask(meta["subj"].astype(np.int64), meta["obj"].astype(np.int64),
                               meta["pred"].astype(np.int64))
    trip = np.asarray(trip, dtype=np.int64)
    is_zs_full, _ = D.zero_shot_mask(meta["subj"].astype(np.int64), meta["obj"].astype(np.int64),
                                     meta["pred"].astype(np.int64))
    is_zs_row = zs_cell_label(phi, y, trip)
    assert np.array_equal(is_zs_row, is_zs_full[keep]), "row zero-shot flags disagree with the mask"
    log(f"relations {n} (kept of {len(keep)}), zero-shot relations {int(is_zs_row.sum())} "
        f"({is_zs_row.mean():.4f})")

    bl = {m: _blocks(_logq(raw[m], AUC_EPS), y, phi) for m in MODELS}
    b0 = bl["none"]
    for m in MODELS[1:]:
        assert bl[m].n_blocks == b0.n_blocks
        assert np.array_equal(bl[m].blk_pair, b0.blk_pair) and np.array_equal(bl[m].blk_cell, b0.blk_cell)
    K = int(y.max()) + 1
    ue = np.unique(phi)
    bcell = ue[b0.blk_cell]
    ly, lz = b0.blk_pair // K, b0.blk_pair % K
    zs_b = zs_cell_label(bcell, ly, trip) | zs_cell_label(bcell, lz, trip)
    log(f"blocks {b0.n_blocks}: zero-shot {int(zs_b.sum())}, seen {int((~zs_b).sum())}")

    _, ginv = np.unique(image, return_inverse=True)
    ginv = ginv.reshape(-1)
    n_g = int(ginv.max()) + 1
    ones = np.ones(n)

    # ---- point estimates and identity checks
    point = {}
    for wt in WEIGHTINGS:
        sums = {m: block_sums(bl[m], ones, wt) for m in MODELS}
        den = sums["none"][1]
        for m in MODELS[1:]:
            assert np.allclose(sums[m][1], den, rtol=1e-12, atol=0), (m, wt)
        num = {m: sums[m][0] for m in MODELS}
        point[wt] = subset_stats(num, den, zs_b)
        for m in MODELS:
            lib = within_cell_auc(raw[m], y, phi, weighting=wt)
            assert abs(point[wt][("overall", "level", m)] - lib) < TOL, (wt, m)
    lib_point = {}
    for new, old in COMPARISONS:
        for wt in WEIGHTINGS:
            lib_point[(new, old, wt)] = within_cell_auc_contrast(
                raw[new], raw[old], y, phi, image, n_boot=1, weighting=wt).difference

    # ---- image-cluster bootstrap, same draws as within_cell_auc_contrast (seed 0)
    draws = {wt: {} for wt in WEIGHTINGS}
    rng = np.random.default_rng(SEED)
    t1 = time.perf_counter()
    for r in range(N_BOOT):
        w = rng.multinomial(n_g, np.full(n_g, 1.0 / n_g)).astype(float)[ginv] * ones
        for wt in WEIGHTINGS:
            sums = {m: block_sums(bl[m], w, wt) for m in MODELS}
            vals = subset_stats({m: sums[m][0] for m in MODELS}, sums["none"][1], zs_b)
            for k, v in vals.items():
                draws[wt].setdefault(k, []).append(v)
    log(f"bootstrap {N_BOOT} replicates in {time.perf_counter() - t1:.1f} s")

    def ci(wt, key):
        d = np.asarray(draws[wt][key], dtype=float)
        ok = np.isfinite(d)
        lo, hi = np.percentile(d[ok], [2.5, 97.5])
        return [float(lo), float(hi)], int((~ok).sum())

    # overall intervals must match the library's image-clustered contrast
    for new, old in COMPARISONS:
        for wt in WEIGHTINGS:
            lib = within_cell_auc_contrast(raw[new], raw[old], y, phi, image, n_boot=N_BOOT,
                                           seed=SEED, weighting=wt)
            mine, _ = ci(wt, ("overall", "change", new, old))
            assert max(abs(mine[0] - lib.ci[0]), abs(mine[1] - lib.ci[1])) < TOL, (new, old, wt, mine, lib.ci)

    # ---- assemble output
    result = {}
    checks = {}
    for wt in WEIGHTINGS:
        p = point[wt]
        pw = {}
        base = {}
        for m in MODELS:
            base[m] = {}
            for name in SUBSETS:
                c, nn = ci(wt, (name, "level", m))
                base[m][name] = {"auc": float(p[(name, "level", m)]), "ci": c, "n_nan_boot": nn}
        pw["baseline_auc"] = base
        share = {name: {"weight_share": float(p[(name, "share")]),
                        "ci_not_computed": True} for name in ("zero_shot", "seen")}
        pw["weight_share"] = share
        con = {}
        for new, old in COMPARISONS:
            key = f"{new} vs {old}"
            entry = {}
            ov_c, ov_n = ci(wt, ("overall", "change", new, old))
            overall = float(p[("overall", "change", new, old)])
            entry["overall"] = {"change": overall, "ci": ov_c, "n_nan_boot": ov_n,
                                "auc_new": float(p[("overall", "level", new)]),
                                "auc_old": float(p[("overall", "level", old)]),
                                "library_point": float(lib_point[(new, old, wt)])}
            contrib = 0.0
            for name in ("zero_shot", "seen"):
                c, nn = ci(wt, (name, "change", new, old))
                ch = float(p[(name, "change", new, old)])
                sh = float(p[(name, "share")])
                contrib += ch * sh
                entry[name] = {"change": ch, "ci": c, "n_nan_boot": nn,
                               "auc_new": float(p[(name, "level", new)]),
                               "auc_old": float(p[(name, "level", old)]),
                               "weight_share": sh,
                               "contribution_to_overall": ch * sh}
            resid = contrib - overall
            entry["decomposition_residual"] = float(resid)
            entry["library_point_residual"] = float(overall - lib_point[(new, old, wt)])
            assert abs(resid) < TOL, (key, wt, resid)
            assert abs(overall - lib_point[(new, old, wt)]) < TOL, (key, wt)
            con[key] = entry
        pw["contrasts"] = con
        result[wt] = pw

    la1_max = max(abs(result[wt]["contrasts"]["la1 vs none"]["overall"]["change"]) for wt in WEIGHTINGS)
    assert la1_max < 1e-6, la1_max
    checks["la1_vs_none_max_abs_overall_change"] = float(la1_max)
    checks["decomposition_tolerance"] = TOL
    checks["decomposition_max_residual"] = float(max(
        abs(result[wt]["contrasts"][k]["decomposition_residual"]) for wt in WEIGHTINGS for k in result[wt]["contrasts"]))
    checks["overall_bootstrap_matches_library_ci"] = True
    checks["blocks_identical_across_models"] = True

    out = {
        "definition": {
            "block": "(cell c = (subject, object) class pair, unordered label pair {y, z}) as in wager.rank._blocks",
            "zero_shot_block": "(c, y) or (c, z) is a zero-shot triplet (subject, predicate, object class absent from training)",
            "seen_block": "complement of zero_shot_block",
            "change": "AUC(new) - AUC(old) over the blocks of the subset, with num and den summed over the subset",
            "weightings": {"comparison": "n_c(y) n_c(z) per block (library default)",
                           "relation": "as comparison, each block scaled by 1 / n_c (library _auc)"},
            "interval": f"image-cluster bootstrap, {N_BOOT} replicates, seed {SEED}, 95% percentile",
            "probabilities": "raw (unrenormalised) stored probabilities from run_sgg_rank_robustness.sgg_data()",
        },
        "n_relations": n,
        "n_images": n_g,
        "n_zero_shot_relations": int(is_zs_row.sum()),
        "n_blocks": {"total": int(b0.n_blocks), "zero_shot": int(zs_b.sum()), "seen": int((~zs_b).sum())},
        "by_weighting": result,
        "checks": checks,
        "runtime_seconds": time.perf_counter() - t0,
    }
    OUT.write_text(json.dumps(out, indent=1))
    log(f"wrote {OUT.relative_to(ROOT)} in {out['runtime_seconds']:.1f} s")
    for wt in WEIGHTINGS:
        log(f"--- {wt} weighting; zero-shot weight share {result[wt]['weight_share']['zero_shot']['weight_share']:.4f}")
        for key, e in result[wt]["contrasts"].items():
            log(f"{key}: overall {e['overall']['change']:+.6f} [{e['overall']['ci'][0]:+.6f}, {e['overall']['ci'][1]:+.6f}] | "
                f"zero-shot {e['zero_shot']['change']:+.6f} [{e['zero_shot']['ci'][0]:+.6f}, {e['zero_shot']['ci'][1]:+.6f}] "
                f"share {e['zero_shot']['weight_share']:.4f} | "
                f"seen {e['seen']['change']:+.6f} [{e['seen']['ci'][0]:+.6f}, {e['seen']['ci'][1]:+.6f}] "
                f"share {e['seen']['weight_share']:.4f}")
        for m in MODELS:
            b = result[wt]["baseline_auc"][m]
            log(f"AUC {m}: overall {b['overall']['auc']:.6f}  zero-shot {b['zero_shot']['auc']:.6f} "
                f"[{b['zero_shot']['ci'][0]:.6f}, {b['zero_shot']['ci'][1]:.6f}]  seen {b['seen']['auc']:.6f}")


if __name__ == "__main__":
    main()
