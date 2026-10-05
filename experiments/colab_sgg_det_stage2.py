"""SGG audit beyond PredCls (Colab): one TDE pass of the released causal MOTIFS-SUM
SGCls or SGDet checkpoint, replayed inline by colab_sgg_inline.py.

Environment:
  WAGER_PROTO     sgcls | sgdet
  WAGER_RANGE     a:b   test images [a, b) of the codebase's test list (resumable chunks)
  WAGER_VALIDATE  1     also keep predictions and run the codebase's own evaluator on
                        the range, so the inline replay can be checked against it
                        (use a short range: the evaluator holds every prediction)

Under SUM fusion the predictor's logits are, for every candidate object pair,
    baseline = vis + ctx(post) + frq(predicted labels)
    TDE      = (vis + ctx(post) + frq(probs)) - (vis + ctx(avg) + frq(probs))
             = ctx(post) - ctx(avg)
so one TDE pass yields the baseline as well; the object predictions (boxes, labels,
scores) are the factual ones and are shared by both models. Requires stage 1 to have
fetched and extracted the protocol's checkpoint to /content/ckpt_<proto>.

Released numbers (Scene-Graph-Benchmark.pytorch README, this checkpoint):
  SGCls  none R@50 39.25 mR@50 8.02 | TDE R@50 26.31 mR@50 13.21
  SGDet  none R@50 32.45 mR@50 5.83 | TDE R@50 16.56 mR@50 8.94
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = "/content"
SGG = f"{ROOT}/sgg"
PROTO = os.environ["WAGER_PROTO"]
A, B = (int(x) for x in os.environ["WAGER_RANGE"].split(":"))
VALIDATE = os.environ.get("WAGER_VALIDATE", "") == "1"
T0 = time.time()


def log(msg):
    print(f"[det-{PROTO} +{time.time()-T0:.0f}s] {msg}", flush=True)


# ---- compat substitutions (as in colab_sgg_stage2.py) ------------------------
SUBS = [
    (r"\b_download_url_to_file\b", "download_url_to_file"),
    (r"torch\._six\.PY3", "True"),
    (r"from torch\._six import string_classes", "string_classes = str"),
    (r"from torch\._six import int_classes", "int_classes = int"),
    (r"torch\._six\.string_classes", "str"),
    (r"torch\._six\.int_classes", "int"),
    (r"np\.float\b(?!\d|_)", "float"),
    (r"np\.bool\b(?!\d|_)", "bool"),
    (r"np\.int\b(?!\d|_|e)", "int"),
    (r"np\.object\b(?!\d|_)", "object"),
    (r"from collections import Iterable", "from collections.abc import Iterable"),
    (r"from collections import Sequence", "from collections.abc import Sequence"),
]
for _dir, _sub, _files in os.walk(f"{SGG}/maskrcnn_benchmark"):
    for _fn in _files:
        if _fn.endswith(".py"):
            _fp = os.path.join(_dir, _fn)
            _txt = open(_fp, encoding="utf-8", errors="replace").read()
            _new = _txt
            for _pat, _rep in SUBS:
                _new = re.sub(_pat, _rep, _new)
            if _new != _txt:
                open(_fp, "w", encoding="utf-8").write(_new)

shutil.copy(f"{ROOT}/colab_sgg_inline.py", f"{SGG}/wager_inline.py")

# ---- predictor: keep the current batch's branch logits ------------------------
_pp = f"{SGG}/maskrcnn_benchmark/modeling/roi_heads/relation_head/roi_relation_predictors.py"
_s = open(_pp).read()
if "# WAGER-LAST" not in _s:
    _ret = "        return obj_dist_list, rel_dist_list, add_losses\n"
    _i = _s.index(_ret, _s.index("class CausalAnalysisPredictor"))
    _call = ("        # WAGER-LAST\n"
             "        if not self.training:\n"
             "            _wager_keep(self, union_features, post_ctx_rep, avg_ctx_rep,\n"
             "                        pair_pred, rel_dists, rel_pair_idxs, num_rels)\n")
    _s = _s[:_i] + _call + _s[_i:]
    _s += '''

# WAGER-LAST: branch logits of the current batch, read by wager_inline.process
import numpy as _wnp
WAGER_LAST = []


def _wager_keep(pred, union_features, post_ctx_rep, avg_ctx_rep, pair_pred, rel_dists,
                rel_pair_idxs, num_rels):
    assert pred.fusion_type == "sum"
    with torch.no_grad():
        parts = {"vis": pred.vis_compress(union_features),
                 "ctxp": pred.ctx_compress(post_ctx_rep),
                 "ctxa": pred.ctx_compress(avg_ctx_rep),
                 "frq": pred.freq_bias.index_with_labels(pair_pred.long()),
                 "out": rel_dists}
        parts = {k: v.float().cpu().numpy() for k, v in parts.items()}
    WAGER_LAST.clear()
    off = 0
    for n, pidx in zip(num_rels, rel_pair_idxs):
        d = {k: v[off:off + n] for k, v in parts.items()}
        d["pairs"] = pidx.cpu().numpy()
        WAGER_LAST.append(d)
        off += n
'''
    open(_pp, "w").write(_s)
    log("predictor patched")

# ---- inference loop: inline replay, keep nothing unless validating -------------
_ip = f"{SGG}/maskrcnn_benchmark/engine/inference.py"
_s = open(_ip).read()
if "wager_inline" not in _s:
    _a = "            output = [o.to(cpu_device) for o in output]\n"
    assert _s.count(_a) == 1
    _s = _s.replace(_a, _a + (
        "            import wager_inline as _wi\n"
        "            import maskrcnn_benchmark.modeling.roi_heads.relation_head.roi_relation_predictors as _wp\n"
        "            for _k, (_iid, _o) in enumerate(zip(image_ids, output)):\n"
        "                _wi.process(data_loader.dataset, _iid, _o, _wp.WAGER_LAST[_k])\n"
        "            if os.environ.get('WAGER_VALIDATE', '') != '1':\n"
        "                output = [None for _ in output]\n"), 1)
    _e = "    torch.cuda.empty_cache()\n    return results_dict\n"
    assert _s.count(_e) == 1
    _s = _s.replace(_e, "    import wager_inline as _wi\n    _wi.flush()\n" + _e)
    _c = "    if not load_prediction_from_cache:\n        predictions = _accumulate"
    assert _s.count(_c) == 1
    _s = _s.replace(_c, "    if os.environ.get('WAGER_VALIDATE', '') != '1':\n"
                        "        return -1.0\n" + _c)
    open(_ip, "w").write(_s)
    log("inference loop patched")

# ---- dataset: restrict the test list to WAGER_RANGE --------------------------
_dp = f"{SGG}/maskrcnn_benchmark/data/datasets/visual_genome.py"
_s = open(_dp).read()
if "WAGER_RANGE" not in _s:
    _a = "            self.img_info = [self.img_info[i] for i in np.where(self.split_mask)[0]]\n"
    assert _s.count(_a) == 1
    _s = _s.replace(_a, _a + (
        "            if self.split == 'test' and os.environ.get('WAGER_RANGE'):\n"
        "                _a, _b = (int(x) for x in os.environ['WAGER_RANGE'].split(':'))\n"
        "                self.filenames, self.img_info = self.filenames[_a:_b], self.img_info[_a:_b]\n"
        "                self.gt_boxes, self.gt_classes = self.gt_boxes[_a:_b], self.gt_classes[_a:_b]\n"
        "                self.gt_attributes = self.gt_attributes[_a:_b]\n"
        "                self.relationships = self.relationships[_a:_b]\n"), 1)
    if "\nimport os\n" not in _s:
        _s = "import os\n" + _s
    open(_dp, "w").write(_s)
    log("dataset patched for image ranges")

# ---- training predicate prior for the logit-adjusted control -------------------
import h5py  # noqa: E402
import numpy as np  # noqa: E402
with h5py.File(f"{SGG}/datasets/vg/VG-SGG-with-attri.h5", "r") as f5:
    split = f5["split"][:]
    first, last = f5["img_to_first_rel"][:], f5["img_to_last_rel"][:]
    preds_all = f5["predicates"][:, 0]
cnt = np.zeros(51, dtype=np.int64)
for i in np.flatnonzero((split == 0) & (first >= 0)):
    np.add.at(cnt, preds_all[first[i]:last[i] + 1], 1)
np.save(f"{ROOT}/train_predicate_counts.npy", cnt)
_s = open(f"{SGG}/wager_inline.py").read()
if "_wager_prior_loaded" not in _s:
    _s += ("\n_wager_prior_loaded = True\n"
           f"set_log_prior(np.load('{ROOT}/train_predicate_counts.npy'))\n")
    open(f"{SGG}/wager_inline.py", "w").write(_s)

# ---- run --------------------------------------------------------------------
pths = sorted(glob.glob(f"{ROOT}/ckpt_{PROTO}/**/*.pth", recursive=True))
model_pth = max(pths, key=os.path.getsize)
log(f"checkpoint {model_pth} ({os.path.getsize(model_pth)/1e9:.2f} GB); range {A}:{B}"
    + (" [validate]" if VALIDATE else ""))
outdir = f"{ROOT}/out_{PROTO}_{A}_{B}"
inline = f"{ROOT}/inline_{PROTO}"
os.makedirs(outdir, exist_ok=True)
open(f"{outdir}/last_checkpoint", "w").write(model_pth)
cmd = ["python", f"{SGG}/tools/relation_test_net.py",
       "--config-file", f"{SGG}/configs/e2e_relation_X_101_32_8_FPN_1x.yaml",
       "MODEL.ROI_RELATION_HEAD.USE_GT_BOX", "True" if PROTO == "sgcls" else "False",
       "MODEL.ROI_RELATION_HEAD.USE_GT_OBJECT_LABEL", "False",
       "MODEL.ROI_RELATION_HEAD.PREDICTOR", "CausalAnalysisPredictor",
       "MODEL.ROI_RELATION_HEAD.CAUSAL.EFFECT_TYPE", "TDE",
       "MODEL.ROI_RELATION_HEAD.CAUSAL.FUSION_TYPE", "sum",
       "MODEL.ROI_RELATION_HEAD.CAUSAL.CONTEXT_LAYER", "motifs",
       "TEST.IMS_PER_BATCH", "1", "DTYPE", "float32",
       "GLOVE_DIR", f"{ROOT}/glove",
       "MODEL.PRETRAINED_DETECTOR_CKPT", model_pth, "OUTPUT_DIR", outdir]
env = dict(os.environ, PYTHONPATH=f"{ROOT}/pylib:{SGG}", WAGER_INLINE=inline,
           WAGER_OFFSET=str(A))
p = subprocess.Popen(cmd, cwd=SGG, env=env, stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT, text=True)
tail = []
for line in p.stdout:
    tail.append(line)
    tail = tail[-300:]
    low = line.lower()
    if "recall" in low or "error" in low or "traceback" in low or "%|" in line and "00/" in line:
        print(line.rstrip()[-200:], flush=True)
p.wait()
if p.returncode != 0:
    print("".join(tail[-120:]), flush=True)
    raise SystemExit(f"run failed rc={p.returncode}")
parts = sorted(glob.glob(f"{inline}/part_*.npz"))
log(f"{len(parts)} inline parts in {inline}")
log(f"DET RANGE COMPLETE {PROTO} {A}:{B}")
