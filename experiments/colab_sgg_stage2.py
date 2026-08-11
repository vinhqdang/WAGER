"""SGG audit stage 2 (Colab): run PredCls evaluation for MOTIFS-SUM baseline
(CAUSAL.EFFECT_TYPE none) and MOTIFS-TDE from the single causal checkpoint,
then convert each eval_results.pytorch into a compact npz of per-relation
51-way softmax vectors with alignment identifiers.

Sanity targets from the paper (Tang et al. 2020): baseline R@50 ~ 65,
TDE mR@50 ~ 25-26. Prints R@K lines from the eval log.
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


# ---- locate checkpoint ----
pths = sorted(glob.glob(f"{ROOT}/ckpt/**/*.pth", recursive=True))
if not pths:
    raise SystemExit("no .pth under /content/ckpt")
model_pth = max(pths, key=os.path.getsize)
log(f"model checkpoint: {model_pth} ({os.path.getsize(model_pth)/1e9:.2f} GB)")
ckpt_dir = os.path.dirname(model_pth)
cfg_candidates = glob.glob(f"{ckpt_dir}/*.yml") + glob.glob(f"{ckpt_dir}/*.yaml")
log(f"ckpt dir files: {os.listdir(ckpt_dir)}")

VARIANTS = {"none": f"{ROOT}/out_none", "TDE": f"{ROOT}/out_tde"}

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
    env = dict(os.environ, PYTHONPATH=f"{ROOT}/pylib:{SGG}")
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

# ---- convert dumps to compact npz ----
for effect, outdir in VARIANTS.items():
    dst = f"{ROOT}/motifs_{effect}_predcls.npz"
    if os.path.exists(dst):
        continue
    log(f"converting {outdir}/eval_results.pytorch")
    d = torch.load(f"{outdir}/eval_results.pytorch", map_location="cpu")
    gts, preds = d["groundtruths"], d["predictions"]
    log(f"{len(gts)} images; gt fields: {gts[0].fields()}; "
        f"pred fields: {preds[0].fields()}; gt size {gts[0].size}, "
        f"pred size {preds[0].size}")
    rows_img, rows_sb, rows_ob, rows_sc, rows_oc, rows_y, rows_q = \
        [], [], [], [], [], [], []
    rows_wh = []
    n_miss = 0
    for i, (gt, pr) in enumerate(zip(gts, preds)):
        rel = gt.get_field("relation_tuple").numpy()      # (m, 3) sub, ob, pred
        labels = gt.get_field("labels").numpy()
        boxes = gt.bbox.numpy()
        w, h = gt.size
        pair_idx = pr.get_field("rel_pair_idxs").numpy()  # (M, 2)
        scores = pr.get_field("pred_rel_scores").numpy()  # (M, 51)
        lut = {(int(a), int(b)): k for k, (a, b) in enumerate(pair_idx)}
        for s, o, y in rel:
            k = lut.get((int(s), int(o)))
            if k is None:
                n_miss += 1
                continue
            rows_img.append(i)
            rows_sb.append(boxes[int(s)])
            rows_ob.append(boxes[int(o)])
            rows_sc.append(labels[int(s)])
            rows_oc.append(labels[int(o)])
            rows_y.append(int(y))
            rows_q.append(scores[k])
            rows_wh.append((w, h))
        if i % 5000 == 0:
            log(f"  {i} images converted")
    np.savez_compressed(
        dst,
        img_wh=np.asarray(rows_wh, dtype=np.float32),
        image_index=np.asarray(rows_img, dtype=np.int32),
        sbox=np.asarray(rows_sb, dtype=np.float32),
        obox=np.asarray(rows_ob, dtype=np.float32),
        subj=np.asarray(rows_sc, dtype=np.int32),
        obj=np.asarray(rows_oc, dtype=np.int32),
        pred=np.asarray(rows_y, dtype=np.int32),
        probs=np.asarray(rows_q, dtype=np.float32),
        n_missing_pairs=n_miss,
    )
    log(f"wrote {dst}: {len(rows_y)} relations, {n_miss} unmatched")
    rd_path = f"{outdir}/result_dict.pytorch"
    if os.path.exists(rd_path):
        rd = torch.load(rd_path, map_location="cpu")
        summary = {}
        for k, v in rd.items():
            try:
                summary[k] = {kk: float(np.mean(vv)) for kk, vv in v.items()}
            except Exception:
                pass
        import json
        with open(f"{ROOT}/motifs_{effect}_recalls.json", "w") as f:
            json.dump(summary, f, indent=2)
        log(f"recall summary keys: {list(summary.keys())[:8]}")

log("STAGE 2 COMPLETE")
