"""Predicate ambiguity: does the SGG audit survive merging synonymous predicates? (REV-6)

Visual Genome predicates overlap (on / sitting on / standing on; wearing / wears;
has / with / of), and a case-level part near zero could reflect how far single
labels can be predicted at all. Two declared merges are applied, neither tuned:

  synonym  11 placement verbs into "on", three "in" forms, wearing/wears, and six
           possessive forms into "has"; every other predicate stays itself (31
           classes)
  coarse   three families: geometric, possessive, semantic (action)

Under a merge a model's probability for a class is the sum over its members and
the label is the member's class; for recall, a relation is a hit for a merged
class when any member would be (the minimum of the members' first-hit ranks).
Reported: the temperature-matched quadratic split, the within-cell AUC and the
micro-averaged mean-recall@50 split, for TDE, the logit-adjusted baseline and
IETrans against the MOTIFS baseline; and the split restricted to relations whose
subject-object pair carries a single annotated predicate.

Run: python experiments/run_predicate_merge.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain, decompose_gain_matrix  # noqa: E402
from wager.rank import within_cell_auc_contrast  # noqa: E402
from sgg_variants import load_variant  # noqa: E402
import run_sgg_audit_wager as AU  # noqa: E402

DDIR = ROOT / "data/vg_motifs/wager_sgg"
OUT = ROOT / "results/predicate_merge.json"
NAMES = json.loads((DDIR / "predicate_names.json").read_text())["names"]
SYNONYM = {
    "on": ["on", "sitting on", "standing on", "laying on", "lying on", "parked on",
           "walking on", "mounted on", "painted on", "growing on", "on back of"],
    "in": ["in", "walking in", "flying in"],
    "wearing": ["wearing", "wears"],
    "has": ["has", "with", "of", "part of", "belonging to", "made of"],
}
COARSE = {
    "geometric": ["above", "across", "against", "along", "at", "attached to", "behind",
                  "between", "in", "in front of", "near", "on", "on back of", "over", "under",
                  "hanging from", "mounted on", "painted on", "growing on", "laying on",
                  "lying on", "sitting on", "standing on", "parked on", "walking on",
                  "walking in", "flying in", "from", "to", "for", "and"],
    "possessive": ["has", "with", "of", "part of", "belonging to", "made of", "wearing",
                   "wears", "carrying", "holding", "covered in", "covering"],
    "semantic": ["eating", "looking at", "playing", "riding", "says", "using", "watching"],
}
VARIANTS = ["TDE", "la1", "ietrans"]


def merge_map(groups):
    """Map 51 indices (0 = background) to merged ids (0 kept for background)."""
    m = np.zeros(51, dtype=np.int64)
    member = {n: g for g, ns in groups.items() for n in ns}
    for n in member:
        assert n in NAMES, n
    classes = list(groups) + [n for n in NAMES[1:] if n not in member]
    for i, n in enumerate(NAMES[1:], start=1):
        m[i] = 1 + classes.index(member.get(n, n))
    return m, len(classes)


def merge_probs(p51, m, k):
    out = np.zeros((len(p51), k + 1))
    for i in range(51):
        out[:, m[i]] += p51[:, i]
    return out


def merge_ranks(r51, m, k):
    out = np.full((len(r51), k + 1), 255, dtype=np.int64)
    for i in range(1, 51):
        out[:, m[i]] = np.minimum(out[:, m[i]], r51[:, i])
    return out


def mean_recall_split(hn, ho, y, phi, image, k):
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    elig = cnt[inv] >= 2
    n_y = np.bincount(y[elig], minlength=k + 1).astype(float)
    w = np.zeros(k + 1)
    w[1:] = np.where(n_y[1:] > 0, 1.0 / (k * np.maximum(n_y[1:], 1)), 0.0)
    h = elig.sum() * w[None, :] * (hn.astype(float) - ho.astype(float))
    g = decompose_gain_matrix(h, y, phi, groups=image, score="hit")
    return {"total": g.total_gain, "group": g.prior_gain, "case": g.alignment_gain,
            "case_ci": list(g.alignment_ci)}


def main():
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    y51 = meta["pred"].astype(np.int64)
    phi = meta["subj"].astype(np.int64) * 151 + meta["obj"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    # relations whose (image, subject box, object box) carries one annotated predicate
    pair_key = np.unique(np.column_stack([image, meta["sbox"], meta["obox"]]), axis=0,
                         return_inverse=True)[1].ravel()
    distinct = {}
    for k_, yy in zip(pair_key, y51):
        distinct.setdefault(int(k_), set()).add(int(yy))
    single = np.array([len(distinct[int(k_)]) == 1 for k_ in pair_key])

    Z = {v: load_variant(v) for v in ["none"] + VARIANTS}
    rng = np.random.default_rng(20260811)               # the audit's calibration split
    imgs = np.unique(image[keep])
    cal_imgs = set(imgs[rng.permutation(len(imgs))[: len(imgs) // 2]].tolist())
    cal = np.array([i in cal_imgs for i in image])
    # temperatures fitted on the unmerged 50-way distributions, as in the audit
    T = {}
    for v, z in Z.items():
        q = z["probs"][:, 1:].astype(np.float64)
        q /= q.sum(1, keepdims=True)
        T[v] = AU.fit_temperature(q[keep & cal], y51[keep & cal] - 1)
    P = {}
    for v, z in Z.items():
        q = z["probs"][:, 1:].astype(np.float64)
        q /= q.sum(1, keepdims=True)
        P[v] = np.column_stack([np.zeros(len(q)), AU.temp_scale(q, T[v])])

    out = {"temperatures": T, "n_single_annotation": int(single[keep].sum()),
           "n_relations": int(keep.sum()), "merges": {}}
    for mname, groups in (("none", {}), ("synonym", SYNONYM), ("coarse", COARSE)):
        m, k = merge_map(groups)
        ym = m[y51]
        res = {"n_classes": k}
        for v in VARIANTS:
            qn, qo = merge_probs(P[v], m, k)[:, 1:], merge_probs(P["none"], m, k)[:, 1:]
            row = {}
            for sub, mask in (("all", keep & ~cal), ("single annotation", keep & ~cal & single)):
                with np.errstate(all="ignore"):
                    g = decompose_gain(qn[mask], qo[mask], ym[mask] - 1, phi[mask],
                                       groups=image[mask], score="brier")
                row[f"matched quadratic, {sub}"] = {
                    "total": g.total_gain, "group": g.prior_gain, "case": g.alignment_gain,
                    "case_ci": list(g.alignment_ci)}
            a = within_cell_auc_contrast(merge_probs(Z[v]["probs"][keep], m, k)[:, 1:],
                                         merge_probs(Z["none"]["probs"][keep], m, k)[:, 1:],
                                         ym[keep] - 1, phi[keep], image[keep], n_boot=100)
            row["auc"] = {"difference": a.difference, "ci": list(a.ci)}
            hn = merge_ranks(Z[v]["gc_rank"].astype(np.int64), m, k)[np.arange(len(ym)), ym] < 50
            ho = merge_ranks(Z["none"]["gc_rank"].astype(np.int64), m, k)[np.arange(len(ym)), ym] < 50
            hn_full = np.zeros((len(ym), k + 1), bool)
            ho_full = np.zeros((len(ym), k + 1), bool)
            rn = merge_ranks(Z[v]["gc_rank"].astype(np.int64), m, k) < 50
            ro = merge_ranks(Z["none"]["gc_rank"].astype(np.int64), m, k) < 50
            hn_full[:], ho_full[:] = rn, ro
            assert np.array_equal(hn_full[np.arange(len(ym)), ym], hn)
            row["mR@50"] = mean_recall_split(hn_full, ho_full, ym, phi, image, k)
            res[v] = row
            r = row["matched quadratic, all"]
            print(f"{mname:8s} {v:8s} quad case {r['case']:+.5f} [{r['case_ci'][0]:+.5f},"
                  f"{r['case_ci'][1]:+.5f}]  AUC {a.difference:+.4f} [{a.ci[0]:+.4f},{a.ci[1]:+.4f}]"
                  f"  mR@50 {row['mR@50']['total']:+.4f} = {row['mR@50']['group']:+.4f} + "
                  f"{row['mR@50']['case']:+.4f}", flush=True)
        out["merges"][mname] = res
        OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
