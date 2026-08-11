"""QA: check that the numbers quoted in the manuscript trace to committed results.

Not a general parser -- it asserts a curated list of (claim, manuscript file,
literal string, expected value from a results file) so that a transcription
slip or a stale figure after a rerun fails loudly.

Run: conda run -n py313 python experiments/verify_manuscript_numbers.py
"""
from __future__ import annotations

import json
import pathlib
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
    ("cal table CB raw dR", "4experiments.tex", "-0.19427",
     recal["rows"]["CB vs CE (raw)"]["dR"], 1e-5),
    ("cal table CB cal dR", "4experiments.tex", "-0.23991",
     recal["rows"]["CB vs CE (cal-both)"]["dR"], 1e-5),
    ("cal table DRW cal dT", "4experiments.tex", "+0.02173",
     recal["rows"]["DRW vs CE (cal-both)"]["dT"], 1e-5),
    ("cal table DRW cal dR", "4experiments.tex", "+0.01957",
     recal["rows"]["DRW vs CE (cal-both)"]["dR"], 1e-5),
    ("cal table control dP", "4experiments.tex", "+0.37960",
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
    ("bridge spatial acc pts", "4experiments.tex", "0.51",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["d_acc"] * 100, 0.006),
    ("bridge spatial mrr pts", "4experiments.tex", "0.60",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["d_mrr"] * 100, 0.006),
    ("bridge spatial r5 pts", "4experiments.tex", "0.86",
     bridge["MLP-SPATIAL-S vs MLP-CLASS-S"]["d_r5"] * 100, 0.006),
    ("bridge clip acc drop", "4experiments.tex", "3.07",
     -bridge["MLP-VISUAL-S vs MLP-SPATIAL-S"]["d_acc"] * 100, 0.006),
    ("bridge clip r5 drop", "4experiments.tex", "2.21",
     -bridge["MLP-VISUAL-S vs MLP-SPATIAL-S"]["d_r5"] * 100, 0.006),
    ("bridge clip pm acc drop", "4experiments.tex", "2.17",
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
    ("VG relations audited", "4experiments.tex", "227,337",
     vg["comparisons"][0]["n_identified"], 0),
    ("VG test relations", "4experiments.tex", "229,605", vgv["n_test"], 0),
    ("CLIP total gain", "4experiments.tex", "-0.04655",
     vgv_rows["MLP-VISUAL-S|MLP-SPATIAL-S"]["total_gain"], 1e-5),
    ("CLIP alignment gain", "4experiments.tex", "0.00641",
     vgv_rows["MLP-VISUAL-S|MLP-SPATIAL-S"]["reasoning_gain"], 1e-5),
    ("CIFAR CB accuracy", "4experiments.tex", "0.2627",
     cif["accuracy"]["CB"], 1e-4),
    ("CIFAR DRW accuracy", "4experiments.tex", "0.3874",
     cif["accuracy"]["DRW"], 1e-4),
]


# seed/ratio robustness table
ms = load("cifar_multiseed.json")
CHECKS += [
    ("robust CB r10 dR", "4experiments.tex", "-0.06903", ms["r10_s0"]["CB cal"]["dR"], 1e-5),
    ("robust CB r50 dR", "4experiments.tex", "-0.24409", ms["r50_s0"]["CB cal"]["dR"], 1e-5),
    ("robust DRW r100s1 dR", "4experiments.tex", "+0.00748",
     ms["r100_s1"]["DRW cal"]["dR"], 1e-5),
    ("robust DRW r100s2 dR", "4experiments.tex", "+0.03124",
     ms["r100_s2"]["DRW cal"]["dR"], 1e-5),
    ("robust LA r50 dR", "4experiments.tex", "+0.03768", ms["r50_s0"]["LA cal"]["dR"], 1e-5),
    ("robust CB mean", "4experiments.tex", "-0.25108",
     ms["across_seeds_r100"]["CB cal.dR"]["mean"], 1e-5),
    ("robust DRW mean", "4experiments.tex", "+0.01953",
     ms["across_seeds_r100"]["DRW cal.dR"]["mean"], 1e-5),
    ("robust r10 CE acc", "4experiments.tex", "0.5388",
     ms["r10_s0"]["accuracy"]["CE"], 1e-4),
    ("robust r50 LA acc", "4experiments.tex", "0.4550",
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

fails = []
for label, fname, literal, actual, tol in CHECKS:
    text = (MS / fname).read_text()
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
    print(f"{status} {label:34s} '{literal}' vs {actual}"
          + ("" if present else "   [NOT IN TEXT]")
          + ("" if ok_val else "   [VALUE MISMATCH]"))

print()
if fails:
    print(f"{len(fails)} CHECK(S) FAILED")
    sys.exit(1)
print(f"all {len(CHECKS)} manuscript numbers trace to committed results")
