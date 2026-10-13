"""Put the DLFE rerun on the standard PredCls test relations.

colab_dlfe_stage2.py evaluates the released MOTIFS baseline and MOTIFS-DLFE
checkpoints (Chiou et al., ACM MM 2021) in their own fork of the Scene-Graph-
Benchmark codebase, and colab_sgg_rank.py (modes dlfe, dlfe_base) turns each
dump into per-relation probabilities and first-hit ranks, one raw directory per
model under data/vg_motifs/wager_dlfe_raw/. The fork keeps duplicate test
relations as the original codebase does, so both runs should list exactly the
183,642 relations of the reference run (data/vg_motifs/wager_sgg/meta.npz);
this script checks that, maps every reference relation to its row in each run
(a bijection also when a key repeats), and writes data/vg_motifs/wager_dlfe/
aligned with the reference run:

  meta.npz, missing_pairs.json      copied from the reference run
  variant_dlfe.npz                  MOTIFS-DLFE: the evaluator's score matrix,
                                    softmax / label frequency (unnormalised;
                                    column 0 is background)
  variant_dlfe_base.npz             the MOTIFS baseline of the same release
  variant_dlfe_soft.npz             the DLFE checkpoint's raw softmax, before
                                    the correction
  summary.json                      alignment report, official-protocol recalls
                                    replayed from the ranks, the evaluator's own
                                    numbers, train predicate counts

and results/dlfe_official_recall.json with the evaluator's printed and stored
values beside the replayed ones.

Run: python experiments/expand_dlfe_to_standard.py
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
RAW = ROOT / "data/vg_motifs/wager_dlfe_raw"
OUT = ROOT / "data/vg_motifs/wager_dlfe"
RUNS = {"dlfe": ("dlfe", "dlfe_soft"), "base": ("dlfe_base",)}
NAMES = {"dlfe": "MOTIFS-DLFE", "dlfe_base": "MOTIFS (DLFE release baseline)",
         "dlfe_soft": "MOTIFS-DLFE before the correction"}


def keys(m):
    return [(int(i), *map(float, sb), *map(float, ob), int(s), int(o), int(p))
            for i, sb, ob, s, o, p in zip(m["image_index"], m["sbox"], m["obox"],
                                          m["subj"], m["obj"], m["pred"])]


def bijection(rk, wk):
    """Index into wk for every element of rk; repeated keys are matched in order."""
    pos = {}
    for j, k in enumerate(wk):
        pos.setdefault(k, []).append(j)
    idx, missing = [], 0
    for k in rk:
        lst = pos.get(k)
        if not lst:
            missing += 1
            continue
        idx.append(lst.pop(0))
    leftover = sum(len(v) for v in pos.values())
    return np.asarray(idx), missing, leftover


def replay(meta, rows, z):
    """Official-protocol R@K, mR@K and their no-graph-constraint forms from ranks."""
    y = meta["pred"].astype(np.int64)[rows]
    img = meta["image_index"].astype(np.int64)[rows]
    _, inv = np.unique(img, return_inverse=True)
    out = {}
    for mode, tag in (("gc_rank", ""), ("ng_rank", "ng-")):
        own = z[mode][rows][np.arange(len(y)), y]
        for K in (20, 50, 100):
            hit = own < K
            out[f"{tag}R@{K}"] = float(np.mean(np.bincount(inv, hit) / np.bincount(inv)))
            out[f"{tag}mR@{K}"] = RS.official_mean_recall(hit, y, img)[0]
    return out


def main():
    ref = np.load(REF / "meta.npz")
    rk = keys(ref)
    ref_missing = json.loads((REF / "missing_pairs.json").read_text())
    report = {"standard_relations": len(rk), "runs": {}}
    aligned = {}
    for run, variants in RUNS.items():
        raw = np.load(RAW / run / "meta.npz")
        wk = keys(raw)
        identical = all(np.array_equal(ref[k], raw[k]) for k in
                        ("image_index", "pred", "subj", "obj", "sbox", "obox"))
        if identical:
            idx, missing, leftover = np.arange(len(rk)), 0, 0
        else:
            idx, missing, leftover = bijection(rk, wk)
        summ = json.loads((RAW / run / "summary.json").read_text())
        chk = summ["checks"]
        rep = {"relations": len(wk), "identical_to_reference": bool(identical),
               "unmatched_standard_relations": missing, "unused_rows": leftover,
               "checks": chk}
        print(run, rep)
        if missing or leftover:
            raise SystemExit(f"{run}: mapping is not a bijection")
        if chk["pairset_mismatch"] or chk["rel_without_gt_pair"] != len(ref_missing["rows"]):
            raise SystemExit(f"{run}: pair set differs from the reference run")
        if chk["official_score_maxdiff"] > 1e-5 or chk["identity_maxdiff"] > 1e-5:
            raise SystemExit(f"{run}: dump does not reproduce the evaluated scores")
        for v in variants:
            z = np.load(RAW / run / f"variant_{v}.npz")
            aligned[v] = {k: z[k][idx] for k in ("probs", "gc_rank", "ng_rank")}
            rep[f"replayed_{v}"] = replay(ref, np.arange(len(rk)), aligned[v])
            # the same ranks on the rerun's own order must give the rerun's summary
            for k in ("mR@50", "ng_mR@50", "R@50"):
                kk = k.replace("ng_", "ng-")
                assert abs(rep[f"replayed_{v}"][kk] - summ["recalls"][v][k]) < 1e-12, (v, k)
        rep["official_this_run"] = summ.get(f"official_{variants[0]}_this_run", {})
        off = RAW / run / f"official_{run}.json"
        rep["evaluator_printed"] = json.loads(off.read_text()) if off.exists() else {}
        report["runs"][run] = rep

    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy(REF / "meta.npz", OUT / "meta.npz")
    shutil.copy(REF / "missing_pairs.json", OUT / "missing_pairs.json")
    for v, z in aligned.items():
        np.savez_compressed(OUT / f"variant_{v}.npz", probs=z["probs"].astype(np.float32),
                            gc_rank=z["gc_rank"], ng_rank=z["ng_rank"])
    train_counts = json.loads((REF / "summary.json").read_text())["train_predicate_counts"]
    (OUT / "summary.json").write_text(json.dumps(
        {**report, "train_predicate_counts": train_counts}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")

    # evaluator values beside the replay, for the results directory
    res = {"source": "colab_dlfe_stage2.py official PredCls evaluation of the released "
                     "checkpoints (coldmanck/recovering-unbiased-scene-graphs), replayed "
                     "from the per-relation ranks of colab_sgg_rank.py",
           "models": {}}
    worst = 0.0
    for run, variants in RUNS.items():
        rep = report["runs"][run]
        v = variants[0]
        printed = rep["evaluator_printed"].get("values", {})
        stored = rep["official_this_run"]
        stored_map = {"R": "predcls_recall", "ng-R": "predcls_recall_nogc",
                      "mR": "predcls_mean_recall", "ng-mR": "predcls_ng_mean_recall"}
        rows = {}
        for k, val in rep[f"replayed_{v}"].items():
            tag, K = k.split("@")
            row = {"replayed": val}
            if k in printed:
                row["evaluator_printed"] = printed[k]
            sk = f"{stored_map[tag]}@{K}"
            if sk in stored:
                row["evaluator_stored"] = stored[sk]
                worst = max(worst, abs(stored[sk] - val))
            rows[k] = row
        res["models"][v] = {"name": NAMES[v], "checkpoint": rep["evaluator_printed"].get("checkpoint"),
                            "recalls": rows, "printed_lines": rep["evaluator_printed"].get("printed", [])}
        print(v + ": " + "  ".join(f"{k} {r['replayed']:.4f}"
                                   + (f" (official {r['evaluator_printed']:.4f})" if "evaluator_printed" in r else "")
                                   for k, r in rows.items() if k.endswith("@50")))
    res["max_abs_difference_replayed_vs_stored"] = worst
    dest = ROOT / "results/dlfe_official_recall.json"
    dest.write_text(json.dumps(res, indent=1))
    print(f"wrote {dest.relative_to(ROOT)}; max |replay - evaluator| = {worst:.2e}")


if __name__ == "__main__":
    main()
