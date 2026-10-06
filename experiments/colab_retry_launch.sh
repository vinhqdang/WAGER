#!/bin/bash
# Retry a Colab T4 on either account every 10 min; on success upload and launch the SGDet resume.
export PATH="$HOME/.local/bin:$PATH"; D=~/.config/colab-cli; R=/home/user/WAGER/experiments; cd /tmp
SESSION=${SESSION:-det4}
START=${START:-4000}
for i in $(seq 1 ${TRIES:-11}); do
  for acct in 1 2; do
    cp $D/token.account$acct.json $D/token.json
    r=$(timeout 300 colab --auth oauth2 new -s $SESSION --gpu T4 2>&1 | tail -1)
    if echo "$r" | grep -q READY; then
      echo "$(date -u +%H:%M) T4 granted on account $acct"
      for f in colab_sgg_stage1.py colab_sgg_det_stage2.py colab_sgg_inline.py colab_vg_test_images.py; do
        colab --auth oauth2 upload -s $SESSION $R/$f /content/$f >/dev/null 2>&1
      done
      colab --auth oauth2 upload -s $SESSION $R/colab_det_chain.sh /content/det_chain.sh >/dev/null 2>&1
      colab --auth oauth2 upload -s $SESSION $R/colab_det_all_resume.sh /content/det_all.sh >/dev/null 2>&1
      echo 'import subprocess; subprocess.Popen("cd /content && START='"$START"' setsid nohup bash det_all.sh > /content/all.out 2>&1 &", shell=True); print("LAUNCHED")' \
        | timeout 110 colab --auth oauth2 exec -s $SESSION 2>&1 | grep LAUNCHED
      exit 0
    fi
  done
  echo "$(date -u +%H:%M) no T4 yet"
  sleep 600
done
exit 1
