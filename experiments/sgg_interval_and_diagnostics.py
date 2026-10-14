"""Interval check, coverage study and diagnostics for the mean-recall split.

Three parts, one results file (results/sgg_interval_and_diagnostics.json).

1. Headline interval check. Reproduces the TDE-vs-MOTIFS graph-constrained mR@50
   split (micro-pooled, class-pair cells) and asserts it against
   results/sgg_recall_split.json. The case-level part gets two standard errors: the
   default image-clustered Hajek influence-function SE, and a delete-a-group jackknife
   over images (images assigned to G groups by permutation(seed 0) % G, G = 100 and 50).

2. Coverage on VG150's own structure. The data-generating process is a cluster bootstrap
   of images from the real data (real y, phi, image and real TDE / MOTIFS hit matrices).
   Each replicate redraws the image multiset with replacement (a drawn image keeps its
   relations and is a new cluster), recomputes the split and its image-clustered interval.
   The truth is the full-sample split. 1,000 replicates, seed 0.

3. Diagnostics the split is compared against: change in micro-pooled mR@50 overall and by
   predicate tier, and change in zero-shot recall@50 (graph-constrained), for the
   comparisons TDE vs none, la1 vs none, TDE vs la1, ietrans vs none, dlfe vs dlfe_base.
   Zero-shot relations are test triplets (subject class, object class, predicate) absent
   from training, read from the Scene-Graph-Benchmark list zeroshot_triplet.pytorch. The
   file is a legacy torch pickle; it is decoded here without torch. Zero-shot recall is
   computed both micro-pooled over relations and as the official per-image average, and
   validated against the official values where they are printed.

Run: python experiments/sgg_interval_and_diagnostics.py
     (Part 2 takes about 40 minutes; run in the background and poll the log.)
Set WAGER_ZS_TRIPLETS to the path of zeroshot_triplet.pytorch if it is not at the default.
"""
from __future__ import annotations

import json
import os
import pathlib
import pickle
import re
import struct
import sys
import time
from statistics import NormalDist

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain_matrix  # noqa: E402
from sgg_variants import load_variant  # noqa: E402
from run_sgg_recall_split import DDIR, N_PRED, tiers  # noqa: E402

OUT = ROOT / "results/sgg_interval_and_diagnostics.json"
K_COL = N_PRED + 1          # columns = predicate index 0..50 (column 0 unused, as in the split)
KREC = 50                   # recall@50
ALPHA = 0.05
Z = NormalDist().inv_cdf(1 - ALPHA / 2)
N_REP = 1000
# Scene-Graph-Benchmark.pytorch's list (maskrcnn_benchmark/data/datasets/evaluation/vg/)
DEFAULT_ZS = ROOT / "data/vg_motifs/zeroshot_triplet.pytorch"
ZS_PATH = pathlib.Path(os.environ.get("WAGER_ZS_TRIPLETS", DEFAULT_ZS))


def log(msg):
    print(msg, flush=True)


def fl(x):
    return float(x)


# ----------------------------------------------------------------------------- data

def base_meta():
    meta = np.load(DDIR / "meta.npz")
    y = meta["pred"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    phi = meta["subj"].astype(np.int64) * 151 + meta["obj"].astype(np.int64)
    _, image_inv = np.unique(image, return_inverse=True)
    summary = json.loads((DDIR / "summary.json").read_text())
    return y, image, phi, image_inv.reshape(-1), summary


def hits(variant):
    """Boolean recall@50 hit of every relation for every label (graph-constrained)."""
    return load_variant(variant)["gc_rank"] < KREC


# ----------------------------------------------------------------------------- split

def mr_split(hn, ho, y, phi, cluster):
    """Mean-recall split of the micro-pooled hit change over the rows given.

    Same construction as run_sgg_recall_split.split: eligible relations are those whose
    class-pair cell has at least two relations within the rows given, weights are
    1 / (50 n_y) over eligible relations, and the contrast is scored with
    decompose_gain_matrix (score="hit", image-clustered Hajek intervals).
    """
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    elig = cnt[inv.reshape(-1)] >= 2
    n_e = int(elig.sum())
    n_y = np.bincount(y[elig], minlength=K_COL).astype(float)
    w = np.zeros(K_COL)
    w[1:] = np.where(n_y[1:] > 0, 1.0 / (N_PRED * np.maximum(n_y[1:], 1)), 0.0)
    h = n_e * w[None, :] * (hn.astype(float) - ho.astype(float))
    return decompose_gain_matrix(h, y, phi, groups=cluster, alpha=ALPHA, score="hit")


def half_width_se(ci):
    return (ci[1] - ci[0]) / (2 * Z)


# ----------------------------------------------------------------------------- part 1

def part1(hT, hN, y, phi, image, image_inv, n_img):
    t0 = time.perf_counter()
    ref = json.loads((ROOT / "results/sgg_recall_split.json").read_text())["results"]["gc@50"]["mean_recall"]
    g = mr_split(hT, hN, y, phi, image)
    got = {"total": g.total_gain, "group": g.prior_gain, "case": g.alignment_gain}
    for k in got:
        assert abs(got[k] - ref[k]) < 1e-6, (k, got[k], ref[k])
    assert all(abs(a - b) < 1e-6 for a, b in zip(g.alignment_ci, ref["case_ci"]))
    assert round(g.total_gain, 5) == 0.09715 and round(g.prior_gain, 5) == 0.08411
    assert round(g.alignment_gain, 5) == 0.01305
    log(f"headline reproduced: total {g.total_gain:+.5f} group {g.prior_gain:+.5f} "
        f"case {g.alignment_gain:+.5f} CI [{g.alignment_ci[0]:+.5f}, {g.alignment_ci[1]:+.5f}]")

    case = fl(g.alignment_gain)
    se_h = half_width_se(g.alignment_ci)
    out = {
        "headline": {"total": fl(g.total_gain), "group": fl(g.prior_gain), "case": case,
                     "case_ci_hajek": [fl(v) for v in g.alignment_ci],
                     "matches_results_file": ref["case_ci"]},
        "case_se_hajek": fl(se_h),
        "case_ci_hajek": [fl(v) for v in g.alignment_ci],
        "jackknife": {},
    }
    for G in (100, 50):
        grp_img = np.random.default_rng(0).permutation(n_img) % G
        grp = grp_img[image_inv]
        thetas = np.empty(G)
        for gi in range(G):
            keep = grp != gi
            thetas[gi] = mr_split(hT[keep], hN[keep], y[keep], phi[keep], image[keep]).alignment_gain
        tbar = thetas.mean()
        se_j = float(np.sqrt((G - 1) / G * np.sum((thetas - tbar) ** 2)))
        out["jackknife"][f"G{G}"] = {
            "groups": G, "se": se_j, "ci": [case - Z * se_j, case + Z * se_j],
            "ratio_to_hajek_se": se_j / se_h, "mean_leave_group_out": fl(tbar),
            "min_leave_group_out": fl(thetas.min()), "max_leave_group_out": fl(thetas.max()),
        }
        log(f"jackknife G={G}: SE {se_j:.6f}  ratio to Hajek {se_j / se_h:.4f}  "
            f"CI [{case - Z * se_j:+.5f}, {case + Z * se_j:+.5f}]")
    log(f"hajek SE {se_h:.6f}  CI [{g.alignment_ci[0]:+.5f}, {g.alignment_ci[1]:+.5f}]")
    out["runtime_seconds"] = time.perf_counter() - t0
    return out


# ----------------------------------------------------------------------------- part 2

def part2(hT, hN, y, phi, image, image_inv, n_img):
    t0 = time.perf_counter()
    truth_g = mr_split(hT, hN, y, phi, image)
    truth_case = fl(truth_g.alignment_gain)
    truth_share = fl(truth_g.reasoning_share)
    truth_gshare = fl(truth_g.prior_gain / truth_g.total_gain)
    log(f"part2 truth: case {truth_case:+.6f} case share {truth_share:.5f} group share {truth_gshare:.5f}")

    order = np.argsort(image_inv, kind="stable")
    sizes = np.bincount(image_inv, minlength=n_img)
    starts = np.concatenate([[0], np.cumsum(sizes)[:-1]])
    rng = np.random.default_rng(0)
    case_est, case_se, case_cov = [], [], []
    share_est, share_se, share_cov = [], [], []
    gshare_cov, n_rows, n_unique = [], [], []
    tot_est = []
    for r in range(N_REP):
        draws = rng.integers(0, n_img, size=n_img)
        dsz = sizes[draws]
        dstart = starts[draws]
        tot = int(dsz.sum())
        cum = np.concatenate([[0], np.cumsum(dsz)[:-1]])
        rows = order[np.repeat(dstart - cum, dsz) + np.arange(tot)]
        clus = np.repeat(np.arange(n_img), dsz)
        g = mr_split(hT[rows], hN[rows], y[rows], phi[rows], clus)
        c = fl(g.alignment_gain)
        s = half_width_se(g.alignment_ci)
        case_est.append(c)
        case_se.append(s)
        case_cov.append(g.alignment_ci[0] <= truth_case <= g.alignment_ci[1])
        sh_ci = g.share_ci
        share_est.append(fl(g.reasoning_share))
        share_se.append(half_width_se(sh_ci))
        share_cov.append(sh_ci[0] <= truth_share <= sh_ci[1])
        # group share = 1 - case share, so its interval is the reflection of the case-share interval
        gshare_cov.append(1 - sh_ci[1] <= truth_gshare <= 1 - sh_ci[0])
        tot_est.append(fl(g.total_gain))
        n_rows.append(tot)
        n_unique.append(len(np.unique(draws)))
        if (r + 1) % 50 == 0:
            el = time.perf_counter() - t0
            log(f"  rep {r + 1}/{N_REP}: case coverage {np.mean(case_cov):.3f}  "
                f"share coverage {np.mean(share_cov):.3f}  elapsed {el / 60:.1f} min")
    case_est, case_se = np.asarray(case_est), np.asarray(case_se)
    share_est, share_se = np.asarray(share_est), np.asarray(share_se)
    cc, sc = np.asarray(case_cov, float), np.asarray(share_cov, float)
    res = {
        "n_replicates": N_REP, "seed": 0,
        "dgp": "cluster bootstrap of images from the real data (real y, phi, image, TDE and MOTIFS hit matrices)",
        "truth": {"case": truth_case, "case_share": truth_share, "group_share": truth_gshare,
                  "total": fl(truth_g.total_gain)},
        "case": {"coverage": float(cc.mean()),
                 "coverage_mc_se": float(np.sqrt(cc.mean() * (1 - cc.mean()) / N_REP)),
                 "mean_estimate": float(case_est.mean()), "bias_vs_truth": float(case_est.mean() - truth_case),
                 "mean_se": float(case_se.mean()), "sd_estimates": float(case_est.std(ddof=1)),
                 "mean_se_over_sd": float(case_se.mean() / case_est.std(ddof=1))},
        "case_share": {"coverage": float(sc.mean()), "mean_estimate": float(share_est.mean()),
                       "bias_vs_truth": float(share_est.mean() - truth_share),
                       "mean_se": float(share_se.mean()), "sd_estimates": float(share_est.std(ddof=1)),
                       "mean_se_over_sd": float(share_se.mean() / share_est.std(ddof=1))},
        "group_share": {"coverage": float(np.mean(gshare_cov)),
                        "note": "group share = 1 - case share; the interval is the reflection of the case-share interval"},
        "total": {"mean_estimate": float(np.mean(tot_est)), "bias_vs_truth": float(np.mean(tot_est) - truth_g.total_gain)},
        "mean_rows_per_replicate": float(np.mean(n_rows)),
        "mean_unique_images_fraction": float(np.mean(n_unique) / n_img),
    }
    res["runtime_seconds"] = time.perf_counter() - t0
    log(f"part2 done: case coverage {res['case']['coverage']:.3f}  mean SE {res['case']['mean_se']:.6f}  "
        f"SD {res['case']['sd_estimates']:.6f}  share coverage {res['case_share']['coverage']:.3f}  "
        f"runtime {res['runtime_seconds'] / 60:.1f} min")
    return res


# ----------------------------------------------------------------------------- part 3

def read_legacy_torch(path):
    """Read a legacy (pre-zipfile) torch.save file of a single tensor, without torch."""
    DT = {"LongStorage": np.int64, "IntStorage": np.int32, "FloatStorage": np.float32,
          "ByteStorage": np.uint8, "DoubleStorage": np.float64}

    class Tensor:
        def __init__(self, storage, offset, size, stride):
            self.storage, self.offset, self.size, self.stride = storage, offset, size, stride

    class U(pickle.Unpickler):
        def __init__(self, f):
            super().__init__(f)
            self.store = {}

        def find_class(self, module, name):
            if module == "torch._utils" and name == "_rebuild_tensor_v2":
                return lambda st, off, size, stride, *rest: Tensor(st, off, tuple(size), tuple(stride))
            if module == "torch" and name in DT:
                return name
            return super().find_class(module, name)

        def persistent_load(self, pid):
            assert pid[0] == "storage", pid
            d = {"dtype": DT[pid[1]], "key": str(pid[2]), "numel": int(pid[4])}
            self.store[d["key"]] = d
            return d

    with open(path, "rb") as f:
        u = U(f)
        assert u.load() == 0x1950A86A20F9469CFC6C
        u.load()
        u.load()
        obj = u.load()
        keys = u.load()
        blobs = {}
        for k in keys:
            numel = struct.unpack("<q", f.read(8))[0]
            d = u.store[str(k)]
            assert numel == d["numel"]
            blobs[str(k)] = np.frombuffer(f.read(numel * np.dtype(d["dtype"]).itemsize),
                                          dtype=d["dtype"]).copy()
    flat = blobs[obj.storage["key"]]
    idx = np.zeros(obj.size, dtype=np.int64) + obj.offset
    for ax, (n, s) in enumerate(zip(obj.size, obj.stride)):
        shape = [1] * len(obj.size)
        shape[ax] = n
        idx = idx + (np.arange(n) * s).reshape(shape)
    return flat[idx]


def zero_shot_mask(subj, obj, pred):
    """Relations whose (subject, object, predicate) triplet is in the benchmark's zero-shot list."""
    trip = read_legacy_torch(ZS_PATH)                  # (subject, object, predicate), 1-indexed
    code = lambda a, b, p: (a * 151 + b) * 51 + p
    is_zs = np.isin(code(subj, obj, pred), code(trip[:, 0], trip[:, 1], trip[:, 2]))
    return is_zs, trip


def zr_stats(hit, is_zs, image):
    idx = np.flatnonzero(is_zs)
    h = hit[idx].astype(float)
    _, inv = np.unique(image[idx], return_inverse=True)
    inv = inv.reshape(-1)
    per_image = np.bincount(inv, h) / np.bincount(inv)
    return {"micro": float(h.mean()), "per_image": float(per_image.mean()),
            "n_relations": int(len(idx)), "n_images": int(len(per_image))}


def mr_eligible(hit, y, elig):
    return np.array([hit[elig & (y == k), k].mean() for k in range(1, K_COL)])


def official_zr50():
    """Official zR@50 values: full precision where stored, otherwise the printed 4-decimal value."""
    off = {}
    audit = json.loads((ROOT / "results/sgg_audit_motifs.json").read_text())["recalls"]
    off["none"] = {"value": audit["MOTIFS"]["predcls_zeroshot_recall@50"],
                   "source": "results/sgg_audit_motifs.json recalls.MOTIFS predcls_zeroshot_recall@50",
                   "precision": "full"}
    off["TDE"] = {"value": audit["MOTIFS-TDE"]["predcls_zeroshot_recall@50"],
                  "source": "results/sgg_audit_motifs.json recalls.MOTIFS-TDE predcls_zeroshot_recall@50",
                  "precision": "full"}
    dl = json.loads((ROOT / "results/dlfe_official_recall.json").read_text())["models"]
    for key in ("dlfe", "dlfe_base"):
        line = [ln for ln in dl[key]["printed_lines"] if re.search(r"(?<![\w-])zR @ 50: ", ln)]
        val = float(re.search(r"(?<![\w-])zR @ 50: ([0-9.]+)", line[0]).group(1))
        off[key] = {"value": val, "source": f"results/dlfe_official_recall.json models.{key} printed line",
                    "precision": "printed (4 decimals)"}
    return off


def part3_run(y, image, phi, subj, obj, pred_summary):
    t0 = time.perf_counter()
    is_zs, trip = zero_shot_mask(subj, obj, y)
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    elig = cnt[inv.reshape(-1)] >= 2
    tier_arr = tiers(pred_summary["train_predicate_counts"])
    tier_sizes = {t: int(sum(tier_arr[q] == t for q in range(1, K_COL))) for t in ("head", "body", "tail")}
    official = official_zr50()

    variants = ["none", "TDE", "la1", "ietrans", "dlfe", "dlfe_base"]
    H = {}
    zr = {}
    mr = {}
    for v in variants:
        H[v] = hits(v)
        zr[v] = zr_stats(H[v][np.arange(len(y)), y], is_zs, image)
        mr[v] = mr_eligible(H[v], y, elig)
        log(f"  {v}: micro mR@50 (eligible) {mr[v].mean():.5f}  zR@50 micro {zr[v]['micro']:.5f} "
            f"per-image {zr[v]['per_image']:.5f}")

    validation = {}
    for v, o in official.items():
        rep = zr[v]["per_image"]
        if o["precision"] == "full":
            ok = abs(rep - o["value"]) < 1e-9
            tol = 1e-9
        else:
            ok = abs(rep - o["value"]) < 5e-5
            tol = 5e-5
        validation[v] = {"replayed_per_image": rep, "official": o["value"], "source": o["source"],
                         "tolerance": tol, "matches": bool(ok),
                         "abs_diff": abs(rep - o["value"])}
        log(f"  validate zR@50 {v}: replay {rep:.6f} official {o['value']:.6f} "
            f"{'OK' if ok else 'MISMATCH'}")

    pairs = [("TDE", "none"), ("la1", "none"), ("TDE", "la1"), ("ietrans", "none"), ("dlfe", "dlfe_base")]
    existing = {("TDE", "none"): "sgg_recall_split.json", ("la1", "none"): "sgg_recall_split_la1_vs_none.json",
                ("TDE", "la1"): "sgg_recall_split_TDE_vs_la1.json",
                ("ietrans", "none"): "sgg_recall_split_ietrans_vs_none.json",
                ("dlfe", "dlfe_base"): "sgg_recall_split_dlfe_vs_dlfe_base.json"}
    comps = {}
    for new, old in pairs:
        diff = mr[new] - mr[old]
        overall = float(diff.mean())
        tier_stats = {}
        for t in ("head", "body", "tail"):
            ks = [q for q in range(1, K_COL) if tier_arr[q] == t]
            d = np.array([diff[q - 1] for q in ks])
            tier_stats[t] = {"n_predicates": len(ks), "mean_change_within_tier": float(d.mean()),
                             "contribution_to_overall": float(d.sum() / N_PRED)}
        ref_path = ROOT / "results" / existing[(new, old)]
        ref = json.loads(ref_path.read_text())["results"]["gc@50"]
        assert abs(overall - ref["mean_recall"]["total"]) < 1e-9, (new, old, overall, ref["mean_recall"]["total"])
        for t in ("head", "body", "tail"):
            assert abs(tier_stats[t]["contribution_to_overall"] - ref[f"mean_recall_{t}"]["total"]) < 1e-9
        comps[f"{new} vs {old}"] = {
            "mR50_change_overall": overall,
            "mR50_change_by_tier": tier_stats,
            "zR50_change_per_image": zr[new]["per_image"] - zr[old]["per_image"],
            "zR50_change_micro": zr[new]["micro"] - zr[old]["micro"],
            "zR50_new_per_image": zr[new]["per_image"], "zR50_old_per_image": zr[old]["per_image"],
            "zR50_new_micro": zr[new]["micro"], "zR50_old_micro": zr[old]["micro"],
            "matches_existing_split_file": existing[(new, old)],
        }
        log(f"  {new} vs {old}: mR@50 {overall:+.5f}  zR@50 per-image "
            f"{comps[f'{new} vs {old}']['zR50_change_per_image']:+.5f}  "
            f"head {tier_stats['head']['mean_change_within_tier']:+.4f} "
            f"body {tier_stats['body']['mean_change_within_tier']:+.4f} "
            f"tail {tier_stats['tail']['mean_change_within_tier']:+.4f}")
    return {
        "zero_shot_triplets": int(len(trip)), "zero_shot_relations": zr["none"]["n_relations"],
        "zero_shot_images": zr["none"]["n_images"],
        "tier_sizes_predicates": tier_sizes,
        "zR50_replay": zr,
        "zR50_validation": validation,
        "comparisons": comps,
        "notes": "mR change is micro-pooled over eligible relations (cells with >= 2 relations), as the split. "
                 "Tier 'mean_change_within_tier' averages the per-predicate change over the tier's predicates; "
                 "'contribution_to_overall' is the tier's share of the 50-predicate average and sums to the overall change.",
        "runtime_seconds": time.perf_counter() - t0,
    }


# ----------------------------------------------------------------------------- main

def main():
    t_all = time.perf_counter()
    y, image, phi, image_inv, summary = base_meta()
    meta = np.load(DDIR / "meta.npz")
    subj = meta["subj"].astype(np.int64)
    obj = meta["obj"].astype(np.int64)
    pred = y
    n_img = int(image_inv.max()) + 1
    results = {"n_relations": int(len(y)), "n_images": n_img}

    hT, hN = hits("TDE"), hits("none")
    log("part 1: headline interval check")
    results["part1_headline_interval"] = part1(hT, hN, y, phi, image, image_inv, n_img)
    OUT.write_text(json.dumps(results, indent=1))

    log("part 2: coverage on VG150's structure (1,000 bootstrap replicates)")
    results["part2_coverage"] = part2(hT, hN, y, phi, image, image_inv, n_img)
    OUT.write_text(json.dumps(results, indent=1))

    log("part 3: diagnostics and zero-shot recall")
    results["part3_diagnostics"] = part3_run(y, image, phi, subj, obj, summary)
    results["runtime_seconds_total"] = time.perf_counter() - t_all
    OUT.write_text(json.dumps(results, indent=1))
    log(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
