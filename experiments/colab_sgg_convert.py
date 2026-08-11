"""Convert one evaluation dump to a compact per-relation npz, in small steps.

The dump is a single pickle holding a BoxList per image with a 51-way score row
for every ordered object pair, so it is large. This converts exactly one variant
per invocation (set WAGER_EFFECT), releases each image's tensors as it goes, and
checkpoints every CHUNK images so an interrupted run resumes rather than
restarting.

weights_only=False is required and safe here: the dump is a file we generate on
our own VM, and it holds BoxList objects that the restricted unpickler cannot
reconstruct.

Usage on the VM:  WAGER_EFFECT=none python colab_sgg_convert.py
"""
import gc
import json
import os
import sys
import time

import numpy as np
import torch

ROOT = "/content"
SGG = f"{ROOT}/sgg"
sys.path.insert(0, f"{ROOT}/pylib")
sys.path.insert(0, SGG)

EFFECT = os.environ.get("WAGER_EFFECT", "none")
OUTDIR = {"none": f"{ROOT}/out_none", "TDE": f"{ROOT}/out_tde"}[EFFECT]
DST = f"{ROOT}/motifs_{EFFECT}_predcls.npz"
PART = f"{ROOT}/motifs_{EFFECT}_partial.npz"
CHUNK = 4000
KEYS = ("image_index", "sbox", "obox", "img_wh", "subj", "obj", "pred", "probs")
T0 = time.time()


def log(m):
    print(f"[convert:{EFFECT} +{time.time()-T0:.0f}s] {m}", flush=True)


def stack(base, cur):
    """Merge accumulated python lists into the persistent arrays."""
    out = {}
    for k in KEYS:
        new = np.asarray(cur[k]) if cur[k] else None
        if base.get(k) is None or len(base[k]) == 0:
            out[k] = new if new is not None else np.asarray([])
        elif new is None:
            out[k] = base[k]
        else:
            out[k] = np.concatenate([base[k], new])
    return out


if os.path.exists(DST):
    log(f"{DST} already exists -- nothing to do")
    sys.exit(0)

log(f"loading {OUTDIR}/eval_results.pytorch")
d = torch.load(f"{OUTDIR}/eval_results.pytorch", map_location="cpu",
               weights_only=False)
gts, preds = d["groundtruths"], d["predictions"]
n_img = len(gts)
log(f"{n_img} images; gt fields {gts[0].fields()}; pred fields {preds[0].fields()}")

base = {k: None for k in KEYS}
start, n_miss = 0, 0
if os.path.exists(PART):
    p = np.load(PART)
    start, n_miss = int(p["next_image"]), int(p["n_miss"])
    base = {k: p[k] for k in KEYS}
    log(f"resuming at image {start} with {len(base['pred'])} relations")

cur = {k: [] for k in KEYS}
for i in range(start, n_img):
    gt, pr = gts[i], preds[i]
    rel = gt.get_field("relation_tuple").numpy()
    labels = gt.get_field("labels").numpy()
    boxes = gt.bbox.numpy()
    w, h = gt.size
    pair_idx = pr.get_field("rel_pair_idxs").numpy()
    scores = pr.get_field("pred_rel_scores").numpy()
    lut = {(int(a), int(b)): k for k, (a, b) in enumerate(pair_idx)}
    for s, o, y in rel:
        k = lut.get((int(s), int(o)))
        if k is None:
            n_miss += 1
            continue
        cur["image_index"].append(i)
        cur["sbox"].append(boxes[int(s)])
        cur["obox"].append(boxes[int(o)])
        cur["img_wh"].append((w, h))
        cur["subj"].append(int(labels[int(s)]))
        cur["obj"].append(int(labels[int(o)]))
        cur["pred"].append(int(y))
        cur["probs"].append(scores[k])
    gts[i] = None                      # release this image's tensors
    preds[i] = None
    if (i + 1) % CHUNK == 0:
        base = stack(base, cur)
        cur = {k: [] for k in KEYS}
        np.savez_compressed(PART, next_image=i + 1, n_miss=n_miss, **base)
        gc.collect()
        log(f"  {i+1}/{n_img} images -> {len(base['pred'])} relations")

final = stack(base, cur)
np.savez_compressed(
    DST,
    image_index=final["image_index"].astype(np.int32),
    sbox=final["sbox"].astype(np.float32),
    obox=final["obox"].astype(np.float32),
    img_wh=final["img_wh"].astype(np.float32),
    subj=final["subj"].astype(np.int32),
    obj=final["obj"].astype(np.int32),
    pred=final["pred"].astype(np.int32),
    probs=final["probs"].astype(np.float32),
    n_missing_pairs=n_miss)
log(f"wrote {DST}: {len(final['pred'])} relations, {n_miss} unmatched pairs")

rd = f"{OUTDIR}/result_dict.pytorch"
if os.path.exists(rd):
    r = torch.load(rd, map_location="cpu", weights_only=False)
    summary = {}
    for k, v in r.items():
        try:
            summary[str(k)] = {str(kk): float(np.mean(vv)) for kk, vv in v.items()}
        except Exception:
            pass
    with open(f"{ROOT}/motifs_{EFFECT}_recalls.json", "w") as f:
        json.dump(summary, f, indent=2)
    log("wrote recall summary")

if os.path.exists(PART):
    os.remove(PART)
log("CONVERT COMPLETE")
