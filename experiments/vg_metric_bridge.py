"""Translate alignment-gain magnitudes into metrics a vision reader calibrates.

For each audited VG pair we report, alongside the decomposition, the change in
top-1 predicate accuracy, in mean reciprocal rank of the true predicate, and
in recall@5 -- and, to give the alignment channel a directly comparable unit,
the same three quantities computed *after* removing the prior channel, i.e.
with both models' predictions prior-matched to the training histogram inside
each audit cell. Differences that survive prior matching are the ones the
alignment channel is measuring.

Run: conda run -n py313 python experiments/vg_metric_bridge.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from wager.antisymmetric import decompose_gain

ROOT = pathlib.Path(__file__).resolve().parents[1]
EPS = 1e-12
SMOOTH = 0.1

raw = np.load(ROOT / "data/vg/vg_predcls.npz")
vis = np.load(ROOT / "data/vg_visual/vg_visual_models.npz")
y = vis["y"].astype(np.int64)
phi = vis["phi"].astype(np.int64)
image = vis["image"]
K = 50

models = {}
for name in ("MLP-CLASS-S", "MLP-SPATIAL-S", "MLP-VISUAL-S"):
    q = vis[name].astype(np.float64)
    models[name] = q / q.sum(axis=1, keepdims=True)

tr = raw["is_train"]
tr_phi, tr_pred = raw["phi"][tr].astype(np.int64), raw["pred"][tr].astype(np.int64)
n_cells = int(max(tr_phi.max(), phi.max())) + 1
counts = np.zeros((n_cells, K))
np.add.at(counts, (tr_phi, tr_pred), 1.0)
global_hist = counts.sum(axis=0)
global_hist /= global_hist.sum()
prior = (counts + SMOOTH) / (counts + SMOOTH).sum(axis=1, keepdims=True)
prior[counts.sum(axis=1) == 0] = global_hist


def prior_match(q):
    qbar = np.zeros((n_cells, K))
    np.add.at(qbar, phi, q)
    cell_n = np.bincount(phi, minlength=n_cells)[:, None].astype(float)
    qbar = np.divide(qbar, cell_n, out=np.full_like(qbar, np.nan), where=cell_n > 0)
    out = q * (prior / np.clip(qbar, EPS, None))[phi]
    return out / out.sum(axis=1, keepdims=True)


def metrics(q):
    order = np.argsort(-q, axis=1)
    rank = np.argmax(order == y[:, None], axis=1) + 1
    return {"acc": float((q.argmax(1) == y).mean()),
            "mrr": float((1.0 / rank).mean()),
            "r@5": float((rank <= 5).mean())}


PAIRS = [("MLP-SPATIAL-S", "MLP-CLASS-S"),
         ("MLP-VISUAL-S", "MLP-CLASS-S"),
         ("MLP-VISUAL-S", "MLP-SPATIAL-S")]

rows = []
with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
    for new, old in PAIRS:
        g = decompose_gain(models[new], models[old], y, phi, groups=image)
        m_new, m_old = metrics(models[new]), metrics(models[old])
        pm_new, pm_old = metrics(prior_match(models[new])), metrics(prior_match(models[old]))
        row = {
            "pair": f"{new} vs {old}",
            "dT": round(g.total_gain, 5), "dP": round(g.prior_gain, 5),
            "dR": round(g.reasoning_gain, 5),
            "d_acc": round(m_new["acc"] - m_old["acc"], 5),
            "d_mrr": round(m_new["mrr"] - m_old["mrr"], 5),
            "d_r5": round(m_new["r@5"] - m_old["r@5"], 5),
            "d_acc_pm": round(pm_new["acc"] - pm_old["acc"], 5),
            "d_mrr_pm": round(pm_new["mrr"] - pm_old["mrr"], 5),
            "d_r5_pm": round(pm_new["r@5"] - pm_old["r@5"], 5),
        }
        rows.append(row)
        print(f"{row['pair']:34s} dT={row['dT']:+.5f} dR={row['dR']:+.5f} | "
              f"raw: dacc={row['d_acc']:+.4f} dmrr={row['d_mrr']:+.4f} "
              f"dr5={row['d_r5']:+.4f} | prior-matched: dacc={row['d_acc_pm']:+.4f} "
              f"dmrr={row['d_mrr_pm']:+.4f} dr5={row['d_r5_pm']:+.4f}", flush=True)

dest = ROOT / "results/vg_metric_bridge.json"
dest.write_text(json.dumps(rows, indent=2))
print(f"wrote {dest}")
