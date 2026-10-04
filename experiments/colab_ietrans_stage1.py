"""IETrans audit stage 1 (Colab): data, checkpoint and codebase for the released
IETrans Neural-Motifs PredCls model (Zhang et al., ECCV 2022).

IETrans is a fork of the Scene-Graph-Benchmark codebase used for TDE, so the
same no-compile patch set applies (colab_sgg_stage1.py). What differs:
  - checkpoint and VG-50 annotation files come from the authors' Google Drive
    (gdown);
  - the standard VG150 annotation file is fetched as well, from the same
    OneDrive share as the TDE audit, and the VG-50 test split is checked
    against it, because the per-relation outputs are aligned with the TDE
    audit's relation for relation.

Usage on the VM:  python colab_ietrans_stage1.py   (idempotent; resumes)
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
IET = f"{ROOT}/iet"
IMG = f"{ROOT}/vg_images"
GDRIVE = {  # authors' MODEL_ZOO.md and DATASET.md
    "ckpt": "10dMDvHPk8WmOaBL0I1LT9FwnM1COYviS",      # Neural Motif, PREDCLS
    "vg50": "1JWa9DAxIlUc5wZsL6QM_29awKIGh7WrK",      # VG-50 annotation files
}
BADGER_APP = "5cbed6ac-a083-4e14-b191-b4ba07653de2"
STD_H5_SHARE = "https://1drv.ms/u/s!AmRLLNf6bzcir8xf9oC3eNWlVMTRDw?e=63t7Ed"
T0 = time.time()


def log(m):
    print(f"[iet1 +{time.time()-T0:.0f}s] {m}", flush=True)


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


def gdrive(fid, dest):
    if os.path.exists(dest + ".done"):
        return
    sh(["gdown", "--fuzzy", f"https://drive.google.com/file/d/{fid}/view", "-O", dest])
    open(dest + ".done", "w").write("1")
    log(f"gdown {dest} ({os.path.getsize(dest)/1e9:.2f} GB)")


def unpack(path, dest):
    os.makedirs(dest, exist_ok=True)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            z.extractall(dest)
    else:
        sh(["tar", "-xf", path, "-C", dest])


sh(["pip", "-q", "install", "gdown", "ipdb", "yacs", "ninja", "cython", "overrides", "h5py",
    "numpy<2"])

# ---- 1. images (shared layout; skipped if a previous run extracted them) ------
os.makedirs(IMG, exist_ok=True)
for name in ("images.zip", "images2.zip"):
    dest = f"{ROOT}/{name}"
    if os.path.exists(dest + ".unzipped"):
        continue
    fetch(f"https://cs.stanford.edu/people/rak248/VG_100K_2/{name}", dest)
    with zipfile.ZipFile(dest) as z:
        for m in z.namelist():
            if m.lower().endswith(".jpg"):
                with z.open(m) as src, open(f"{IMG}/{os.path.basename(m)}", "wb") as out:
                    out.write(src.read())
    open(dest + ".unzipped", "w").write("1")
    os.remove(dest)
    log(f"extracted {name}")
log(f"{len(os.listdir(IMG))} images")
fetch("https://homes.cs.washington.edu/~ranjay/visualgenome/data/dataset/image_data.json.zip",
      f"{ROOT}/image_data.json.zip")
with zipfile.ZipFile(f"{ROOT}/image_data.json.zip") as z:
    z.extractall(f"{ROOT}/imgmeta")

# ---- 2. code, checkpoint, annotations ------------------------------------------
if not os.path.exists(f"{IET}/.git"):
    sh(["git", "clone", "--depth", "1",
        "https://github.com/waxnkw/IETrans-SGG.pytorch", IET])
gdrive(GDRIVE["ckpt"], f"{ROOT}/ietrans_motif_predcls.bin")
gdrive(GDRIVE["vg50"], f"{ROOT}/ietrans_vg50.bin")
onedrive(STD_H5_SHARE, f"{ROOT}/VG-SGG-with-attri.std.h5")

V = f"{IET}/datasets/vg"
os.makedirs(V, exist_ok=True)
if not os.path.exists(f"{V}/50"):
    unpack(f"{ROOT}/ietrans_vg50.bin", f"{ROOT}/vg50_unpacked")  # a real zip
    h5s = glob.glob(f"{ROOT}/vg50_unpacked/**/VG-SGG-with-attri.h5", recursive=True)
    assert h5s, "VG-50 archive has no VG-SGG-with-attri.h5"
    shutil.copytree(os.path.dirname(h5s[0]), f"{V}/50")
log(f"vg/50: {sorted(os.listdir(f'{V}/50'))}")
if not os.path.exists(f"{V}/VG_100K"):
    os.symlink(IMG, f"{V}/VG_100K")
shutil.copy(f"{ROOT}/imgmeta/image_data.json", f"{V}/image_data.json")

# the Drive file is the .pth itself (torch's zip serialization), not an archive of
# files: no config ships with it, and it holds no frequency-bias weights because the
# model was trained without one. The authors' evaluation command (cmds/50/motif/
# predcls/lt/combine/val.sh) turns PREDICT_USE_BIAS on, which builds the bias at test
# time from the training split's predicate statistics; stage 2 does the same.
os.makedirs(f"{ROOT}/iet_ckpt", exist_ok=True)
if not os.path.exists(f"{ROOT}/iet_ckpt/ietrans_motif_predcls.pth"):
    shutil.copy(f"{ROOT}/ietrans_motif_predcls.bin", f"{ROOT}/iet_ckpt/ietrans_motif_predcls.pth")
log(f"checkpoint {os.path.getsize(f'{ROOT}/iet_ckpt/ietrans_motif_predcls.pth')/1e9:.2f} GB")

# ---- 3. is VG-50 the standard VG150 test split? ---------------------------------
import h5py  # noqa: E402
import numpy as np  # noqa: E402

# Checked once by hand: every array is identical except `split`, where IETrans moved
# 5,000 training images to a validation split (0 -> 1); the test split (2) is unchanged.
with h5py.File(f"{V}/50/VG-SGG-with-attri.h5", "r") as a, \
        h5py.File(f"{ROOT}/VG-SGG-with-attri.std.h5", "r") as b:
    same = {k: bool(a[k].shape == b[k].shape and np.array_equal(a[k][:], b[k][:]))
            for k in b.keys() if k != "split"}
    sa, sb = a["split"][:], b["split"][:]
    same["test split"] = bool(np.array_equal(sa == 2, sb == 2))
    same["split changes"] = {f"{int(x)}->{int(y)}": int(n) for (x, y), n in zip(
        *np.unique(np.stack([sb[sa != sb], sa[sa != sb]], 1), axis=0, return_counts=True))}
log(f"VG-50 against the standard VG150 h5: {same}")
json.dump(same, open(f"{ROOT}/ietrans_h5_check.json", "w"))
if not (same["test split"] and all(v for k, v in same.items()
                                   if k not in ("test split", "split changes"))):
    raise SystemExit("VG-50 test data differ from the standard split")

# ---- 4. the no-compile patch set of colab_sgg_stage1.py ------------------------
L = f"{IET}/maskrcnn_benchmark/layers"
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

pc = f"{IET}/maskrcnn_benchmark/config/paths_catalog.py"
s = open(pc).read()
s = re.sub(r'^(\s*)DATA_DIR\s*=\s*".*?"',
           lambda m: f'{m.group(1)}DATA_DIR = "{IET}/datasets"', s, count=1, flags=re.M)
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
for base in (f"{IET}/maskrcnn_benchmark", f"{IET}/tools"):
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
    ["python", "-c", "import sys; sys.path[:0]=['/content/pylib','/content/iet'];"
     "import tools.relation_test_net as t; print('entry point imports OK')"],
    cwd=IET, capture_output=True, text=True,
    env=dict(os.environ, PYTHONPATH=f"{ROOT}/pylib:{IET}"))
print(probe.stdout.strip() or probe.stderr[-3000:], flush=True)
if probe.returncode != 0:
    raise SystemExit("IETrans entry point does not import")
log("IETRANS STAGE 1 COMPLETE")
