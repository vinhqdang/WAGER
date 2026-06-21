"""Prepare a real Visual-Genome PredCls dataset for the WAGER SGG study.

Parses the raw Visual Genome ``relationships.json`` into per-relationship
records (subject class, object class, predicate, both boxes), builds a VG150-style
vocabulary (top object classes / predicates by frequency), splits images into a
train pool (for fitting models) and a test pool (on which WAGER is evaluated),
and writes a compact ``.npz``.

This requires NO images and NO GPU -- only the annotation JSON.  The geometric
(spatial) features derived from the boxes are genuine image-derived signal, so a
predicate predictor that uses them exercises reasoning *beyond* the
(subject, object) class-pair frequency prior phi -- exactly WAGER's question.
"""
from __future__ import annotations

import json
import os
import re
import sys
import zipfile
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DL = os.path.join(ROOT, "downloads")
OUT = os.path.join(ROOT, "data", "vg")
os.makedirs(OUT, exist_ok=True)

N_OBJ = 150        # VG150-style object vocabulary size
N_PRED = 50        # VG150-style predicate vocabulary size
TRAIN_FRAC = 0.7   # image-level split: train pool vs WAGER test pool
_WS = re.compile(r"\s+")


def _clean(name: str) -> str:
    if name is None:
        return ""
    return _WS.sub(" ", str(name).strip().lower())


def _obj_name(o: dict) -> str:
    if "names" in o and o["names"]:
        return _clean(o["names"][0])
    return _clean(o.get("name", ""))


def _load_relationships(path_zip: str):
    """Yield (image_id, relationships list) from relationships.json[.zip]."""
    if path_zip.endswith(".zip"):
        with zipfile.ZipFile(path_zip) as z:
            inner = [n for n in z.namelist() if n.endswith(".json")][0]
            with z.open(inner) as f:
                data = json.load(f)
    else:
        with open(path_zip) as f:
            data = json.load(f)
    for entry in data:
        yield entry.get("image_id"), entry.get("relationships", [])


def build(path_zip: str, seed: int = 0):
    print(f"Parsing {path_zip} ...")
    # ---- first pass: vocabularies ----
    obj_counter, pred_counter = Counter(), Counter()
    raw = list(_load_relationships(path_zip))
    print(f"  {len(raw)} images")
    for _, rels in raw:
        for r in rels:
            s = _obj_name(r.get("subject", {}))
            o = _obj_name(r.get("object", {}))
            p = _clean(r.get("predicate", ""))
            if s and o and p:
                obj_counter[s] += 1
                obj_counter[o] += 1
                pred_counter[p] += 1

    obj_vocab = [w for w, _ in obj_counter.most_common(N_OBJ)]
    pred_vocab = [w for w, _ in pred_counter.most_common(N_PRED)]
    obj_id = {w: i for i, w in enumerate(obj_vocab)}
    pred_id = {w: i for i, w in enumerate(pred_vocab)}
    print(f"  object vocab {len(obj_vocab)}, predicate vocab {len(pred_vocab)}")
    print(f"  top predicates: {pred_vocab[:10]}")

    # ---- second pass: records ----
    rng = np.random.default_rng(seed)
    subj_c, obj_c, pred_c = [], [], []
    sbox, obox, img = [], [], []
    for image_id, rels in raw:
        for r in rels:
            s = _obj_name(r.get("subject", {}))
            o = _obj_name(r.get("object", {}))
            p = _clean(r.get("predicate", ""))
            if s in obj_id and o in obj_id and p in pred_id:
                S, O = r["subject"], r["object"]
                try:
                    sb = [float(S["x"]), float(S["y"]), float(S["w"]), float(S["h"])]
                    ob = [float(O["x"]), float(O["y"]), float(O["w"]), float(O["h"])]
                except (KeyError, TypeError, ValueError):
                    continue
                subj_c.append(obj_id[s]); obj_c.append(obj_id[o]); pred_c.append(pred_id[p])
                sbox.append(sb); obox.append(ob); img.append(int(image_id))

    subj_c = np.array(subj_c, np.int32); obj_c = np.array(obj_c, np.int32)
    pred_c = np.array(pred_c, np.int32)
    sbox = np.array(sbox, np.float32); obox = np.array(obox, np.float32)
    img = np.array(img, np.int64)
    print(f"  {len(pred_c)} relationships kept")

    # ---- image-level train/test split ----
    uniq_img = np.unique(img)
    rng.shuffle(uniq_img)
    n_train = int(TRAIN_FRAC * len(uniq_img))
    train_imgs = set(uniq_img[:n_train].tolist())
    is_train = np.array([im in train_imgs for im in img], dtype=bool)

    # phi cell id = subject_class * N_OBJ + object_class
    phi = subj_c.astype(np.int64) * N_OBJ + obj_c.astype(np.int64)

    out_path = os.path.join(OUT, "vg_predcls.npz")
    np.savez_compressed(
        out_path,
        subj=subj_c, obj=obj_c, pred=pred_c, sbox=sbox, obox=obox,
        image=img, is_train=is_train, phi=phi,
        obj_vocab=np.array(obj_vocab, dtype=object),
        pred_vocab=np.array(pred_vocab, dtype=object),
        n_obj=N_OBJ, n_pred=N_PRED,
    )
    print(f"  train rels {is_train.sum()}, test rels {(~is_train).sum()}")
    print(f"  saved -> {out_path}")
    return out_path


if __name__ == "__main__":
    zip_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DL, "relationships.json.zip")
    build(zip_path)
