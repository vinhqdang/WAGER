"""Memory-equivalent rewrite of rel_nms (VG-PENET maskrcnn_benchmark/data/datasets/
evaluation/vg/sgg_eval.py), used only because the original runs out of memory on
the 12 GB Colab runtime.

The original builds an N x N x 51 float array for the pair-pair overlap score l21
(N = number of predicted pairs in an image; a dense image has N of several thousand,
which is over 10 GB). This version computes the identical l21 values in row blocks
(the same elementwise operations and the same last-axis sum), keeps the overlap test
as an N x N mask (the original repeats it over the 51 predicates, and every use indexes
one predicate column, so the repeated copies are never read differently), and runs the
same greedy loop. Outputs are identical; `python penet_rel_nms_chunked.py <sgg_eval.py>`
checks this against the original function on random inputs.
"""
import ast
import sys

import numpy as np

BLOCK = 128


def rel_nms_chunked(pred_boxes, pred_classes, pred_rel_inds, rel_scores, nms_thresh=0.5,
                    l21_thr=0.7, bbox_overlaps=None):
    ious = bbox_overlaps(pred_boxes, pred_boxes)
    sub_ious = ious[pred_rel_inds[:, 0]][:, pred_rel_inds[:, 0]]
    obj_ious = ious[pred_rel_inds[:, 1]][:, pred_rel_inds[:, 1]]
    rel_ious = np.minimum(sub_ious, obj_ious)
    sub_labels = pred_classes[pred_rel_inds[:, 0]]
    obj_labels = pred_classes[pred_rel_inds[:, 1]]
    n = rel_scores.shape[0]
    overlap = np.zeros((n, n), dtype=bool)
    for i0 in range(0, n, BLOCK):
        i1 = min(n, i0 + BLOCK)
        l21 = np.sqrt((np.power(rel_scores[i0:i1, None, :], 2.0)
                       + np.power(rel_scores[None, :, :], 2.0))).sum(axis=-1)
        overlap[i0:i1] = ((rel_ious[i0:i1] >= nms_thresh)
                          & (sub_labels[i0:i1, None] == sub_labels[None, :])
                          & (obj_labels[i0:i1, None] == obj_labels[None, :])
                          & (l21 > l21_thr))
    rel_scores_cp = rel_scores.copy()
    rel_scores_cp[:, 0] = 0.
    pred_rels = np.zeros(rel_scores_cp.shape[0], dtype=np.int64)
    for i in range(rel_scores_cp.shape[0]):
        box_ind, cls_ind = np.unravel_index(rel_scores_cp.argmax(), rel_scores_cp.shape)
        if float(pred_rels[int(box_ind)]) > 0:
            pass
        else:
            pred_rels[int(box_ind)] = int(cls_ind)
        rel_scores_cp[overlap[box_ind], cls_ind] = 0.0
        rel_scores_cp[box_ind] = -1.
    return pred_rels, rel_scores[np.arange(pred_rels.shape[0], dtype=np.int64), pred_rels]


def _iou(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    lt = np.maximum(a[:, None, :2], b[None, :, :2])
    rb = np.minimum(a[:, None, 2:], b[None, :, 2:])
    wh = np.clip(rb - lt, 0, None)
    inter = wh[..., 0] * wh[..., 1]
    area_a = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1])
    area_b = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    return inter / (area_a[:, None] + area_b[None, :] - inter)


def selftest(sgg_eval_path, trials=300, seed=0):
    src = open(sgg_eval_path).read()
    fn = next(n for n in ast.parse(src).body
              if isinstance(n, ast.FunctionDef) and n.name == "rel_nms")
    ns = {"np": np, "bbox_overlaps": _iou}
    exec(compile(ast.Module([fn], []), sgg_eval_path, "exec"), ns)
    original = ns["rel_nms"]
    rng = np.random.default_rng(seed)
    checked = 0
    for t in range(trials):
        n_obj = int(rng.integers(2, 40))
        xy = rng.uniform(0, 100, (n_obj, 2))
        wh = rng.uniform(2, 60, (n_obj, 2))
        boxes = np.concatenate([xy, xy + wh], 1).astype(np.float32)
        classes = rng.integers(1, 6, n_obj).astype(np.int64)
        pairs = np.array([(i, j) for i in range(n_obj) for j in range(n_obj) if i != j])
        keep = rng.random(len(pairs)) < 0.7
        pairs = pairs[keep] if keep.any() else pairs[:1]
        logits = rng.normal(0, 3, (len(pairs), 51)).astype(np.float32)
        scores = np.exp(logits - logits.max(1, keepdims=True))
        scores = (scores / scores.sum(1, keepdims=True)).astype(np.float32)
        a = original(boxes, classes, pairs, scores, 0.6)
        b = rel_nms_chunked(boxes, classes, pairs, scores, 0.6, bbox_overlaps=_iou)
        assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]), f"trial {t} differs"
        checked += 1
    return checked


if __name__ == "__main__":
    k = selftest(sys.argv[1])
    print(f"rel_nms_chunked matches the original on {k} random images")
