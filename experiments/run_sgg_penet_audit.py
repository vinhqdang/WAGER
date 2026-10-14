"""Audit of the released PE-Net PredCls checkpoint (Zheng et al., CVPR 2023, "Prototype-
based Embedding Network for Scene Graph Generation") against the reference MOTIFS
baseline of the TDE release ("none" in data/vg_motifs/wager_sgg).

The comparison is across architectures: PE-Net replaces the MOTIFS predicate head by
prototype embeddings with a cosine predicate classifier on the Scene-Graph-Benchmark
relation head, and it was trained separately from the TDE release's MOTIFS checkpoint.
The difference is therefore a difference between two trained systems, not an
intervention on one model.

The same instruments as run_sgg_dlfe_audit.py, with the code paths those audits use:

1. the mean-recall split of the change under the six official protocols (graph-
   constrained and no-graph-constraint recall at K = 20, 50, 100), via
   run_sgg_recall_split.main, which also writes results/sgg_recall_split_penet_vs_none.json;
2. the within-cell AUC change under the four weightings of sgg_auc_label_weighting.py
   (comparison, relation, pair, predicate), with 1,000 image-bootstrap replicates and
   seed 0, AUC clipping floor 1e-300, the pixel-study reference gain and the TOST verdicts
   of that script, the weight shares, and the tier-pair breakdown under predicate
   weighting;
3. the matched split of the proper-score gain under one temperature per model and
   under temperature plus a per-class bias (run_sgg_rank_robustness.recalibration_rows);
4. top-1 predicate accuracy.

Every probability used by the AUC paths must be strictly positive; the run stops if not.

Run: python experiments/run_sgg_penet_audit.py
Writes results/sgg_penet_audit.json (and results/sgg_recall_split_penet_vs_none.json).
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
from wager.rank import AUC_EPS, _blocks  # noqa: E402
from sgg_variants import load_variant  # noqa: E402
from sgg_equivalence import verdicts  # noqa: E402
import sgg_auc_label_weighting as AL  # noqa: E402
import run_sgg_rank_robustness as RR  # noqa: E402
import run_sgg_recall_split as RS  # noqa: E402

OUT = ROOT / "results/sgg_penet_audit.json"
DDIR = ROOT / "data/vg_motifs/wager_sgg"
NEW, OLD = "penet", "none"
NAMES = {"penet": "PE-Net (PredCls release)",
         "none": "MOTIFS (TDE release baseline)"}
EPS = 1e-12
T0 = time.time()


def log(m):
    print(f"[penet-audit +{time.time()-T0:.0f}s] {m}", flush=True)


def sgg_data():
    """The data of RR.sgg_data restricted to the two models of this audit (same
    relations, same drop of the pairs without a ground-truth box, same calibration
    split: seed 20260811, half of the images)."""
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    y = meta["pred"].astype(np.int64)[keep] - 1
    phi = (meta["subj"].astype(np.int64) * 151 + meta["obj"].astype(np.int64))[keep]
    image = meta["image_index"].astype(np.int64)[keep]
    raw = {v: load_variant(v)["probs"][keep][:, 1:].astype(np.float64) for v in (OLD, NEW)}
    Q = {v: p / p.sum(1, keepdims=True) for v, p in raw.items()}
    rng = np.random.default_rng(20260811)
    imgs = np.unique(image)
    cal = np.isin(image, imgs[rng.permutation(len(imgs))[: len(imgs) // 2]])
    return Q, raw, y, phi, image, cal


def recall_split():
    RS.main(NEW, OLD)
    f = ROOT / "results" / f"sgg_recall_split_{NEW}_vs_{OLD}.json"
    d = json.loads(f.read_text())
    rows = {}
    for proto, res in d["results"].items():
        m = res["mean_recall"]
        rows[proto] = {"official_mR_old": res[f"official_mR_{OLD}"],
                       "official_mR_new": res[f"official_mR_{NEW}"],
                       "micro_mR_eligible_old": res[f"micro_mR_eligible_{OLD}"],
                       "micro_mR_eligible_new": res[f"micro_mR_eligible_{NEW}"],
                       "total": m["total"], "group": m["group"], "case": m["case"],
                       "case_ci": m["case_ci"], "group_ci": m["group_ci"],
                       "share": m["case"] / m["total"] if m["total"] else None,
                       "tiers": {t: res[f"mean_recall_{t}"] for t in ("head", "body", "tail")}}
    return {"file": str(f.relative_to(ROOT)), "n_eligible": d["n_eligible"],
            "coverage": d["coverage"], "protocols": rows}


def auc_block(raw, y, phi, image, tier_of, kS):
    """Within-cell AUC change under the four weightings (all relations), the reference
    gain, TOST verdicts, weight shares and the tier-pair breakdown under predicate
    weighting: sgg_auc_label_weighting.main restricted to this comparison."""
    P, py, pphi, pimage, _pcal = RR.pixel_data()
    kP = P[AL.REF_PAIR[0]].shape[1]
    reference = {}
    for wt in AL.WEIGHTINGS:
        c = AL.contrast(P[AL.REF_PAIR[0]], P[AL.REF_PAIR[1]], py, pphi, pimage, wt, kP)
        reference[wt] = float(c.difference)
        log(f"reference pixel {AL.REF_PAIR[0]} vs {AL.REF_PAIR[1]} {wt}: {c.difference:+.5f}")
    auc = {}
    for wt in AL.WEIGHTINGS:
        c = AL.contrast(raw[NEW], raw[OLD], y, phi, image, wt, kS)
        d = c.draws
        lo95, hi95 = np.nanpercentile(d, [2.5, 97.5])
        lo90, hi90 = np.nanpercentile(d, [5, 95])
        auc[wt] = {"auc_new": float(c.auc_new), "auc_old": float(c.auc_old),
                   "difference": float(c.difference),
                   "ci95": [float(lo95), float(hi95)], "ci90": [float(lo90), float(hi90)],
                   "largest_change_excluded": float(max(abs(lo90), abs(hi90))),
                   "reference_gain": reference[wt],
                   "tost": verdicts(float(lo90), float(hi90), reference[wt])}
        log(f"AUC {NEW} vs {OLD} {wt}: d {c.difference:+.5f} ci95 [{lo95:+.5f},{hi95:+.5f}] "
            f"ref {reference[wt]:.5f}")
    bl0 = _blocks(np.log(np.maximum(raw[OLD], AUC_EPS)), y, phi)
    weight_share = {wt: AL.share_by_tier(bl0, wt, y, kS, tier_of) for wt in AL.WEIGHTINGS}
    _, w_pred = AL.weighting_args("predicate", y, kS)
    tpp, overall = AL.tier_pair_predicate(raw[NEW], raw[OLD], y, phi, image, tier_of, w_pred)
    assert abs(overall - auc["predicate"]["difference"]) < 1e-9
    return {"reference": reference, "auc": auc, "weight_share": weight_share,
            "tier_pair_predicate": {f"{NEW} vs {OLD}": tpp}}


def main():
    Q, raw, y, phi, image, cal = sgg_data()
    kS = raw[OLD].shape[1]
    min_p = {v: float(raw[v].min()) for v in raw}
    zeros = {v: int((raw[v] <= 0).sum()) for v in raw}
    log(f"minimum probability {min_p}; zeros {zeros}")
    if any(m <= 0 for m in min_p.values()):
        raise SystemExit("non-positive probabilities; the AUC paths would clip them")
    acc = {v: float((Q[v].argmax(1) == y).mean()) for v in Q}
    log(f"top-1 predicate accuracy {acc}")

    out = {"comparison": f"{NEW} vs {OLD}", "names": NAMES, "n_boot": AL.N_BOOT,
           "seed": AL.SEED, "auc_eps": AUC_EPS,
           "architecture_note": "PE-Net and the TDE MOTIFS baseline are separately trained "
                                "models of different architectures; the comparison is between "
                                "two trained systems, not an intervention on one.",
           "checks": {"min_probability": min_p, "nonpositive_probabilities": zeros,
                      "rel_nms": "the evaluator's predcls graph-constrained path applies "
                                 "rel_nms (sgg_eval.py); the variant's gc_rank follows it"},
           "top1_accuracy": acc}
    assert AL.N_BOOT == 1000 and AL.SEED == 0, "the audit uses 1,000 replicates and seed 0"

    out["mean_recall_split"] = {f"{NEW} vs {OLD}": recall_split()}
    log("mean-recall split written")

    counts = np.asarray(json.loads((DDIR / "summary.json").read_text())
                        ["train_predicate_counts"])[1:]
    tier_of = np.where(counts > RR.HEAD_MIN, 0, np.where(counts < RR.TAIL_MAX, 2, 1))
    out.update(auc_block(raw, y, phi, image, tier_of, kS))
    log("AUC block done")

    out["matched_split"] = RR.recalibration_rows(Q, y, phi, image, cal,
                                                 pairs=((NEW, OLD),))
    OUT.write_text(json.dumps(out, indent=1))
    log(f"wrote {OUT.relative_to(ROOT)}")
    r = out["mean_recall_split"][f"{NEW} vs {OLD}"]["protocols"]["gc@50"]
    log(f"gc-mR@50 {r['official_mR_old']:.4f} -> {r['official_mR_new']:.4f}; split total "
        f"{r['total']:+.4f} = group {r['group']:+.4f} + case {r['case']:+.4f} "
        f"[{r['case_ci'][0]:+.4f}, {r['case_ci'][1]:+.4f}] (share {r['share']:.3f})")


if __name__ == "__main__":
    main()
