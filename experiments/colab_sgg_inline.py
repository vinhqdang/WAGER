"""Inline evaluator replay for SGCls / SGDet (imported inside the inference loop).

In SGCls and SGDet a pass stores every object pair's logits for 51 predicates; for
SGDet that is up to 6,320 pairs per image, about 68 GB of branch logits over the
test set, and the codebase's own evaluator keeps every prediction in memory. So
instead of dumping logits (colab_sgg_stage2.py, PredCls), this module is called
once per test image inside compute_on_dataset and keeps only what the audit needs
for each ground-truth relation r = (s, o, y):

  gc_rank[r, y']  graph constraint: best position, in the post-processor's
                  triple-score order (predicate score x subject score x object
                  score), of a predicted pair that matches (s, o) -- same classes
                  as the ground truth and both boxes IoU >= 0.5 -- and whose top
                  non-background predicate is y'
  ng_rank[r, y']  no graph constraint: best position of (pair, y') in the
                  evaluator's argsort of object-score-weighted predicate scores
  probs[r]        the predicate distribution of the matched pair with the largest
                  summed IoU (a choice made from boxes and labels only, which the
                  baseline and TDE share), or NaN if no predicted pair matches

for three models computed from one TDE pass of the causal MOTIFS-SUM checkpoint:
  none   vis + ctx(post) + frq(predicted labels)      the baseline
  TDE    the returned logits (= ctx(post) - ctx(avg) under SUM fusion)
  la1    none - log training predicate prior          the operating-point control
The baseline and TDE share every object prediction, so the grouping by ground-truth
class pair, and the matching structure, are identical for all three.

Results are flushed every 500 images to WAGER_INLINE/part_<first>_<last>.npz, with
image indices offset by WAGER_OFFSET so separate image ranges can be merged.
"""
import os

import numpy as np
import torch

OUT = os.environ.get("WAGER_INLINE", "")
OFFSET = int(os.environ.get("WAGER_OFFSET", "0"))
BIG = 255
VARIANTS = ("none", "TDE", "la1")
_LOGPRIOR = None
_BUF = None
CHECK = {"pairset_mismatch": 0, "official_score_maxdiff": 0.0, "identity_maxdiff": 0.0,
         "images": 0, "relations": 0, "relations_matched": 0}


def _reset():
    global _BUF
    _BUF = {"first": None, "last": None,
            **{k: [] for k in ("image_index", "sbox", "obox", "img_wh", "subj", "obj",
                               "pred", "matched")},
            **{f"{v}_{k}": [] for v in VARIANTS for k in ("probs", "gc", "ng")}}


_reset()


def set_log_prior(counts):
    global _LOGPRIOR
    lp = np.zeros(51, dtype=np.float32)
    lp[1:] = np.log(counts[1:] / counts[1:].sum()).astype(np.float32)
    _LOGPRIOR = lp


def _softmax(x):
    return torch.softmax(torch.from_numpy(np.ascontiguousarray(x, dtype=np.float32)), -1).numpy()


def _ranks(prob, order, objprod):
    m = prob.shape[0]
    pair_rank = np.empty(m, dtype=np.int64)
    pair_rank[order] = np.arange(m)
    sp = objprod[order][:, None] * prob[order][:, 1:]
    flat = np.argsort(-sp.ravel())                       # the evaluator's argsort_desc
    pos = np.empty(flat.size, dtype=np.int64)
    pos[flat] = np.arange(flat.size)
    ng = np.full((m, 51), 1 << 40, dtype=np.int64)
    ng[:, 1:] = pos.reshape(sp.shape)[pair_rank]
    top = 1 + prob[:, 1:].argmax(1)
    return pair_rank, ng, top


def process(dataset, img_id, pred_boxlist, branch):
    from maskrcnn_benchmark.utils.miscellaneous import bbox_overlaps
    gt = dataset.get_groundtruth(img_id, evaluation=True)
    rel = gt.get_field("relation_tuple").numpy().astype(np.int64)
    if len(rel) == 0:
        return
    w, h = gt.size
    pr = pred_boxlist.resize((w, h))
    gl = gt.get_field("labels").numpy().astype(np.int64)
    gb = gt.convert("xyxy").bbox.numpy()
    pl = pr.get_field("pred_labels").numpy().astype(np.int64)
    ps = pr.get_field("pred_scores").numpy().astype(np.float64)
    pb = pr.convert("xyxy").bbox.numpy()
    off_pairs = pr.get_field("rel_pair_idxs").numpy().astype(np.int64)
    off_scores = pr.get_field("pred_rel_scores").numpy()

    pairs = branch["pairs"].astype(np.int64)
    n_p = len(pl)
    key = pairs[:, 0] * n_p + pairs[:, 1]
    okey = off_pairs[:, 0] * n_p + off_pairs[:, 1]
    if len(key) != len(okey) or set(key.tolist()) != set(okey.tolist()):
        CHECK["pairset_mismatch"] += 1
        return
    pos_of = {int(k): i for i, k in enumerate(key)}
    off_order = np.asarray([pos_of[int(k)] for k in okey])

    logits = {"none": branch["vis"] + branch["ctxp"] + branch["frq"], "TDE": branch["out"]}
    logits["la1"] = logits["none"] - _LOGPRIOR
    CHECK["identity_maxdiff"] = max(CHECK["identity_maxdiff"], float(np.abs(
        (branch["ctxp"] - branch["ctxa"]) - branch["out"]).max()))
    p_tde = _softmax(branch["out"])
    CHECK["official_score_maxdiff"] = max(CHECK["official_score_maxdiff"],
                                          float(np.abs(p_tde[off_order] - off_scores).max()))

    iou = bbox_overlaps(gb, pb)
    mobj = (gl[:, None] == pl[None, :]) & (iou >= 0.5)
    lut = np.full((n_p, n_p), -1, dtype=np.int64)
    lut[pairs[:, 0], pairs[:, 1]] = np.arange(len(pairs))
    cands, own = [], np.full(len(rel), -1, dtype=np.int64)
    for r, (s, o, _y) in enumerate(rel):
        si, oi = np.where(mobj[s])[0], np.where(mobj[o])[0]
        grid = lut[np.ix_(si, oi)]
        cc = grid.ravel()
        cands.append(cc[cc >= 0])
        if (grid >= 0).any():
            score = iou[s, si][:, None] + iou[o, oi][None, :]
            score[grid < 0] = -1
            own[r] = grid.ravel()[int(score.argmax())]
    objprod = ps[pairs[:, 0]] * ps[pairs[:, 1]]

    for v in VARIANTS:
        if v == "TDE":
            p = np.empty_like(p_tde)
            p[off_order] = off_scores                    # the evaluated scores and order
            order = off_order
        else:
            p = _softmax(logits[v])
            triple = torch.from_numpy(p[:, 1:].max(1) * objprod)
            order = torch.sort(triple, descending=True)[1].numpy()
        pair_rank, ngr, top = _ranks(p, order, objprod)
        g_out = np.full((len(rel), 51), BIG, dtype=np.int64)
        n_out = np.full((len(rel), 51), BIG, dtype=np.int64)
        for r, cc in enumerate(cands):
            if len(cc):
                np.minimum.at(g_out[r], top[cc], pair_rank[cc])
                n_out[r] = np.minimum(n_out[r], ngr[cc].min(0))
        _BUF[f"{v}_gc"].append(np.minimum(g_out, BIG).astype(np.uint8))
        _BUF[f"{v}_ng"].append(np.minimum(n_out, BIG).astype(np.uint8))
        pv = np.full((len(rel), 51), np.nan, dtype=np.float32)
        pv[own >= 0] = p[own[own >= 0]]
        _BUF[f"{v}_probs"].append(pv)

    gidx = OFFSET + int(img_id)
    _BUF["first"] = gidx if _BUF["first"] is None else _BUF["first"]
    _BUF["last"] = gidx
    _BUF["image_index"].append(np.full(len(rel), gidx, dtype=np.int32))
    _BUF["sbox"].append(gb[rel[:, 0]].astype(np.float32))
    _BUF["obox"].append(gb[rel[:, 1]].astype(np.float32))
    _BUF["img_wh"].append(np.tile(np.float32([w, h]), (len(rel), 1)))
    _BUF["subj"].append(gl[rel[:, 0]].astype(np.int32))
    _BUF["obj"].append(gl[rel[:, 1]].astype(np.int32))
    _BUF["pred"].append(rel[:, 2].astype(np.int32))
    _BUF["matched"].append(own >= 0)
    CHECK["images"] += 1
    CHECK["relations"] += len(rel)
    CHECK["relations_matched"] += int((own >= 0).sum())
    if len(_BUF["pred"]) >= 500:
        flush()


def flush():
    if not _BUF["pred"]:
        return
    os.makedirs(OUT, exist_ok=True)
    name = f"{OUT}/part_{_BUF['first']:06d}_{_BUF['last']:06d}"
    np.savez_compressed(name + ".tmp.npz", check=np.array(str(CHECK)),
                        **{k: np.concatenate(v) for k, v in _BUF.items()
                           if isinstance(v, list)})
    os.replace(name + ".tmp.npz", name + ".npz")
    _reset()
