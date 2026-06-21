import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from experiments import sgg_models as M
from wager.pipeline import ModelData, run_wager_permutations

d = np.load(os.path.join("data", "vg", "vg_predcls.npz"), allow_pickle=True)
subj, obj, pred = d["subj"], d["obj"], d["pred"]
sbox, obox, image, phi = d["sbox"], d["obox"], d["image"], d["phi"]
is_train = d["is_train"]
K, n_obj = int(d["n_pred"]), int(d["n_obj"])
tr, te = is_train, ~is_train

# FREQ anchor on a subsample
freq = M.freq_baseline(subj[tr], obj[tr], pred[tr], subj[te], obj[te], K, n_obj)
print("FREQ shape", freq.shape, "rowsum~1:", np.allclose(freq.sum(1), 1.0))
acc = np.mean(freq.argmax(1) == pred[te])
print(f"FREQ test acc = {acc:.4f}")

# spatial features sanity
feat = M.spatial_features(sbox.astype(np.float64), obox.astype(np.float64))
print("spatial feat shape", feat.shape, "finite:", np.isfinite(feat).all())

# WAGER anchor on small image-blocked subsample
img_te = image[te]
uniq = np.unique(img_te)[:4000]
keep = np.isin(img_te, uniq)
print("subsample N =", keep.sum())
coarse = subj[te][keep].astype(np.int64)
data = ModelData("FREQ", freq[keep], pred[te][keep], phi[te][keep], img_te[keep], coarse=coarse)
res = run_wager_permutations(data, R=10, c=float(np.log(K)), alpha=0.05, seed=0)
print(f"FREQ anchor (hier backoff): I_reason={res.I_reason:.4f} e={res.e_value:.3e} I_prior={res.I_prior:.3f}")
