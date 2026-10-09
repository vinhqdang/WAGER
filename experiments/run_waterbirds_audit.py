"""An input-grounded audit outside scene graphs: Waterbirds (R2-12).

Waterbirds (Sagawa et al. 2020) pastes CUB landbirds and waterbirds on Places
backgrounds, so that in training the background predicts the label 95% of the time.
Cells are the background's scene category: a property of the input, not of the label.
Models are logistic regressions on frozen CLIP ViT-L/14 features
(colab_waterbirds_features.py), trained on the training split:

  ERM   unweighted;
  GRW   reweighted so each (label, background) group counts equally (the standard
        debiasing intervention; the analogue of TDE in Sec. 5).

Temperature and a per-class bias are fitted on the validation split, which is
group-balanced like the test split; everything is evaluated on the test split. A model's
gain over ERM splits into a group-level part (a different label prior in each
background) and a case-level part (what the model knows about a bird beyond its
background). The matched comparison recalibrates both models the same way; "ERM
recalibrated vs ERM" shows what recalibration alone does to the two parts, and the
within-cell AUC is unchanged by it.

Run: python experiments/run_waterbirds_audit.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
from scipy.optimize import minimize

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain  # noqa: E402
from wager.rank import within_cell_auc, within_cell_auc_contrast  # noqa: E402
from run_sgg_rank_robustness import apply_family, fit_family  # noqa: E402

DATA = ROOT / "data/waterbirds/features_clip_vitl14.npz"
OUT = ROOT / "results/waterbirds_audit.json"
EPS = 1e-12


def fit_lr(X, y, w, lam):
    """Weighted two-class logistic regression with an L2 penalty (L-BFGS)."""
    n, d = X.shape
    w = w / w.sum()

    def f(p):
        W, b = p[: 2 * d].reshape(2, d), p[2 * d:]
        z = X @ W.T + b
        z -= z.max(1, keepdims=True)
        lse = np.log(np.exp(z).sum(1))
        loss = np.sum(w * (lse - z[np.arange(n), y])) + 0.5 * lam * np.sum(W * W)
        g = np.exp(z - lse[:, None])
        g[np.arange(n), y] -= 1
        g *= w[:, None]
        return loss, np.concatenate([(g.T @ X + lam * W).ravel(), g.sum(0)])
    return minimize(f, np.zeros(2 * d + 2), jac=True, method="L-BFGS-B", options={"maxiter": 500}).x


def predict(p, X):
    d = X.shape[1]
    z = X @ p[: 2 * d].reshape(2, d).T + p[2 * d:]
    z -= z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def nll(q, y):
    return float(-np.mean(np.log(np.clip(q[np.arange(len(y)), y], EPS, None))))


def split_rows(M, y, phi, image, score):
    out = {}
    for name, (a, b) in M.items():
        g = decompose_gain(a, b, y, phi, groups=image, score=score)
        out[name] = {"total": g.total_gain, "group": g.prior_gain, "case": g.alignment_gain,
                     "case_ci": list(g.alignment_ci)}
    return out


def main():
    z = np.load(DATA)
    X, y, place, split, scene = z["X"].astype(np.float64), z["y"].astype(np.int64), z["place"], z["split"], z["scene"]
    mu, sd = X[split == 0].mean(0), X[split == 0].std(0) + 1e-6
    X = (X - mu) / sd
    tr, va, te = split == 0, split == 1, split == 2
    grp = 2 * y + place
    n_g = np.bincount(grp[tr], minlength=4).astype(float)

    # ridge strength by validation worst-group accuracy would favour GRW; use the validation
    # log-loss of each model instead (each model gets its own, as in a fair comparison)
    P, lam_used = {}, {}
    for name, w in (("ERM", np.ones(tr.sum())), ("GRW", 1.0 / n_g[grp[tr]])):
        best = None
        for lam in (1e-4, 1e-3, 1e-2, 1e-1):
            p = fit_lr(X[tr], y[tr], w, lam)
            v = nll(predict(p, X[va]), y[va])
            if best is None or v < best[0]:
                best = (v, lam, p)
        lam_used[name], P[name] = best[1], best[2]
        print(name, "ridge", best[1], "val nll", round(best[0], 4), flush=True)

    raw = {k: predict(p, X[te]) for k, p in P.items()}
    logv = {k: np.log(np.clip(predict(p, X[va]), EPS, None)) for k, p in P.items()}
    fam = {k: fit_family(logv[k], y[va], True) for k in P}                # temperature + class bias, on val
    cal = {k: apply_family(np.log(np.clip(raw[k], EPS, None)), fam[k], True) for k in P}
    control = cal["ERM"]                                                    # ERM's ranking, GRW-free prior

    yt = y[te]
    image = np.arange(te.sum())
    res = {"n_test": int(te.sum()), "ridge": lam_used,
           "n_scene_cells": int(len(np.unique(scene[te]))), "accuracy": {}, "worst_group_accuracy": {},
           "splits": {}, "auc": {}}
    for label, q in (("ERM", raw["ERM"]), ("GRW", raw["GRW"]), ("ERM cal", cal["ERM"]), ("GRW cal", cal["GRW"])):
        pred = q.argmax(1)
        res["accuracy"][label] = float((pred == yt).mean())
        res["worst_group_accuracy"][label] = float(min((pred[grp[te] == g] == yt[grp[te] == g]).mean()
                                                       for g in range(4)))
    print("accuracy", {k: round(v, 4) for k, v in res["accuracy"].items()},
          "worst group", {k: round(v, 4) for k, v in res["worst_group_accuracy"].items()}, flush=True)

    for cell_name, phi in (("scene", scene[te]), ("background", place[te])):
        _, phi = np.unique(phi, return_inverse=True)
        elig = np.bincount(phi)[phi] >= 2
        res["splits"][cell_name] = {}
        for score in ("brier", "log"):
            res["splits"][cell_name][score] = split_rows(
                {"GRW vs ERM": (raw["GRW"], raw["ERM"]),
                 "ERM recalibrated vs ERM": (control, raw["ERM"]),
                 "GRW vs ERM, both recalibrated": (cal["GRW"], cal["ERM"])},
                yt, phi, image, score)
        res["auc"][cell_name] = {"ERM": within_cell_auc(raw["ERM"], yt, phi),
                                 "GRW": within_cell_auc(raw["GRW"], yt, phi)}
        for wt in ("comparison", "relation"):
            r = within_cell_auc_contrast(raw["GRW"], raw["ERM"], yt, phi, image, n_boot=200, weighting=wt)
            res["auc"][cell_name][f"GRW minus ERM, {wt}"] = {"difference": r.difference, "ci": list(r.ci)}
        for score in ("brier", "log"):
            for k, v in res["splits"][cell_name][score].items():
                print(f"{cell_name:10s} {score:5s} {k:32s} T {v['total']:+.5f} P {v['group']:+.5f} "
                      f"R {v['case']:+.5f} [{v['case_ci'][0]:+.5f},{v['case_ci'][1]:+.5f}]", flush=True)
        print(cell_name, "AUC", {k: (round(v, 4) if not isinstance(v, dict) else
                                     (round(v["difference"], 4), [round(c, 4) for c in v["ci"]]))
                                 for k, v in res["auc"][cell_name].items()}, flush=True)
    OUT.write_text(json.dumps(res, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
