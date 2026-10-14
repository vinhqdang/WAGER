#!/bin/bash
# Get a Colab T4 on any of the stored accounts (retrying every 10 min), upload the
# PE-Net audit scripts and start the chain detached. SESSION names the session.
export PATH="$HOME/.local/bin:$PATH"; D=~/.config/colab-cli; R=$(cd "$(dirname "$0")" && pwd); cd /tmp
SESSION=${SESSION:-penet}
for i in $(seq 1 ${TRIES:-12}); do
  for acct in ${ACCOUNTS:-1 2 3}; do
    cp $D/token.account$acct.json $D/token.json
    r=$(timeout 300 colab --auth oauth2 new -s $SESSION --gpu T4 2>&1 | tail -1)
    if echo "$r" | grep -q READY; then
      echo "$(date -u +%H:%M) T4 granted on account $acct"
      for f in colab_penet_stage1.py colab_penet_stage2.py colab_sgg_rank.py colab_vg_test_images.py penet_rel_nms_chunked.py; do
        colab --auth oauth2 upload -s $SESSION $R/$f /content/$f >/dev/null 2>&1
      done
      colab --auth oauth2 upload -s $SESSION $R/colab_penet_chain.sh /content/penet_chain.sh >/dev/null 2>&1
      echo 'import subprocess; subprocess.Popen("cd /content && setsid nohup bash penet_chain.sh > /content/chain.out 2>&1 &", shell=True); print("LAUNCHED")' \
        | timeout 110 colab --auth oauth2 exec -s $SESSION 2>&1 | grep LAUNCHED
      exit 0
    fi
  done
  echo "$(date -u +%H:%M) no T4 yet"; sleep 600
done
exit 1
