"""Aggregate WAGER analysis over the CIFAR-100-LT seed/ratio matrix.

Consumes every data/cifar_lt/cifar_lt_*.npz (the original seed-0 file plus the
matrix produced by colab_cifar_multiseed.py) and reports, per configuration:

  - raw and calibration-matched decompositions (held-out temperature, 20
    splits, as in cifar_recalibration_control.py) for CB vs CE and DRW vs CE;
  - a post-hoc logit-adjustment arm LA(CE) vs CE: q_LA(y|x) proportional to
    q_CE(y|x) / pi_train(y), the classical pure-prior correction. Because it
    adds no instance information, its decomposition must be almost entirely
    prior channel -- the cheap falsification case for the channel semantics.

Across seeds at the primary ratio it prints mean +/- sd of each channel, the
across-seed uncertainty that single-run intervals cannot express.

Run: conda run -n py313 python experiments/run_cifar_multiseed_wager.py
"""
from __future__ import annotations

import glob
import json
import pathlib
import re
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from wager.antisymmetric import decompose_gain

ROOT = pathlib.Path(__file__).resolve().parents[1]
N_SPLITS = 20
T_GRID = np.geomspace(0.05, 20.0, 240)
coarse = np.load(ROOT / "data/cifar_lt/coarse_of_class.npy")


def temp_scale(p, T, eps=1e-12):
    z = np.log(np.clip(p, eps, None)) / T
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def nll(p, labels, eps=1e-12):
    return float(-np.mean(np.log(np.clip(p[np.arange(len(labels)), labels], eps, None))))


def fit_temperature(p, labels):
    return float(T_GRID[int(np.argmin([nll(temp_scale(p, t), labels) for t in T_GRID]))])


def logit_adjust(p, train_counts, tau=1.0, eps=1e-12):
    pi = train_counts / train_counts.sum()
    z = np.log(np.clip(p, eps, None)) - tau * np.log(pi)[None, :]
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def analyze(path: pathlib.Path) -> dict:
    d = np.load(path)
    y = d["y_test"]
    phi = coarse[y]
    models = {
        "CE": d["probs_baseline"].astype(np.float64),
        "CB": d["probs_cb"].astype(np.float64),
        "DRW": d["probs_drw"].astype(np.float64),
    }
    models["LA"] = logit_adjust(models["CE"], d["per_class_train_n"].astype(float))
    acc = {m: float(np.mean(q.argmax(1) == y)) for m, q in models.items()}

    rows: dict[str, list] = {}
    rng = np.random.default_rng(20260811)
    for _ in range(N_SPLITS):
        perm = rng.permutation(len(y))
        cal, aud = perm[: len(y) // 2], perm[len(y) // 2:]
        T = {m: fit_temperature(q[cal], y[cal]) for m, q in models.items()}
        cal_p = {m: temp_scale(q, T[m]) for m, q in models.items()}
        for new in ("CB", "DRW", "LA"):
            g = decompose_gain(models[new][aud], models["CE"][aud], y[aud], phi[aud])
            rows.setdefault(f"{new} raw", []).append(
                (g.total_gain, g.prior_gain, g.reasoning_gain))
            g = decompose_gain(cal_p[new][aud], cal_p["CE"][aud], y[aud], phi[aud])
            rows.setdefault(f"{new} cal", []).append(
                (g.total_gain, g.prior_gain, g.reasoning_gain))
    out = {"accuracy": acc,
           "imbalance_ratio": float(d["imbalance_ratio"]), "seed": int(d["seed"])}
    for name, vals in rows.items():
        a = np.asarray(vals)
        out[name] = {"dT": round(float(a[:, 0].mean()), 5),
                     "dP": round(float(a[:, 1].mean()), 5),
                     "dR": round(float(a[:, 2].mean()), 5),
                     "dR_sd": round(float(a[:, 2].std(ddof=1)), 5)}
    return out


def main():
    results = {}
    files = sorted(glob.glob(str(ROOT / "data/cifar_lt/cifar_lt_*.npz")))
    for f in files:
        p = pathlib.Path(f)
        m = re.search(r"cifar_lt_r(\d+)_s(\d+)", p.name)
        tag = f"r{m.group(1)}_s{m.group(2)}" if m else "r100_s0"
        print(f"=== {tag} ({p.name})", flush=True)
        results[tag] = analyze(p)
        for k, v in results[tag].items():
            if isinstance(v, dict) and "dT" in v:
                print(f"  {k:8s} dT={v['dT']:+.5f} dP={v['dP']:+.5f} "
                      f"dR={v['dR']:+.5f} ({v['dR_sd']:.5f})", flush=True)
        print(f"  acc: {results[tag]['accuracy']}", flush=True)

    # across-seed summary at the primary ratio
    seeds = {t: r for t, r in results.items() if t.startswith("r100")}
    if len(seeds) > 1:
        print(f"\n=== across {len(seeds)} seeds at ratio 100 (mean +/- sd)")
        summary = {}
        for arm in ("CB raw", "CB cal", "DRW raw", "DRW cal", "LA raw", "LA cal"):
            for ch in ("dT", "dP", "dR"):
                v = np.array([r[arm][ch] for r in seeds.values()])
                summary[f"{arm}.{ch}"] = {"mean": round(float(v.mean()), 5),
                                          "sd": round(float(v.std(ddof=1)), 5)}
            m = summary
            print(f"  {arm:8s} dT={m[arm+'.dT']['mean']:+.5f}({m[arm+'.dT']['sd']:.5f}) "
                  f"dP={m[arm+'.dP']['mean']:+.5f}({m[arm+'.dP']['sd']:.5f}) "
                  f"dR={m[arm+'.dR']['mean']:+.5f}({m[arm+'.dR']['sd']:.5f})", flush=True)
        results["across_seeds_r100"] = summary

    dest = ROOT / "results/cifar_multiseed.json"
    dest.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
