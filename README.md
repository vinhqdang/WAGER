# WAGER — Wealth-Anchored Gain Estimation of Reasoning

A distribution-free, **anytime-valid** framework that decomposes a computer-vision
benchmark gain into a *prior-recoverable* part (fitting annotation-frequency
priors) and a *genuine visual-reasoning* part, with a finite-sample validity
certificate. Target venue: **WACV 2027** (Evaluations & Datasets track).

See [`algorithm.md`](algorithm.md) for the full specification and
[`report/REPORT.md`](report/REPORT.md) for results.

## What WAGER answers

> *"How much of a reported gain from method `f` to `f'` is real visual reasoning,
> and how much is just better fitting of the annotation-frequency prior — and with
> what confidence?"*

For a fixed model `f` it constructs a **self-prior projection** `q̄_f` (the model's
own predictions collapsed onto the frequency-defining features `φ`), then runs a
**testing-by-betting** capital process that wagers on `f` out-predicting `q̄_f` on
held-out data. From that single process it reads:

- an **e-value** — a distribution-free certificate that the model uses image
  information beyond the prior (Theorem 1, via Ville's inequality);
- a **growth rate** equal to the model's *usable reasoning information* beyond the
  prior (Theorem 2);
- the **Reasoning Gain Ratio (RGR)** with an anytime-valid confidence interval
  (Theorem 4): `RGR < 0.5` flags a gain as *non-substantive*.

## Install

```bash
conda activate py313           # Python 3.13, NumPy, SciPy, PyTorch (CUDA optional)
pip install -r requirements.txt
```

## Reproduce

```bash
# unit tests (Ville control, coverage, model=prior => I_reason ~ 0)
pytest tests/ -q

# Phase 1 -- validity & power simulations (the credibility backbone)
python experiments/phase1_simulation.py

# Phase 2 -- real Visual Genome PredCls study
python experiments/vg_prepare.py                 # parse downloaded relationships.json.zip
python experiments/run_sgg_wager.py              # build models + run WAGER (GPU for MLPs)

# figures
python experiments/make_figures.py
```

`results/` holds the JSON outputs and `results/figures/` the plots; the write-up
is in `report/REPORT.md`.

## Package layout

| Module | Contents |
|---|---|
| `wager/core.py` | self-prior projection (KT + hierarchical empirical-Bayes backoff + Jensen debias), ONS betting, wealth process, anytime-valid betting CI |
| `wager/pipeline.py` | `ModelData`, R-permutation (image-blocked) driver, frozen train-fit projection path |
| `wager/rgr.py` | Reasoning Gain Ratio with Fieller and anytime-valid CIs + verdict |
| `experiments/` | synthetic generator, Phase-1 gates, VG data prep, SGG models, figures |

## Key design points

- **Self-prior projection as a frozen forecaster.** Comparing `f` to its *own*
  frequency-collapsed self (not an external FREQ table) makes the null exact
  without knowing the true prior and is provably calibration-invariant (Cor. 3).
- **Hierarchical backoff** (cell → coarse key → global) and a second-order Jensen
  bias correction keep the projection honest on heavy-tailed real data — this is
  what makes the FREQ anchor (`I_reason ≈ 0`, `e ≈ 1`) hold.
- **Everything operates on cached probability vectors**, so the GPU is used only
  once to produce logits; all WAGER computation is CPU NumPy.
