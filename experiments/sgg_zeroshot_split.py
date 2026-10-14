"""Group-level / case-level split of the micro-pooled zero-shot recall@50 change.

Zero-shot status of a test relation is a function of its (subject, object) class
cell and its label: (subject, predicate, object) is in the benchmark's zero-shot
list. Writing zR@50 = sum_i w(phi_i, y_i) hit_i(y_i) with

    w(c, y) = 1{(c, y) is a zero-shot triplet} / n_zs,

the contrast h_i(y) = (n_e / n_zs) * 1{(phi_i, y) zero-shot} * [hit_new_i(y) - hit_old_i(y)]
is scored by decompose_gain_matrix (score="hit", image-clustered Hajek intervals), with
n_e the number of relations in cells with at least two relations, so that the mean of
h over eligible relations equals the zero-shot change. Transport keeps each cell's label
frequencies, so the zero-shot indicator of a transported label is evaluated at that label.

Relations whose cell holds only that relation have no within-cell counterfactual and are
not in decompose_gain_matrix's identified set. Their share of the direct change is
reported as a separate unidentified remainder, so that

    group-level + case-level + singleton remainder = direct micro-pooled zR@50 change

holds to 1e-9. Hits are graph-constrained recall@50 (gc@50), as in run_sgg_recall_split.py.

Writes results/sgg_zeroshot_split.json.
Run: python experiments/sgg_zeroshot_split.py
     (set WAGER_ZS_TRIPLETS to zeroshot_triplet.pytorch if it is not at the default path)
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
from wager.antisymmetric import decompose_gain_matrix  # noqa: E402
import sgg_interval_and_diagnostics as D  # noqa: E402
from run_sgg_recall_split import DDIR, N_PRED, N_OBJ  # noqa: E402

OUT = ROOT / "results/sgg_zeroshot_split.json"
TOL = 1e-9
COMPARISONS = [("TDE", "none"), ("la1", "none"), ("TDE", "la1")]
K_COL = N_PRED + 1


def log(msg):
    print(msg, flush=True)


def zero_shot_matrix(subj, obj, trip):
    """(N, K_COL) boolean: is (subject, predicate, object) a zero-shot triplet, for every predicate."""
    codes = (trip[:, 0] * N_OBJ + trip[:, 1]) * K_COL + trip[:, 2]
    cand = (subj * N_OBJ + obj)[:, None] * K_COL + np.arange(K_COL)[None, :]
    return np.isin(cand, codes)


def compare(new, old, y, phi, image, elig, is_zs, Zm, n_zs, n_e):
    ix = np.arange(len(y))
    hn, ho = D.hits(new), D.hits(old)
    own_n, own_o = hn[ix, y], ho[ix, y]
    direct = float(own_n[is_zs].mean() - own_o[is_zs].mean())
    zr_new = float(own_n[is_zs].mean())
    zr_old = float(own_o[is_zs].mean())

    diff = hn.astype(float) - ho.astype(float)
    h = (n_e / n_zs) * Zm.astype(float) * diff
    g = decompose_gain_matrix(h, y, phi, groups=image, alpha=D.ALPHA, score="hit")

    d_obs = diff[ix, y]
    singleton = is_zs & ~elig
    singleton_change = float(d_obs[singleton].sum() / n_zs)
    identified_change = float(d_obs[is_zs & elig].sum() / n_zs)

    assert abs(g.total_gain - identified_change) < TOL, (new, old, g.total_gain, identified_change)
    residual = g.prior_gain + g.alignment_gain + singleton_change - direct
    assert abs(residual) < TOL, (new, old, residual)
    assert abs(g.prior_gain + g.alignment_gain - g.total_gain) < TOL
    return {
        "zR50_new_micro": zr_new,
        "zR50_old_micro": zr_old,
        "direct_change": direct,
        "identified_change": float(g.total_gain),
        "unidentified_singleton_change": singleton_change,
        "group_level": float(g.prior_gain),
        "group_level_ci_image_clustered": [float(v) for v in g.prior_ci],
        "case_level": float(g.alignment_gain),
        "case_level_ci_image_clustered": [float(v) for v in g.alignment_ci],
        "identified_total_ci_image_clustered": [float(v) for v in g.total_ci],
        "case_share_of_identified": float(g.reasoning_share),
        "case_share_of_identified_ci_image_clustered": [float(v) for v in g.share_ci],
        "case_share_of_direct": float(g.alignment_gain / direct) if direct != 0 else None,
        "identity_residual": float(residual),
        "n_eligible_relations": int(elig.sum()),
        "n_zs_identified": int((is_zs & elig).sum()),
        "n_zs_unidentified_singleton": int(singleton.sum()),
        "matches_diagnostics_file": None,
    }


def main():
    t0 = time.perf_counter()
    meta = np.load(DDIR / "meta.npz")
    y = meta["pred"].astype(np.int64)
    subj = meta["subj"].astype(np.int64)
    obj = meta["obj"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    phi = subj * N_OBJ + obj
    n = len(y)
    ix = np.arange(n)

    is_zs, trip = D.zero_shot_mask(subj, obj, y)
    Zm = zero_shot_matrix(subj, obj, trip)
    assert np.array_equal(Zm[ix, y], is_zs), "zero-shot matrix disagrees with observed-label indicator"
    assert not Zm[:, 0].any()

    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1)
    elig = cnt[inv] >= 2
    n_e = int(elig.sum())
    n_zs = int(is_zs.sum())
    zs_cells = np.unique(inv[is_zs & elig])
    n_cells_ge2 = int((cnt >= 2).sum())
    n_cells_zs_ge2 = int(len(zs_cells))
    n_zs_in_those = int(np.sum(is_zs & np.isin(inv, zs_cells)))
    log(f"relations {n}, zero-shot {n_zs} ({n_zs / n:.4f}), eligible {n_e}, "
        f"zero-shot in singleton cells {int((is_zs & ~elig).sum())}, "
        f"cells with zs and >=2 relations {n_cells_zs_ge2} of {n_cells_ge2}")

    diag = json.loads((ROOT / "results/sgg_interval_and_diagnostics.json").read_text())
    diag_comps = diag["part3_diagnostics"]["comparisons"]

    comps = {}
    for new, old in COMPARISONS:
        key = f"{new} vs {old}"
        t1 = time.perf_counter()
        r = compare(new, old, y, phi, image, elig, is_zs, Zm, n_zs, n_e)
        dref = diag_comps[key]
        for a, b in (("zR50_new_micro", "zR50_new_micro"), ("zR50_old_micro", "zR50_old_micro")):
            assert abs(r[a] - dref[b]) < TOL, (key, a, r[a], dref[b])
        r["matches_diagnostics_file"] = True
        r["runtime_seconds"] = time.perf_counter() - t1
        comps[key] = r
        log(f"{key}: zR@50 micro {r['zR50_old_micro']:.6f} -> {r['zR50_new_micro']:.6f} "
            f"change {r['direct_change']:+.6f} = group {r['group_level']:+.6f} "
            f"+ case {r['case_level']:+.6f} [{r['case_level_ci_image_clustered'][0]:+.6f}, "
            f"{r['case_level_ci_image_clustered'][1]:+.6f}] + singleton {r['unidentified_singleton_change']:+.6f}; "
            f"case share of identified {r['case_share_of_identified']:.4f}; "
            f"residual {r['identity_residual']:.2e}")

    out = {
        "definition": {
            "zero_shot": "(subject class, predicate, object class) in the benchmark zero-shot list, "
                         "evaluated at the (cell, label) of each relation and of each transported label",
            "weight": "w(c, y) = 1{(c, y) zero-shot} / n_zs, micro-pooled over all test relations",
            "hits": "graph-constrained recall@50 (gc@50)",
            "contrast": "h_i(y) = (n_e / n_zs) * 1{(phi_i, y) zero-shot} * [hit_new_i(y) - hit_old_i(y)], "
                        "n_e = relations in cells with >= 2 relations",
            "estimator": "decompose_gain_matrix(score='hit', groups=image) over identified relations; "
                         "singleton-cell zero-shot relations enter as a separate unidentified remainder",
        },
        "n_relations": n,
        "n_zero_shot_relations": n_zs,
        "zero_shot_share_of_relations": n_zs / n,
        "n_zero_shot_identified": int((is_zs & elig).sum()),
        "n_zero_shot_unidentified_singleton": int((is_zs & ~elig).sum()),
        "n_eligible_relations": n_e,
        "n_cells_ge2": n_cells_ge2,
        "n_cells_with_zero_shot_and_ge2": n_cells_zs_ge2,
        "share_of_cells_ge2_with_zero_shot": n_cells_zs_ge2 / n_cells_ge2,
        "n_zero_shot_relations_in_those_cells": n_zs_in_those,
        "comparisons": comps,
        "runtime_seconds": time.perf_counter() - t0,
    }
    OUT.write_text(json.dumps(out, indent=1))
    log(f"wrote {OUT.relative_to(ROOT)} in {out['runtime_seconds']:.1f} s")


if __name__ == "__main__":
    main()
