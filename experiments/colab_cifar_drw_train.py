"""Add a third CIFAR-100-LT classifier: deferred re-weighting (DRW).

Applying class-balanced weights from scratch (the CB run) degraded balanced test
accuracy, which is the documented failure mode of strong re-weighting early in
training: it distorts representation learning.  The standard remedy (Cao et al.,
NeurIPS 2019) is to train with plain cross-entropy first and switch on the
class-balanced weights only for the final epochs.  This run keeps every other
hyperparameter identical to the baseline so the comparison isolates the schedule.

Loads the existing /content/cifar_lt_results.npz and rewrites it with the DRW
probabilities added.
"""
import io
import json
import time
import urllib.request

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as T
from PIL import Image

SEED = 0
IMBALANCE_RATIO = 100.0
EPOCHS = 80
DRW_START = 60          # switch to class-balanced weights here (Cao et al. 2019)
BATCH = 128
LR = 0.1
WD = 2e-4
MOMENTUM = 0.9
WARMUP_EPOCHS = 5
CB_BETA = 0.9999
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

torch.manual_seed(SEED)
np.random.seed(SEED)

BASE = "https://huggingface.co/datasets/uoft-cs/cifar100/resolve/main/cifar100"
FILES = {"train": "train-00000-of-00001.parquet", "test": "test-00000-of-00001.parquet"}


def fetch(split):
    path = f"/content/cifar100_{split}.parquet"
    import os
    if not os.path.exists(path):
        url = f"{BASE}/{FILES[split]}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            while True:
                chunk = r.read(1 << 22)
                if not chunk:
                    break
                f.write(chunk)
    return pd.read_parquet(path)


def to_arrays(df):
    img_col = "img" if "img" in df.columns else "image"
    lab_col = "fine_label" if "fine_label" in df.columns else "label"
    cells = df[img_col].tolist()
    imgs = np.stack([
        np.array(Image.open(io.BytesIO(c["bytes"] if isinstance(c, dict) else c)).convert("RGB"))
        for c in cells
    ])
    return imgs, df[lab_col].to_numpy().astype(np.int64)


train_imgs, train_labels = to_arrays(fetch("train"))
test_imgs, test_labels = to_arrays(fetch("test"))
print(f"train {train_imgs.shape}, test {test_imgs.shape}", flush=True)

MEAN = (0.5071, 0.4865, 0.4409)
STD = (0.2673, 0.2564, 0.2762)
train_tf = T.Compose([T.RandomCrop(32, padding=4), T.RandomHorizontalFlip(),
                      T.ToTensor(), T.Normalize(MEAN, STD)])
test_tf = T.Compose([T.ToTensor(), T.Normalize(MEAN, STD)])


class ArrayDS(Dataset):
    def __init__(self, imgs, labels, tf):
        self.imgs, self.labels, self.tf = imgs, labels, tf

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, i):
        return self.tf(Image.fromarray(self.imgs[i])), int(self.labels[i])


n_cls = 100
mu = IMBALANCE_RATIO ** (-1.0 / (n_cls - 1))
per_class_n = np.array([int(500 * (mu ** c)) for c in range(n_cls)])
rng = np.random.default_rng(SEED)
lt_indices = np.concatenate([
    rng.choice(np.flatnonzero(train_labels == c), size=per_class_n[c], replace=False)
    for c in range(n_cls)
])
rng.shuffle(lt_indices)
train_lt = ArrayDS(train_imgs[lt_indices], train_labels[lt_indices], train_tf)
test_ds = ArrayDS(test_imgs, test_labels, test_tf)
print(f"LT train size: {len(train_lt)}", flush=True)


class BasicBlock(nn.Module):
    def __init__(self, cin, cout, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(cin, cout, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(cout)
        self.conv2 = nn.Conv2d(cout, cout, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(cout)
        self.short = None
        if stride != 1 or cin != cout:
            self.short = nn.Sequential(nn.Conv2d(cin, cout, 1, stride, bias=False),
                                       nn.BatchNorm2d(cout))

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return F.relu(out + (x if self.short is None else self.short(x)))


class ResNet32(nn.Module):
    def __init__(self, n_classes=100, n_blocks=5):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, 1, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(16)
        self.layer1 = self._make_layer(16, 16, n_blocks, 1)
        self.layer2 = self._make_layer(16, 32, n_blocks, 2)
        self.layer3 = self._make_layer(32, 64, n_blocks, 2)
        self.fc = nn.Linear(64, n_classes)

    @staticmethod
    def _make_layer(cin, cout, n, stride):
        layers = [BasicBlock(cin, cout, stride)]
        for _ in range(n - 1):
            layers.append(BasicBlock(cout, cout, 1))
        return nn.Sequential(*layers)

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer3(self.layer2(self.layer1(out)))
        return self.fc(F.adaptive_avg_pool2d(out, 1).flatten(1))


def lr_at(ep):
    if ep < WARMUP_EPOCHS:
        return LR * (ep + 1) / WARMUP_EPOCHS
    p = (ep - WARMUP_EPOCHS) / max(1, EPOCHS - WARMUP_EPOCHS)
    return 0.5 * LR * (1 + np.cos(np.pi * p))


eff_num = 1.0 - np.power(CB_BETA, per_class_n)
cb_w = (1.0 - CB_BETA) / eff_num
cb_w = cb_w / cb_w.sum() * n_cls
cb_t = torch.as_tensor(cb_w, dtype=torch.float32, device=DEVICE)

net = ResNet32().to(DEVICE)
opt = torch.optim.SGD(net.parameters(), lr=LR, momentum=MOMENTUM, weight_decay=WD, nesterov=True)
loader = DataLoader(train_lt, batch_size=BATCH, shuffle=True, num_workers=0)
t0 = time.time()
print(f"Training DRW (plain CE, class-balanced weights from epoch {DRW_START}) ...", flush=True)
for ep in range(EPOCHS):
    net.train()
    for g in opt.param_groups:
        g["lr"] = lr_at(ep)
    w = cb_t if ep >= DRW_START else None
    tot, corr, n = 0.0, 0, 0
    for xb, yb in loader:
        xb, yb = xb.to(DEVICE), yb.to(DEVICE)
        opt.zero_grad()
        out = net(xb)
        loss = F.cross_entropy(out, yb, weight=w)
        loss.backward()
        opt.step()
        tot += loss.item() * len(yb)
        corr += (out.argmax(1) == yb).sum().item()
        n += len(yb)
    if (ep + 1) % 10 == 0 or ep == DRW_START:
        print(f"  [DRW] epoch {ep+1}/{EPOCHS} loss={tot/n:.4f} acc={corr/n:.4f} "
              f"reweighted={ep>=DRW_START} elapsed={time.time()-t0:.0f}s", flush=True)

net.eval()
probs, ys = [], []
with torch.no_grad():
    for xb, yb in DataLoader(test_ds, batch_size=512, shuffle=False, num_workers=0):
        probs.append(F.softmax(net(xb.to(DEVICE)), dim=1).cpu().numpy())
        ys.append(yb.numpy())
probs_drw = np.concatenate(probs).astype(np.float32)
y_test = np.concatenate(ys).astype(np.int64)
acc_drw = float(np.mean(probs_drw.argmax(1) == y_test))
print(f"DRW test accuracy: {acc_drw:.4f}", flush=True)

old = dict(np.load("/content/cifar_lt_results.npz", allow_pickle=True))
assert np.array_equal(old["y_test"], y_test), "test label order changed between runs"
old["probs_drw"] = probs_drw
old["acc_drw"] = acc_drw
old["drw_start_epoch"] = DRW_START
np.savez_compressed("/content/cifar_lt_results.npz", **old)
print(f"Rewrote /content/cifar_lt_results.npz  "
      f"(baseline={float(old['acc_baseline']):.4f}, cb={float(old['acc_cb']):.4f}, "
      f"drw={acc_drw:.4f})", flush=True)
