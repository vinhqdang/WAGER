"""Does label ambiguity (synonyms, generic vs specific predicates) move the within-cell AUC?

The within-cell AUC scores each relation against single Visual Genome labels, so a model
that prefers a specific predicate ("sitting on") to the labelled generic one ("on") is
penalised. Three questions, one results file (results/sgg_auc_label_ambiguity.json):

1. Merged labels. Each merge scheme of run_predicate_merge.py (imported, not redefined)
   is applied: probabilities are summed within merged groups and labels are mapped to
   the merged class. The within-cell AUC change for TDE, la1 and IETrans against the
   baseline is reported under the relation, comparison and pair weightings, with 95%
   image-bootstrap intervals and the baseline's AUC level on the same merged labels.
   The unmerged reference is the scheme with no groups; it must equal
   results/sgg_auc_label_weighting.json.
2. Within-group vs across-group label pairs. Using the finest scheme's groups, a label
   pair (y, z) is within-group when both labels fall in the same merged group and
   across-group otherwise. The unmerged comparison-weighted AUC change is split by pair
   type from the per-block numerator and denominator sums (as tier_pair_auc does for tier
   pairs), with each type's share of the comparison weight and the baseline's AUC level
   within that type. Image bootstrap, seed 0.
3. A compact log and the list of merge groups used.

AUC eps is 1e-300 throughout (wager.rank.AUC_EPS).

Run:  python experiments/sgg_auc_label_ambiguity.py
      WAGER_N_BOOT=20 python experiments/sgg_auc_label_ambiguity.py   (quick check)
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.rank import AUC_EPS, _blocks, _logq, within_cell_auc_contrast  # noqa: E402
import run_sgg_rank_robustness as RR  # noqa: E402
import run_predicate_merge as PM  # noqa: E402
from sgg_auc_label_weighting import per_block  # noqa: E402

OUT = ROOT / "results/sgg_auc_label_ambiguity.json"
REF = ROOT / "results/sgg_auc_label_weighting.json"
N_BOOT = int(os.environ.get("WAGER_N_BOOT", "1000"))
SEED = 0
VARIANTS = ("TDE", "la1", "ietrans")
WEIGHTINGS = ("relation", "comparison", "pair")
SCHEMES = {"synonym": PM.SYNONYM, "coarse": PM.COARSE}
NONE = {}                                    # the unmerged reference (identity map)


def float_dict(d):
    return {k: float(v) for k, v in d.items()}


def block_labels(bl, y):
    """Positive and negative label (0-based) of every block."""
    ylab = y[bl.elem]
    pos = np.zeros(bl.n_blocks, dtype=np.int64)
    neg = np.zeros(bl.n_blocks, dtype=np.int64)
    pos[bl.block[bl.pos]] = ylab[bl.pos]
    neg[bl.block[~bl.pos]] = ylab[~bl.pos]
    return pos, neg


def main():
    t0 = time.time()
    print(f"N_BOOT={N_BOOT} seed={SEED}", flush=True)
    _, raw, y, phi, image, _ = RR.sgg_data()
    n = len(y)
    y51 = y + 1                                       # 1..50, as in run_predicate_merge
    raw51 = {v: np.column_stack([np.zeros(n), raw[v]]) for v in ("none",) + VARIANTS}
    print(f"relations {n}, cells {int(np.unique(phi).size)}, images {int(np.unique(image).size)}",
          flush=True)

    # merge schemes: the unmerged reference first, then the two imported schemes
    maps = {}
    for name, groups in [("none", NONE)] + list(SCHEMES.items()):
        m, k = PM.merge_map(groups)
        maps[name] = (m, k, groups)
        print(f"scheme {name:8s} classes {k}", flush=True)
    m_none, k_none, _ = maps["none"]
    assert np.array_equal(m_none[1:], np.arange(1, 51)), "unmerged map is not the identity"
    finest = max(SCHEMES, key=lambda s: maps[s][1])
    print(f"finest scheme for pair types: {finest} ({maps[finest][1]} classes)", flush=True)

    # 1. merged-label AUC contrasts
    ref = json.loads(REF.read_text())["auc"]
    unmerged_cmp = {}                                  # comparison-weighted contrast, per variant
    merged = {}
    max_dev = 0.0
    for name, (m, k, groups) in maps.items():
        ym = m[y51] - 1                                # merged labels, 0-based
        qn_all = {v: PM.merge_probs(raw51[v], m, k)[:, 1:] for v in raw51}
        block = merged.setdefault(name, {"n_classes": k, "comparisons": {}})
        for v in VARIANTS:
            key = f"{v} vs none"
            block["comparisons"][key] = {}
            for wt in WEIGHTINGS:
                c = within_cell_auc_contrast(qn_all[v], qn_all["none"], ym, phi, image,
                                             n_boot=N_BOOT, alpha=0.05, seed=SEED,
                                             eps=AUC_EPS, weighting=wt)
                row = {"auc_new": float(c.auc_new), "auc_old": float(c.auc_old),
                       "difference": float(c.difference), "ci95": [float(x) for x in c.ci]}
                if name == "none":
                    r = ref[key][wt]
                    dev = abs(row["difference"] - r["difference"]) + abs(row["auc_old"] - r["auc_old"])
                    dev_ci = max(abs(row["ci95"][0] - r["ci95"][0]), abs(row["ci95"][1] - r["ci95"][1]))
                    row["matches_sgg_auc_label_weighting"] = {
                        "point_abs_dev": float(dev), "ci95_abs_dev": float(dev_ci)}
                    max_dev = max(max_dev, dev)
                    if wt in ("relation", "comparison"):
                        assert dev < 1e-9, (key, wt, dev)
                    if N_BOOT == 1000:
                        assert dev_ci < 1e-9, (key, wt, dev_ci)
                block["comparisons"][key][wt] = row
                if name == "none" and wt == "comparison":
                    unmerged_cmp[v] = c
                tag = "match" if name == "none" else ""
                print(f"{name:8s} {key:12s} {wt:10s} d {c.difference:+.5f} "
                      f"[{c.ci[0]:+.5f},{c.ci[1]:+.5f}] base {c.auc_old:.4f} {tag}",
                      flush=True)
    print(f"unmerged reference matches results/sgg_auc_label_weighting.json "
          f"(max point deviation {max_dev:.2e})", flush=True)

    # 2. within-group vs across-group label pairs, unmerged labels, comparison weighting
    m_f, k_f, groups_f = maps[finest]
    group_of = m_f[1:]                                  # merged id of each 0-based label
    _, ginv = np.unique(image, return_inverse=True)
    n_g = ginv.max() + 1
    bn_blocks = _blocks(_logq(raw["none"], AUC_EPS), y, phi)
    pair_types = {}
    for v in VARIANTS:
        bn = _blocks(_logq(raw[v], AUC_EPS), y, phi)
        bo = bn_blocks
        assert np.array_equal(bn.blk_pair, bo.blk_pair)
        pos, neg = block_labels(bn, y)
        within = group_of[pos] == group_of[neg]
        types = {"within-group": within, "across-group": ~within}
        pl = np.minimum(pos, neg) * 50 + np.maximum(pos, neg)
        ones = np.ones(n)

        def stats(w):
            nn, dn = per_block(bn, w)
            no, _ = per_block(bo, w)
            return {t: (nn[msk].sum(), no[msk].sum(), dn[msk].sum()) for t, msk in types.items()}

        point = stats(ones)
        tot_d = sum(point[t][2] for t in types)
        tot_diff = (sum(point[t][0] for t in types) - sum(point[t][1] for t in types)) / tot_d
        assert abs(tot_diff - unmerged_cmp[v].difference) < 1e-9, (v, tot_diff)
        rng = np.random.default_rng(SEED)
        draws = {t: np.empty(N_BOOT) for t in types}
        for r in range(N_BOOT):
            w = rng.multinomial(n_g, np.full(n_g, 1.0 / n_g)).astype(float)[ginv]
            st = stats(w)
            for t in types:
                a, b, d = st[t]
                draws[t][r] = (a - b) / d if d > 0 else np.nan
        res = {}
        for t, msk in types.items():
            a, b, d = point[t]
            lo, hi = np.nanpercentile(draws[t], [2.5, 97.5])
            pairs = np.unique(pl[msk])
            res[t] = {"difference": float((a - b) / d), "ci95": [float(lo), float(hi)],
                      "auc_new": float(a / d), "auc_old": float(b / d),
                      "weight_share": float(d / tot_d),
                      "contribution_to_total": float((a - b) / tot_d),
                      "n_blocks": int(msk.sum()), "n_label_pairs": int(len(pairs))}
            print(f"pairs {v} vs none {t:13s} d {res[t]['difference']:+.5f} "
                  f"[{lo:+.5f},{hi:+.5f}] base {res[t]['auc_old']:.4f} "
                  f"share {res[t]['weight_share']:.4f} label pairs {len(pairs)}", flush=True)
        res["total"] = {"difference": float(tot_diff)}
        pair_types[f"{v} vs none"] = res

    out = {"n_boot": N_BOOT, "seed": SEED, "eps": AUC_EPS,
           "weightings": list(WEIGHTINGS), "variants": list(VARIANTS),
           "schemes": {name: {"n_classes": maps[name][1],
                              "groups": {g: list(ns) for g, ns in maps[name][2].items()}}
                       for name in maps},
           "finest_scheme": finest,
           "unmerged_reference_max_point_deviation": float(max_dev),
           "merged_auc": {k_: v_ for k_, v_ in merged.items() if k_ != "none"},
           "unmerged_auc": merged["none"]["comparisons"],
           "pair_type_auc": pair_types,
           "runtime_seconds": round(time.time() - t0, 1)}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
