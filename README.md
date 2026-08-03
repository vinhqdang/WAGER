# WAGER — Within-cell Antisymmetric Gain Evaluation of Reasoning

WAGER attributes the proper-score improvement between two frozen vision models
without fitting a separate prior baseline. It matches examples that share a declared
prior feature `phi`, crosses their labels, and decomposes the observed gain exactly:

```text
total model gain = prior-transported gain + instance-alignment gain
```

The instance-alignment term is an order-two U-statistic. With the quadratic/Brier
score, it equals twice the within-cell covariance gained between probability changes
and the correct label. A class-only change that is constant inside each prior cell has
exactly zero alignment gain.

## Why this is a new algorithm

The rejected version of WAGER estimated each model's frequency-collapsed projection
and attached a generic betting process. The redesigned method removes that stack. It
operates on the *difference between two models*, creates its counterfactual by
within-cell label transport, and obtains an exact finite-sample identity. There is no
projection fold, smoothing model, clipping constant, betting order, or thresholded gain
ratio.

The covariance identity is a model-pair relative of the classical resolution term in
proper-score decomposition (Murphy 1973; DeGroot & Fienberg 1983; Brocker 2009), applied
to a gain contrast rather than to one forecaster. Two exact results go beyond that
classical decomposition and beyond the rejected precursor:

- **Attenuation.** A naive in-sample plug-in prior (fit the cell's own label frequency
  and use it as the counterfactual, with no held-out evaluation fold) is provably biased
  by a factor `(n_c - 1)/n_c` relative to WAGER's leave-one-out estimate, worst in small
  cells. This is the formal reason the redesign needs no projection/evaluation split.
- **Coarsening.** Merging prior cells changes the estimated alignment gain by an exact
  between-cell covariance term (law of total covariance), which is not sign-definite.
  This explains, rather than just reports, why the finest defensible audit feature is the
  conservative default.

## Reproduce

```powershell
conda run -n py313 python -m pytest tests/test_antisymmetric.py -q
conda run -n py313 python experiments/antisymmetric_simulation.py
conda run -n py313 python experiments/run_sgg_wager.py
conda run -n py313 python experiments/antisymmetric_ablations.py
conda run -n py313 python experiments/make_antisymmetric_figures.py
```

The Visual Genome driver trains five controlled PredCls predictors and writes
`results/antisymmetric_results.json`. The core estimator runs on cached probabilities
in `O(NK)` time.

## Main API

```python
from wager.antisymmetric import decompose_gain

result = decompose_gain(
    q_new, q_old, y, phi,
    groups=image_ids,       # cluster-robust inference
    score="brier",
)
print(result.total_gain, result.prior_gain, result.reasoning_gain)
```

Cells with fewer than two observations cannot identify a within-cell counterfactual;
WAGER excludes them and reports coverage explicitly. The interpretation is always
conditional on the chosen `phi`: a positive alignment gain is evidence of improved
instance-specific prediction beyond that declared prior, not proof of causal or
human-like reasoning.

See [`algorithm.md`](algorithm.md) for the mathematics and
[`manuscript/main.pdf`](manuscript/main.pdf) for the paper.
