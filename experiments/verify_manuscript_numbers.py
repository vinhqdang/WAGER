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
    ("consequence VISUAL' dP", "4experiments.tex", "+0.02401",
     cons_row("VISUAL' vs VISUAL")["prior"], 1e-5),
    ("consequence VISUAL' dR", "4experiments.tex", "+0.00111",
     cons_row("VISUAL' vs VISUAL")["reasoning"], 1e-5),
    ("consequence corrected dT", "4experiments.tex", "-0.02143",
     cons_row("VISUAL' vs SPATIAL")["total"], 1e-5),
    ("consequence corrected dR", "4experiments.tex", "+0.00752",
     cons_row("VISUAL' vs SPATIAL")["reasoning"], 1e-5),
    ("consequence both-corrected dR", "4experiments.tex", "+0.00663",
     cons_row("VISUAL' vs SPATIAL' (both corrected)")["reasoning"], 1e-5),
    ("consequence cal-matched dR", "4experiments.tex", "+0.00467",
     cons_row("VISUAL vs SPATIAL cal-both (audit half)")["reasoning"], 1e-5),
    ("bridge spatial dR", "4experiments.tex", "0.01023",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["dR"], 1e-5),
    ("bridge spatial acc pts", "appendix.tex", "0.51",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["d_acc"] * 100, 0.006),
    ("bridge spatial mrr pts", "appendix.tex", "0.60",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["d_mrr"] * 100, 0.006),
    ("bridge spatial r5 pts", "appendix.tex", "0.86",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["d_r5"] * 100, 0.006),
    ("bridge clip acc drop", "appendix.tex", "3.07",
     -bridge["MLP-VISUAL-S vs MLP-SPATIAL-S"]["d_acc"] * 100, 0.006),
    ("bridge clip r5 drop", "appendix.tex", "2.21",
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
    ("CLIP total gain", "4experiments.tex", "-0.04655",
     vgv_rows["MLP-VISUAL-S|MLP-SPATIAL-S"]["total_gain"], 1e-5),
    ("CLIP alignment gain", "4experiments.tex", "0.00641",
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
    ("cvpr raw log |dR| rounded", "5_audit.tex", "0.126", abs(sgg_raw_l["reasoning_gain"]), 5e-4),
    ("cvpr raw log |dP| rounded", "5_audit.tex", "0.159", abs(sgg_raw_l["prior_gain"]), 5e-4),
    ("cvpr subject dT", "5_audit.tex", "-0.11536", sgg_subj["total_gain"], 1e-5),
    ("cvpr subject dP", "5_audit.tex", "+0.10175", sgg_subj["prior_gain"], 1e-5),
    ("cvpr subject dP rounded", "5_audit.tex", "+0.102", sgg_subj["prior_gain"], 5e-4),
    ("cvpr subject dR rounded", "5_audit.tex", "-0.217", sgg_subj["reasoning_gain"], 5e-4),
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
    ("cvpr CLIP accuracy", "6_pixels.tex", "0.6161", vgv["accuracy"]["MLP-VISUAL-S"], 5e-5),
    ("cvpr geometry accuracy", "6_pixels.tex", "0.6467", vgv["accuracy"]["MLP-SPATIAL-S"], 5e-5),
    ("cvpr CLIP-geometry dP", "6_pixels.tex", "0.05296", vis_spa["prior_gain"], 1e-5),
    ("cvpr CLIP-geometry dR ci lo", "6_pixels.tex", "0.00514", vis_spa["reasoning_ci"][0], 1e-5),
    ("cvpr CLIP-geometry dR ci hi", "6_pixels.tex", "0.00769", vis_spa["reasoning_ci"][1], 1e-5),
    ("cvpr CLIP-geometry p", "6_pixels.tex", ".002", vis_spa["randomization_p"], 5e-4),
    ("cvpr CLIP-class dR", "6_pixels.tex", "0.01665",
     vgv_rows["MLP-VISUAL-S|MLP-CLASS-S"]["reasoning_gain"], 1e-5),
    ("cvpr geometry-class dR", "6_pixels.tex", "0.01023",
     vgv_rows["MLP-SPATIAL-S|MLP-CLASS-S"]["reasoning_gain"], 1e-5),
    ("cvpr train subsample", "6_pixels.tex", "100{,}000", vgv["n_train_relations"], 0),
    ("cvpr prior correction dP", "6_pixels.tex", "+0.02401", cons_rows["VISUAL' vs VISUAL"]["prior"], 1e-5),
    ("cvpr prior correction dR", "6_pixels.tex", "+0.00111",
     cons_rows["VISUAL' vs VISUAL"]["reasoning"], 1e-5),
    ("cvpr corrected deficit", "6_pixels.tex", "-0.02143", cons_rows["VISUAL' vs SPATIAL"]["total"], 1e-5),
    ("cvpr corrected dR", "6_pixels.tex", "+0.00752", cons_rows["VISUAL' vs SPATIAL"]["reasoning"], 1e-5),
    ("cvpr both corrected dR", "6_pixels.tex", "+0.00663",
     cons_rows["VISUAL' vs SPATIAL' (both corrected)"]["reasoning"], 1e-5),
    ("cvpr CLIP matched dR", "6_pixels.tex", "+0.00467",
     cons_rows["VISUAL vs SPATIAL cal-both (audit half)"]["reasoning"], 1e-5),
    ("cvpr CLIP matched ci lo", "6_pixels.tex", "+0.00314",
     cons_rows["VISUAL vs SPATIAL cal-both (audit half)"]["reasoning_ci"][0], 1e-5),
    ("cvpr CLIP matched ci hi", "6_pixels.tex", "+0.00621",
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
    ("cvpr CLIP matched dP", "6_pixels.tex", "0.04727",
     cons_rows["VISUAL vs SPATIAL cal-both (audit half)"]["prior"], 1e-5),
    ("cvpr CLIP prior-matched acc gap, points", "6_pixels.tex", "2.17",
     bridge_vs["d_acc_pm"] * 100, 5e-3),
    ("cvpr CLIP prior-matched MRR gap, points", "6_pixels.tex", "1.68",
     bridge_vs["d_mrr_pm"] * 100, 5e-3),
    ("cvpr CLIP prior-matched R@5 gap, points", "6_pixels.tex", "1.05",
     bridge_vs["d_r5_pm"] * 100, 5e-3),
]

# A claim no single literal carries: "under a tenth of [the total] even at the upper end of
# the log-score interval" (abstract, Secs. 1 and 5). The earlier "at most a twelfth" held for
# the point estimate only and failed at the interval bound; this asserts the bound itself.
worst = max(max(abs(x) for x in r["reasoning_ci"]) / abs(r["total_gain"])
            for r in (sgg_matched_q, sgg_matched_l))
if worst >= 0.1:
    print(f"FAIL 'under a tenth': worst matched interval bound |dR|/|dT| is {worst:.4f}")
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
    CHECKS = [c for c in CHECKS if not c[0].startswith("cvpr ")]
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
