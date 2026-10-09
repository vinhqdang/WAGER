#!/bin/bash
# Zero-shot CLIP ViT-L/14 with a prompt ensemble on a Colab T4; tries both accounts.
export PATH="$HOME/.local/bin:$PATH"; D=~/.config/colab-cli; R=/home/user/WAGER/experiments; W=/home/user/WAGER/data/vg_motifs/wager_sgg
cd /tmp; SESSION=${SESSION:-zsL}
for i in $(seq 1 ${TRIES:-10}); do
  for acct in 1 2; do
    cp $D/token.account$acct.json $D/token.json
    r=$(timeout 300 colab --auth oauth2 new -s $SESSION --gpu T4 2>&1 | tail -1)
    if echo "$r" | grep -q READY; then
      echo "$(date -u +%H:%M) T4 granted on account $acct"
      colab --auth oauth2 upload -s $SESSION $R/colab_clip_zeroshot.py /content/colab_clip_zeroshot.py >/dev/null 2>&1
      colab --auth oauth2 upload -s $SESSION $R/colab_vg_test_images.py /content/colab_vg_test_images.py >/dev/null 2>&1
      colab --auth oauth2 upload -s $SESSION $W/meta.npz /content/meta.npz >/dev/null 2>&1
      colab --auth oauth2 upload -s $SESSION $W/predicate_names.json /content/predicate_names.json >/dev/null 2>&1
      echo 'import subprocess; subprocess.Popen("cd /content && WAGER_CLIP_MODEL=ViT-L-14 WAGER_CLIP_PRETRAINED=openai WAGER_PROMPTS=ensemble WAGER_ZS_OUT=variant_clip_zs_L.npz setsid nohup python -u colab_clip_zeroshot.py > /content/zs.log 2>&1 &", shell=True); print("LAUNCHED")' \
        | timeout 110 colab --auth oauth2 exec -s $SESSION 2>&1 | grep LAUNCHED
      exit 0
    fi
  done
  echo "$(date -u +%H:%M) no T4 yet"; sleep 600
done
exit 1
