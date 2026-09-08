"""Build a flat, single-file LaTeX bundle of the submission.

Some submission systems take a flat file set: no subdirectories, so the figures/ folder
and the \\input{} split of manuscript/ both have to go.  This flattens main.tex, rewrites
the figure paths from figures/x.png to x.png, and copies the figures, the style files and
ref.bib alongside it.  TMLR imposes no page limit, so the appendices are inline in that
one document and there is no second file to flatten.

The output renders identically to the modular build; it exists only for packaging.

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

    for src, dst in (("main.tex", "main.tex"),):
        flat = inline_inputs((MS / src).read_text(encoding="utf-8"))
        if "\\input{" in flat:
            raise SystemExit("an \\input{} survived inlining; nested inputs are not supported")
        flat = flat.replace("{figures/", "{")
        if "figures/" in flat:
            raise SystemExit("a figures/ path survived flattening")
        (OUT / dst).write_text(flat, encoding="utf-8")

    for png in sorted((MS / "figures").glob("*.png")):
        shutil.copy(png, OUT / png.name)
    for aux in ("ref.bib", "tmlr.sty", "tmlr.bst"):
        shutil.copy(MS / aux, OUT / aux)

    names = sorted(p.name for p in OUT.iterdir())
    print(f"wrote {OUT} with {len(names)} flat files:")
    for n in names:
        print(f"  {n}")

    if "--zip" in sys.argv:
        archive = shutil.make_archive(str(ROOT / "submission"), "zip", root_dir=OUT)
        print(f"packaged {archive}")


if __name__ == "__main__":
    main()
