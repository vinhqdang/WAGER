"""Sweep the projection shrinkage m and split fraction for the FREQ anchor.

We want FREQ (a pure frequency lookup) to yield I_reason ~ 0.  Also check a
spatial-style model still shows positive reasoning so the regime isn't degenerate.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from experiments import sgg_models as M
from wager.pipeline import ModelData, run_wager_permutations

d = np.load(os.path.join("data", "vg", "vg_predcls.npz"), allow_pickle=True)
subj, obj, pred = d["subj"], d["obj"], d["pred"]
sbox, obox, image, phi = d["sbox"], d["obox"], d["image"], d["phi"]
is_train = d["is_train"]
K, n_obj = int(d["n_pred"]), int(d["n_obj"])
tr, te = is_train, ~is_train

freq = M.freq_baseline(subj[tr], obj[tr], pred[tr], subj[te], obj[te], K, n_obj)

# image-blocked subsample ~40k
img_te = image[te]
uniq = np.unique(img_te); rng = np.random.default_rng(0); rng.shuffle(uniq)
keep_imgs = set(); cnt = 0
for im in uniq:
    keep_imgs.add(im); cnt += int(np.sum(img_te == im))
    if cnt >= 40000: break
keep = np.array([im in keep_imgs for im in img_te])
yk, phik, imgk = pred[te][keep], phi[te][keep], img_te[keep]
coarsek = subj[te][keep].astype(np.int64)
c = float(np.log(K))

print(f"N={keep.sum()}  cells_in_subsample={len(np.unique(phik))}")
for sf in (0.4, 0.5):
    for m in (0.0, 0.1, 0.3, 1.0):
        data = ModelData("FREQ", freq[keep], yk, phik, imgk, coarse=coarsek)
        res = run_wager_permutations(data, R=12, c=c, alpha=0.05, seed=0, split_frac=sf, m=m)
        print(f"  split={sf} m={m}:  FREQ I_reason={res.I_reason:.4f}  e={res.e_value:.2e}  I_prior={res.I_prior:.3f}")
