#!/usr/bin/env bash
# Build the TMLR submission. One document now: the appendices are inline, so a plain
# LaTeX/BibTeX/LaTeX/LaTeX cycle resolves everything and there is no cross-document
# reference table to generate.
set -euo pipefail
cd "$(dirname "$0")"

pass() {
  pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null 2>&1 \
    || { echo "FAILED"; grep -m8 '^!' main.log; exit 1; }
}
pass; bibtex main >/dev/null 2>&1 || true; pass; pass

fail=0
for pat in 'undefined' 'multiply defined'; do
  if grep -qi "$pat" main.log; then echo "main.log: $pat"; grep -i "$pat" main.log | head -5; fail=1; fi
done
printf 'main.pdf  %s pages, %s references\n' \
  "$(pdfinfo main.pdf | awk '/^Pages/{print $2}')" \
  "$(grep -c '\\bibitem' main.bbl || true)"
exit $fail
