"""How far the scene-graph audit's case-level verdicts depend on how they are measured.

Three questions, one results file (results/sgg_rank_robustness.json):

1. AUC weighting. The within-cell AUC averages cell-and-label-pair AUCs with weight
   n_c(y) n_c(z) ("comparison"), which weights a cell by about n_c^2; the case-level
   part weights it by n_c ("relation": n_c(y) n_c(z) / n_c). Both weightings, on all
   identified relations and on the audit half the matched split uses, for the SGG
   comparisons and the real-pixel study (seed 0).
2. Where TDE's discrimination moved. The comparison-weighted AUC change restricted to
   label pairs by predicate tier (head > 10,000 training instances, tail < 500), with
   each tier pair's share of the weight.
3. Recalibration family. The matched split of each SGG comparison under (a) one
   temperature per model, (b) one temperature shared by both models, (c) temperature
   plus a per-class bias per model. Every family preserves each model's within-cell
   ranking, so none can change the AUC; (c) also absorbs any global log-prior shift,
   so the logit-adjusted control becomes the baseline exactly.

Run: python experiments/run_sgg_rank_robustness.py
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
from wager.rank import _auc, _blocks, within_cell_auc_contrast  # noqa: E402
from sgg_variants import load_variant  # noqa: E402
import run_sgg_audit_wager as AU  # noqa: E402

OUT = ROOT / "results/sgg_rank_robustness.json"
DDIR = ROOT / "data/vg_motifs/wager_sgg"
N_BOOT = 200
EPS = 1e-12
HEAD_MIN, TAIL_MAX = 10_000, 500


def sgg_data():
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    y = meta["pred"].astype(np.int64)[keep] - 1
    phi = (meta["subj"].astype(np.int64) * 151 + meta["obj"].astype(np.int64))[keep]
    image = meta["image_index"].astype(np.int64)[keep]

    raw = {v: load_variant(v)["probs"][keep][:, 1:].astype(np.float64)
           for v in ("none", "TDE", "la1", "ietrans")}
    Q = {v: p / p.sum(1, keepdims=True) for v, p in raw.items()}
    rng = np.random.default_rng(20260811)                 # the audit's calibration split
    imgs = np.unique(image)
    cal = np.isin(image, imgs[rng.permutation(len(imgs))[: len(imgs) // 2]])
    return Q, raw, y, phi, image, cal


def auc_rows(Q, pairs, y, phi, image, aud):
    rows = []
    for new, old in pairs:
        row = {"new": new, "old": old}
        for sample, m in (("all", np.ones(len(y), bool)), ("audit half", aud)):
            for wt in ("comparison", "relation"):
                a = within_cell_auc_contrast(Q[new][m], Q[old][m], y[m], phi[m], image[m],
                                             n_boot=N_BOOT, weighting=wt)
                row[f"{sample}, {wt}"] = {"auc_new": a.auc_new, "auc_old": a.auc_old,
                                          "difference": a.difference, "ci": list(a.ci)}
        rows.append(row)
        print(f"AUC {new} vs {old}: " + "  ".join(
            f"{k} {row[k]['difference']:+.4f} [{row[k]['ci'][0]:+.4f},{row[k]['ci'][1]:+.4f}]"
            for k in row if isinstance(row[k], dict)), flush=True)
    return rows


def tier_pair_auc(Q, new, old, y, phi, image, tier_of):
    """Comparison-weighted AUC change within each predicate-tier pair, image bootstrap."""
    bn = _blocks(np.log(np.maximum(Q[new], EPS)), y, phi)
    bo = _blocks(np.log(np.maximum(Q[old], EPS)), y, phi)
    # tier pair of each block, from the labels of its positive and negative elements
    def block_tiers(bl):
        ylab = y[bl.elem]
        pos_lab = np.zeros(bl.n_blocks, dtype=np.int64)
        neg_lab = np.zeros(bl.n_blocks, dtype=np.int64)
        pos_lab[bl.block[bl.pos]] = ylab[bl.pos]
        neg_lab[bl.block[~bl.pos]] = ylab[~bl.pos]
        a, b = tier_of[pos_lab], tier_of[neg_lab]
        return np.where(a <= b, a * 3 + b, b * 3 + a)
    tp = block_tiers(bn)
    assert np.array_equal(tp, block_tiers(bo))

    def per_block(bl, w):
        we = w[bl.elem]
        wn = np.where(bl.pos, 0.0, we)
        wp = np.where(bl.pos, we, 0.0)
        cum = np.cumsum(wn)
        tie_neg = np.bincount(bl.tie, wn)
        tie_end = np.cumsum(np.bincount(bl.tie))
        below_tie = cum[tie_end - 1] - tie_neg
        blk_start = np.r_[0, np.flatnonzero(np.diff(bl.block)) + 1]
        below = below_tie[bl.tie] - np.r_[0.0, cum][blk_start][bl.block]
        num = np.bincount(bl.block, wp * (below + 0.5 * tie_neg[bl.tie]), bl.n_blocks)
        den = np.bincount(bl.block, wp, bl.n_blocks) * np.bincount(bl.block, wn, bl.n_blocks)
        return num, den

    def stats(w):
        nn, dn = per_block(bn, w)
        no, _ = per_block(bo, w)
        out = {}
        for g in np.unique(tp):
            m = tp == g
            out[int(g)] = ((nn[m].sum() - no[m].sum()) / dn[m].sum(), dn[m].sum())
        rest = tp != 0
        out["non head-head"] = ((nn[rest].sum() - no[rest].sum()) / dn[rest].sum(), dn[rest].sum())
        return out
    one = np.ones(len(y))
    point = stats(one)
    _, ginv = np.unique(image, return_inverse=True)
    n_g = ginv.max() + 1
    rng = np.random.default_rng(0)
    draws = [stats(rng.multinomial(n_g, np.full(n_g, 1 / n_g)).astype(float)[ginv])
             for _ in range(N_BOOT)]
    names = {0: "head-head", 1: "head-body", 2: "head-tail", 4: "body-body", 5: "body-tail",
             8: "tail-tail", "non head-head": "all but head-head"}
    total_w = sum(v[1] for k, v in point.items() if k != "non head-head")
    res = {}
    for k, (d, wsum) in point.items():
        ds = [x[k][0] for x in draws if k in x]
        res[names[k]] = {"difference": float(d), "weight_share": float(wsum / total_w),
                         "ci": list(np.percentile(ds, [2.5, 97.5]))}
    print(f"tier pairs {new} vs {old}: " + "  ".join(
        f"{k} {v['difference']:+.4f} [{v['ci'][0]:+.4f},{v['ci'][1]:+.4f}] w={v['weight_share']:.3f}"
        for k, v in res.items()), flush=True)
    return res


def fit_family(logq, y, bias):
    k = logq.shape[1]

    def f(p):
        a = np.exp(p[0])
        z = a * logq + (p[1:] if bias else 0.0)
        z = z - z.max(1, keepdims=True)
        lse = np.log(np.exp(z).sum(1))
        nll = np.mean(lse - z[np.arange(len(y)), y])
        g = np.exp(z - lse[:, None])
        g[np.arange(len(y)), y] -= 1
        g /= len(y)
        grad = [np.sum(g * logq) * a] + (list(g.sum(0)) if bias else [])
        return nll, np.array(grad)
    return minimize(f, np.zeros(1 + (k if bias else 0)), jac=True, method="L-BFGS-B").x


def apply_family(logq, p, bias):
    z = np.exp(p[0]) * logq + (p[1:] if bias else 0.0)
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def fit_common(qa, qb, y):
    grid = np.geomspace(0.05, 20.0, 240)
    nll = [float(-np.mean(np.log(np.clip(AU.temp_scale(qa, t)[np.arange(len(y)), y], EPS, None)))
                 - np.mean(np.log(np.clip(AU.temp_scale(qb, t)[np.arange(len(y)), y], EPS, None))))
           for t in grid]
    return float(grid[int(np.argmin(nll))])


def recalibration_rows(Q, y, phi, image, cal):
    aud = ~cal
    L = {v: np.log(np.clip(q, EPS, None)) for v, q in Q.items()}
    fams = {}
    for v in Q:
        T = AU.fit_temperature(Q[v][cal], y[cal])
        fams.setdefault("temperature", {})[v] = AU.temp_scale(Q[v], T)[aud]
        p = fit_family(L[v][cal], y[cal], bias=True)
        fams.setdefault("temperature + class bias", {})[v] = apply_family(L[v], p, True)[aud]
    rows = []
    for new in ("TDE", "la1", "ietrans"):
        tc = fit_common(Q[new][cal], Q["none"][cal], y[cal])
        fams.setdefault("shared temperature", {})[new] = (AU.temp_scale(Q[new], tc)[aud],
                                                         AU.temp_scale(Q["none"], tc)[aud])
        row = {"new": new, "old": "none"}
        for fam in ("temperature", "shared temperature", "temperature + class bias"):
            if fam == "shared temperature":
                qn, qo = fams[fam][new]
            else:
                qn, qo = fams[fam][new], fams[fam]["none"]
            for sc in ("brier", "log"):
                with np.errstate(all="ignore"):
                    g = decompose_gain(qn, qo, y[aud], phi[aud], groups=image[aud], score=sc)
                row[f"{fam}, {sc}"] = {"total": g.total_gain, "group": g.prior_gain,
                                       "case": g.alignment_gain, "case_ci": list(g.alignment_ci)}
        rows.append(row)
        print(f"recal {new}: " + "  ".join(
            f"{k} {row[k]['case']:+.5f} [{row[k]['case_ci'][0]:+.5f},{row[k]['case_ci'][1]:+.5f}]"
            for k in row if isinstance(row[k], dict)), flush=True)
    return rows


def pixel_data():
    vis = np.load(ROOT / "data/vg_visual/vg_visual_models.npz")
    y, phi, image = vis["y"].astype(np.int64), vis["phi"].astype(np.int64), vis["image"]
    Q = {k: vis[k].astype(np.float64) / vis[k].sum(1, keepdims=True)
         for k in ("MLP-CLASS-S", "MLP-SPATIAL-S", "MLP-VISUAL-S")}
    g = np.random.default_rng(20260810)                   # Sec. 6's calibration split
    imgs = np.unique(image)
    cal = np.isin(image, imgs[g.permutation(len(imgs))[: len(imgs) // 2]])
    return Q, y, phi, image, cal


def main():
    out = {"n_boot": N_BOOT}
    Q, raw, y, phi, image, cal = sgg_data()
    # AUCs from the stored (unrenormalised) probabilities, as run_sgg_rank_contrast.py
    out["sgg_auc"] = auc_rows(raw, [("TDE", "none"), ("la1", "none"), ("ietrans", "none")],
                              y, phi, image, ~cal)
    counts = np.asarray(json.loads((DDIR / "summary.json").read_text())["train_predicate_counts"])[1:]
    tier_of = np.where(counts > HEAD_MIN, 0, np.where(counts < TAIL_MAX, 2, 1))
    out["tier_sizes"] = {"head": int((tier_of == 0).sum()), "body": int((tier_of == 1).sum()),
                         "tail": int((tier_of == 2).sum())}
    out["tier_pair_auc"] = {f"{n} vs none": tier_pair_auc(raw, n, "none", y, phi, image, tier_of)
                            for n in ("TDE", "la1", "ietrans")}
    out["recalibration"] = recalibration_rows(Q, y, phi, image, cal)
    OUT.write_text(json.dumps(out, indent=1))
    P, py, pphi, pimage, pcal = pixel_data()
    out["pixel_auc"] = auc_rows(P, [("MLP-VISUAL-S", "MLP-SPATIAL-S"),
                                    ("MLP-SPATIAL-S", "MLP-CLASS-S"),
                                    ("MLP-VISUAL-S", "MLP-CLASS-S")], py, pphi, pimage, ~pcal)
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
