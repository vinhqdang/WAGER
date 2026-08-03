# WAGER redesign report

_Within-cell Antisymmetric Gain Evaluation of Reasoning_

## What changed

The self-prior projection, ONS betting process, e-value/growth-rate identity, calibration
corollary, Fieller RGR interval, and `RGR < 0.5` verdict have been removed from the paper.
The new WAGER is a direct algorithm for a pair of frozen models:

1. Form the proper-score gain vector `H_i(y)` of the new model over the old model.
2. Transport labels only among examples with the same declared prior feature `phi`.
3. Subtract crossed assignment gain from observed assignment gain.
4. Report the exact decomposition `total = prior-transported + instance-alignment`.

The alignment component is an order-two U-statistic. Under the quadratic score it equals
twice the within-cell covariance gained between probability changes and the correct label.

## Validation

- Complete repository suite: **18/18 passed**.
- Controlled null: type-I error **0.030** at level 0.05 over 200 runs.
- Signal recovery: monotone for injected signal `beta = 0.0, ..., 0.8`.
- Visual Genome coverage: **227,337 / 229,605 = 99.0%** test relations.

## Visual Genome results

Quadratic-score gains; intervals are image-cluster robust.

| New vs old | Total | Prior-transported | Instance alignment (95% CI) | Share | Randomization p |
|---|---:|---:|---:|---:|---:|
| MLP-CLASS vs FREQ | 0.03386 | 0.03386 | 0.00000 [0.00000, 0.00000] | 0.00 | .724 |
| MLP-SPATIAL vs FREQ | 0.04270 | 0.02832 | 0.01439 [0.01373, 0.01504] | 0.34 | .002 |
| MLP-SPATIAL+ vs FREQ | 0.04644 | 0.02885 | 0.01760 [0.01686, 0.01834] | 0.38 | .002 |
| MLP-SPATIAL vs MLP-CLASS | 0.00885 | -0.00554 | 0.01439 [0.01373, 0.01504] | 1.63 | .002 |
| MLP-SPATIAL+ vs MLP-SPATIAL | 0.00374 | 0.00053 | 0.00321 [0.00289, 0.00353] | 0.86 | .002 |

The share above one for SPATIAL vs CLASS is informative: spatial alignment improves more
than the aggregate score because the prior component deteriorates. This is why the new
paper treats signed alignment gain as primary and does not threshold a ratio.

## Artifacts

- Core: `wager/antisymmetric.py`
- Tests: `tests/test_antisymmetric.py`
- Real-data driver: `experiments/run_sgg_wager.py`
- Simulation: `experiments/antisymmetric_simulation.py`
- Ablations: `experiments/antisymmetric_ablations.py`
- Final manuscript: `manuscript/main.pdf`

## Addendum: second revision (2026-08)

Responding to a further desk rejection citing stale references, insufficient length, and
experiments too simple to support the claims.

**References.** Twenty-two verified 2024--2026 entries added across SGG debiasing,
long-tailed recognition, proper-score decomposition, U-statistics/permutation testing and
shortcut learning. Forty-four of forty-five entries now carry a DOI, each confirmed
against an individual CrossRef or arXiv record rather than constructed from a publisher
pattern; `ojala2010permutation` is deliberately left without one, since JMLR registers no
DOIs and CrossRef's nearest match is a different paper by the same authors. Four metadata
errors were corrected in passing, the most consequential being an entry still recorded as
a preprint that has since appeared in Biometrika under a changed title.

**Cross-domain experiment (new).** The estimator is applied unchanged to long-tailed
image classification on CIFAR-100-LT, using the benchmark's own coarse superclasses as
the audit cell. Taking the fine class label as `phi` would make every cell
label-homogeneous and force the alignment gain to zero as an algebraic artifact, so the
superclass partition is the meaningful choice.

| Comparison | Accuracy | Total | Prior | Alignment |
|---|---|---:|---:|---:|
| CB vs CE  | 0.3662 -> 0.2627 | +0.00143 | +0.19713 | **-0.19569** |
| DRW vs CE | 0.3662 -> 0.3874 | +0.06606 | +0.04206 | **+0.02400** (p=.002) |

Class-balanced re-weighting from initialization produces a near-zero aggregate gain that
conceals two large cancelling channels -- precisely the confound the method exists to
expose -- while the deferred schedule's genuine improvement is roughly two-thirds
prior-refitting and one-third instance alignment, concentrated on rare classes (+0.09009
few-shot against -0.07624 many-shot).

This also yielded an external check on the theory: computing the alignment term from the
covariance identity through an independent code path gives -0.19530, which matches the
estimator's -0.19569 only after applying the `(n_c-1)/n_c` factor of the attenuation
proposition at `n_c = 500`. Theorem 1 and Proposition 1 are thereby confirmed on real
trained models rather than only on synthetic populations.

**Manuscript.** Expanded from 17 to 27 pages and restructured to six numbered sections.
New figures show the decomposition and per-tier alignment, and real dataset samples
illustrating what an audit cell contains. Prose was revised for sentence-length variety
after a mechanical, uniformly short-sentence cadence was identified: mean sentence length
in the experiments section rose from 22.7 to 26.9 words and sentences under thirteen words
fell from 31.8% to 10.8%.

**Defects found and fixed.** `\mathbb 1` was rendering a wrong glyph for every indicator
in the paper, since `amssymb` defines blackboard-bold letters only. An over-wide display
in Appendix A.3 has been broken across lines, leaving the document with no overfull
boxes. Two passages still described an audit-cell design that had been abandoned.

**Outstanding.** A real-pixel Visual Genome study, in which a frozen CLIP encoder replaces
annotation-derived box geometry, is implemented (`experiments/colab_vg_visual.py`,
`experiments/run_vg_visual_wager.py`, both validated) but not yet run to completion: the
GPU runtime was reclaimed three times mid-job and the account's GPU quota is currently
exhausted. The manuscript carries the design and methodology for that study with its
results section pending.

## Addendum: response to desk rejection for insufficient novelty

The manuscript above was desk-rejected a second time for lacking new knowledge. The
gain-transport algorithm itself was unchanged, but its *technical contribution* was
underspecified: the covariance identity is a model-pair relative of the classical
reliability/resolution decomposition of a proper score (Murphy 1973; DeGroot & Fienberg
1983; Brocker 2009), and the paper did not say so or state what is new relative to it.
This pass adds:

1. An explicit Related Work subsection positioning WAGER against that classical
   decomposition and stating precisely what it adds: a paired-contrast construction,
   an exact finite-sample identity, and inference for a specific model-to-model gain,
   none of which the single-model decomposition supplies.
2. **Proposition (exact attenuation of the in-sample plug-in).** The naive in-sample
   plug-in prior (fit a cell's own label frequency and use it as the counterfactual) is
   biased by a deterministic factor `(n_c - 1)/n_c` relative to WAGER's leave-one-out
   estimate. This gives a closed-form reason -- not just a design choice -- for why the
   redesign needs no projection/evaluation fold: leave-one-out transport removes the
   bias exactly, at the full sample, for every `phi`-cell with `n_c >= 2`.
3. **Proposition (coarsening decomposition).** Merging prior cells changes the
   population alignment gain by an exact between-cell covariance term (law of total
   covariance), not sign-definite. This explains, rather than merely reports, why
   coarsening `phi` from class-pair to subject-only cells raised the estimated alignment
   gain in the sensitivity analysis, and formalizes why the finest identified partition
   is the conservative default.
4. A new sensitivity table (`Table 3` in the manuscript) replacing inline prose numbers,
   and two new unit tests verifying both propositions
   (`test_attenuation_proposition_matches_insample_plugin`,
   `test_coarsening_proposition_law_of_total_covariance`), the second against an
   explicit discrete population computed independently of the estimator's own code path.
5. A bibliography cleanup removing 32 uncited entries left over from the pre-redesign
   (betting/e-value) draft.

Both propositions are proved in Appendix A of the manuscript and verified numerically in
`tests/test_antisymmetric.py`; see `algorithm.md` §5 for a plain-language summary.
