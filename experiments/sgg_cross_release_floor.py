"""Empirical noise floor for comparisons between separately trained SGG models.

Three instruments, one results file (results/sgg_cross_release_floor.json):

1. Within-cell AUC change (wager.rank.within_cell_auc_contrast, through the same
   weighting wrapper as sgg_auc_label_weighting.py) under four weightings: relation,
   comparison, pair, and predicate (comparison with element weight 1/N[y]). 1,000 image-
   bootstrap replicates, seed 0. For each pair: point difference, 95% interval (2.5/97.5)
   and 90% interval (5/95) from the draws.
   The penet vs none point estimates must reproduce results/sgg_penet_audit.json to 1e-9.
2. Mean-recall split (run_sgg_recall_split.main, the same code path that
   run_sgg_penet_audit.py uses via RS.main(NEW, OLD)) for each pair. Each pair's
   results file is written by that function as results/sgg_recall_split_<new>_vs_<old>.json.
   The dlfe vs dlfe_base gc@50 split must reproduce the stored file (checked to 1e-9).
3. Background mass: per model, the mean over the identified relations of the predicate-0
   column of the stored probabilities, plus the same column after row normalisation (a
   labelled extra: the stored DLFE probabilities are not normalised).

Data: run_sgg_rank_robustness.sgg_data (relation filter, raw probabilities for AUC).

Run: python experiments/sgg_cross_release_floor.py
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
from sgg_variants import load_variant  # noqa: E402
import sgg_auc_label_weighting as AL  # noqa: E402
import run_sgg_rank_robustness as RR  # noqa: E402
import run_sgg_recall_split as RS  # noqa: E402

OUT = ROOT / "results/sgg_cross_release_floor.json"
DDIR = ROOT / "data/vg_motifs/wager_sgg"
RESULTS = ROOT / "results"
AUC_PAIRS = [("dlfe_base", "none"), ("penet", "dlfe_base"), ("penet", "none"),
             ("dlfe", "dlfe_soft")]
SPLIT_PAIRS = [("dlfe_base", "none"), ("penet", "dlfe_base"), ("dlfe", "dlfe_soft"),
               ("dlfe", "dlfe_base")]
BACKGROUND_MODELS = ["none", "TDE", "la1", "dlfe_base", "dlfe", "penet"]
EXTRA_VARIANTS = ("dlfe_base", "dlfe", "dlfe_soft", "penet")
WEIGHTINGS = ("relation", "comparison", "pair", "predicate")
T0 = time.time()


def log(m):
    print(f"[floor +{time.time() - T0:.0f}s] {m}", flush=True)


def keep_mask():
    """The relation filter of RR.sgg_data (pairs without a ground-truth box dropped)."""
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    return keep


def auc_block(raw, y, phi, image, k, pair):
    new, old = pair
    out = {}
    for wt in WEIGHTINGS:
        c = AL.contrast(raw[new], raw[old], y, phi, image, wt, k)
        d = c.draws
        lo95, hi95 = np.nanpercentile(d, [2.5, 97.5])
        lo90, hi90 = np.nanpercentile(d, [5, 95])
        out[wt] = {"auc_new": float(c.auc_new), "auc_old": float(c.auc_old),
                   "difference": float(c.difference),
                   "ci95": [float(lo95), float(hi95)], "ci90": [float(lo90), float(hi90)],
                   "n_boot": int(c.n_boot)}
        log(f"AUC {new} vs {old} {wt:10s} d {c.difference:+.6f} "
            f"ci95 [{lo95:+.6f},{hi95:+.6f}] ci90 [{lo90:+.6f},{hi90:+.6f}]")
    return out


def split_summary(new, old):
    RS.main(new, old)
    f = RESULTS / f"sgg_recall_split_{new}_vs_{old}.json"
    d = json.loads(f.read_text())
    protocols = {}
    for proto, res in d["results"].items():
        m = res["mean_recall"]
        protocols[proto] = {
            "official_mR_old": res[f"official_mR_{old}"],
            "official_mR_new": res[f"official_mR_{new}"],
            "micro_mR_eligible_old": res[f"micro_mR_eligible_{old}"],
            "micro_mR_eligible_new": res[f"micro_mR_eligible_{new}"],
            "total": m["total"], "group": m["group"], "case": m["case"],
            "case_ci": m["case_ci"], "group_ci": m["group_ci"],
            "share": m["case"] / m["total"] if m["total"] else None,
        }
    return {"file": str(f.relative_to(ROOT)), "n_eligible": d["n_eligible"],
            "coverage": d["coverage"], "protocols": protocols}


def background_block(keep):
    out = {}
    for v in BACKGROUND_MODELS:
        p = load_variant(v)["probs"][keep].astype(np.float64)
        rows = p.sum(1)
        out[v] = {"mean_stored_p0": float(p[:, 0].mean()),
                  "mean_row_sum": float(rows.mean()),
                  "mean_normalised_p0": float((p[:, 0] / rows).mean())}
        log(f"background {v:10s} stored p0 {out[v]['mean_stored_p0']:.6f} "
            f"row sum {out[v]['mean_row_sum']:.4f} normalised p0 "
            f"{out[v]['mean_normalised_p0']:.6f}")
    return out


def main():
    keep = keep_mask()
    Q, raw, y, phi, image, cal = RR.sgg_data(extra=EXTRA_VARIANTS)
    k = raw["none"].shape[1]
    log(f"relations {len(y)}, classes {k}, bootstrap {AL.N_BOOT}, seed {AL.SEED}")
    out = {"n_boot": AL.N_BOOT, "seed": AL.SEED, "weightings": AL.WEIGHTINGS,
           "n_relations": int(len(y)), "runtime_seconds": {}}

    t = time.time()
    out["auc_change"] = {f"{n} vs {o}": auc_block(raw, y, phi, image, k, (n, o))
                         for n, o in AUC_PAIRS}
    out["runtime_seconds"]["auc_change"] = round(time.time() - t, 1)

    penet_ref = json.loads((RESULTS / "sgg_penet_audit.json").read_text())["auc"]
    checks = {}
    for wt in ("relation", "comparison"):
        mine = out["auc_change"]["penet vs none"][wt]["difference"]
        ref = penet_ref[wt]["difference"]
        checks[f"penet_vs_none_{wt}_difference_abs_diff"] = abs(mine - ref)
        assert abs(mine - ref) < 1e-9, f"penet vs none {wt}: {mine} != {ref}"
    log("penet vs none point estimates reproduce sgg_penet_audit.json (1e-9)")

    t = time.time()
    # RS.main overwrites results/sgg_recall_split_dlfe_vs_dlfe_base.json: read the stored
    # file first so the reproduction check compares against what was there before the run
    stored_dlfe = json.loads((RESULTS / "sgg_recall_split_dlfe_vs_dlfe_base.json").read_text())
    stored_gc50 = stored_dlfe["results"]["gc@50"]["mean_recall"]
    split = {}
    for new, old in SPLIT_PAIRS:
        split[f"{new} vs {old}"] = split_summary(new, old)
        g = split[f"{new} vs {old}"]["protocols"]["gc@50"]
        log(f"split {new} vs {old} gc@50: total {g['total']:+.6f} = group {g['group']:+.6f} "
            f"+ case {g['case']:+.6f} [{g['case_ci'][0]:+.6f},{g['case_ci'][1]:+.6f}]")
    out["mean_recall_split"] = split
    out["runtime_seconds"]["mean_recall_split"] = round(time.time() - t, 1)

    mine = out["mean_recall_split"]["dlfe vs dlfe_base"]["protocols"]["gc@50"]
    for key in ("total", "group", "case"):
        checks[f"dlfe_vs_dlfe_base_gc50_{key}_abs_diff_from_stored"] = abs(
            mine[key] - stored_gc50[key])
        assert abs(mine[key] - stored_gc50[key]) < 1e-9, f"dlfe split {key} differs"
    log("dlfe vs dlfe_base gc@50 split reproduces the stored file (1e-9)")
    checks["dlfe_vs_dlfe_soft_auc_difference"] = {
        wt: out["auc_change"]["dlfe vs dlfe_soft"][wt]["difference"] for wt in WEIGHTINGS}
    out["checks"] = checks
    out["background_mass"] = background_block(keep)
    out["runtime_seconds"]["total"] = round(time.time() - T0, 1)
    OUT.write_text(json.dumps(out, indent=1))
    log(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
