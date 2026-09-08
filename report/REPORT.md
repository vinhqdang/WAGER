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

---

## Addendum: fifth revision (2026-09-07), after the JSPI rejection

*Journal of Statistical Planning and Inference* rejected Ms. Ref. No. JSPI-D-26-00452R1
outright. The editors' letter cited insufficient substance and interest; the single
referee report was entirely about presentation, and is worth quoting because it drove
this whole pass:

> The article needs a simple and precise description of what are its main contributions.
> At present, it is not describing anything in simple terms. There is a lot of unexplained
> words and terminology that are making things obscure. [...] The Introduction itself is
> so hard for me to follow and I can barely make sense of what is going on. I think the
> article had something interesting to contribute, but I am not willing to recommend a
> resubmission. I would encourage the author to write technically and in simple
> statistical terms what the article is planning to contribute.

Notably, the referee credited the work with "something interesting to contribute" and
still declined to recommend resubmission, on legibility alone. The prior four revisions
had each added material — four theorems, a third domain, a sensitivity analysis — in
response to desk rejections for insufficient novelty. That strategy had made the paper
harder to read at exactly the rate it made it more substantial. This revision reverses
the direction: nothing was added to the theory, and the paper got shorter where a reader
first meets it.

### What was rewritten

**Title.** ``WAGER: Within-cell Antisymmetric Gain Evaluation of Resolution'' —
four pieces of coined vocabulary before the colon has even done its work — becomes
*An Exact Decomposition of Paired Score Differences: Separating Prior Fit from Within-Group
Resolution*. The acronym survives as the estimator's short name inside the paper and as
the repository name, but no longer greets the reader.

**Abstract.** Rewritten from 335 to ~265 words, opening on the concrete situation ("two
probabilistic classifiers are compared on a test set and the newer one scores higher")
rather than on an attribution question posed in the abstract's own terminology. The
construction is now stated in one sentence of plain English before any of its properties
are claimed.

**Introduction.** Rewritten end to end. It now opens on a worked situation from a real
benchmark — given (`man`, `surfboard`) the relation is usually `riding`, so two models
observing the object classes can differ in score for two quite different reasons — states
the identity in words before any notation, and says explicitly, in standard terms, that
the remainder is the resolution term of the Murphy/DeGroot--Fienberg/Bröcker
decomposition applied to a model pair. The nine-item contribution list is now four items,
each one sentence of plain statistics. Two new subsections were added: a
**terminology table** mapping every term the paper coins to its standard statistical
counterpart (grouping variable/stratifying variable, cell/stratum, transport/within-block
relabelling, resolution gain/resolution difference), and a **scope** subsection stating
the three interpretation limits before any result appears rather than after all of them.

**New Section 2: a worked example.** Four data points, one cell, two labels, all
arithmetic in eighths. Two candidate replacement models — one that moves every case to
the cell's label frequencies, one that moves each case towards its own correct label by
the same amount — exhibit, in numbers a reader can check by hand, every property the rest
of the paper proves in general:

| | total | prior fit | resolution |
|---|---:|---:|---:|
| A (pure prior refit) | 1/8 | 1/8 | **0** |
| B (case-specific shift) | 3/8 | −1/8 | **1/2** |

Model A's exact zero is Theorem 1. Model B's total *understating* its resolution gain is
the paper's thesis in miniature. And the in-sample covariance plug-in for B returns 3/8,
not 1/2, which is exactly the `(n_c-1)/n_c = 3/4` factor of Proposition 1 — so the
attenuation result, previously an appendix-flavoured technicality, is now something the
reader has already seen happen.
`tests/test_antisymmetric.py::test_worked_example_of_the_paper_reproduces_every_printed_value`
checks all of it against the estimator (suite now 17/17).

**Terminology, throughout.** The paper's coinages were replaced with standard vocabulary
wherever one exists: *audit feature*/*prior feature* → **grouping variable**; *audit
cell*/*prior cell* → **cell**; *prior-transported gain* → **prior-fit gain**;
*instance-alignment gain*/*antisymmetric residual* → **within-group resolution gain**
(``antisymmetric'' is retained only where the kernel's antisymmetry is actually used).
This is not cosmetic: *resolution* is the term the statistical literature already uses for
this exact quantity, so the paper now names its own contribution in the words a reader of
that literature would reach for. One collateral collision was caught and fixed — the
randomization test's `p`-value granularity had been described as a "resolution floor",
which now means something else in this paper.

**Restructure.** Sections were reordered around the plain statement and one flagship
application. The audit of two released MOTIFS/MOTIFS-TDE checkpoints stays in the main
text: the models are not ours, the claimed improvement is one the field already reports,
and it is the paper's strongest evidence of usefulness. The other three empirical studies
— our own VG predictors, the frozen-CLIP variant, and long-tailed image and text
classification — moved wholesale to Appendix E, with a one-page main-text summary of what
each adds. The calibration-matching protocol moved *into* the main text, since it is a
property of the estimator rather than of any application. All theory stayed in the main
text: the referee's objection was legibility, not depth, and the editors' substance
objection is not answered by hiding the substance.

Result: main text 26 pages (was ~36 by the same count), total 52 with references and five
appendices. Method section 9 pages, experiments 4, discussion 3.

**Front matter.** Retargeted to be venue-neutral pending a venue decision:
`\journal{}` removed, cover letter rewritten as a fresh-submission letter that leads with
the problem in one paragraph and the contribution in two, highlights and title page
retitled. `revision_notes.tex`/`.pdf` were deleted — they answered a JSPI revision round
that has now closed, and a fresh submission does not carry them.

### Defects found and fixed in passing

- **`Appendix Appendix A`.** `elsarticle` expands `\thesection` to "Appendix~A" inside the
  appendix, so every `Appendix~\ref{...}` in the prose had been rendering as "Appendix
  Appendix A" — all 48 such references in the current draft, and the defect has been
  present since the paper was first typeset in this class without being noticed. Fixed by
  numbering the appendices with bare letters and letting the prose supply the word.
- Four cross-references broke in the restructure (`sec:related-longtail` had been deleted
  with the old related-work section; `Section~\ref{}` prefixes pointing at what are now
  appendices). All resolved; the build has no undefined references and one 1.9pt overfull
  box in float output.
- `experiments/verify_manuscript_numbers.py` asserts each literal against a *named*
  manuscript file, so moving four studies to an appendix invalidated 52 of its 83 entries'
  file fields. Retargeted; all 83 numbers still trace to committed results. No reported
  value changed in this revision — this was a presentation pass, and the verifier is what
  proves it.

### Venue

Elsevier offered five transfer suggestions against the JSPI submission. Assessed against
what the paper actually is — an estimand for a *paired score differential* with exact
finite-sample and asymptotic inference — they rank as follows.

1. **Econometrics and Statistics** (IF 2.5, CiteScore 4.0) — recommended when this
   section was written, and **withdrawn** by the 2026-09-07 panel; see the note at the end
   of this section before acting on it. The
   paper's inferential target is the comparison of two forecasters, and
   Corollary~\ref{cor:dm} establishes that its undecomposed statistic *is* a clustered
   Diebold--Mariano/Giacomini--White test. Comparative predictive ability is native
   territory for this journal, and its Statistics section takes methodology with
   substantial data applications, so the benchmark studies are an asset rather than a
   mismatch. The paper would need its forecast-evaluation framing moved forward, which
   the restructured related-work section (Section 3.2) has already done.
2. **Journal of Computational Mathematics and Data Science** (CiteScore 5.3, no IF) — a
   plausible fallback: computational methodology with data-science applications, and the
   $O(NK)$ algorithm plus released code fit. Low visibility among statisticians is the
   cost.
3. **Computational Statistics & Data Analysis** — **do not transfer.** CSDA desk-rejected
   this manuscript in August 2026 (see the fourth-revision addendum above); the
   suggestion engine has no way to know that. Re-entering the same editorial office with
   a paper it already declined wastes a submission cycle.
4. **Results in Applied Mathematics**, **Journal of Computational and Applied
   Mathematics** — poor fit. Both are applied/numerical mathematics venues; nothing in
   the paper is a numerical-analysis contribution, and neither readership works on
   forecast evaluation or scoring rules.

A transfer would carry the *old* title and files, so if the transfer route is taken the
restructured manuscript should be uploaded in place of the transferred version before the
submission is completed. The front matter is deliberately left venue-neutral
(`\journal{}` removed, cover letter addressed to `[Journal name]`) so that retargeting is
a one-line change.

### Correction to the above, after the 2026-09-07 panel

The ranking above was written from the paper's *theory* and is wrong about its *evidence*.
The panel's Journal-Fit seat raised a CRITICAL finding that settles the point: the
manuscript contains no econometric or forecasting application at all. Thirty of its
references are ML conference papers (13 CVPR, 5 ICML, 4 NeurIPS, 3 ICLR) against exactly
two econometrics journal citations — Diebold & Mariano (1995) and Giacomini & White (2006)
— with nothing from that literature after 2006 and no discussion of frozen versus
estimated forecasts. That seat judged the gap not repairable by rewriting, and its
recommendation flips to reject-at-venue for Econometrics and Statistics without an added
application.

So the recommendation is now conditional, and the condition is an author decision rather
than an editorial one:

- **With a forecasting application added**, Econometrics and Statistics remains the best
  fit on the transfer list, for the Corollary 3 reason given above.
- **Without one**, the honest targets are the *International Journal of Forecasting*, the
  *Journal of Forecasting*, or JBES if the Diebold–Mariano framing is kept and given real
  forecasting evidence; or JMLR/TMLR if the benchmark-auditing framing is kept instead and
  the statistical apparatus is presented as the means rather than the claim.
- **CSDA remains a non-option** regardless, for the reason above: it already desk-rejected
  this manuscript.

Nothing in the panel treated this as a defect in the work — the finding is about audience,
not correctness — and no rewriting in the sixth revision addressed it, deliberately.

---

## Addendum: sixth revision (2026-09-07), after the panel found the framing wrong

The fifth revision above was a presentation pass, and a 5-seat simulated panel run against
it (`reviews/2026-09-07-panel/`) returned Major Revision from all four seats that issue a
recommendation, with three CRITICAL findings. One of them invalidated the framing that
pass had just built. The full editorial synthesis, roadmap and panel provenance are in
that directory; what follows is what changed and what was verified before changing it.

### The central correction: ΔR is not the classical resolution term

The Domain seat and, independently, the Methodology seat found that the paper's headline
identification is false. The argument is short and decisive, and the paper had contained
its own refutation for three revisions:

- Classical DeGroot–Fienberg resolution depends on a forecast only through the partition
  its level sets generate, so it is invariant under any strictly monotone rescaling of
  forecast values.
- The paper's own Discussion states that ΔR is **not** invariant to recalibration — which
  is why the calibration-matching protocol exists.
- Both cannot be true of one quantity.

Verified directly before acting. Under a strictly monotone recalibration, classical
resolution holds at `0.046160` while the within-cell covariance moves `0.257157 →
0.184819`; on a recalibrated-versus-raw pair the estimator returns `ΔR = −0.072338` where
the difference of classical resolutions is exactly `0.000000`. The Methodology seat's
independent counterexample gives `ΔR̂ = −0.35964444` against a classical resolution
difference of exactly `0`.

Theorem 1 is untouched — `ΔR_c = Σ_y Cov(H_X(y), 1{Y=y} | C=c)` is definitional. What was
wrong is the attribution, and it was made structural by the fifth revision, which promoted
"resolution" from an occasional gloss to the paper's primary term and put it in the title.
Corrected throughout:

- **Retitled** to *An Exact Decomposition of Paired Score Differences by Relabelling
  Within Groups* — naming the operation, which is unarguable, rather than an
  interpretation that is false.
- **ΔR renamed** the *within-group covariance gain*. Yates (1982) added as the source of
  the covariance representation, which the paper had been crediting to Murphy and to
  DeGroot & Fienberg. The precise relation — equal to twice a classical resolution
  difference exactly when both models are calibrated within cells, and not otherwise — is
  now stated in the abstract, the introduction, §3.1 and the conclusion.
- "Discrimination" was considered and rejected as a replacement name: standard
  discrimination measures (AUC, the c-statistic) are rank-based and *are* monotone
  invariant, so that name would have reproduced the same error.
- The acronym's expansion is retired. WAGER is now just the software's name.

### The second correction: ΔP is not prior fit either

The Domain seat also found "prior-fit gain" a misnomer, and the paper had no result
characterizing ΔP at all — five revisions had left it named by assumption. Derived and
verified: for the quadratic score,

```
ΔP_c = [ ||p(c) − q̄₀(c)||² − ||p(c) − q̄₁(c)||² ]  −  [ tr Var(q₁|c) − tr Var(q₀|c) ]
```

a mean-forecast-fit improvement minus a within-cell dispersion increase, checked against
the estimator on random inputs to 1e-12. Only the first bracket is prior fit. The second
rewards *less* dispersed predictions at a fixed mean forecast, so ΔP can absorb an entire
gain with both models' mean forecast sitting exactly on the cell frequencies — a
four-point counterexample now in the paper and in the test suite. Added as
**Proposition 2** with an appendix proof; ΔP renamed the *transported gain*, for the
operation rather than an interpretation.

This also fixed the fifth revision's worst self-inflicted error, which the Devil's
Advocate seat caught: §2 had explained model B's `ΔP = −1/8` by saying its prior fit "got
worse", when B's mean-forecast fit in fact *improves* by `+0.09375`. The true explanation
is that dispersion rises by exactly the same `0.09375`, cancelling it, and the `−1/8`
comes from leave-one-out transport removing the `(1/n_c)ΔR̂ = 1/8` the in-sample plug-in
credits to the transported channel. Both numbers were right; the sentence explaining them
was not.

### The third correction: a committed file contradicted the paper's reassurance

The Devil's Advocate seat found that `results/sensitivity_bound.json` — committed with
Proposition 3 in the fourth revision, cited nowhere in the manuscript, and the only
committed results file the verifier did not check — holds `bound_B = 0.232845` and
`robustness_value_rho_dagger = 0.061272` for the main Visual Genome pair. Verified:
`ρ† × B = 0.014267 = |ΔR|` exactly, and at the ρ̄ = 0.1 the paper itself suggests as
plausible, the sharp bound `0.023284` **exceeds** the estimate. §3.5 had meanwhile
asserted that a confounder would need "an implausibly strong, simultaneous effect" to
explain a reported ΔR away, reporting only the crude bound it conceded was orders of
magnitude too loose.

An aggregate correlation of `0.061` is not implausibly strong. §3.5 now reports both
bounds and the robustness value, states that a modest confounder would suffice for the
Visual Genome gains, and notes that the flagship audit is not exposed the same way because
its estimate is already indistinguishable from zero. The file is now in
`verify_manuscript_numbers.py`.

**Corollary 2 re-derived** (Methodology W5): bounding `Σ_y Var(b_y)` label-by-label with
Popoviciu gives `K/4` and discards `Σ_y b_y = 1`, which forces `Σ_y Var(b_y) ≤ 1 − 1/K`.
The free bound is `M√(K−1)` = `14.00`, not `K M / 2` = `50.00`. `sensitivity_bound_check.json`
regenerated; the superseded value is retained in the file for the record.

### Other corrections, each verified before editing

- **Theorem 4's printed sandwich variance was `1/G` times the correct quantity** — the
  `N_*/G` prefactor cancels the `G/(G−1)` numerator, so the stated consistency claim was
  false as printed while Appendix B and the code were right.
- **Conditions (iii) and (v) could not both bind.** (v) forces `N_*/N → 1`, making the
  identified-fraction assumption vacuous; it is dropped rather than stated alongside a
  condition that contradicts it, and the theorem now says plainly that it does not describe
  the regime the applications sit in.
- **The Hájek remainder rate was asserted at the wrong level.** A per-cell `o_p(n_c^{-1/2})`
  does not aggregate to `o_p(N_*^{-1/2})` when the cell count grows. Repaired with the
  degenerate second-order rate `O_p(n_c^{-1})`, which needs only `C = o(√N_*)` — stated as
  Eq. (cellcount).
- **"Most eligible VG150 cells sit at the minimum size n_c = 2" was false**, in three
  places, and it carried the paper's honesty statement about condition (v). The paper's own
  ablation refutes it: 2,286 of 6,346 eligible cells hold fewer than five examples, and
  those carry 2.7% of identified relations. The correction runs in the paper's favour,
  which is precisely why it had to be made rather than defended.
- **The Diebold–Mariano corollary was invoked out of scope.** It is stated at the trivial
  partition for `N⁻¹Σᵢ`, but §4.10 and Appendix E.2 invoked it at non-trivial groupings
  where the reported statistic is the `N_*`-weighted identified-subsample mean. Both now
  carry the subsample qualifier.
- **A false sentence in §4.10**: a resolution term "applied without any conditioning at
  all" is identically zero. Corrected — at the trivial partition ΔR is the *unconditional*
  covariance contrast, and ΔP is not a calibration term.
- **§5.1's "averaging over repeated splits … throughout" was false.** Only CIFAR averages
  (20 splits); the SGG audit and VG-visual each use one fixed-seed split, and the omitted
  between-split sd (`0.001725`) exceeds the audit's reported CI half-width (`0.00115`).
  Stated.
- **Figure 1 was stale in a way this log had claimed was fixed two revisions ago.** The
  committed PNG was still the text-only flowchart titled "Within-cell Antisymmetric Gain
  Evaluation of **Reasoning**" — abandoned terminology, and exactly the jargon the retitle
  removed. `make_fig1_concept.py` had long since superseded it but its output was never
  committed. The script's own labels were updated and the figure regenerated; it now shows
  the two real VG150 relations with crossed labels that the caption describes.
- **Coverage column added** to the granularity table, whose rows target different
  identified subpopulations (99.0% → 86.7%) and so are not four estimates of one quantity.
- **Terminology audit completed past §1**, which is where the fifth revision's sweep had
  stopped: four names for the grouping variable and five for ΔP were still in circulation
  in §4–§6, along with three agreement artefacts ("an cell" ×2, "an covariance").

### Two additions the panel's criticism earned

**A decision the split changes** (§2.1). The Devil's Advocate seat's sharpest point was
that the paper never exhibited a single decision the decomposition would alter — it
disclaimed "says where a gain lives, not whether it is worth having" and then showed no
ranking that reverses. It does now, on the same four points, exactly:

| | benchmark gain | after a label-frequency shift to (¼, ¾) |
|---|---:|---:|
| model A (all transported) | +1/8 | **−3/8** |
| model B (all covariance)  | +3/8 | **+3/8** |

Model A does not merely lose its margin; it becomes *worse* than the model it was meant to
replace, while B is untouched. The decomposition says in advance which is exposed and the
aggregate score does not — ΔP is the part of a reported gain contingent on the evaluation
set's label frequencies matching deployment, and ΔR is the part that is not.

**Fineness is not a total order** (§6). The Devil's Advocate built an adversarial example
the paper could not answer, and it is now stated as a limitation. Four cases, one model
pair, `ΔT = +0.480` and 100% coverage under all three partitions below:

| declared φ | cells | ΔP | ΔR |
|---|---|---:|---:|
| {1,3},{2,4} | 2×2 | −1.120 | **+1.600** |
| {1,2,3,4} | 1×4 | −0.587 | +1.067 |
| {1,2},{3,4} | 2×2 | +0.480 | **0.000** |

The first and third are equally fine and fully identified and disagree about whether the
improvement is entirely case-level or entirely transported. "Choose the finest defensible
φ" cannot arbitrate, and Proposition 1 is silent because neither coarsens the other. The
paper previously attached this warning only to the degenerate choice φ = Y; the general
version is less comfortable and we have no procedure that resolves it. A
recalibration-invariant rank-based alternative is now discussed too, along with what it
would cost (the exact additivity that is the whole point).

**Adjacent literatures** added, all nine new citations verified against CrossRef records
before use: Yates (1982); Ferro (2007), DelSole & Tippett (2014) and Siegert et al. (2017)
on inference for skill differences, which the paper's gap claim had overstated the silence
of; Oaxaca (1973), Blinder (1973) and DiNardo, Fortin & Lemieux (1996) on decomposing a
gap into composition and conditional behaviour; Mantel & Haenszel (1959) on within-stratum
association and non-collapsibility; Holland & Thayer (1986) on differential item
functioning. Note that the panel's author list for Siegert et al. was wrong and the
CrossRef check caught it.

### State

Main text 34 pages (from 26; the additions above are the cost), 62 total. Suite 20/20;
89 verifier checks, up from 83, the new ones covering the sharp sensitivity bound and the
robustness value. One 1.9pt overfull box, no undefined references. Front matter, README and
`algorithm.md` all carry the corrected framing.

**What is not addressed.** The Journal-Fit seat's CRITICAL — no econometric or forecasting
application, 30 ML conference citations against two econometrics ones — is a venue
judgment, not a defect in the work, and it is the open question for the transfer decision
(see the Venue section above). The panel's remaining Minor findings are tracked in the
roadmap and not all acted on.

---

## Submission status (2026-09-08): under review at Econometrics and Statistics

Submitted to *Econometrics and Statistics* (Elsevier), via the transfer offer that followed
the JSPI rejection.

| field | value |
|---|---|
| Article type | Annals of Statistical Data Science (SDS) |
| Classifications | 10.50 prediction; 10.38 model selection; 10.29 hypothesis testing; 10.33 machine learning |
| Suggested associate editors | Eric Beutner (VU Amsterdam); Ansgar Steland (RWTH Aachen); Armelle Guillou (Strasbourg); Yoonkyung Lee (Ohio State) |
| Files | flat single-file `main.tex` + 8 figures + `ref.bib`; `cover_letter.pdf`; `title_page.pdf` |
| Manuscript state | commit `9304b98`, 61 pp., suite 20/20, verifier 89/89 |

The SDS section was chosen over Part A deliberately: the contribution is statistical and the
applications are ML benchmarks, so routing to the econometrics side would have invited the
fit objection the 2026-09-07 panel raised. The cover letter states the fit problem outright
rather than letting a referee find it.

### Known risk at the time of submission

A scope desk-rejection is the live risk, and it was identified *before* submission rather
than after, so if one arrives it needs no re-diagnosis. Measured on the submitted PDF:

- **Figure 1, page 3, full text width, is two photographs of surfers with bounding boxes.**
  It is the first visual in the paper.
- The abstract's second sentence names "the object-class pair in a relation-prediction
  benchmark."
- The introduction's motivating example is Visual Genome.
- **43 of 76 references (57%) are ML/CV venues or arXiv preprints**; 18 are statistics or
  econometrics journals.

So the first impression is computer vision, and this is the axis all four previous
rejections turned on. CVIU declined it as not meeting their bar; CSDA and JSPI declined it
as insufficiently interesting to statisticians, while JSPI's referee said it "had something
interesting to contribute." The paper reads as computer vision to statisticians and as
statistics to computer-vision people.

A front-door pass was proposed and **not** carried out, because submission had already
happened: rebuild Figure 1 as a schematic without photographs, replace the abstract's CV
example clause, and open on a statistically-native example (industry sector for credit
default, age band for diagnostic prevalence) with the ML benchmarks introduced as the place
the structure is extreme and the data public. That pass is still the right move for any
*statistics* venue.

### Contingency: on rejection, re-aim at computer vision

The author's decision, recorded 2026-09-08. If EcoSta declines, stop trying to enter
statistics venues and target computer vision / machine learning instead. Notes for whoever
picks this up:

**The framing pass inverts.** Everything in the front-door pass above should be done in
reverse. For a CV venue: keep the photographs, promote Figure 1 rather than demote it, lead
with the benchmark problem (frequency baselines are competitive on Visual Genome; mean
recall moves ten points on evidence that is mostly transported), bring the MOTIFS/MOTIFS-TDE
checkpoint audit to the front as the headline result, and compress Sections 3–4 into one
methods section with the proofs, the CLT and the sensitivity theory moved to supplementary
material. The theory is the paper's strength for a statistics audience and its liability for
a CV one; length is also a liability there, since 61 pages is far outside CV norms.

**Do not resubmit to CVIU.** It desk-rejected an earlier and substantially different version
in August 2026 with boilerplate. That version had no Bregman theorem, no CLT, no sensitivity
analysis and no text-domain study, so a resubmission is not obviously futile — but it is a
second attempt at an office that already said no, and the reason was never disclosed.

**Candidate venues**, in the order I would try them:
1. **TMLR** — no page limit, values careful evaluation methodology, and reviews claims rather
   than novelty. The single best match for a long, rigorous, benchmark-auditing paper.
2. **A CV conference with an evaluation/benchmarks track** — the audit of a published
   debiasing method is exactly the kind of result those tracks exist for. Deadline-driven,
   and 61 pages must become 8 plus supplementary.
3. **IJCV** — journal-length CV work, tolerant of methodology, would accept the SGG audit as
   the centrepiece.
4. **JMLR** — a fit on rigour and length, but its reviewers may read the contribution as an
   evaluation metric rather than a learning-theoretic result.

**What travels unchanged.** The estimator, all 20 tests, the 89 verified numbers, and every
correction the 2026-09-07 panel produced. None of that is venue-specific, and the framing
corrections in particular — the remainder is not the classical resolution term, the
transported gain is not prior fit, the sensitivity bound is reported against the paper's own
estimates — must survive any reframing. They were expensive to find and they are what makes
the paper honest.


---

## Addendum: reframed for Pattern Recognition (2026-09-08)

The Econometrics and Statistics submission was sent back for a procedural reason (remove
author details for double-blind review) and, rather than resubmit, the decision was taken to
re-aim at computer vision. The send-back was the cheapest possible exit: no review had
happened and no editor had formed a view.

### What changed, and what did not

The contribution is unchanged. Every framing correction the 2026-09-07 panel forced survives
intact: the remainder is a Yates-type covariance and not the classical resolution term, the
transported gain is not prior fit, and the sensitivity bound is reported against our own
estimates. What changed is presentation: the paper now opens on what a reported benchmark
gain buys, states the MOTIFS/MOTIFS-TDE audit as the headline result, and keeps the
photographic Figure 1 rather than the domain-neutral schematic built for the opposite purpose
(`experiments/make_fig1_schematic.py` is retained unused, in case a statistics venue is ever
targeted again).

### The page limit, and a bet I got wrong

Pattern Recognition's guide states its length rule three times and contradicts itself:
"20-35 pages (incl. figures, tables, references, bio-sketches, appendices)" is immediately
followed by "Appendices are not included in the page limit", while the submission checklist
says "including ... appendices". I built the first version on the one clause that excludes
appendices, reaching 35 main-text pages inside a 78-page document. The author caught it. Two
of the three statements include appendices, so the conservative reading is the right one, and
the fix is the provision I should have used from the start: supplementary material, which the
guide treats as separate files outside the manuscript.

The manuscript is now 35 pages including references, and everything else is a standalone
46-page supplementary document. Getting there took the main text from 67 pages to 31 plus 4
of references:

- The worked example, the controlled-predictor study, the real-pixel study's detail, the
  long-tailed studies, the sensitivity analyses, the proofs, the influence-function
  derivation, the terminology table, the algorithm box, and the statements of the Bregman
  identity, the finite-sample identity, the limit theorem, the sensitivity bound, the
  transported-gain composition and the coarsening proposition all moved to the supplementary,
  each behind a main-text summary that keeps the finding.
- Cut outright: the adjacent-literatures subsection, the broader-applicability subsection
  (which repeated the scope subsection), the preprint-heavy permutation passages, and roughly
  6,000 words of prose.
- The bibliography went 76 to 39 entries. Twelve of those cuts came from thinning citation
  clusters, which the guide separately asks for: it warns against citing groups without
  commenting on them individually, and the related-work section had exactly that pattern.

Cross-document references are hard-coded rather than resolved with `xr`, so each document
compiles standalone: the manuscript cites "Supplementary Section S3", the supplementary cites
"Theorem 1 of the manuscript". `experiments/build_flat_submission.py` now flattens both.

### Also per the guide

Single anonymized review, so author details stay. Added a CRediT statement. The conclusion
was rewritten to exceed the abstract and to cover weaknesses and future work under their own
headings, as the guide requires. Highlights are five bullets, longest 83 characters. The cover
letter answers the three mandatory questions; the state-of-the-art one needed care rather
than a dodge, since an evaluation method has no accuracy to beat, so it names the five works
representing current practice on the same question and says what this adds to them.

### One near-miss, recorded because it nearly went into the paper

Intending to correct eight bibliography entries recorded with arXiv DOIs, I checked them
against CrossRef first. Every hit was spurious --- the CLIP paper matched a paper in
*Aquacultural Engineering*. CrossRef does not index ICML/NeurIPS/ICLR proceedings, and those
entries already carried correct venues. Applied blindly, that pass would have put eight
fabricated attributions into the bibliography.

### State

Manuscript 35 pages (31 body + 4 references), supplementary 46, 39 references of which four
cite a preprint venue. Suite 20/20, verifier 89/89 after repointing file references five
times as material moved. Both documents build clean with no undefined references, and the
flat bundle is confirmed identical to the modular build for both.

## Filling in the submission questionnaire, and what it exposed (2026-09-08)

Pattern Recognition's submission form asks about thirty small factual questions --- word
count, font sizes, margins, reference count, abstract length --- under a heading that calls
references a "common desk-check failure". Answering them honestly meant measuring the built
PDFs rather than the source, and three of the answers came back non-compliant.

### The measurement discipline is the finding

- **Abstract.** Recorded as 249 words from `0abstract.tex`. On the rendered page it was
  254: `$O(NK)$`, `$\Delta R$` and the em dashes are one token each in the source and a
  visible word each to a reader. Now 241, with the thesis sentence ("We decompose the gain
  exactly") that an earlier trim had silently dropped put back.
- **Title.** The guide asks for 14 pt. `elsarticle` sets `\@title` in `\Large`, which is
  14.4 pt at a 10 pt base, so the size is now pinned with `\fontsize{14}{17}\selectfont`.
  At the smaller size the manual line break stranded "Gains" on a line of its own, so the
  title wraps naturally instead.
- **Captions and footnotes.** The guide asks for 8 pt. Captions were unset, inheriting the
  10 pt base; `\usepackage[font=footnotesize,labelfont=bf]{caption}` fixes both documents.
- **References.** The guide requests 35--55. The manuscript's list held 33: `ref.bib` has
  39 entries but six were cited only by the supplementary.

### The cross-reference rot

Checking the reference count turned up something worse. The manuscript and the supplementary
are separate documents, so neither can `\ref` into the other, and the numbers had been
written out by hand. They had gone stale wholesale. The manuscript pointed at Supplementary
Sections S2 through S11 and S10.1--S10.5, of which almost none named the section meant:
proofs were cited as S1, the terminology table as S8, the influence function as S2, the limit
theorem as S6. The supplementary cited manuscript Theorems 2 and 3, Propositions 1 and 2,
Corollaries 1 and 2 and Equations 8, 16, 18 and 20 --- none of which exist in the manuscript
any more, since those results moved into the supplementary itself. Several sites carried a
duplicated word from an earlier `sed` pass ("Theorem Theorem 1 of the manuscript"), and one
subsection was titled "Compute environment for Appendices Section 5.4 of the
manuscript--S15.5".

Renumbering by hand is what produced the mess, so the fix removes hand-numbering entirely.
`experiments/gen_cross_refs.py` reads each document's `.aux` and writes the other a table of
`\csname suppref@<label>\endcsname` definitions; the prose now says `\suppref{app:proofs}`
and `\mainref{sec:sggaudit}`. A label that disappears prints a bold `??`, which
`manuscript/build.sh` greps for after alternating LaTeX passes with the generator. The flat
submission builder drops the `\IfFileExists` guard so a single-file bundle freezes the
current numbers instead of printing `??`. Determining what each of the 105 sites was
*supposed* to point at was the work; keeping them right is now automatic.

Two smaller things fell out of the same audit: three supplementary sections the manuscript
cites had no `\label` at all, the document called itself an appendix in fifteen places
although it is supplementary material with S-numbered sections, and the related-work section
stated the label-shift connection twice --- in Sections 2.2 and 2.3, same two citations,
same forward reference.

### Getting the references right without breaking the page limit

The six missing references were not padding; each is an attribution the main text owed. The
elicited-correlation bound is a Cinelli--Hazlett robustness value and said so nowhere; the
Hajek expansion is the standard route for order-two U-statistics and cited neither Serfling
nor van der Vaart; the CIFAR-100-LT study uses a residual backbone and the text study the
20-Newsgroups corpus, both uncited; and the related-work tour of scene graph generation began
with the frequency baseline without naming the message-passing formulation it is competitive
against. Adding them took the list to 39 and the manuscript to 36 pages, one over.

Closing that page took about 190 words, and the duplicated label-shift paragraph supplied
most of it. The rest came from passages that said the same thing a third time: the four scope
limits are stated in Section 1.3, again in Section 5.1 and again in Section 6, so the
forward statement keeps every limit and every number and drops the restatement. Nothing was
cut that is stated only once.

### Three answers that are the author's, not ours

The questionnaire has three items that are decisions rather than measurements, and
`submission_notes/pattern_recognition_questionnaire.md` flags them as such: the Software
Impacts co-submission (recommend declining --- a second reviewed article about the same
released code adds a fee and a review process without adding reach), the SSRN preprint
(recommend accepting --- free DOI, no editorial effect), and the data statement. On the last,
"Data will be made available on request" is the default option and it understates a release
that is already public; worse, Pattern Recognition applies Elsevier's Option C, which wants a
deposit that can be *cited*, and GitHub has no DOI. The accurate answer is the
public-repository option plus a Zenodo DOI for the release.

One item is flagged to check rather than answer: "under consideration elsewhere" can be
answered No only once every earlier statistics-venue submission is closed, and a manuscript
sent back for double-blind reformatting rather than withdrawn may still be open in that
system. The cover letter makes the same claim, so the two have to agree.

### State

Manuscript 35 pages (31 text and declarations + 4 references), supplementary 45, 39
references of which four cite a preprint venue, abstract 241 words, title 14 words at 14 pt,
7 keywords, 5 highlights at most 83 characters, 6 numbered sections and 24 subsections.
Suite 20/20, verifier 89/89. Both documents build with no undefined citation, no undefined
reference and no unresolved cross-document reference, and the flat bundle renders identically
to the modular build for both. Deliverables: manuscript, supplementary, cover letter (2 pp,
1,078 words), highlights, title page, `declarations.docx` for the attach-files step, and
`code.zip` (61 files).
