"""Official-statistic group / case split of gc@50 for all requested comparisons.

Same estimator as run_sgg_image_weighted.py (imported, not modified): the official per-image
mean recall change over eligible relations is split into a group part (expected change under
uniform within-cell label permutations, 200 seeds) and a case part (total minus group). The
case interval is a delete-a-group jackknife over images (50 groups, 50 permutations per
replicate, same seeds). The image-weighted floor is also computed, and its total must equal the
official change exactly.

Additions for this run, each derived from the same jackknife replicates:
  - a 95% interval for the group part (z-interval with the group's jackknife SE);
  - a 95% interval for the share group / total (z-interval with the jackknife SE of the share).
The image-weighted floor's total interval is the image-clustered Hajek interval, as stored.

Reproduces TDE vs none first and asserts it against results/sgg_image_weighted.json (1e-6).

Writes results/sgg_official_split_all.json.
Run: python experiments/sgg_official_split_all.py
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
import run_sgg_image_weighted as RIW  # noqa: E402
from run_sgg_recall_split import DDIR, N_OBJ, RESULTS  # noqa: E402
from sgg_variants import load_variant  # noqa: E402

OUT = RESULTS / "sgg_official_split_all.json"
K = 50
TOL = 1e-6                       # reproduction tolerance for the stored TDE vs none values
COMPARISONS = [("TDE", "none"), ("la1", "none"), ("ietrans", "none"), ("dlfe", "dlfe_base"),
               ("penet", "none"), ("penet", "dlfe_base"), ("TDE", "la1"), ("dlfe_base", "none")]
MODELS = ("none", "TDE", "la1", "ietrans", "dlfe", "dlfe_base", "penet")
Z = RIW.NormalDist().inv_cdf(1.0 - RIW.ALPHA / 2.0)


def log(msg):
    print(msg, flush=True)


def estimate(new, old, H, ctx):
    """Permutation estimator for gc@K as in run_sgg_image_weighted.main, for one comparison."""
    y, phi, image, eligible = ctx["y"], ctx["phi"], ctx["image"], ctx["eligible"]
    elig_idx, y_e, cell_e, img_e = ctx["elig_idx"], ctx["y_e"], ctx["cell_e"], ctx["img_e"]
    ix = np.arange(len(y))
    hn, ho = H[new], H[old]

    g = RIW.image_split(hn, ho, y, phi, image, eligible)
    m_new, m_old, official = RIW.official_change_eligible(hn, ho, y, image, eligible, ix)
    gap = g.total_gain - official
    assert abs(gap) < RIW.TOL, (new, old, gap)

    # observed-label values
    p0 = RIW.prep(y_e, img_e)
    obs_hn = hn[elig_idx, y_e].astype(np.float64)
    obs_ho = ho[elig_idx, y_e].astype(np.float64)
    obs_off = RIW.eval_off(p0, obs_hn) - RIW.eval_off(p0, obs_ho)
    assert abs(obs_off - official) < RIW.TOL, (new, old, obs_off, official)
    obs_mic = RIW.eval_mic(p0, obs_hn) - RIW.eval_mic(p0, obs_ho)

    # full-sample permutations
    perms = RIW.make_perms(y_e, cell_e, range(1, RIW.N_PERM + 1))
    acc_off = np.empty(RIW.N_PERM)
    acc_mic = np.empty(RIW.N_PERM)
    for r, yp in enumerate(perms):
        p = RIW.prep(yp, img_e)
        hv_n = hn[elig_idx, yp].astype(np.float64)
        hv_o = ho[elig_idx, yp].astype(np.float64)
        acc_off[r] = RIW.eval_off(p, hv_n) - RIW.eval_off(p, hv_o)
        acc_mic[r] = RIW.eval_mic(p, hv_n) - RIW.eval_mic(p, hv_o)
    total = float(official)
    group = float(acc_off.mean())
    group_mc_se = float(acc_off.std(ddof=1) / np.sqrt(RIW.N_PERM))
    case = total - group
    share = group / total

    # delete-a-group jackknife over images (same grouping as the script)
    grp_img = np.random.default_rng(0).permutation(ctx["n_img"]) % RIW.N_JACK
    grp_e = grp_img[img_e]
    th_case = np.empty(RIW.N_JACK)
    th_group = np.empty(RIW.N_JACK)
    th_total = np.empty(RIW.N_JACK)
    th_mic_group = np.empty(RIW.N_JACK)
    for gidx in range(RIW.N_JACK):
        keep = grp_e != gidx
        sub = elig_idx[keep]
        ys, cs, ims = y_e[keep], cell_e[keep], img_e[keep]
        pj0 = RIW.prep(ys, ims)
        tot = (RIW.eval_off(pj0, hn[sub, ys].astype(np.float64))
               - RIW.eval_off(pj0, ho[sub, ys].astype(np.float64)))
        gsum = 0.0
        gsum_m = 0.0
        for yp in RIW.make_perms(ys, cs, range(1, RIW.N_PERM_JACK + 1)):
            p = RIW.prep(yp, ims)
            hv_n = hn[sub, yp].astype(np.float64)
            hv_o = ho[sub, yp].astype(np.float64)
            gsum += RIW.eval_off(p, hv_n) - RIW.eval_off(p, hv_o)
            gsum_m += RIW.eval_mic(p, hv_n) - RIW.eval_mic(p, hv_o)
        th_total[gidx] = tot
        th_group[gidx] = gsum / RIW.N_PERM_JACK
        th_case[gidx] = tot - gsum / RIW.N_PERM_JACK
        th_mic_group[gidx] = gsum_m / RIW.N_PERM_JACK

    def jk_se(theta):
        return float(np.sqrt((RIW.N_JACK - 1.0) / RIW.N_JACK * np.sum((theta - theta.mean()) ** 2)))

    case_se = jk_se(th_case)
    group_se = jk_se(th_group)
    share_se = jk_se(th_group / th_total)
    mic_group = float(acc_mic.mean())
    micro_ref = RIW.micro_reference(new, old, K)
    mic_check = {"total": float(obs_mic), "group": mic_group, "group_mc_se": float(acc_mic.std(ddof=1) / np.sqrt(RIW.N_PERM)),
                 "case": float(obs_mic - mic_group)}
    if micro_ref is not None:
        mic_check.update({"analytic_group": micro_ref["group"], "analytic_case": micro_ref["case"],
                          "gap_group": mic_group - micro_ref["group"],
                          "gap_group_in_mc_se": (mic_group - micro_ref["group"]) / mic_check["group_mc_se"]})
    return {
        "total": total,
        "total_check_official_new": float(m_new),
        "total_check_official_old": float(m_old),
        "group": group,
        "group_mc_se": group_mc_se,
        "group_jk_se": group_se,
        "group_ci": [group - Z * group_se, group + Z * group_se],
        "case": case,
        "case_jk_se": case_se,
        "case_ci": [case - Z * case_se, case + Z * case_se],
        "share": share,
        "share_jk_se": share_se,
        "share_ci": [share - Z * share_se, share + Z * share_se],
        "floor": {"total": float(g.total_gain), "group": float(g.prior_gain), "case": float(g.alignment_gain),
                  "case_ci_hajek": [float(v) for v in g.alignment_ci],
                  "total_ci_hajek": [float(v) for v in g.total_ci]},
        "micro_check": mic_check,
        "n_perm": RIW.N_PERM, "n_jack_groups": RIW.N_JACK, "n_perm_per_jack": RIW.N_PERM_JACK,
    }


def main():
    t_all = time.perf_counter()
    meta = np.load(DDIR / "meta.npz")
    y = meta["pred"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    phi = meta["subj"].astype(np.int64) * N_OBJ + meta["obj"].astype(np.int64)
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1).astype(np.int64)
    eligible = cnt[inv] >= 2
    image_compact = np.unique(image, return_inverse=True)[1].reshape(-1).astype(np.int64)
    elig_idx = np.flatnonzero(eligible)
    ctx = {
        "y": y, "phi": phi, "image": image, "eligible": eligible,
        "elig_idx": elig_idx, "y_e": y[elig_idx], "cell_e": inv[elig_idx], "img_e": image_compact[elig_idx],
        "n_img": int(image_compact.max()) + 1,
    }
    log(f"relations {len(y)}, eligible {int(eligible.sum())}, images {ctx['n_img']}")

    H = {m: load_variant(m)["gc_rank"] < K for m in MODELS}
    log("hit matrices loaded for " + ", ".join(MODELS))

    # reproduce the stored TDE vs none estimate before anything else
    stored = json.loads((RESULTS / "sgg_image_weighted.json").read_text())["comparisons"]["TDE vs none"]["gc@50"]
    t0 = time.perf_counter()
    rep = estimate("TDE", "none", H, ctx)
    rep_secs = time.perf_counter() - t0
    checks = {
        "total": (rep["total"], stored["total"]),
        "group": (rep["group"], stored["permutation"]["group"]),
        "case": (rep["case"], stored["permutation"]["case"]),
        "case_ci_lo": (rep["case_ci"][0], stored["permutation"]["case_ci"][0]),
        "case_ci_hi": (rep["case_ci"][1], stored["permutation"]["case_ci"][1]),
        "share": (rep["share"], stored["permutation"]["share"]),
        "floor_group": (rep["floor"]["group"], stored["group"]),
        "floor_case": (rep["floor"]["case"], stored["case"]),
        "micro_group": (rep["micro_check"]["group"], stored["permutation"]["micro_check"]["group"]),
    }
    max_diff = 0.0
    for k, (a, b) in checks.items():
        d = abs(a - b)
        max_diff = max(max_diff, d)
        log(f"  reproduce TDE vs none {k}: mine {a:.10f} stored {b:.10f} diff {d:.2e}")
        assert d < TOL, (k, a, b)
    log(f"TDE vs none reproduced: max abs difference {max_diff:.2e} (tolerance {TOL:g}); {rep_secs:.1f} s")

    results = {}
    for new, old in COMPARISONS:
        t1 = time.perf_counter()
        r = rep if (new, old) == ("TDE", "none") else estimate(new, old, H, ctx)
        r["runtime_seconds"] = time.perf_counter() - t1
        results[f"{new} vs {old}"] = r
        log(f"{new} vs {old}: total {r['total']:+.5f} group {r['group']:+.5f} "
            f"case {r['case']:+.5f} [{r['case_ci'][0]:+.5f}, {r['case_ci'][1]:+.5f}] "
            f"share {r['share']:.3f} [{r['share_ci'][0]:.3f}, {r['share_ci'][1]:.3f}]  "
            f"({r['runtime_seconds']:.0f} s)")

    out = {
        "estimator": "run_sgg_image_weighted.py permutation estimator at gc@50, imported unchanged: "
                     f"{RIW.N_PERM} uniform within-cell label permutations (seeds 1..{RIW.N_PERM}); "
                     f"case interval delete-a-group jackknife over images ({RIW.N_JACK} groups, "
                     f"{RIW.N_PERM_JACK} permutations per replicate); 95% z-intervals",
        "group_and_share_intervals": "z-intervals with the jackknife SE of the group part and of group/total",
        "tde_vs_none_reproduction": {"max_abs_difference": float(max_diff), "tolerance": TOL,
                                     "checks": {k: {"mine": float(a), "stored": float(b)} for k, (a, b) in checks.items()}},
        "n_relations": int(len(y)), "n_eligible": int(eligible.sum()), "n_images": ctx["n_img"],
        "comparisons": results,
        "runtime_seconds": time.perf_counter() - t_all,
    }
    OUT.write_text(json.dumps(out, indent=1))
    log(f"wrote {OUT.relative_to(ROOT)} in {out['runtime_seconds'] / 60:.1f} min")


if __name__ == "__main__":
    main()
