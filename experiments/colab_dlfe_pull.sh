#!/bin/bash
# Mirror finished DLFE outputs from the Colab VM into data/vg_motifs/wager_dlfe_raw;
# exits when the chain ends or fails, or the session is lost.
export PATH="$HOME/.local/bin:$PATH"; W=$(cd "$(dirname "$0")/.." && pwd)/data/vg_motifs/wager_dlfe_raw; cd /tmp
S=${SESSION:-dlfe}
for i in $(seq 1 ${POLLS:-200}); do
  out=$(echo 'import glob,os;print("P"," ".join(sorted(glob.glob("/content/wager_dlfe_raw/*/*"))));t=open("/content/chain.log").read() if os.path.exists("/content/chain.log") else "";print("C",t.strip().splitlines()[-1] if t.strip() else "-");p=sorted(glob.glob("/content/progress_*.txt"));print("G",[open(x).read().strip()[-60:] for x in p][-1:] )' | timeout 110 colab --auth oauth2 exec -s $S 2>&1)
  if echo "$out" | grep -q "not found\|appears to be lost\|No active"; then echo "$(date +%H:%M) SESSION LOST"; exit 2; fi
  for f in $(echo "$out" | grep "^P" | cut -c3-); do
    m=$(basename $(dirname $f)); mkdir -p $W/$m
    [ -f $W/$m/$(basename $f) ] || colab --auth oauth2 download -s $S $f $W/$m/$(basename $f) >/dev/null 2>&1
  done
  c=$(echo "$out" | grep "^C" | cut -c3-); g=$(echo "$out" | grep "^G" | cut -c3-)
  echo "$(date +%H:%M) $c | $g | local: $(ls $W/*/ 2>/dev/null | tr '\n' ' ')"
  echo "$c" | grep -q "CHAIN COMPLETE\|failed\|incomplete" && exit 0
  sleep ${SLEEP:-180}
done
