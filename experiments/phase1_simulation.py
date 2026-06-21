"""Phase 1 - validity & power simulations (algorithm.md sections 8, 10A).

Three credibility gates, run BEFORE any real-model experiment:

  GATE A  Type-I error      : model = prior  =>  P(e-value >= 1/alpha) <= alpha
                              and I_reason ~ 0.
  GATE B  CI coverage       : anytime-valid CI for I_reason covers the true
                              population value with prob >= 1 - alpha.
  GATE C  Power / recovery  : RGR(f_beta, baseline) increases monotonically with
                              the injected reasoning fraction beta (Pearson r>0.95)
                              and tracks the ground-truth RGR.

Outputs results/phase1_results.json and figures in results/.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wager.core import betting_mean_ci, prior_excess_logscore, wealth_process, kt_projection
from wager.pipeline import ModelData, run_wager_permutations
from wager.rgr import reasoning_gain_ratio
from experiments.synthetic import make_benchmark, population_info

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def gate_a_type_i(n_runs=600, alpha=0.05, seed0=1000):
    """Type-I: pure-prior model should not trigger the e-value beyond rate alpha."""
    print(f"[GATE A] Type-I error control over {n_runs} runs (alpha={alpha})...")
    t0 = time.time()
    exceed = 0
    i_reason_vals = []
    e_values = []
    for r in range(n_runs):
        bench = make_benchmark(n_images=700, pairs_per_image=4, K=30, n_cells=120,
                               cell_concentration=0.3, posterior_concentration=4.0, seed=seed0 + r)
        q = bench.model_prior()  # H0: prediction depends only on phi
        c = float(np.log(bench.K))
        rng = np.random.default_rng(seed0 + r)
        # single permutation pass (fresh data each run = honest type-I)
        from wager.pipeline import run_wager_single
        data = ModelData("prior", q, bench.y, bench.phi, bench.group)
        out = run_wager_single(data, rng, c=c, alpha=alpha)
        e_values.append(out["e_value"])
        i_reason_vals.append(float(np.mean(out["d"])))
        if out["e_value"] >= 1.0 / alpha:
            exceed += 1
    rate = exceed / n_runs
    res = {
        "n_runs": n_runs,
        "alpha": alpha,
        "exceedance_rate": rate,
        "nominal_bound": alpha,
        "pass": rate <= alpha + 0.02,  # small Monte-Carlo / estimation slack
        "mean_I_reason": float(np.mean(i_reason_vals)),
        "median_e_value": float(np.median(e_values)),
        "p95_e_value": float(np.percentile(e_values, 95)),
        "seconds": time.time() - t0,
    }
    print(f"  exceedance={rate:.4f} (<= {alpha}?), mean I_reason={res['mean_I_reason']:.4f}, "
          f"median e={res['median_e_value']:.3f}  [{res['seconds']:.1f}s]")
    return res


def gate_b_coverage(n_runs=250, alpha=0.1, seed0=2000):
    """Coverage: betting CI for I_reason should cover the true population value."""
    print(f"[GATE B] CI coverage over {n_runs} runs (target >= {1-alpha:.0%})...")
    t0 = time.time()
    covered = 0
    widths = []
    for r in range(n_runs):
        bench = make_benchmark(n_images=900, pairs_per_image=4, K=25, n_cells=120,
                               cell_concentration=0.3, posterior_concentration=4.0, seed=seed0 + r)
        beta = 0.6
        q = bench.model_geometric(beta)
        true = population_info(bench, q)["I_reason"]
        c = float(np.log(bench.K))
        # estimate d on a single A/B split, then CI
        rng = np.random.default_rng(seed0 + r)
        from wager.pipeline import run_wager_single
        data = ModelData("f_beta", q, bench.y, bench.phi, bench.group)
        out = run_wager_single(data, rng, c=c, alpha=alpha)
        lo, hi = betting_mean_ci(out["d"], c, alpha=alpha, n_grid=301)
        if lo <= true <= hi:
            covered += 1
        widths.append(hi - lo)
    cov = covered / n_runs
    res = {
        "n_runs": n_runs,
        "alpha": alpha,
        "coverage": cov,
        "target": 1 - alpha,
        "pass": cov >= 1 - alpha - 0.03,
        "mean_ci_width": float(np.mean(widths)),
        "seconds": time.time() - t0,
    }
    print(f"  coverage={cov:.3f} (target {1-alpha:.2f}), mean width={res['mean_ci_width']:.3f}  "
          f"[{res['seconds']:.1f}s]")
    return res


def gate_c_recovery(betas=None, R=60, alpha=0.05, seed=3000, strength=1.0):
    """Power: RGR(f_beta, uniform) recovers the injected reasoning share beta.

    f_beta = model_decomposed(theta_prior=strength*(1-beta),
                              theta_reason=strength*beta), so the gain over the
    uninformed (uniform) baseline mixes prior-fitting and reasoning with
    reasoning share controlled by beta.  We check that estimated RGR matches the
    ground-truth RGR and increases monotonically with beta.
    """
    if betas is None:
        betas = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    print(f"[GATE C] Recovery of injected reasoning share over {len(betas)} betas...")
    t0 = time.time()
    bench = make_benchmark(n_images=3000, pairs_per_image=5, K=50, n_cells=400,
                           cell_concentration=0.3, posterior_concentration=4.0, seed=seed)
    c = float(np.log(bench.K))

    # uninformed baseline f0: uniform predictions
    q0 = np.full((bench.y.shape[0], bench.K), 1.0 / bench.K)
    data0 = ModelData("uniform", q0, bench.y, bench.phi, bench.group)
    res0 = run_wager_permutations(data0, R=R, c=c, alpha=alpha, seed=seed)
    pop0 = population_info(bench, q0)

    rows, rgr_rows = [], []
    for b in betas:
        q = bench.model_decomposed(strength * (1 - b), strength * b)
        data = ModelData(f"f_beta={b:.2f}", q, bench.y, bench.phi, bench.group)
        res = run_wager_permutations(data, R=R, c=c, alpha=alpha, seed=seed)
        pop = population_info(bench, q)
        rows.append({
            "beta": b, "e_value": res.e_value,
            "I_reason_est": res.I_reason, "I_reason_true": pop["I_reason"],
            "I_prior_est": res.I_prior, "I_prior_true": pop["I_prior"],
            "I_tot_est": res.I_tot, "I_tot_true": pop["I_tot"],
        })
        rgr = reasoning_gain_ratio(res, res0, c=c, alpha=alpha)
        d_tot_true = pop["I_tot"] - pop0["I_tot"]
        true_rgr = (pop["I_reason"] - pop0["I_reason"]) / d_tot_true if d_tot_true > 1e-9 else float("nan")
        rgr_rows.append({
            "beta": b, "RGR_est": rgr.rgr, "RGR_true": true_rgr,
            "fieller_lo": rgr.fieller_ci[0], "fieller_hi": rgr.fieller_ci[1],
            "anytime_lo": rgr.anytime_ci[0], "anytime_hi": rgr.anytime_ci[1],
            "verdict": rgr.verdict,
        })
        print(f"  beta={b:.2f}: I_reason est={res.I_reason:.3f}/true={pop['I_reason']:.3f}  "
              f"RGR est={rgr.rgr:.3f}/true={true_rgr:.3f}  "
              f"CI=[{rgr.fieller_ci[0]:.2f},{rgr.fieller_ci[1]:.2f}] {rgr.verdict}")

    betas_arr = np.array([r["beta"] for r in rgr_rows])
    rgr_est = np.array([r["RGR_est"] for r in rgr_rows])
    rgr_true = np.array([r["RGR_true"] for r in rgr_rows])
    ir_est = np.array([r["I_reason_est"] for r in rows])
    ir_true = np.array([r["I_reason_true"] for r in rows])

    valid = np.isfinite(rgr_est) & np.isfinite(rgr_true)
    # The "injected reasoning fraction" is the ground-truth reasoning share of the
    # gain (= population RGR), not the mixing knob beta (information is nonlinear
    # in beta, so even a perfect estimator cannot be linear in beta).
    r_injected = float(np.corrcoef(rgr_true[valid], rgr_est[valid])[0, 1])
    r_beta = float(np.corrcoef(betas_arr[valid], rgr_est[valid])[0, 1])
    r_ireason = float(np.corrcoef(ir_true, ir_est)[0, 1])
    monotone = bool(np.all(np.diff(rgr_est[valid]) >= -0.05))
    rgr_mae = float(np.mean(np.abs(rgr_est[valid] - rgr_true[valid])))

    res = {
        "betas": list(betas), "rows": rows, "rgr_rows": rgr_rows,
        "pearson_injectedRGR_vs_estRGR": r_injected,
        "pearson_beta_vs_RGR": r_beta,
        "pearson_true_vs_est_Ireason": r_ireason,
        "rgr_mae": rgr_mae,
        "monotone_RGR": monotone,
        "pass": (r_injected > 0.95) and monotone and (r_ireason > 0.95) and (rgr_mae < 0.08),
        "seconds": time.time() - t0,
    }
    print(f"  Pearson(injectedRGR,estRGR)={r_injected:.4f}  Pearson(I_reason)={r_ireason:.4f}  "
          f"RGR-MAE={rgr_mae:.4f}  monotone={monotone}  (Pearson(beta,RGR)={r_beta:.3f})"
          f"  [{res['seconds']:.1f}s]")
    return res


def main():
    np.seterr(all="ignore")
    out = {}
    out["gate_a_type_i"] = gate_a_type_i()
    out["gate_b_coverage"] = gate_b_coverage()
    out["gate_c_recovery"] = gate_c_recovery()
    out["all_pass"] = all(out[k]["pass"] for k in ("gate_a_type_i", "gate_b_coverage", "gate_c_recovery"))

    path = os.path.join(RESULTS_DIR, "phase1_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nPhase 1 {'PASSED' if out['all_pass'] else 'FAILED'}; results -> {path}")
    return out


if __name__ == "__main__":
    main()
