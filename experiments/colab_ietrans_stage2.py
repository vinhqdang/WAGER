"""IETrans audit stage 2 (Colab): one PredCls evaluation of the released IETrans
Neural-Motifs checkpoint, dumping its logits for every object pair.

MotifPredictor's PredCls logit is  ctx + frq : a context-and-vision term plus the
frequency bias indexed by the object-class pair. The patched predictor writes
both terms and the returned logits for every pair of every test image, in the
format colab_sgg_rank.py reads (WAGER_RANK_MODE=ietrans). The official
evaluator still runs on the returned logits.

The evaluation reproduces the authors' command (cmds/50/motif/predcls/lt/combine/
val.sh): configs/sup-50.yaml, MotifPredictor, PREDICT_USE_BIAS True. The released
weights hold no frequency bias (trained without one); with PREDICT_USE_BIAS the
predictor builds it at test time from the training split's log predicate
frequencies per object-class pair, so frq is a fixed per-cell log-prior.
"""
import glob
import os
import subprocess
import time

ROOT = "/content"
IET = f"{ROOT}/iet"
OUT = f"{ROOT}/out_ietrans"
DUMP = f"{ROOT}/branch_dump_ietrans"
T0 = time.time()


def log(m):
    print(f"[iet2 +{time.time()-T0:.0f}s] {m}", flush=True)


# ---- dump hook in MotifPredictor (idempotent) -----------------------------------
pp = f"{IET}/maskrcnn_benchmark/modeling/roi_heads/relation_head/roi_relation_predictors.py"
s = open(pp).read()
if "# WAGER-DUMP" not in s:
    start = s.index("class MotifPredictor")
    old = ("        if (self.train_use_bias and self.training) or "
           "(self.predict_use_bias and not self.training):\n"
           "            rel_dists = rel_dists + self.freq_bias.index_with_labels(pair_pred.long())\n")
    i = s.index(old, start)
    assert i < s.index("@registry", start + 10), "bias line not inside MotifPredictor"
    new = ("        _w_ctx = rel_dists  # WAGER-DUMP\n" + old +
           "        if WAGER_DUMP and (not self.training):\n"
           "            _wager_record(_w_ctx, self.freq_bias.index_with_labels(pair_pred.long()),\n"
           "                          rel_dists, rel_pair_idxs, num_rels)\n")
    s = s[:i] + new + s[i + len(old):]
    s += '''

# WAGER-DUMP helpers: per-pair logits for offline re-scoring.
import os as _wos
import numpy as _wnp
WAGER_DUMP = _wos.environ.get("WAGER_DUMP", "")
WAGER_IMAGE_IDS = None
_WKEYS = ("pairs", "ctx", "frq", "out")
_WBUF = {"ids": [], "n_pairs": [], "chunk": 0, **{k: [] for k in _WKEYS}}


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


def _wager_record(ctx, frq, out, rel_pair_idxs, num_rels):
    ids = WAGER_IMAGE_IDS
    assert ids is not None and len(ids) == len(num_rels), "image ids not set"
    with torch.no_grad():
        parts = {"ctx": ctx, "frq": frq, "out": torch.cat(out) if isinstance(out, (list, tuple)) else out}
        parts = {k: v.float().cpu().numpy().astype(_wnp.float32) for k, v in parts.items()}
    off = 0
    for img_id, n, pidx in zip(ids, num_rels, rel_pair_idxs):
        _WBUF["ids"].append(int(img_id))
        _WBUF["n_pairs"].append(int(n))
        _WBUF["pairs"].append(pidx.cpu().numpy().astype(_wnp.int16))
        for k, v in parts.items():
            _WBUF[k].append(v[off:off + n])
        off += n
    if len(_WBUF["ids"]) >= 1000:
        _wager_flush()
'''
    open(pp, "w").write(s)
    log("MotifPredictor patched for the dump")

ip = f"{IET}/maskrcnn_benchmark/engine/inference.py"
s = open(ip).read()
if "WAGER_IMAGE_IDS" not in s:
    a = "            images, targets, image_ids = batch\n"
    mod = "maskrcnn_benchmark.modeling.roi_heads.relation_head.roi_relation_predictors"
    assert s.count(a) == 1
    s = s.replace(a, a + f"            import {mod} as _wp\n"
                  "            _wp.WAGER_IMAGE_IDS = list(image_ids)\n")
    e = "    torch.cuda.empty_cache()\n    return results_dict\n"
    assert s.count(e) == 1
    s = s.replace(e, f"    import {mod} as _wp\n    _wp._wager_flush()\n" + e)
    open(ip, "w").write(s)
    log("inference loop patched")

# ---- run ------------------------------------------------------------------------
pths = sorted(glob.glob(f"{ROOT}/iet_ckpt/**/*.pth", recursive=True), key=os.path.getsize)
assert pths, "no checkpoint .pth"
model_pth = pths[-1]
cfgs = glob.glob(f"{ROOT}/iet_ckpt/**/config.yml", recursive=True)
cfg_file = cfgs[0] if cfgs else f"{IET}/configs/sup-50.yaml"
log(f"checkpoint {model_pth}; config {cfg_file}")
os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/last_checkpoint", "w").write(model_pth)
if not glob.glob(f"{OUT}/inference/*/eval_results.pytorch"):
    cmd = ["python", f"{IET}/tools/relation_test_net.py", "--config-file", cfg_file,
           "MODEL.ROI_RELATION_HEAD.USE_GT_BOX", "True",
           "MODEL.ROI_RELATION_HEAD.USE_GT_OBJECT_LABEL", "True",
           "MODEL.ROI_RELATION_HEAD.PREDICTOR", "MotifPredictor",
           "MODEL.ROI_RELATION_HEAD.PREDICT_USE_BIAS", "True",
           "DATASETS.TEST", '("50VG_stanford_filtered_with_attribute_test",)',
           "TEST.IMS_PER_BATCH", "1", "DTYPE", "float32",
           "GLOVE_DIR", f"{ROOT}/glove",
           "MODEL.PRETRAINED_DETECTOR_CKPT", model_pth,
           "OUTPUT_DIR", OUT]
    env = dict(os.environ, PYTHONPATH=f"{ROOT}/pylib:{IET}", WAGER_DUMP=DUMP)
    p = subprocess.Popen(cmd, cwd=IET, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True)
    tail = []
    for line in p.stdout:
        tail = (tail + [line])[-300:]
        if "SGG eval" in line or "rror" in line or "Loading" in line:
            print(line.rstrip(), flush=True)
    p.wait()
    if p.returncode != 0:
        print("".join(tail[-120:]), flush=True)
        raise SystemExit(f"evaluation failed rc={p.returncode}")
n = len(glob.glob(f"{DUMP}/chunk_*[0-9].npz"))
log(f"dump: {n} chunks")
if n == 0:
    raise SystemExit("no dump written")
log("IETRANS STAGE 2 COMPLETE")
