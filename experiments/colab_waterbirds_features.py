"""Frozen CLIP ViT-L/14 features for Waterbirds (R2-12).

Downloads the Waterbirds release (Sagawa et al. 2020: CUB birds pasted on Places
backgrounds), embeds every image once with frozen CLIP ViT-L/14 and stores the features
with the metadata (label y: landbird/waterbird, background place 0/1, scene category of
the background, split). No part of the audit trains the image encoder.

Output on the VM: /content/waterbirds_features.npz
"""
import os
import subprocess
import sys
import tarfile
import time
import urllib.request

import numpy as np

T0 = time.time()
URL = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
ROOT = "/content/wb"


def log(m):
    print(f"[wb +{time.time()-T0:.0f}s] {m}", flush=True)


subprocess.run([sys.executable, "-m", "pip", "install", "-q", "open_clip_torch", "pandas"], check=True)
import open_clip  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402

os.makedirs(ROOT, exist_ok=True)
tar = f"{ROOT}/wb.tar.gz"
if not os.path.exists(tar + ".done"):
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(tar, "wb") as f:
        while (c := r.read(1 << 22)):
            f.write(c)
    open(tar + ".done", "w").write("1")
log("downloaded")
if not os.path.exists(f"{ROOT}/.extracted"):
    with tarfile.open(tar) as t:
        t.extractall(ROOT)
    open(f"{ROOT}/.extracted", "w").write("1")
base = next(os.path.join(ROOT, d) for d in os.listdir(ROOT) if d.startswith("waterbird_complete"))
meta = pd.read_csv(f"{base}/metadata.csv")
log(f"{len(meta)} images; columns {list(meta.columns)}")

dev = "cuda" if torch.cuda.is_available() else "cpu"
model, _, preprocess = open_clip.create_model_and_transforms("ViT-L-14-quickgelu", pretrained="openai")
model = model.to(dev).eval().half()
feats, batch = [], []


def flush():
    if batch:
        with torch.no_grad():
            f = model.encode_image(torch.stack(batch).to(dev).half()).float()
        feats.append(torch.nn.functional.normalize(f, dim=-1).cpu().numpy())
        batch.clear()


for i, fn in enumerate(meta["img_filename"], 1):
    batch.append(preprocess(Image.open(f"{base}/{fn}").convert("RGB")))
    if len(batch) == 128:
        flush()
    if i % 2000 == 0:
        log(f"  {i}/{len(meta)}")
flush()
X = np.concatenate(feats)
scene = meta["place_filename"].str.split("/").str[2].values.astype(str)      # /b/bamboo_forest/0001.jpg
species = meta["img_filename"].str.split("/").str[0].values.astype(str)
np.savez_compressed("/content/waterbirds_features.npz", X=X, y=meta["y"].values, place=meta["place"].values,
                    split=meta["split"].values, scene=scene, species=species,
                    img=meta["img_filename"].values.astype(str))
log(f"features {X.shape}")
log("WATERBIRDS COMPLETE")
