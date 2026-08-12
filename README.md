# WAGER — Within-cell Antisymmetric Gain Evaluation of Resolution

When two models are compared on a benchmark whose labels are partly determined by a
feature both of them observe, the score difference confounds two things: a closer fit to
that feature's conditional label distribution, and better prediction of individual cases.
WAGER separates them exactly. It matches test examples sharing a declared feature `phi`,
crosses their labels, and splits the observed gain:

```text
total gain = prior-transported gain + instance-alignment gain
```

The alignment term is an order-two U-statistic. Under the quadratic score it equals the
within-cell covariance the new model has gained between its probability changes and the
label, which identifies it with the resolution term of the classical proper-score
decomposition (Murphy 1973; DeGroot & Fienberg 1983; Bröcker 2009) applied to a model
*pair* rather than to one forecaster. A change that is constant inside each cell — a pure
prior refit — has exactly zero alignment gain, by construction rather than by
approximation.

There is no fitted nuisance model, no sample splitting, and no tuning parameter. Two
exact results follow from the construction:

- **Attenuation.** Using the cell's own label frequency as the counterfactual (the
  in-sample plug-in) is biased by exactly `(n_c - 1)/n_c` relative to leave-one-out
  transport, worst in small cells. This is why no held-out fold is needed.
- **Coarsening.** Merging cells changes the estimand by an explicit between-cell
  covariance term (law of total covariance), which is not sign-definite — so a coarser
  audit feature cannot be assumed neutral.

Inference is by Hájek influence function with cluster-robust intervals, plus a
cell-stratified randomization test.

## Quick start

```python
from wager import decompose_gain

r = decompose_gain(
    q_new, q_old, y, phi,     # two (N, K) probability matrices, labels, cell ids
    groups=image_ids,          # optional: cluster-robust intervals
    score="brier",             # or "log"
)
print(r.total_gain, r.prior_gain, r.alignment_gain, r.alignment_ci)
```

Four aligned arrays are all it needs, so any pair of frozen probabilistic models can be
audited from cached predictions. Cost is `O(NK)`.

### Reading the result honestly

- Cells with fewer than two examples cannot identify a within-cell counterfactual. WAGER
  excludes them and reports `coverage` rather than smoothing over them.
- The interpretation is conditional on `phi`. A positive alignment gain means the new
  model aligns its probability changes with the right example better *among cases sharing
  that feature* — not that it reasons, or that the improvement is causal.
- The channel credits **any** unrecorded signal varying inside a cell, including
  shortcuts. Choosing `phi` to be the label itself makes every cell homogeneous and forces
  the alignment gain to zero as an algebraic artifact.
- The alignment channel is **not invariant to recalibration**: sharpening or softening a
  model moves score between the two channels while adding no information. Compare
  calibration-matched models when they differ visibly in confidence — see
  `experiments/cifar_recalibration_control.py` for the protocol and how much it matters.

`alignment_gain`, `alignment_ci` and `alignment_share` are the names used in the paper;
the earlier `reasoning_*` fields remain as aliases.

## Reproducing the paper

The estimator and every analysis step are pure NumPy and need no GPU; only the model
training that *produces* the probability caches does.

```bash
conda run -n py313 python -m pytest tests -q                        # 13 tests
conda run -n py313 python experiments/verify_manuscript_numbers.py  # 55 quoted values
```

The verifier checks every number quoted in the manuscript against the committed results
files, so a transcription slip or a stale figure fails loudly.

### Analyses

| command | what it produces |
|---|---|
| `antisymmetric_simulation.py` | recovery, null, interval coverage, discriminant validity |
| `run_sgg_wager.py` | main Visual Genome study (trains five controlled predictors) |
| `antisymmetric_ablations.py` | sensitivity to score, cell granularity, minimum cell size |
| `run_sgg_audit_wager.py` | audit of the released MOTIFS / MOTIFS-TDE checkpoints |
| `run_vg_visual_wager.py` | matched-subsample frozen-CLIP study |
| `vg_prior_consequence.py` | post-hoc prior matching and calibration control on VG |
| `vg_metric_bridge.py` | translates score gains into accuracy, MRR and recall@5 |
| `run_cifar_multiseed_wager.py` | CIFAR-100-LT across seeds, ratios, and a logit-adjustment arm |
| `cifar_recalibration_control.py` | held-out temperature protocol for the long-tail study |
| `cifar_covariance_check.py` | independent cross-check of the covariance identity |

Figures: `make_fig1_concept.py`, `make_antisymmetric_figures.py`, `make_cifar_figures.py`,
`make_vg_visual_figure.py`, `make_dataset_samples_figure.py`. The sample-image figures
fetch their few source images on demand, so no bulk download is required.

`run_sgg_wager.py` reuses `results/sgg_dists.npz` if present, so the analysis can be rerun
without retraining. Because every model in a comparison must come from the same run, that
cache is used wholesale or not at all.

### GPU-side scripts

These run on a Colab-style host, train the models, and write back only the small
probability caches that the analyses consume (`data/cifar_lt/`, `data/vg_visual/`,
`data/vg_motifs/`).

| script | produces |
|---|---|
| `colab_cifar_lt_train.py`, `colab_cifar_drw_train.py` | the original CE / CB / DRW ResNet-32 triple |
| `colab_cifar_multiseed.py` | the same triple across seeds and imbalance ratios |
| `colab_vg_visual.py` | matched-subsample CLIP / geometry / class-only VG models |
| `colab_sgg_stage1.py`, `colab_sgg_stage2.py`, `colab_sgg_convert.py` | fetch and patch Scene-Graph-Benchmark, evaluate the released MOTIFS checkpoint in both modes, and convert the dumps to per-relation arrays |

`vg_prepare.py` builds the VG150-style dataset used by the main study from the released
Visual Genome annotations. Note that this is a reconstruction with a frequency-derived
vocabulary and its own image split — the checkpoint audit in `run_sgg_audit_wager.py` uses
the canonical VG150 split instead, and the paper keeps the two settings distinct.

## Layout

```
wager/antisymmetric.py   the estimator: transport, identity, inference
experiments/             analysis drivers, figure scripts, GPU training jobs
tests/                   13 tests, including numerical checks of both propositions
results/*.json           cached outputs every reported number is checked against
manuscript/              the paper (elsarticle), figures, cover letter
algorithm.md             the mathematics in prose
report/REPORT.md         development log across the three revisions
```

See [`algorithm.md`](algorithm.md) for the derivations and
[`manuscript/main.pdf`](manuscript/main.pdf) for the paper.
