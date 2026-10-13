"""DLFE audit stage 2 (Colab): one official PredCls evaluation each of the released
MOTIFS baseline and MOTIFS-DLFE checkpoints (Chiou et al., ACM MM 2021), dumping
the predicate distribution the evaluator consumes for every object pair.

Where DLFE acts at test time (maskrcnn_benchmark/modeling/roi_heads/relation_head):
  relation_head.py   with MODEL.BALANCED_NORM, ROIRelationHead.forward passes the
                     predictor's logits through BalancedNorm1d (layers/
                     balanced_norm.py), which in eval mode returns
                         softmax(logits) / (running_labeling_prob + 1e-5),
                     the running estimate of the per-predicate label frequency
                     p(s=r | y=r) kept as a buffer in the checkpoint (index 0,
                     background, fixed at 1). Nothing renormalises the result
                     (MODEL.BALANCED_NORM_NORMALIZED_PROBS is off by default and
                     absent from the released config).
  inference.py       PostProcessor.forward takes that matrix as rel_class_prob
                     (plain softmax(logits) for the baseline), ranks pairs by its
                     foreground maximum (times the object scores, one in PredCls)
                     and stores the matrix as the pred_rel_scores field the
                     evaluator reads.
The patch below sits in PostProcessor.forward, so what is dumped is exactly
rel_class_prob -- post-correction for DLFE, raw softmax for the baseline -- plus
the raw softmax, the pair indices and, once per chunk, the labeling-probability
vector. colab_sgg_rank.py (WAGER_RANK_MODE=dlfe / dlfe_base) turns the dump into
per-relation probabilities and first-hit ranks and checks them against the
official dump and the official recalls.

Per README: configs/e2e_relation_X_101_32_8_FPN_1x.yaml, MotifPredictor, PredCls,
MODEL.BALANCED_NORM True for the DLFE model; the baseline is the same command
without it. OUTPUT_DIR must contain "predcls" (the fork asserts it). The authors'
training-set statistics cache ships in the zip and is reused.

Usage on the VM:  python colab_dlfe_stage2.py   (idempotent; resumes per model)
Env: WAGER_DLFE_MODELS=dlfe,base (default) selects / orders the runs.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import time

ROOT = "/content"
DLFE = f"{ROOT}/dlfe"
CKPT = f"{ROOT}/dlfe_ckpt/output"
MODELS = {
    # name: (checkpoint dir in the zip, extra config overrides)
    "dlfe": ("motif-precls-exmp-balanced_norm", ["MODEL.BALANCED_NORM", "True"]),
    "base": ("motif-precls-exmp", []),
}
ORDER = [m for m in os.environ.get("WAGER_DLFE_MODELS", "dlfe,base").split(",") if m]
T0 = time.time()


def log(m):
    print(f"[dlfe2 +{time.time()-T0:.0f}s] {m}", flush=True)


# ---- dump hook in PostProcessor.forward (idempotent) ----------------------------
pp = f"{DLFE}/maskrcnn_benchmark/modeling/roi_heads/relation_head/inference.py"
s = open(pp).read()
if "# WAGER-DUMP" not in s:
    anchor = "            rel_scores, rel_class = rel_class_prob[:, 1:].max(dim=1)\n"
    assert s.count(anchor) == 1, "post-processor anchor not found"
    s = s.replace(anchor, (
        "            if WAGER_DUMP and (not self.training):  # WAGER-DUMP\n"
        "                _wager_record(i, rel_pair_idx, F.softmax(rel_logit, -1), rel_class_prob,\n"
        "                              None if relation_probs_norm is None else labeling_prob)\n")
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
    extra = {} if b["lp"] is None else {"lp": b["lp"]}
    _wnp.savez(tmp, image_ids=_wnp.asarray(b["ids"], dtype=_wnp.int64),
               n_pairs=_wnp.asarray(b["n_pairs"], dtype=_wnp.int64),
               **{k: _wnp.concatenate(b[k]) for k in _WKEYS}, **extra)
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
        if labeling_prob is not None:
            lp = labeling_prob.float().cpu().numpy().astype(_wnp.float64)
            assert _WBUF["lp"] is None or _wnp.array_equal(_WBUF["lp"], lp), "labeling prob moved"
            _WBUF["lp"] = lp
    if len(_WBUF["ids"]) >= 1000:
        _wager_flush()
'''
    open(pp, "w").write(s)
    log("PostProcessor patched for the dump")

ip = f"{DLFE}/maskrcnn_benchmark/engine/inference.py"
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

# ---- runs -----------------------------------------------------------------------
TEST = "VG_stanford_filtered_with_attribute_test"
for name in ORDER:
    sub, extra = MODELS[name]
    cdir = f"{CKPT}/{sub}"
    pths = sorted(glob.glob(f"{cdir}/*.pth"))
    assert len(pths) == 1, f"{cdir}: {pths}"
    model_pth = pths[0]
    out = f"{ROOT}/out_{name}_predcls"
    dump = f"{ROOT}/dump_{name}"
    os.makedirs(out, exist_ok=True)
    open(f"{out}/last_checkpoint", "w").write(model_pth)
    cache = f"{cdir}/VG_stanford_filtered_with_attribute_train_statistics.cache"
    if os.path.exists(cache) and not os.path.exists(f"{out}/{os.path.basename(cache)}"):
        shutil.copy(cache, out)
    if os.path.exists(f"{out}/inference/{TEST}/result_dict.pytorch") and \
            os.path.exists(f"{out}/official_{name}.json"):
        log(f"{name}: already evaluated")
        continue
    shutil.rmtree(dump, ignore_errors=True)          # a partial dump cannot be resumed
    log(f"=== {name}: {model_pth} ({os.path.getsize(model_pth)/1e9:.2f} GB) ===")
    cmd = ["python", f"{DLFE}/tools/relation_test_net.py",
           "--config-file", f"{DLFE}/configs/e2e_relation_X_101_32_8_FPN_1x.yaml",
           "MODEL.ROI_RELATION_HEAD.USE_GT_BOX", "True",
           "MODEL.ROI_RELATION_HEAD.USE_GT_OBJECT_LABEL", "True",
           "MODEL.ROI_RELATION_HEAD.PREDICTOR", "MotifPredictor",
           *extra,
           "TEST.IMS_PER_BATCH", "1", "DTYPE", "float32",
           "GLOVE_DIR", f"{ROOT}/glove",
           "MODEL.PRETRAINED_DETECTOR_CKPT", model_pth,
           "OUTPUT_DIR", out]
    env = dict(os.environ, PYTHONPATH=f"{ROOT}/pylib:{DLFE}", WAGER_DUMP=dump)
    p = subprocess.Popen(cmd, cwd=DLFE, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True)
    tail, official = [], []
    with open(f"{ROOT}/eval_{name}.log", "w") as lf:
        for line in p.stdout:
            lf.write(line)
            tail = (tail + [line])[-300:]
            if "SGG eval" in line:
                official.append(line.strip())
            if "SGG eval" in line or "rror" in line or "Loading" in line:
                print(line.rstrip(), flush=True)
            if re.search(r"\b\d+/26446 \[", line):
                open(f"{ROOT}/progress_{name}.txt", "w").write(line.rsplit("\r", 1)[-1])
    p.wait()
    if p.returncode != 0:
        print("".join(tail[-120:]), flush=True)
        raise SystemExit(f"{name}: evaluation failed rc={p.returncode}")
    n = len(glob.glob(f"{dump}/chunk_*[0-9].npz"))
    log(f"{name}: dump has {n} chunks")
    if n == 0:
        raise SystemExit(f"{name}: no dump written")
    # the printed official numbers, parsed: {"R@20": .., "ng-R@20": .., "mR@50": .., ...}
    vals = {}
    for ln in official:
        m = re.search(r"SGG eval:\s*(.*?);\s+for mode=predcls, type=(.*?)\.?$", ln)
        if not m:
            continue
        for tag, K, v in re.findall(r"([A-Za-z\-]+) @ (\d+): ([\d.]+)", m.group(1)):
            vals[f"{tag}@{K}"] = float(v)
    json.dump({"model": name, "checkpoint": model_pth, "printed": official, "values": vals},
              open(f"{out}/official_{name}.json", "w"), indent=1)
    log(f"{name}: official " + ", ".join(f"{k} {v}" for k, v in vals.items()
                                         if k in ("R@50", "mR@50", "ng-R@50", "ng-mR@50")))
log("DLFE STAGE 2 COMPLETE")
