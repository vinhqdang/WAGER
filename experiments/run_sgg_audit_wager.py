"""WAGER audit of released MOTIFS checkpoints: align the Colab eval dumps to
the repo's canonical VG150 test rows and decompose TDE's gain over the biased
baseline.

Alignment is content-based (the two pipelines filter test images slightly
differently): images are matched by the multiset of (subject class, object
class, predicate) triplets, with box-geometry disambiguation -- dump boxes are
normalized by the resized frame recorded in the npz, ours by the original
image sizes from image_data.json. Within an image, relations are matched by
triplet, ties broken by nearest normalized subject box.

Inputs (downloaded from the Colab session):
  data/vg_motifs/motifs_none_predcls.npz   MOTIFS-SUM baseline
  data/vg_motifs/motifs_TDE_predcls.npz    MOTIFS-TDE
  data/vg_motifs/image_data.json           VG image metadata (id -> w,h)

The 51-way dump softmax includes the background predicate at index 0; the
audit restricts to the 50 real predicates and renormalizes, which is the
probability-space analogue of ranking real predicates only.

Run: conda run -n py313 python experiments/run_sgg_audit_wager.py
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from wager.antisymmetric import cyclic_randomization_test, decompose_gain

ROOT = pathlib.Path(__file__).resolve().parents[1]
MDIR = ROOT / "data/vg_motifs"
N_RANDOMIZATIONS = 999


def load_dump(effect: str):
    d = np.load(MDIR / f"motifs_{effect}_predcls.npz")
    q = d["probs"].astype(np.float64)[:, 1:]          # drop background column
    q /= q.sum(axis=1, keepdims=True)
    return {
        "img": d["image_index"].astype(int),
        "sbox": d["sbox"].astype(float), "obox": d["obox"].astype(float),
        "wh": d["img_wh"].astype(float),
        "subj": d["subj"].astype(int) - 1,            # 1..150 -> 0..149
        "obj": d["obj"].astype(int) - 1,
        "pred": d["pred"].astype(int) - 1,            # 1..50 -> 0..49
        "q": q,
    }


def fingerprint(subj, obj, pred):
    return tuple(sorted(zip(subj.tolist(), obj.tolist(), pred.tolist())))


def main():
    raw = np.load(ROOT / "data/vg/vg_predcls.npz")
    te = np.flatnonzero(~raw["is_train"])
    ours = {k: raw[k][te] for k in ("subj", "obj", "pred", "sbox", "obox",
                                    "image", "phi")}
    sizes = {int(r["image_id"]): (float(r["width"]), float(r["height"]))
             for r in json.load(open(MDIR / "image_data.json"))}

    our_groups = defaultdict(list)
    for row, img in enumerate(ours["image"]):
        our_groups[int(img)].append(row)
    our_fp = defaultdict(list)
    for img, rows in our_groups.items():
        r = np.asarray(rows)
        our_fp[fingerprint(ours["subj"][r], ours["obj"][r], ours["pred"][r])
               ].append(img)

    base = load_dump("none")
    tde = load_dump("TDE")
    assert np.array_equal(base["img"], tde["img"]) and \
        np.array_equal(base["pred"], tde["pred"]), "variant dumps differ in layout"

    dump_groups = defaultdict(list)
    for row, i in enumerate(base["img"]):
        dump_groups[int(i)].append(row)

    # ---- image-level matching ----
    n_img_matched = n_img_ambiguous = n_img_unmatched = 0
    aligned_ours, aligned_dump = [], []
    used_imgs: set[int] = set()
    for di, drows in dump_groups.items():
        dr = np.asarray(drows)
        fp = fingerprint(base["subj"][dr], base["obj"][dr], base["pred"][dr])
        cands = [c for c in our_fp.get(fp, []) if c not in used_imgs]
        if not cands:
            n_img_unmatched += 1
            continue
        if len(cands) > 1:
            # disambiguate by normalized subject-box geometry
            def geo_cost(img_id):
                r = np.asarray(our_groups[img_id])
                w, h = sizes.get(img_id, (None, None))
                if w is None:
                    return np.inf
                ob = ours["sbox"][r] / np.array([w, h, w, h])
                db = base["sbox"][dr] / np.repeat(base["wh"][dr], 2, axis=1)
                # compare sorted normalized top-left corners
                return float(np.abs(np.sort(ob[:, 0]) - np.sort(db[:, 0])).sum()
                             + np.abs(np.sort(ob[:, 1]) - np.sort(db[:, 1])).sum())
            cands.sort(key=geo_cost)
            n_img_ambiguous += 1
        img_id = cands[0]
        used_imgs.add(img_id)
        n_img_matched += 1

        # ---- relation-level matching inside the image ----
        r = np.asarray(our_groups[img_id])
        w, h = sizes.get(img_id, (1.0, 1.0))
        ob_norm = ours["sbox"][r] / np.array([w, h, w, h])
        db_norm = base["sbox"][dr] / np.repeat(base["wh"][dr], 2, axis=1)
        by_triplet = defaultdict(list)
        for k, rd in enumerate(dr):
            by_triplet[(base["subj"][rd], base["obj"][rd], base["pred"][rd])
                       ].append(k)
        taken: set[int] = set()
        for j, ro in enumerate(r):
            key = (int(ours["subj"][ro]), int(ours["obj"][ro]),
                   int(ours["pred"][ro]))
            avail = [k for k in by_triplet.get(key, []) if k not in taken]
            if not avail:
                continue
            if len(avail) > 1:
                # dump xyxy top-left vs our xywh top-left
                d0 = db_norm[avail][:, :2]
                o0 = ob_norm[j][:2]
                avail = [avail[int(np.abs(d0 - o0).sum(axis=1).argmin())]]
            k = avail[0]
            taken.add(k)
            aligned_ours.append(ro)
            aligned_dump.append(dr[k])

    aligned_ours = np.asarray(aligned_ours)
    aligned_dump = np.asarray(aligned_dump)
    n = len(aligned_ours)
    print(f"images: matched {n_img_matched} (ambiguous {n_img_ambiguous}), "
          f"unmatched {n_img_unmatched} of {len(dump_groups)}")
    print(f"relations aligned: {n} of {len(te)} ours / {len(base['img'])} dump "
          f"({n/len(te):.1%} of ours)")
    agree = np.mean(ours["pred"][aligned_ours] == base["pred"][aligned_dump])
    assert agree == 1.0, f"label mismatch rate {1-agree:.4f}"

    y = ours["pred"][aligned_ours].astype(np.int64)
    phi = ours["phi"][aligned_ours].astype(np.int64)
    groups = ours["image"][aligned_ours]
    q_base = base["q"][aligned_dump]
    q_tde = tde["q"][aligned_dump]
    acc = {"MOTIFS": float((q_base.argmax(1) == y).mean()),
           "MOTIFS-TDE": float((q_tde.argmax(1) == y).mean())}
    print(f"top-1 on aligned relations: {acc}")

    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        g = decompose_gain(q_tde, q_base, y, phi, groups=groups, score="brier")
        p, _ = cyclic_randomization_test(q_tde, q_base, y, phi, score="brier",
                                         n_randomizations=N_RANDOMIZATIONS,
                                         seed=0)
    print(f"TDE vs MOTIFS: dT={g.total_gain:+.5f} dP={g.prior_gain:+.5f} "
          f"dR={g.reasoning_gain:+.5f} "
          f"CI=[{g.reasoning_ci[0]:+.5f},{g.reasoning_ci[1]:+.5f}] p={p:.4g} "
          f"coverage={g.coverage:.3f} cells={g.n_cells}")

    out = {"aligned_relations": int(n), "of_ours": int(len(te)),
           "images_matched": n_img_matched, "images_unmatched": n_img_unmatched,
           "accuracy": acc,
           "decomposition": {"total": g.total_gain, "prior": g.prior_gain,
                             "reasoning": g.reasoning_gain,
                             "reasoning_ci": list(g.reasoning_ci),
                             "randomization_p": p,
                             "n_cells": g.n_cells,
                             "coverage": g.coverage}}
    dest = ROOT / "results/sgg_audit_motifs.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
