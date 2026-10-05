#!/bin/bash
# Full SGCls then SGDet runs in resumable 2,000-image chunks.
cd /content
for P in ${PROTOS:-sgcls sgdet}; do
  [ -d inline_${P} ] && [ ! -d inline_${P}_val ] && mv inline_${P} inline_${P}_val
  for A in $(seq ${START:-0} 2000 26446); do
    B=$((A+2000)); [ $B -gt 26446 ] && B=26446
    M=/content/done_${P}_${A}_${B}
    [ -f $M ] && continue
    WAGER_PROTO=$P WAGER_RANGE=$A:$B python -u colab_sgg_det_stage2.py > /content/run_${P}_${A}.log 2>&1 \
      && grep -q "DET RANGE COMPLETE" /content/run_${P}_${A}.log && touch $M \
      || { echo "chunk $P $A failed" >> /content/chain.log; exit 1; }
    echo "$(date +%H:%M) done $P $A:$B" >> /content/chain.log
  done
done
echo "CHAIN COMPLETE" >> /content/chain.log
