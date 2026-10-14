"""Audit of the released MOTIFS-DLFE PredCls checkpoint (Chiou et al., ACM MM 2021)
against its own released baseline and against the reference MOTIFS baseline of
the TDE release, with the three instruments used for TDE and IETrans:

1. the label-transport split of the mean-recall change under the six official
   protocols (graph-constrained and no-graph-constraint recall at K = 20, 50,
   100; run_sgg_recall_split.py, which also writes its own per-comparison file);
2. the within-cell AUC under the comparison and the relation weighting, on all
   identified relations and on the audit half, image bootstrap
   (run_sgg_rank_robustness.auc_rows);
3. the calibration-matched proper-score split (quadratic and log score) under
   one temperature per model and under temperature plus a per-class bias per
   model, fitted on the calibration half of the images and audited on the other
   half (the split of run_sgg_audit_wager.py).

DLFE divides every predicate probability by a per-predicate constant (the
estimated label frequency), which within a cell shifts every log-odds
log q(y) - log q(z) by the same amount for all relations: the AUC of the DLFE
model therefore equals that of the same network before the correction
(variant dlfe_soft), and the temperature-plus-class-bias family absorbs the
correction exactly. Both are reported as checks.

Run: python experiments/run_sgg_dlfe_audit.py
Writes results/sgg_dlfe_audit.json (and the sgg_recall_split_*.json files).
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain  # noqa: E402
from sgg_variants import load_variant  # noqa: E402
import run_sgg_audit_wager as AU  # noqa: E402
import run_sgg_rank_robustness as RR  # noqa: E402
import run_sgg_recall_split as RS  # noqa: E402

OUT = ROOT / "results/sgg_dlfe_audit.json"
DDIR = ROOT / "data/vg_motifs/wager_sgg"
PAIRS = [("dlfe", "dlfe_base"), ("dlfe", "none")]
CHECK_PAIRS = [("dlfe", "dlfe_soft")]
NAMES = {"dlfe": "MOTIFS-DLFE", "dlfe_base": "MOTIFS (DLFE release baseline)",
         "none": "MOTIFS (TDE release baseline)", "dlfe_soft": "MOTIFS-DLFE before the correction"}
EPS = 1e-12
N_BOOT = int(os.environ.get("WAGER_N_BOOT", "200"))


def sgg_data(variants):
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    y = meta["pred"].astype(np.int64)[keep] - 1
    phi = (meta["subj"].astype(np.int64) * 151 + meta["obj"].astype(np.int64))[keep]
    image = meta["image_index"].astype(np.int64)[keep]
    raw = {v: load_variant(v)["probs"][keep][:, 1:].astype(np.float64) for v in variants}
    Q = {v: p / p.sum(1, keepdims=True) for v, p in raw.items()}
    rng = np.random.default_rng(20260811)                 # the audit's calibration split
    imgs = np.unique(image)
    cal = np.isin(image, imgs[rng.permutation(len(imgs))[: len(imgs) // 2]])
    return Q, raw, y, phi, image, cal


def recall_split_rows(new, old):
    RS.main(new, old)
    f = ROOT / "results" / f"sgg_recall_split_{new}_vs_{old}.json"
    d = json.loads(f.read_text())
    rows = {}
    for proto, res in d["results"].items():
        m = res["mean_recall"]
        rows[proto] = {"official_mR_old": res[f"official_mR_{old}"],
                       "official_mR_new": res[f"official_mR_{new}"],
                       "total": m["total"], "group": m["group"], "case": m["case"],
                       "case_ci": m["case_ci"], "group_ci": m["group_ci"],
                       "share": m["case"] / m["total"] if m["total"] else None,
                       "tiers": {t: res[f"mean_recall_{t}"] for t in ("head", "body", "tail")}}
    return {"file": str(f.relative_to(ROOT)), "n_eligible": d["n_eligible"],
            "coverage": d["coverage"], "protocols": rows}


def matched_rows(Q, y, phi, image, cal, pairs):
    aud = ~cal
    L = {v: np.log(np.clip(q, EPS, None)) for v, q in Q.items()}
    fams, params = {}, {}
    for v in Q:
        T = AU.fit_temperature(Q[v][cal], y[cal])
        fams.setdefault("temperature", {})[v] = AU.temp_scale(Q[v], T)[aud]
        p = RR.fit_family(L[v][cal], y[cal], bias=True)
        fams.setdefault("temperature + class bias", {})[v] = RR.apply_family(L[v], p, True)[aud]
        params[v] = {"T": T, "T_bias_family": float(np.exp(p[0]))}
    rows = []
    for new, old in pairs:
        row = {"new": new, "old": old, "T_new": params[new]["T"], "T_old": params[old]["T"]}
        for fam in ("temperature", "temperature + class bias"):
            qn, qo = fams[fam][new], fams[fam][old]
            for sc in ("brier", "log"):
                with np.errstate(all="ignore"):
                    g = decompose_gain(qn, qo, y[aud], phi[aud], groups=image[aud], score=sc)
                row[f"{fam}, {sc}"] = {"total": g.total_gain, "group": g.prior_gain,
                                       "case": g.alignment_gain, "case_ci": list(g.alignment_ci),
                                       "share": g.alignment_share, "n_identified": g.n_identified}
        rows.append(row)
        print(f"matched {new} vs {old}: " + "  ".join(
            f"{k} {row[k]['case']:+.5f} [{row[k]['case_ci'][0]:+.5f},{row[k]['case_ci'][1]:+.5f}]"
            for k in row if isinstance(row[k], dict)), flush=True)
    return rows


def main():
    variants = sorted({v for p in PAIRS + CHECK_PAIRS for v in p})
    out = {"names": NAMES, "n_boot": N_BOOT, "comparisons": [f"{n} vs {o}" for n, o in PAIRS],
           "mean_recall_split": {}, "auc": None, "matched_split": None, "checks": {}}
    for new, old in PAIRS:
        out["mean_recall_split"][f"{new} vs {old}"] = recall_split_rows(new, old)
    Q, raw, y, phi, image, cal = sgg_data(variants)
    acc = {v: float((Q[v].argmax(1) == y).mean()) for v in variants}
    out["top1_accuracy"] = acc
    print(f"top-1 predicate accuracy: {acc}")
    out["auc"] = RR.auc_rows(raw, PAIRS, y, phi, image, ~cal)
    out["matched_split"] = matched_rows(Q, y, phi, image, cal, PAIRS)
    # checks: the correction is a per-predicate constant, so it cannot move the AUC
    # and the class-bias family removes it
    chk_auc = RR.auc_rows(raw, CHECK_PAIRS, y, phi, image, ~cal)
    chk_matched = matched_rows(Q, y, phi, image, cal, CHECK_PAIRS)
    ratio = Q["dlfe"] / Q["dlfe_soft"]
    out["checks"] = {"auc_dlfe_vs_dlfe_soft": chk_auc, "matched_dlfe_vs_dlfe_soft": chk_matched,
                     "dlfe_over_soft_ratio_is_per_predicate_constant":
                         float(np.max(np.abs(np.log(ratio) - np.log(ratio)[:1]))) < 1e-3}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")
    for new, old in PAIRS:
        r = out["mean_recall_split"][f"{new} vs {old}"]["protocols"]["gc@50"]
        print(f"{new} vs {old}: gc-mR@50 {r['official_mR_old']:.4f} -> {r['official_mR_new']:.4f}; "
              f"split total {r['total']:+.4f} = group {r['group']:+.4f} + case {r['case']:+.4f} "
              f"[{r['case_ci'][0]:+.4f}, {r['case_ci'][1]:+.4f}] (share {r['share']:.3f})")


def refresh_auc():
    """Recompute only the within-cell AUC entries (auc and checks.auc_dlfe_vs_dlfe_soft)
    and merge them into the existing results file."""
    variants = sorted({v for p in PAIRS + CHECK_PAIRS for v in p})
    out = json.loads(OUT.read_text())
    _, raw, y, phi, image, cal = sgg_data(variants)
    out["n_boot"] = N_BOOT
    out["auc"] = RR.auc_rows(raw, PAIRS, y, phi, image, ~cal)
    out["checks"]["auc_dlfe_vs_dlfe_soft"] = RR.auc_rows(raw, CHECK_PAIRS, y, phi, image, ~cal)
    OUT.write_text(json.dumps(out, indent=1))
    print(f"refreshed AUC entries in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    if "--auc-only" in sys.argv:
        refresh_auc()
    else:
        main()
