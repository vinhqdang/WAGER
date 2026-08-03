# WAGER algorithm specification

## 1. Inputs and estimand

For every test example `i`, WAGER needs:

- `q_new[i, :]` and `q_old[i, :]`: two frozen predictive distributions;
- `y[i]`: the observed label;
- `phi[i]`: a predeclared discrete prior cell;
- optionally, `group[i]` such as an image id for cluster-robust inference.

Let `S(q,y)` be a higher-is-better proper score and define the gain vector

```text
H_i(y) = S(q_new[i], y) - S(q_old[i], y).
```

The default quadratic score is `S(q,y) = 2*q[y] - sum(q**2)`. It is bounded and
strictly proper.

## 2. Counterfactual label transport

Inside a cell `c`, the observed gain is

```text
T_c = mean_i H_i(y_i).
```

Transport each prediction contrast to labels from *other* examples in the same cell:

```text
P_c = 1/[n_c(n_c-1)] * sum_{i != j} H_i(y_j).
```

The within-cell instance-alignment gain is

```text
R_c = T_c - P_c.
```

Equivalently, it is the all-pairs U-statistic with kernel

```text
A_ij = 0.5 * [H_i(y_i) + H_j(y_j) - H_i(y_j) - H_j(y_i)].
```

Therefore `T_c = P_c + R_c` exactly for every finite sample. Population-wise,

```text
R_c = sum_y Cov(H_X(y), 1[Y=y] | phi=c).
```

For the quadratic score this simplifies to

```text
R_c = 2 * sum_y Cov(q_new(y|X)-q_old(y|X), 1[Y=y] | phi=c).
```

This is the new technical mechanism: direct gain attribution through an antisymmetric
within-prior-cell coupling. It is not a subtraction of two separately estimated model
decompositions.

## 3. Linear-time implementation

For cell label counts `m_c[y]`, each example's transported score is

```text
P_i = (dot(H_i, m_c) - H_i[y_i]) / (n_c - 1).
R_i = H_i[y_i] - P_i.
```

Averaging gives `P_c` and `R_c` in `O(n_c*K)` rather than `O(n_c**2)`. Dataset-level
estimates weight cells by their number of identified examples. Singleton cells are
unidentified and reported rather than smoothed.

## 4. Inference

The implementation computes the Hájek projection of the order-two U-statistic and
aggregates influence contributions by image for a one-way cluster-robust confidence
interval. It also offers a cell-stratified cyclic-label randomization test. The latter
is exact under the sharp null that labels are exchangeable relative to frozen model
outputs within each cell; for datasets with multiple observations per image, the
image-clustered interval is primary.

## 5. Relation to classical score decomposition and two new identities

`R_c` is a model-pair relative of the classical reliability/resolution/uncertainty
partition of a single proper score (Murphy 1973; DeGroot & Fienberg 1983; Brocker 2009):
conditioned on a grouping variable, a proper score splits into calibration and
resolution, and resolution is a within-group covariance between forecast and outcome.
WAGER forms the paired gain vector `H_x(y)` first and decomposes the *contrast* between
two models in one pass, rather than decomposing each model separately and subtracting.
This buys two exact results the single-model decomposition does not have:

- **Attenuation.** The naive in-sample plug-in transported score
  `P_tilde_i = mean_j H_i(y_j)` over the whole cell (including `i`) relates to WAGER's
  leave-one-out `P_i` by `P_tilde_i = P_i + R_i / n_c`, so the plug-in's implied
  alignment `H_i(y_i) - P_tilde_i` is exactly `(n_c - 1)/n_c` times WAGER's `R_i` --
  biased at every finite `n_c`, worst at small cells. This is why the redesign needs no
  projection/evaluation split: leave-one-out transport removes the self-prediction bias
  exactly, at the full sample.
- **Coarsening.** If `phi_bar` is any coarsening of `phi` (so each `phi_bar`-cell is a
  union of `phi`-cells), then `R_{c_bar} = E[R_C | phi_bar = c_bar] + between-cell
  covariance term`, by the law of total covariance applied per label and summed. The
  second term is not sign-definite, so coarsening the audit cell is never guaranteed
  neutral -- only the finest identified partition isolates alignment gain net of every
  prior regularity expressible in `phi`.

Proofs and unit tests: `manuscript/7appendix.tex` (Appendix A) and
`tests/test_antisymmetric.py` (`test_attenuation_proposition_matches_insample_plugin`,
`test_coarsening_proposition_law_of_total_covariance`).

## 6. Interpretation

- `R > 0`: the new model improves prediction-label alignment within the declared prior
  cells.
- `P > 0`: some improvement survives after instance assignments are broken and is
  prior-recoverable.
- `R/T` is descriptive only when `T > 0`; it may exceed one if alignment improves while
  prior fitting worsens.
- A positive `R` is not automatically causal reasoning. Any unmeasured within-cell
  shortcut can contribute, so `phi` must be justified and stress-tested.

Reference implementation: `wager/antisymmetric.py`.
