"""Figure showing what a WAGER audit cell actually contains, on both benchmarks.

The point of the figure is the audit cell, not the datasets: in each row the two
samples share the same declared prior feature phi, yet carry different labels. That
is exactly the configuration within-cell label transport exploits -- crossing the two
labels preserves the cell and its label histogram while destroying which prediction
belongs with which instance.

Visual Genome images are fetched individually from the public Stanford mirror (no
bulk download needed); CIFAR-100 images come from the HuggingFace parquet mirror.
Both are cached under data/samples/ so the figure is reproducible offline.
"""
from __future__ import annotations

import io
import json
import os
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "samples")
OUTDIRS = [os.path.join(ROOT, "results", "figures"),
           os.path.join(ROOT, "manuscript", "figures")]
os.makedirs(CACHE, exist_ok=True)

SUBJ_C = "#E24A33"   # subject box
OBJ_C = "#348ABD"    # object box

# Two test relations from the same phi cell (man, surfboard) whose predicates cannot
# be recovered from the class pair alone -- only the pixels separate them.
VG = [
    dict(image_id=2394072, predicate="riding",
         sbox=(189, 96, 179, 222), obox=(149, 254, 306, 102)),
    dict(image_id=61564, predicate="carrying",
         sbox=(158, 432, 120, 414), obox=(22, 438, 371, 291)),
]
VG_CELL = "(man, surfboard)"

# Two CIFAR-100 test images from the same coarse superclass, at opposite ends of the
# long-tailed training distribution.
CIFAR = [dict(fine="beaver", n_train=415), dict(fine="whale", n_train=6)]
CIFAR_CELL = "aquatic_mammals"


def fetch_vg(image_id):
    path = os.path.join(CACHE, f"vg_{image_id}.jpg")
    if not os.path.exists(path):
        for base in ("VG_100K", "VG_100K_2"):
            url = f"https://cs.stanford.edu/people/rak248/{base}/{image_id}.jpg"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    if r.status == 200:
                        data = r.read()
                        if data[:2] == b"\xff\xd8":       # JPEG magic
                            open(path, "wb").write(data)
                            break
            except Exception:
                continue
        else:
            raise SystemExit(f"could not fetch VG image {image_id}")
    return Image.open(path).convert("RGB")


def fetch_cifar():
    """Return {fine_label_name: 32x32 RGB array} for the two chosen classes."""
    path = os.path.join(CACHE, "cifar100_test.parquet")
    if not os.path.exists(path):
        url = ("https://huggingface.co/datasets/uoft-cs/cifar100/resolve/main/"
               "cifar100/test-00000-of-00001.parquet")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=180) as r, open(path, "wb") as f:
            while (chunk := r.read(1 << 22)):
                f.write(chunk)

    import pyarrow.parquet as pq
    import pandas as pd
    pf = pq.ParquetFile(path)
    meta = [json.loads(v.decode()) for k, v in (pf.schema_arrow.metadata or {}).items()
            if "fine_label" in v.decode()][0]
    names = meta["info"]["features"]["fine_label"]["names"]
    df = pd.read_parquet(path)
    out = {}
    for spec in CIFAR:
        cls = names.index(spec["fine"])
        rows = df[df["fine_label"] == cls]
        cell = rows.iloc[0]["img"]
        raw = cell["bytes"] if isinstance(cell, dict) else cell
        out[spec["fine"]] = np.array(Image.open(io.BytesIO(raw)).convert("RGB"))
    return out


def draw_box(ax, box, color, label, anchor="top"):
    """Draw one annotated box. `anchor` puts the caption above or below the box, so
    that overlapping subject/object boxes do not collide in their labels."""
    x, y, w, h = box
    ax.add_patch(mpatches.Rectangle((x, y), w, h, fill=False, edgecolor=color, lw=2.4))
    if anchor == "top":
        ty, va = y + 3, "top"
    else:
        ty, va = y + h - 3, "bottom"
    ax.text(x + 3, ty, label, color="white", fontsize=8.5, va=va, ha="left",
            bbox=dict(facecolor=color, edgecolor="none", pad=1.6, alpha=0.95))


def main():
    fig = plt.figure(figsize=(11, 6.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.9, 1.0], hspace=0.30, wspace=0.10)

    for k, spec in enumerate(VG):
        ax = fig.add_subplot(gs[0, k])
        im = fetch_vg(spec["image_id"])
        ax.imshow(im)
        draw_box(ax, spec["sbox"], SUBJ_C, "subject: man", anchor="top")
        draw_box(ax, spec["obox"], OBJ_C, "object: surfboard", anchor="bottom")
        ax.set_title(f'label $y$ = "{spec["predicate"]}"', fontsize=11, pad=5)
        ax.set_xticks([]); ax.set_yticks([])

    cif = fetch_cifar()
    for k, spec in enumerate(CIFAR):
        ax = fig.add_subplot(gs[1, k])
        ax.imshow(cif[spec["fine"]], interpolation="nearest")
        ax.set_title(f'label $y$ = "{spec["fine"]}"   '
                     f'({spec["n_train"]} training images)', fontsize=11, pad=5)
        ax.set_xticks([]); ax.set_yticks([])

    fig.text(0.5, 0.955, f"Visual Genome PredCls  —  audit cell $\\phi$ = {VG_CELL}",
             ha="center", fontsize=12, weight="bold")
    fig.text(0.5, 0.375, f"CIFAR-100-LT  —  audit cell $\\phi$ = {CIFAR_CELL}",
             ha="center", fontsize=12, weight="bold")
    fig.subplots_adjust(top=0.90, bottom=0.03)

    for d in OUTDIRS:
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "fig6_dataset_samples.png")
        fig.savefig(p, dpi=200, bbox_inches="tight")
        print(f"wrote {p}", flush=True)


if __name__ == "__main__":
    main()
