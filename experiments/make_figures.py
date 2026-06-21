"""Generate figures for the WAGER report from results JSON files."""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(RES, "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.autolayout": True})
ACCENT = "#2b6cb0"
WARM = "#dd6b20"


def fig_phase1():
    path = os.path.join(RES, "phase1_results.json")
    if not os.path.exists(path):
        print("no phase1 results"); return
    R = json.load(open(path))

    # recovery curve: estimated vs true RGR
    rows = R["gate_c_recovery"]["rgr_rows"]
    betas = [r["beta"] for r in rows]
    est = [r["RGR_est"] for r in rows]
    true = [r["RGR_true"] for r in rows]
    lo = [r["fieller_lo"] for r in rows]
    hi = [r["fieller_hi"] for r in rows]

    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    ax[0].plot(true, est, "o-", color=ACCENT, label="WAGER estimate")
    mn, mx = min(true + est), max(true + est)
    ax[0].plot([mn, mx], [mn, mx], "--", color="gray", label="ideal (y=x)")
    ax[0].set_xlabel("ground-truth RGR"); ax[0].set_ylabel("estimated RGR")
    ax[0].set_title(f"RGR recovery  (Pearson={R['gate_c_recovery']['pearson_injectedRGR_vs_estRGR']:.3f})")
    ax[0].legend(frameon=False)

    irows = R["gate_c_recovery"]["rows"]
    ir_true = [r["I_reason_true"] for r in irows]
    ir_est = [r["I_reason_est"] for r in irows]
    bx = [r["beta"] for r in irows]
    ax[1].plot(bx, ir_true, "s-", color="gray", label="true $I_{reason}$")
    ax[1].plot(bx, ir_est, "o-", color=WARM, label="WAGER $\\hat I_{reason}$")
    ax[1].set_xlabel("reasoning mixing weight $\\beta$"); ax[1].set_ylabel("$I_{reason}$ (nats)")
    ax[1].set_title("Reasoning-information recovery")
    ax[1].legend(frameon=False)
    fig.savefig(os.path.join(FIG, "phase1_recovery.png"))
    plt.close(fig)
    print("wrote phase1_recovery.png")


def fig_sgg():
    path = os.path.join(RES, "sgg_results.json")
    if not os.path.exists(path):
        print("no sgg results"); return
    S = json.load(open(path))
    rows = S["model_rows"]
    names = [r["model"] for r in rows]
    I_reason = [r["I_reason"] for r in rows]
    I_prior = [r["I_prior"] for r in rows]
    acc = [r.get("test_acc", np.nan) for r in rows]

    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.bar(x, I_prior, color="#a0aec0", label="$I_{prior}$ (frequency-fitting)")
    ax.bar(x, I_reason, bottom=I_prior, color=ACCENT, label="$I_{reason}$ (visual reasoning)")
    for i, a in enumerate(acc):
        ax.text(i, I_prior[i] + I_reason[i] + 0.03, f"acc {a:.2f}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=20, ha="right")
    ax.set_ylabel("information (nats)")
    ax.set_title("VG PredCls: information decomposition by model")
    ax.legend(frameon=False)
    fig.savefig(os.path.join(FIG, "sgg_decomposition.png"))
    plt.close(fig)
    print("wrote sgg_decomposition.png")

    # RGR verdicts
    rr = S["rgr_rows"]
    labels = [f"{r['f_prime']}\nvs {r['f']}" for r in rr]
    rgr = [r["RGR"] for r in rr]
    lo = [r["fieller_lo"] for r in rr]
    hi = [r["fieller_hi"] for r in rr]
    colors = [ACCENT if r["verdict"] == "reasoning-supported" else WARM for r in rr]
    yerr = np.array([[max(0, rgr[i] - lo[i]) for i in range(len(rr))],
                     [max(0, hi[i] - rgr[i]) for i in range(len(rr))]])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.errorbar(range(len(rr)), rgr, yerr=yerr, fmt="o", color="black", ecolor="gray", capsize=3)
    for i, cc in enumerate(colors):
        ax.scatter(i, rgr[i], color=cc, zorder=5, s=60)
    ax.axhline(0.5, ls="--", color="red", label="decision threshold 0.5")
    ax.set_xticks(range(len(rr))); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Reasoning Gain Ratio")
    ax.set_title("RGR with anytime-valid CIs (blue=reasoning, orange=non-substantive)")
    ax.legend(frameon=False)
    fig.savefig(os.path.join(FIG, "sgg_rgr.png"))
    plt.close(fig)
    print("wrote sgg_rgr.png")


if __name__ == "__main__":
    fig_phase1()
    fig_sgg()
