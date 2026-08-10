"""Train the CE / CB / DRW ResNet-32 triple on CIFAR-100-LT across seeds and
imbalance ratios (Colab GPU job).

Extends the single-run scripts (colab_cifar_lt_train.py, colab_cifar_drw_train.py)
to the matrix the audit needs: seed replication at the primary ratio and a ratio
sweep at the primary seed. The (ratio=100, seed=0) cell already exists as
/content-era data/cifar_lt/cifar_lt_results.npz and is not retrained.

Writes one npz per (ratio, seed): /content/cifar_lt_r{ratio}_s{seed}.npz with
softmax probabilities for all three arms plus labels and per-class train counts.
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

MATRIX = [(100.0, 1), (100.0, 2), (10.0, 0), (50.0, 0)]
EPOCHS = 80
BATCH = 128
LR = 0.1
WD = 2e-4
MOMENTUM = 0.9
WARMUP_EPOCHS = 5
CB_BETA = 0.9999
DRW_START = 60
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

BASE = "https://huggingface.co/datasets/uoft-cs/cifar100/resolve/main/cifar100"
FILES = {"train": "train-00000-of-00001.parquet", "test": "test-00000-of-00001.parquet"}


def fetch(split):
    path = f"/content/cifar100_{split}.parquet"
    url = f"{BASE}/{FILES[split]}"
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        while True:
            chunk = r.read(1 << 22)
            if not chunk:
                break
            f.write(chunk)
    print(f"  fetched {split} in {time.time()-t0:.1f}s", flush=True)
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


print("Downloading CIFAR-100 from the HuggingFace mirror ...", flush=True)
train_imgs, train_labels = to_arrays(fetch("train"))
test_imgs, test_labels = to_arrays(fetch("test"))

MEAN = (0.5071, 0.4865, 0.4409)
STD = (0.2673, 0.2564, 0.2762)
train_tf = T.Compose([
    T.RandomCrop(32, padding=4),
    T.RandomHorizontalFlip(),
    T.ToTensor(),
    T.Normalize(MEAN, STD),
])
test_tf = T.Compose([T.ToTensor(), T.Normalize(MEAN, STD)])


class ArrayDS(Dataset):
    def __init__(self, imgs, labels, tf):
        self.imgs, self.labels, self.tf = imgs, labels, tf

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, i):
        return self.tf(Image.fromarray(self.imgs[i])), int(self.labels[i])


class BasicBlock(nn.Module):
    def __init__(self, cin, cout, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(cin, cout, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(cout)
        self.conv2 = nn.Conv2d(cout, cout, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(cout)
        self.short = None
        if stride != 1 or cin != cout:
            self.short = nn.Sequential(
                nn.Conv2d(cin, cout, 1, stride, bias=False), nn.BatchNorm2d(cout)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        sc = x if self.short is None else self.short(x)
        return F.relu(out + sc)


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
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = F.adaptive_avg_pool2d(out, 1).flatten(1)
        return self.fc(out)


def lr_at(epoch):
    if epoch < WARMUP_EPOCHS:
        return LR * (epoch + 1) / WARMUP_EPOCHS
    progress = (epoch - WARMUP_EPOCHS) / max(1, EPOCHS - WARMUP_EPOCHS)
    return 0.5 * LR * (1 + np.cos(np.pi * progress))


def train_one(train_lt, weights_from_epoch, class_weights, label):
    """weights_from_epoch: 0 = CB (from init), DRW_START = deferred, None = plain CE."""
    net = ResNet32().to(DEVICE)
    opt = torch.optim.SGD(net.parameters(), lr=LR, momentum=MOMENTUM,
                          weight_decay=WD, nesterov=True)
    loader = DataLoader(train_lt, batch_size=BATCH, shuffle=True, num_workers=0)
    cw = None if class_weights is None else torch.as_tensor(
        class_weights, dtype=torch.float32, device=DEVICE)
    t0 = time.time()
    for ep in range(EPOCHS):
        net.train()
        for g in opt.param_groups:
            g["lr"] = lr_at(ep)
        w = None
        if weights_from_epoch is not None and ep >= weights_from_epoch:
            w = cw
        tot, correct, n = 0.0, 0, 0
        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            opt.zero_grad()
            out = net(xb)
            loss = F.cross_entropy(out, yb, weight=w)
            loss.backward()
            opt.step()
            tot += loss.item() * len(yb)
            correct += (out.argmax(1) == yb).sum().item()
            n += len(yb)
        if (ep + 1) % 20 == 0 or ep == EPOCHS - 1:
            print(f"  [{label}] epoch {ep+1}/{EPOCHS} loss={tot/n:.4f} "
                  f"acc={correct/n:.4f} elapsed={time.time()-t0:.0f}s", flush=True)
        with open("/content/progress_multiseed.txt", "w") as pf:
            pf.write(f"{label} epoch {ep+1}/{EPOCHS} elapsed={time.time()-t0:.0f}s\n")
    return net


def predict_probs(net, test_ds):
    net.eval()
    loader = DataLoader(test_ds, batch_size=512, shuffle=False, num_workers=0)
    probs, ys = [], []
    with torch.no_grad():
        for xb, yb in loader:
            out = net(xb.to(DEVICE))
            probs.append(F.softmax(out, dim=1).cpu().numpy())
            ys.append(yb.numpy())
    return np.concatenate(probs).astype(np.float32), np.concatenate(ys).astype(np.int64)


test_ds = ArrayDS(test_imgs, test_labels, test_tf)
summary = {}
for ratio, seed in MATRIX:
    tag = f"r{int(ratio)}_s{seed}"
    print(f"=== config {tag} ===", flush=True)
    torch.manual_seed(seed)
    np.random.seed(seed)

    n_cls, n_max = 100, 500
    mu = ratio ** (-1.0 / (n_cls - 1))
    per_class_n = np.array([int(n_max * (mu ** c)) for c in range(n_cls)])
    rng = np.random.default_rng(seed)
    lt_indices = np.concatenate([
        rng.choice(np.flatnonzero(train_labels == c), size=per_class_n[c], replace=False)
        for c in range(n_cls)
    ])
    rng.shuffle(lt_indices)
    train_lt = ArrayDS(train_imgs[lt_indices], train_labels[lt_indices], train_tf)
    print(f"  LT train size {len(train_lt)}", flush=True)

    eff_num = 1.0 - np.power(CB_BETA, per_class_n)
    cb_weights = (1.0 - CB_BETA) / eff_num
    cb_weights = cb_weights / cb_weights.sum() * n_cls

    arms = {}
    accs = {}
    for label, start in (("CE", None), ("CB", 0), ("DRW", DRW_START)):
        torch.manual_seed(seed)  # same init for every arm within a config
        net = train_one(train_lt, start, cb_weights if start is not None else None,
                        f"{tag}/{label}")
        arms[label], y_test = predict_probs(net, test_ds)
        accs[label] = float(np.mean(arms[label].argmax(1) == y_test))
        del net
        torch.cuda.empty_cache()
    print(f"  accuracies {tag}: " + "  ".join(f"{k}={v:.4f}" for k, v in accs.items()),
          flush=True)
    np.savez_compressed(
        f"/content/cifar_lt_{tag}.npz",
        probs_baseline=arms["CE"], probs_cb=arms["CB"], probs_drw=arms["DRW"],
        y_test=y_test, per_class_train_n=per_class_n,
        imbalance_ratio=ratio, epochs=EPOCHS, seed=seed,
        acc_baseline=accs["CE"], acc_cb=accs["CB"], acc_drw=accs["DRW"],
        drw_start_epoch=DRW_START,
    )
    summary[tag] = accs
    with open("/content/cifar_multiseed_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  saved /content/cifar_lt_{tag}.npz", flush=True)

print("ALL CONFIGS DONE", flush=True)
