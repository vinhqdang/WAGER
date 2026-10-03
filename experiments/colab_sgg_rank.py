"""Offline re-scoring of the branch dump with the official PredCls recall rules.

Input (on the Colab VM, written by colab_sgg_stage2.py):
  /content/branch_dump/chunk_*.npz     per-pair vis, ctx(post), ctx(avg), frq and
                                       the returned (TDE) logits, all test images
  <out dir>/inference/<test>/eval_results.pytorch   official evaluation of the run
(WAGER_RANK_MODE=tde: TDE pass of the causal MOTIFS checkpoint; =ietrans: IETrans)

For every variant (baseline, TDE, single branches, branch pairs) and every
ground-truth relation r = (s, o, y) this records, for each of the 50 predicates
y', the position at which the official evaluator would first match the triplet
(s, o, y'):
  gc_rank[r, y']  graph constraint: best rank, among predicted pairs matching
                  (s, o) (same classes, both boxes IoU >= 0.5), of a pair whose
                  top non-background predicate is y'; pairs ordered by the
                  post-processor's triple score
  ng_rank[r, y']  no graph constraint: best position of (pair, y') in the
                  evaluator's argsort of all pair-predicate scores
so a relation is a recall@K hit under label y' iff rank < K. Ranks are clipped
to 255 (only K <= 100 is used). This makes recall, and mean recall, exact
functions of the label assignment, which is what the label-transport split of
mean recall needs.

Checks written to the summary: the dumped pair set equals the evaluated pair
set; softmax(returned logits) equals the stored TDE scores; the returned logits
equal (vis + ctx(post) + frq) - (vis + ctx(avg) + frq); and the re-scored
R@K / mR@K / ng-mR@K reproduce the official numbers for TDE (this run) and for
the baseline (archived run).
"""
import glob
import json
import os
import sys
import time

import numpy as np

ROOT = "/content"
MODE = os.environ.get("WAGER_RANK_MODE", "tde")
MODES = {
    # released causal MOTIFS checkpoint, one TDE pass (colab_sgg_stage2.py)
    "tde": {
        "code": f"{ROOT}/sgg",
        "eval": f"{ROOT}/out_tde/inference/VG_stanford_filtered_with_attribute_test",
        "dump": f"{ROOT}/branch_dump", "out": f"{ROOT}/wager_sgg",
        "keys": ("pairs", "vis", "ctxp", "ctxa", "frq", "out"),
        "official": "TDE",
        # the returned logits must equal this (the TDE cancellation)
        "identity": lambda b: ((b["vis"] + b["ctxp"]) + b["frq"])
        - ((b["vis"] + b["ctxa"]) + b["frq"]),
        "la_base": lambda b: (b["vis"] + b["ctxp"]) + b["frq"],
        "h5": "datasets/vg/VG-SGG-with-attri.h5",
        "variants": {
            "none": lambda b: (b["vis"] + b["ctxp"]) + b["frq"],
            "TDE": lambda b: b["out"],
            "vis": lambda b: b["vis"],
            "ctx": lambda b: b["ctxp"],
            "frq": lambda b: b["frq"],
            "vis_ctx": lambda b: b["vis"] + b["ctxp"],
            "ctx_frq": lambda b: b["ctxp"] + b["frq"],
            "vis_frq": lambda b: b["vis"] + b["frq"],
        },
    },
    # released IETrans Neural-Motifs PredCls checkpoint (colab_ietrans_stage2.py)
    "ietrans": {
        "code": f"{ROOT}/iet",
        "eval": f"{ROOT}/out_ietrans/inference/50VG_stanford_filtered_with_attribute_test",
        "dump": f"{ROOT}/branch_dump_ietrans", "out": f"{ROOT}/wager_ietrans",
        "keys": ("pairs", "ctx", "frq", "out"),
        "official": "ietrans",
        "identity": lambda b: b["ctx"] + b["frq"],
        "la_base": None,
        "h5": "datasets/vg/50/VG-SGG-with-attri.h5",
        "variants": {
            "ietrans": lambda b: b["out"],
            "ietrans_ctx": lambda b: b["ctx"],
        },
    },
}
CFG = MODES[MODE]
SGG = CFG["code"]
sys.path.insert(0, f"{ROOT}/pylib")
sys.path.insert(0, SGG)

EVAL, DUMP, OUT = CFG["eval"], CFG["dump"], CFG["out"]
OFFICIAL = CFG["official"]
KS = (20, 50, 100)
BIG = 255
T0 = time.time()
VARIANTS = dict(CFG["variants"])


def train_predicate_counts():
    """Training-split predicate counts (index 0 is background, always 0)."""
    import h5py
    with h5py.File(f"{SGG}/{CFG['h5']}", "r") as f5:
        split = f5["split"][:]
        first, last = f5["img_to_first_rel"][:], f5["img_to_last_rel"][:]
        preds_all = f5["predicates"][:, 0]
    cnt = np.zeros(51, dtype=np.int64)
    for i in np.flatnonzero((split == 0) & (first >= 0)):
        np.add.at(cnt, preds_all[first[i]:last[i] + 1], 1)
    return cnt


def add_logit_adjusted(cnt, taus=(0.5, 1.0)):
    """Post-hoc logit adjustment of the baseline by the training predicate prior."""
    if CFG["la_base"] is None:
        return
    lp = np.zeros(51, dtype=np.float32)
    lp[1:] = np.log(cnt[1:] / cnt[1:].sum()).astype(np.float32)
    for t in taus:
        VARIANTS[f"la{t:g}"] = (lambda b, t=t: CFG["la_base"](b) - np.float32(t) * lp)


def log(m):
    print(f"[rank +{time.time()-T0:.0f}s] {m}", flush=True)


def softmax(x):
    import torch
    return torch.softmax(torch.from_numpy(np.ascontiguousarray(x)), -1).numpy()


def ranks_for_variant(prob, order):
    """Pair rank and per-(pair, predicate) no-graph-constraint rank."""
    m = prob.shape[0]
    pair_rank = np.empty(m, dtype=np.int64)
    pair_rank[order] = np.arange(m)
    sp = prob[order][:, 1:]
    # identical call to the evaluator's argsort_desc on the sorted score matrix
    flat = np.argsort(-sp.ravel())
    pos = np.empty(flat.size, dtype=np.int64)
    pos[flat] = np.arange(flat.size)
    ng_sorted = pos.reshape(sp.shape)            # rows in sorted-pair order
    ng = np.full((m, 51), 1 << 40, dtype=np.int64)
    ng[:, 1:] = ng_sorted[pair_rank]
    top = 1 + prob[:, 1:].argmax(1)
    return pair_rank, ng, top


def match_candidates(rel, labels, iou, pairs, n_obj):
    """Indices of predicted pairs the evaluator would match to each GT relation."""
    mobj = (labels[:, None] == labels[None, :]) & (iou >= 0.5)
    lut = np.full((n_obj, n_obj), -1, dtype=np.int64)
    lut[pairs[:, 0], pairs[:, 1]] = np.arange(len(pairs))
    cands = []
    for s, o, _y in rel:
        cc = lut[np.ix_(np.where(mobj[s])[0], np.where(mobj[o])[0])].ravel()
        cands.append(cc[cc >= 0])
    return cands, lut


def relation_ranks(prob, order, cands):
    """(n_rel, 51) graph-constrained and no-graph-constraint first-hit ranks."""
    pair_rank, ngr, top = ranks_for_variant(prob, order)
    g_out = np.full((len(cands), 51), BIG, dtype=np.int64)
    n_out = np.full((len(cands), 51), BIG, dtype=np.int64)
    for r, cc in enumerate(cands):
        if len(cc) == 0:
            continue
        np.minimum.at(g_out[r], top[cc], pair_rank[cc])
        n_out[r] = np.minimum(n_out[r], ngr[cc].min(0))
    return (np.minimum(g_out, BIG).astype(np.uint8),
            np.minimum(n_out, BIG).astype(np.uint8))


def main():
    import torch
    from maskrcnn_benchmark.utils.miscellaneous import bbox_overlaps
    os.makedirs(OUT, exist_ok=True)
    cnt = train_predicate_counts()
    add_logit_adjusted(cnt)
    log(f"train predicate counts: {int(cnt.sum())} relations; variants {list(VARIANTS)}")
    log(f"loading {EVAL}/eval_results.pytorch")
    d = torch.load(f"{EVAL}/eval_results.pytorch", map_location="cpu",
                   weights_only=False)  # our own dump; holds BoxList objects
    gts, preds = d["groundtruths"], d["predictions"]
    n_img = len(gts)
    log(f"{n_img} images")

    rows = {k: [] for k in ("image_index", "sbox", "obox", "img_wh", "subj",
                            "obj", "pred")}
    probs = {v: [] for v in VARIANTS}
    gc = {v: [] for v in VARIANTS}
    ng = {v: [] for v in VARIANTS}
    chk = {"pairset_mismatch": 0, "official_score_maxdiff": 0.0,
           "identity_maxdiff": 0.0, "no_match": 0, "images_seen": 0,
           "rel_without_gt_pair": 0, "top100_ties": {v: 0 for v in VARIANTS},
           "order_mismatch_TDE": 0}
    seen = set()

    for cf in sorted(glob.glob(f"{DUMP}/chunk_*.npz")):
        if cf.endswith(".tmp.npz"):
            continue
        c = np.load(cf)
        offs = np.concatenate([[0], np.cumsum(c["n_pairs"])])
        if "frq_gap" in c.files:
            chk["frq_gap"] = max(chk.get("frq_gap", 0.0), float(c["frq_gap"]))
        arrs = {k: c[k] for k in CFG["keys"]}
        for j, img in enumerate(c["image_ids"]):
            img = int(img)
            if img in seen:
                continue
            seen.add(img)
            sl = slice(offs[j], offs[j + 1])
            b = {k: v[sl] for k, v in arrs.items()}
            gt, pr = gts[img], preds[img]
            rel = gt.get_field("relation_tuple").numpy().astype(np.int64)
            if len(rel) == 0:
                continue
            labels = gt.get_field("labels").numpy().astype(np.int64)
            boxes = gt.convert("xyxy").bbox.numpy()
            w, h = gt.size
            pairs = b["pairs"].astype(np.int64)
            n_obj = len(labels)

            # --- checks against the official dump
            off_pairs = pr.get_field("rel_pair_idxs").numpy().astype(np.int64)
            off_scores = pr.get_field("pred_rel_scores").numpy()
            key = pairs[:, 0] * n_obj + pairs[:, 1]
            okey = off_pairs[:, 0] * n_obj + off_pairs[:, 1]
            if len(key) != len(okey) or set(key.tolist()) != set(okey.tolist()):
                chk["pairset_mismatch"] += 1
                continue
            pos_of = {int(k): i for i, k in enumerate(key)}
            off_order = np.asarray([pos_of[int(k)] for k in okey])
            p_tde = softmax(b["out"])
            chk["official_score_maxdiff"] = max(
                chk["official_score_maxdiff"],
                float(np.abs(p_tde[off_order] - off_scores).max()))
            recon = CFG["identity"](b)
            chk["identity_maxdiff"] = max(
                chk["identity_maxdiff"], float(np.abs(recon - b["out"]).max()))

            # --- official matching structure (PredCls: predicted boxes and
            # classes are the ground-truth ones)
            iou = bbox_overlaps(boxes, boxes)
            cands, lut = match_candidates(rel, labels, iou, pairs, n_obj)
            p_off = np.empty_like(p_tde)
            p_off[off_order] = off_scores          # the evaluated TDE scores

            for v, f in VARIANTS.items():
                if v == OFFICIAL:
                    p, order = p_off, off_order     # the evaluated order
                else:
                    p = softmax(f(b))
                    ms = torch.from_numpy(p[:, 1:].max(1))
                    order = torch.sort(ms, descending=True)[1].numpy()
                    srt = p[order][:, 1:].max(1)[:101]
                    chk["top100_ties"][v] += int((np.diff(srt) == 0).sum())
                g_out, n_out = relation_ranks(p, order, cands)
                gc[v].append(g_out)
                ng[v].append(n_out)
                own = lut[rel[:, 0], rel[:, 1]]
                probs[v].append(p[np.maximum(own, 0)].astype(np.float32))

            own = lut[rel[:, 0], rel[:, 1]]
            chk["rel_without_gt_pair"] += int((own < 0).sum())
            chk["no_match"] += int(sum(len(cc) == 0 for cc in cands))
            rows["image_index"].append(np.full(len(rel), img, dtype=np.int32))
            rows["sbox"].append(boxes[rel[:, 0]].astype(np.float32))
            rows["obox"].append(boxes[rel[:, 1]].astype(np.float32))
            rows["img_wh"].append(np.tile(np.float32([w, h]), (len(rel), 1)))
            rows["subj"].append(labels[rel[:, 0]].astype(np.int32))
            rows["obj"].append(labels[rel[:, 1]].astype(np.int32))
            rows["pred"].append(rel[:, 2].astype(np.int32))
            gts[img] = None
            preds[img] = None
        chk["images_seen"] = len(seen)
        log(f"{os.path.basename(cf)}: {len(seen)} images, "
            f"{sum(len(x) for x in rows['pred'])} relations")

    meta = {k: np.concatenate(v) for k, v in rows.items()}
    np.savez_compressed(f"{OUT}/meta.npz", **meta)
    for v in VARIANTS:
        np.savez_compressed(f"{OUT}/variant_{v}.npz",
                            probs=np.concatenate(probs[v]),
                            gc_rank=np.concatenate(gc[v]),
                            ng_rank=np.concatenate(ng[v]))
    log(f"wrote {OUT}: {len(meta['pred'])} relations")

    # --- official-style recall from the ranks (per-image, then averaged)
    img, y = meta["image_index"], meta["pred"]
    summary = {"train_predicate_counts": cnt.tolist(), "checks": chk, "n_relations": int(len(y)),
               "n_images_with_relations": int(len(np.unique(img))),
               "recalls": {}}
    _, inv = np.unique(img, return_inverse=True)
    for v in VARIANTS:
        z = np.load(f"{OUT}/variant_{v}.npz")
        out = {}
        for tag, rk in (("", z["gc_rank"]), ("ng_", z["ng_rank"])):
            own = rk[np.arange(len(y)), y]
            for K in KS:
                hit = (own < K).astype(np.float64)
                per_img = np.bincount(inv, hit) / np.bincount(inv)
                out[f"{tag}R@{K}"] = float(per_img.mean())
                # mean recall: per image and predicate, then over images, then
                # over the 50 predicates (absent predicates count as zero)
                cell = inv * 51 + y
                ch = np.bincount(cell, hit, minlength=(inv.max() + 1) * 51)
                cn = np.bincount(cell, minlength=(inv.max() + 1) * 51)
                ch, cn = ch.reshape(-1, 51), cn.reshape(-1, 51)
                per = []
                for q in range(1, 51):
                    msk = cn[:, q] > 0
                    per.append(float((ch[msk, q] / cn[msk, q]).mean()) if msk.any() else 0.0)
                out[f"{tag}mR@{K}"] = float(np.mean(per))
        summary["recalls"][v] = out
        log(f"{v}: " + ", ".join(f"{k} {val:.4f}" for k, val in out.items()
                                  if k.endswith("@50")))
    rd = f"{EVAL}/result_dict.pytorch"
    if os.path.exists(rd):
        r = torch.load(rd, map_location="cpu", weights_only=False)
        summary[f"official_{OFFICIAL}_this_run"] = {
            f"{k}@{kk}": float(np.mean(vv)) for k, v in r.items()
            if isinstance(v, dict) and "recall" in k and "list" not in k
            and "collect" not in k
            for kk, vv in v.items() if not isinstance(vv, (dict, list)) or len(vv)}
    with open(f"{OUT}/summary.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    log("RANK COMPLETE")


if __name__ == "__main__":
    main()
