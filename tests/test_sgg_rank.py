"""The offline recall ranks must reproduce the official PredCls evaluator.

experiments/colab_sgg_rank.py turns each image's pair scores into, for every
ground-truth relation and every predicate, the rank at which the evaluator would
first match that triplet. Mean-recall decomposition then evaluates recall under
counterfactual labels from those ranks alone, so they have to agree with the
evaluator for any labelling, not just the observed one. This checks them against
the evaluator's matching code (Scene-Graph-Benchmark.pytorch, sgg_eval.py,
reproduced below) on random images with duplicated objects, repeated pairs and
relabelled ground truth.
"""
from __future__ import annotations

import importlib.util
import pathlib
from functools import reduce

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "colab_sgg_rank", ROOT / "experiments/colab_sgg_rank.py")
rank = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rank)


# ---- reference: the evaluator's own routines -------------------------------
def iou(b1, b2):
    lt = np.maximum(b1[:, None, :2], b2[:, :2])
    rb = np.minimum(b1[:, None, 2:], b2[:, 2:])
    wh = np.clip(rb - lt + 1, 0, None)
    inter = wh[..., 0] * wh[..., 1]
    a1 = (b1[:, 2] - b1[:, 0] + 1) * (b1[:, 3] - b1[:, 1] + 1)
    a2 = (b2[:, 2] - b2[:, 0] + 1) * (b2[:, 3] - b2[:, 1] + 1)
    return inter / (a1[:, None] + a2 - inter)


def intersect_2d(x1, x2):
    return (x1[..., None] == x2.T[None, ...]).all(1)


def argsort_desc(scores):
    return np.column_stack(np.unravel_index(np.argsort(-scores.ravel()), scores.shape))


def _triplet(relations, classes, boxes):
    s, o, p = relations[:, 0], relations[:, 1], relations[:, 2]
    return (np.column_stack((classes[s], p, classes[o])),
            np.column_stack((boxes[s], boxes[o])))


def _compute_pred_matches(gt_triplets, pred_triplets, gt_boxes, pred_boxes, thr=0.5):
    keeps = intersect_2d(gt_triplets, pred_triplets)
    gt_has_match = keeps.any(1)
    pred_to_gt = [[] for _ in range(pred_boxes.shape[0])]
    for gt_ind, gt_box, keep_inds in zip(np.where(gt_has_match)[0],
                                         gt_boxes[gt_has_match], keeps[gt_has_match]):
        boxes = pred_boxes[keep_inds]
        sub_iou = iou(gt_box[None, :4], boxes[:, :4])[0]
        obj_iou = iou(gt_box[None, 4:], boxes[:, 4:])[0]
        inds = (sub_iou >= thr) & (obj_iou >= thr)
        for i in np.where(keep_inds)[0][inds]:
            pred_to_gt[i].append(int(gt_ind))
    return pred_to_gt


def official_hits(gt_rels, classes, boxes, pred_rel_inds, rel_scores, k):
    """Per-GT hit indicators, graph constraint and no graph constraint."""
    gt_t, gt_b = _triplet(gt_rels, classes, boxes)
    pred_rels = np.column_stack((pred_rel_inds, 1 + rel_scores[:, 1:].argmax(1)))
    pt, pb = _triplet(pred_rels, classes, boxes)
    p2g = _compute_pred_matches(gt_t, pt, gt_b, pb)
    gc = reduce(np.union1d, p2g[:k]) if k else []
    inds = argsort_desc(rel_scores[:, 1:])[:100]
    ng_rels = np.column_stack((pred_rel_inds[inds[:, 0]], inds[:, 1] + 1))
    nt, nb = _triplet(ng_rels, classes, boxes)
    p2g = _compute_pred_matches(gt_t, nt, gt_b, nb)
    ng = reduce(np.union1d, p2g[:k])
    out_gc = np.zeros(len(gt_rels), bool)
    out_ng = np.zeros(len(gt_rels), bool)
    out_gc[np.asarray(gc, dtype=int)] = True
    out_ng[np.asarray(ng, dtype=int)] = True
    return out_gc, out_ng


# ---- fixture -----------------------------------------------------------------
def random_image(rng):
    n = int(rng.integers(3, 10))
    base = rng.uniform(0, 300, size=(n, 2))
    boxes = np.column_stack((base, base + rng.uniform(20, 120, size=(n, 2))))
    labels = rng.integers(1, 4, size=n)          # few classes -> same-class objects
    for i in range(1, n):                        # near-duplicate objects
        if rng.random() < 0.35:
            j = int(rng.integers(0, i))
            boxes[i] = boxes[j] + rng.uniform(-8, 8, size=4)
            labels[i] = labels[j]
    pairs = np.array([(a, b) for a in range(n) for b in range(n) if a != b])
    logits = rng.normal(0, 2.5, size=(len(pairs), 51))
    logits[:, 1:4] += rng.normal(1.5, 1.0, size=(len(pairs), 3))  # contested head
    prob = np.exp(logits - logits.max(1, keepdims=True))
    prob = (prob / prob.sum(1, keepdims=True)).astype(np.float32)
    n_rel = int(rng.integers(1, 2 * n))
    rel = pairs[rng.integers(0, len(pairs), size=n_rel)]   # repeated pairs allowed
    rel = np.column_stack((rel, rng.integers(1, 51, size=n_rel)))
    return labels, boxes.astype(np.float32), pairs, prob, rel


def test_ranks_reproduce_the_official_evaluator_under_any_labelling():
    rng = np.random.default_rng(7)
    checked = 0
    for _ in range(150):
        labels, boxes, pairs, prob, rel = random_image(rng)
        order = np.argsort(-prob[:, 1:].max(1), kind="stable")
        cands, _ = rank.match_candidates(rel, labels, iou(boxes, boxes), pairs, len(labels))
        gc_rank, ng_rank = rank.relation_ranks(prob, order, cands)
        for relabel in range(4):
            y = rel[:, 2] if relabel == 0 else rng.integers(1, 51, size=len(rel))
            if relabel == 3:                  # labels each image's pairs predict
                y = 1 + prob[[np.where((pairs == r[:2]).all(1))[0][0] for r in rel], 1:].argmax(1)
            gt = np.column_stack((rel[:, :2], y))
            for k in (1, 5, 20, 50, 100):
                hg, hn = official_hits(gt, labels, boxes, pairs[order], prob[order], k)
                ix = np.arange(len(rel))
                assert np.array_equal(gc_rank[ix, y] < k, hg)
                assert np.array_equal(ng_rank[ix, y] < k, hn)
                checked += len(rel)
    assert checked > 5000
