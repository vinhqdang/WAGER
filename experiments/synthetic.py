"""Synthetic benchmark generator for WAGER validity / power simulations.

Mimics a label-imbalanced vision benchmark (e.g. VG150 scene-graph generation):

  * K labels (predicates) with a long-tailed marginal.
  * prior-feature cells phi (e.g. ordered (subject, object) pairs), each carrying
    a peaked conditional p(y | phi=c) -- this is the *annotation-frequency prior*.
  * a latent image signal that lets an oracle sharpen beyond the prior, while
    remaining *consistent*:  E[ oracle(.|x) | phi=c ] = p(y | phi=c)  exactly,
    so the oracle adds genuine within-cell (reasoning) information and zero extra
    prior information.

Models are produced by log-linear (geometric) pooling of the prior and oracle
with weight beta in [0, 1] -- beta is the injected reasoning fraction whose
recovery by RGR we validate.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

_EPS = 1e-12


@dataclass
class SyntheticBenchmark:
    y: np.ndarray              # (N,) true labels, drawn from the per-instance posterior
    phi: np.ndarray            # (N,) cell ids
    group: np.ndarray          # (N,) image ids (for blocked permutation)
    P_cell: np.ndarray         # (N, K) true prior conditional p(y|phi) per instance
    posterior: np.ndarray      # (N, K) true posterior r(y|x) (E[r|phi]=P_cell), y~r
    K: int

    def model_geometric(self, beta: float) -> np.ndarray:
        """Log-linear pool: q ∝ P_cell^(1-beta) * posterior^beta  (row-normalized).

        beta = 0 -> pure prior (constant within cell, zero reasoning);
        beta = 1 -> true posterior (full image reasoning).
        """
        logq = (1.0 - beta) * np.log(self.P_cell + _EPS) + beta * np.log(self.posterior + _EPS)
        logq -= logq.max(axis=1, keepdims=True)
        q = np.exp(logq)
        q /= q.sum(axis=1, keepdims=True)
        return q

    def model_decomposed(self, theta_prior: float, theta_reason: float) -> np.ndarray:
        """Model with separately tunable prior-fitting and reasoning strength.

        log q ∝ log u + theta_prior * (log P_cell - log u)
                       + theta_reason * (log posterior - log P_cell)

        theta_prior dials how much of the frequency prior the model captures;
        theta_reason dials how much within-cell (image) information it captures.
        This lets us synthesize a gain that is a controlled mixture of
        prior-fitting and reasoning, so the true reasoning share is known.
        """
        K = self.K
        log_u = np.log(1.0 / K)
        g_prior = np.log(self.P_cell + _EPS) - log_u
        g_reason = np.log(self.posterior + _EPS) - np.log(self.P_cell + _EPS)
        logq = log_u + theta_prior * g_prior + theta_reason * g_reason
        logq -= logq.max(axis=1, keepdims=True)
        q = np.exp(logq)
        q /= q.sum(axis=1, keepdims=True)
        return q

    def model_prior(self) -> np.ndarray:
        """Pure prior model: prediction depends only on phi (constant within cell)."""
        return self.P_cell.copy()

    def model_oracle(self) -> np.ndarray:
        """The Bayes-optimal model: the true per-instance posterior r(y|x)."""
        return self.posterior.copy()


def make_benchmark(
    n_images: int = 4000,
    pairs_per_image: int = 5,
    K: int = 50,
    n_cells: int = 400,
    cell_concentration: float = 0.3,
    cell_zipf: float = 1.1,
    posterior_concentration: float = 4.0,
    seed: int = 0,
) -> SyntheticBenchmark:
    """Generate a long-tailed benchmark with *genuine* within-cell information.

    Parameters
    ----------
    cell_concentration : Dirichlet alpha for per-cell label distributions; small
        -> peaked (strong frequency prior).
    cell_zipf : exponent of the Zipf marginal over cells (cell popularity).
    posterior_concentration : kappa for the per-instance posterior
        r_i ~ Dirichlet(kappa * P_cell).  E[r_i | phi]=P_cell (consistency), so
        the prior carries no spurious reasoning, while smaller kappa means the
        image more strongly determines the label (more conditional information
        I(Y;X|phi)).  The label is drawn from r_i, so reasoning is real.
    """
    rng = np.random.default_rng(seed)
    N = n_images * pairs_per_image

    # --- cell (phi) popularity: long-tailed ---
    cell_rank = np.arange(1, n_cells + 1)
    cell_pop = 1.0 / np.power(cell_rank, cell_zipf)
    cell_pop /= cell_pop.sum()

    # --- per-cell label conditional p(y|phi=c): peaked Dirichlet ---
    P_by_cell = rng.dirichlet(np.full(K, cell_concentration), size=n_cells)  # (n_cells,K)

    # --- assign instances to images and cells ---
    group = np.repeat(np.arange(n_images), pairs_per_image)
    phi = rng.choice(n_cells, size=N, p=cell_pop)
    P_cell = P_by_cell[phi]                       # (N,K) true prior per instance

    # --- per-instance true posterior r_i ~ Dirichlet(kappa * P_cell) ---
    # E[r_i | phi] = P_cell  =>  prior-projection of the oracle equals the prior,
    # so the oracle adds *only* reasoning information, none extra prior.
    alpha_post = posterior_concentration * P_cell + _EPS
    posterior = rng.gamma(alpha_post, 1.0)
    posterior /= posterior.sum(axis=1, keepdims=True)

    # --- sample true labels from the per-instance posterior r_i ---
    cdf = np.cumsum(posterior, axis=1)
    u = rng.random(N)[:, None]
    y = (u < cdf).argmax(axis=1)

    return SyntheticBenchmark(y=y, phi=phi, group=group, P_cell=P_cell,
                              posterior=posterior, K=K)


# --------------------------------------------------------------------------- #
# Population (ground-truth) information quantities for a given model q         #
# --------------------------------------------------------------------------- #
def population_info(bench: SyntheticBenchmark, q: np.ndarray):
    """Exact population I_prior, I_reason, I_tot for model q on the benchmark.

    Expectations are taken under the *true* per-instance label law r_i (the
    posterior the labels were drawn from), averaged over instances.  These are
    the ground-truth targets the WAGER estimators should recover.

      I_reason = mean_i  E_{y~r_i}[ log q_i(y) - log qbar(y|phi) ]
      I_prior  = mean_i  E_{y~r_i}[ log qbar(y|phi) - log u ]
      I_tot    = I_reason + I_prior
    """
    K = bench.K
    log_u = np.log(1.0 / K)
    # exact self-prior projection: average q within each cell
    qbar = np.empty_like(q)
    for c in np.unique(bench.phi):
        m = bench.phi == c
        qbar[m] = q[m].mean(axis=0, keepdims=True)

    R = bench.posterior  # true label law per instance
    I_reason = float(np.sum(R * (np.log(q + _EPS) - np.log(qbar + _EPS)), axis=1).mean())
    I_prior = float(np.sum(R * (np.log(qbar + _EPS) - log_u), axis=1).mean())
    I_tot = I_reason + I_prior
    return {"I_reason": I_reason, "I_prior": I_prior, "I_tot": I_tot}
