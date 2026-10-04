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
           "ctx": "ctx", "vis_ctx": "vis+ctx", "vis": "vis", "ietrans": "IETrans",
           "ietrans_ctx": "IETrans w/o prior"}
    lines = [r"\begin{tabular}{@{}lrrrl@{}}", r"\toprule",
             r"Comparison & AUC new & AUC old & $\Delta$AUC & 95\% CI \\", r"\midrule"]
    for r in rows:
        lines.append(f"{lab[r['new']]} vs {lab[r['old']]} & {r['auc_new']:.4f} & "
                     f"{r['auc_old']:.4f} & ${f4(r['difference'])}$ & {ci(r['ci'])} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tde_path():
    d = json.loads((RES / "sgg_tde_path.json").read_text())
    lines = [r"\begin{tabular}{@{}lrrrlrl@{}}", r"\toprule",
             r"Step & $\Delta mR@50$ & group & case & case 95\% CI & $\Delta$AUC & 95\% CI \\",
             r"\midrule"]
    for r in d["path"]:
        m = r["mR@50 gc"]
        lines.append(f"{r['step']} & ${f4(m['total'])}$ & ${f4(m['group'])}$ & "
                     f"${f4(m['case'])}$ & {ci(m['case_ci'])} & "
                     f"${f4(r['auc']['difference'])}$ & {ci(r['auc']['ci'])} \\\\")
    lines += [r"\midrule", r"\multicolumn{7}{@{}l}{\emph{No graph constraint; last two columns: matched quadratic-score case-level part}} \\"]
    for r in d["path"]:
        m = r["mR@50 ng"]
        q = r["proper brier matched"]
        lines.append(f"{r['step']} & ${f4(m['total'])}$ & ${f4(m['group'])}$ & "
                     f"${f4(m['case'])}$ & {ci(m['case_ci'])} & ${q['case']:+.5f}$ & "
                     f"{{\\scriptsize$[{q['case_ci'][0]:+.5f},{q['case_ci'][1]:+.5f}]$}} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def logit_energy():
    e = json.loads((RES / "sgg_tde_path.json").read_text())["logit_energy"]
    lines = [r"\begin{tabular}{@{}lrrrrrr@{}}", r"\toprule",
             r"Logit term & rms & global & between & within & non-global rms & "
             r"corr.\ with $\log\pi$ \\", r"\midrule"]
    for k in ("frq", "vis", "ctx(post)", "ctx(avg)", "TDE", "baseline"):
        x = e[k]
        lines.append(f"{k} & {x['rms']:.2f} & {x['global']:.4f} & {x['between']:.4f} & "
                     f"{x['within']:.4f} & {x['rms_non_global']:.3f} & "
                     f"${x['corr_global_log_prior']:+.3f}$ \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


IET_COMPARISONS = [
    ("sgg_recall_split_ietrans_vs_none.json", "IETrans vs base"),
    ("sgg_recall_split_ietrans_vs_la1.json", r"IETrans vs LA$_{1}$"),
    ("sgg_recall_split_ietrans_vs_TDE.json", "IETrans vs TDE"),
    ("sgg_recall_split_ietrans_vs_ietrans_ctx.json", "IETrans vs IETrans w/o prior"),
]


def ietrans_split():
    lines = [r"\begin{tabular}{@{}llrrrl@{}}", r"\toprule",
             r"Comparison & Protocol / tier & $\Delta mR$ & group & case & case 95\% CI \\",
             r"\midrule"]
    for k, (fn, label) in enumerate(IET_COMPARISONS):
        d = json.loads((RES / fn).read_text())["results"]
        rows = [("mR@50", d["gc@50"]["mean_recall"]), ("ng-mR@50", d["ng@50"]["mean_recall"])]
        if k == 0:
            rows += [(f"mR@50 {t}", d["gc@50"][f"mean_recall_{t}"]) for t in ("head", "body", "tail")]
        for j, (name, m) in enumerate(rows):
            lines.append(f"{label if j == 0 else ''} & {name} & ${f4(m['total'])}$ & "
                         f"${f4(m['group'])}$ & ${f4(m['case'])}$ & {ci(m['case_ci'])} \\\\")
        if k < len(IET_COMPARISONS) - 1:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def ietrans_protocols():
    s = json.loads((ROOT / "data/vg_motifs/wager_ietrans/summary.json").read_text())
    off = s["official_protocol"]
    cols = [("R@50", "R@50"), ("mR@20", "mR@20"), ("mR@50", "mR@50"), ("mR@100", "mR@100"),
            ("ng-mR@50", "ng-mR@50")]
    lines = [r"\begin{tabular}{@{}l" + "r" * len(cols) + "@{}}", r"\toprule",
             "Test relations & " + " & ".join(c for c, _ in cols) + r" \\", r"\midrule"]
    for name, key in ((f"IETrans's ({s['ietrans_relations']:,})".replace(",", "{,}"),
                       "ietrans_dedup_test"),
                      (f"standard ({s['standard_relations']:,})".replace(",", "{,}"),
                       "standard_test")):
        lines.append(name + " & " + " & ".join(f"{off[f'{key} ietrans {k}']:.4f}"
                                               for _, k in cols) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def main():
    head = "% generated by experiments/make_cvpr_recall_tables.py -- do not edit\n"
    (OUT / "tab_recall_split.tex").write_text(head + recall_split() + "\n")
    (OUT / "tab_recall_tiers.tex").write_text(head + tiers() + "\n")
    (OUT / "tab_recall_validation.tex").write_text(head + validation() + "\n")
    (OUT / "tab_recall_auc.tex").write_text(head + auc() + "\n")
    (OUT / "tab_tde_path.tex").write_text(head + tde_path() + "\n")
    (OUT / "tab_logit_energy.tex").write_text(head + logit_energy() + "\n")
    (OUT / "tab_ietrans_split.tex").write_text(head + ietrans_split() + "\n")
    (OUT / "tab_ietrans_protocols.tex").write_text(head + ietrans_protocols() + "\n")
    (OUT / "tab_proper_configs.tex").write_text(head + proper_configs() + "\n")
    print("wrote", ", ".join(p.name for p in sorted(OUT.glob("tab_*.tex"))))


if __name__ == "__main__":
    main()
