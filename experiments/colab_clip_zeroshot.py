"""Zero-shot CLIP predicate scoring on the canonical VG150 PredCls test relations.

For every relation of the TDE audit (data/vg_motifs/wager_sgg/meta.npz) this crops
the union box of subject and object from the image and scores the 50 predicates
with frozen CLIP ViT-B/32 against the prompts "a photo of a {subject} {predicate}
a {object}", one prompt set per subject-object class pair. Nothing is trained on
Visual Genome labels, so the model has no predicate prior of its own: it is the
model "the audience uses", audited on the same relations as TDE and IETrans.

Dataset index -> image file follows the codebase's own loader exactly
(load_image_filenames + load_graphs, test split, filter_empty_rels), and the
image sizes in image_data.json are checked against the audit's stored sizes.

Inputs on the VM: /content/meta.npz, /content/predicate_names.json.
Output: /content/variant_clip_zs.npz with probs (N, 51), column 0 (background) 0.
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
import zipfile

import numpy as np

ROOT = "/content"
IMG = f"{ROOT}/vg_images"
BADGER_APP = "5cbed6ac-a083-4e14-b191-b4ba07653de2"
H5_SHARE = "https://1drv.ms/u/s!AmRLLNf6bzcir8xf9oC3eNWlVMTRDw?e=63t7Ed"
DICTS = ("https://raw.githubusercontent.com/KaihuaTang/Scene-Graph-Benchmark.pytorch/"
         "master/datasets/vg/VG-SGG-dicts-with-attri.json")
CORRUPTED = {"1592.jpg", "1722.jpg", "4616.jpg", "4617.jpg"}
BATCH = 512
T0 = time.time()


def log(m):
    print(f"[zs +{time.time()-T0:.0f}s] {m}", flush=True)


def fetch(url, dest, headers=None):
    if os.path.exists(dest + ".done"):
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        while (c := r.read(1 << 22)):
            f.write(c)
    open(dest + ".done", "w").write("1")


def onedrive(share, dest):
    if os.path.exists(dest + ".done"):
        return
    tok = json.load(urllib.request.urlopen(urllib.request.Request(
        "https://api-badgerp.svc.ms/v1.0/token", data=json.dumps({"appId": BADGER_APP}).encode(),
        headers={"Content-Type": "application/json"}, method="POST"), timeout=30))["token"]
    enc = base64.urlsafe_b64encode(share.encode()).decode().rstrip("=")
    d = json.load(urllib.request.urlopen(urllib.request.Request(
        f"https://my.microsoftpersonalcontent.com/_api/v2.0/shares/u!{enc}"
        "/driveItem?$select=id,name,size,@content.downloadUrl",
        headers={"Authorization": f"Badger {tok}", "Prefer": "autoredeem"}), timeout=30))
    fetch(d["@content.downloadUrl"], dest)


# ---- data -----------------------------------------------------------------------
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "open_clip_torch", "h5py"], check=True)
import h5py  # noqa: E402

os.makedirs(IMG, exist_ok=True)
for name in ("images.zip", "images2.zip"):
    dest = f"{ROOT}/{name}"
    if os.path.exists(dest + ".unzipped"):
        continue
    fetch(f"https://cs.stanford.edu/people/rak248/VG_100K_2/{name}", dest)
    with zipfile.ZipFile(dest) as z:
        for m in z.namelist():
            if m.lower().endswith(".jpg"):
                out = f"{IMG}/{os.path.basename(m)}"
                if not os.path.exists(out):
                    with z.open(m) as s, open(out + ".part", "wb") as o:
                        o.write(s.read())
                    os.replace(out + ".part", out)
    open(dest + ".unzipped", "w").write("1")
    os.remove(dest)
    log(f"extracted {name}")
fetch("https://homes.cs.washington.edu/~ranjay/visualgenome/data/dataset/image_data.json.zip",
      f"{ROOT}/image_data.json.zip")
with zipfile.ZipFile(f"{ROOT}/image_data.json.zip") as z:
    z.extractall(f"{ROOT}/imgmeta")
onedrive(H5_SHARE, f"{ROOT}/VG-SGG-with-attri.h5")
fetch(DICTS, f"{ROOT}/dicts.json")

# dataset index -> file, exactly as the codebase's loader does it
im_data = json.load(open(f"{ROOT}/imgmeta/image_data.json"))
fns, info = [], []
for img in im_data:
    base = f"{img['image_id']}.jpg"
    if base in CORRUPTED:
        continue
    if os.path.exists(f"{IMG}/{base}"):
        fns.append(f"{IMG}/{base}")
        info.append(img)
assert len(fns) == 108073, len(fns)
with h5py.File(f"{ROOT}/VG-SGG-with-attri.h5", "r") as h:
    mask = (h["split"][:] == 2) & (h["img_to_first_box"][:] >= 0) & (h["img_to_first_rel"][:] >= 0)
test_idx = np.where(mask)[0]
test_files = [fns[i] for i in test_idx]
test_info = [info[i] for i in test_idx]
log(f"{len(test_files)} test images")

meta = np.load(f"{ROOT}/meta.npz")
img_i = meta["image_index"].astype(np.int64)
wh = np.asarray([(test_info[i]["width"], test_info[i]["height"]) for i in img_i], dtype=np.float32)
gap = float(np.abs(wh - meta["img_wh"]).max())
log(f"image size check against the audit: max |difference| {gap}")
assert gap < 1e-3, "dataset index -> image mapping disagrees with the audit"

dicts = json.load(open(f"{ROOT}/dicts.json"))
obj_names = ["__bg__"] + [dicts["idx_to_label"][str(i)] for i in range(1, 151)]
pred_names = json.load(open(f"{ROOT}/predicate_names.json"))["names"]
assert pred_names[1:] == [dicts["idx_to_predicate"][str(i)] for i in range(1, 51)]

# ---- CLIP ---------------------------------------------------------------------------
import torch  # noqa: E402
import open_clip  # noqa: E402
from PIL import Image  # noqa: E402

dev = "cuda" if torch.cuda.is_available() else "cpu"
model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32-quickgelu", pretrained="openai")
tok = open_clip.get_tokenizer("ViT-B-32-quickgelu")
model = model.to(dev).eval()
if dev == "cuda":
    model = model.half()
scale = float(model.logit_scale.exp().detach())

# text: one prompt set per subject-object class pair present in the test set
subj, obj = meta["subj"].astype(np.int64), meta["obj"].astype(np.int64)
pairs, pair_of = np.unique(np.stack([subj, obj], 1), axis=0, return_inverse=True)
pair_of = pair_of.ravel()
text = np.zeros((len(pairs), 50, model.text_projection.shape[1]), dtype=np.float32)
prompts = [f"a photo of a {obj_names[s]} {pred_names[p]} a {obj_names[o]}"
           for s, o in pairs for p in range(1, 51)]
with torch.no_grad():
    feats = []
    for i in range(0, len(prompts), 2048):
        f = model.encode_text(tok(prompts[i:i + 2048]).to(dev)).float()
        feats.append(torch.nn.functional.normalize(f, dim=-1).cpu().numpy())
text = np.concatenate(feats).reshape(len(pairs), 50, -1)
log(f"encoded {len(prompts)} prompts for {len(pairs)} class pairs")

# images: union crop of subject and object, deduplicated by (image, union box)
sb, ob = meta["sbox"].astype(np.float64), meta["obox"].astype(np.float64)
ub = np.stack([np.minimum(sb[:, 0], ob[:, 0]), np.minimum(sb[:, 1], ob[:, 1]),
               np.maximum(sb[:, 2], ob[:, 2]), np.maximum(sb[:, 3], ob[:, 3])], 1)
keys = np.concatenate([img_i[:, None], np.rint(ub).astype(np.int64)], 1)
uniq, first, inv = np.unique(keys, axis=0, return_index=True, return_inverse=True)
inv = inv.ravel()
emb = np.zeros((len(uniq), text.shape[2]), dtype=np.float32)
order = np.argsort(uniq[:, 0], kind="stable")
batch, slots, cur, cur_im = [], [], None, None


def flush():
    if not batch:
        return
    x = torch.stack(batch).to(dev)
    with torch.no_grad():
        f = model.encode_image(x.half() if dev == "cuda" else x).float()
    emb[np.asarray(slots)] = torch.nn.functional.normalize(f, dim=-1).cpu().numpy()
    batch.clear()
    slots.clear()


for n, k in enumerate(order, 1):
    im_id = int(uniq[k, 0])
    if im_id != cur:
        cur_im, cur = Image.open(test_files[im_id]).convert("RGB"), im_id
    x1, y1, x2, y2 = uniq[k, 1:]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(cur_im.width, max(x2, x1 + 1)), min(cur_im.height, max(y2, y1 + 1))
    batch.append(preprocess(cur_im.crop((x1, y1, x2, y2))))
    slots.append(k)
    if len(batch) >= BATCH:
        flush()
    if n % 50000 == 0:
        log(f"  encoded {n}/{len(uniq)} union crops")
flush()
log(f"encoded {len(uniq)} union crops for {len(img_i)} relations")

np.savez(f"{ROOT}/zs_features.npz", emb=emb, text=text, inv=inv, pair_of=pair_of, scale=scale)
probs = np.zeros((len(img_i), 51), dtype=np.float32)
for s in range(0, len(img_i), 8192):           # chunked: text[pair_of] in one go is ~19 GB
    e = min(s + 8192, len(img_i))
    logits = scale * np.einsum("nd,nkd->nk", emb[inv[s:e]], text[pair_of[s:e]])
    logits -= logits.max(1, keepdims=True)
    p = np.exp(logits)
    probs[s:e, 1:] = p / p.sum(1, keepdims=True)
np.savez_compressed(f"{ROOT}/variant_clip_zs.npz", probs=probs,
                    n_union_crops=len(uniq), n_class_pairs=len(pairs))
acc = float((probs[:, 1:].argmax(1) + 1 == meta["pred"]).mean())
log(f"zero-shot top-1 accuracy {acc:.4f}")
log("ZEROSHOT COMPLETE")
