#!/bin/bash
# Waterbirds CLIP features on a Colab T4; tries all signed-in accounts.
export PATH="$HOME/.local/bin:$PATH"; D=~/.config/colab-cli; R=/home/user/WAGER/experiments
cd /tmp; SESSION=${SESSION:-wb}
for i in $(seq 1 ${TRIES:-10}); do
  for acct in 1 2 3; do
    cp $D/token.account$acct.json $D/token.json
    r=$(timeout 300 colab --auth oauth2 new -s $SESSION --gpu T4 2>&1 | tail -1)
    if echo "$r" | grep -q READY; then
      echo "$(date -u +%H:%M) T4 granted on account $acct"
      colab --auth oauth2 upload -s $SESSION $R/colab_waterbirds_features.py /content/colab_waterbirds_features.py >/dev/null 2>&1
      echo 'import subprocess; subprocess.Popen("cd /content && setsid nohup python -u colab_waterbirds_features.py > /content/wb.log 2>&1 &", shell=True); print("LAUNCHED")' \
        | timeout 110 colab --auth oauth2 exec -s $SESSION 2>&1 | grep LAUNCHED
      exit 0
    fi
  done
  echo "$(date -u +%H:%M) no T4 yet"; sleep 600
done
exit 1
