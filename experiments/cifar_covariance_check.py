"""Reproduce the covariance-identity cross-check quoted in the CIFAR section.

Computes the alignment term directly from the quadratic-score covariance
identity (Eq. cov-id), through a code path sharing nothing with the transport
estimator, then applies the (n_c-1)/n_c attenuation factor of Proposition
`attenuate` to compare against `decompose_gain`'s leave-one-out estimate.

Run: conda run -n py313 python experiments/cifar_covariance_check.py
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from wager.antisymmetric import decompose_gain

ROOT = pathlib.Path(__file__).resolve().parents[1]
d = np.load(ROOT / "data/cifar_lt/cifar_lt_results.npz")
coarse = np.load(ROOT / "data/cifar_lt/coarse_of_class.npy")
y = d["y_test"]
phi = coarse[y]
ce = d["probs_baseline"].astype(np.float64)
cb = d["probs_cb"].astype(np.float64)

# Path 1: plug-in within-cell covariance, summed over labels, n_c-weighted.
delta = cb - ce                      # probability movement of the new model
n = len(y)
total, weight = 0.0, 0
for c in np.unique(phi):
    ix = np.flatnonzero(phi == c)
    onehot = np.zeros((len(ix), delta.shape[1]))
    onehot[np.arange(len(ix)), y[ix]] = 1.0
    dc = delta[ix] - delta[ix].mean(axis=0, keepdims=True)
    oc = onehot - onehot.mean(axis=0, keepdims=True)
    cov_sum = (dc * oc).sum() / len(ix)          # plug-in Cov summed over labels
    total += 2.0 * cov_sum * len(ix)
    weight += len(ix)
plugin = total / weight

n_c = 500                                        # balanced superclass cell size
rescaled = plugin * n_c / (n_c - 1.0)
est = decompose_gain(cb, ce, y, phi).reasoning_gain

print(f"plug-in covariance path : {plugin:+.5f}")
print(f"x n_c/(n_c-1) (Prop. 1) : {rescaled:+.6f}")
print(f"transport estimator     : {est:+.6f}")
assert abs(rescaled - est) < 5e-6, "cross-check FAILED"
print("cross-check OK: independent code paths agree")
