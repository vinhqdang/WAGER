"""Discriminant validity against a class-wise operating-point shift (Sec. 4 design).

The calibration-only arm of antisymmetric_simulation.py softens a model by a
temperature, which per-model temperature matching undoes by construction. Here the
new model is the old one with a per-class logit offset b_y added -- a different
operating point with identical within-cell information, so every within-cell
ranking and the within-cell AUC are unchanged. A scalar temperature cannot undo
it. Reported, per replicate: the raw case-level part, the part under per-model
temperature matching, and the part under temperature + per-class-bias matching,
which can represent the shift exactly. Two offset patterns: b = -log of the class
frequencies (a logit adjustment) and random b ~ N(0, 1).

Run: python experiments/sim_classwise_shift.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain  # noqa: E402
from wager.rank import within_cell_auc  # noqa: E402
from antisymmetric_simulation import _fit_temperature, _softmax_power, generate  # noqa: E402
from run_sgg_rank_robustness import apply_family, fit_family  # noqa: E402

OUT = ROOT / "results/sim_classwise_shift.json"
N_REPS = 200


def main():
    res = {}
    for pattern in ("logit adjustment", "random offsets"):
        raw, temp, tb, dauc = [], [], [], []
        for r in range(N_REPS):
            rng = np.random.default_rng(90_000 + r)
            q_mix, _, y, phi = generate(90_000 + r, beta=0.35, per=100)
            q_old = _softmax_power(q_mix, 2.0)
            k = q_old.shape[1]
            if pattern == "logit adjustment":
                b = -np.log(np.bincount(y, minlength=k) / len(y) + 1e-3)
            else:
                b = rng.normal(0.0, 1.0, size=k)
            z = np.log(np.clip(q_old, 1e-12, None)) + b
            q_new = np.exp(z - z.max(1, keepdims=True))
            q_new /= q_new.sum(1, keepdims=True)
            half = rng.permutation(len(y))
            cal, aud = half[: len(y) // 2], half[len(y) // 2:]
            raw.append(decompose_gain(q_new[aud], q_old[aud], y[aud], phi[aud]).alignment_gain)
            tn, to = _fit_temperature(q_new[cal], y[cal]), _fit_temperature(q_old[cal], y[cal])
            temp.append(decompose_gain(_softmax_power(q_new, 1 / tn)[aud],
                                       _softmax_power(q_old, 1 / to)[aud],
                                       y[aud], phi[aud]).alignment_gain)
            ln, lo = np.log(np.clip(q_new, 1e-12, None)), np.log(np.clip(q_old, 1e-12, None))
            pn, po = fit_family(ln[cal], y[cal], True), fit_family(lo[cal], y[cal], True)
            tb.append(decompose_gain(apply_family(ln, pn, True)[aud], apply_family(lo, po, True)[aud],
                                     y[aud], phi[aud]).alignment_gain)
            dauc.append(within_cell_auc(q_new, y, phi) - within_cell_auc(q_old, y, phi))
        res[pattern] = {k: {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1))}
                        for k, v in (("raw", raw), ("temperature matched", temp),
                                     ("temperature + class bias matched", tb),
                                     ("auc difference", dauc))}
        print(pattern, {k: f"{v['mean']:+.5f} (sd {v['sd']:.5f})" for k, v in res[pattern].items()},
              flush=True)
    OUT.write_text(json.dumps({"n_reps": N_REPS, "score": "quadratic", **res}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
