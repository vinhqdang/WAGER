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

## 5. Interpretation

- `R > 0`: the new model improves prediction-label alignment within the declared prior
  cells.
- `P > 0`: some improvement survives after instance assignments are broken and is
  prior-recoverable.
- `R/T` is descriptive only when `T > 0`; it may exceed one if alignment improves while
  prior fitting worsens.
- A positive `R` is not automatically causal reasoning. Any unmeasured within-cell
  shortcut can contribute, so `phi` must be justified and stress-tested.

Reference implementation: `wager/antisymmetric.py`.
