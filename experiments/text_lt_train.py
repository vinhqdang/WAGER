"""Train three small MLP classifiers on the 20 Newsgroups-LT SVD features
prepared by ``text_lt_prepare.py``: a vanilla cross-entropy baseline (CE), a
class-balanced effective-number-reweighted model (CB, Cui et al. 2019), and a
deferred re-weighting model (DRW, Cao et al. 2019) that trains with uniform
weights and switches to the CB weights only for the final quarter of epochs.

This is a direct adaptation of ``colab_cifar_lt_train.py`` /
``colab_cifar_drw_train.py`` to a tabular (SVD-reduced TF-IDF) input instead
of pixels: same three-arm protocol, same effective-number formula, same
train-full-then-defer-reweighting schedule, just a small MLP standing in for
ResNet-32 since the input is already a compact dense vector.  Runs happily on
CPU; uses CUDA automatically when available.

Writes ``data/text_lt/text_lt_results.npz`` with field names matching what
``run_cifar_lt_wager.py`` expects from ``cifar_lt_results.npz`` (probs_baseline,
probs_cb, probs_drw, y_test, per_class_train_n, coarse_of_class,
imbalance_ratio, epochs, drw_start_epoch), so ``run_text_lt_wager.py`` can be a
close adaptation of ``run_cifar_lt_wager.py``.
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

SEED = 0
EPOCHS = 60
DRW_START = 45          # final quarter of epochs (Cao et al. 2019 schedule)
BATCH = 64
LR = 1e-3
WD = 1e-4
CB_BETA = 0.9999
HIDDEN = (256, 128)
DROPOUT = 0.3
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

torch.manual_seed(SEED)
np.random.seed(SEED)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "text_lt")
DATA_PATH = os.path.join(DATA_DIR, "text_lt_data.npz")


class MLP(nn.Module):
    """300 -> 256 -> 128 -> n_classes, ReLU + dropout. Small stand-in for the
    ResNet-32 used on CIFAR-100-LT; the input here is already a dense,
    information-rich SVD embedding rather than raw pixels."""

    def __init__(self, in_dim: int, n_classes: int, hidden=HIDDEN, dropout=DROPOUT):
        super().__init__()
        layers = []
        d = in_dim
        for h in hidden:
            layers += [nn.Linear(d, h), nn.ReLU(), nn.Dropout(dropout)]
            d = h
        layers.append(nn.Linear(d, n_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def lr_at(epoch: int) -> float:
    """Cosine decay, no warmup -- the MLP is small and shallow enough that
    warmup is unnecessary (unlike the 80-epoch ResNet-32 CIFAR runs)."""
    progress = epoch / max(1, EPOCHS - 1)
    return 0.5 * LR * (1 + np.cos(np.pi * progress))


def train_one(X_train, y_train, n_classes, class_weights, drw_start, label):
    net = MLP(X_train.shape[1], n_classes).to(DEVICE)
    opt = torch.optim.Adam(net.parameters(), lr=LR, weight_decay=WD)
    ds = TensorDataset(torch.as_tensor(X_train, dtype=torch.float32),
                        torch.as_tensor(y_train, dtype=torch.int64))
    loader = DataLoader(ds, batch_size=BATCH, shuffle=True, num_workers=0)
    cw = None if class_weights is None else torch.as_tensor(
        class_weights, dtype=torch.float32, device=DEVICE)
    t0 = time.time()
    for ep in range(EPOCHS):
        net.train()
        for g in opt.param_groups:
            g["lr"] = lr_at(ep)
        use_weights = cw is not None and (drw_start is None or ep >= drw_start)
        w = cw if use_weights else None
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
        if (ep + 1) % 10 == 0 or ep == EPOCHS - 1 or (drw_start is not None and ep == drw_start):
            print(f"  [{label}] epoch {ep+1}/{EPOCHS} loss={tot/n:.4f} acc={correct/n:.4f} "
                  f"reweighted={use_weights} elapsed={time.time()-t0:.0f}s", flush=True)
    return net


def predict_probs(net, X, batch=512):
    net.eval()
    ds = TensorDataset(torch.as_tensor(X, dtype=torch.float32))
    loader = DataLoader(ds, batch_size=batch, shuffle=False, num_workers=0)
    probs = []
    with torch.no_grad():
        for (xb,) in loader:
            out = net(xb.to(DEVICE))
            probs.append(F.softmax(out, dim=1).cpu().numpy())
    return np.concatenate(probs).astype(np.float64)


def main():
    if not os.path.exists(DATA_PATH):
        raise SystemExit(f"missing {DATA_PATH}\nRun experiments/text_lt_prepare.py first.")
    d = np.load(DATA_PATH, allow_pickle=True)
    X_train, y_train = d["X_train"], d["y_train"].astype(np.int64)
    X_test, y_test = d["X_test"], d["y_test"].astype(np.int64)
    per_class_train_n = d["per_class_train_n"].astype(np.int64)
    coarse_of_class = d["coarse_of_class"].astype(np.int64)
    n_classes = len(per_class_train_n)
    imbalance_ratio = float(d["imbalance_ratio"])

    eff_num = 1.0 - np.power(CB_BETA, per_class_train_n)
    cb_weights = (1.0 - CB_BETA) / eff_num
    cb_weights = cb_weights / cb_weights.sum() * n_classes
    print("CB class weights (min/max):", float(cb_weights.min()), float(cb_weights.max()),
          flush=True)

    print(f"Training CE (vanilla cross-entropy) on device={DEVICE} ...", flush=True)
    net_ce = train_one(X_train, y_train, n_classes, class_weights=None, drw_start=None,
                       label="CE")

    print("Training CB (class-balanced effective-number reweighted) ...", flush=True)
    net_cb = train_one(X_train, y_train, n_classes, class_weights=cb_weights, drw_start=0,
                       label="CB")

    print(f"Training DRW (plain CE, class-balanced weights from epoch {DRW_START}) ...",
          flush=True)
    net_drw = train_one(X_train, y_train, n_classes, class_weights=cb_weights,
                        drw_start=DRW_START, label="DRW")

    probs_ce = predict_probs(net_ce, X_test)
    probs_cb = predict_probs(net_cb, X_test)
    probs_drw = predict_probs(net_drw, X_test)
    acc_ce = float(np.mean(probs_ce.argmax(1) == y_test))
    acc_cb = float(np.mean(probs_cb.argmax(1) == y_test))
    acc_drw = float(np.mean(probs_drw.argmax(1) == y_test))
    print(f"Test accuracy: CE={acc_ce:.4f}  CB={acc_cb:.4f}  DRW={acc_drw:.4f}", flush=True)

    out_path = os.path.join(DATA_DIR, "text_lt_results.npz")
    np.savez_compressed(
        out_path,
        probs_baseline=probs_ce.astype(np.float32),
        probs_cb=probs_cb.astype(np.float32),
        probs_drw=probs_drw.astype(np.float32),
        y_test=y_test,
        per_class_train_n=per_class_train_n,
        coarse_of_class=coarse_of_class,
        imbalance_ratio=imbalance_ratio,
        epochs=EPOCHS,
        drw_start_epoch=DRW_START,
        seed=SEED,
        acc_baseline=acc_ce,
        acc_cb=acc_cb,
        acc_drw=acc_drw,
    )
    with open(os.path.join(DATA_DIR, "text_lt_train_summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "acc_ce": acc_ce, "acc_cb": acc_cb, "acc_drw": acc_drw,
            "epochs": EPOCHS, "drw_start_epoch": DRW_START,
            "imbalance_ratio": imbalance_ratio,
            "n_train_lt": int(len(y_train)), "n_test": int(len(y_test)),
            "mlp_hidden": list(HIDDEN), "dropout": DROPOUT,
            "lr": LR, "weight_decay": WD, "batch_size": BATCH,
            "device": DEVICE,
        }, f, indent=2)
    print(f"Saved {out_path}", flush=True)


if __name__ == "__main__":
    main()
