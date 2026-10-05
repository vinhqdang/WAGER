"""How much the confidence-matched SGG split depends on the image split (REV-3).

The matched rows of the audit fit each model's temperature on one random half of
the test images and split the other half. This repeats that for 20 independent
image splits, for TDE, the logit-adjusted baseline (LA) and IETrans against the
MOTIFS baseline, under the quadratic and log scores. It also adds the variant the
review asked for when two models share weights: one temperature for both, fitted
on the pooled calibration half.

Run: python experiments/run_sgg_split_robustness.py
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
import run_sgg_audit_wager as AU  # noqa: E402

OUT = ROOT / "results/sgg_split_robustness.json"
N_SPLITS = 20
NEW = ["TDE", "la1", "ietrans"]


def fit_common(qa, qb, y):
    grid = np.geomspace(0.05, 20.0, 240)
    nll = [float(-np.mean(np.log(np.clip(AU.temp_scale(qa, t)[np.arange(len(y)), y], 1e-12, None)))
                 - np.mean(np.log(np.clip(AU.temp_scale(qb, t)[np.arange(len(y)), y], 1e-12, None))))
           for t in grid]
    return float(grid[int(np.argmin(nll))])


def main():
    base = AU.load("none")
    y, image = base["y"], base["image"]
    phi = base["subj"] * AU.N_OBJ + base["obj"]
    Q = {"none": base["q"], **{v: AU.load(v)["q"] for v in NEW}}
    imgs = np.unique(image)
    rows = []
    for s in range(N_SPLITS):
        rng = np.random.default_rng(1000 + s)
        cal_imgs = set(imgs[rng.permutation(len(imgs))[: len(imgs) // 2]].tolist())
        cal = np.array([i in cal_imgs for i in image])
        aud = np.where(~cal)[0]
        T = {v: AU.fit_temperature(q[cal], y[cal]) for v, q in Q.items()}
        row = {"split": s, "T": T}
        for v in NEW:
            for sc in ("brier", "log"):
                with np.errstate(all="ignore"):
                    g = decompose_gain(AU.temp_scale(Q[v], T[v])[aud],
                                       AU.temp_scale(Q["none"], T["none"])[aud],
                                       y[aud], phi[aud], groups=image[aud], score=sc)
                row[f"{v} {sc}"] = {"total": g.total_gain, "group": g.prior_gain,
                                    "case": g.alignment_gain, "case_ci": list(g.alignment_ci)}
        tc = fit_common(Q["TDE"][cal], Q["none"][cal], y[cal])
        row["T_common"] = tc
        for sc in ("brier", "log"):
            with np.errstate(all="ignore"):
                g = decompose_gain(AU.temp_scale(Q["TDE"], tc)[aud], AU.temp_scale(Q["none"], tc)[aud],
                                   y[aud], phi[aud], groups=image[aud], score=sc)
            row[f"TDE common-T {sc}"] = {"total": g.total_gain, "group": g.prior_gain,
                                         "case": g.alignment_gain, "case_ci": list(g.alignment_ci)}
        rows.append(row)
        print(f"split {s:2d}: " + "  ".join(
            f"{k} {row[k]['case']:+.5f}" for k in row if isinstance(row[k], dict) and "case" in row[k]),
            flush=True)
        OUT.write_text(json.dumps({"n_splits": len(rows), "rows": rows}, indent=1))

    summary = {}
    for k in [k for k in rows[0] if isinstance(rows[0][k], dict) and "case" in rows[0][k]]:
        c = np.array([r[k]["case"] for r in rows])
        sig = int(sum(r[k]["case_ci"][0] > 0 or r[k]["case_ci"][1] < 0 for r in rows))
        summary[k] = {"mean": float(c.mean()), "sd": float(c.std(ddof=1)), "min": float(c.min()),
                      "max": float(c.max()), "n_excluding_zero": sig,
                      "n_positive": int((c > 0).sum())}
        print(f"{k:22s} mean {c.mean():+.5f} sd {c.std(ddof=1):.5f} range [{c.min():+.5f}, "
              f"{c.max():+.5f}]  CI excludes 0 in {sig}/{len(rows)}")
    OUT.write_text(json.dumps({"n_splits": len(rows), "summary": summary, "rows": rows}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
