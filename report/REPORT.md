# WAGER redesign report

_Within-cell Antisymmetric Gain Evaluation of Resolution_

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

**Real-pixel experiment (new).** A frozen CLIP ViT-B/32 encoder replaces
annotation-derived box geometry. All three compared predictors train on the same 100,000
relations and differ only in features, so a difference between them isolates feature
content rather than training-set size; the audit uses the full 229,605-relation test
split.

| Comparison | Accuracy | Total | Prior | Alignment (95% CI) |
|---|---|---:|---:|---:|
| SPATIAL-S vs CLASS-S | 0.6467 / 0.6416 | +0.00503 | -0.00520 | +0.01023 [0.00967, 0.01079] |
| VISUAL-S vs CLASS-S  | 0.6161 / 0.6416 | -0.04152 | -0.05816 | **+0.01665** [0.01534, 0.01796] |
| VISUAL-S vs SPATIAL-S| 0.6161 / 0.6467 | -0.04655 | -0.05296 | **+0.00641** [0.00514, 0.00769] |

By every aggregate measure the CLIP model is the worst of the three, scoring 0.04655
below the box-geometry model and three accuracy points lower; an evaluator reading either
number would discard it. The decomposition shows its entire deficit sits in the prior
channel while its instance alignment is significantly *better* (p=.002), and that pixels
buy more alignment over the class-only baseline than box geometry does (+0.01665 versus
+0.01023, well-separated intervals). Real image content therefore carries more
instance-specific signal than the geometric proxy standing in for it.

Together with the CIFAR-100-LT case the two experiments bracket the failure mode from
both sides: there a near-zero total gain concealed a large alignment loss, here a clearly
negative total conceals a real alignment gain. In both the aggregate score is not merely
imprecise but actively misleading.

**Venue.** Reformatted for Computer Vision and Image Understanding (Elsevier
`elsarticle`): anonymized manuscript plus separate title page for double-anonymized
review, abstract held to 249 of 250 permitted words, highlights file with each bullet
inside the 85-character limit, and declarations of generative AI use, CRediT
contributions, competing interests and funding.

**Reproduction cost, for planning.** The real-pixel job takes roughly an hour end to end
on one T4: 17 minutes to fetch 10.14 GB covering 71,990 images (3 unavailable upstream),
about 35 minutes to encode 422,143 unique crops at ~207/s, then training. Crops are
deduplicated by (image, box) beforehand, which removes 36.0% of the encoder work.

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

---

## Addendum: third revision (2026-08-11), after the CVIU desk rejection

The manuscript was desk-rejected by CVIU with only the boilerplate that it "does not meet
the required quality standards." With no reviewer report to work from, a five-perspective
review panel was simulated (editor, methodologist, domain expert, cross-disciplinary
reviewer, devil's advocate) and its findings drove this revision. The reports and the
resulting roadmap are in `reviews/2026-08-10-panel/`. Two independent checks in that pass
found the proofs correct and every printed number traceable to a committed results file,
so the work below is about identification, coverage, and framing rather than corrections.

### The calibration confound (the panel's one critical finding)

The alignment channel is a covariance between probability movements and labels, so it is
**not invariant to monotone recalibration**: softening an overconfident model moves score
mass from alignment to prior while adding no information about any individual example.
Temperature-scaling the CIFAR baseline alone reproduces almost exactly the channel split
the paper had attributed to class-balanced re-weighting.

The fix is a protocol, not a retraction. Each model's temperature is now fitted by
held-out likelihood on half the test split and the audit runs on the disjoint half, over
twenty random splits (`experiments/cifar_recalibration_control.py`). The corrected reading
is stronger than the original:

| Comparison | Regime | Total | Prior | Alignment |
|---|---|---:|---:|---:|
| CB vs CE | raw | +0.00208 | +0.19635 | -0.19427 |
| CB vs CE | calibration-matched | -0.12912 | +0.11079 | **-0.23991** |
| DRW vs CE | raw | +0.06712 | +0.04258 | +0.02454 |
| DRW vs CE | calibration-matched | +0.02173 | +0.00216 | **+0.01957** |
| CE recalibrated vs CE | control | +0.20495 | +0.37960 | -0.17464 |

Class-balanced re-weighting has genuinely lost within-class discrimination rather than
trading it for prior fit, and the deferred schedule's improvement is almost entirely
instance alignment -- the "two-thirds prior-recoverable" claim of the previous revision
was itself a calibration artifact.

### Consequence and falsification tests

- **Prior matching on Visual Genome** (`experiments/vg_prior_consequence.py`). Correcting
  a model's within-cell prior toward the training histogram registers as almost pure
  prior channel (+0.02401 prior against +0.00111 alignment), as a correction carrying no
  instance information must. It halves the CLIP model's aggregate deficit
  (-0.04655 to -0.02143) while its alignment advantage persists (+0.00752), and the
  advantage also survives calibration matching (+0.00467, CI [+0.00314, +0.00621]).
- **Logit adjustment on CIFAR** falsifies the natural guess in an instructive direction:
  it is *not* a pure prior move at the superclass audit. Its within-cell component is
  multiplicative in each example's own probabilities, so calibration-matched it reads as
  almost pure alignment (+0.032) while achieving the best balanced accuracy of any arm.
  Together the two corrections show transport separating histogram-level from
  instance-coupled adjustments.

### Validation of the instrument itself

`experiments/antisymmetric_simulation.py` gained four arms:

- **Interval coverage** in a VG-like regime (image-clustered examples, Zipf cell sizes
  dominated by `n_c = 2`): the cluster-robust interval covers in 94.0% of 500 runs; an
  interval ignoring clustering covers in 88.6%.
- **Calibration-only alternative**: raw alignment -0.488, calibration-matched -0.0003.
- **Prior-only improvement**: alignment centred at zero (0.0002) with a clearly positive
  prior channel -- no leakage.
- **Unrecorded within-cell shortcut**: credited to alignment (+0.041), quantifying the
  documented limitation that the channel measures all within-cell signal relative to the
  declared `phi`.

### Seeds and imbalance ratios

Single-seed intervals cannot support method-level claims, so the CIFAR triple was
retrained across seeds and imbalance ratios (`experiments/colab_cifar_multiseed.py`,
`experiments/run_cifar_multiseed_wager.py`). The corrected conclusions replicate, and the
across-seed spread is larger than test-set sampling error -- which is the honest
uncertainty for any statement about a training method.

### Statistical completeness

Influence function derived (it was asserted) and the identified-subpopulation estimand
defined, both in Appendix B; Theorem 2 now states i.i.d.-within-cell where exchangeability
was too weak for the claimed unbiasedness; the coarsening prose states its vanishing
condition precisely; the exact-zero interval is footnoted as exact by construction; the
`p = .002` randomization floor and the absence of multiplicity adjustment are stated.
Training details the tables relied on (FREQ smoothing and backoff, per-arm MLP schedules,
the DRW switch epoch) are now in the appendix, and the covariance cross-check the paper
quotes is committed as `experiments/cifar_covariance_check.py`.

### Positioning and presentation

The claim that the field reports "a single aggregate score" was a strawman and is
replaced: mean recall by frequency group, zero-shot recall and GQA-OOD all slice a single
model's performance, but none decomposes a fixed pair's gain with an exact identity and
inference. Canonical references are now cited where their methods are named (Cui, Cao,
Menon, Kang; Xu 2017 for the VG150 PredCls protocol; Lu 2016 for zero-shot recall), and
three adjacent literatures are bridged: comparative forecast evaluation
(Diebold-Mariano, Giacomini-White), label shift (Saerens, Lipton) as the post-hoc face of
the prior channel, and multicalibration for the many-`phi` question. Figure 1 was rebuilt
around two real Visual Genome relations with their labels crossed, replacing a text-only
flowchart. The acronym's R now expands to **Resolution**, which is what the residual
provably is; "Reasoning" over-claimed and travelled without its disclaimer.

`experiments/verify_manuscript_numbers.py` asserts every quoted value against the
committed results files, so a transcription slip fails loudly.

---

## Addendum: fourth revision (2026-08-27), after CSDA desk rejection, for JSPI major revision

The manuscript was desk-rejected by *Computational Statistics and Data Analysis* and is
now under major revision at the *Journal of Statistical Planning and Inference*
(Ms. Ref. No. JSPI-D-26-00452), without a reviewer report available to work from at the
time of this pass. Given JSPI's statistical (rather than CV) readership, this revision
adds theory depth and a third, non-visual application domain rather than further CV
experiments.

### New theory

1. **Theorem (Bregman-score covariance identity).** Generalizes Eq.~(cov-id) from the
   quadratic score to every score generated by a strictly convex, differentiable
   function on the simplex, recovering the quadratic and log-score identities as named
   corollaries rather than an unexplained extra case.
2. **Theorem (asymptotic normality).** A formal central-limit theorem for the
   dataset-level estimator, under a bounded score and a condition ruling out one cluster
   from dominating the sample, with consistency of the already-implemented sandwich
   variance estimator -- this is what licenses reading the image-clustered intervals
   reported throughout the experiments as asymptotically valid rather than a plausible
   finite-sample proxy.
3. **Proposition (sensitivity bound for an unrecorded confounder) and its worst-case
   Corollary.** Turns the paper's standing qualitative caveat -- an unrecorded shortcut
   inflates the alignment channel -- into a numeric bound, elicited from a single
   correlation parameter, with a data-free (Cauchy--Schwarz/Popoviciu) fallback needing
   only the label cardinality and score bound.
4. **Corollary (relation to Diebold--Mariano/Giacomini--White).** At a trivial audit
   feature, the undecomposed statistic and its interval are exactly a clustered DM/GW
   test for the paired score differential, situating WAGER precisely relative to
   comparative forecast evaluation.

A first draft of the sensitivity proposition contained a genuine derivation error: it
claimed the Cauchy-Schwarz bound on the (unobservable) correlation term could be
tightened to a **sum** of per-label square roots of observable per-cell dispersion,
$\sum_y\sqrt{\operatorname{Var}(H(y)\mid c)\,p_y(c)(1-p_y(c))}$. A numeric counterexample
(two labels with anti-correlated dispersion patterns) shows this does not hold in
general; Cauchy--Schwarz only licenses a **product of two square-root sums**,
$\sqrt{\sum_y\operatorname{Var}(H(y)\mid c)}\cdot\sqrt{\sum_yp_y(c)(1-p_y(c))}$. The
proposition, its appendix proof, and the accompanying script
(`experiments/sensitivity_analysis.py`) were corrected before this revision was
finalized; `tests/test_antisymmetric.py::test_sensitivity_bound_ordering_crude_ge_tight_ge_exact_bias`
now checks the corrected ordering (exact bias $\le$ tight bound $\le$ crude bound)
directly, on an explicit discrete population with a known omitted confounder.

### Third domain: long-tailed text classification

`experiments/text_lt_prepare.py`, `text_lt_train.py`, `run_text_lt_wager.py`, and
`make_text_lt_figures.py` apply the identical, unmodified estimator to 20-Newsgroups-LT
(imbalance ratio 100, six coarse topics as `phi`, CE/CB/DRW three-arm protocol mirroring
CIFAR-100-LT). The domain has neither a spatial nor a class-frequency prior, directly
answering the "statistics paper in a CV costume" critique from the earlier CVIU review
panel by demonstrating generality rather than asserting it.

| Comparison | Accuracy | Total | Prior | Alignment |
|---|---|---:|---:|---:|
| CB vs CE  | 0.3532 -> 0.3960 | +0.11388 | +0.07071 | **+0.04317** [0.03664, 0.04970] (p=.002) |
| DRW vs CE | 0.3532 -> 0.3776 | +0.11490 | +0.11335 | +0.00155 [-0.00296, 0.00605] (p=.236) |

The two schedules swap roles relative to CIFAR-100-LT: there, CB's near-zero total
concealed a large alignment *loss* and DRW's gain was genuinely alignment-driven; here,
CB buys real within-topic alignment while DRW's comparably large total gain is 98.6%
prior-transported, its small residual not distinguishable from zero at the superclass
audit and significantly negative once the coarser tier partition is used instead. This
single-run, single-seed result does not yet carry the calibration-matched,
multi-seed protocol applied to CIFAR-100-LT; extending that fuller protocol to text is
the natural next replication.

### Manuscript

Expanded from 25 to 46 pages (`3method.tex`, `7appendix.tex`, `4experiments.tex`,
`5discussion.tex`, `6conclusions.tex`, `ref.bib` all touched). Five new citations were
verified against publisher/arXiv records before being added: Cinelli & Hazlett (2020,
JRSS-B), Rosenbaum (2002), Freidling & Zhao (2025, JCGS), Zhang & Zhao (2026,
Biometrika), Serfling (1980), van der Vaart (1998), and Lang (1995) for 20 Newsgroups.
Three new unit tests verify the new theory numerically, bringing the suite to 16/16.

### Simulated 5-seat review panel (same day), and what it found

Full reports and the editorial synthesis: `reviews/2026-08-27-panel/`.

With no real JSPI referee reports available, a fresh 5-seat simulated panel (Journal-Fit,
Methodology, Domain, Perspective, Devil's Advocate -- independent, blind to each other)
was run against this revision. Genuine, checkable findings, distinct from the earlier
2026-08-10 CVIU panel:

- **Front-matter mismatch (Journal-Fit, Critical).** `main.tex`'s `\journal{}` macro,
  `cover_letter.tex`, and `title_page.tex` still addressed *Computational Statistics and
  Data Analysis* -- the paper's previous venue -- despite the README and this report both
  stating the current target is JSPI. Fixed: retargeted all three files and the
  cover letter's scope argument to JSPI.
- **Score-dependent significance on the flagship claim (Devil's Advocate, Critical).**
  Table `tab:sggaudit`'s calibration-matched log-score row (`dR=+0.04396`) was missing
  its confidence interval in the manuscript, even though the driver script had already
  computed one (`results/sgg_audit_motifs.json`). Adding it (`[+0.04079,+0.04714]`)
  shows the log score's alignment estimate is significantly *positive* -- it does **not**
  reproduce the quadratic score's null (`[-0.00120,+0.00109]`). The abstract, intro,
  conclusion, and cover letter's "instance alignment is statistically unchanged" language
  overstated a single-score result as the headline finding; all four (plus the LaTeX
  table and `highlights.txt`) were rewritten to state precisely what both scores agree on
  (prior-transported dominance, at least an order of magnitude larger than either
  alignment estimate) versus what they disagree on (whether any alignment remainder is
  exactly zero).
- **Related-work argument checked and found wrong (Domain, Major).** Section 2.5's claim
  that "the bias does not cancel under subtraction because it scales with each model's
  own cell counts" is false when both models share the same `phi`-partition: the same
  `(n_c-1)/n_c` attenuation factor applies to each model's own resolution term (same
  `n_c`, shared partition), so subtracting two separately-debiased single-model
  resolutions recovers WAGER's own estimate exactly, term for term. Verified independently
  by hand before editing. The real distinguishing point -- inference for the *contrast*,
  which the single-model literature does not supply even with its own bias correction
  (Ferro & Fricker 2012) or variance estimator (Siegert 2014) -- was kept and sharpened;
  the false point was removed. Added Ferro & Fricker (2012), Siegert (2014), and
  DeLong et al. (1988, paired-correlated-AUC U-statistics) as citations, all verified
  against publisher records.
- **Text-domain claim overstated relative to its own evidence (Devil's Advocate, Major).**
  The Conclusion's framing of the 20-Newsgroups-LT result as the paper's "sharpest
  demonstration" of cross-domain generality did not carry the single-seed,
  non-calibration-matched caveat that the CIFAR-100-LT study itself showed is
  load-bearing (recalibrating a baseline alone moved CIFAR's channels by comparable
  magnitude to the entire text-domain finding). Reworded to state the result as
  suggestive pending the fuller protocol, not as already-earned.
- **"Genuine"/"genuinely" register (Devil's Advocate, Major).** The paper renamed its
  acronym's R from Reasoning to Resolution specifically to stop implying causal or
  compositional understanding, but reused "genuine" a dozen times in exactly the
  sections readers see first. Added one clarifying sentence to the Discussion's existing
  disclaimer rather than rewording every occurrence.

Methodology (proof-by-proof rigor) and Perspective (CV/ML outsider) reports raised
mostly Major/Minor presentation and positioning points -- CIFAR's own CB accuracy not
benchmarked against the literature it re-implements, the benchmarks-should-archive-
probabilities recommendation underestimating real adoption barriers, the paper's length
and CV-heavy proportion being unusual for JSPI's typical submission -- tracked but not
all yet acted on; see the synthesis for the full editorial decision and roadmap.
