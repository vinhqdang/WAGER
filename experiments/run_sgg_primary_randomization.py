"""Cyclic randomization test under the paper's primary recalibration protocol.

The supplement's cyclic randomization p for TDE against the baseline came from the
temperature-only matched protocol (run_sgg_audit_wager.py). The primary protocol is
temperature plus a per-class bias, fitted per model on the calibration half and applied
to the audit half, using the renormalised probabilities Q (as in
run_sgg_rank_robustness.recalibration_rows). This script reruns the test under that
protocol, and reruns the temperature-only protocol for TDE against the baseline as a
check against the stored p = .555.

For each case the case-level part (decompose_gain(...).alignment_gain) is recorded and
compared with the stored recalibration rows in results/sgg_rank_robustness.json.

Run: python experiments/run_sgg_primary_randomization.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import cyclic_randomization_test, decompose_gain  # noqa: E402
import run_sgg_audit_wager as AU  # noqa: E402
import run_sgg_rank_robustness as RR  # noqa: E402

RES = ROOT / "results"
OUT = RES / "sgg_primary_randomization.json"
N_RANDOMIZATIONS, SEED = 999, 1
EPS = 1e-12
PRIMARY = "temperature + class bias"
COMPARISONS = (("TDE", "none"), ("la1", "none"), ("TDE", "la1"))
SCORES = ("brier", "log")


def main():
    t0 = time.time()
    Q, raw, y, phi, image, cal = RR.sgg_data()
    aud = ~cal
    L = {v: np.log(np.clip(q, EPS, None)) for v, q in Q.items()}
    cache = {}

    def calibrated(family, v):
        """Each model's recalibrated audit-half probabilities, fitted on the cal half."""
        if (family, v) not in cache:
            if family == "temperature":
                T = AU.fit_temperature(Q[v][cal], y[cal])
                cache[family, v] = AU.temp_scale(Q[v], T)[aud]
            else:
                p = RR.fit_family(L[v][cal], y[cal], bias=True)
                cache[family, v] = RR.apply_family(L[v], p, True)[aud]
        return cache[family, v]

    stored = json.loads((RES / "sgg_rank_robustness.json").read_text())["recalibration"]
    stored = {(r["new"], r["old"]): r for r in stored}

    def run(new, old, family, sc, randomize=True):
        qn, qo = calibrated(family, new), calibrated(family, old)
        with np.errstate(all="ignore"):
            g = decompose_gain(qn, qo, y[aud], phi[aud], groups=image[aud], score=sc)
        row = {"comparison": f"{new} vs {old}", "family": family, "score": sc,
               "case": float(g.alignment_gain), "case_ci": [float(x) for x in g.alignment_ci],
               "total": float(g.total_gain), "group": float(g.prior_gain)}
        if randomize:
            p, _ = cyclic_randomization_test(qn, qo, y[aud], phi[aud], score=sc,
                                             n_randomizations=N_RANDOMIZATIONS, seed=SEED)
            row["randomization_p"] = float(p)
        srow = stored.get((new, old))
        if srow is not None and f"{family}, {sc}" in srow:
            s = srow[f"{family}, {sc}"]["case"]
            row["stored_case"] = float(s)
            row["case_abs_diff_from_stored"] = abs(row["case"] - s)
        ptxt = f"p={row['randomization_p']:.3f}" if randomize else "p=-"
        stxt = (f"stored {row['stored_case']:+.5f} |diff| {row['case_abs_diff_from_stored']:.1e}"
                if "stored_case" in row else "stored n/a")
        print(f"{row['comparison']:14s} {family:26s} {sc:6s} {ptxt} case {row['case']:+.5f} "
              f"CI [{row['case_ci'][0]:+.5f},{row['case_ci'][1]:+.5f}] {stxt} "
              f"({time.time() - t0:.0f}s)", flush=True)
        return row

    rows = [run(new, old, PRIMARY, sc) for new, old in COMPARISONS for sc in SCORES]
    check = run("TDE", "none", "temperature", "brier")
    print(f"temperature-only check: TDE vs none brier p={check['randomization_p']:.4f} "
          f"(stored supplement value .555)", flush=True)

    out = {"n_randomizations": N_RANDOMIZATIONS, "seed": SEED,
           "primary_family": PRIMARY,
           "protocol": "temperature and per-class bias fitted per model on the calibration "
                       "half, applied and tested on the audit half, renormalised probabilities",
           "rows": rows, "temperature_check": check}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}  total {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
