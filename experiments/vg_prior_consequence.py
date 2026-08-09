"""Consequence test: does the alignment channel predict what happens after
post-hoc prior correction?

The matched-subsample study found MLP-VISUAL-S loses to MLP-SPATIAL-S overall
while gaining on instance alignment, with the whole deficit in the prior
channel. If dR carries genuine instance information, correcting the visual
model's prior channel post hoc -- without touching what it knows about
individual examples -- should recover the aggregate loss; and the correction
itself, which adds no instance information, should register as almost pure dP.

Correction: within-cell prior matching (label-shift style). For cell c with
training-count histogram f_c and mean test prediction qbar_c (labels unused),
reweight q'_i(y) proportional to q_i(y) * f_c(y) / qbar_c(y).

Also runs a calibration-matched control (per-model temperature fitted on a
held-out image split) to confirm the visual model's alignment gain is not a
confidence-scaling artifact.

Run: conda run -n py313 python experiments/vg_prior_consequence.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from wager.antisymmetric import cyclic_randomization_test, decompose_gain

ROOT = pathlib.Path(__file__).resolve().parents[1]
ALPHA = 0.05
N_RANDOMIZATIONS = 999
SMOOTH = 0.1
EPS = 1e-12

raw = np.load(ROOT / "data/vg/vg_predcls.npz")
vis = np.load(ROOT / "data/vg_visual/vg_visual_models.npz")
y, phi, image = vis["y"].astype(np.int64), vis["phi"].astype(np.int64), vis["image"]
K = 50

models = {}
for name in ("MLP-SPATIAL-S", "MLP-VISUAL-S"):
    q = vis[name].astype(np.float64)
    models[name] = q / q.sum(axis=1, keepdims=True)

# Training-count prior per cell (the declared benchmark prior), Laplace-smoothed,
# global-histogram fallback for cells unseen in training.
tr = raw["is_train"]
tr_phi, tr_pred = raw["phi"][tr].astype(np.int64), raw["pred"][tr].astype(np.int64)
n_cells = int(max(tr_phi.max(), phi.max())) + 1
counts = np.zeros((n_cells, K))
np.add.at(counts, (tr_phi, tr_pred), 1.0)
global_hist = counts.sum(axis=0)
global_hist /= global_hist.sum()
unseen = counts.sum(axis=1) == 0
prior = (counts + SMOOTH) / (counts + SMOOTH).sum(axis=1, keepdims=True)
prior[unseen] = global_hist


def prior_match(q: np.ndarray) -> np.ndarray:
    """Reweight q so its implied within-cell marginal matches the training prior."""
    qbar = np.zeros((n_cells, K))
    np.add.at(qbar, phi, q)
    cell_n = np.bincount(phi, minlength=n_cells)[:, None].astype(float)
    qbar = np.divide(qbar, cell_n, out=np.full_like(qbar, np.nan), where=cell_n > 0)
    w = prior / np.clip(qbar, EPS, None)
    out = q * w[phi]
    return out / out.sum(axis=1, keepdims=True)


def temp_scale(p, T):
    z = np.log(np.clip(p, EPS, None)) / T
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def fit_temperature(p, labels):
    grid = np.linspace(0.25, 8.0, 311)
    nlls = [float(-np.mean(np.log(np.clip(temp_scale(p, t)[np.arange(len(labels)), labels],
                                          EPS, None)))) for t in grid]
    return float(grid[int(np.argmin(nlls))])


def brier(q):
    onehot_term = 1.0 - 2.0 * q[np.arange(len(y)), y] + (q * q).sum(axis=1)
    return float(onehot_term.mean())


def row(name, q_new, q_old, idx=None, with_p=False, seed=0):
    sl = slice(None) if idx is None else idx
    r = decompose_gain(q_new[sl], q_old[sl], y[sl], phi[sl], groups=image[sl],
                       score="brier", alpha=ALPHA)
    p = None
    if with_p:
        p, _ = cyclic_randomization_test(q_new[sl], q_old[sl], y[sl], phi[sl],
                                         score="brier",
                                         n_randomizations=N_RANDOMIZATIONS, seed=seed)
    print(f"{name:44s} T={r.total_gain:+.5f} P={r.prior_gain:+.5f} "
          f"R={r.reasoning_gain:+.5f} CI=[{r.reasoning_ci[0]:+.5f},"
          f"{r.reasoning_ci[1]:+.5f}]" + (f" p={p:.4g}" if p is not None else ""),
          flush=True)
    return {"name": name, "total": r.total_gain, "prior": r.prior_gain,
            "reasoning": r.reasoning_gain, "reasoning_ci": list(r.reasoning_ci),
            "randomization_p": p}


def main():
    t0 = time.time()
    spa, visq = models["MLP-SPATIAL-S"], models["MLP-VISUAL-S"]
    spa_c, vis_c = prior_match(spa), prior_match(visq)

    print("Brier totals (lower better):")
    for n, q in [("SPATIAL-S", spa), ("VISUAL-S", visq),
                 ("SPATIAL-S prior-matched", spa_c), ("VISUAL-S prior-matched", vis_c)]:
        print(f"  {n:26s} {brier(q):.5f}  acc={float(np.mean(q.argmax(1) == y)):.4f}")

    rows = []
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        print("\nThe correction itself (should be almost pure dP):")
        rows.append(row("VISUAL' vs VISUAL", vis_c, visq))
        rows.append(row("SPATIAL' vs SPATIAL", spa_c, spa))

        print("\nReference (paper row) and consequence rows:")
        rows.append(row("VISUAL vs SPATIAL (paper)", visq, spa, with_p=True, seed=0))
        rows.append(row("VISUAL' vs SPATIAL", vis_c, spa, with_p=True, seed=1))
        rows.append(row("VISUAL' vs SPATIAL' (both corrected)", vis_c, spa_c,
                        with_p=True, seed=2))

        print("\nCalibration-matched control (T fit on held-out image half):")
        rng = np.random.default_rng(20260810)
        imgs = np.unique(image)
        half = rng.permutation(len(imgs))
        cal_imgs = set(imgs[half[: len(imgs) // 2]].tolist())
        cal_idx = np.array([i in cal_imgs for i in image])
        aud_idx = ~cal_idx
        T_spa = fit_temperature(spa[cal_idx], y[cal_idx])
        T_vis = fit_temperature(visq[cal_idx], y[cal_idx])
        print(f"  T*(SPATIAL-S)={T_spa:.2f}  T*(VISUAL-S)={T_vis:.2f}")
        rows.append(row("VISUAL vs SPATIAL raw (audit half)", visq, spa,
                        idx=np.where(aud_idx)[0]))
        rows.append(row("VISUAL vs SPATIAL cal-both (audit half)",
                        temp_scale(visq, T_vis), temp_scale(spa, T_spa),
                        idx=np.where(aud_idx)[0]))

    out = {
        "n_randomizations": N_RANDOMIZATIONS, "smooth": SMOOTH,
        "brier": {n: brier(q) for n, q in
                  [("SPATIAL-S", spa), ("VISUAL-S", visq),
                   ("SPATIAL-S-pm", spa_c), ("VISUAL-S-pm", vis_c)]},
        "accuracy": {n: float(np.mean(q.argmax(1) == y)) for n, q in
                     [("SPATIAL-S", spa), ("VISUAL-S", visq),
                      ("SPATIAL-S-pm", spa_c), ("VISUAL-S-pm", vis_c)]},
        "temperatures": {"SPATIAL-S": T_spa, "VISUAL-S": T_vis},
        "rows": rows, "seconds": time.time() - t0,
    }
    dest = ROOT / "results/vg_prior_consequence.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {dest} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
