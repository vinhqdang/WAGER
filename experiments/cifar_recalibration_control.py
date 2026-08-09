"""Calibration-controlled WAGER decomposition on CIFAR-100-LT.

Addresses the recalibration confound: the alignment channel dR is not
invariant to monotone recalibration, so a decomposition against a badly
overconfident baseline mixes confidence scaling into both channels.
Protocol: split the test set into a calibration half and an audit half,
choose each model's temperature by minimizing NLL on the calibration half
only, then decompose on the audit half in three regimes:

  raw        -- as in the original submission (no recalibration);
  cal-old    -- old model temperature-recalibrated, new model raw;
  cal-both   -- both models temperature-recalibrated.

A calibration-only row (recalibrated CE vs raw CE) documents the size of
the confound itself.  Repeated over random splits for stability.

Run: conda run -n py313 python experiments/cifar_recalibration_control.py
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from wager.antisymmetric import decompose_gain

ROOT = pathlib.Path(__file__).resolve().parents[1]
N_SPLITS = 20
T_GRID = np.linspace(0.25, 8.0, 311)

d = np.load(ROOT / "data/cifar_lt/cifar_lt_results.npz")
coarse = np.load(ROOT / "data/cifar_lt/coarse_of_class.npy")
y = d["y_test"]
models = {
    "CE": d["probs_baseline"].astype(np.float64),
    "CB": d["probs_cb"].astype(np.float64),
    "DRW": d["probs_drw"].astype(np.float64),
}


def temp_scale(p: np.ndarray, T: float, eps: float = 1e-12) -> np.ndarray:
    z = np.log(np.clip(p, eps, None)) / T
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def nll(p: np.ndarray, labels: np.ndarray, eps: float = 1e-12) -> float:
    return float(-np.mean(np.log(np.clip(p[np.arange(len(labels)), labels], eps, None))))


def fit_temperature(p: np.ndarray, labels: np.ndarray) -> float:
    return float(T_GRID[int(np.argmin([nll(temp_scale(p, t), labels) for t in T_GRID]))])


def decomp(q_new, q_old, idx):
    g = decompose_gain(q_new[idx], q_old[idx], y[idx], coarse[y[idx]])
    return g.total_gain, g.prior_gain, g.reasoning_gain


rows: dict[str, list[tuple[float, float, float]]] = {}
temps: dict[str, list[float]] = {m: [] for m in models}
rng_master = np.random.default_rng(20260810)
for split in range(N_SPLITS):
    perm = rng_master.permutation(len(y))
    cal, aud = perm[: len(y) // 2], perm[len(y) // 2 :]
    T = {m: fit_temperature(p[cal], y[cal]) for m, p in models.items()}
    for m in models:
        temps[m].append(T[m])
    cal_p = {m: temp_scale(p, T[m]) for m, p in models.items()}

    for new in ("CB", "DRW"):
        rows.setdefault(f"{new} vs CE (raw)", []).append(
            decomp(models[new], models["CE"], aud))
        rows.setdefault(f"{new} vs CE (cal-old)", []).append(
            decomp(models[new], cal_p["CE"], aud))
        rows.setdefault(f"{new} vs CE (cal-both)", []).append(
            decomp(cal_p[new], cal_p["CE"], aud))
    rows.setdefault("CE(cal) vs CE (confound size)", []).append(
        decomp(cal_p["CE"], models["CE"], aud))

out = {"n_splits": N_SPLITS, "temperatures": {}, "rows": {}}
for m in models:
    t = np.asarray(temps[m])
    out["temperatures"][m] = {"mean": round(float(t.mean()), 3),
                              "sd": round(float(t.std(ddof=1)), 3)}
    print(f"T*({m}) = {t.mean():.2f} +/- {t.std(ddof=1):.2f}")
print()
for name, vals in rows.items():
    a = np.asarray(vals)
    mean, sd = a.mean(axis=0), a.std(axis=0, ddof=1)
    out["rows"][name] = {
        "dT": round(float(mean[0]), 5), "dP": round(float(mean[1]), 5),
        "dR": round(float(mean[2]), 5),
        "dT_sd": round(float(sd[0]), 5), "dP_sd": round(float(sd[1]), 5),
        "dR_sd": round(float(sd[2]), 5),
    }
    print(f"{name:34s} dT={mean[0]:+.5f}({sd[0]:.5f})  "
          f"dP={mean[1]:+.5f}({sd[1]:.5f})  dR={mean[2]:+.5f}({sd[2]:.5f})")

dest = ROOT / "results/cifar_recalibration.json"
dest.write_text(json.dumps(out, indent=2))
print(f"\nwrote {dest}")
