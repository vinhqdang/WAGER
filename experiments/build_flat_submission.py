"""Build the flat, single-file LaTeX bundle an Elsevier submission system wants.

Elsevier's Editorial Manager takes a flat file set: no subdirectories, so the
figures/ folder and the \\input{} split of manuscript/ both have to go.  This
script flattens both main.tex and supplementary.tex, rewriting the figure paths
from figures/x.png to x.png, and copies the figures and ref.bib alongside them.
The supplementary is a separate file because the journal's 20-35 page limit
applies to the manuscript, and supplementary material sits outside it.

The output is byte-equivalent in rendered content to the modular build; the only
reason it exists separately is packaging.

Run: python experiments/build_flat_submission.py [--zip]
"""
from __future__ import annotations

import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
OUT = ROOT / "submission"


def inline_inputs(text: str) -> str:
    """Replace every \\input{f} with the contents of manuscript/f, marked."""

    def sub(match: re.Match) -> str:
        name = match.group(1)
        if not name.endswith(".tex"):
            name += ".tex"
        body = (MS / name).read_text(encoding="utf-8").rstrip("\n")
        return f"% ---------- begin {name} ----------\n{body}\n% ---------- end {name} ----------"

    return re.sub(r"\\input\{([^}]+)\}", sub, text)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for src, dst in (("main.tex", "main.tex"), ("supplementary.tex", "supplementary.tex")):
        flat = inline_inputs((MS / src).read_text(encoding="utf-8"))
        if "\\input{" in flat:
            raise SystemExit("an \\input{} survived inlining; nested inputs are not supported")
        flat = flat.replace("{figures/", "{")
        if "figures/" in flat:
            raise SystemExit("a figures/ path survived flattening")
        (OUT / dst).write_text(flat, encoding="utf-8")

    for png in sorted((MS / "figures").glob("*.png")):
        shutil.copy(png, OUT / png.name)
    shutil.copy(MS / "ref.bib", OUT / "ref.bib")

    names = sorted(p.name for p in OUT.iterdir())
    print(f"wrote {OUT} with {len(names)} flat files:")
    for n in names:
        print(f"  {n}")

    if "--zip" in sys.argv:
        archive = shutil.make_archive(str(ROOT / "submission"), "zip", root_dir=OUT)
        print(f"packaged {archive}")


if __name__ == "__main__":
    main()
