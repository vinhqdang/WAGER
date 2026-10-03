#!/usr/bin/env python3
"""Supplementary tables for the SGG audit, written from the results files.

  cvpr2027/supp/tab_recall_split.tex     mean-recall split, every protocol and K,
                                          every comparison, with tiers
  cvpr2027/supp/tab_recall_validation.tex re-scored vs official recall
  cvpr2027/supp/tab_proper_configs.tex   proper-score split, every configuration

Run: python experiments/make_cvpr_recall_tables.py
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = ROOT / "cvpr2027" / "supp"
DDIR = ROOT / "data/vg_motifs/wager_sgg"

COMPARISONS = [  # (results file, label)
    ("sgg_recall_split.json", "TDE vs base"),
    ("sgg_recall_split_la1_vs_none.json", r"LA$_{1}$ vs base"),
    ("sgg_recall_split_la0.5_vs_none.json", r"LA$_{.5}$ vs base"),
    ("sgg_recall_split_TDE_vs_la1.json", r"TDE vs LA$_{1}$"),
    ("sgg_recall_split_ctx_vs_none.json", "ctx vs base"),
    ("sgg_recall_split_vis_ctx_vs_none.json", "vis+ctx vs base"),
    ("sgg_recall_split_TDE_vs_ctx.json", "TDE vs ctx"),
]


def f4(x):
    return f"{x:+.4f}".replace("0.", ".", 1)


def ci(c):
    return r"{\scriptsize$[" + f4(c[0]) + "," + f4(c[1]) + r"]$}"


def recall_split():
    lines = [r"\begin{tabular}{@{}llrrrl@{}}", r"\toprule",
             r"Comparison & Protocol & $\Delta mR$ & group & case & case 95\% CI \\",
             r"\midrule"]
    for k, (fn, label) in enumerate(COMPARISONS):
        d = json.loads((RES / fn).read_text())["results"]
        first = True
        for mode, name in (("gc", "mR"), ("ng", "ng-mR")):
            for K in (20, 50, 100):
                m = d[f"{mode}@{K}"]["mean_recall"]
                lines.append(f"{label if first else ''} & {name}@{K} & ${f4(m['total'])}$ & "
                             f"${f4(m['group'])}$ & ${f4(m['case'])}$ & {ci(m['case_ci'])} \\\\")
                first = False
        if k < len(COMPARISONS) - 1:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tiers():
    lines = [r"\begin{tabular}{@{}llrrrl@{}}", r"\toprule",
             r"Comparison & Tier & $\Delta mR@50$ & group & case & case 95\% CI \\",
             r"\midrule"]
    for k, (fn, label) in enumerate(COMPARISONS[:4]):
        d = json.loads((RES / fn).read_text())["results"]["gc@50"]
        for j, t in enumerate(("head", "body", "tail")):
            m = d[f"mean_recall_{t}"]
            lines.append(f"{label if j == 0 else ''} & {t} & ${f4(m['total'])}$ & "
                         f"${f4(m['group'])}$ & ${f4(m['case'])}$ & {ci(m['case_ci'])} \\\\")
        if k < 3:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def validation():
    s = json.loads((DDIR / "summary.json").read_text())
    audit = json.loads((RES / "sgg_audit_motifs.json").read_text())["recalls"]
    off = {"none": audit["MOTIFS"], "TDE": audit["MOTIFS-TDE"]}
    keys = [("R@50", "predcls_recall@50"), ("mR@50", "predcls_mean_recall@50"),
            ("ng-R@50", "predcls_recall_nogc@50"), ("ng-mR@50", "predcls_ng_mean_recall@50"),
            ("mR@100", "predcls_mean_recall@100")]
    lines = [r"\begin{tabular}{@{}l" + "r" * len(keys) + "@{}}", r"\toprule",
             "Model & " + " & ".join(k for k, _ in keys) + r" \\", r"\midrule"]
    for v, name in (("none", "base, official"), ("none", "base, re-scored"),
                    ("TDE", "TDE, official"), ("TDE", "TDE, re-scored"),
                    ("la1", r"LA$_1$, re-scored"), ("la0.5", r"LA$_{.5}$, re-scored")):
        if "official" in name:
            vals = [off[v][o] for _, o in keys]
        else:
            r = s["recalls"][v]
            vals = [r[k.replace("ng-", "ng_")] for k, _ in keys]
        lines.append(name + " & " + " & ".join(f"{x:.4f}" for x in vals) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def proper_configs():
    rows = json.loads((RES / "sgg_audit_motifs.json").read_text())["comparisons"]

    def label(r):
        cmp = (r["comparison"].replace("MOTIFS-TDE", "TDE")
               .replace("MOTIFS logit-adjusted tau=1", "LA$_1$")
               .replace("MOTIFS logit-adjusted tau=0.5", "LA$_{.5}$")
               .replace(" vs MOTIFS", " vs base"))
        reg = r.get("regime", "raw")
        if r.get("prior_feature") == "subject class":
            reg = "raw, subject only"
        return cmp, reg, "quad." if r["score"] == "brier" else "log"

    lines = [r"\begin{tabular}{@{}lllrrrl@{}}", r"\toprule",
             r"Comparison & Outputs & Score & $\hdT$ & $\hdP$ & $\hdR$ & $\hdR$ 95\% CI \\",
             r"\midrule"]
    for r in rows:
        cmp, reg, sc = label(r)
        reg = reg.replace("calibration-matched", "matched").replace("audit-half raw", "raw, audit half")
        lo, hi = r["reasoning_ci"]
        lines.append(f"{cmp} & {reg} & {sc} & ${r['total_gain']:+.5f}$ & "
                     f"${r['prior_gain']:+.5f}$ & ${r['reasoning_gain']:+.5f}$ & "
                     f"{{\\scriptsize$[{lo:+.5f},{hi:+.5f}]$}} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def auc():
    rows = json.loads((RES / "sgg_rank_contrast.json").read_text())["rows"]
    lab = {"none": "base", "TDE": "TDE", "la1": r"LA$_1$", "la0.5": r"LA$_{.5}$",
           "ctx": "ctx", "vis_ctx": "vis+ctx", "vis": "vis"}
    lines = [r"\begin{tabular}{@{}lrrrl@{}}", r"\toprule",
             r"Comparison & AUC new & AUC old & $\Delta$AUC & 95\% CI \\", r"\midrule"]
    for r in rows:
        lines.append(f"{lab[r['new']]} vs {lab[r['old']]} & {r['auc_new']:.4f} & "
                     f"{r['auc_old']:.4f} & ${f4(r['difference'])}$ & {ci(r['ci'])} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def main():
    head = "% generated by experiments/make_cvpr_recall_tables.py -- do not edit\n"
    (OUT / "tab_recall_split.tex").write_text(head + recall_split() + "\n")
    (OUT / "tab_recall_tiers.tex").write_text(head + tiers() + "\n")
    (OUT / "tab_recall_validation.tex").write_text(head + validation() + "\n")
    (OUT / "tab_recall_auc.tex").write_text(head + auc() + "\n")
    (OUT / "tab_proper_configs.tex").write_text(head + proper_configs() + "\n")
    print("wrote", ", ".join(p.name for p in sorted(OUT.glob("tab_*.tex"))))


if __name__ == "__main__":
    main()
