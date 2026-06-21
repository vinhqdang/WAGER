import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from experiments import sgg_models as M
from wager.pipeline import ModelData, build_projection, run_wager_eval
from wager.core import wealth_process, betting_mean_ci, prior_excess_logscore

d = np.load(os.path.join("data", "vg", "vg_predcls.npz"), allow_pickle=True)
subj, obj, pred = d["subj"], d["obj"], d["pred"]
image, phi, is_train = d["image"], d["phi"], d["is_train"]
K, n_obj = int(d["n_pred"]), int(d["n_obj"])
tr, te = is_train, ~is_train

freq = M.freq_baseline(subj[tr], obj[tr], pred[tr], subj[te], obj[te], K, n_obj)
phi_te, subj_te, pred_te, img_te = phi[te], subj[te].astype(np.int64), pred[te], image[te]
img_u = np.unique(img_te); rng = np.random.default_rng(0); rng.shuffle(img_u)
proj_imgs = set(img_u[: len(img_u)//2].tolist())
in_proj = np.array([im in proj_imgs for im in img_te]); ev = ~in_proj
c = float(np.log(K))

t=time.time(); proj = build_projection(freq[in_proj], phi_te[in_proj], K, m=0.25, coarse_proj=subj_te[in_proj]); print("build_projection", round(time.time()-t,2))

cell_proj, cell_corr, coarse_proj, glob, unif = proj
t=time.time()
dd, ee = prior_excess_logscore(freq[ev], pred_te[ev], phi_te[ev], cell_proj, cell_corr, coarse_proj, glob, unif, c, coarse=subj_te[ev])
print("prior_excess", round(time.time()-t,2), "N=", len(dd))

t=time.time(); w,_,g = wealth_process(dd, c, track=False); print("wealth x1", round(time.time()-t,2), "e=", w)
t=time.time(); lo,hi = betting_mean_ci(dd, c, alpha=0.05); print("betting_ci x1", round(time.time()-t,2), "CI", lo, hi)
t=time.time()
data = ModelData("FREQ", freq[ev], pred_te[ev], phi_te[ev], img_te[ev], coarse=subj_te[ev])
res = run_wager_eval(data, proj, R=30, c=c, alpha=0.05, seed=0, ci_max_perms=8)
print("run_wager_eval R=30", round(time.time()-t,2), "I_reason", round(res.I_reason,4), "e", res.e_value)
