"""Test FREQ anchor with a dense held-out test-fold projection (run_wager_eval)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from experiments import sgg_models as M
from wager.pipeline import ModelData, build_projection, run_wager_eval

d = np.load(os.path.join("data", "vg", "vg_predcls.npz"), allow_pickle=True)
subj, obj, pred = d["subj"], d["obj"], d["pred"]
sbox, obox, image, phi = d["sbox"], d["obox"], d["image"], d["phi"]
is_train = d["is_train"]
K, n_obj = int(d["n_pred"]), int(d["n_obj"])
tr, te = is_train, ~is_train

# FREQ predictions on the full test set
freq_te = M.freq_baseline(subj[tr], obj[tr], pred[tr], subj[te], obj[te], K, n_obj)
phi_te, subj_te, pred_te, img_te = phi[te], subj[te].astype(np.int64), pred[te], image[te]

# split test images 50/50 -> PROJ (projection-fit) vs EVAL
img_u = np.unique(img_te); rng = np.random.default_rng(0); rng.shuffle(img_u)
proj_imgs = set(img_u[: len(img_u) // 2].tolist())
in_proj = np.array([im in proj_imgs for im in img_te])
ev = ~in_proj
print(f"PROJ N={in_proj.sum()}  EVAL N={ev.sum()}  cells(EVAL)={len(np.unique(phi_te[ev]))}")

c = float(np.log(K))
for m in (0.0, 0.25):
    proj = build_projection(freq_te[in_proj], phi_te[in_proj], K, m=m,
                            coarse_proj=subj_te[in_proj])
    data = ModelData("FREQ", freq_te[ev], pred_te[ev], phi_te[ev], img_te[ev], coarse=subj_te[ev])
    res = run_wager_eval(data, proj, R=20, c=c, alpha=0.05, seed=0)
    print(f"  m={m}: FREQ I_reason={res.I_reason:.4f}  e={res.e_value:.3e}  "
          f"I_prior={res.I_prior:.3f}  CI[{res.I_reason_ci[0]:.3f},{res.I_reason_ci[1]:.3f}]")
