"""Publication figure suite for the WAGER manuscript.

Generates eye-catching, self-explanatory figures from the *real* VG PredCls run
(results/sgg_figdata.npz, results/sgg_results.json), the Phase-1 simulation
(results/phase1_results.json) and the ablations (results/ablations.json).

All figures are written to manuscript/figures/ as PNG (and the concept/pipeline
schematics as PDF too, for crisp vector rendering in the paper).

Run with the py313 environment:
  python experiments/make_paper_figures.py
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "manuscript", "figures")
os.makedirs(FIG, exist_ok=True)

# --------------------------------------------------------------------------- #
# Style                                                                       #
# --------------------------------------------------------------------------- #
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "font.size": 10,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "legend.frameon": False,
    "figure.autolayout": False,
})
C_PRIOR = "#94a3b8"     # slate-400  (prior-fitting)
C_REASON = "#2563eb"    # blue-600   (reasoning)
C_WARM = "#ea580c"      # orange-600 (non-substantive)
C_GREEN = "#16a34a"     # green-600  (reasoning-supported)
C_RED = "#dc2626"       # red-600    (threshold)
C_INK = "#1e293b"       # slate-800
C_GOLD = "#d97706"

_EPS = 1e-12
_ONS = 2.0 / (2.0 - np.log(3.0))


def _load_figdata():
    return np.load(os.path.join(RES, "sgg_figdata.npz"), allow_pickle=True)


def _load_json(name):
    with open(os.path.join(RES, name)) as f:
        return json.load(f)


def cum_logwealth(d, c):
    """Cumulative log-wealth path of the one-sided ONS capital process (nats)."""
    d = np.asarray(d, dtype=np.float64)
    n = d.size
    lam_cap = 0.5 / c
    lam, A, logW = 0.0, 1.0, 0.0
    out = np.empty(n)
    z_prev = None
    for i in range(n):
        if z_prev is not None:
            grad = z_prev / (1.0 + lam * z_prev + _EPS)
            A += grad * grad
            lam += _ONS * grad / (A + _EPS)
            lam = min(max(lam, 0.0), lam_cap)
        zi = d[i]
        factor = 1.0 + lam * zi
        if factor < _EPS:
            factor = _EPS
        logW += np.log(factor)
        out[i] = logW
        z_prev = zi
    return out


MODELS = ["FREQ", "FREQ+OVERLAP", "MLP-CLASS", "MLP-SPATIAL", "MLP-SPATIAL+"]
MODEL_COLORS = {
    "FREQ": "#64748b", "FREQ+OVERLAP": "#0891b2", "MLP-CLASS": "#7c3aed",
    "MLP-SPATIAL": "#2563eb", "MLP-SPATIAL+": "#db2777",
}


def _save(fig, name):
    fig.savefig(os.path.join(FIG, name + ".png"), bbox_inches="tight")
    plt.close(fig)
    print("wrote", name + ".png")


# --------------------------------------------------------------------------- #
# Fig 1 - concept / teaser                                                    #
# --------------------------------------------------------------------------- #
def fig_concept():
    d = _load_figdata()
    y, phi, image = d["y"], d["phi"], d["image"]
    subj, obj = d["coarse"], d["obj"]
    sbox, obox = d["sbox"], d["obox"]
    qF = d["q_FREQ"]
    ov, pv = list(d["obj_vocab"]), list(d["pred_vocab"])

    # pick an image with 3-4 relations and a confidently-peaked FREQ cell
    uimg, counts = np.unique(image, return_counts=True)
    cand = uimg[(counts >= 3) & (counts <= 5)]
    best = None
    for im in cand:
        idx = np.where(image == im)[0]
        peak = np.mean([qF[i, y[i]] for i in idx])  # how well FREQ already nails it
        if best is None or peak > best[1]:
            best = (im, peak, idx)
    im, _, idx = best
    idx = idx[:4]

    fig = plt.figure(figsize=(13, 4.1))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.0], wspace=0.28)

    # (a) scene layout drawn from the real annotated boxes
    axa = fig.add_subplot(gs[0, 0])
    allb = np.vstack([sbox[idx], obox[idx]])
    x0 = min(allb[:, 0].min(), 0)
    y0 = min(allb[:, 1].min(), 0)
    x1 = (allb[:, 0] + allb[:, 2]).max()
    y1 = (allb[:, 1] + allb[:, 3]).max()
    pad = 0.06 * max(x1 - x0, y1 - y0)
    axa.set_xlim(x0 - pad, x1 + pad)
    axa.set_ylim(y1 + pad, y0 - pad)  # invert y (image coords)
    axa.set_aspect("equal")
    axa.set_xticks([]); axa.set_yticks([])
    for sp in axa.spines.values():
        sp.set_visible(True); sp.set_color("#cbd5e1")
    pal = ["#2563eb", "#db2777", "#16a34a", "#d97706"]
    drawn = {}
    for k, i in enumerate(idx):
        col = pal[k % len(pal)]
        for box, cls in [(sbox[i], subj[i]), (obox[i], obj[i])]:
            key = (round(float(box[0])), round(float(box[1])), int(cls))
            if key in drawn:
                continue
            drawn[key] = True
            r = Rectangle((box[0], box[1]), box[2], box[3], fill=False,
                          edgecolor=col, lw=2.0, alpha=0.85)
            axa.add_patch(r)
            axa.text(box[0] + 2, box[1] + 12, ov[int(cls)], color="white", fontsize=8,
                     fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.15", fc=col, ec="none", alpha=0.9))
        scx, scy = sbox[i, 0] + sbox[i, 2] / 2, sbox[i, 1] + sbox[i, 3] / 2
        ocx, ocy = obox[i, 0] + obox[i, 2] / 2, obox[i, 1] + obox[i, 3] / 2
        axa.annotate("", xy=(ocx, ocy), xytext=(scx, scy),
                     arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6, alpha=0.7,
                                     connectionstyle="arc3,rad=0.15"))
    axa.set_title("(a)  A scene and its annotated relations", loc="left")
    rels = ", ".join(f"$\\langle$ {ov[int(subj[i])]}, {pv[int(y[i])]}, {ov[int(obj[i])]} $\\rangle$"
                     for i in idx[:2])
    axa.set_xlabel(rels, fontsize=8.5, color=C_INK)

    # (b) the frequency shortcut for the first relation
    axb = fig.add_subplot(gs[0, 1])
    i0 = idx[0]
    probs = qF[i0]
    top = np.argsort(probs)[::-1][:7]
    if y[i0] not in top:
        top = np.append(top[:6], y[i0])
    names = [pv[int(t)] for t in top]
    vals = probs[top]
    colors = [C_RED if t == y[i0] else C_PRIOR for t in top]
    axb.barh(range(len(top))[::-1], vals, color=colors)
    axb.set_yticks(range(len(top))[::-1]); axb.set_yticklabels(names, fontsize=8.5)
    axb.set_xlabel("$P(\\mathrm{predicate}\\mid \\mathrm{subj},\\mathrm{obj})$  (train counts)")
    axb.set_title("(b)  A lookup table already wins", loc="left")
    axb.text(0.97, 0.05, f"FREQ$(y^\\star)$ = {probs[y[i0]]:.2f}", transform=axb.transAxes,
             ha="right", va="bottom", fontsize=9, color=C_RED, fontweight="bold")

    # (c) WAGER's question
    axc = fig.add_subplot(gs[0, 2])
    axc.axis("off")
    axc.set_title("(c)  WAGER asks: is the gain real?", loc="left")
    # mini RGR axis
    axc.add_patch(FancyBboxPatch((0.06, 0.55), 0.88, 0.32, boxstyle="round,pad=0.02",
                                 fc="#f1f5f9", ec="#cbd5e1"))
    axc.text(0.5, 0.79, "$\\mathrm{RGR}(f',f)=\\dfrac{\\Delta I_{\\mathrm{reason}}}"
                        "{\\Delta I_{\\mathrm{tot}}}$", ha="center", va="center", fontsize=12)
    axc.annotate("", xy=(0.94, 0.40), xytext=(0.06, 0.40),
                 arrowprops=dict(arrowstyle="-|>", color=C_INK, lw=1.5))
    axc.plot([0.5, 0.5], [0.36, 0.44], color=C_RED, lw=2)
    axc.text(0.5, 0.30, "0.5", ha="center", color=C_RED, fontsize=9)
    axc.text(0.27, 0.46, "prior-fitting", ha="center", color=C_WARM, fontsize=9, fontweight="bold")
    axc.text(0.74, 0.46, "reasoning", ha="center", color=C_GREEN, fontsize=9, fontweight="bold")
    axc.text(0.5, 0.13, "with a distribution-free,\nanytime-valid confidence interval",
             ha="center", va="center", fontsize=9, color=C_INK)

    fig.suptitle("WAGER: how much of a benchmark gain is genuine visual reasoning, "
                 "not annotation-frequency prior-fitting?", fontsize=12.5, fontweight="bold", y=1.04)
    _save(fig, "fig1_concept")


# --------------------------------------------------------------------------- #
# Fig 2 - method pipeline schematic                                           #
# --------------------------------------------------------------------------- #
def fig_pipeline():
    fig, ax = plt.subplots(figsize=(13, 4.4))
    ax.set_xlim(0, 14); ax.set_ylim(0, 6); ax.axis("off")

    def box(x, y, w, h, text, fc, ec=C_INK, fs=9.5, tc=C_INK):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                    fc=fc, ec=ec, lw=1.3))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=14, color=C_INK, lw=1.4))

    box(0.2, 2.4, 2.1, 1.2, "Cached probs\n$q_f(\\cdot\\mid x)$\n(GPU once)", "#e0f2fe")
    arrow(2.3, 3.0, 3.1, 3.0)
    box(3.1, 4.0, 2.3, 1.1, "Fold A (40%)\nself-prior projection\n$\\bar q_f(\\cdot\\mid\\phi)$  (Def. 1)", "#dcfce7")
    box(3.1, 0.9, 2.3, 1.1, "Fold B (60%)\nevaluation stream\n(image-blocked)", "#fef9c3")
    arrow(2.3, 3.1, 3.0, 4.4)
    arrow(2.3, 2.9, 3.0, 1.6)
    arrow(5.4, 4.3, 6.3, 3.4)
    arrow(5.4, 1.5, 6.3, 2.6)
    box(6.3, 2.4, 2.5, 1.2,
        "$d_i=\\log q_f(y_i\\mid x_i)$\n$-\\log\\bar q_f(y_i\\mid\\phi_i)$\n(Def. 2, clipped)", "#ede9fe")
    arrow(8.8, 3.0, 9.6, 3.0)
    box(9.6, 2.4, 2.3, 1.2, "ONS betting $\\lambda_i$\nwealth $W_n=\\prod(1{+}\\lambda_i d_i)$\n(Def. 3)", "#fee2e2")
    # two readouts
    arrow(11.9, 3.2, 12.6, 4.5)
    arrow(11.9, 2.8, 12.6, 1.6)
    box(12.4, 4.2, 1.5, 1.1, "e-value\n(Thm. 1\nVille)", "#dbeafe", fs=8.5)
    box(12.4, 0.8, 1.5, 1.1, "growth $=$\n$I_{\\mathrm{reason}}$\n(Thm. 2)", "#dbeafe", fs=8.5)

    ax.text(7.0, 5.7, "One capital process  →  certify  &  quantify;  two models  →  RGR with anytime-valid CI (Thm. 4)",
            ha="center", fontsize=10.5, color=C_INK, fontweight="bold")
    _save(fig, "fig2_pipeline")


# --------------------------------------------------------------------------- #
# Fig 3 - long-tail predicate distribution (the disease)                      #
# --------------------------------------------------------------------------- #
def fig_longtail():
    d = _load_figdata()
    ptr = d["pred_train"]
    pv = list(d["pred_vocab"])
    K = len(pv)
    counts = np.bincount(ptr, minlength=K).astype(float)
    order = np.argsort(counts)[::-1]
    cs = counts[order]
    frac = cs / cs.sum()
    cum = np.cumsum(frac)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    # (a) ranked frequency, log scale, head/body/tail bands
    n = len(cs)
    head, body = max(1, n // 10), max(2, n // 3)
    colors = [C_REASON if i < head else (C_GOLD if i < body else C_PRIOR) for i in range(n)]
    ax[0].bar(range(n), cs, color=colors, width=0.9)
    ax[0].set_yscale("log")
    ax[0].set_xlabel("predicate rank (of 50)")
    ax[0].set_ylabel("training instances (log)")
    ax[0].set_title("(a)  Visual Genome predicates are heavy-tailed", loc="left")
    for i in range(5):
        ax[0].text(order_i := i, cs[i] * 1.15, pv[int(order[i])], rotation=90,
                   fontsize=7.5, ha="center", va="bottom", color=C_INK)
    from matplotlib.patches import Patch
    ax[0].legend(handles=[Patch(color=C_REASON, label="head (top 10%)"),
                          Patch(color=C_GOLD, label="body"),
                          Patch(color=C_PRIOR, label="tail")], fontsize=8, loc="upper right")

    # (b) cumulative coverage
    ax[1].plot(range(1, n + 1), cum, color=C_INK, lw=2)
    ax[1].fill_between(range(1, n + 1), cum, color=C_REASON, alpha=0.12)
    k5 = cum[4]
    ax[1].axvline(5, ls=":", color=C_RED)
    ax[1].annotate(f"top-5 predicates\n= {k5*100:.0f}% of all relations",
                   xy=(5, k5), xytext=(16, 0.55), fontsize=9, color=C_RED,
                   arrowprops=dict(arrowstyle="->", color=C_RED))
    ax[1].set_xlabel("number of predicates (ranked)")
    ax[1].set_ylabel("cumulative share of instances")
    ax[1].set_ylim(0, 1.02)
    ax[1].set_title("(b)  A few predicates dominate the metric", loc="left")
    _save(fig, "fig3_longtail")


# --------------------------------------------------------------------------- #
# Fig 4 - wealth-process trajectories (testing by betting)                     #
# --------------------------------------------------------------------------- #
def fig_wealth():
    d = _load_figdata()
    K = len(list(d["pred_vocab"]))
    c = float(np.log(K))
    alpha = 0.05
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    for m in MODELS:
        dd = d[f"d_{m}"].astype(np.float64)
        perm = rng.permutation(len(dd))
        logW = cum_logwealth(dd[perm], c)
        log10W = logW / np.log(10.0)
        xs = np.linspace(0, len(dd) - 1, 600).astype(int)
        ax.plot(xs, log10W[xs], color=MODEL_COLORS[m], lw=2.0, label=m)
    ax.axhline(np.log10(1 / alpha), ls="--", color=C_RED, lw=1.3)
    ax.text(0.01, np.log10(1 / alpha) + 1.5, "reject $H_0$  ($W_n\\geq 1/\\alpha$, $\\alpha=0.05$)",
            color=C_RED, fontsize=8.5, transform=ax.get_yaxis_transform())
    ax.axhline(0, color=C_INK, lw=0.8, alpha=0.5)
    ax.set_xlabel("evaluation instances processed  $n$")
    ax.set_ylabel("$\\log_{10} W_n$  (capital, log scale)")
    ax.set_title("Testing by betting: capital grows only when the model\nout-predicts its own self-prior projection")
    ax.legend(loc="center right", fontsize=9)
    _save(fig, "fig4_wealth")


# --------------------------------------------------------------------------- #
# Fig 5 - information decomposition                                            #
# --------------------------------------------------------------------------- #
def fig_decomposition():
    S = _load_json("sgg_results.json")
    rows = {r["model"]: r for r in S["model_rows"]}
    names = MODELS
    I_prior = [rows[n]["I_prior"] for n in names]
    I_reason = [rows[n]["I_reason"] for n in names]
    acc = [rows[n]["test_acc"] for n in names]
    lo = [rows[n]["I_reason_lo"] for n in names]
    hi = [rows[n]["I_reason_hi"] for n in names]

    fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.4), gridspec_kw={"width_ratios": [1.2, 1]})
    x = np.arange(len(names))
    ax[0].bar(x, I_prior, color=C_PRIOR, label="$I_{\\mathrm{prior}}$  (frequency-fitting)")
    ax[0].bar(x, I_reason, bottom=I_prior, color=C_REASON,
              label="$I_{\\mathrm{reason}}$  (visual reasoning)")
    for i in range(len(names)):
        ax[0].text(i, I_prior[i] + max(I_reason[i], 0) + 0.07, f"acc\n{acc[i]:.3f}",
                   ha="center", fontsize=8, color=C_INK)
    ax[0].set_xticks(x); ax[0].set_xticklabels(names, rotation=18, ha="right", fontsize=9)
    ax[0].set_ylabel("information over uniform (nats)")
    ax[0].set_title("(a)  Almost all 'information' is prior-fitting", loc="left")
    ax[0].legend(loc="lower right", fontsize=9)

    # zoom on the reasoning channel with CIs
    colr = [C_WARM if v <= 0 else C_REASON for v in I_reason]
    yerr = np.array([[max(0, I_reason[i] - lo[i]) for i in range(len(names))],
                     [max(0, hi[i] - I_reason[i]) for i in range(len(names))]])
    ax[1].bar(x, I_reason, color=colr, yerr=yerr, capsize=4,
              error_kw=dict(ecolor=C_INK, lw=1))
    ax[1].axhline(0, color=C_INK, lw=1)
    ax[1].set_xticks(x); ax[1].set_xticklabels(names, rotation=18, ha="right", fontsize=9)
    ax[1].set_ylabel("$I_{\\mathrm{reason}}$ (nats)")
    ax[1].set_title("(b)  Reasoning channel (zoom): FREQ $\\approx 0$", loc="left")
    _save(fig, "fig5_decomposition")


# --------------------------------------------------------------------------- #
# Fig 6 - RGR forest plot with verdicts                                       #
# --------------------------------------------------------------------------- #
def fig_rgr_forest():
    S = _load_json("sgg_results.json")
    rr = S["rgr_rows"]
    labels = [f"{r['f_prime']}  vs  {r['f']}" for r in rr]
    rgr = [r["RGR"] for r in rr]
    lo = [r["fieller_lo"] for r in rr]
    hi = [r["fieller_hi"] for r in rr]
    verdict = [r["verdict"] for r in rr]

    order = np.argsort(rgr)
    labels = [labels[i] for i in order]; rgr = [rgr[i] for i in order]
    lo = [lo[i] for i in order]; hi = [hi[i] for i in order]
    verdict = [verdict[i] for i in order]

    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.axvspan(-0.05, 0.5, color=C_WARM, alpha=0.06)
    ax.axvspan(0.5, 1.05, color=C_GREEN, alpha=0.06)
    ax.axvline(0.5, ls="--", color=C_RED, lw=1.5, label="decision threshold (0.5)")
    for i in range(len(rgr)):
        col = C_GREEN if verdict[i] == "reasoning-supported" else C_WARM
        ax.errorbar(rgr[i], i, xerr=[[max(0, rgr[i] - lo[i])], [max(0, hi[i] - rgr[i])]],
                    fmt="o", color=col, ecolor=col, capsize=4, ms=9, lw=2)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(-0.05, 1.0)
    ax.set_ylim(-0.6, len(labels) - 0.1)
    ax.set_xlabel("Reasoning Gain Ratio (RGR) with Fieller CI")
    ax.set_title("Which VG PredCls gains are genuine reasoning?", pad=14)
    ax.text(0.24, -0.45, "non-substantive", color=C_WARM, ha="center",
            fontsize=9, fontweight="bold")
    ax.text(0.76, -0.45, "reasoning-supported", color=C_GREEN, ha="center",
            fontsize=9, fontweight="bold")
    _save(fig, "fig6_rgr_forest")


# --------------------------------------------------------------------------- #
# Fig 7 - Phase-1 validity & power                                            #
# --------------------------------------------------------------------------- #
def fig_phase1():
    P = _load_json("phase1_results.json")
    rec = P["gate_c_recovery"]
    rr = rec["rgr_rows"]
    true = [r["RGR_true"] for r in rr]
    est = [r["RGR_est"] for r in rr]
    flo = [r["fieller_lo"] for r in rr]
    fhi = [r["fieller_hi"] for r in rr]
    irows = rec["rows"]
    beta = [r["beta"] for r in irows]
    irt = [r["I_reason_true"] for r in irows]
    ire = [r["I_reason_est"] for r in irows]

    fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.9))
    # (a) RGR recovery
    yerr = np.array([[max(0, est[i] - flo[i]) for i in range(len(est))],
                     [max(0, fhi[i] - est[i]) for i in range(len(est))]])
    ax[0].errorbar(true, est, yerr=yerr, fmt="o", color=C_REASON, capsize=3, ms=6)
    mn, mx = min(true + est), max(true + est)
    ax[0].plot([mn, mx], [mn, mx], "--", color="gray", label="ideal $y=x$")
    ax[0].set_xlabel("ground-truth RGR"); ax[0].set_ylabel("WAGER estimate")
    ax[0].set_title(f"(a)  RGR recovery (r={rec['pearson_injectedRGR_vs_estRGR']:.3f})", loc="left")
    ax[0].legend(fontsize=8)
    # (b) I_reason recovery
    ax[1].plot(beta, irt, "s-", color="gray", label="true $I_{\\mathrm{reason}}$")
    ax[1].plot(beta, ire, "o-", color=C_GOLD, label="WAGER $\\hat I_{\\mathrm{reason}}$")
    ax[1].set_xlabel("injected reasoning weight $\\beta$")
    ax[1].set_ylabel("$I_{\\mathrm{reason}}$ (nats)")
    ax[1].set_title("(b)  Monotone reasoning recovery", loc="left")
    ax[1].legend(fontsize=8)
    # (c) gate summary
    ga, gb = P["gate_a_type_i"], P["gate_b_coverage"]
    cats = ["Type-I\nerror", "1$-$coverage"]
    obs = [ga["exceedance_rate"], 1 - gb["coverage"]]
    nom = [ga["alpha"], gb["alpha"]]
    xx = np.arange(2)
    ax[2].bar(xx - 0.18, obs, 0.36, color=C_REASON, label="observed")
    ax[2].bar(xx + 0.18, nom, 0.36, color=C_PRIOR, label="nominal $\\alpha$")
    ax[2].set_xticks(xx); ax[2].set_xticklabels(cats, fontsize=9)
    ax[2].set_ylabel("rate")
    ax[2].set_title("(c)  Validity gates hold", loc="left")
    for i, v in enumerate(obs):
        ax[2].text(i - 0.18, v + 0.002, f"{v:.3f}", ha="center", fontsize=8)
    ax[2].legend(fontsize=8)
    _save(fig, "fig7_phase1")


# --------------------------------------------------------------------------- #
# Fig 8 - ablations                                                           #
# --------------------------------------------------------------------------- #
def fig_ablations():
    A = _load_json("ablations.json")
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.7), sharey=True)

    def panel(a, rows, key, title):
        labs = [str(r[key]) for r in rows]
        vals = [r["RGR"] for r in rows]
        cols = [C_GREEN if r["verdict"] == "reasoning-supported" else C_WARM for r in rows]
        a.bar(range(len(rows)), vals, color=cols)
        a.axhline(0.5, ls="--", color=C_RED, lw=1.3)
        a.set_xticks(range(len(rows))); a.set_xticklabels(labs, fontsize=9)
        a.set_title(title, loc="left", fontsize=10)
        for i, v in enumerate(vals):
            a.text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=8)

    panel(ax[0], A["phi_granularity"], "phi", "(a)  prior feature $\\phi$")
    panel(ax[1], A["clip_c"], "c", "(b)  clip $c$")
    panel(ax[2], A["shrinkage_m"], "m", "(c)  shrinkage $m$")
    ax[0].set_ylabel("RGR (MLP-SPATIAL vs FREQ)")
    fig.suptitle("Verdict stability across design choices (dashed = 0.5 threshold)",
                 fontsize=11, fontweight="bold", y=1.03)
    _save(fig, "fig8_ablations")


# --------------------------------------------------------------------------- #
# Fig 9 - self-prior projection illustration                                  #
# --------------------------------------------------------------------------- #
def fig_projection():
    d = _load_figdata()
    y, phi = d["y"], d["phi"]
    q = d["q_MLP-SPATIAL"]
    qbar = d["qbar_MLP-SPATIAL"]
    dd = d["d_MLP-SPATIAL"]
    pv = list(d["pred_vocab"])

    # choose a populated cell with predicate diversity
    uphi, cnt = np.unique(phi, return_counts=True)
    cand = uphi[cnt >= 40]
    best = None
    for cph in cand:
        idx = np.where(phi == cph)[0]
        div = len(np.unique(y[idx]))
        if best is None or div > best[1]:
            best = (cph, div, idx)
    cph, _, idx = best
    qbar_cell = qbar[idx[0]]  # constant within the cell
    top = np.argsort(qbar_cell)[::-1][:8]
    names = [pv[int(t)] for t in top]

    fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.3), gridspec_kw={"width_ratios": [1, 1]})
    # (a) the frozen forecaster + individual model predictions
    x = np.arange(len(top))
    ax[0].bar(x, qbar_cell[top], color=C_PRIOR, width=0.6,
              label="$\\bar q_f$ (self-prior projection, frozen)")
    rng = np.random.default_rng(1)
    sub = rng.choice(idx, size=min(8, len(idx)), replace=False)
    for j, i in enumerate(sub):
        ax[0].scatter(x + (rng.random(len(x)) - 0.5) * 0.3, q[i, top], s=14,
                      color=C_REASON, alpha=0.5,
                      label="$q_f(\\cdot\\mid x_i)$ (per instance)" if j == 0 else None)
    ax[0].set_xticks(x); ax[0].set_xticklabels(names, rotation=30, ha="right", fontsize=8.5)
    ax[0].set_ylabel("probability")
    ax[0].set_title("(a)  Within one $\\phi$-cell: projection vs. per-instance", loc="left")
    ax[0].legend(fontsize=8)

    # (b) distribution of d_i in this cell -> where image info helps
    dvals = dd[idx]
    ax[1].hist(dvals, bins=30, color=C_REASON, alpha=0.8)
    ax[1].axvline(0, color=C_INK, lw=1)
    ax[1].axvline(dvals.mean(), color=C_RED, lw=2, ls="--",
                  label=f"mean $d_i$ = {dvals.mean():.3f}")
    ax[1].set_xlabel("$d_i=\\log q_f(y_i\\mid x_i)-\\log\\bar q_f(y_i\\mid\\phi_i)$")
    ax[1].set_ylabel("count")
    ax[1].set_title("(b)  Per-instance scores spread around the frozen prior", loc="left")
    ax[1].legend(fontsize=8.5)
    _save(fig, "fig9_projection")


# --------------------------------------------------------------------------- #
# Fig 10 - qualitative examples on the REAL processed images                   #
# --------------------------------------------------------------------------- #
_VG_DIRS = ["https://cs.stanford.edu/people/rak248/VG_100K/",
            "https://cs.stanford.edu/people/rak248/VG_100K_2/"]
_IMG_CACHE = os.path.join(
    os.environ.get("TEMP", "/tmp"), "claude", "C--work-WAGER", "vg_images")


def _download_vg_image(iid):
    import ssl, urllib.request
    os.makedirs(_IMG_CACHE, exist_ok=True)
    fp = os.path.join(_IMG_CACHE, f"{iid}.jpg")
    if os.path.exists(fp):
        return fp
    ctx = ssl.create_default_context(); ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    for base in _VG_DIRS:
        try:
            req = urllib.request.Request(base + f"{iid}.jpg",
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                data = r.read()
            with open(fp, "wb") as f:
                f.write(data)
            return fp
        except Exception:
            continue
    return None


def fig_qualitative(n_examples=2):
    """Overlay our boxes + WAGER per-instance scores on the real VG images."""
    import matplotlib.image as mpimg
    d = _load_figdata()
    y, image = d["y"], d["image"]
    subj, obj = d["coarse"], d["obj"]
    sbox, obox = d["sbox"], d["obox"]
    qF = d["q_FREQ"]; dS = d["d_MLP-SPATIAL"]
    ov, pv = list(d["obj_vocab"]), list(d["pred_vocab"])

    uimg, counts = np.unique(image, return_counts=True)
    cand = uimg[(counts >= 3) & (counts <= 7)]
    # prefer images whose relations show a mix of reasoning (d>0) and prior-only
    scored = []
    for im in cand:
        idx = np.where(image == im)[0]
        scored.append((float(np.ptp(dS[idx])), int(im), idx))
    scored.sort(reverse=True)

    chosen = []
    for _, im, idx in scored:
        fp = _download_vg_image(im)
        if fp is None:
            continue
        try:
            img = mpimg.imread(fp)
        except Exception:
            continue
        chosen.append((im, idx, img))
        if len(chosen) >= n_examples:
            break
    if not chosen:
        print("[skip] fig_qualitative: no images downloaded")
        return

    fig, axes = plt.subplots(1, len(chosen), figsize=(6.4 * len(chosen), 5.2))
    if len(chosen) == 1:
        axes = [axes]
    pal = ["#2563eb", "#db2777", "#16a34a", "#d97706", "#9333ea", "#0891b2"]
    for ax, (im, idx, img) in zip(axes, chosen):
        ax.imshow(img)
        H, W = img.shape[:2]
        idx = idx[:5]
        lines = []
        for k, i in enumerate(idx):
            col = pal[k % len(pal)]
            for box, cls in [(sbox[i], subj[i]), (obox[i], obj[i])]:
                r = Rectangle((box[0], box[1]), box[2], box[3], fill=False,
                              edgecolor=col, lw=2.2)
                ax.add_patch(r)
                ax.text(box[0] + 2, max(box[1] - 4, 8), ov[int(cls)], color="white",
                        fontsize=8, fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.12", fc=col, ec="none", alpha=0.85))
            scx, scy = sbox[i, 0] + sbox[i, 2] / 2, sbox[i, 1] + sbox[i, 3] / 2
            ocx, ocy = obox[i, 0] + obox[i, 2] / 2, obox[i, 1] + obox[i, 3] / 2
            ax.annotate("", xy=(ocx, ocy), xytext=(scx, scy),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8, alpha=0.8))
            freq_top = pv[int(np.argmax(qF[i]))]
            tag = "image helps" if dS[i] > 0.05 else "prior suffices"
            lines.append(
                f"⟨{ov[int(subj[i])]}, {pv[int(y[i])]}, {ov[int(obj[i])]}⟩"
                f"   FREQ→{freq_top}   d={dS[i]:+.2f} ({tag})")
        ax.set_xlim(0, W); ax.set_ylim(H, 0)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"VG image {im}", fontsize=10, loc="left")
        cap = "\n".join("• " + ln for ln in lines)
        ax.text(0.0, -0.04, cap, transform=ax.transAxes, va="top", fontsize=8.2,
                color=C_INK, linespacing=1.6, family="DejaVu Sans")
    fig.suptitle("Real Visual Genome relations we process: WAGER's per-instance "
                 "reasoning score $d_i$ flags where the image adds signal beyond the "
                 "class-pair prior", fontsize=11, fontweight="bold", y=1.02)
    fig.subplots_adjust(bottom=0.22, top=0.9, wspace=0.08)
    _save(fig, "fig10_qualitative")


# --------------------------------------------------------------------------- #
# Fig 11 - stratified reasoning by predicate tier                             #
# --------------------------------------------------------------------------- #
def fig_stratified():
    S = _load_json("stratified.json")
    tiers = S["tiers"]
    tcol = {"head": C_PRIOR, "body": C_GOLD, "tail": C_REASON}
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    x = np.arange(len(MODELS))
    w = 0.26
    for j, t in enumerate(tiers):
        vals = [S["models"][m][t]["mean_d"] for m in MODELS]
        ax.bar(x + (j - 1) * w, vals, w, color=tcol[t],
               label=f"{t} ({'5' if t=='head' else '11' if t=='body' else '34'} predicates)")
    ax.axhline(0, color=C_INK, lw=1)
    ax.set_xticks(x); ax.set_xticklabels(MODELS, rotation=18, ha="right", fontsize=9)
    ax.set_ylabel("mean reasoning score  $\\bar d$  (nats)")
    ax.set_title("Reasoning concentrates on rare predicates: per-tier $\\bar d$\n"
                 "(head predicates are won by the prior; body/tail carry the reasoning signal)")
    ax.legend(fontsize=9, title="predicate tier")
    _save(fig, "fig11_stratified")


def main():
    for fn in [fig_concept, fig_pipeline, fig_longtail, fig_wealth, fig_decomposition,
               fig_rgr_forest, fig_phase1, fig_ablations, fig_projection, fig_stratified,
               fig_qualitative]:
        try:
            fn()
        except Exception as e:
            import traceback
            print(f"[FAIL] {fn.__name__}: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
