"""SGG audit stage 1 (Colab): fetch everything headlessly and prepare the
Scene-Graph-Benchmark codebase for PyTorch-2 inference without compiling.

Downloads (all verified headless-reachable):
  - VG-SGG-with-attri.h5 + causal MOTIFS PredCls checkpoint: OneDrive via the
    badger-token flow the OneDrive web client itself uses.
  - VG images (14 GB) from Stanford; image_data.json from the UW mirror.
  - GloVe 6B from nlp.stanford.edu.

Patch strategy: PredCls inference only touches nms and roi_align from the
compiled _C extension; both have exact torchvision.ops equivalents. Every
other _C consumer is stubbed so imports succeed but use raises.
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
import zipfile

ROOT = "/content"
SGG = f"{ROOT}/sgg"
BADGER_APP = "5cbed6ac-a083-4e14-b191-b4ba07653de2"
ONEDRIVE = {
    f"{ROOT}/VG-SGG-with-attri.h5":
        "https://1drv.ms/u/s!AmRLLNf6bzcir8xf9oC3eNWlVMTRDw?e=63t7Ed",
    f"{ROOT}/causal_motif_predcls.zip":
        "https://1drv.ms/u/s!AmRLLNf6bzcir9xx725wYjN7lytynA?e=0B65Ws",
}


def log(msg):
    print(f"[stage1 +{time.time()-T0:.0f}s] {msg}", flush=True)


def fetch(url, dest, headers=None, resume=True):
    if os.path.exists(dest + ".done"):
        log(f"skip {dest} (done)")
        return
    h = dict(headers or {})
    h.setdefault("User-Agent", "Mozilla/5.0")
    pos = os.path.getsize(dest) if resume and os.path.exists(dest) else 0
    if pos:
        h["Range"] = f"bytes={pos}-"
    req = urllib.request.Request(url, headers=h)
    mode = "ab" if pos else "wb"
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, mode) as f:
        while True:
            chunk = r.read(1 << 22)
            if not chunk:
                break
            f.write(chunk)
            pos += len(chunk)
    open(dest + ".done", "w").write("1")
    log(f"fetched {dest} ({pos/1e9:.2f} GB, {pos/1e6/max(1,time.time()-t0):.1f} MB/s)")


def badger_token():
    req = urllib.request.Request(
        "https://api-badgerp.svc.ms/v1.0/token",
        data=json.dumps({"appId": BADGER_APP}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    return json.load(urllib.request.urlopen(req, timeout=30))["token"]


def onedrive_url(share_url, tok):
    enc = base64.urlsafe_b64encode(share_url.encode()).decode().rstrip("=")
    req = urllib.request.Request(
        f"https://my.microsoftpersonalcontent.com/_api/v2.0/shares/u!{enc}"
        "/driveItem?$select=id,name,size,@content.downloadUrl",
        headers={"Authorization": f"Badger {tok}", "Prefer": "autoredeem"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    log(f"resolved {d['name']} ({d['size']/1e9:.2f} GB)")
    return d["@content.downloadUrl"]


def sh(args, cwd=None):
    log(f"$ {' '.join(args)}")
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:], flush=True)
        print(r.stderr[-3000:], flush=True)
        raise RuntimeError(f"command failed: {args[0]}")
    return r.stdout


T0 = time.time()

# ---- 1. OneDrive artifacts -------------------------------------------------
for attempt in range(3):
    try:
        tok = badger_token()
        for dest, share in ONEDRIVE.items():
            if not os.path.exists(dest + ".done"):
                fetch(onedrive_url(share, tok), dest)
        break
    except Exception as e:  # tempauth URLs expire; refresh token and resume
        log(f"onedrive attempt {attempt}: {e}")
        time.sleep(10)
else:
    raise RuntimeError("OneDrive downloads failed after 3 attempts")

# ---- 2. VG images + metadata ------------------------------------------------
os.makedirs(f"{SGG}/datasets/vg/VG_100K", exist_ok=True)
for name in ("images.zip", "images2.zip"):
    dest = f"{ROOT}/{name}"
    if not os.path.exists(dest + ".unzipped"):
        fetch(f"https://cs.stanford.edu/people/rak248/VG_100K_2/{name}", dest)
        log(f"extracting {name} ...")
        with zipfile.ZipFile(dest) as z:
            for m in z.namelist():
                if m.lower().endswith(".jpg"):
                    with z.open(m) as src, open(
                            f"{SGG}/datasets/vg/VG_100K/{os.path.basename(m)}",
                            "wb") as out:
                        out.write(src.read())
        open(dest + ".unzipped", "w").write("1")
        os.remove(dest)
        log(f"extracted+removed {name}")
n_imgs = len(os.listdir(f"{SGG}/datasets/vg/VG_100K"))
log(f"VG_100K contains {n_imgs} images")

fetch("https://homes.cs.washington.edu/~ranjay/visualgenome/data/dataset/image_data.json.zip",
      f"{ROOT}/image_data.json.zip")
with zipfile.ZipFile(f"{ROOT}/image_data.json.zip") as z:
    z.extractall(f"{ROOT}/imgmeta")

# ---- 3. repo clone + deps ---------------------------------------------------
import shutil

if not os.path.exists(SGG + "/.git"):
    sh(["git", "clone", "--depth", "1",
        "https://github.com/KaihuaTang/Scene-Graph-Benchmark.pytorch", SGG])
sh(["pip", "-q", "install", "yacs", "ninja", "cython", "overrides", "h5py",
    "numpy<2"])

# dataset layout expected by paths_catalog.py (DATA_DIR=datasets)
shutil.copy(f"{ROOT}/VG-SGG-with-attri.h5", f"{SGG}/datasets/vg/")
shutil.copy(f"{ROOT}/imgmeta/image_data.json", f"{SGG}/datasets/vg/")
# dicts file ships in the repo already at datasets/vg/

# checkpoint
os.makedirs(f"{ROOT}/ckpt", exist_ok=True)
with zipfile.ZipFile(f"{ROOT}/causal_motif_predcls.zip") as z:
    z.extractall(f"{ROOT}/ckpt")
for dirpath, _dirs, files in os.walk(f"{ROOT}/ckpt"):
    for fn in files:
        if fn.endswith(".pth") or fn == "last_checkpoint":
            log(f"ckpt file: {os.path.join(dirpath, fn)}")

# GloVe
os.makedirs(f"{ROOT}/glove", exist_ok=True)
if not os.path.exists(f"{ROOT}/glove/glove.6B.200d.txt"):
    fetch("https://nlp.stanford.edu/data/glove.6B.zip", f"{ROOT}/glove.6B.zip")
    with zipfile.ZipFile(f"{ROOT}/glove.6B.zip") as z:
        z.extract("glove.6B.200d.txt", f"{ROOT}/glove")
    os.remove(f"{ROOT}/glove.6B.zip")
    log("glove ready")

# ---- 4. no-compile patch set ------------------------------------------------
L = f"{SGG}/maskrcnn_benchmark/layers"

open(f"{L}/nms.py", "w").write(
    "from torchvision.ops import nms as _tv_nms\n"
    "def nms(boxes, scores, threshold):\n"
    "    return _tv_nms(boxes.float(), scores.float(), threshold)\n")

open(f"{L}/roi_align.py", "w").write("""
import torch
from torch import nn
from torchvision.ops import roi_align as _tv_roi_align


def roi_align(input, rois, output_size, spatial_scale, sampling_ratio):
    return _tv_roi_align(input, rois, output_size, spatial_scale,
                         sampling_ratio, aligned=False)


class ROIAlign(nn.Module):
    def __init__(self, output_size, spatial_scale, sampling_ratio):
        super().__init__()
        self.output_size = output_size
        self.spatial_scale = spatial_scale
        self.sampling_ratio = sampling_ratio

    def forward(self, input, rois):
        return _tv_roi_align(input, rois.float(), self.output_size,
                             self.spatial_scale, self.sampling_ratio,
                             aligned=False)

    def __repr__(self):
        return f"ROIAlign(output_size={self.output_size})"
""")

open(f"{L}/roi_pool.py", "w").write("""
from torch import nn


def roi_pool(*a, **k):
    raise RuntimeError("roi_pool stubbed out (not used in PredCls inference)")


class ROIPool(nn.Module):
    def __init__(self, output_size, spatial_scale):
        super().__init__()
        self.output_size, self.spatial_scale = output_size, spatial_scale

    def forward(self, *a, **k):
        raise RuntimeError("ROIPool stubbed out (not used in PredCls inference)")
""")

open(f"{L}/sigmoid_focal_loss.py", "w").write("""
from torch import nn


class SigmoidFocalLoss(nn.Module):
    def __init__(self, gamma=0.0, alpha=0.0):
        super().__init__()

    def forward(self, *a, **k):
        raise RuntimeError("SigmoidFocalLoss stubbed out")
""")

open(f"{L}/dcn/deform_conv_func.py", "w").write(
    "def deform_conv(*a, **k):\n    raise RuntimeError('dcn stubbed')\n"
    "def modulated_deform_conv(*a, **k):\n    raise RuntimeError('dcn stubbed')\n")
open(f"{L}/dcn/deform_pool_func.py", "w").write(
    "def deform_roi_pooling(*a, **k):\n    raise RuntimeError('dcn stubbed')\n")
open(f"{L}/dcn/deform_conv_module.py", "w").write(
    "from torch import nn\n" + "".join(
        f"class {c}(nn.Module):\n"
        "    def __init__(self, *a, **k):\n        super().__init__()\n"
        "    def forward(self, *a, **k):\n"
        "        raise RuntimeError('dcn stubbed')\n"
        for c in ("DeformConv", "ModulatedDeformConv", "ModulatedDeformConvPack")))
open(f"{L}/dcn/deform_pool_module.py", "w").write(
    "from torch import nn\n" + "".join(
        f"class {c}(nn.Module):\n"
        "    def __init__(self, *a, **k):\n        super().__init__()\n"
        "    def forward(self, *a, **k):\n"
        "        raise RuntimeError('dcn stubbed')\n"
        for c in ("DeformRoIPooling", "DeformRoIPoolingPack",
                  "ModulatedDeformRoIPoolingPack")))

# torch._six and numpy-deprecation fixes across the tree
import re

n_patched = 0
for base in (f"{SGG}/maskrcnn_benchmark", f"{SGG}/tools"):
    for dirpath, _dirs, files in os.walk(base):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dirpath, fn)
            s = open(p, encoding="utf-8", errors="replace").read()
            orig = s
            s = s.replace("torch._six.PY3", "True")
            s = re.sub(r"from torch\._six import string_classes",
                       "string_classes = str", s)
            s = re.sub(r"torch\._six\.string_classes", "str", s)
            s = re.sub(r"np\.float\b(?!\d|_)", "float", s)
            s = re.sub(r"np\.bool\b(?!\d|_)", "bool", s)
            if s != orig:
                open(p, "w", encoding="utf-8").write(s)
                n_patched += 1
log(f"tree-wide compat patch touched {n_patched} files")

# apex stub importable before the real thing
os.makedirs(f"{ROOT}/pylib/apex", exist_ok=True)
open(f"{ROOT}/pylib/apex/__init__.py", "w").write("from . import amp\n")
open(f"{ROOT}/pylib/apex/amp.py", "w").write(
    "import contextlib\n"
    "def init(*a, **k): pass\n"
    "def initialize(models, optimizers=None, **k):\n"
    "    return (models, optimizers) if optimizers is not None else models\n"
    "@contextlib.contextmanager\n"
    "def scale_loss(loss, optimizer, **k):\n    yield loss\n")

# ---- 5. import smoke test ----------------------------------------------------
test = f"""
import sys
sys.path.insert(0, '{ROOT}/pylib'); sys.path.insert(0, '{SGG}')
import torch, apex
from maskrcnn_benchmark.config import cfg
from maskrcnn_benchmark.layers import nms, ROIAlign
cfg.merge_from_file('{SGG}/configs/e2e_relation_X_101_32_8_FPN_1x.yaml')
print('config + layers import OK; torch', torch.__version__)
from maskrcnn_benchmark.data.datasets.visual_genome import VGDataset
print('VGDataset import OK')
"""
open(f"{ROOT}/smoke.py", "w").write(test)
sh(["python", f"{ROOT}/smoke.py"], cwd=SGG)

log("STAGE 1 COMPLETE — ready for relation_test_net runs")
