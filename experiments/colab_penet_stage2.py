"""PE-Net audit stage 2 (Colab): one official PredCls evaluation of the released
PE-Net checkpoint (Zheng et al., CVPR 2023), dumping the predicate distribution the
evaluator consumes for every object pair.

PE-Net's predicate logits are cosine similarities between the relation and the
predicate prototypes, scaled by exp(logit_scale) (roi_relation_predictors.py,
PrototypeEmbeddingNetwork.forward: rel_dists = rel_rep_norm @ predicate_proto_norm.t()
* logit_scale.exp()). The post-processor applies a plain softmax to them
(inference.py, PostProcessor.forward), so the dump holds, per pair, the softmax
(rel_class_prob at the point where it is first defined, before the pairs are
sorted by triple score) and the pair indices, exactly as colab_dlfe_stage2.py does
for MOTIFS-DLFE. colab_sgg_rank.py (WAGER_RANK_MODE=penet) turns the dump into
per-relation probabilities and ranks, replaying the evaluator's predcls path,
which applies rel_nms (sgg_eval.py, SGRecall.calculate_recall) to the graph-
constrained recall; the no-graph-constraint recall is not affected.

Per README (Test): configs/e2e_relation_X_101_32_8_FPN_1x.yaml, PrototypeEmbeddingNetwork,
USE_GT_BOX and USE_GT_OBJECT_LABEL True, TEST.IMS_PER_BATCH 1, DTYPE float32,
MODEL.WEIGHT = the checkpoint. The README's MODEL.PRETRAINED_DETECTOR_CKPT is read
only by the training code (relation_train_net.py), not by relation_test_net.py, so
it is not passed. OUTPUT_DIR must contain "predcls" (the fork asserts it).

Usage on the VM:  python colab_penet_stage2.py   (idempotent)
"""
import glob
import json
import os
import re
import shutil
import subprocess
import time

ROOT = "/content"
PN = f"{ROOT}/penet"
CKPT = f"{ROOT}/penet_ckpt/pred_cls_model_final.pth"
OUT = f"{ROOT}/out_penet_predcls"
DUMP = f"{ROOT}/dump_penet"
TEST = "VG_stanford_filtered_with_attribute_test"
T0 = time.time()


def log(m):
    print(f"[penet2 +{time.time()-T0:.0f}s] {m}", flush=True)


# ---- dump hook in PostProcessor.forward (idempotent) ----------------------------
pp = f"{PN}/maskrcnn_benchmark/modeling/roi_heads/relation_head/inference.py"
s = open(pp).read()
if "# WAGER-DUMP" not in s:
    anchor = "            rel_scores, rel_class = rel_class_prob[:, 1:].max(dim=1)\n"
    assert s.count(anchor) == 1, "post-processor anchor not found"
    s = s.replace(anchor, (
        "            if WAGER_DUMP and (not self.training):  # WAGER-DUMP\n"
        "                _wager_record(i, rel_pair_idx, F.softmax(rel_logit, -1), rel_class_prob, None)\n")
        + anchor)
    s += '''

# WAGER-DUMP helpers: the per-pair predicate scores the evaluator consumes.
import os as _wos
import numpy as _wnp
WAGER_DUMP = _wos.environ.get("WAGER_DUMP", "")
WAGER_IMAGE_IDS = None
_WKEYS = ("pairs", "soft", "out")
_WBUF = {"ids": [], "n_pairs": [], "chunk": 0, "lp": None, **{k: [] for k in _WKEYS}}


def _wager_flush():
    b = _WBUF
    if not b["ids"]:
        return
    _wos.makedirs(WAGER_DUMP, exist_ok=True)
    tmp = f"{WAGER_DUMP}/chunk_{b['chunk']:04d}.tmp.npz"
    _wnp.savez(tmp, image_ids=_wnp.asarray(b["ids"], dtype=_wnp.int64),
               n_pairs=_wnp.asarray(b["n_pairs"], dtype=_wnp.int64),
               **{k: _wnp.concatenate(b[k]) for k in _WKEYS})
    _wos.replace(tmp, f"{WAGER_DUMP}/chunk_{b['chunk']:04d}.npz")
    b["chunk"] += 1
    b["ids"], b["n_pairs"] = [], []
    for k in _WKEYS:
        b[k] = []


def _wager_record(i, rel_pair_idx, soft, out, labeling_prob):
    ids = WAGER_IMAGE_IDS
    assert ids is not None and i < len(ids), "image ids not set"
    with torch.no_grad():
        _WBUF["ids"].append(int(ids[i]))
        _WBUF["n_pairs"].append(int(rel_pair_idx.shape[0]))
        _WBUF["pairs"].append(rel_pair_idx.cpu().numpy().astype(_wnp.int16))
        _WBUF["soft"].append(soft.float().cpu().numpy().astype(_wnp.float32))
        _WBUF["out"].append(out.float().cpu().numpy().astype(_wnp.float32))
    if len(_WBUF["ids"]) >= 1000:
        _wager_flush()
'''
    open(pp, "w").write(s)
    log("PostProcessor patched for the dump")

ip = f"{PN}/maskrcnn_benchmark/engine/inference.py"
s = open(ip).read()
if "WAGER_IMAGE_IDS" not in s:
    a = "            images, targets, image_ids = batch\n"
    mod = "maskrcnn_benchmark.modeling.roi_heads.relation_head.inference"
    assert s.count(a) == 1
    s = s.replace(a, a + f"            import {mod} as _wp\n"
                  "            _wp.WAGER_IMAGE_IDS = list(image_ids)\n")
    e = "    torch.cuda.empty_cache()\n    return results_dict\n"
    assert s.count(e) == 1
    s = s.replace(e, f"    import {mod} as _wp\n    _wp._wager_flush()\n" + e)
    open(ip, "w").write(s)
    log("inference loop patched")

# ---- run ----------------------------------------------------------------------------
assert os.path.exists(CKPT), CKPT
os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/last_checkpoint", "w").write(CKPT)
if os.path.exists(f"{OUT}/inference/{TEST}/result_dict.pytorch") and \
        os.path.exists(f"{OUT}/official_penet.json"):
    log("already evaluated")
else:
    shutil.rmtree(DUMP, ignore_errors=True)        # a partial dump cannot be resumed
    log(f"=== penet: {CKPT} ({os.path.getsize(CKPT)/1e9:.2f} GB) ===")
    cmd = ["python", f"{PN}/tools/relation_test_net.py",
           "--config-file", f"{PN}/configs/e2e_relation_X_101_32_8_FPN_1x.yaml",
           "MODEL.ROI_RELATION_HEAD.USE_GT_BOX", "True",
           "MODEL.ROI_RELATION_HEAD.USE_GT_OBJECT_LABEL", "True",
           "MODEL.ROI_RELATION_HEAD.PREDICTOR", "PrototypeEmbeddingNetwork",
           "TEST.IMS_PER_BATCH", "1", "DTYPE", "float32",
           "GLOVE_DIR", f"{ROOT}/glove",
           "MODEL.WEIGHT", CKPT,
           "OUTPUT_DIR", OUT]
    env = dict(os.environ, PYTHONPATH=f"{ROOT}/pylib:{PN}", WAGER_DUMP=DUMP)
    p = subprocess.Popen(cmd, cwd=PN, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True)
    tail, official, warn = [], [], []
    with open(f"{ROOT}/eval_penet.log", "w") as lf:
        for line in p.stdout:
            lf.write(line)
            tail = (tail + [line])[-300:]
            if "SGG eval" in line:
                official.append(line.strip())
            if re.search(r"missing|unexpected|not found|mismatch", line, re.I):
                warn.append(line.strip()[:300])
            if "SGG eval" in line or "rror" in line or "Loading" in line:
                print(line.rstrip(), flush=True)
            if re.search(r"\b\d+/26446 \[", line):
                open(f"{ROOT}/progress_penet.txt", "w").write(line.rsplit("\r", 1)[-1])
    p.wait()
    if p.returncode != 0:
        print("".join(tail[-120:]), flush=True)
        raise SystemExit(f"penet: evaluation failed rc={p.returncode}")
    n = len(glob.glob(f"{DUMP}/chunk_*[0-9].npz"))
    log(f"penet: dump has {n} chunks; load warnings: {len(warn)}")
    if n == 0:
        raise SystemExit("penet: no dump written")
    # the printed official numbers, parsed: {"R@20": .., "ng-R@20": .., "mR@50": .., ...}
    vals = {}
    for ln in official:
        m = re.search(r"SGG eval:\s*(.*?);\s+for mode=predcls, type=(.*?)\.?$", ln)
        if not m:
            continue
        for tag, K, v in re.findall(r"([A-Za-z\-]+) @ (\d+): ([\d.]+)", m.group(1)):
            vals[f"{tag}@{K}"] = float(v)
    json.dump({"model": "penet", "checkpoint": CKPT, "printed": official, "values": vals,
               "load_warnings": warn[:50]},
              open(f"{OUT}/official_penet.json", "w"), indent=1)
    log("penet: official " + ", ".join(f"{k} {v}" for k, v in vals.items()
                                       if k in ("R@50", "mR@50", "ng-R@50", "ng-mR@50")))
log("PENET STAGE 2 COMPLETE")
