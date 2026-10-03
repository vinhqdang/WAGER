#!/usr/bin/env bash
# Build the CVPR submission and split it into the two files that are uploaded.
#
# The kit compiles the supplementary into the same document as the paper, after the
# bibliography, so the two can \ref each other. This builds that one document, then cuts
# it at the page carrying the supplementary title: everything before is paper.pdf, which
# CVPR caps at eight pages plus references, and everything from there is supp.pdf.
set -euo pipefail
cd "$(dirname "$0")"

pass() {
  pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null 2>&1 \
    || { echo "FAILED"; grep -m8 -A3 '^!' main.log; exit 1; }
}
pass; bibtex main >/dev/null 2>&1 || true; pass; pass

fail=0
if grep -qi 'undefined\|multiply defined' main.log; then
  grep -i 'undefined\|multiply defined' main.log | sort -u | head -10; fail=1
fi

python3 - <<'PY'
import subprocess, sys
n = int(subprocess.run(["pdfinfo", "main.pdf"], capture_output=True, text=True)
        .stdout.split("Pages:")[1].split()[0])
def text(p):
    return subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "main.pdf", "-"],
                          capture_output=True, text=True).stdout
supp = next(p for p in range(1, n + 1) if "Supplementary Material" in text(p))
refs = next(p for p in range(1, supp) if "\nReferences\n" in "\n" + text(p))
# The reference list may start part-way down a page; that page still counts towards the
# eight only if paper text sits above the heading.
first = text(refs)
before = first.split("References")[0].strip()
content_pages = refs if before else refs - 1
subprocess.run(["qpdf", "main.pdf", "--pages", "main.pdf", f"1-{supp-1}", "--", "paper.pdf"], check=True)
subprocess.run(["qpdf", "main.pdf", "--pages", "main.pdf", f"{supp}-{n}", "--", "supp.pdf"], check=True)
print(f"paper.pdf  {supp-1} pages: {content_pages} of content, references from page {refs}")
print(f"supp.pdf   {n-supp+1} pages")
if content_pages > 8:
    print(f"OVER THE LIMIT: {content_pages} pages of content, CVPR allows 8"); sys.exit(1)
PY
exit $fail
