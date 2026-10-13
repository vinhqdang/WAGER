#!/bin/bash
# DLFE audit on one Colab VM, end to end and resumable: stage 1 (data, code,
# checkpoints), stage 2 (one official PredCls evaluation per checkpoint with the
# score dump), then the per-relation re-scoring of each dump (colab_sgg_rank.py).
# Progress lines go to /content/chain.log; the mirror script polls that file.
cd /content
python -u colab_dlfe_stage1.py > /content/stage1.log 2>&1 || { echo "stage1 failed" >> chain.log; exit 1; }
grep -q "DLFE STAGE 1 COMPLETE" stage1.log || { echo "stage1 incomplete" >> chain.log; exit 1; }
echo "$(date +%H:%M) stage1 done" >> chain.log
for M in ${MODELS:-dlfe base}; do
  WAGER_DLFE_MODELS=$M python -u colab_dlfe_stage2.py > /content/stage2_$M.log 2>&1 || { echo "stage2 $M failed" >> chain.log; exit 1; }
  grep -q "DLFE STAGE 2 COMPLETE" stage2_$M.log || { echo "stage2 $M incomplete" >> chain.log; exit 1; }
  echo "$(date +%H:%M) stage2 $M done" >> chain.log
  MODE=$([ "$M" = base ] && echo dlfe_base || echo dlfe)
  if [ ! -f /content/wager_dlfe_raw/$M/summary.json ]; then
    WAGER_RANK_MODE=$MODE python -u colab_sgg_rank.py > /content/rank_$M.log 2>&1 || { echo "rank $M failed" >> chain.log; exit 1; }
    grep -q "RANK COMPLETE" rank_$M.log || { echo "rank $M incomplete" >> chain.log; exit 1; }
  fi
  cp /content/out_${M}_predcls/official_$M.json /content/wager_dlfe_raw/$M/ 2>/dev/null
  cp /content/eval_$M.log /content/wager_dlfe_raw/$M/ 2>/dev/null
  echo "$(date +%H:%M) rank $M done" >> chain.log
done
echo "CHAIN COMPLETE" >> chain.log
