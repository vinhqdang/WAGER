"""Image-weighted sensitivity of the mean-recall split.

The micro-pooled split in run_sgg_recall_split.py weights relation i by
1 / (K n_y), where n_y counts eligible relations with label y. The official
statistic averages per image first: for predicate q, recall_q is the mean over
images g containing q of (hits of q in g) / (count of q in g), and mR is the
mean over predicates. Written per relation, the official change over eligible
relations is

    sum_i Delta_i / (K G_y c_{g(i),y}),   y = y_i,

where G_y is the number of images with at least one eligible relation labelled
y and c_{g,y} is the number of eligible relations labelled y in image g.

Three estimates of the group / case split are stored per comparison and K:

* "image-weighted floor" (top-level keys): w_img(i,y) for every label column,
  with c floored at 1 for counterfactual labels, split with
  decompose_gain_matrix(groups=image, score="hit"). Its total equals the
  official change over eligible relations exactly; the script asserts this.
* "fixed_case_weight": w_i = 1 / (K G_{y_i} c_{g(i),y_i}) taken from relation
  i's own label for every column, split the same way.
* "permutation": the group part is the expected official change when labels
  are permuted uniformly within each eligible cell (200 seeds). The case part
  is total minus group. The case interval is a delete-a-group jackknife over
  images (50 groups; each replicate uses 50 permutations and the same seeds).
  The same permutation estimate is computed for the micro-pooled statistic and
  compared with the analytic micro split as a sanity check.

Run: python experiments/run_sgg_image_weighted.py
"""
from __future__ import annotations

import json
import pathlib
import sys
from statistics import NormalDist

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain_matrix  # noqa: E402
from run_sgg_recall_split import (  # noqa: E402
    ALPHA, DDIR, N_OBJ, N_PRED, RESULTS, load, official_mean_recall,
)

KS = (20, 50, 100)
MODELS = ("TDE", "la1", "none")
COMPARISONS = (("TDE", "none"), ("la1", "none"), ("TDE", "la1"))
TOL = 1e-9
N_PERM = 200
N_JACK = 50
N_PERM_JACK = 50
K_LAB = N_PRED + 1


# ---------------------------------------------------------------- image-weighted

def image_weights(y, image, eligible):
    """w[i, y] = 1 / (K G_y c_{g(i), y}) for every label column y.

    Column 0 and labels with G_y = 0 are zero; those columns never enter the
    within-cell transport because no eligible relation carries them.
    """
    _, img = np.unique(image, return_inverse=True)
    img = img.reshape(-1).astype(np.int64)
    n_img = int(img.max()) + 1
    counts = np.bincount(img[eligible] * K_LAB + y[eligible],
                         minlength=n_img * K_LAB).reshape(n_img, K_LAB).astype(np.float64)
    g_y = (counts > 0).sum(axis=0).astype(np.float64)              # G_y
    c = np.maximum(counts[img], 1.0)                               # c_{g(i), y}, floored at 1
    present = g_y > 0
    w = np.zeros((len(y), K_LAB), dtype=np.float64)
    w[:, present] = 1.0 / (N_PRED * g_y[present][None, :] * c[:, present])
    return w


def image_split(hit_new, hit_old, y, phi, image, eligible):
    n_e = int(eligible.sum())
    w = image_weights(y, image, eligible)
    h = n_e * w * (hit_new.astype(np.float64) - hit_old.astype(np.float64))
    return decompose_gain_matrix(h, y, phi, groups=image, alpha=ALPHA, score="hit")


def fixed_split(hit_new, hit_old, y, phi, image, eligible):
    """w_i from relation i's own label, applied to every column."""
    n_e = int(eligible.sum())
    _, img = np.unique(image, return_inverse=True)
    img = img.reshape(-1).astype(np.int64)
    n_img = int(img.max()) + 1
    counts = np.bincount(img[eligible] * K_LAB + y[eligible],
                         minlength=n_img * K_LAB).reshape(n_img, K_LAB).astype(np.float64)
    g_y = (counts > 0).sum(axis=0).astype(np.float64)
    ix = np.arange(len(y))
    c_own = np.maximum(counts[img, y], 1.0)
    gy_own = g_y[y]
    w_own = np.where(gy_own > 0, 1.0 / (N_PRED * np.maximum(gy_own, 1.0) * c_own), 0.0)
    h = n_e * w_own[:, None] * (hit_new.astype(np.float64) - hit_old.astype(np.float64))
    h[:, 0] = 0.0
    return decompose_gain_matrix(h, y, phi, groups=image, alpha=ALPHA, score="hit")


def official_change_eligible(hit_new, hit_old, y, image, eligible, ix):
    new = hit_new[ix, y][eligible]
    old = hit_old[ix, y][eligible]
    m_new = official_mean_recall(new, y[eligible], image[eligible])[0]
    m_old = official_mean_recall(old, y[eligible], image[eligible])[0]
    return m_new, m_old, m_new - m_old


def micro_reference(new, old, K):
    """Micro-pooled split already stored by run_sgg_recall_split, if present."""
    name = "sgg_recall_split.json" if (new, old) == ("TDE", "none") \
        else f"sgg_recall_split_{new}_vs_{old}.json"
    path = RESULTS / name
    if not path.exists():
        return None
    m = json.loads(path.read_text())["results"][f"gc@{K}"]["mean_recall"]
    return {"total": m["total"], "group": m["group"], "case": m["case"]}


# ------------------------------------------------------------ permutation helpers

def make_perms(y_sub, cell_sub, seeds):
    """Uniform random permutation of labels within each cell, one per seed."""
    s = np.argsort(cell_sub, kind="stable")
    cs = cell_sub[s]
    ys = y_sub[s]
    out = []
    for r in seeds:
        rnd = np.random.default_rng(r).random(len(s))
        o = np.lexsort((rnd, cs))            # shuffles inside each cell block only
        yp = np.empty_like(y_sub)
        yp[s] = ys[o]
        out.append(yp)
    return out


def prep(yp, img_sub):
    """Label-only quantities shared by every model evaluated at these labels."""
    key = img_sub * K_LAB + yp
    ukey, kinv, kcnt = np.unique(key, return_inverse=True, return_counts=True)
    kinv = kinv.reshape(-1)
    return {
        "y": yp,
        "a": 1.0 / kcnt[kinv],                                   # 1 / cn_{g(i), y_i}
        "gq": np.bincount(ukey % K_LAB, minlength=K_LAB).astype(np.float64),  # G_q
        "cnt": np.bincount(yp, minlength=K_LAB).astype(np.float64),
    }


def eval_off(p, hv):
    """Official per-image mean recall at the labels in p (hv: hits at those labels)."""
    s = np.bincount(p["y"], weights=hv * p["a"], minlength=K_LAB)
    return float(np.mean(s[1:] / np.maximum(p["gq"][1:], 1.0)))


def eval_mic(p, hv):
    """Micro-pooled mean recall at the labels in p."""
    s = np.bincount(p["y"], weights=hv, minlength=K_LAB)
    return float(np.mean(s[1:] / np.maximum(p["cnt"][1:], 1.0)))


def z_interval(est, se):
    z = NormalDist().inv_cdf(1.0 - ALPHA / 2.0)
    return [float(est - z * se), float(est + z * se)]


def main():
    meta = np.load(DDIR / "meta.npz")
    y = meta["pred"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    phi = meta["subj"].astype(np.int64) * N_OBJ + meta["obj"].astype(np.int64)
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1).astype(np.int64)
    eligible = cnt[inv] >= 2
    n_e = int(eligible.sum())
    ix = np.arange(len(y))

    image_compact = np.unique(image, return_inverse=True)[1].reshape(-1).astype(np.int64)
    elig_idx = np.flatnonzero(eligible)
    y_e = y[elig_idx]
    cell_e = inv[elig_idx]
    img_e = image_compact[elig_idx]

    models = {m: load(m) for m in MODELS}
    H = {(m, K): models[m]["gc"] < K for m in MODELS for K in KS}
    del models

    out = {
        "definition": "w_img(i,y) = 1/(K G_y c_{g(i),y}); K = N_PRED; G_y = images with an "
                      "eligible relation labelled y; c floored at 1; h = N_elig w_img "
                      "(hit_new - hit_old); split by decompose_gain_matrix(groups=image, "
                      "score='hit'). fixed_case_weight uses w_i from the own label for all "
                      "columns. permutation: uniform within-cell label permutations "
                      f"(seeds 1..{N_PERM}); case CI = delete-a-group jackknife over images "
                      f"({N_JACK} groups, {N_PERM_JACK} permutations per replicate).",
        "n_relations": int(len(y)),
        "n_eligible": n_e,
        "n_images": int(len(np.unique(image))),
        "n_images_eligible": int(len(np.unique(image[eligible]))),
        "comparisons": {},
    }
    rows = []
    base = {}
    for new, old in COMPARISONS:
        for K in KS:
            hn, ho = H[(new, K)], H[(old, K)]
            g = image_split(hn, ho, y, phi, image, eligible)
            m_new, m_old, official = official_change_eligible(hn, ho, y, image, eligible, ix)
            gap = g.total_gain - official
            if abs(gap) > TOL:
                raise AssertionError(
                    f"{new} vs {old} gc@{K}: estimator total {g.total_gain!r} "
                    f"!= official change {official!r} (gap {gap:.3e})")
            row = {
                "total": float(g.total_gain),
                "group": float(g.prior_gain),
                "case": float(g.alignment_gain),
                "case_ci": [float(v) for v in g.alignment_ci],
                "group_ci": [float(v) for v in g.prior_ci],
                "total_ci": [float(v) for v in g.total_ci],
                "share": float(g.prior_gain / g.total_gain),
                "official_new": float(m_new),
                "official_old": float(m_old),
                "official_change": float(official),
                "identity_gap": float(gap),
            }
            ref = micro_reference(new, old, K)
            if ref is not None:
                row["micro_reference"] = ref

            f = fixed_split(hn, ho, y, phi, image, eligible)
            fgap = f.total_gain - official
            if abs(fgap) > TOL:
                raise AssertionError(f"fixed weight {new} vs {old} gc@{K}: gap {fgap:.3e}")
            row["fixed_case_weight"] = {
                "total": float(f.total_gain),
                "group": float(f.prior_gain),
                "case": float(f.alignment_gain),
                "case_ci": [float(v) for v in f.alignment_ci],
                "group_ci": [float(v) for v in f.prior_ci],
                "share": float(f.prior_gain / f.total_gain),
                "identity_gap": float(fgap),
            }
            base[(new, old, K)] = row
            out["comparisons"].setdefault(f"{new} vs {old}", {})[f"gc@{K}"] = row

    # Observed labels: check the vectorized official formula against the reference.
    for new, old in COMPARISONS:
        for K in KS:
            p0 = prep(y_e, img_e)
            hv_n = H[(new, K)][elig_idx, y_e].astype(np.float64)
            hv_o = H[(old, K)][elig_idx, y_e].astype(np.float64)
            obs_off = eval_off(p0, hv_n) - eval_off(p0, hv_o)
            ref_off = base[(new, old, K)]["official_change"]
            if abs(obs_off - ref_off) > TOL:
                raise AssertionError(f"vectorized official mismatch {new} vs {old} gc@{K}")
            obs_mic = eval_mic(p0, hv_n) - eval_mic(p0, hv_o)
            ref_mic = micro_reference(new, old, K)
            if ref_mic is not None and abs(obs_mic - ref_mic["total"]) > TOL:
                raise AssertionError(f"micro total mismatch {new} vs {old} gc@{K}")
            base[(new, old, K)]["_obs_mic"] = obs_mic

    # Full-sample permutations: group = mean over permutations of the change.
    keys = [(new, old, K) for new, old in COMPARISONS for K in KS]
    acc_off = {k: np.empty(N_PERM) for k in keys}
    acc_mic = {k: np.empty(N_PERM) for k in keys}
    perms = make_perms(y_e, cell_e, range(1, N_PERM + 1))
    for r, yp in enumerate(perms):
        p = prep(yp, img_e)
        for new, old, K in keys:
            hv_n = H[(new, K)][elig_idx, yp].astype(np.float64)
            hv_o = H[(old, K)][elig_idx, yp].astype(np.float64)
            acc_off[(new, old, K)][r] = eval_off(p, hv_n) - eval_off(p, hv_o)
            acc_mic[(new, old, K)][r] = eval_mic(p, hv_n) - eval_mic(p, hv_o)
    print("full-sample permutations done", flush=True)

    # Delete-a-group jackknife over images.
    grp_img = np.random.default_rng(0).permutation(int(image_compact.max()) + 1) % N_JACK
    grp_e = grp_img[img_e]
    th_case = {k: np.empty(N_JACK) for k in keys}
    th_group = {k: np.empty(N_JACK) for k in keys}
    th_case_mic = {k: np.empty(N_JACK) for k in keys}
    th_group_mic = {k: np.empty(N_JACK) for k in keys}
    for gidx in range(N_JACK):
        keep = grp_e != gidx
        sub = elig_idx[keep]
        ys, cs, ims = y_e[keep], cell_e[keep], img_e[keep]
        p0 = prep(ys, ims)
        gsum = {k: 0.0 for k in keys}
        gsum_m = {k: 0.0 for k in keys}
        tot = {}
        tot_m = {}
        for new, old, K in keys:
            hv_n = H[(new, K)][sub, ys].astype(np.float64)
            hv_o = H[(old, K)][sub, ys].astype(np.float64)
            tot[(new, old, K)] = eval_off(p0, hv_n) - eval_off(p0, hv_o)
            tot_m[(new, old, K)] = eval_mic(p0, hv_n) - eval_mic(p0, hv_o)
        for yp in make_perms(ys, cs, range(1, N_PERM_JACK + 1)):
            p = prep(yp, ims)
            for new, old, K in keys:
                hv_n = H[(new, K)][sub, yp].astype(np.float64)
                hv_o = H[(old, K)][sub, yp].astype(np.float64)
                gsum[(new, old, K)] += eval_off(p, hv_n) - eval_off(p, hv_o)
                gsum_m[(new, old, K)] += eval_mic(p, hv_n) - eval_mic(p, hv_o)
        for k in keys:
            th_group[k][gidx] = gsum[k] / N_PERM_JACK
            th_case[k][gidx] = tot[k] - gsum[k] / N_PERM_JACK
            th_group_mic[k][gidx] = gsum_m[k] / N_PERM_JACK
            th_case_mic[k][gidx] = tot_m[k] - gsum_m[k] / N_PERM_JACK
    print("jackknife done", flush=True)

    def jk_se(theta):
        return float(np.sqrt((N_JACK - 1.0) / N_JACK * np.sum((theta - theta.mean()) ** 2)))

    for new, old, K in keys:
        b = base[(new, old, K)]
        obs_mic = b.pop("_obs_mic")
        ao = acc_off[(new, old, K)]
        am = acc_mic[(new, old, K)]
        total = b["official_change"]
        group = float(ao.mean())
        group_se = float(ao.std(ddof=1) / np.sqrt(N_PERM))
        case = total - group
        case_se = jk_se(th_case[(new, old, K)])
        mic_group = float(am.mean())
        mic_group_se = float(am.std(ddof=1) / np.sqrt(N_PERM))
        an = micro_reference(new, old, K)
        gap_g = mic_group - an["group"]
        gap_c = (obs_mic - mic_group) - an["case"]
        b["permutation"] = {
            "total": total,
            "group": group,
            "group_mc_se": group_se,
            "group_perm_sd": float(ao.std(ddof=1)),
            "group_jk_se": jk_se(th_group[(new, old, K)]),
            "case": case,
            "case_ci": z_interval(case, case_se),
            "case_jk_se": case_se,
            "share": group / total,
            "n_perm": N_PERM,
            "n_jack_groups": N_JACK,
            "n_perm_per_jack": N_PERM_JACK,
            "micro_check": {
                "total": obs_mic,
                "group": mic_group,
                "group_mc_se": mic_group_se,
                "case": obs_mic - mic_group,
                "case_jk_se": jk_se(th_case_mic[(new, old, K)]),
                "analytic_group": an["group"],
                "analytic_case": an["case"],
                "gap_group": gap_g,
                "gap_group_in_mc_se": gap_g / mic_group_se if mic_group_se > 0 else float("nan"),
                "gap_case": gap_c,
            },
        }
        rows.append((new, old, K, b))
        out["comparisons"][f"{new} vs {old}"][f"gc@{K}"] = b

    print("\nImage-weighted floor (top) | fixed own-label weight | permutation  "
          "[total = official change, eligible relations]")
    hdr = (f"{'comparison':<13}{'K':>5}{'total':>9}  {'floor group':>11}{'floor case':>11}"
           f"{'share':>7}  {'fixed group':>11}{'fixed case':>11}{'fixed share':>12}  "
           f"{'perm group':>11}{'+-mc':>8}{'perm case':>10}{'jk 95% CI':>22}{'perm share':>11}")
    print(hdr)
    for new, old, K, r in rows:
        p = r["permutation"]
        f = r["fixed_case_weight"]
        ci = f"[{p['case_ci'][0]:+.4f}, {p['case_ci'][1]:+.4f}]"
        print(f"{new + ' vs ' + old:<13}{'gc@' + str(K):>5}{r['total']:+9.4f}  "
              f"{r['group']:+11.4f}{r['case']:+11.4f}{r['share']:7.0%}  "
              f"{f['group']:+11.4f}{f['case']:+11.4f}{f['share']:12.0%}  "
              f"{p['group']:+11.4f}{p['group_mc_se']:8.4f}{p['case']:+10.4f}{ci:>22}"
              f"{p['share']:11.0%}")
    print("\nMicro-pooled sanity check (permutation estimate vs analytic micro split):")
    print(f"{'comparison':<13}{'K':>5}{'mc group':>11}{'+-mc':>8}{'analytic':>11}"
          f"{'gap':>10}{'gap/mc':>9}{'mc case':>10}{'analytic':>10}")
    for new, old, K, r in rows:
        m = r["permutation"]["micro_check"]
        print(f"{new + ' vs ' + old:<13}{'gc@' + str(K):>5}{m['group']:+11.4f}"
              f"{m['group_mc_se']:8.4f}{m['analytic_group']:+11.4f}{m['gap_group']:+10.4f}"
              f"{m['gap_group_in_mc_se']:+9.2f}{m['case']:+10.4f}{m['analytic_case']:+10.4f}")

    dest = RESULTS / "sgg_image_weighted.json"
    dest.write_text(json.dumps(out, indent=1))
    print(f"wrote {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
