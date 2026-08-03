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

The estimator and every analysis step are pure NumPy and need no GPU. Only the model
training that *produces* the probability matrices does.

```bash
conda run -n py313 python -m pytest tests -q
conda run -n py313 python experiments/antisymmetric_simulation.py
conda run -n py313 python experiments/run_sgg_wager.py           # main VG study
conda run -n py313 python experiments/antisymmetric_ablations.py # sensitivity checks
conda run -n py313 python experiments/make_antisymmetric_figures.py
```

`run_sgg_wager.py` trains the five controlled PredCls predictors and writes
`results/antisymmetric_results.json`; if `results/sgg_dists.npz` is already present it
loads those cached distributions instead, so the analysis can be rerun without
retraining. Because every model in a comparison must come from the same run, the cache
is used wholesale or not at all.

### Analyses driven by cached model outputs

```bash
conda run -n py313 python experiments/run_cifar_lt_wager.py       # cross-domain study
conda run -n py313 python experiments/make_cifar_figures.py
conda run -n py313 python experiments/run_vg_visual_wager.py      # real-pixel study
conda run -n py313 python experiments/make_vg_visual_figure.py
conda run -n py313 python experiments/make_dataset_samples_figure.py
```

Each expects the corresponding `.npz` of cached test probabilities under `data/`
(`data/cifar_lt/`, `data/vg_visual/`). Those are produced by the GPU-side scripts in
`experiments/colab_*.py`, which train the models and write only the small probability
caches back:

| script | produces |
|---|---|
| `colab_cifar_lt_train.py` | CIFAR-100-LT cross-entropy and class-balanced ResNet-32 |
| `colab_cifar_drw_train.py` | adds the deferred-reweighting arm |
| `colab_vg_visual.py` | matched-subsample CLIP / geometry / class-only VG models |

`make_dataset_samples_figure.py` fetches its handful of source images on demand, so it
needs no bulk download.

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
