"""Real-pixel signal on Visual Genome, as a self-contained matched-subsample study.

Design notes (both matter for what the numbers mean):

1. Matched training data. MLP-VISUAL is compared only against models trained on the
   *same* relation subsample. Comparing it against the full-data MLP-SPATIAL of
   Table 2 would confound feature content with training-set size, which is precisely
   the sort of confound this paper exists to expose. The full-data table is therefore
   left alone and this study reports its own internally consistent comparison.

2. Fetch only what is needed. The two official archives are ~15 GB and stream at about
   6 MB/s from the Stanford host, which twice cost more than a Colab VM lifetime. Only
   the images actually referenced by the audited relations are fetched, individually and
   concurrently, which is both smaller and resumable: a re-run skips whatever is
   already on disk.

Expects /content/vg_predcls.npz.
"""
import os
import subprocess
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np

ROOT = "/content"
IMG_DIR = os.path.join(ROOT, "vg_images")
CKPT = os.path.join(ROOT, "clip_ckpt.npz")
os.makedirs(IMG_DIR, exist_ok=True)

SEED = 0
N_TRAIN = 100_000        # relations used to train all three compared models
BATCH = 512
CKPT_EVERY = 50_000
WORKERS = 16             # concurrent image fetches; kept modest to be polite to the host
rng = np.random.default_rng(SEED)


def log(msg):
    print(msg, flush=True)
    with open("/content/progress_vg.txt", "a") as f:
        f.write(msg + "\n")


# --------------------------------------------------------------------------- #
# 1. Which relations, and therefore which images, do we actually need?         #
# --------------------------------------------------------------------------- #
d = np.load(os.path.join(ROOT, "vg_predcls.npz"), allow_pickle=True)
subj, obj, pred = d["subj"], d["obj"], d["pred"]
sbox, obox = d["sbox"].astype(np.float64), d["obox"].astype(np.float64)
image, is_train = d["image"], d["is_train"]
phi_all = d["phi"]
K, n_obj = int(d["n_pred"]), int(d["n_obj"])

tr_all = np.flatnonzero(is_train)
te_idx = np.flatnonzero(~is_train)
tr_idx = np.sort(rng.choice(tr_all, size=min(N_TRAIN, len(tr_all)), replace=False))
use_idx = np.concatenate([tr_idx, te_idx])
needed = np.unique(image[use_idx])
log(f"{len(tr_idx)} train + {len(te_idx)} test relations; {len(needed)} distinct images needed")

# --------------------------------------------------------------------------- #
# 2. Concurrent, resumable image fetch                                         #
# --------------------------------------------------------------------------- #
BASES = ("https://cs.stanford.edu/people/rak248/VG_100K",
         "https://cs.stanford.edu/people/rak248/VG_100K_2")
_lock = threading.Lock()
_state = dict(done=0, bytes=0, missing=0)
t_fetch = time.time()


def fetch_one(img_id):
    path = os.path.join(IMG_DIR, f"{img_id}.jpg")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    for base in BASES:
        try:
            req = urllib.request.Request(f"{base}/{img_id}.jpg",
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                data = r.read()
            if data[:2] == b"\xff\xd8":
                tmp = path + ".part"
                with open(tmp, "wb") as f:
                    f.write(data)
                os.replace(tmp, path)         # atomic: a partial file is never seen as done
                with _lock:
                    _state["bytes"] += len(data)
                break
        except Exception:
            continue
    else:
        with _lock:
            _state["missing"] += 1
    with _lock:
        _state["done"] += 1
        n = _state["done"]
    if n % 5000 == 0:
        el = time.time() - t_fetch
        log(f"  fetched {n}/{len(needed)} images, {_state['bytes']/1e9:.2f} GB, "
            f"{_state['bytes']/1e6/max(el,1e-9):.1f} MB/s, missing={_state['missing']}, "
            f"eta {(len(needed)-n)/max(n/max(el,1e-9),1e-9)/60:.0f} min")


todo = [int(i) for i in needed
        if not os.path.exists(os.path.join(IMG_DIR, f"{int(i)}.jpg"))]
log(f"{len(needed)-len(todo)} images already present; fetching {len(todo)} with {WORKERS} workers")
if todo:
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(fetch_one, todo))
log(f"image fetch done in {time.time()-t_fetch:.0f}s, {_state['bytes']/1e9:.2f} GB, "
    f"{_state['missing']} unavailable")

# --------------------------------------------------------------------------- #
# 3. Deduplicate crops                                                         #
# --------------------------------------------------------------------------- #
def crop_keys(idx, boxes):
    b = np.rint(boxes[idx]).astype(np.int64)
    return np.stack([image[idx].astype(np.int64), b[:, 0], b[:, 1], b[:, 2], b[:, 3]], axis=1)

keys = np.concatenate([crop_keys(use_idx, sbox), crop_keys(use_idx, obox)], axis=0)
_, first_pos, inverse = np.unique(keys, axis=0, return_index=True, return_inverse=True)
inverse = inverse.ravel()
n_unique, n_rel = len(first_pos), len(use_idx)
subj_slot, obj_slot = inverse[:n_rel], inverse[n_rel:]
rep_rel = np.where(first_pos < n_rel, first_pos, first_pos - n_rel)
rep_is_subj = first_pos < n_rel
rep_global = use_idx[rep_rel]
rep_box = np.where(rep_is_subj[:, None], sbox[rep_global], obox[rep_global])
rep_image = image[rep_global]
log(f"Unique crops: {n_unique} (from {2*n_rel}; {100*(1-n_unique/(2*n_rel)):.1f}% deduplicated)")

# --------------------------------------------------------------------------- #
# 4. CLIP encoding (checkpointed)                                              #
# --------------------------------------------------------------------------- #
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "open_clip_torch"], check=True)
import torch
import open_clip
from PIL import Image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# OpenAI's CLIP weights were trained with QuickGELU; the plain "ViT-B-32" config
# silently substitutes standard GELU and degrades every embedding.
model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32-quickgelu", pretrained="openai")
model = model.to(DEVICE).eval()
if DEVICE == "cuda":
    model = model.half()
EMB_DIM = model.visual.output_dim
log(f"CLIP ViT-B-32-quickgelu ready (dim={EMB_DIM}, device={DEVICE})")

emb = np.zeros((n_unique, EMB_DIM), dtype=np.float32)
start_at = 0
if os.path.exists(CKPT):
    ck = np.load(CKPT)
    if ck["emb"].shape == emb.shape:
        emb, start_at = ck["emb"], int(ck["done"])
        log(f"Resumed CLIP encoding at crop {start_at}")

# Order is computed over all crops then sliced, so `done` means the same on a resume.
order = np.argsort(rep_image, kind="stable")[start_at:]

def crop_box(im, box):
    x, y, w, h = box
    x1, y1 = max(0.0, x), max(0.0, y)
    x2 = min(float(im.width), x + max(w, 1.0))
    y2 = min(float(im.height), y + max(h, 1.0))
    if x2 <= x1 or y2 <= y1:
        return im.resize((224, 224))
    return im.crop((x1, y1, x2, y2))

batch_t, batch_slot, missing = [], [], 0
t0 = time.time()

def flush():
    if not batch_t:
        return
    x = torch.stack(batch_t).to(DEVICE)
    if DEVICE == "cuda":
        x = x.half()
    with torch.no_grad():
        f = model.encode_image(x).float().cpu().numpy()
    emb[np.asarray(batch_slot)] = f
    batch_t.clear(); batch_slot.clear()

cur_id, cur_im = None, None
for n_done, slot in enumerate(order, start=start_at + 1):
    img_id = int(rep_image[slot])
    if img_id != cur_id:
        p = os.path.join(IMG_DIR, f"{img_id}.jpg")
        cur_im = None
        if os.path.exists(p):
            try:
                cur_im = Image.open(p).convert("RGB")
            except Exception:
                cur_im = None
        if cur_im is None:
            missing += 1
        cur_id = img_id
    c = crop_box(cur_im, rep_box[slot]) if cur_im is not None else Image.new("RGB", (224, 224))
    batch_t.append(preprocess(c)); batch_slot.append(slot)
    if len(batch_t) >= BATCH:
        flush()
    if n_done % CKPT_EVERY == 0:
        flush(); np.savez(CKPT, emb=emb, done=n_done)
        rate = (n_done - start_at) / max(time.time() - t0, 1e-9)
        log(f"  encoded {n_done}/{n_unique} crops, {rate:.0f}/s, "
            f"eta {(n_unique-n_done)/max(rate,1e-9)/60:.0f} min")
flush(); np.savez(CKPT, emb=emb, done=n_unique)
log(f"CLIP encoding done: {n_unique} crops in {time.time()-t0:.0f}s, {missing} missing images")

# --------------------------------------------------------------------------- #
# 5. Train the three matched-subsample models                                  #
# --------------------------------------------------------------------------- #
import torch.nn as nn

emb_cls = np.random.default_rng(0).normal(0, 1, size=(n_obj, 32)).astype(np.float32)
cls_feat = np.concatenate([emb_cls[subj[use_idx]], emb_cls[obj[use_idx]]], axis=1)


def spatial_features(sb, ob):
    eps = 1e-9
    sx, sy, sw, sh = [sb[:, i] for i in range(4)]
    ox, oy, ow, oh = [ob[:, i] for i in range(4)]
    sw, sh = np.maximum(sw, 1.0), np.maximum(sh, 1.0)
    ow, oh = np.maximum(ow, 1.0), np.maximum(oh, 1.0)
    scx, scy, ocx, ocy = sx + sw / 2, sy + sh / 2, ox + ow / 2, oy + oh / 2
    diag = np.sqrt((sw + ow) ** 2 + (sh + oh) ** 2) + eps
    ix1, iy1 = np.maximum(sx, ox), np.maximum(sy, oy)
    ix2, iy2 = np.minimum(sx + sw, ox + ow), np.minimum(sy + sh, oy + oh)
    inter = np.maximum(ix2 - ix1, 0) * np.maximum(iy2 - iy1, 0)
    union = sw * sh + ow * oh - inter + eps
    return np.stack([
        (ocx - scx) / diag, (ocy - scy) / diag, np.log(ow * oh / (sw * sh)),
        np.log(sw / sh), np.log(ow / oh), np.log(sw * sh) / 20.0, np.log(ow * oh) / 20.0,
        inter / union, inter / (sw * sh + eps), inter / (ow * oh + eps),
        np.sign(ocy - scy), np.sign(ocx - scx),
    ], axis=1).astype(np.float32)


sp_feat = spatial_features(sbox[use_idx], obox[use_idx])
vis_feat = np.concatenate([emb[subj_slot], emb[obj_slot]], axis=1)

FEATURES = {
    "MLP-CLASS-S": cls_feat,
    "MLP-SPATIAL-S": np.concatenate([cls_feat, sp_feat], axis=1),
    "MLP-VISUAL-S": np.concatenate([cls_feat, vis_feat], axis=1),
}
n_tr = len(tr_idx)
y_tr = pred[tr_idx].astype(np.int64)
y_te = pred[te_idx].astype(np.int64)
out_models = {}

for name, feat in FEATURES.items():
    torch.manual_seed(SEED)
    g = torch.Generator().manual_seed(SEED)
    Xtr = torch.as_tensor(feat[:n_tr]); Xte = torch.as_tensor(feat[n_tr:])
    mu, sd = Xtr.mean(0, keepdim=True), Xtr.std(0, keepdim=True) + 1e-6
    Xtr, Xte = (Xtr - mu) / sd, (Xte - mu) / sd
    net = nn.Sequential(
        nn.Linear(feat.shape[1], 256), nn.ReLU(), nn.Dropout(0.1),
        nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.1), nn.Linear(128, K)).to(DEVICE)
    opt = torch.optim.AdamW(net.parameters(), lr=1e-3, weight_decay=1e-5)
    Xtr_d = Xtr.to(DEVICE); ytr_d = torch.as_tensor(y_tr).to(DEVICE)
    for ep in range(15):
        net.train()
        perm = torch.randperm(len(y_tr), generator=g)
        tot = 0.0
        for i in range(0, len(y_tr), 4096):
            b = perm[i:i + 4096]
            opt.zero_grad()
            loss = nn.functional.cross_entropy(net(Xtr_d[b]), ytr_d[b])
            loss.backward(); opt.step()
            tot += loss.item() * len(b)
        if (ep + 1) % 5 == 0:
            log(f"  [{name}] epoch {ep+1}/15 loss={tot/len(y_tr):.4f}")
    net.eval()
    probs = []
    with torch.no_grad():
        for i in range(0, len(Xte), 65536):
            probs.append(torch.softmax(net(Xte[i:i + 65536].to(DEVICE)), 1).cpu().numpy())
    q = np.concatenate(probs).astype(np.float32)
    out_models[name] = q
    log(f"  {name} test accuracy {float(np.mean(q.argmax(1) == y_te)):.4f}")

np.savez_compressed(
    os.path.join(ROOT, "vg_visual_models.npz"),
    **out_models, y=y_te, phi=phi_all[te_idx], image=image[te_idx],
    n_train_relations=n_tr, n_unique_crops=n_unique,
    n_missing_images=missing, n_images_fetched=len(needed),
)
log("Saved /content/vg_visual_models.npz")
