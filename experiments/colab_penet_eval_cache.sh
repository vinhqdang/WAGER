#!/bin/bash
# PE-Net after an evaluator out-of-memory kill during stage 2 (the inference and the
# score dump had completed; eval_results.pytorch was saved). Steps, sequential to bound
# memory:
#   1. colab_sgg_rank.py (mode penet) on the saved dump and eval_results;
#   2. the official evaluator again, in cache mode (TEST.ALLOW_LOAD_FROM_CACHE True:
#      predictions come from eval_results.pytorch, no second model pass), which prints
#      the SGG eval lines and writes result_dict.pytorch;
#   3. official_penet.json from the printed lines, as colab_penet_stage2.py does.
# rel_nms is the memory-equivalent override appended to sgg_eval.py (penet_rel_nms_chunked.py).
cd /content
WAGER_RANK_MODE=penet python -u colab_sgg_rank.py > /content/rank_penet.log 2>&1 || { echo "rank failed" >> chain.log; exit 1; }
grep -q "RANK COMPLETE" rank_penet.log || { echo "rank incomplete" >> chain.log; exit 1; }
echo "$(date +%H:%M) rank done" >> chain.log
cd /content/penet
PYTHONPATH=/content/pylib:/content/penet python -u tools/relation_test_net.py \
  --config-file configs/e2e_relation_X_101_32_8_FPN_1x.yaml \
  MODEL.ROI_RELATION_HEAD.USE_GT_BOX True MODEL.ROI_RELATION_HEAD.USE_GT_OBJECT_LABEL True \
  MODEL.ROI_RELATION_HEAD.PREDICTOR PrototypeEmbeddingNetwork TEST.IMS_PER_BATCH 1 DTYPE float32 \
  GLOVE_DIR /content/glove MODEL.WEIGHT /content/penet_ckpt/pred_cls_model_final.pth \
  OUTPUT_DIR /content/out_penet_predcls TEST.ALLOW_LOAD_FROM_CACHE True \
  > /content/eval_penet_cache.log 2>&1 || { echo "evaluator failed" >> /content/chain.log; exit 1; }
cd /content
grep -q "SGG eval" eval_penet_cache.log || { echo "evaluator printed nothing" >> chain.log; exit 1; }
python - <<'PY'
import json, re
lines = [l.strip() for l in open("/content/eval_penet_cache.log", errors="replace") if "SGG eval" in l]
vals = {}
for ln in lines:
    m = re.search(r"SGG eval:\s*(.*?);\s+for mode=predcls, type=(.*?)\.?$", ln)
    if m:
        for tag, K, v in re.findall(r"([A-Za-z\-]+) @ (\d+): ([\d.]+)", m.group(1)):
            vals[f"{tag}@{K}"] = float(v)
json.dump({"model": "penet", "checkpoint": "/content/penet_ckpt/pred_cls_model_final.pth",
           "printed": lines, "values": vals, "note": "evaluator re-run in cache mode after an OOM kill"},
          open("/content/out_penet_predcls/official_penet.json", "w"), indent=1)
print({k: v for k, v in vals.items() if k in ("R@20","R@50","R@100","mR@50","ng-R@50","ng-mR@50")})
PY
cp /content/out_penet_predcls/official_penet.json /content/wager_penet_raw/penet/ 2>/dev/null
cp /content/eval_penet_cache.log /content/wager_penet_raw/penet/ 2>/dev/null
echo "$(date +%H:%M) evaluator done" >> chain.log
echo "CHAIN COMPLETE" >> chain.log
