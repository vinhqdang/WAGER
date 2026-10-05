#!/bin/bash
cd /content
WAGER_EXTRA_CKPTS=sgcls,sgdet WAGER_SKIP_PREDCLS=1 WAGER_TEST_IMAGES_ONLY=1 python -u colab_sgg_stage1.py > /content/s1.log 2>&1 || { echo "stage1 failed" >> /content/chain.log; exit 1; }
grep -q "STAGE 1 COMPLETE" /content/s1.log || { echo "stage1 incomplete" >> /content/chain.log; exit 1; }
echo "$(date +%H:%M) stage1 done" >> /content/chain.log
bash /content/det_chain.sh
