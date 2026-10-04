"""Why TDE's case-level part is near zero (REV-5): its change, split along its branches.

In PredCls the released causal MOTIFS predictor's logits are
    baseline = vis + ctx(post) + frq,         TDE = ctx(post) - ctx(avg),
so the change from the baseline to TDE runs through three models:
    baseline -> vis+ctx      drop the frequency prior
    vis+ctx  -> ctx          drop the visual term
    ctx      -> TDE          subtract the context term under averaged features
Every quantity below is linear in the gain vector or a difference of per-model
values, so the three steps add up to TDE's total exactly (asserted): the
mean-recall split, the within-cell AUC, and the proper-score split with each
model's own held-out temperature. The path is one order of three; the steps are
attributions along it, not order-free effects.

It also splits each logit term's energy into a part shared by every relation, a
part set by the subject-object cell and a part that varies within cells (logits
are recovered from the stored log-probabilities, up to a per-row constant).

Run: python experiments/run_sgg_tde_path.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain  # noqa: E402
from wager.rank import within_cell_auc_contrast  # noqa: E402
from sgg_variants import load_variant  # noqa: E402
import run_sgg_recall_split as RS  # noqa: E402
import run_sgg_audit_wager as AU  # noqa: E402

DDIR = ROOT / "data/vg_motifs/wager_sgg"
OUT = ROOT / "results/sgg_tde_path.json"
PATH = [("vis_ctx", "none", "drop the frequency prior"),
        ("ctx", "vis_ctx", "drop the visual term"),
        ("TDE", "ctx", "subtract the averaged context")]
N_OBJ = 151


def energy(x, phi, log_prior):
    """Split a logit term's energy into global, between-cell and within-cell parts.

    Rows are centred first (logits are known up to a per-row constant). The
    global part is the vector shared by every relation; between-cell is what the
    subject-object cell adds; within-cell is what varies among relations sharing
    a cell. Also: the global vector's correlation with the log training prior,
    and the root-mean-square size of the term and of its non-global remainder.
    """
    _, inv = np.unique(phi, return_inverse=True)
    x = x - x.mean(1, keepdims=True)
    tot = (x ** 2).sum()
    g = x.mean(0)
    glob = len(x) * (g ** 2).sum()
    cnt = np.bincount(inv).astype(float)
    means = np.stack([np.bincount(inv, x[:, k]) / cnt for k in range(x.shape[1])], 1)
    within = ((x - means[inv]) ** 2).sum()
    return {"global": float(glob / tot), "between": float((tot - glob - within) / tot),
            "within": float(within / tot), "rms": float(np.sqrt(tot / x.size)),
            "rms_non_global": float(np.sqrt((tot - glob) / x.size)),
            "corr_global_log_prior": float(np.corrcoef(g, log_prior)[0, 1])}


def main():
    meta = np.load(DDIR / "meta.npz")
    drop = json.loads((DDIR / "missing_pairs.json").read_text())["rows"]
    keep = np.ones(len(meta["pred"]), dtype=bool)
    keep[drop] = False
    y_all = meta["pred"].astype(np.int64)
    phi_all = meta["subj"].astype(np.int64) * N_OBJ + meta["obj"].astype(np.int64)
    img_all = meta["image_index"].astype(np.int64)
    _, inv, cnt = np.unique(phi_all, return_inverse=True, return_counts=True)
    eligible = cnt[inv] >= 2
    n_y = np.bincount(y_all[eligible], minlength=RS.N_PRED + 1).astype(float)
    w = np.zeros(RS.N_PRED + 1)
    w[1:] = np.where(n_y[1:] > 0, 1.0 / (RS.N_PRED * np.maximum(n_y[1:], 1)), 0.0)

    models = {v for a, b, _ in PATH for v in (a, b)}
    Z = {v: load_variant(v) for v in models}

    # held-out temperatures, the audit's own protocol and seed
    y, phi, image = y_all[keep] - 1, phi_all[keep], img_all[keep]
    rng = np.random.default_rng(20260811)
    imgs = np.unique(image)
    cal_imgs = set(imgs[rng.permutation(len(imgs))[: len(imgs) // 2]].tolist())
    cal = np.array([i in cal_imgs for i in image])
    aud = np.where(~cal)[0]
    Q, T = {}, {}
    for v in models:
        q = Z[v]["probs"][keep].astype(np.float64)[:, 1:]
        q /= q.sum(1, keepdims=True)
        T[v] = AU.fit_temperature(q[cal], y[cal])
        Q[v] = AU.temp_scale(q, T[v])

    steps = []
    for new, old, what in PATH:
        row = {"new": new, "old": old, "step": what}
        for mode in ("gc", "ng"):
            hn, ho = Z[new][f"{mode}_rank"] < 50, Z[old][f"{mode}_rank"] < 50
            row[f"mR@50 {mode}"] = RS.split(hn, ho, y_all, phi_all, img_all, eligible, w)
        a = within_cell_auc_contrast(Z[new]["probs"][keep], Z[old]["probs"][keep],
                                     y_all[keep], phi_all[keep], img_all[keep], n_boot=200)
        row["auc"] = {"difference": a.difference, "ci": list(a.ci),
                      "auc_new": a.auc_new, "auc_old": a.auc_old}
        for sc in ("brier", "log"):
            with np.errstate(all="ignore"):
                g = decompose_gain(Q[new][aud], Q[old][aud], y[aud], phi[aud],
                                   groups=image[aud], score=sc)
            row[f"proper {sc} matched"] = {
                "total": g.total_gain, "group": g.prior_gain, "case": g.alignment_gain,
                "case_ci": list(g.alignment_ci)}
        steps.append(row)
        m = row["mR@50 gc"]
        print(f"{what:32s} mR@50 {m['total']:+.4f} = {m['group']:+.4f} + {m['case']:+.4f} "
              f"[{m['case_ci'][0]:+.4f},{m['case_ci'][1]:+.4f}]  AUC {a.difference:+.4f} "
              f"[{a.ci[0]:+.4f},{a.ci[1]:+.4f}]  quad case "
              f"{row['proper brier matched']['case']:+.5f}", flush=True)

    # the steps must add up to TDE vs the baseline
    total = json.loads((ROOT / "results/sgg_recall_split.json").read_text())["results"]
    for mode in ("gc", "ng"):
        ref = total[f"{mode}@50"]["mean_recall"]
        for part in ("total", "group", "case"):
            s = sum(r[f"mR@50 {mode}"][part] for r in steps)
            assert abs(s - ref[part]) < 1e-10, (mode, part, s, ref[part])
    auc_sum = sum(r["auc"]["difference"] for r in steps)
    with np.errstate(all="ignore"):
        direct = decompose_gain(Q["TDE"][aud], Q["none"][aud], y[aud], phi[aud],
                                groups=image[aud])
    q_sum = sum(r["proper brier matched"]["case"] for r in steps)
    assert abs(q_sum - direct.alignment_gain) < 1e-10, (q_sum, direct.alignment_gain)

    # how much of each logit term is a function of the cell
    L = {v: np.log(Z[v]["probs"][keep].astype(np.float64)) for v in
         ("none", "vis_ctx", "ctx", "TDE")}
    L["vis"] = np.log(load_variant("vis")["probs"][keep].astype(np.float64))
    terms = {"frq": L["none"] - L["vis_ctx"], "vis": L["vis"], "ctx(post)": L["ctx"],
             "ctx(avg)": L["ctx"] - L["TDE"], "TDE": L["TDE"], "baseline": L["none"]}
    cnt = np.asarray(json.loads((DDIR / "summary.json").read_text())
                     ["train_predicate_counts"][1:], dtype=float)
    log_prior = np.log(cnt / cnt.sum())
    shares = {k: energy(v[:, 1:], phi, log_prior) for k, v in terms.items()}
    for k, e in shares.items():
        print(f"  {k:10s} rms {e['rms']:.2f}  global {e['global']:.4f}  between "
              f"{e['between']:.4f}  within {e['within']:.4f}  non-global rms "
              f"{e['rms_non_global']:.3f}  corr(global, log prior) "
              f"{e['corr_global_log_prior']:+.3f}")

    out = {"path": steps, "temperatures": T, "auc_sum": auc_sum,
           "proper_brier_case_direct": direct.alignment_gain,
           "logit_energy": shares,
           "note": "steps add up exactly to TDE vs baseline (asserted)"}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
