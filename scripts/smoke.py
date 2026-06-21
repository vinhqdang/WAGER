import numpy as np
from experiments.synthetic import make_benchmark, population_info

b = make_benchmark(n_images=800, pairs_per_image=5, K=50, n_cells=300, seed=1)
print("N", len(b.y), "K", b.K, "cells", len(np.unique(b.phi)), "imgs", len(np.unique(b.group)))
for beta in [0.0, 0.3, 0.6, 1.0]:
    q = b.model_geometric(beta)
    pop = population_info(b, q)
    print(f"beta={beta}: I_reason={pop['I_reason']:.3f} I_prior={pop['I_prior']:.3f} I_tot={pop['I_tot']:.3f}")
