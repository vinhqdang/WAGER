"""Numerical check of the Proposition 3 (unrecorded-confounder) sensitivity bound.

Reads the already-committed coarsening ablation (results/antisymmetric_ablations.json,
produced by antisymmetric_ablations.py) and treats the coarsening from the class-pair
cell (subject, object) down to the subject-only cell as an instance of "declaring
phi = subject-only and leaving Z = object unrecorded." The exact bias this omission
causes is available directly as the difference of the two already-reported aggregate
alignment gains (law of total expectation applied to Proposition 2, summed over cells);
this script reports that empirical bias next to the crude Cauchy-Schwarz/Popoviciu bound
of Proposition 3, to show how loose the bound is at VG150's scale (K=50).

The free bound is M*sqrt(K-1), not the K*M/2 reported before 2026-09: bounding
sum_y Var(b_y) by Popoviciu's K/4 discards the constraint that the label probabilities
b_y sum to one, which forces sum_y Var(b_y) <= 1 - 1/K.  At K=50, M=2 that is 14.00
rather than 50.00, a factor of 3.57.
"""
from __future__ import annotations

import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = 50          # VG150 predicate vocabulary
M = 2.0         # Brier-score contrast H_x(y) in [-2, 2]; see Section 3.1


def main():
    with open(os.path.join(ROOT, "results", "antisymmetric_ablations.json"), encoding="utf-8") as f:
        ablations = json.load(f)
    rows = {r["setting"]: r for r in ablations["rows"] if r["factor"] == "prior feature"}
    fine = rows["class-pair"]["reasoning_gain"]
    coarse = rows["subject-only"]["reasoning_gain"]
    empirical_bias = coarse - fine  # law of total expectation applied to Eq. (coarsen)

    # sum_y Var(a_y) <= K*M^2 (each a_y in [-M, M]);
    # sum_y Var(b_y) <= 1 - 1/K, because sum_y b_y = 1 gives sum_y b_y^2 <= 1 while
    # sum_y (E b_y)^2 >= 1/K by Cauchy-Schwarz.  Hence the free bound is
    #   sqrt(K*M^2) * sqrt(1 - 1/K) = M * sqrt(K - 1).
    crude_bound = M * math.sqrt(K - 1.0)
    superseded_bound = K * M / 2.0   # the pre-2026-09 value, retained for the record
    rho_required = abs(empirical_bias) / crude_bound  # smallest rho for which Eq. (sensitivity-bound) holds

    out = {
        "K": K,
        "M": M,
        "delta_r_class_pair_phi": fine,
        "delta_r_subject_only_phi": coarse,
        "empirical_coarsening_bias": empirical_bias,
        "crude_cauchy_schwarz_bound": crude_bound,
        "superseded_popoviciu_bound": superseded_bound,
        "minimum_rho_for_bound_to_hold": rho_required,
        "looseness_ratio": crude_bound / abs(empirical_bias),
        "note": (
            "Free bound M*sqrt(K-1); the earlier K*M/2 discarded sum_y b_y = 1. The bound "
            "holds for any rho >= minimum_rho_for_bound_to_hold; since that threshold is "
            "far below 1, the free bound is directionally correct but still conservative "
            "at VG150's K=50 scale, which is why Section 3.5 now reports the sharp, "
            "per-cell bound of results/sensitivity_bound.json alongside it."
        ),
    }
    with open(os.path.join(ROOT, "results", "sensitivity_bound_check.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
