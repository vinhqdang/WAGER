"""Zero-shot comparisons for PE-Net, DLFE and IETrans against their reference models.

Reuses the estimators of sgg_zeroshot_split.py (micro-pooled zR@50, exact group / case /
unidentified-singleton split) and sgg_zeroshot_auc.py (within-cell AUC on zero-shot and seen
comparison blocks, image-cluster bootstrap, 1,000 replicates, seed 0). Nothing in those
files is modified; this script only calls their functions with other variants.

Pairs: penet vs none, penet vs dlfe_base, dlfe vs dlfe_base, dlfe vs dlfe_soft, ietrans vs none.

Part 1 (micro-pooled split, all 183,642 relations, as sgg_zeroshot_split.py):
  direct micro-pooled zR@50 change, per-image zR@50 change (official averaging), exact
  group + case + unidentified-singleton identity, image-clustered Hajek intervals, and the
  raw zero-shot gain's case-level share (case / direct change).
Part 2 (within-cell AUC, rows with missing pairs dropped, as sgg_zeroshot_auc.py):
  overall / zero-shot-block / seen-block AUC change under comparison and relation weightings,
  image-cluster bootstrap intervals (1,000 replicates, seed 0), and the zero-shot minus seen
  difference of changes. The three pairs that sgg_zeroshot_auc.py already stores (TDE vs none,
  la1 vs none, TDE vs la1) are recomputed in the same run and checked against that file.

Validation: per-image zR@50 for none, TDE, penet (printed 0.1713), dlfe and dlfe_base
(printed values) are checked. The IETrans summary is read and reported, including which
training split defines its unseen set.

Writes results/sgg_zeroshot_more.json.
Run: python experiments/sgg_zeroshot_more.py   (Part 2 takes tens of minutes; run in background)
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.rank import AUC_EPS, _blocks, _logq, within_cell_auc, within_cell_auc_contrast  # noqa: E402
from run_sgg_rank_robustness import sgg_data  # noqa: E402
from run_sgg_recall_split import DDIR, N_OBJ  # noqa: E402
import sgg_interval_and_diagnostics as D  # noqa: E402
import sgg_zeroshot_split as S  # noqa: E402
import sgg_zeroshot_auc as A  # noqa: E402

OUT = ROOT / "results/sgg_zeroshot_more.json"
N_BOOT = 1000
SEED = 0
TOL = 1e-9
PAIRS = [("penet", "none"), ("penet", "dlfe_base"), ("dlfe", "dlfe_base"), ("dlfe", "dlfe_soft"),
         ("ietrans", "none")]
STORED_PAIRS = [("TDE", "none"), ("la1", "none"), ("TDE", "la1")]    # reproduced from sgg_zeroshot_auc.json
EXTRA = ("penet", "dlfe", "dlfe_base", "dlfe_soft")
MODELS = ("none", "TDE", "la1", "ietrans") + EXTRA
WEIGHTINGS = ("comparison", "relation")
PRINTED_PENET_ZR50 = 0.1713          # PE-Net evaluator, results/... (wager_penet/summary.json)
PRINTED_TOL = 5e-5                   # printed to 4 decimals


def log(msg):
    print(msg, flush=True)


# ----------------------------------------------------------------------------- part 1

def part1():
    t0 = time.perf_counter()
    meta = np.load(DDIR / "meta.npz")
    y = meta["pred"].astype(np.int64)
    subj = meta["subj"].astype(np.int64)
    obj = meta["obj"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    phi = subj * N_OBJ + obj
    n = len(y)
    ix = np.arange(n)

    is_zs, trip = D.zero_shot_mask(subj, obj, y)
    Zm = S.zero_shot_matrix(subj, obj, trip)
    assert np.array_equal(Zm[ix, y], is_zs)
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    elig = cnt[inv.reshape(-1)] >= 2
    n_e = int(elig.sum())
    n_zs = int(is_zs.sum())
    log(f"part 1: relations {n}, zero-shot {n_zs}, eligible {n_e}, triplets in list {len(trip)}")

    out = {}
    for new, old in PAIRS:
        t1 = time.perf_counter()
        r = S.compare(new, old, y, phi, image, elig, is_zs, Zm, n_zs, n_e)
        r.pop("matches_diagnostics_file", None)
        own_n = D.hits(new)[ix, y]
        own_o = D.hits(old)[ix, y]
        zn = D.zr_stats(own_n, is_zs, image)
        zo = D.zr_stats(own_o, is_zs, image)
        r["zR50_new_per_image"] = zn["per_image"]
        r["zR50_old_per_image"] = zo["per_image"]
        r["zR50_change_per_image"] = zn["per_image"] - zo["per_image"]
        r["case_share_of_raw_gain"] = r["case_share_of_direct"]
        r["n_zs_relations"] = n_zs
        r["runtime_seconds"] = time.perf_counter() - t1
        out[f"{new} vs {old}"] = r
        log(f"  {new} vs {old}: zR@50 micro {r['zR50_old_micro']:.6f} -> {r['zR50_new_micro']:.6f} "
            f"(change {r['direct_change']:+.6f}); per-image {zo['per_image']:.6f} -> {zn['per_image']:.6f} "
            f"({r['zR50_change_per_image']:+.6f}); group {r['group_level']:+.6f} "
            f"case {r['case_level']:+.6f} [{r['case_level_ci_image_clustered'][0]:+.6f}, "
            f"{r['case_level_ci_image_clustered'][1]:+.6f}] singleton {r['unidentified_singleton_change']:+.6f}; "
            f"case share of raw gain {r['case_share_of_raw_gain']:.4f}; residual {r['identity_residual']:.1e}")

    # validation of per-image zR@50 against the official printed / stored values
    per_image = {}
    for v in ("none", "TDE", "penet", "dlfe", "dlfe_base"):
        per_image[v] = D.zr_stats(D.hits(v)[ix, y], is_zs, image)["per_image"]
    dl = json.loads((ROOT / "results/dlfe_official_recall.json").read_text())["models"]

    def printed(key):
        line = [ln for ln in dl[key]["printed_lines"] if re.search(r"(?<![\w-])zR @ 50: ", ln)]
        return float(re.search(r"(?<![\w-])zR @ 50: ([0-9.]+)", line[0]).group(1))
    audit = json.loads((ROOT / "results/sgg_audit_motifs.json").read_text())["recalls"]
    val = {
        "none": {"replayed": per_image["none"], "reference": audit["MOTIFS"]["predcls_zeroshot_recall@50"],
                 "tolerance": TOL, "source": "results/sgg_audit_motifs.json (full precision)"},
        "TDE": {"replayed": per_image["TDE"], "reference": audit["MOTIFS-TDE"]["predcls_zeroshot_recall@50"],
                "tolerance": TOL, "source": "results/sgg_audit_motifs.json (full precision)"},
        "penet": {"replayed": per_image["penet"], "reference": PRINTED_PENET_ZR50,
                  "tolerance": PRINTED_TOL,
                  "source": "data/vg_motifs/wager_penet/summary.json evaluator_printed zR @ 50 (4 decimals)"},
        "dlfe": {"replayed": per_image["dlfe"], "reference": printed("dlfe"),
                 "tolerance": PRINTED_TOL, "source": "results/dlfe_official_recall.json (printed, 4 decimals)"},
        "dlfe_base": {"replayed": per_image["dlfe_base"], "reference": printed("dlfe_base"),
                      "tolerance": PRINTED_TOL, "source": "results/dlfe_official_recall.json (printed, 4 decimals)"},
    }
    for v, e in val.items():
        e["abs_diff"] = abs(e["replayed"] - e["reference"])
        e["matches"] = bool(e["abs_diff"] < e["tolerance"])
        log(f"  validate zR@50 per-image {v}: replayed {e['replayed']:.6f} reference {e['reference']:.6f} "
            f"{'OK' if e['matches'] else 'MISMATCH'}")
    return {
        "n_relations": n, "n_zero_shot_relations": n_zs, "n_eligible_relations": n_e,
        "n_zero_shot_triplets": int(len(trip)),
        "pairs": out, "validation_per_image_zR50": val,
        "runtime_seconds": time.perf_counter() - t0,
    }, (y, subj, obj, image, phi, is_zs, trip, elig)


# ----------------------------------------------------------------------------- part 2

def subset_stats(num, den, zs_b, pairs):
    """As sgg_zeroshot_auc.subset_stats, for the given models and pairs."""
    models = sorted({m for p in pairs for m in p})
    vals = {}
    dt = den.sum()
    masks = {"overall": np.ones(len(den), bool), "zero_shot": zs_b, "seen": ~zs_b}
    for name, mk in masks.items():
        dS = den[mk].sum()
        lev = {m: (num[m][mk].sum() / dS if dS > 0 else np.nan) for m in models}
        for m in models:
            vals[(name, "level", m)] = lev[m]
        vals[(name, "share")] = dS / dt
        for new, old in pairs:
            vals[(name, "change", new, old)] = lev[new] - lev[old]
    return vals


def part2(y, subj, obj, image, phi, trip_full):
    t0 = time.perf_counter()
    Q, raw, y2, phi2, image2, cal = sgg_data(extra=EXTRA)
    n = len(y2)
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    assert n == int(keep.sum())
    assert np.array_equal(y2, meta["pred"].astype(np.int64)[keep] - 1)
    assert np.array_equal(phi2, (meta["subj"].astype(np.int64) * 151 + meta["obj"].astype(np.int64))[keep])
    assert np.array_equal(image2, meta["image_index"].astype(np.int64)[keep])
    trip = np.asarray(trip_full, dtype=np.int64)
    is_zs_row = A.zs_cell_label(phi2, y2, trip)
    is_zs_full, _ = D.zero_shot_mask(meta["subj"].astype(np.int64), meta["obj"].astype(np.int64),
                                     meta["pred"].astype(np.int64))
    assert np.array_equal(is_zs_row, is_zs_full[keep]), "row zero-shot flags disagree with the mask"
    y, phi, image = y2, phi2, image2
    log(f"part 2: kept relations {n}, zero-shot {int(is_zs_row.sum())}")

    bl = {m: _blocks(_logq(raw[m], AUC_EPS), y, phi) for m in MODELS}
    b0 = bl["none"]
    for m in MODELS[1:]:
        assert bl[m].n_blocks == b0.n_blocks
        assert np.array_equal(bl[m].blk_pair, b0.blk_pair) and np.array_equal(bl[m].blk_cell, b0.blk_cell)
    K = int(y.max()) + 1
    ue = np.unique(phi)
    bcell = ue[b0.blk_cell]
    ly, lz = b0.blk_pair // K, b0.blk_pair % K
    zs_b = A.zs_cell_label(bcell, ly, trip) | A.zs_cell_label(bcell, lz, trip)
    log(f"  blocks {b0.n_blocks}: zero-shot {int(zs_b.sum())}, seen {int((~zs_b).sum())}")

    all_pairs = PAIRS + STORED_PAIRS
    _, ginv = np.unique(image, return_inverse=True)
    ginv = ginv.reshape(-1)
    n_g = int(ginv.max()) + 1
    ones = np.ones(n)

    point = {}
    for wt in WEIGHTINGS:
        sums = {m: A.block_sums(bl[m], ones, wt) for m in MODELS}
        den = sums["none"][1]
        for m in MODELS[1:]:
            assert np.allclose(sums[m][1], den, rtol=1e-12, atol=0), (m, wt)
        num = {m: sums[m][0] for m in MODELS}
        point[wt] = subset_stats(num, den, zs_b, all_pairs)
        for m in MODELS:
            lib = within_cell_auc(raw[m], y, phi, weighting=wt)
            assert abs(point[wt][("overall", "level", m)] - lib) < TOL, (wt, m)
    lib_point = {(new, old, wt): within_cell_auc_contrast(raw[new], raw[old], y, phi, image, n_boot=1,
                                                          weighting=wt).difference
                 for new, old in all_pairs for wt in WEIGHTINGS}
    log("  point estimates done")

    draws = {wt: {} for wt in WEIGHTINGS}
    rng = np.random.default_rng(SEED)
    t1 = time.perf_counter()
    for r in range(N_BOOT):
        w = rng.multinomial(n_g, np.full(n_g, 1.0 / n_g)).astype(float)[ginv] * ones
        for wt in WEIGHTINGS:
            sums = {m: A.block_sums(bl[m], w, wt) for m in MODELS}
            vals = subset_stats({m: sums[m][0] for m in MODELS}, sums["none"][1], zs_b, all_pairs)
            for k, v in vals.items():
                draws[wt].setdefault(k, []).append(v)
        if (r + 1) % 100 == 0:
            log(f"    bootstrap {r + 1}/{N_BOOT} ({(time.perf_counter() - t1) / 60:.1f} min)")
    log(f"  bootstrap done in {(time.perf_counter() - t1) / 60:.1f} min")

    def ci_of(d):
        d = np.asarray(d, dtype=float)
        ok = np.isfinite(d)
        lo, hi = np.percentile(d[ok], [2.5, 97.5])
        return [float(lo), float(hi)], int((~ok).sum())

    def ci(wt, key):
        return ci_of(draws[wt][key])

    result = {}
    for wt in WEIGHTINGS:
        p = point[wt]
        con = {}
        for new, old in all_pairs:
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
                               "weight_share": sh, "contribution_to_overall": ch * sh}
            zs_d = np.asarray(draws[wt][("zero_shot", "change", new, old)], float)
            se_d = np.asarray(draws[wt][("seen", "change", new, old)], float)
            ok = np.isfinite(zs_d) & np.isfinite(se_d)
            lo, hi = np.percentile((zs_d - se_d)[ok], [2.5, 97.5])
            entry["zero_shot_minus_seen"] = {
                "difference": entry["zero_shot"]["change"] - entry["seen"]["change"],
                "ci": [float(lo), float(hi)]}
            entry["decomposition_residual"] = float(contrib - overall)
            entry["library_point_residual"] = float(overall - lib_point[(new, old, wt)])
            assert abs(contrib - overall) < TOL, (key, wt)
            assert abs(overall - lib_point[(new, old, wt)]) < TOL, (key, wt)
            con[key] = entry
        base = {m: {name: {"auc": float(p[(name, "level", m)]),
                           "ci": ci(wt, (name, "level", m))[0]} for name in ("overall", "zero_shot", "seen")}
                for m in MODELS}
        result[wt] = {"contrasts": con, "baseline_auc": base,
                      "weight_share": {"zero_shot": float(p[("zero_shot", "share")]),
                                       "seen": float(p[("seen", "share")])}}

    # reproduction of the stored sgg_zeroshot_auc.json for TDE vs none, la1 vs none, TDE vs la1
    stored = json.loads((ROOT / "results/sgg_zeroshot_auc.json").read_text())["by_weighting"]
    repro = {}
    worst = 0.0
    for wt in WEIGHTINGS:
        for new, old in STORED_PAIRS:
            key = f"{new} vs {old}"
            mine = result[wt]["contrasts"][key]
            ref = stored[wt]["contrasts"][key]
            diffs = {}
            for sub in ("overall", "zero_shot", "seen"):
                diffs[f"{sub}_change"] = abs(mine[sub]["change"] - ref[sub]["change"])
                diffs[f"{sub}_ci_lo"] = abs(mine[sub]["ci"][0] - ref[sub]["ci"][0])
                diffs[f"{sub}_ci_hi"] = abs(mine[sub]["ci"][1] - ref[sub]["ci"][1])
            diffs["zs_weight_share"] = abs(mine["zero_shot"]["weight_share"] - ref["zero_shot"]["weight_share"])
            repro[f"{wt} {key}"] = {k: float(v) for k, v in diffs.items()}
            worst = max(worst, max(diffs.values()))
    log(f"  reproduction of sgg_zeroshot_auc.json: max abs difference {worst:.2e}")
    assert worst < 1e-9, worst

    return {
        "definition": {
            "block": "(cell, unordered label pair) as wager.rank._blocks; zero-shot block if either label is zero-shot in its cell",
            "change": "AUC(new) - AUC(old) over the subset's blocks",
            "zero_shot_minus_seen": "change on zero-shot blocks minus change on seen blocks (paired within each bootstrap replicate)",
            "interval": f"image-cluster bootstrap, {N_BOOT} replicates, seed {SEED}, 95% percentile",
            "probabilities": "raw (unrenormalised) stored probabilities from sgg_data(); rows with missing pairs dropped",
        },
        "n_relations_kept": int(n), "n_images": n_g,
        "n_zero_shot_relations": int(is_zs_row.sum()),
        "n_blocks": {"total": int(b0.n_blocks), "zero_shot": int(zs_b.sum()), "seen": int((~zs_b).sum())},
        "by_weighting": result,
        "reproduction_of_sgg_zeroshot_auc": {"max_abs_difference": float(worst), "entries": repro},
        "runtime_seconds": time.perf_counter() - t0,
    }


# ----------------------------------------------------------------------------- IETrans

def ietrans_notes():
    std = json.loads((DDIR / "summary.json").read_text())
    ie = json.loads((ROOT / "data/vg_motifs/wager_ietrans/summary.json").read_text())
    ier = json.loads((ROOT / "data/vg_motifs/wager_ietrans_raw/summary.json").read_text())
    std_counts = np.asarray(std["train_predicate_counts"])
    ie_counts = np.asarray(ie["train_predicate_counts"])
    ier_counts = np.asarray(ier["train_predicate_counts"])
    return {
        "stored_fields_wager_ietrans_summary": {
            "standard_relations": ie["standard_relations"],
            "ietrans_relations": ie["ietrans_relations"],
            "duplicates_restored": ie["duplicates_restored"],
            "unused_ietrans_rows": ie["unused_ietrans_rows"],
            "keys_with_several_ietrans_rows": ie["keys_with_several_ietrans_rows"],
            "rank_mismatch_within_shared_keys": ie["rank_mismatch_within_shared_keys"],
            "max_prob_difference_within_shared_keys": ie["max_prob_difference_within_shared_keys"],
        },
        "train_predicate_counts_in_wager_ietrans_summary_equal_wager_sgg": bool(np.array_equal(ie_counts, std_counts)),
        "train_predicate_counts_in_wager_ietrans_raw_summary": {
            "equal_to_wager_sgg": bool(np.array_equal(ier_counts, std_counts)),
            "predicates_differing_from_wager_sgg": int(np.sum(ier_counts != std_counts)),
            "total_train_count_wager_sgg": int(std_counts.sum()),
            "total_train_count_ietrans_raw": int(ier_counts.sum()),
            "example_predicate_1_counts": {"wager_sgg": int(std_counts[1]), "ietrans_raw": int(ier_counts[1])},
        },
        "unseen_definition_used": (
            "benchmark zero-shot list data/vg_motifs/zeroshot_triplet.pytorch (Scene-Graph-Benchmark list), "
            "which is fixed by the standard VG training split. The stored IETrans summaries hold predicate "
            "counts only, not training triplets, so the zero-shot set cannot be re-derived from IETrans's own "
            "relabelled training subset here."),
        "note": ie.get("note", ""),
    }


def main():
    t0 = time.perf_counter()
    part1_out, shared = part1()
    p2 = part2(*shared[:5], shared[6])
    out = {
        "definition": {
            "zero_shot": "(subject class, predicate, object class) in the benchmark zero-shot list",
            "hits": "graph-constrained recall@50 (gc@50) for part 1 and the AUC is on the stored probabilities",
            "split": "as sgg_zeroshot_split.py: exact group/case split of the identified micro-pooled change; "
                     "singleton-cell zero-shot relations are a separate unidentified remainder",
        },
        "part1_zero_shot_split": part1_out,
        "part2_within_cell_auc": p2,
        "ietrans": ietrans_notes(),
        "runtime_seconds": time.perf_counter() - t0,
    }
    OUT.write_text(json.dumps(out, indent=1))
    log(f"wrote {OUT.relative_to(ROOT)} in {out['runtime_seconds'] / 60:.1f} min")


if __name__ == "__main__":
    main()
