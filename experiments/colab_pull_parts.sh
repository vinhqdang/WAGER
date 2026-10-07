#!/bin/bash
# Mirror finished inline parts from the Colab VM; exit on chain end/failure or session loss.
export PATH="$HOME/.local/bin:$PATH"; cd /tmp; WAGER_ROOT=/home/user/WAGER
for i in $(seq 1 70); do
  out=$(echo 'import glob,os;print("P"," ".join(sorted(glob.glob("/content/inline_sg*/part_*.npz"))));t=open("/content/chain.log").read() if os.path.exists("/content/chain.log") else "";print("C",t.strip().splitlines()[-1] if t.strip() else "-")' | timeout 110 colab --auth oauth2 exec -s ${SESSION:-det2} 2>&1)
  if echo "$out" | grep -q "not found\|appears to be lost"; then echo "$(date +%H:%M) SESSION LOST"; exit 2; fi
  for f in $(echo "$out" | grep "^P" | cut -c3-); do
    proto=$(echo $f | sed 's#.*/inline_\(sg[a-z]*\)/.*#\1#'); d=/home/user/WAGER/data/vg_motifs/wager_$proto/parts; mkdir -p $d
    [ -f $d/$(basename $f) ] || colab --auth oauth2 download -s ${SESSION:-det2} $f $d/$(basename $f) >/dev/null 2>&1
  done
  if [ -n "${PUSH_BRANCH:-}" ]; then   # optional: checkpoint each mirrored part to a branch
    git -C "$WAGER_ROOT" add -f "$WAGER_ROOT"/data/vg_motifs/wager_sg*/parts >/dev/null 2>&1
    if ! git -C "$WAGER_ROOT" diff --cached --quiet; then
      git -C "$WAGER_ROOT" commit -qm "SGG inline-replay parts (partial run)" && \
        git -C "$WAGER_ROOT" push -q origin HEAD:"$PUSH_BRANCH" >/dev/null 2>&1
    fi
  fi
  c=$(echo "$out" | grep "^C" | cut -c3-)
  echo "$(date +%H:%M) $c | local sgcls $(ls /home/user/WAGER/data/vg_motifs/wager_sgcls/parts 2>/dev/null | wc -l) sgdet $(ls /home/user/WAGER/data/vg_motifs/wager_sgdet/parts 2>/dev/null | wc -l)"
  echo "$c" | grep -q "CHAIN COMPLETE\|failed\|incomplete" && exit 0
  sleep 90
done
