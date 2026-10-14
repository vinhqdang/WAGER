#!/bin/bash
# PE-Net audit on one Colab VM, end to end and resumable: stage 1 (data, code,
# checkpoint), stage 2 (one official PredCls evaluation with the score dump), then the
# per-relation re-scoring of the dump (colab_sgg_rank.py, mode penet: rel_nms path).
# Progress lines go to /content/chain.log; the mirror script polls that file.
cd /content
python -u colab_penet_stage1.py > /content/stage1.log 2>&1 || { echo "stage1 failed" >> chain.log; exit 1; }
grep -q "PENET STAGE 1 COMPLETE" stage1.log || { echo "stage1 incomplete" >> chain.log; exit 1; }
echo "$(date +%H:%M) stage1 done" >> chain.log
# The shipped rel_nms builds an N x N x 51 array per image and runs out of memory on dense
# images; use the identical row-blocked version (penet_rel_nms_chunked.py) in both the
# evaluator and the re-scoring.
F=/content/penet/maskrcnn_benchmark/data/datasets/evaluation/vg/sgg_eval.py
grep -q "^rel_nms = rel_nms_chunked" $F || { cat /content/penet_rel_nms_chunked.py >> $F; echo "rel_nms = rel_nms_chunked" >> $F; }
python -u colab_penet_stage2.py > /content/stage2.log 2>&1 || { echo "stage2 failed" >> chain.log; exit 1; }
grep -q "PENET STAGE 2 COMPLETE" stage2.log || { echo "stage2 incomplete" >> chain.log; exit 1; }
echo "$(date +%H:%M) stage2 done" >> chain.log
if [ ! -f /content/wager_penet_raw/penet/summary.json ]; then
  WAGER_RANK_MODE=penet python -u colab_sgg_rank.py > /content/rank_penet.log 2>&1 || { echo "rank failed" >> chain.log; exit 1; }
  grep -q "RANK COMPLETE" rank_penet.log || { echo "rank incomplete" >> chain.log; exit 1; }
fi
cp /content/out_penet_predcls/official_penet.json /content/wager_penet_raw/penet/ 2>/dev/null
cp /content/eval_penet.log /content/wager_penet_raw/penet/ 2>/dev/null
echo "$(date +%H:%M) rank done" >> chain.log
echo "CHAIN COMPLETE" >> chain.log
