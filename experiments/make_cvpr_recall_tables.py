#!/usr/bin/env python3
"""Supplementary tables for the SGG audit, written from the results files.

  cvpr2027/supp/tab_recall_split.tex     mean-recall split, every protocol and K,
                                          every comparison, with tiers
  cvpr2027/supp/tab_recall_validation.tex re-scored vs official recall
  cvpr2027/supp/tab_proper_configs.tex   proper-score split, every configuration
  cvpr2027/supp/tab_split_robustness.tex  matched split over 20 image splits
  cvpr2027/supp/tab_label_shift.tex       split under a within-cell label shift
  cvpr2027/supp/tab_predicate_merge.tex   split after merging predicates
  cvpr2027/supp/tab_clip_zeroshot.tex     zero-shot CLIP on the canonical relations
  cvpr2027/supp/tab_rank_weighting.tex    within-cell AUC under both weightings
  cvpr2027/supp/tab_tier_pair_auc.tex     AUC change by predicate-tier pair
  cvpr2027/supp/tab_recalibration.tex     matched split under three recalibration families
  cvpr2027/supp/tab_label_shift_path.tex  case-level part along a path of label mixes
  cvpr2027/supp/tab_small_cells.tex       interval coverage with small cells

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


def vg_seeds():
    d = json.loads((RES / "vg_visual_seeds.json").read_text())
    short = {"MLP-VISUAL-S": "CLIP", "MLP-SPATIAL-S": "geometry",
             "MLP-VISGEO-S": "CLIP+geometry", "MLP-CLASS-S": "class"}
    pairs = ["MLP-VISUAL-S vs MLP-SPATIAL-S", "MLP-VISGEO-S vs MLP-SPATIAL-S",
             "MLP-VISGEO-S vs MLP-VISUAL-S"]
    lines = [r"\begin{tabular}{@{}llrrrrll@{}}", r"\toprule",
             r"Comparison & Seed & acc.\ new & acc.\ old & group & case & case 95\% CI & "
             r"$\Delta$AUC [95\% CI] \\", r"\midrule"]
    for k, pair in enumerate(pairs):
        new, old = pair.split(" vs ")
        for j, sd in enumerate(d["seeds"]):
            row = d["per_seed"][str(sd)]
            m, a = row["pairs"][pair]["matched"], row["pairs"][pair]["auc"]
            lab = f"{short[new]} vs {short[old]}" if j == 0 else ""
            lines.append(f"{lab} & {sd} & {row['accuracy'][new]:.4f} & {row['accuracy'][old]:.4f} & "
                         f"${m['group']:+.5f}$ & ${m['case']:+.5f}$ & "
                         f"{{\\scriptsize$[{m['case_ci'][0]:+.5f},{m['case_ci'][1]:+.5f}]$}} & "
                         f"${f4(a['difference'])}$ {ci(a['ci'])} \\\\")
        if k < len(pairs) - 1:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def f5(x):
    return f"{x:+.5f}"


def ci5(c):
    return r"{\scriptsize$[" + f5(c[0]) + "," + f5(c[1]) + r"]$}"


ROB_LABELS = {"TDE": "TDE vs base", "la1": r"LA$_{1}$ vs base", "ietrans": "IETrans vs base",
              "TDE common-T": "TDE vs base, one $T$"}


def split_robustness():
    d = json.loads((RES / "sgg_split_robustness.json").read_text())
    n = d["n_splits"]
    lines = [r"\begin{tabular}{@{}llrrrrr@{}}", r"\toprule",
             r"Comparison & Score & mean & sd & min & max & CI $\not\ni 0$ \\", r"\midrule"]
    for k, v in enumerate(("TDE", "la1", "ietrans", "TDE common-T")):
        for j, sc in enumerate(("brier", "log")):
            m = d["summary"][f"{v} {sc}"]
            lines.append(f"{ROB_LABELS[v] if j == 0 else ''} & {'quadratic' if sc == 'brier' else 'log'} & "
                         f"${f5(m['mean'])}$ & ${m['sd']:.5f}$ & ${f5(m['min'])}$ & ${f5(m['max'])}$ & "
                         f"{m['n_excluding_zero']}/{n} \\\\")
        if k < 3:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def label_shift():
    d = json.loads((RES / "label_shift.json").read_text())
    short = {"TDE vs MOTIFS": "TDE vs base", "logit-adjusted vs MOTIFS": r"LA$_{1}$ vs base",
             "IETrans vs MOTIFS": "IETrans vs base", "TDE vs logit-adjusted": r"TDE vs LA$_{1}$",
             "class-only vs FREQ": "class vs FREQ", "geometry vs class-only": "geometry vs class",
             "CLIP vs class-only": "CLIP vs class", "CLIP vs geometry": "CLIP vs geometry"}
    lines = [r"\begin{tabular}{@{}lrrlrrl@{}}", r"\toprule",
             r"& \multicolumn{3}{c}{benchmark labels} & \multicolumn{3}{c}{uniform within cells} \\",
             r"\cmidrule(lr){2-4}\cmidrule(l){5-7}",
             r"Comparison & group & case & case 95\% CI & group & case & case 95\% CI \\", r"\midrule"]
    for k, r in enumerate(d["rows"]):
        o, s_ = r["original"], r["shifted"]
        if k == 4:
            lines.append(r"\midrule")
        lines.append(f"{short[r['comparison']]} & ${f5(o['group'])}$ & ${f5(o['case'])}$ & {ci5(o['case_ci'])} & "
                     f"${f5(s_['group'])}$ & ${f5(s_['case'])}$ & {ci5(s_['case_ci'])} \\\\")
    lines += [r"\midrule", r"& \multicolumn{3}{c}{$\Delta$AUC, benchmark labels} & "
              r"\multicolumn{3}{c}{$\Delta$AUC, uniform within cells} \\", r"\midrule"]
    for v, lab in (("TDE", "TDE vs base"), ("la1", r"LA$_{1}$ vs base"), ("ietrans", "IETrans vs base")):
        a = d["auc_sgg"][v]
        lines.append(f"{lab} & \\multicolumn{{3}}{{l}}{{${f4(a['original']['difference'])}$ "
                     f"{ci(a['original']['ci'])}}} & \\multicolumn{{3}}{{l}}{{${f4(a['shifted']['difference'])}$ "
                     f"{ci(a['shifted']['ci'])}}} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def predicate_merge():
    d = json.loads((RES / "predicate_merge.json").read_text())
    lab = {"TDE": "TDE", "la1": r"LA$_{1}$", "ietrans": "IETrans"}
    lines = [r"\begin{tabular}{@{}llrlrlrrl@{}}", r"\toprule",
             r"Merge & vs base & case & 95\% CI & case, single & $\Delta$AUC [95\% CI] & "
             r"$\Delta mR$ & group & case [95\% CI] \\", r"\midrule"]
    for k, (mname, res) in enumerate(d["merges"].items()):
        for j, v in enumerate(("TDE", "la1", "ietrans")):
            r = res[v]
            a, b = r["matched quadratic, all"], r["matched quadratic, single annotation"]
            m, au = r["mR@50"], r["auc"]
            first = f"{mname} ({res['n_classes']})" if j == 0 else ""
            lines.append(f"{first} & {lab[v]} & ${f5(a['case'])}$ & {ci5(a['case_ci'])} & ${f5(b['case'])}$ & "
                         f"${f4(au['difference'])}$ {ci(au['ci'])} & ${f4(m['total'])}$ & ${f4(m['group'])}$ & "
                         f"${f4(m['case'])}$ {ci(m['case_ci'])} \\\\")
        if k < 2:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def clip_zeroshot():
    d = json.loads((RES / "clip_zeroshot_audit.json").read_text())
    name = {"CLIP0": "zero-shot CLIP", "CLIP0+FREQ": "zero-shot CLIP + FREQ", "MOTIFS": "MOTIFS",
            "TDE": "TDE", "FREQ": "FREQ"}
    lines = [r"\begin{tabular}{@{}lrrrlrl@{}}", r"\toprule",
             r"Comparison & $\Delta T$ & group & case & case 95\% CI & case (log) & 95\% CI \\",
             r"\midrule"]
    for r in d["rows"]:
        b, lg = r["brier"], r["log"]
        lines.append(f"{name[r['new']]} vs {name[r['old']]} & ${f5(b['total'])}$ & ${f5(b['group'])}$ & "
                     f"${f5(b['case'])}$ & {ci5(b['case_ci'])} & ${f5(lg['case'])}$ & {ci5(lg['case_ci'])} \\\\")
    lines += [r"\midrule", r"Model & \multicolumn{2}{r}{top-1 acc.} & \multicolumn{2}{r}{within-cell AUC} & "
              r"\multicolumn{2}{r}{$T^*$} \\", r"\midrule"]
    for k in ("CLIP0", "CLIP0+FREQ", "FREQ", "MOTIFS", "TDE"):
        auc = d["auc"].get(k, d["auc"]["CLIP0"] if k == "CLIP0+FREQ" else None)
        lines.append(f"{name[k]} & \\multicolumn{{2}}{{r}}{{{d['accuracy'][k]:.4f}}} & "
                     f"\\multicolumn{{2}}{{r}}{{{auc:.4f}}} & \\multicolumn{{2}}{{r}}{{{d['temperatures'][k]:.2f}}} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


NAME = {"TDE": "TDE", "la1": r"LA$_{1}$", "ietrans": "IETrans+Rwt", "none": "base",
        "MLP-VISUAL-S": "CLIP", "MLP-SPATIAL-S": "geometry", "MLP-CLASS-S": "class"}


def rank_weighting():
    d = json.loads((RES / "sgg_rank_robustness.json").read_text())
    tl = json.loads((RES / "sgg_auc_tde_la.json").read_text())["rows"]
    cols = ("all, comparison", "all, relation", "audit half, comparison", "audit half, relation")
    lines = [r"\begin{tabular}{@{}llll@{}}", r"\toprule",
             r"Comparison & weighting & all relations & audit half \\", r"\midrule"]
    rows = d["sgg_auc"][:1] + tl + d["sgg_auc"][1:] + [None] + d["pixel_auc"]
    for r in rows:
        if r is None:
            lines.append(r"\midrule")
            continue
        for j, wt in enumerate(("comparison", "relation")):
            a, b = r[f"all, {wt}"], r[f"audit half, {wt}"]
            lab = f"{NAME[r['new']]} vs {NAME[r['old']]}" if j == 0 else ""
            lines.append(f"{lab} & {wt} & ${f4(a['difference'])}$ {ci(a['ci'])} & "
                         f"${f4(b['difference'])}$ {ci(b['ci'])} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def tier_pair():
    d = json.loads((RES / "sgg_rank_robustness.json").read_text())["tier_pair_auc"]
    order = ["head-head", "head-body", "head-tail", "body-body", "body-tail", "tail-tail",
             "all but head-head"]
    lines = [r"\begin{tabular}{@{}lr" + "l" * 3 + r"@{}}", r"\toprule",
             r"Tier pair & weight & TDE vs base & LA$_{1}$ vs base & IETrans+Rwt vs base \\",
             r"\midrule"]
    for t in order:
        w = d["TDE vs none"][t]["weight_share"]
        cells = [f"${f4(d[k][t]['difference'])}$ {ci(d[k][t]['ci'])}"
                 for k in ("TDE vs none", "la1 vs none", "ietrans vs none")]
        if t == "all but head-head":
            lines.append(r"\midrule")
        lines.append(f"{t} & {w:.3f} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def recalibration():
    d = json.loads((RES / "sgg_rank_robustness.json").read_text())["recalibration"]
    fams = ("temperature", "shared temperature", "temperature + class bias")
    lines = [r"\begin{tabular}{@{}llrrl@{}}", r"\toprule",
             r"Comparison & Matching & group & case & case 95\% CI \\", r"\midrule"]
    for k, r in enumerate(d):
        for sc in ("brier", "log"):
            for j, fam in enumerate(fams):
                m = r[f"{fam}, {sc}"]
                lab = (f"{NAME[r['new']]} vs base, {'quadratic' if sc == 'brier' else 'log'}"
                       if j == 0 else "")
                lines.append(f"{lab} & {fam} & ${f5(m['group'])}$ & ${f5(m['case'])}$ & "
                             f"{ci5(m['case_ci'])} \\\\")
        if k < len(d) - 1:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def label_shift_path():
    d = json.loads((RES / "label_shift.json").read_text())
    keys = ["original", "alpha=0.25", "alpha=0.5", "alpha=0.75", "shifted"]
    short = {"TDE vs MOTIFS": "TDE vs base", "logit-adjusted vs MOTIFS": r"LA$_{1}$ vs base",
             "IETrans vs MOTIFS": "IETrans+Rwt vs base", "TDE vs logit-adjusted": r"TDE vs LA$_{1}$"}
    lines = [r"\begin{tabular}{@{}l" + "r" * len(keys) + r"@{}}", r"\toprule",
             r"$\alpha$ & " + " & ".join(["0", ".25", ".5", ".75", "1"]) + r" \\", r"\midrule"]
    for r in d["rows"][:4]:
        lines.append(short[r["comparison"]] + " & " + " & ".join(f"${f5(r[k]['case'])}$" for k in keys)
                     + r" \\")
        lines.append(" & " + " & ".join(ci5(r[k]["case_ci"]) for k in keys) + r" \\")
    r0 = d["rows"][0]
    lines += [r"\midrule", "Kish $n$ & " + " & ".join(f"{r0[k]['kish_n']:,.0f}".replace(",", "{,}")
                                                     for k in keys) + r" \\",
              r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines)


def small_cells():
    d = json.loads((RES / "sim_small_cells.json").read_text())
    lines = [r"\begin{tabular}{@{}lrr@{}}", r"\toprule",
             r"Cell sizes & coverage & SE / SD \\", r"\midrule"]
    for k in ("n_c=2", "n_c=3", "n_c=4", "n_c=8", "n_c=20", "VG150 cell sizes"):
        lab = k.replace("n_c=", "every cell $n_c=") + "$" if k.startswith("n_c") else k
        lines.append(f"{lab} & {100 * d[k]['coverage']:.1f}\\% & {d[k]['se_over_sd']:.2f} \\\\")
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
    (OUT / "tab_vg_seeds.tex").write_text(head + vg_seeds() + "\n")
    (OUT / "tab_proper_configs.tex").write_text(head + proper_configs() + "\n")
    (OUT / "tab_split_robustness.tex").write_text(head + split_robustness() + "\n")
    (OUT / "tab_label_shift.tex").write_text(head + label_shift() + "\n")
    (OUT / "tab_predicate_merge.tex").write_text(head + predicate_merge() + "\n")
    (OUT / "tab_clip_zeroshot.tex").write_text(head + clip_zeroshot() + "\n")
    (OUT / "tab_rank_weighting.tex").write_text(head + rank_weighting() + "\n")
    (OUT / "tab_tier_pair_auc.tex").write_text(head + tier_pair() + "\n")
    (OUT / "tab_recalibration.tex").write_text(head + recalibration() + "\n")
    (OUT / "tab_label_shift_path.tex").write_text(head + label_shift_path() + "\n")
    (OUT / "tab_small_cells.tex").write_text(head + small_cells() + "\n")
    print("wrote", ", ".join(p.name for p in sorted(OUT.glob("tab_*.tex"))))


if __name__ == "__main__":
    main()
