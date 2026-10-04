"""Put the IETrans rerun on the standard PredCls test relations.

IETrans's data loader removes exact duplicate relations -- the same subject
object, object object and predicate annotated twice -- from the test set as
well as the training set (visual_genome.py, get_groundtruth: `if True:` keyed on
(o0, o1, r)), where the codebase it forks keeps them at test time. Its official
numbers are therefore on 152,226 test relations, not the standard 183,642.

An exact duplicate has the same pair and the same label as the relation that was
kept, so the evaluator would match it at exactly the same ranks and the model
scores it with exactly the same probabilities. This script maps every standard
relation (data/vg_motifs/wager_sgg/meta.npz) to the IETrans row with the same
image, boxes, classes and predicate, checks that the mapping is total and that
any key shared by several IETrans rows carries identical ranks and
probabilities, and writes data/vg_motifs/wager_ietrans/ aligned with the
reference run. It also reports IETrans's official-protocol mean recall on both
test sets, so the published figure and the standard-protocol one sit side by
side.

Run: python experiments/expand_ietrans_to_standard.py
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
import run_sgg_recall_split as RS  # noqa: E402

REF = ROOT / "data/vg_motifs/wager_sgg"
RAW = ROOT / "data/vg_motifs/wager_ietrans_raw"
OUT = ROOT / "data/vg_motifs/wager_ietrans"
VARIANTS = ("ietrans", "ietrans_ctx")


def keys(m):
    return [(int(i), *map(float, sb), *map(float, ob), int(s), int(o), int(p))
            for i, sb, ob, s, o, p in zip(m["image_index"], m["sbox"], m["obox"],
                                          m["subj"], m["obj"], m["pred"])]


def main():
    ref, raw = np.load(REF / "meta.npz"), np.load(RAW / "meta.npz")
    rk, wk = keys(ref), keys(raw)
    first = {}
    groups = {}
    for j, k in enumerate(wk):
        first.setdefault(k, j)
        groups.setdefault(k, []).append(j)
    missing = [i for i, k in enumerate(rk) if k not in first]
    if missing:
        raise SystemExit(f"{len(missing)} standard relations have no IETrans row, e.g. {missing[:5]}")
    idx = np.asarray([first[k] for k in rk])
    unused = set(range(len(wk))) - set(idx.tolist())
    shared = [g for g in groups.values() if len(g) > 1]

    Z = {v: np.load(RAW / f"variant_{v}.npz") for v in VARIANTS}
    # rows sharing a key must be interchangeable
    worst_prob, rank_mismatch = 0.0, 0
    for g in shared:
        for v in VARIANTS:
            for k in ("gc_rank", "ng_rank"):
                rank_mismatch += int(any(not np.array_equal(Z[v][k][g[0]], Z[v][k][j])
                                         for j in g[1:]))
            worst_prob = max(worst_prob, max(float(np.abs(Z[v]["probs"][g[0]]
                                                          - Z[v]["probs"][j]).max())
                                             for j in g[1:]))
    report = {"standard_relations": len(rk), "ietrans_relations": len(wk),
              "unused_ietrans_rows": len(unused), "keys_with_several_ietrans_rows": len(shared),
              "rank_mismatch_within_shared_keys": rank_mismatch,
              "max_prob_difference_within_shared_keys": worst_prob,
              "duplicates_restored": int(len(rk) - len(set(rk)))}
    print(report)
    if unused or rank_mismatch:
        raise SystemExit("mapping is not clean")

    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy(REF / "meta.npz", OUT / "meta.npz")
    shutil.copy(REF / "missing_pairs.json", OUT / "missing_pairs.json")
    for v in VARIANTS:
        np.savez_compressed(OUT / f"variant_{v}.npz", probs=Z[v]["probs"][idx],
                            gc_rank=Z[v]["gc_rank"][idx], ng_rank=Z[v]["ng_rank"][idx])

    # official-protocol mean recall on both test sets (per image, then predicate)
    off = {}
    for name, meta, rows in (("ietrans_dedup_test", raw, np.arange(len(wk))),
                             ("standard_test", ref, idx)):
        y = meta["pred"].astype(np.int64)
        img = meta["image_index"].astype(np.int64)
        for v in VARIANTS:
            for mode, tag in (("gc_rank", "mR"), ("ng_rank", "ng-mR")):
                own = Z[v][mode][rows][np.arange(len(y)), y]
                for K in (20, 50, 100):
                    off[f"{name} {v} {tag}@{K}"] = RS.official_mean_recall(own < K, y, img)[0]
                own = Z[v]["gc_rank"][rows][np.arange(len(y)), y]
            off[f"{name} {v} R@50"] = float(np.mean(
                np.bincount(np.unique(img, return_inverse=True)[1], own < 50)
                / np.bincount(np.unique(img, return_inverse=True)[1])))
    raw_summary = json.loads((RAW / "summary.json").read_text())
    report["official_protocol"] = off
    report["rescored_on_ietrans_test"] = raw_summary["recalls"]
    report["official_ietrans_run"] = raw_summary.get("official_ietrans_this_run", {})
    for k in ("mR@50", "ng-mR@50", "R@50"):
        print(f"IETrans {k}: dedup test {off[f'ietrans_dedup_test ietrans {k}']:.4f}  "
              f"standard test {off[f'standard_test ietrans {k}']:.4f}")
    assert abs(off["ietrans_dedup_test ietrans mR@50"]
               - raw_summary["recalls"]["ietrans"]["mR@50"]) < 1e-12
    (OUT / "summary.json").write_text(json.dumps(
        {**report, "train_predicate_counts": json.loads(
            (REF / "summary.json").read_text())["train_predicate_counts"]}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
