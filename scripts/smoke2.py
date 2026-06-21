import numpy as np
from experiments.phase1_simulation import gate_c_recovery

np.seterr(all="ignore")
res = gate_c_recovery(betas=[0.0, 0.25, 0.5, 0.75, 1.0], R=20, seed=3000)
print("PASS:", res["pass"])
