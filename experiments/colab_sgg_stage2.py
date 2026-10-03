"""SGG audit stage 2 (Colab): one PredCls evaluation of the released causal
MOTIFS-SUM checkpoint with CAUSAL.EFFECT_TYPE TDE, dumping every branch logit.

In PredCls the predictor's logits are, for every ordered object pair,
    baseline  = (vis + ctx(post)) + frq
    TDE       = baseline - ((vis + ctx(avg)) + frq)
and, because object probabilities are exact one-hots, TE equals TDE and NIE is
identically zero. A patched predictor therefore writes vis, ctx(post), ctx(avg),
frq and the returned logits for all pairs of all test images (WAGER_DUMP), so
the baseline, TDE and any branch combination can be scored offline by
colab_sgg_rank.py without further GPU passes. The official evaluator still runs
on TDE, which checks the offline re-scoring.

Archived official values (results/sgg_audit_motifs.json): baseline R@50 0.6612,
mR@50 0.1459; TDE R@50 0.4588, mR@50 0.2476.
"""
import glob
import os
import re
import subprocess
import sys
import time

import numpy as np
import torch

ROOT = "/content"
SGG = f"{ROOT}/sgg"
sys.path.insert(0, f"{ROOT}/pylib")
sys.path.insert(0, SGG)

T0 = time.time()


def log(msg):
    print(f"[stage2 +{time.time()-T0:.0f}s] {msg}", flush=True)


# Idempotent re-assert of the DATA_DIR patch: the upstream paths_catalog hardcodes a
# contributor's absolute path, and every dataset path resolves against it. Applied
# here too so this stage is self-sufficient if stage 1 ran from an older revision.
_pc = f"{SGG}/maskrcnn_benchmark/config/paths_catalog.py"
_s = open(_pc).read()
if f'DATA_DIR = "{SGG}/datasets"' not in _s:
    _s = re.sub(r'^(\s*)DATA_DIR\s*=\s*".*?"',
                lambda m: f'{m.group(1)}DATA_DIR = "{SGG}/datasets"', _s,
                count=1, flags=re.M)
    open(_pc, "w").write(_s)
    log("DATA_DIR repointed")
for _rel in ("vg/VG_100K", "vg/VG-SGG-with-attri.h5",
             "vg/VG-SGG-dicts-with-attri.json", "vg/image_data.json"):
    _p = f"{SGG}/datasets/{_rel}"
    if not os.path.exists(_p):
        raise SystemExit(f"missing dataset path {_p} -- rerun stage 1")
log("dataset paths verified")

# --- torch/numpy API drift since the codebase was written (PyTorch 1.4 era) -------
# Applied tree-wide and idempotently, then verified by actually importing the entry
# point, so an unknown rename fails in seconds instead of after a multi-hour run.
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
_n = 0
for _dir, _sub, _files in os.walk(f"{SGG}/maskrcnn_benchmark"):
    for _fn in _files:
        if not _fn.endswith(".py"):
            continue
        _fp = os.path.join(_dir, _fn)
        _txt = open(_fp, encoding="utf-8", errors="replace").read()
        _new = _txt
        for _pat, _rep in SUBS:
            _new = re.sub(_pat, _rep, _new)
        if _new != _txt:
            open(_fp, "w", encoding="utf-8").write(_new)
            _n += 1
log(f"compat substitutions touched {_n} files")

_probe = subprocess.run(
    ["python", "-c",
     "import sys; sys.path[:0]=['/content/pylib','/content/sgg'];"
     "import tools.relation_test_net as t; print('entry point imports OK')"],
    cwd=SGG, capture_output=True, text=True,
    env=dict(os.environ, PYTHONPATH=f"{ROOT}/pylib:{SGG}"))
print(_probe.stdout.strip() or _probe.stderr[-2500:], flush=True)
if _probe.returncode != 0:
    raise SystemExit("entry point still does not import -- fix before evaluating")


# ---- branch-logit dump (idempotent) ------------------------------------------
_pp = f"{SGG}/maskrcnn_benchmark/modeling/roi_heads/relation_head/roi_relation_predictors.py"
_s = open(_pp).read()
if "# WAGER-DUMP" not in _s:
    _ret = "        return obj_dist_list, rel_dist_list, add_losses\n"
    _i = _s.index(_ret, _s.index("class CausalAnalysisPredictor"))
    _call = ("        # WAGER-DUMP\n"
             "        if WAGER_DUMP and (not self.training):\n"
             "            _wager_record(self, union_features, post_ctx_rep, avg_ctx_rep,\n"
             "                          pair_pred, pair_obj_probs, rel_dists, rel_pair_idxs, num_rels)\n")
    _s = _s[:_i] + _call + _s[_i:]
    _s += '''

# WAGER-DUMP helpers: per-pair branch logits for offline re-scoring.
import os as _wos
import atexit as _watexit
import numpy as _wnp
WAGER_DUMP = _wos.environ.get("WAGER_DUMP", "")
WAGER_IMAGE_IDS = None
_WKEYS = ("pairs", "vis", "ctxp", "ctxa", "frq", "out")
_WBUF = {"ids": [], "n_pairs": [], "chunk": 0, "frq_gap": 0.0,
         **{k: [] for k in _WKEYS}}


def _wager_flush():
    b = _WBUF
    if not b["ids"]:
        return
    _wos.makedirs(WAGER_DUMP, exist_ok=True)
    tmp = f"{WAGER_DUMP}/chunk_{b['chunk']:04d}.tmp.npz"
    _wnp.savez(tmp, image_ids=_wnp.asarray(b["ids"], dtype=_wnp.int64),
               n_pairs=_wnp.asarray(b["n_pairs"], dtype=_wnp.int64),
               frq_gap=_wnp.float64(b["frq_gap"]),
               **{k: _wnp.concatenate(b[k]) for k in _WKEYS})
    _wos.replace(tmp, f"{WAGER_DUMP}/chunk_{b['chunk']:04d}.npz")
    b["chunk"] += 1
    b["ids"], b["n_pairs"] = [], []
    for k in _WKEYS:
        b[k] = []


_watexit.register(_wager_flush)


def _wager_record(pred, union_features, post_ctx_rep, avg_ctx_rep, pair_pred,
                  pair_obj_probs, rel_dists, rel_pair_idxs, num_rels):
    ids = WAGER_IMAGE_IDS
    assert ids is not None and len(ids) == len(num_rels), "image ids not set"
    with torch.no_grad():
        vis = pred.vis_compress(union_features)
        ctxp = pred.ctx_compress(post_ctx_rep)
        ctxa = pred.ctx_compress(avg_ctx_rep)
        frq = pred.freq_bias.index_with_labels(pair_pred.long())
        frqp = pred.freq_bias.index_with_probability(pair_obj_probs)
        _WBUF["frq_gap"] = max(_WBUF["frq_gap"], float((frq - frqp).abs().max()))
        parts = {"vis": vis, "ctxp": ctxp, "ctxa": ctxa, "frq": frq,
                 "out": rel_dists}
        parts = {k: v.float().cpu().numpy().astype(_wnp.float32)
                 for k, v in parts.items()}
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
    open(_pp, "w").write(_s)
    log("predictor patched for branch dump")
_ip = f"{SGG}/maskrcnn_benchmark/engine/inference.py"
_s = open(_ip).read()
if "WAGER_IMAGE_IDS" not in _s:
    _a = "            images, targets, image_ids = batch\n"
    _s = _s.replace(_a, _a + "            import maskrcnn_benchmark.modeling.roi_heads.relation_head."
                    "roi_relation_predictors as _wp\n"
                    "            _wp.WAGER_IMAGE_IDS = list(image_ids)\n", 1)
    _e = "    torch.cuda.empty_cache()\n    return results_dict\n"
    assert _s.count(_e) == 1
    _s = _s.replace(_e, "    import maskrcnn_benchmark.modeling.roi_heads.relation_head."
                    "roi_relation_predictors as _wp\n    _wp._wager_flush()\n" + _e)
    assert "WAGER_IMAGE_IDS" in _s
    open(_ip, "w").write(_s)
    log("inference loop patched to expose image ids")


# ---- locate checkpoint ----
pths = sorted(glob.glob(f"{ROOT}/ckpt/**/*.pth", recursive=True))
if not pths:
    raise SystemExit("no .pth under /content/ckpt")
model_pth = max(pths, key=os.path.getsize)
log(f"model checkpoint: {model_pth} ({os.path.getsize(model_pth)/1e9:.2f} GB)")
ckpt_dir = os.path.dirname(model_pth)
cfg_candidates = glob.glob(f"{ckpt_dir}/*.yml") + glob.glob(f"{ckpt_dir}/*.yaml")
log(f"ckpt dir files: {os.listdir(ckpt_dir)}")

VARIANTS = {"TDE": f"{ROOT}/out_tde"}
DUMP = f"{ROOT}/branch_dump"

for effect, outdir in VARIANTS.items():
    if os.path.exists(f"{outdir}/eval_results.pytorch"):
        log(f"skip {effect} (already evaluated)")
        continue
    os.makedirs(outdir, exist_ok=True)
    with open(f"{outdir}/last_checkpoint", "w") as f:
        f.write(model_pth)
    cmd = [
        "python", f"{SGG}/tools/relation_test_net.py",
        "--config-file", f"{SGG}/configs/e2e_relation_X_101_32_8_FPN_1x.yaml",
        "MODEL.ROI_RELATION_HEAD.USE_GT_BOX", "True",
        "MODEL.ROI_RELATION_HEAD.USE_GT_OBJECT_LABEL", "True",
        "MODEL.ROI_RELATION_HEAD.PREDICTOR", "CausalAnalysisPredictor",
        "MODEL.ROI_RELATION_HEAD.CAUSAL.EFFECT_TYPE", effect,
        "MODEL.ROI_RELATION_HEAD.CAUSAL.FUSION_TYPE", "sum",
        "MODEL.ROI_RELATION_HEAD.CAUSAL.CONTEXT_LAYER", "motifs",
        "TEST.IMS_PER_BATCH", "1",
        "DTYPE", "float32",
        "GLOVE_DIR", f"{ROOT}/glove",
        "MODEL.PRETRAINED_DETECTOR_CKPT", model_pth,
        "OUTPUT_DIR", outdir,
    ]
    log(f"=== evaluating EFFECT_TYPE={effect} ===")
    env = dict(os.environ, PYTHONPATH=f"{ROOT}/pylib:{SGG}", WAGER_DUMP=DUMP)
    p = subprocess.Popen(cmd, cwd=SGG, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True)
    tail = []
    for line in p.stdout:
        tail.append(line)
        if len(tail) > 400:
            tail.pop(0)
        low = line.lower()
        if ("r @" in low or "recall" in low or "error" in low or "@ 50" in low
                or "loading" in low and len(tail) % 50 == 0):
            print(line.rstrip(), flush=True)
        with open(f"{ROOT}/progress_sgg_{effect}.txt", "w") as pf:
            pf.write(line)
    p.wait()
    if p.returncode != 0:
        print("".join(tail[-120:]), flush=True)
        raise SystemExit(f"eval {effect} failed rc={p.returncode}")
    log(f"eval {effect} done")

n_chunks = len(glob.glob(f"{DUMP}/chunk_*.npz"))
log(f"branch dump: {n_chunks} chunk files in {DUMP}")
if n_chunks == 0:
    raise SystemExit("no branch dump written")
log("STAGE 2 COMPLETE")
