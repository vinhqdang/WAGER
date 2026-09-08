#!/usr/bin/env bash
# Build the manuscript and the supplementary together.
#
# The two are separate documents that cite each other, so the loop below alternates
# LaTeX passes with experiments/gen_cross_refs.py, which turns each document's .aux
# into a lookup table the other one \input's.  Three rounds are enough for the numbers
# to settle: pass 1 produces the .aux files, pass 2 consumes them, pass 3 stabilises
# page and reference numbers that shifted in pass 2.
set -euo pipefail
cd "$(dirname "$0")"
GEN=../experiments/gen_cross_refs.py

pass() {  # pass <jobname>
  pdflatex -interaction=nonstopmode -halt-on-error "$1.tex" >/dev/null 2>&1 \
    || { echo "FAILED: $1"; grep -m5 '^!' "$1.log"; exit 1; }
}

for doc in main supplementary; do pass "$doc"; bibtex "$doc" >/dev/null 2>&1 || true; done
for round in 1 2 3; do
  python3 "$GEN" >/dev/null
  for doc in main supplementary; do pass "$doc"; done
done

fail=0
for doc in main supplementary; do
  for pat in 'undefined' 'multiply defined' 'Citation .* undefined'; do
    if grep -qi "$pat" "$doc.log"; then echo "$doc.log: $pat"; fail=1; fi
  done
  if pdftotext "$doc.pdf" - | grep -q '??'; then
    echo "$doc.pdf: contains an unresolved cross-document reference (??)"; fail=1
  fi
  printf '%-14s %s pages, %s references\n' "$doc.pdf" \
    "$(pdfinfo "$doc.pdf" | awk '/^Pages/{print $2}')" \
    "$(grep -c '\\bibitem' "$doc.bbl" || true)"
done
exit $fail
