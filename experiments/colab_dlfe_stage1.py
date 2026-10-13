"""DLFE audit stage 1 (Colab): data, checkpoints and codebase for the released
MOTIFS baseline and MOTIFS-DLFE PredCls models (Chiou et al., ACM MM 2021,
"Recovering the Unbiased Scene Graphs from the Biased Ones").

The authors' repository is a fork of the Scene-Graph-Benchmark codebase used for
TDE, so the no-compile patch set of colab_sgg_stage1.py applies as it did for
IETrans (colab_ietrans_stage1.py). What differs:
  - both checkpoints ship in one Google Drive zip (README: "unzip to output/"),
    fetched with gdown;
  - the standard VG150 annotation file comes from the same OneDrive share as the
    TDE audit; the fork ships the dicts file and image_data.json itself;
  - only the 26,446 test images are fetched (colab_vg_test_images.py), with empty
    placeholders for the rest so the loader's image index stays aligned.

Usage on the VM:  python colab_dlfe_stage1.py   (idempotent; resumes)
"""
import base64
import glob
import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
import zipfile

ROOT = "/content"
DLFE = f"{ROOT}/dlfe"
IMG = f"{ROOT}/vg_images"
GDRIVE_ZIP = "19n2Z8udljxgSpDwG8vPRWSEe76GzL9DM"      # README, "Models": both checkpoints
BADGER_APP = "5cbed6ac-a083-4e14-b191-b4ba07653de2"
STD_H5_SHARE = "https://1drv.ms/u/s!AmRLLNf6bzcir8xf9oC3eNWlVMTRDw?e=63t7Ed"
T0 = time.time()


def log(m):
    print(f"[dlfe1 +{time.time()-T0:.0f}s] {m}", flush=True)


def sh(args, cwd=None):
    log("$ " + " ".join(args))
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:], flush=True)
        raise RuntimeError(f"command failed: {args[0]}")
    return r.stdout


def fetch(url, dest, headers=None):
    if os.path.exists(dest + ".done"):
        return
    h = {"User-Agent": "Mozilla/5.0", **(headers or {})}
    pos = os.path.getsize(dest) if os.path.exists(dest) else 0
    if pos:
        h["Range"] = f"bytes={pos}-"
    t0 = time.time()
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=180) as r, \
            open(dest, "ab" if pos else "wb") as f:
        while chunk := r.read(1 << 22):
            f.write(chunk)
            pos += len(chunk)
    open(dest + ".done", "w").write("1")
    log(f"fetched {dest} ({pos/1e9:.2f} GB, {pos/1e6/max(1, time.time()-t0):.1f} MB/s)")


def onedrive(share, dest):
    if os.path.exists(dest + ".done"):
        return
    for attempt in range(20):           # OneDrive resets long transfers; fetch resumes
        try:
            tok = json.load(urllib.request.urlopen(urllib.request.Request(
                "https://api-badgerp.svc.ms/v1.0/token",
                data=json.dumps({"appId": BADGER_APP}).encode(),
                headers={"Content-Type": "application/json"}, method="POST"), timeout=30))["token"]
            enc = base64.urlsafe_b64encode(share.encode()).decode().rstrip("=")
            d = json.load(urllib.request.urlopen(urllib.request.Request(
                f"https://my.microsoftpersonalcontent.com/_api/v2.0/shares/u!{enc}"
                "/driveItem?$select=id,name,size,@content.downloadUrl",
                headers={"Authorization": f"Badger {tok}", "Prefer": "autoredeem"}), timeout=30))
            fetch(d["@content.downloadUrl"], dest)
            return
        except Exception as e:
            log(f"onedrive attempt {attempt}: {e}")
            time.sleep(15)
    raise RuntimeError("OneDrive download failed after 20 attempts")


def gdrive(fid, dest):
    if os.path.exists(dest + ".done"):
        return
    sh(["gdown", "--continue", fid, "-O", dest])
    open(dest + ".done", "w").write("1")
    log(f"gdown {dest} ({os.path.getsize(dest)/1e9:.2f} GB)")


sh(["pip", "-q", "install", "gdown", "ipdb", "yacs", "ninja", "cython", "overrides", "h5py",
    "networkx", "numpy<2"])

# ---- 1. code -----------------------------------------------------------------
if not os.path.exists(f"{DLFE}/.git"):
    sh(["git", "clone", "--depth", "1",
        "https://github.com/coldmanck/recovering-unbiased-scene-graphs", DLFE])
V = f"{DLFE}/datasets/vg"
for req in ("VG-SGG-dicts-with-attri.json", "image_data.json"):
    assert os.path.exists(f"{V}/{req}"), f"fork does not ship {req}"

# ---- 2. annotations, checkpoints, test images ---------------------------------
onedrive(STD_H5_SHARE, f"{ROOT}/VG-SGG-with-attri.h5")
if not os.path.exists(f"{V}/VG-SGG-with-attri.h5"):
    os.symlink(f"{ROOT}/VG-SGG-with-attri.h5", f"{V}/VG-SGG-with-attri.h5")
gdrive(GDRIVE_ZIP, f"{ROOT}/dlfe_models.zip")
if not os.path.exists(f"{ROOT}/dlfe_ckpt/.done"):
    with zipfile.ZipFile(f"{ROOT}/dlfe_models.zip") as z:
        names = z.namelist()
        log(f"zip: {len(names)} members; {[n for n in names if not n.endswith('/')][:20]}")
        z.extractall(f"{ROOT}/dlfe_ckpt")
    open(f"{ROOT}/dlfe_ckpt/.done", "w").write("1")
pths = sorted(glob.glob(f"{ROOT}/dlfe_ckpt/**/*.pth", recursive=True))
for p in pths:
    log(f"ckpt file: {p} ({os.path.getsize(p)/1e9:.2f} GB)")
assert len(pths) >= 2, "expected the baseline and the DLFE checkpoint"

os.makedirs(IMG, exist_ok=True)
if not os.path.exists(f"{IMG}/.done"):
    sh(["python", f"{ROOT}/colab_vg_test_images.py", f"{ROOT}/VG-SGG-with-attri.h5",
        f"{V}/image_data.json", IMG])
    open(f"{IMG}/.done", "w").write("1")
log(f"{len(os.listdir(IMG))} image files (test images plus placeholders)")
if not os.path.exists(f"{V}/VG_100K"):
    os.symlink(IMG, f"{V}/VG_100K")

# ---- 3. the no-compile patch set of colab_sgg_stage1.py ------------------------
L = f"{DLFE}/maskrcnn_benchmark/layers"
open(f"{L}/nms.py", "w").write(
    "from torchvision.ops import nms as _tv_nms\n"
    "def nms(boxes, scores, threshold):\n"
    "    return _tv_nms(boxes.float(), scores.float(), threshold)\n")
open(f"{L}/roi_align.py", "w").write('''
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
                             self.spatial_scale, self.sampling_ratio, aligned=False)
''')
open(f"{L}/roi_pool.py", "w").write('''
from torch import nn


def roi_pool(*a, **k):
    raise RuntimeError("roi_pool stubbed out")


class ROIPool(nn.Module):
    def __init__(self, output_size, spatial_scale):
        super().__init__()

    def forward(self, *a, **k):
        raise RuntimeError("ROIPool stubbed out")
''')
open(f"{L}/sigmoid_focal_loss.py", "w").write(
    "from torch import nn\nclass SigmoidFocalLoss(nn.Module):\n"
    "    def __init__(self, gamma=0.0, alpha=0.0):\n        super().__init__()\n"
    "    def forward(self, *a, **k):\n        raise RuntimeError('stubbed')\n")
if os.path.isdir(f"{L}/dcn"):
    open(f"{L}/dcn/deform_conv_func.py", "w").write(
        "def deform_conv(*a, **k):\n    raise RuntimeError('dcn stubbed')\n"
        "def modulated_deform_conv(*a, **k):\n    raise RuntimeError('dcn stubbed')\n")
    open(f"{L}/dcn/deform_pool_func.py", "w").write(
        "def deform_roi_pooling(*a, **k):\n    raise RuntimeError('dcn stubbed')\n")
    for fn, classes in (("deform_conv_module.py", ("DeformConv", "ModulatedDeformConv",
                                                   "ModulatedDeformConvPack")),
                        ("deform_pool_module.py", ("DeformRoIPooling", "DeformRoIPoolingPack",
                                                   "ModulatedDeformRoIPoolingPack"))):
        open(f"{L}/dcn/{fn}", "w").write("from torch import nn\n" + "".join(
            f"class {c}(nn.Module):\n    def __init__(self, *a, **k):\n        super().__init__()\n"
            "    def forward(self, *a, **k):\n        raise RuntimeError('dcn stubbed')\n"
            for c in classes))

pc = f"{DLFE}/maskrcnn_benchmark/config/paths_catalog.py"
s = open(pc).read()
s = re.sub(r'^(\s*)DATA_DIR\s*=\s*".*?"',
           lambda m: f'{m.group(1)}DATA_DIR = "{DLFE}/datasets"', s, count=1, flags=re.M)
open(pc, "w").write(s)

SUBS = [
    (r"torch\._six\.PY3", "True"),
    (r"from torch\._six import string_classes", "string_classes = str"),
    (r"from torch\._six import int_classes", "int_classes = int"),
    (r"torch\._six\.string_classes", "str"),
    (r"torch\._six\.int_classes", "int"),
    (r"\b_download_url_to_file\b", "download_url_to_file"),
    (r"np\.float\b(?!\d|_)", "float"),
    (r"np\.bool\b(?!\d|_)", "bool"),
    (r"np\.int\b(?!\d|_|e)", "int"),
    (r"np\.object\b(?!\d|_)", "object"),
    (r"from collections import Iterable", "from collections.abc import Iterable"),
    (r"from collections import Sequence", "from collections.abc import Sequence"),
]
n = 0
for base in (f"{DLFE}/maskrcnn_benchmark", f"{DLFE}/tools"):
    for dp, _d, files in os.walk(base):
        for fn in files:
            if fn.endswith(".py"):
                p = os.path.join(dp, fn)
                t = open(p, encoding="utf-8", errors="replace").read()
                u = t
                for pat, rep in SUBS:
                    u = re.sub(pat, rep, u)
                if u != t:
                    open(p, "w", encoding="utf-8").write(u)
                    n += 1
log(f"compat substitutions touched {n} files")

os.makedirs(f"{ROOT}/pylib/apex", exist_ok=True)
open(f"{ROOT}/pylib/apex/__init__.py", "w").write("from . import amp\n")
open(f"{ROOT}/pylib/apex/amp.py", "w").write(
    "import contextlib\ndef init(*a, **k): pass\n"
    "def initialize(models, optimizers=None, **k):\n"
    "    return (models, optimizers) if optimizers is not None else models\n"
    "@contextlib.contextmanager\ndef scale_loss(loss, optimizer, **k):\n    yield loss\n")

# GloVe
os.makedirs(f"{ROOT}/glove", exist_ok=True)
if not os.path.exists(f"{ROOT}/glove/glove.6B.200d.txt"):
    fetch("https://nlp.stanford.edu/data/glove.6B.zip", f"{ROOT}/glove.6B.zip")
    with zipfile.ZipFile(f"{ROOT}/glove.6B.zip") as z:
        z.extract("glove.6B.200d.txt", f"{ROOT}/glove")
    os.remove(f"{ROOT}/glove.6B.zip")

probe = subprocess.run(
    ["python", "-c", "import sys; sys.path[:0]=['/content/pylib','/content/dlfe'];"
     "import tools.relation_test_net as t; print('entry point imports OK')"],
    cwd=DLFE, capture_output=True, text=True,
    env=dict(os.environ, PYTHONPATH=f"{ROOT}/pylib:{DLFE}"))
print(probe.stdout.strip() or probe.stderr[-3000:], flush=True)
if probe.returncode != 0:
    raise SystemExit("DLFE entry point does not import")
log("DLFE STAGE 1 COMPLETE")
