"""Audit two released scene-graph checkpoints on the canonical VG150 test split.

Both variants come from Tang et al.'s causal MOTIFS PredCls release: the biased
MOTIFS-SUM baseline (CAUSAL.EFFECT_TYPE none) and its Total Direct Effect
debiased counterpart (TDE), evaluated by the original codebase so that the two
prediction sets are aligned relation-for-relation by construction.

Everything the audit needs is inside the evaluation dumps -- subject class,
object class, predicate, image id and the predicate distribution -- so this is
self-contained on the standard split and its standard vocabulary, independent of
the VG150-style reconstruction used elsewhere in the paper.

The dumps carry a 51-way distribution whose index 0 is the background class;
PredCls scores the 50 real predicates, so that column is dropped and the rest
renormalized. Classes and predicates are 1-indexed in the dump.

Run: conda run -n py313 python experiments/run_sgg_audit_wager.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from wager.antisymmetric import cyclic_randomization_test, decompose_gain

ROOT = pathlib.Path(__file__).resolve().parents[1]
MDIR = ROOT / "data/vg_motifs"
N_RANDOMIZATIONS = 999
N_OBJ = 150
ALPHA = 0.05


def load(effect: str):
    d = np.load(MDIR / f"motifs_{effect}_predcls.npz")
    q = d["probs"].astype(np.float64)[:, 1:]          # drop background column
    q /= q.sum(axis=1, keepdims=True)
    return {
        "q": q,
        "y": d["pred"].astype(np.int64) - 1,          # 1..50 -> 0..49
        "subj": d["subj"].astype(np.int64) - 1,       # 1..150 -> 0..149
        "obj": d["obj"].astype(np.int64) - 1,
        "image": d["image_index"].astype(np.int64),
    }


def recalls(effect: str):
    p = MDIR / f"motifs_{effect}_recalls.json"
    if not p.exists():
        return {}
    raw = json.loads(p.read_text())
    out = {}
    for k, v in raw.items():
        for kk, vv in v.items():
            out[f"{k}@{kk}"] = vv
    return out


def temp_scale(p, T, eps=1e-12):
    z = np.log(np.clip(p, eps, None)) / T
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def fit_temperature(p, labels, eps=1e-12):
    grid = np.geomspace(0.05, 20.0, 240)
    nll = [float(-np.mean(np.log(np.clip(
        temp_scale(p, t)[np.arange(len(labels)), labels], eps, None)))) for t in grid]
    return float(grid[int(np.argmin(nll))])


def main():
    base, tde = load("none"), load("TDE")
    for k in ("y", "subj", "obj", "image"):
        assert np.array_equal(base[k], tde[k]), f"variants disagree on {k}"
    y, image = base["y"], base["image"]
    phi = base["subj"] * N_OBJ + base["obj"]
    n_cells = len(np.unique(phi))
    print(f"{len(y)} relations, {len(np.unique(image))} images, {n_cells} class-pair cells")

    acc = {"MOTIFS": float((base["q"].argmax(1) == y).mean()),
           "MOTIFS-TDE": float((tde["q"].argmax(1) == y).mean())}
    print(f"top-1 predicate accuracy: {acc}")

    rows = []
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        g = decompose_gain(tde["q"], base["q"], y, phi, groups=image,
                           score="brier", alpha=ALPHA)
        p, _ = cyclic_randomization_test(tde["q"], base["q"], y, phi,
                                         score="brier",
                                         n_randomizations=N_RANDOMIZATIONS, seed=0)
        print(f"TDE vs MOTIFS  dT={g.total_gain:+.5f}  dP={g.prior_gain:+.5f}  "
              f"dR={g.alignment_gain:+.5f}  CI=[{g.alignment_ci[0]:+.5f},"
              f"{g.alignment_ci[1]:+.5f}]  p={p:.4g}  coverage={g.coverage:.3f}")
        rows.append({"comparison": "MOTIFS-TDE vs MOTIFS", "score": "brier",
                     **g.as_row(), "randomization_p": p})

        # log score as a declared sensitivity, as elsewhere in the paper
        gl = decompose_gain(tde["q"], base["q"], y, phi, groups=image, score="log")
        print(f"  (log score)  dT={gl.total_gain:+.5f}  dP={gl.prior_gain:+.5f}  "
              f"dR={gl.alignment_gain:+.5f}")
        rows.append({"comparison": "MOTIFS-TDE vs MOTIFS", "score": "log",
                     **gl.as_row(), "randomization_p": None})

        # coarser audit cell: subject class only (Proposition 2 in a third setting)
        gs = decompose_gain(tde["q"], base["q"], y, base["subj"], groups=image)
        print(f"  (phi=subject) dT={gs.total_gain:+.5f}  dP={gs.prior_gain:+.5f}  "
              f"dR={gs.alignment_gain:+.5f}")
        rows.append({"comparison": "MOTIFS-TDE vs MOTIFS", "score": "brier",
                     "prior_feature": "subject class", **gs.as_row(),
                     "randomization_p": None})

        # calibration-matched regime: TDE's counterfactual logit subtraction changes
        # the shape of the distribution, and the alignment channel is not invariant
        # to that, so temperatures are fitted on images held out from the audit.
        rng = np.random.default_rng(20260811)
        imgs = np.unique(image)
        cal_imgs = set(imgs[rng.permutation(len(imgs))[: len(imgs) // 2]].tolist())
        cal = np.array([i in cal_imgs for i in image])
        aud = np.where(~cal)[0]
        t_base = fit_temperature(base["q"][cal], y[cal])
        t_tde = fit_temperature(tde["q"][cal], y[cal])
        gc = decompose_gain(temp_scale(tde["q"], t_tde)[aud],
                            temp_scale(base["q"], t_base)[aud],
                            y[aud], phi[aud], groups=image[aud])
        gr = decompose_gain(tde["q"][aud], base["q"][aud], y[aud], phi[aud],
                            groups=image[aud])
        print(f"  T*(MOTIFS)={t_base:.2f}  T*(TDE)={t_tde:.2f}")
        print(f"  (audit half, raw)  dT={gr.total_gain:+.5f} dP={gr.prior_gain:+.5f} "
              f"dR={gr.alignment_gain:+.5f}")
        print(f"  (calibration-matched) dT={gc.total_gain:+.5f} "
              f"dP={gc.prior_gain:+.5f} dR={gc.alignment_gain:+.5f} "
              f"CI=[{gc.alignment_ci[0]:+.5f},{gc.alignment_ci[1]:+.5f}]")
        rows.append({"comparison": "MOTIFS-TDE vs MOTIFS", "score": "brier",
                     "regime": "audit-half raw", **gr.as_row(),
                     "randomization_p": None})
        rows.append({"comparison": "MOTIFS-TDE vs MOTIFS", "score": "brier",
                     "regime": "calibration-matched", "T_old": t_base,
                     "T_new": t_tde, **gc.as_row(), "randomization_p": None})

        gcl = decompose_gain(temp_scale(tde["q"], t_tde)[aud],
                             temp_scale(base["q"], t_base)[aud],
                             y[aud], phi[aud], groups=image[aud], score="log")
        print(f"  (cal-matched, log) dT={gcl.total_gain:+.5f} "
              f"dP={gcl.prior_gain:+.5f} dR={gcl.alignment_gain:+.5f}")
        rows.append({"comparison": "MOTIFS-TDE vs MOTIFS", "score": "log",
                     "regime": "calibration-matched", **gcl.as_row(),
                     "randomization_p": None})

        p_cal, _ = cyclic_randomization_test(
            temp_scale(tde["q"], t_tde)[aud], temp_scale(base["q"], t_base)[aud],
            y[aud], phi[aud], score="brier", n_randomizations=N_RANDOMIZATIONS,
            seed=1)
        print(f"  (cal-matched randomization p={p_cal:.4g})")
        rows[-2]["randomization_p"] = p_cal

    out = {
        "dataset": "VG150 PredCls (canonical split, Tang et al. released checkpoints)",
        "n_relations": int(len(y)), "n_images": int(len(np.unique(image))),
        "n_cells": int(n_cells), "accuracy": acc,
        "recalls": {"MOTIFS": recalls("none"), "MOTIFS-TDE": recalls("TDE")},
        "comparisons": rows,
    }
    dest = ROOT / "results/sgg_audit_motifs.json"
    dest.write_text(json.dumps(out, indent=2, default=float))
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
