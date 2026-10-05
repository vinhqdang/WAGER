"""QA: check that the numbers quoted in the manuscript trace to committed results.

Not a general parser -- it asserts a curated list of (claim, manuscript file,
literal string, expected value from a results file) so that a transcription
slip or a stale figure after a rerun fails loudly.

Run: conda run -n py313 python experiments/verify_manuscript_numbers.py
     python experiments/verify_manuscript_numbers.py --driver cvpr2027/main.tex

With --driver, the checks run against a different paper built from the same results --
the CVPR rewrite, say -- whose file layout has nothing in common with the long-form
manuscript's. There each literal must appear somewhere in the document that driver
compiles, paper or supplementary, and the report says which of the two carries it.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
RES = ROOT / "results"


def load(name):
    return json.loads((RES / name).read_text())


sim = load("antisymmetric_simulation.json")
recal = load("cifar_recalibration.json")
cons = load("vg_prior_consequence.json")
bridge = {r["pair"]: r for r in load("vg_metric_bridge.json")}
vg = load("antisymmetric_results.json")
cif = load("cifar_lt_results.json")
vgv = load("vg_visual_results.json")


def cons_row(name):
    return next(r for r in cons["rows"] if r["name"] == name)


CHECKS = [
    # (label, file, literal in tex, actual value, tolerance)
    ("sim coverage clustered", "4experiments.tex", "94.0",
     sim["coverage"]["coverage_clustered"] * 100, 0.05),
    ("sim coverage iid", "4experiments.tex", "88.6",
     sim["coverage"]["coverage_iid_naive"] * 100, 0.05),
    ("sim calib raw dR", "4experiments.tex", "-0.488",
     sim["calibration_only"]["raw_reasoning_mean"], 5e-4),
    ("sim calib matched dR", "4experiments.tex", "-0.0003",
     sim["calibration_only"]["calibration_matched_reasoning_mean"], 5e-5),
    ("sim prior-only dR", "4experiments.tex", "0.0002",
     sim["prior_only"]["reasoning_mean"], 5e-5),
    ("sim shortcut dR", "4experiments.tex", "+0.041",
     sim["hidden_shortcut"]["reasoning_mean"], 5e-4),
    ("cal table CB raw dR", "appendix.tex", "-0.19427",
     recal["rows"]["CB vs CE (raw)"]["dR"], 1e-5),
    ("cal table CB cal dR", "appendix.tex", "-0.23991",
     recal["rows"]["CB vs CE (cal-both)"]["dR"], 1e-5),
    ("cal table DRW cal dT", "appendix.tex", "+0.02173",
     recal["rows"]["DRW vs CE (cal-both)"]["dT"], 1e-5),
    ("cal table DRW cal dR", "appendix.tex", "+0.01957",
     recal["rows"]["DRW vs CE (cal-both)"]["dR"], 1e-5),
    ("cal table control dP", "appendix.tex", "+0.37960",
     recal["rows"]["CE(cal) vs CE (confound size)"]["dP"], 1e-5),
    ("consequence VISUAL' dP", "4experiments.tex", "+0.02390",
     cons_row("VISUAL' vs VISUAL")["prior"], 1e-5),
    ("consequence VISUAL' dR", "4experiments.tex", "+0.00114",
     cons_row("VISUAL' vs VISUAL")["reasoning"], 1e-5),
    ("consequence corrected dT", "4experiments.tex", "-0.02138",
     cons_row("VISUAL' vs SPATIAL")["total"], 1e-5),
    ("consequence corrected dR", "4experiments.tex", "+0.00754",
     cons_row("VISUAL' vs SPATIAL")["reasoning"], 1e-5),
    ("consequence both-corrected dR", "4experiments.tex", "+0.00664",
     cons_row("VISUAL' vs SPATIAL' (both corrected)")["reasoning"], 1e-5),
    ("consequence cal-matched dR", "4experiments.tex", "+0.00464",
     cons_row("VISUAL vs SPATIAL cal-both (audit half)")["reasoning"], 1e-5),
    ("bridge spatial dR", "4experiments.tex", "0.01023",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["dR"], 1e-5),
    ("bridge spatial acc pts", "appendix.tex", "0.51",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["d_acc"] * 100, 0.006),
    ("bridge spatial mrr pts", "appendix.tex", "0.60",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["d_mrr"] * 100, 0.006),
    ("bridge spatial r5 pts", "appendix.tex", "0.86",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["d_r5"] * 100, 0.006),
    ("bridge clip acc drop", "appendix.tex", "3.11",
     -bridge["MLP-VISUAL-S vs MLP-SPATIAL-S"]["d_acc"] * 100, 0.006),
    ("bridge clip r5 drop", "appendix.tex", "2.20",
     -bridge["MLP-VISUAL-S vs MLP-SPATIAL-S"]["d_r5"] * 100, 0.006),
    ("bridge clip pm acc drop", "appendix.tex", "2.17",
     -bridge["MLP-VISUAL-S vs MLP-SPATIAL-S"]["d_acc_pm"] * 100, 0.006),
]


def find_number(res, *path):
    cur = res
    for p in path:
        cur = cur[p]
    return cur


# original headline numbers still quoted in abstract/intro/experiments
vg_rows = {f"{r['new']}|{r['old']}": r for r in vg["comparisons"]}
vgv_rows = {f"{r['new']}|{r['old']}": r for r in vgv["comparisons"]}
CHECKS += [
    ("VG relations audited", "appendix.tex", "227,337",
     vg["comparisons"][0]["n_identified"], 0),
    ("VG test relations", "appendix.tex", "229,605", vgv["n_test"], 0),
    ("CLIP total gain", "4experiments.tex", "-0.04642",
     vgv_rows["MLP-VISUAL-S|MLP-SPATIAL-S"]["total_gain"], 1e-5),
    ("CLIP alignment gain", "4experiments.tex", "0.00640",
     vgv_rows["MLP-VISUAL-S|MLP-SPATIAL-S"]["reasoning_gain"], 1e-5),
    ("CIFAR CB accuracy", "appendix.tex", "0.2627",
     cif["accuracy"]["CB"], 1e-4),
    ("CIFAR DRW accuracy", "appendix.tex", "0.3874",
     cif["accuracy"]["DRW"], 1e-4),
]


# seed/ratio robustness table
ms = load("cifar_multiseed.json")
CHECKS += [
    ("robust CB r10 dR", "appendix.tex", "-0.06903", ms["r10_s0"]["CB cal"]["dR"], 1e-5),
    ("robust CB r50 dR", "appendix.tex", "-0.24409", ms["r50_s0"]["CB cal"]["dR"], 1e-5),
    ("robust DRW r100s1 dR", "appendix.tex", "+0.00748",
     ms["r100_s1"]["DRW cal"]["dR"], 1e-5),
    ("robust DRW r100s2 dR", "appendix.tex", "+0.03124",
     ms["r100_s2"]["DRW cal"]["dR"], 1e-5),
    ("robust LA r50 dR", "appendix.tex", "+0.03768", ms["r50_s0"]["LA cal"]["dR"], 1e-5),
    ("robust CB mean", "appendix.tex", "-0.25108",
     ms["across_seeds_r100"]["CB cal.dR"]["mean"], 1e-5),
    ("robust DRW mean", "appendix.tex", "+0.01953",
     ms["across_seeds_r100"]["DRW cal.dR"]["mean"], 1e-5),
    ("robust r10 CE acc", "appendix.tex", "0.5388",
     ms["r10_s0"]["accuracy"]["CE"], 1e-4),
    ("robust r50 LA acc", "appendix.tex", "0.4550",
     ms["r50_s0"]["accuracy"]["LA"], 1e-4),
]


# SGG checkpoint audit
sgg = load("sgg_audit_motifs.json")
def sgg_row(score, regime=None, phi=None):
    for r in sgg["comparisons"]:
        if r["score"] != score:
            continue
        if regime is not None and r.get("regime") != regime:
            continue
        if regime is None and "regime" in r:
            continue
        if phi is not None and r.get("prior_feature") != phi:
            continue
        if phi is None and "prior_feature" in r:
            continue
        return r
    raise KeyError((score, regime, phi))

CHECKS += [
    ("sgg n relations", "4experiments.tex", "183{,}639", sgg["n_relations"], 0),
    ("sgg n images", "4experiments.tex", "26{,}446", sgg["n_images"], 0),
    ("sgg n cells", "4experiments.tex", "7{,}127", sgg["n_cells"], 0),
    ("sgg base acc", "4experiments.tex", "0.6981", sgg["accuracy"]["MOTIFS"], 5e-5),
    ("sgg tde acc", "4experiments.tex", "0.5577", sgg["accuracy"]["MOTIFS-TDE"], 5e-5),
    ("sgg raw dT", "4experiments.tex", "-0.11651", sgg_row("brier")["total_gain"], 1e-5),
    ("sgg raw dP", "4experiments.tex", "-0.10296", sgg_row("brier")["prior_gain"], 1e-5),
    ("sgg raw dR", "4experiments.tex", "-0.01355",
     sgg_row("brier")["reasoning_gain"], 1e-5),
    ("sgg cal dR", "4experiments.tex", "-0.00006",
     sgg_row("brier", "calibration-matched")["reasoning_gain"], 1e-5),
    ("sgg cal dP", "4experiments.tex", "-0.18258",
     sgg_row("brier", "calibration-matched")["prior_gain"], 1e-5),
    ("sgg cal log dR", "4experiments.tex", "+0.04396",
     sgg_row("log", "calibration-matched")["reasoning_gain"], 1e-5),
    ("sgg cal log dR ci lo", "4experiments.tex", "+0.04079",
     sgg_row("log", "calibration-matched")["reasoning_ci"][0], 1e-5),
    ("sgg cal log dR ci hi", "4experiments.tex", "+0.04714",
     sgg_row("log", "calibration-matched")["reasoning_ci"][1], 1e-5),
    ("sgg raw log dR ci lo", "4experiments.tex", "-0.13093",
     sgg_row("log")["reasoning_ci"][0], 1e-5),
    ("sgg raw log dR ci hi", "4experiments.tex", "-0.12145",
     sgg_row("log")["reasoning_ci"][1], 1e-5),
    ("sgg subject dR", "4experiments.tex", "-0.21711",
     sgg_row("brier", None, "subject class")["reasoning_gain"], 1e-5),
    ("sgg base R@50", "4experiments.tex", "0.6612",
     sgg["recalls"]["MOTIFS"]["predcls_recall@50"], 5e-5),
    ("sgg tde mR@50", "4experiments.tex", "0.2476",
     sgg["recalls"]["MOTIFS-TDE"]["predcls_mean_recall@50"], 5e-5),
    ("sgg base mR@50", "4experiments.tex", "0.1459",
     sgg["recalls"]["MOTIFS"]["predcls_mean_recall@50"], 5e-5),
    ("sgg tde zR@50", "4experiments.tex", "0.1432",
     sgg["recalls"]["MOTIFS-TDE"]["predcls_zeroshot_recall@50"], 5e-5),
]


# --- numbers the CVPR rewrite prints that the long-form checks above never covered ------
# Every data number in cvpr2027/sec/ traces here or above. The file field names the
# CVPR section; in --driver mode only presence in the compiled document is required.
cons_rows = {r["name"]: r for r in cons["rows"]}
sgg_matched_q = sgg_row("brier", "calibration-matched")
sgg_matched_l = sgg_row("log", "calibration-matched")
sgg_raw_q, sgg_raw_l = sgg_row("brier"), sgg_row("log")
sgg_subj = sgg_row("brier", None, "subject class")
vis_spa = vgv_rows["MLP-VISUAL-S|MLP-SPATIAL-S"]
CHECKS += [
    # TDE audit (Table 1 and Sec. 5)
    ("cvpr mR base, points", "5_audit.tex", "14.6",
     sgg["recalls"]["MOTIFS"]["predcls_mean_recall@50"] * 100, 0.05),
    ("cvpr mR TDE, points", "5_audit.tex", "24.8",
     sgg["recalls"]["MOTIFS-TDE"]["predcls_mean_recall@50"] * 100, 0.05),
    ("cvpr identified cells", "5_audit.tex", "5{,}044", sgg_raw_q["n_cells"], 0),
    ("cvpr identified share of relations", "5_audit.tex", "98.9",
     sgg_raw_q["coverage"] * 100, 0.05),
    ("cvpr T* baseline", "5_audit.tex", "2.50", sgg_matched_q["T_old"], 5e-3),
    ("cvpr T* TDE", "5_audit.tex", "0.92", sgg_matched_q["T_new"], 5e-3),
    ("cvpr raw quad dR ci lo", "5_audit.tex", "-0.01504", sgg_raw_q["reasoning_ci"][0], 1e-5),
    ("cvpr raw quad dR ci hi", "5_audit.tex", "-0.01206", sgg_raw_q["reasoning_ci"][1], 1e-5),
    ("cvpr raw log dT", "5_audit.tex", "+0.03277", sgg_raw_l["total_gain"], 1e-5),
    ("cvpr raw log dP", "5_audit.tex", "+0.15897", sgg_raw_l["prior_gain"], 1e-5),
    ("cvpr raw log dR", "5_audit.tex", "-0.12619", sgg_raw_l["reasoning_gain"], 1e-5),
    ("cvpr subject dT", "5_audit.tex", "-0.11536", sgg_subj["total_gain"], 1e-5),
    ("cvpr subject dP", "5_audit.tex", "+0.10175", sgg_subj["prior_gain"], 1e-5),
    ("cvpr matched quad dT", "5_audit.tex", "-0.18264", sgg_matched_q["total_gain"], 1e-5),
    ("cvpr matched quad dR ci lo", "5_audit.tex", "-0.00120",
     sgg_matched_q["reasoning_ci"][0], 1e-5),
    ("cvpr matched quad dR ci hi", "5_audit.tex", "+0.00109",
     sgg_matched_q["reasoning_ci"][1], 1e-5),
    ("cvpr matched quad p", "5_audit.tex", ".555", sgg_matched_q["randomization_p"], 5e-4),
    ("cvpr matched log dT", "5_audit.tex", "-0.54760", sgg_matched_l["total_gain"], 1e-5),
    ("cvpr matched log dP", "5_audit.tex", "-0.59157", sgg_matched_l["prior_gain"], 1e-5),
    # Controlled predictors (Sec. 4)
    ("cvpr CLASS-FREQ dT", "4_validation.tex", "0.03386",
     vg_rows["MLP-CLASS|FREQ"]["total_gain"], 1e-5),
    ("cvpr CLASS-FREQ dR", "4_validation.tex", "0.00000",
     vg_rows["MLP-CLASS|FREQ"]["reasoning_gain"], 5e-6),
    ("cvpr CLASS-FREQ p", "4_validation.tex", ".724", vg_rows["MLP-CLASS|FREQ"]["randomization_p"], 5e-4),
    ("cvpr SPATIAL-CLASS dT", "4_validation.tex", "0.00885",
     vg_rows["MLP-SPATIAL|MLP-CLASS"]["total_gain"], 1e-5),
    ("cvpr SPATIAL-CLASS dP", "4_validation.tex", "0.00554",
     vg_rows["MLP-SPATIAL|MLP-CLASS"]["prior_gain"], 1e-5),
    ("cvpr SPATIAL-CLASS dR ci lo", "4_validation.tex", "0.01373",
     vg_rows["MLP-SPATIAL|MLP-CLASS"]["reasoning_ci"][0], 1e-5),
    ("cvpr SPATIAL-CLASS dR ci hi", "4_validation.tex", "0.01504",
     vg_rows["MLP-SPATIAL|MLP-CLASS"]["reasoning_ci"][1], 1e-5),
    ("cvpr VG identified cells", "4_validation.tex", "6{,}346",
     vg_rows["MLP-SPATIAL|MLP-CLASS"]["n_cells"], 0),
    ("cvpr VG coverage", "4_validation.tex", "99.0",
     vg_rows["MLP-SPATIAL|MLP-CLASS"]["coverage"] * 100, 0.05),
    # Simulation (Sec. 4)
    ("cvpr sim type-I", "4_validation.tex", "0.030", sim["null_type1_alpha_005"], 5e-4),
    ("cvpr sim null mean x1e5", "4_validation.tex", "-8.97", sim["null_reasoning_mean"] * 1e5, 5e-3),
    ("cvpr sim prior-only sd", "4_validation.tex", "0.0035", sim["prior_only"]["reasoning_sd"], 5e-5),
    ("cvpr sim shortcut sd", "4_validation.tex", "0.004", sim["hidden_shortcut"]["reasoning_sd"], 5e-4),
    ("cvpr sim calib matched sd", "4_validation.tex", "0.0017",
     sim["calibration_only"]["calibration_matched_reasoning_sd"], 5e-5),
    # CLIP (Sec. 6)
    ("cvpr CLIP accuracy", "6_pixels.tex", "0.6156", vgv["accuracy"]["MLP-VISUAL-S"], 5e-5),
    ("cvpr geometry accuracy", "6_pixels.tex", "0.6467", vgv["accuracy"]["MLP-SPATIAL-S"], 5e-5),
    ("cvpr CLIP-geometry dP", "6_pixels.tex", "0.05282", vis_spa["prior_gain"], 1e-5),
    ("cvpr CLIP-geometry dR ci lo", "6_pixels.tex", "0.00513", vis_spa["reasoning_ci"][0], 1e-5),
    ("cvpr CLIP-geometry dR ci hi", "6_pixels.tex", "0.00767", vis_spa["reasoning_ci"][1], 1e-5),
    ("cvpr CLIP-geometry p", "6_pixels.tex", ".002", vis_spa["randomization_p"], 5e-4),
    ("cvpr CLIP-class dR", "6_pixels.tex", "0.01663",
     vgv_rows["MLP-VISUAL-S|MLP-CLASS-S"]["reasoning_gain"], 1e-5),
    ("cvpr geometry-class dR", "6_pixels.tex", "0.01023",
     vgv_rows["MLP-SPATIAL-S|MLP-CLASS-S"]["reasoning_gain"], 1e-5),
    ("cvpr train subsample", "6_pixels.tex", "100{,}000", vgv["n_train_relations"], 0),
    ("cvpr prior correction dP", "6_pixels.tex", "+0.02390", cons_rows["VISUAL' vs VISUAL"]["prior"], 1e-5),
    ("cvpr prior correction dR", "6_pixels.tex", "+0.00114",
     cons_rows["VISUAL' vs VISUAL"]["reasoning"], 1e-5),
    ("cvpr corrected deficit", "6_pixels.tex", "-0.02138", cons_rows["VISUAL' vs SPATIAL"]["total"], 1e-5),
    ("cvpr corrected dR", "6_pixels.tex", "+0.00754", cons_rows["VISUAL' vs SPATIAL"]["reasoning"], 1e-5),
    ("cvpr both corrected dR", "6_pixels.tex", "+0.00664",
     cons_rows["VISUAL' vs SPATIAL' (both corrected)"]["reasoning"], 1e-5),
    ("cvpr CLIP matched dR", "6_pixels.tex", "+0.00464",
     cons_rows["VISUAL vs SPATIAL cal-both (audit half)"]["reasoning"], 1e-5),
    ("cvpr CLIP matched ci lo", "6_pixels.tex", "+0.00311",
     cons_rows["VISUAL vs SPATIAL cal-both (audit half)"]["reasoning_ci"][0], 1e-5),
    ("cvpr CLIP matched ci hi", "6_pixels.tex", "+0.00618",
     cons_rows["VISUAL vs SPATIAL cal-both (audit half)"]["reasoning_ci"][1], 1e-5),
    # Limitations (Sec. 7)
    ("cvpr robustness value", "7_conclusion.tex", "0.061",
     load("sensitivity_bound.json")["robustness_value_rho_dagger"], 5e-4),
]

bridge_vs = bridge["MLP-VISUAL-S vs MLP-SPATIAL-S"]
CHECKS += [
    # Added with the 2026-10-03 panel corrections.
    ("cvpr TDE R@50", "5_audit.tex", "0.4588",
     sgg["recalls"]["MOTIFS-TDE"]["predcls_recall@50"], 5e-5),
    ("cvpr base ng-mR@50", "5_audit.tex", "0.3260",
     sgg["recalls"]["MOTIFS"]["predcls_ng_mean_recall@50"], 5e-5),
    ("cvpr TDE ng-mR@50", "5_audit.tex", "0.2981",
     sgg["recalls"]["MOTIFS-TDE"]["predcls_ng_mean_recall@50"], 5e-5),
    ("cvpr CLIP matched dP", "6_pixels.tex", "0.04705",
     cons_rows["VISUAL vs SPATIAL cal-both (audit half)"]["prior"], 1e-5),
    ("cvpr CLIP prior-matched acc gap, points", "6_pixels.tex", "2.17",
     bridge_vs["d_acc_pm"] * 100, 5e-3),
    ("cvpr CLIP prior-matched MRR gap, points", "6_pixels.tex", "1.67",
     bridge_vs["d_mrr_pm"] * 100, 5e-3),
    ("cvpr CLIP prior-matched R@5 gap, points", "6_pixels.tex", "1.07",
     bridge_vs["d_r5_pm"] * 100, 5e-3),
]

# --- the mean-recall split of the rerun (REV-1, REV-3; Sec. 5, App. on the split) ----------
def _split(name):
    return load(name)["results"]


_DD = ROOT / "data/vg_motifs/wager_sgg"
_names = json.loads((_DD / "predicate_names.json").read_text())["names"]
_rer = json.loads((_DD / "summary.json").read_text())["recalls"]
sp, sp_la = _split("sgg_recall_split.json"), _split("sgg_recall_split_la1_vs_none.json")
sp_tla = _split("sgg_recall_split_TDE_vs_la1.json")
sp_la5 = _split("sgg_recall_split_la0.5_vs_none.json")
sp_vc = _split("sgg_recall_split_vis_ctx_vs_none.json")
m50, la50, tla50 = sp["gc@50"]["mean_recall"], sp_la["gc@50"]["mean_recall"], sp_tla["gc@50"]["mean_recall"]
auc = {(r["new"], r["old"]): r for r in load("sgg_rank_contrast.json")["rows"]}
pp = sp["gc@50"]["per_predicate"]


def _cmp(name, score):
    return next(r for r in sgg["comparisons"]
                if r["comparison"] == name and r["score"] == score
                and r.get("regime") == "calibration-matched")


la_q = _cmp("MOTIFS logit-adjusted tau=1 vs MOTIFS", "brier")
la_l = _cmp("MOTIFS logit-adjusted tau=1 vs MOTIFS", "log")
tla_q = _cmp("MOTIFS-TDE vs MOTIFS logit-adjusted tau=1", "brier")
tla_l = _cmp("MOTIFS-TDE vs MOTIFS logit-adjusted tau=1", "log")
tiers = load("sgg_recall_split.json")["tiers"]
tail_rec = [sp["gc@50"]["official_per_predicate_TDE"][q - 1] for q in tiers["tail"]]
tail_base = [sp["gc@50"]["official_per_predicate_none"][q - 1] for q in tiers["tail"]]
meta_n = int(np.load(_DD / "meta.npz")["pred"].shape[0])
tail_n = int(sum((np.load(_DD / "meta.npz")["pred"] == q).sum() for q in tiers["tail"]))
r_cost_tde = _rer["none"]["R@50"] - _rer["TDE"]["R@50"]
r_cost_la = _rer["none"]["R@50"] - _rer["la1"]["R@50"]
P = lambda name: pp[_names.index(name) - 1]   # noqa: E731
CHECKS += [
    ("rec n relations", "5_audit.tex", "183{,}642", meta_n, 0),
    ("rec LA mR@50", "5_audit.tex", "0.2343", _rer["la1"]["mR@50"], 5e-5),
    ("rec LA R@50", "5_audit.tex", "0.6437", _rer["la1"]["R@50"], 5e-5),
    ("rec TDE dmR", "5_audit.tex", "0.0972", m50["total"], 5e-5),
    ("rec TDE dmR official", "5_audit.tex", "0.1017",
     sp["gc@50"]["official_mR_TDE"] - sp["gc@50"]["official_mR_none"], 5e-5),
    ("rec TDE group", "5_audit.tex", "+0.0841", m50["group"], 5e-5),
    ("rec TDE case", "5_audit.tex", "+0.0130", m50["case"], 5e-5),
    ("rec TDE case lo", "5_audit.tex", "+0.0093", m50["case_ci"][0], 5e-5),
    ("rec TDE case hi", "5_audit.tex", "+0.0168", m50["case_ci"][1], 5e-5),
    ("rec TDE group share, %", "5_audit.tex", "87", 100 * m50["group"] / m50["total"], 0.5),
    ("rec n head", "5_audit.tex", "head above", "counted below", 0),
    ("rec n body", "5_audit.tex", "26 body", "counted below", 0),
    ("rec n tail", "5_audit.tex", "15 tail", "counted below", 0),
    ("rec body total", "5_audit.tex", "+0.1224", sp["gc@50"]["mean_recall_body"]["total"], 5e-5),
    ("rec body group", "5_audit.tex", "+0.1082", sp["gc@50"]["mean_recall_body"]["group"], 5e-5),
    ("rec head loss", "5_audit.tex", "0.0255", -sp["gc@50"]["mean_recall_head"]["total"], 5e-5),
    ("rec tail gain", "5_audit.tex", "0.0003", sp["gc@50"]["mean_recall_tail"]["total"], 5e-5),
    ("rec tail test relations", "5_audit.tex", "1{,}480", tail_n, 0),
    ("rec tail predicates TDE recalls", "5_audit.tex", "TDE recalls one", "counted below", 0),
    ("rec tail baseline recalls none", "5_audit.tex", "baseline recalls none", "counted below", 0),
    ("rec tail 'to' recall", "5_audit.tex", "0.016",
     sp["gc@50"]["official_per_predicate_TDE"][_names.index("to") - 1], 5e-4),
    ("rec parked on after", "5_audit.tex", "0.886",
     sp["gc@50"]["per_predicate_recall_TDE"][_names.index("parked on") - 1], 5e-4),
    ("rec parked on before", "5_audit.tex", "0.000",
     sp["gc@50"]["per_predicate_recall_none"][_names.index("parked on") - 1], 5e-4),
    ("rec on loss", "5_audit.tex", "0.558", -P("on")["total"], 5e-4),
    ("rec LA dmR", "5_audit.tex", "+0.0941", la50["total"], 5e-5),
    ("rec LA group", "5_audit.tex", "+0.0802", la50["group"], 5e-5),
    ("rec LA case", "5_audit.tex", "+0.0139", la50["case"], 5e-5),
    ("rec TDE-LA case", "5_audit.tex", "-0.0008", tla50["case"], 5e-5),
    ("rec TDE-LA case lo", "5_audit.tex", "-0.0050", tla50["case_ci"][0], 5e-5),
    ("rec TDE-LA case hi", "5_audit.tex", "+0.0033", tla50["case_ci"][1], 5e-5),
    ("rec table TDE-LA total", "5_audit.tex", "+.0031", tla50["total"], 5e-5),
    ("rec table TDE-LA group", "5_audit.tex", "+.0039", tla50["group"], 5e-5),
    ("rec table LA case lo", "5_audit.tex", "+.0101", la50["case_ci"][0], 5e-5),
    ("rec table LA case hi", "5_audit.tex", "+.0176", la50["case_ci"][1], 5e-5),
    ("auc TDE-base", "5_audit.tex", "+0.0026", auc[("TDE", "none")]["difference"], 5e-5),
    ("auc TDE-base lo", "5_audit.tex", "-0.0028", auc[("TDE", "none")]["ci"][0], 5e-5),
    ("auc TDE-base hi", "5_audit.tex", "+0.0086", auc[("TDE", "none")]["ci"][1], 5e-5),
    ("auc TDE-LA lo", "5_audit.tex", "-.0029", auc[("TDE", "la1")]["ci"][0], 5e-5),
    ("auc LA-base", "5_audit.tex", "+.0001", auc[("la1", "none")]["difference"], 5e-5),
    ("ps TDE-LA quad case", "5_audit.tex", "-0.0040", tla_q["reasoning_gain"], 5e-5),
    ("ps TDE-LA log case", "5_audit.tex", "+0.0154", tla_l["reasoning_gain"], 5e-5),
    ("ps LA quad case", "5_audit.tex", "+0.0039", la_q["reasoning_gain"], 5e-5),
    ("ps LA log case", "5_audit.tex", "+0.0285", la_l["reasoning_gain"], 5e-5),
    ("ps matched quad dP", "5_audit.tex", "-0.18258", sgg_matched_q["prior_gain"], 1e-5),
    ("rec R cost TDE", "5_audit.tex", "0.2023", r_cost_tde, 5e-5),
    ("rec R cost LA", "5_audit.tex", "0.0175", r_cost_la, 5e-5),
    ("rec LA.5 case", "3_recall.tex", "+0.0064", sp_la5["gc@50"]["mean_recall"]["case"], 5e-5),
    ("rec drop-frq case", "3_recall.tex", "+0.0053", sp_vc["gc@50"]["mean_recall"]["case"], 5e-5),
    ("rec ng TDE-LA case", "3_recall.tex", "+0.0072", sp_tla["ng@50"]["mean_recall"]["case"], 5e-5),
    ("rec ng TDE-LA case lo", "3_recall.tex", "-0.0001", sp_tla["ng@50"]["mean_recall"]["case_ci"][0], 5e-5),
    ("rec ng TDE-LA case hi", "3_recall.tex", "+0.0145", sp_tla["ng@50"]["mean_recall"]["case_ci"][1], 5e-5),
    ("rec train relations", "3_recall.tex", "439{,}063",
     sum(json.loads((_DD / "summary.json").read_text())["train_predicate_counts"]), 0),
    ("acc LA", "3_recall.tex", "0.6820", sgg["accuracy"]["MOTIFS logit-adjusted tau=1"], 5e-5),
]

_tp = load("sgg_tde_path.json")
_st = {r["step"]: r for r in _tp["path"]}
_frq, _vis, _avg = (_st["drop the frequency prior"], _st["drop the visual term"],
                    _st["subtract the averaged context"])
_en = _tp["logit_energy"]["ctx(avg)"]
CHECKS += [
    ("path frq dmR", "5_audit.tex", "-0.0009", _frq["mR@50 gc"]["total"], 5e-5),
    ("path vis dmR", "5_audit.tex", "+0.0164", _vis["mR@50 gc"]["total"], 5e-5),
    ("path vis case", "5_audit.tex", "+0.0016", _vis["mR@50 gc"]["case"], 5e-5),
    ("path vis case lo", "5_audit.tex", "-0.0006", _vis["mR@50 gc"]["case_ci"][0], 5e-5),
    ("path vis case hi", "5_audit.tex", "+0.0037", _vis["mR@50 gc"]["case_ci"][1], 5e-5),
    ("path avg dmR", "5_audit.tex", "+0.0817", _avg["mR@50 gc"]["total"], 5e-5),
    ("path avg-ctx global share, %", "5_audit.tex", "99.96", 100 * _en["global"], 5e-3),
    ("path avg-ctx corr log prior", "5_audit.tex", "+0.75", _en["corr_global_log_prior"], 5e-3),
    ("path frq quad case", "3_recall.tex", "+0.00915", _frq["proper brier matched"]["case"], 1e-5),
    ("path avg-ctx non-global rms", "3_recall.tex", "0.021", _en["rms_non_global"], 5e-4),
    ("path avg-ctx rms", "3_recall.tex", "1.10", _en["rms"], 5e-3),
    ("path avg AUC", "3_recall.tex", "+0.0016", _avg["auc"]["difference"], 5e-5),
]
if abs(_frq["auc"]["difference"]) > 5e-4:
    print("FAIL 'dropping the frequency prior does not move the within-cell AUC'")
    sys.exit(1)

_ie = load("sgg_recall_split_ietrans_vs_none.json")["results"]["gc@50"]
_iec = load("sgg_recall_split_ietrans_vs_ietrans_ctx.json")["results"]["gc@50"]["mean_recall"]
_ies = json.loads((ROOT / "data/vg_motifs/wager_ietrans/summary.json").read_text())
_iq = _cmp("IETrans vs MOTIFS", "brier")
_il = _cmp("IETrans vs MOTIFS", "log")
_ia = auc[("ietrans", "none")]
CHECKS += [
    ("iet mR@50 standard", "5_audit.tex", "0.3587",
     _ies["official_protocol"]["standard_test ietrans mR@50"], 5e-5),
    ("iet mR@50 own test", "5_audit.tex", "0.3576",
     _ies["official_protocol"]["ietrans_dedup_test ietrans mR@50"], 5e-5),
    ("iet mR@50 own test = official run", "5_audit.tex", "0.3576",
     _ies["official_ietrans_run"]["predcls_mean_recall@50"], 5e-5),
    ("iet dmR", "5_audit.tex", "+0.2204", _ie["mean_recall"]["total"], 5e-5),
    ("iet group", "5_audit.tex", "+0.2143", _ie["mean_recall"]["group"], 5e-5),
    ("iet case", "5_audit.tex", "+0.0060", _ie["mean_recall"]["case"], 5e-5),
    ("iet case lo", "5_audit.tex", "-0.0031", _ie["mean_recall"]["case_ci"][0], 5e-5),
    ("iet case hi", "5_audit.tex", "+0.0151", _ie["mean_recall"]["case_ci"][1], 5e-5),
    ("iet tail", "5_audit.tex", "+0.0889", _ie["mean_recall_tail"]["total"], 5e-5),
    ("iet quad case", "5_audit.tex", "-0.0162", _iq["reasoning_gain"], 5e-5),
    ("iet log case", "5_audit.tex", "-0.0544", _il["reasoning_gain"], 5e-5),
    ("iet auc", "5_audit.tex", "-0.0093", _ia["difference"], 5e-5),
    ("iet auc lo", "5_audit.tex", "-0.0181", _ia["ci"][0], 5e-5),
    ("iet auc hi", "5_audit.tex", "+0.0004", _ia["ci"][1], 5e-5),
    ("iet points", "0_abstract.tex", "21 points",
     "checked below", 0),
    ("iet group share", "0_abstract.tex", "97\\%", "checked below", 0),
    ("iet own test relations", "3_recall.tex", "152{,}226", _ies["ietrans_relations"], 0),
    ("iet prior cost", "3_recall.tex", "0.0133", -_iec["total"], 5e-5),
    ("iet prior case", "3_recall.tex", "-0.0088", _iec["case"], 5e-5),
]
if round(100 * (_ies["official_protocol"]["standard_test ietrans mR@50"]
                - sgg["recalls"]["MOTIFS"]["predcls_mean_recall@50"])) != 21:
    print("FAIL '21 points'"); sys.exit(1)
if round(100 * _ie["mean_recall"]["group"] / _ie["mean_recall"]["total"]) != 97:
    print("FAIL '97% group-level'"); sys.exit(1)
if not (_iq["reasoning_ci"][1] < 0 and _il["reasoning_ci"][1] < 0):
    print("FAIL 'falls under both proper scores'"); sys.exit(1)

_vr = load("vg_visual_rank.json")
_vrr = {(r["new"], r["old"]): r for r in _vr["rows"]}
_vs = _vrr[("MLP-VISUAL-S", "MLP-SPATIAL-S")]
CHECKS += [
    ("vrank CLIP auc", "6_pixels.tex", "0.5408", _vs["auc_new"], 5e-5),
    ("vrank geometry auc", "6_pixels.tex", "0.5323", _vs["auc_old"], 5e-5),
    ("vrank diff", "6_pixels.tex", "+0.0085", _vs["difference"], 5e-5),
    ("vrank diff lo", "6_pixels.tex", "-0.0062", _vs["ci"][0], 5e-5),
    ("vrank diff hi", "6_pixels.tex", "+0.0214", _vs["ci"][1], 5e-5),
    ("vrank CLIP vs class", "6_pixels.tex", "+0.0408",
     _vrr[("MLP-VISUAL-S", "MLP-CLASS-S")]["difference"], 5e-5),
    ("vrank geometry vs class", "6_pixels.tex", "+0.0323",
     _vrr[("MLP-SPATIAL-S", "MLP-CLASS-S")]["difference"], 5e-5),
]
if not (_vs["ci"][0] < 0 < _vs["ci"][1]) or abs(_vr["auc_class_only"] - 0.5) > 1e-12:
    print("FAIL 'the AUC does not separate CLIP from geometry' / class-only AUC 1/2"); sys.exit(1)

_sd = load("vg_visual_seeds.json")
_seeds = [_sd["per_seed"][str(k)] for k in _sd["seeds"]]
_vsp = [r["pairs"]["MLP-VISUAL-S vs MLP-SPATIAL-S"] for r in _seeds]
_gsp = [r["pairs"]["MLP-VISGEO-S vs MLP-SPATIAL-S"] for r in _seeds]
CHECKS += [
    ("seeds CLIP case min", "6_pixels.tex", "+0.00413", min(p["matched"]["case"] for p in _vsp), 1e-5),
    ("seeds CLIP case max", "6_pixels.tex", "+0.00474", max(p["matched"]["case"] for p in _vsp), 1e-5),
    ("seeds CLIP+geo case min", "6_pixels.tex", "+0.00807", min(p["matched"]["case"] for p in _gsp), 1e-5),
    ("seeds CLIP+geo case max", "6_pixels.tex", "+0.00949", max(p["matched"]["case"] for p in _gsp), 1e-5),
]
_ok = (len(_seeds) == 5 and max(_sd["seed0_vs_reference"].values()) == 0.0
       and all(p["matched"]["case_ci"][0] > 0 for p in _vsp + _gsp)
       and all(r["accuracy"]["MLP-VISUAL-S"] < r["accuracy"]["MLP-SPATIAL-S"] for r in _seeds)
       and all(p["auc"]["difference"] > 0 for p in _vsp)
       and sum(p["auc"]["ci"][0] > 0 for p in _vsp) == 1
       and 1.5 < min(g["matched"]["case"] / v["matched"]["case"] for g, v in zip(_gsp, _vsp))
       and max(g["matched"]["case"] / v["matched"]["case"] for g, v in zip(_gsp, _vsp)) < 2.5)
if not _ok:
    print("FAIL seeds claims (seed 0 exact; intervals; accuracy below; AUC 5/5 positive, 1/5 "
          "excluding zero; 'doubles')"); sys.exit(1)

# Claims no single literal carries.
assert m50["total"] - m50["group"] - m50["case"] < 1e-12
if not r_cost_la < 0.1 * r_cost_tde:
    print("FAIL 'under a tenth of TDE's cost in R@50'")
    sys.exit(1)
if [len(tiers[t]) for t in ("head", "body", "tail")] != [9, 26, 15]:
    print("FAIL tier sizes 9 / 26 / 15")
    sys.exit(1)
if sum(x > 0 for x in tail_rec) != 1 or sum(x > 0 for x in tail_base) != 0:
    print("FAIL 'baseline recalls none [of the tail], TDE recalls one'")
    sys.exit(1)
if not (round(100 * la50["total"]) == 9 and round(100 * m50["total"]) == 10):
    print("FAIL 'nine of the ten points'")
    sys.exit(1)

# confounding-sensitivity bound (Corollary: worst-case)
sens = load("sensitivity_bound_check.json")
CHECKS += [
    ("sens class-pair dR", "4experiments.tex", "0.01439",
     sens["delta_r_class_pair_phi"], 1e-5),
    ("sens subject dR", "4experiments.tex", "0.02181",
     sens["delta_r_subject_only_phi"], 1e-5),
    ("sens empirical bias", "appendix.tex", "0.00742",
     sens["empirical_coarsening_bias"], 5e-5),
    ("sens free bound", "appendix.tex", "14.00",
     sens["crude_cauchy_schwarz_bound"], 5e-3),
    ("sens min rho", "appendix.tex", "0.00053",
     sens["minimum_rho_for_bound_to_hold"], 5e-6),
    ("sens superseded bound", "appendix.tex", "50.00",
     sens["superseded_popoviciu_bound"], 5e-3),
    ("sens looseness ratio", "appendix.tex", "1{,}887", sens["looseness_ratio"], 1.0),
]


# Sharp per-cell sensitivity bound and robustness value.  Section 3.5 reports these; the
# file was committed in the fourth revision but cited nowhere and checked by nothing
# until the 2026-09 panel found the omission.
sharp = load("sensitivity_bound.json")
CHECKS += [
    ("sharp bound B", "appendix.tex", "0.23284", sharp["bound_B"], 5e-6),
    ("sharp bound at rho=0.1", "appendix.tex", "0.02328",
     sharp["bound_B"] / 10.0, 5e-6),
    ("robustness value", "appendix.tex", "0.06127",
     sharp["robustness_value_rho_dagger"], 5e-6),
    ("sharp bound dR", "appendix.tex", "0.01427", sharp["reasoning_gain"], 5e-6),
]


# text classification cross-domain study (20-Newsgroups-LT)
txt = load("text_lt_results.json")
txt_rows = {f"{r['prior_feature']}|{r['new']}": r for r in txt["comparisons"]}
CHECKS += [
    ("text CE accuracy", "appendix.tex", "0.3532", txt["accuracy"]["CE"], 5e-4),
    ("text CB accuracy", "appendix.tex", "0.3960", txt["accuracy"]["CB"], 5e-4),
    ("text DRW accuracy", "appendix.tex", "0.3776", txt["accuracy"]["DRW"], 5e-4),
    ("text CB superclass dT", "appendix.tex", "0.11388",
     txt_rows["superclass|MLP-CB"]["total_gain"], 1e-5),
    ("text CB superclass dP", "appendix.tex", "0.07071",
     txt_rows["superclass|MLP-CB"]["prior_gain"], 1e-5),
    ("text CB superclass dR", "appendix.tex", "0.04317",
     txt_rows["superclass|MLP-CB"]["reasoning_gain"], 1e-5),
    ("text CB global dR", "appendix.tex", "0.04185",
     txt_rows["global|MLP-CB"]["reasoning_gain"], 1e-5),
    ("text CB tier dR", "appendix.tex", "0.03578",
     txt_rows["tier|MLP-CB"]["reasoning_gain"], 1e-5),
    ("text DRW superclass dT", "appendix.tex", "0.11490",
     txt_rows["superclass|MLP-DRW"]["total_gain"], 1e-5),
    ("text DRW superclass dP", "appendix.tex", "0.11335",
     txt_rows["superclass|MLP-DRW"]["prior_gain"], 1e-5),
    ("text DRW superclass dR", "appendix.tex", "0.00155",
     txt_rows["superclass|MLP-DRW"]["reasoning_gain"], 1e-5),
    ("text DRW global dR", "appendix.tex", "-0.00319",
     txt_rows["global|MLP-DRW"]["reasoning_gain"], 1e-5),
    ("text DRW tier dR", "appendix.tex", "-0.00901",
     txt_rows["tier|MLP-DRW"]["reasoning_gain"], 1e-5),
]
tier_rows = {(r["new"], r["tier"]): r for r in txt["per_tier_at_superclass_phi"]}
CHECKS += [
    ("text CB few-shot dR", "appendix.tex", "0.04991",
     tier_rows[("MLP-CB", "few-shot (<20)")]["alignment_gain"], 1e-5),
    ("text CB medium-shot dR", "appendix.tex", "0.19213",
     tier_rows[("MLP-CB", "medium-shot (20-100)")]["alignment_gain"], 1e-5),
    ("text CB many-shot dR", "appendix.tex", "-0.09227",
     tier_rows[("MLP-CB", "many-shot (>100)")]["alignment_gain"], 1e-5),
    ("text DRW few-shot dR", "appendix.tex", "0.07352",
     tier_rows[("MLP-DRW", "few-shot (<20)")]["alignment_gain"], 1e-5),
    ("text DRW medium-shot dR", "appendix.tex", "0.07171",
     tier_rows[("MLP-DRW", "medium-shot (20-100)")]["alignment_gain"], 1e-5),
    ("text DRW many-shot dR", "appendix.tex", "-0.10753",
     tier_rows[("MLP-DRW", "many-shot (>100)")]["alignment_gain"], 1e-5),
]

# A check can only vouch for a file the manuscript actually pulls in.  Twice now a
# restructure has left an old .tex on disk, unreferenced, with the checks still reading
# it -- they pass while the live text says something else.  So resolve main.tex's
# \input graph first and refuse to read anything outside it.
def inputted_files(driver: pathlib.Path) -> list[str]:
    base, seen, order, queue = driver.parent, set(), [], [driver.name]
    while queue:
        name = queue.pop(0)
        if name in seen:
            continue
        seen.add(name)
        order.append(name)
        body = re.sub(r"(?m)(?<!\\)%.*$", "", (base / name).read_text())
        for ref in re.findall(r"\\input\{([^}]+)\}", body):
            queue.append(ref if ref.endswith(".tex") else ref + ".tex")
    return order


driver_arg = sys.argv[sys.argv.index("--driver") + 1] if "--driver" in sys.argv else None

if driver_arg is None:
    CHECKS = [c for c in CHECKS if not c[0].startswith(("cvpr ", "rec ", "auc ", "ps ", "acc ", "path ", "iet ", "vrank ", "seeds "))]
    LIVE = set(inputted_files(MS / "main.tex"))
    orphans = sorted({f for _, f, *_ in CHECKS} - LIVE)
    if orphans:
        print("these files are checked but not \\input by main.tex: " + ", ".join(orphans))
        sys.exit(1)

    def text_for(fname: str, label: str = "") -> str:
        return (MS / fname).read_text()
    where = None
else:
    driver = (ROOT / driver_arg).resolve()
    files = inputted_files(driver)
    whole = "\n".join((driver.parent / f).read_text() for f in files)
    supp = "\n".join((driver.parent / f).read_text() for f in files if f.startswith("supp/"))
    paper = "\n".join((driver.parent / f).read_text() for f in files if not f.startswith("supp/"))
    print(f"checking against {driver_arg}: {len(files)} files in its \\input closure\n")

    # Which numbers the paper itself must print is declared, not inferred. Inferring it
    # from the current text is circular: a number mistyped in the paper vanishes from the
    # paper, gets reclassified as supplementary-only, and passes on a correct copy there.
    # A mutation test caught exactly that. So the scope lives in a committed manifest,
    # frozen from a verified state with --freeze-paper-scope, and is enforced on every run.
    manifest = driver.parent / "paper_numbers.txt"
    labels = {c[0] for c in CHECKS}
    if "--freeze-paper-scope" in sys.argv:
        scoped = sorted(c[0] for c in CHECKS if c[2] in paper)
        manifest.write_text("# Checks whose number the paper itself must print, not only the\n"
                            "# supplementary. Written by verify_manuscript_numbers.py\n"
                            "# --freeze-paper-scope from a state in which every check passed.\n"
                            + "\n".join(scoped) + "\n")
        print(f"froze {len(scoped)} paper-scoped checks to {manifest.relative_to(ROOT)}\n")
    PAPER_SCOPED = set()
    if manifest.exists():
        PAPER_SCOPED = {l.strip() for l in manifest.read_text().splitlines()
                        if l.strip() and not l.startswith("#")}
        unknown = sorted(PAPER_SCOPED - labels)
        if unknown:
            print("paper_numbers.txt names checks that no longer exist: " + ", ".join(unknown))
            sys.exit(1)

    def text_for(fname: str, label: str = "") -> str:
        return paper if label in PAPER_SCOPED else whole

    def where(literal: str) -> str:
        return "paper" if literal in paper else "supp " if literal in supp else "     "

fails = []
in_paper = 0
for label, fname, literal, actual, tol in CHECKS:
    text = text_for(fname, label)
    present = literal in text
    if isinstance(actual, str):
        ok_val = True
    else:
        try:
            quoted = float(literal.replace("{,}", "").replace(",", "")
                           .replace("+", ""))
            ok_val = abs(abs(quoted) - abs(float(actual))) <= tol
        except ValueError:
            ok_val = False
    status = "OK " if (present and ok_val) else "FAIL"
    if status == "FAIL":
        fails.append((label, fname, literal, actual, present, ok_val))
    loc = f"[{where(literal)}] " if where else ""
    in_paper += bool(where) and where(literal) == "paper"
    print(f"{status} {loc}{label:34s} '{literal}' vs {actual}"
          + ("" if present else ("   [NOT IN THE PAPER]" if where and label in PAPER_SCOPED
                                 else "   [NOT IN TEXT]"))
          + ("" if ok_val else "   [VALUE MISMATCH]"))

print()
if fails:
    print(f"{len(fails)} CHECK(S) FAILED")
    sys.exit(1)
print(f"all {len(CHECKS)} manuscript numbers trace to committed results")
if where:
    print(f"{in_paper} of them are printed in the paper itself, the rest in the supplementary")
