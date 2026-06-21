"""Build cached predicate distributions for the VG PredCls WAGER study.

Models (all predict P(predicate | ...) for an annotated subject-object pair):

  FREQ        : P(pred | subj_class, obj_class) from train counts (the classic
                Neural-Motifs frequency baseline).  Constant within a phi-cell.
  FREQ+OVERLAP: FREQ but conditioned also on whether the boxes overlap (a tiny
                amount of geometry leaks in).
  MLP-CLASS   : an MLP on (subj_emb, obj_emb) only -- learns a smoothed prior,
                still essentially phi-measurable.
  MLP-SPATIAL : an MLP on (subj_emb, obj_emb, spatial geometry features) -- uses
                box geometry (genuine image-derived signal) beyond the class pair.
  MLP-SPATIAL+: a larger spatial MLP (more capacity to extract geometry).

The spatial features (relative position, scale, aspect, overlap/IoU) are the
"pixels beyond phi" that distinguish reasoning from prior-fitting.  Models train
in seconds-to-minutes on an 8 GB GPU.  Output: a dict of (N_test, K) probability
matrices aligned to the test split, cached to results/sgg_dists.npz.
"""
from __future__ import annotations

import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "vg", "vg_predcls.npz")
RESULTS = os.path.join(ROOT, "results")
os.makedirs(RESULTS, exist_ok=True)

_EPS = 1e-9


def spatial_features(sbox, obox):
    """Translation/scale-invariant geometry features for a subject-object pair.

    sbox/obox: (N,4) as [x, y, w, h].  Returns (N, D) features describing relative
    position, relative scale, aspect ratios, containment, and IoU.
    """
    sx, sy, sw, sh = [sbox[:, i] for i in range(4)]
    ox, oy, ow, oh = [obox[:, i] for i in range(4)]
    sw = np.maximum(sw, 1.0); sh = np.maximum(sh, 1.0)
    ow = np.maximum(ow, 1.0); oh = np.maximum(oh, 1.0)
    scx, scy = sx + sw / 2, sy + sh / 2
    ocx, ocy = ox + ow / 2, oy + oh / 2
    diag = np.sqrt((sw + ow) ** 2 + (sh + oh) ** 2) + _EPS

    # intersection / union for IoU
    ix1 = np.maximum(sx, ox); iy1 = np.maximum(sy, oy)
    ix2 = np.minimum(sx + sw, ox + ow); iy2 = np.minimum(sy + sh, oy + oh)
    iw = np.maximum(ix2 - ix1, 0.0); ih = np.maximum(iy2 - iy1, 0.0)
    inter = iw * ih
    union = sw * sh + ow * oh - inter + _EPS
    iou = inter / union

    feats = np.stack([
        (ocx - scx) / diag,                 # rel x position
        (ocy - scy) / diag,                 # rel y position
        np.log(ow * oh / (sw * sh)),        # log relative area
        np.log(sw / sh), np.log(ow / oh),   # aspect ratios
        np.log(sw * sh) / 20.0, np.log(ow * oh) / 20.0,  # absolute scales (scaled)
        iou, inter / (sw * sh + _EPS), inter / (ow * oh + _EPS),  # overlap ratios
        np.sign(ocy - scy), np.sign(ocx - scx),            # above/below, left/right
    ], axis=1).astype(np.float32)
    return feats


def freq_baseline(subj_tr, obj_tr, pred_tr, subj_te, obj_te, K, n_obj, alpha=1.0):
    """P(pred | subj, obj) from train counts with add-alpha smoothing.

    Returns (N_test, K). Backoffs: cell -> subject-marginal -> global marginal.
    """
    cell_tr = subj_tr.astype(np.int64) * n_obj + obj_tr
    cell_te = subj_te.astype(np.int64) * n_obj + obj_te

    # global and per-subject backoff distributions
    glob = np.bincount(pred_tr, minlength=K).astype(np.float64) + alpha
    glob /= glob.sum()
    subj_counts = {}
    for s, p in zip(subj_tr, pred_tr):
        subj_counts.setdefault(int(s), np.zeros(K))
        subj_counts[int(s)][p] += 1
    subj_dist = {s: (v + alpha) / (v.sum() + alpha * K) for s, v in subj_counts.items()}

    cell_counts = {}
    for c, p in zip(cell_tr, pred_tr):
        cell_counts.setdefault(int(c), np.zeros(K))
        cell_counts[int(c)][p] += 1

    out = np.empty((len(cell_te), K), dtype=np.float64)
    for i, (c, s) in enumerate(zip(cell_te, subj_te)):
        if int(c) in cell_counts:
            v = cell_counts[int(c)]
            out[i] = (v + alpha) / (v.sum() + alpha * K)
        elif int(s) in subj_dist:
            out[i] = subj_dist[int(s)]
        else:
            out[i] = glob
    return out


def freq_overlap_baseline(subj_tr, obj_tr, pred_tr, ov_tr,
                          subj_te, obj_te, ov_te, K, n_obj, alpha=1.0):
    """FREQ conditioned additionally on a binary overlap indicator."""
    def key(s, o, ov):
        return (int(s) * n_obj + int(o)) * 2 + int(ov)
    counts = {}
    for s, o, p, v in zip(subj_tr, obj_tr, pred_tr, ov_tr):
        k = key(s, o, v)
        counts.setdefault(k, np.zeros(K))
        counts[k][p] += 1
    glob = np.bincount(pred_tr, minlength=K).astype(np.float64) + alpha
    glob /= glob.sum()
    out = np.empty((len(subj_te), K), dtype=np.float64)
    for i, (s, o, v) in enumerate(zip(subj_te, obj_te, ov_te)):
        k = key(s, o, v)
        if k in counts:
            cc = counts[k]
            out[i] = (cc + alpha) / (cc.sum() + alpha * K)
        else:
            out[i] = glob
    return out


# --------------------------------------------------------------------------- #
# GPU-trained MLP predicate predictors (PyTorch)                              #
# --------------------------------------------------------------------------- #
def train_mlp(features_tr, pred_tr, features_te, K, hidden=(256, 128),
              epochs=12, lr=1e-3, batch=4096, weight_decay=1e-5, seed=0,
              device=None, label="mlp"):
    """Train a small MLP classifier and return softmax probs on the test split.

    Uses the GPU when available.  Returns (N_test, K) float64 probability matrix.
    """
    import torch
    import torch.nn as nn

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed)

    Xtr = torch.as_tensor(features_tr, dtype=torch.float32)
    ytr = torch.as_tensor(pred_tr, dtype=torch.long)
    Xte = torch.as_tensor(features_te, dtype=torch.float32)

    mu = Xtr.mean(0, keepdim=True)
    sd = Xtr.std(0, keepdim=True) + 1e-6
    Xtr = (Xtr - mu) / sd
    Xte = (Xte - mu) / sd

    layers, d = [], features_tr.shape[1]
    for h in hidden:
        layers += [nn.Linear(d, h), nn.ReLU(), nn.Dropout(0.1)]
        d = h
    layers += [nn.Linear(d, K)]
    net = nn.Sequential(*layers).to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=weight_decay)
    lossf = nn.CrossEntropyLoss()

    n = len(ytr)
    Xtr_d, ytr_d = Xtr.to(device), ytr.to(device)
    for ep in range(epochs):
        net.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, batch):
            idx = perm[i:i + batch]
            opt.zero_grad()
            out = net(Xtr_d[idx])
            loss = lossf(out, ytr_d[idx])
            loss.backward()
            opt.step()
            tot += loss.item() * len(idx)
        print(f"    [{label}] epoch {ep+1}/{epochs} loss={tot/n:.4f}", flush=True)

    net.eval()
    probs = []
    with torch.no_grad():
        for i in range(0, len(Xte), 65536):
            xb = Xte[i:i + 65536].to(device)
            probs.append(torch.softmax(net(xb), dim=1).cpu().numpy())
    return np.concatenate(probs).astype(np.float64)


def class_embeddings(subj, obj, n_obj, dim=32, seed=0):
    """Fixed random embeddings for subject/object classes (concatenated)."""
    rng = np.random.default_rng(seed)
    emb = rng.normal(0, 1, size=(n_obj, dim)).astype(np.float32)
    return np.concatenate([emb[subj], emb[obj]], axis=1)
