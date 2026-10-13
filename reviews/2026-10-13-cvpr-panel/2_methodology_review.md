# Peer Review Report (Peer Reviewer 1, Methodology)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission #***** (anonymous), repository commit 18a72c9
- **Review Date**: 2026-10-13
- **Review Round**: Round 1 (simulated CVPR panel, mode full)

## Reviewer Information
- **Reviewer Role**: Peer Reviewer 1 (Methodology)
- **Reviewer Identity**: Expert in evaluation statistics for vision: calibration, proper scores, U-statistics, equivalence testing, uncertainty on benchmark metrics.
- **Review Focus**: Whether the exact split, its estimator, its intervals, its controls and its equivalence tests support the stated claims about TDE, IETrans and the CLIP model. Literature coverage and cross-disciplinary significance are outside this seat.

### Calibration Status
`NOT_CALIBRATED`

`criteria_binding_unavailable` (no #684 criteria authority was supplied; no venue-alignment claim is made).

## Overall Assessment

### Recommendation
**Major Revision** (borderline; the core identity and estimator are sound and the validation is unusually thorough, but several inferential claims about the two released checkpoints are stated more strongly than the statistics license).

### Confidence Score
4. Core expertise in proper scores, U-statistics and equivalence testing. I could not re-run the checkpoint inference or the recalibration protocol, and I did not examine the replay of the official evaluator. Confidence is a scope disclosure only.

### Summary Assessment
The paper splits the score or mean-recall difference between two frozen models into a within-group transported part and a within-group covariance part, using label transport inside declared cells. The identity is exact (I confirmed it by brute force), the estimator is an order-two U-statistic with a clustered Hájek interval, and the validation includes algebraic-zero, prior-only, shortcut and calibration-only negative controls. The operating-point control (a logit adjustment that changes no within-cell ranking) is a good design for a thresholded metric.

My concerns are about what is inferred from this machinery. (1) The estimator's unbiasedness and interval rest on i.i.d. draws within a cell, but 33% of audited relations share image and boxes (hence identical inputs) with another relation, and dropping same-image partners moves the raw case-level part by about 8%, more than the interval half-width. (2) The equivalence margins are arbitrary, partly tied to the very effect under test, and the audit trail does not show they were fixed before the data. One margin is about 75% of the quantity it bounds. (3) Everything about "TDE" and "IETrans" is one checkpoint each, so the intervals cover test-sampling error only, while the authors' own CIFAR study shows fourfold seed variation. (4) The headline "+0.0045 is confidence, not ranking" is a protocol-dependent quantity read through a weighting-dependent AUC.

These are repairable with re-analysis, narrower wording and an honest margin justification.

## Strengths

### S1: Exact identity, correctly derived and implemented
**Evidence Anchor**: text: Theorem 3 (supplement B.5) "∆T d c = ∆P d c + ∆R d c" and wager/antisymmetric.py `decompose_gain_matrix`.
I recomputed total, transported and covariance parts for a random multi-cell problem by explicit O(n^2) enumeration and matched the library to 1e-15. The 21 unit tests pass. The Hájek influence (2*pm - theta_c - estimate) is the correct projection for a cell-size-weighted order-two U-statistic, including the cell-size term.

### S2: Negative controls that can fail
**Evidence Anchor**: text: Sec. 4 "the case-level gain is 0.00000 with a zero-width interval, an algebraic zero" and the prior-only, shortcut and calibration-only designs.
The calibration-only control (-0.488 raw, -0.0003 matched) honestly exposes the main weakness of a covariance-based part and then shows how the protocol handles it. The hidden-shortcut design states plainly that the case-level part credits any within-cell signal.

### S3: Operating-point control for a thresholded metric
**Evidence Anchor**: table: Table 1 rows LA and TDE-LA (case-level +.0139 for LA, -.0008 [-.0050,+.0033] for TDE-LA).
The paper recognises that a hit metric can show case-level credit from a moved threshold with no new discrimination, and builds a training-free control that isolates this. This is a real methodological contribution and makes the TDE reading far more defensible than the raw split.

### S4: Candid statement of scope and theory gap
**Evidence Anchor**: text: Appendix J "the theorem does not describe the regime the paper’s own applications sit in".
The paper states that the limit theorem does not cover its regime, discloses that the interval undercovers at two-case cells (81.5%), and reports the sign dependence of the proper-score part on protocol and label mix.

### S5: Reported numbers trace to results files
**Evidence Anchor**: table: Table 2 against results/sgg_recall_split*.json (see recomputation log).
Every Table 1 and Table 2 entry I checked matches the committed JSON to rounding.

## Weaknesses

### W1: i.i.d. assumption violated by same-image and identical-input pairs; interval and unbiasedness claims not stress-tested for it
**Problem**: Theorem 3 gives unbiasedness only "when the cell’s examples are drawn i.i.d. from the cell population". In VG, relations from one image share context, and 33.1% of the 183,642 audited relations (60,813) share image and both boxes with another relation, so the model gives them identical outputs and they carry different predicate labels. For such a pair the kernel A_ij is exactly zero, and the transport of a label that is always different from the case's own label is not a draw from an independent coupling. A further 58.7% of relations have some same-image same-cell partner. Only 0.47% of ordered same-cell pairs are same-image, but they dominate small cells, which carry the weight in per-relation averaging.
Probe (raw quadratic score, TDE vs baseline, my code outside the repo): the paper's estimator gives case-level +0.02246 with a clustered 95% interval of half-width 0.0013. Restricting transport to other-image labels gives +0.02444 (+0.0020, about 9% of the part and 1.5 half-widths). By cell size on the same relation set, the shift is +0.0103 (cells of 2-4, 13%), +0.0125 (5-19, 23%), +0.0015 (20-99) and +0.0001 (100+). The same pattern holds for the log score and for LA vs baseline. I could not run this on the matched primary protocol or on hit contrasts, so I cannot say how much of +0.0045 or of the 87% share moves. A synthetic probe with an image-level latent and 8 relations per image gave negligible bias in large cells but 92.0% interval coverage (300 runs, SE about 1.6 points).
**Evidence Anchor**: text: Theorem 3, supplement B.5: "when the cell’s examples are drawn i.i.d. from the cell population"
**Why it matters**: The reported case-level parts and their intervals are the paper's primary currency, and the small-cell bias is of the same size as the intervals. It most affects the small differences (+0.0045, -0.0008, +0.0033) on which the equivalence and "confidence not ranking" readings depend.
**Suggestion**: Transport only to labels from other images (and exclude identical-input partners) as the primary estimator, or report both; give the identity for that variant (it remains an exact split of the observed gain onto a modified transport); show coverage in a simulation with within-image label dependence and duplicate-box multi-label pairs; report the effect of the change on the mean-recall share and on the matched +0.0045.
**Severity**: Major
**Confidence**: 4. Core expertise in U-statistics; probe run on real released outputs, but on raw rather than matched scores.

### W2: Equivalence margins are arbitrary, partly outcome-referenced, not shown to be pre-specified, and in one case nearly as large as the quantity bounded
**Problem**: Three issues.
(a) The AUC margins are one tenth of what box geometry buys on the authors' own reconstructed-split MLPs (±0.0063 relation-weighted, ±0.0032 comparison-weighted). The factor 1/10 has no substantive justification (no downstream-decision argument), and the reference models and data differ from the TDE audit.
(b) The mean-recall margin is one tenth of TDE's mean-recall gain (±0.0097), a margin tied to the outcome under study. TDE's whole case-level part against the baseline is +0.0130, so a margin of 0.0097 is 75% of that part, and "equivalent to zero within a tenth of TDE’s gain" says little about whether the case-level part is small relative to itself.
(c) The text twice says the margin was "fixed in advance"/"declared before the audit", but the script header tags the analysis "(R3-2)", which reads as a response to a reviewer comment, and I could not and did not inspect history to settle this. If added after the TDE AUC was known, the claim needs removing.
The abstract states equivalence under the primary weighting; the comparison-weighted test fails (90% interval [-0.0022,+0.0074] vs ±0.0032) and is mentioned only in Sec. 5.
**Evidence Anchor**: text: experiments/sgg_equivalence.py header "Equivalence margins and minimal detectable effects for the TDE ranking null (R3-2)" and paper Sec. 5 "so we fixed one in advance"
**Why it matters**: The equivalence claim is the paper's answer to "did TDE improve ranking within pairs?". A margin that is arbitrary, possibly post hoc, and large relative to the effect does not bound the effect in a way a reader can interpret.
**Suggestion**: Justify the margin by a decision-relevant quantity (e.g. AUC change that would alter a downstream ranking or a recall point); report equivalence over a grid of margins (a margin curve); give the date or protocol stamp, or drop "in advance"; state in the abstract that the comparison-weighted test does not establish equivalence; give the mean-recall case-level margin as a fraction of its own total.
**Severity**: Major
**Confidence**: 4. Core expertise in equivalence testing.

### W3: One checkpoint per method; intervals cover test-sampling only, yet claims are about "TDE" and "IETrans"
**Problem**: Each released model was run once ("We ran it once"), and IETrans has no matched baseline, so the "TDE" and "IETrans" findings are about single trained weight sets. Image-clustered intervals quantify only test-set sampling. The authors' own CIFAR-100-LT study reports that "magnitude varies roughly fourfold across seeds" and that this is "why a method-level claim needs" seed variation. The abstract and conclusion nonetheless state "TDE’s ranking within pairs is equivalent to the baseline’s" and that TDE's gain is group-level, although Sec. 7 does say "On two released Neural-Motifs checkpoints". The IETrans-vs-baseline comparison confounds relabelling with a separately trained baseline, which the paper states.
**Evidence Anchor**: absence: Sec. 5 and Sec. 7 — expected training-seed uncertainty or an explicit "single checkpoint" qualifier on the method-level equivalence claim; checked abstract, Sec. 5, Sec. 7, Appendix N.5 and P
**Why it matters**: The equivalence conclusion for TDE would be undermined if baseline-vs-TDE AUC changes vary across training seeds by more than the 0.0063 margin; the CLIP comparison gets a five-seed treatment that TDE does not.
**Suggestion**: Retrain baseline and TDE for a few seeds (the authors' own code is public) and report the seed spread of the split and of the AUC change; otherwise rephrase every method-level statement as a statement about the released checkpoint, and treat IETrans as exploratory.
**Severity**: Major
**Confidence**: 4. Core expertise; the authors' own CIFAR table supports the concern.

### W4: The central proper-score reading ("case-level +0.0045 is confidence, not ranking") is protocol-dependent and indirectly inferred
**Problem**: The sign and size of TDE's matched proper-score case-level part depend on the matching family (-0.00006 with temperature only, -0.0184 with a shared temperature, +0.00445 primary), and the paper says so. The "confidence rather than ranking" interpretation is not tested directly (no analysis of within-pair confidence or sharpness conditional on correctness); it is inferred from an AUC whose sign for the CLIP-vs-geometry comparison flips with the weighting (-0.0067 vs +0.0085). The calibration parameters (temperature plus per-class bias, fit by maximum likelihood on a random half) are treated as fixed when forming the interval on the other half, so fitting uncertainty is not propagated; the 20-half check gives a split-to-split sd of about 0.0004 against an interval half-width of about 0.0009. The family is chosen by a stated criterion, which is sensible, but a model-specific within-cell confidence pattern (the residual) cannot be removed by any per-class family, so "matched" does not mean "confidence-equal".
**Evidence Anchor**: text: Sec. 5 "A case-level gain with no change in within-cell ranking is confidence: within a pair, TDE is more certain where it is right."
**Why it matters**: The abstract presents the +0.0045 as "confidence within pairs, not ranking", an interpretive claim that goes beyond a covariance whose sign depends on protocol.
**Suggestion**: Test the claim directly (e.g. compare case-level parts after a within-cell monotone, case-dependent confidence rescaling, or show reliability and sharpness conditional on within-cell rank); propagate calibration-fit uncertainty by cross-fitting the halves and reporting the combined interval; present the primary-protocol value with the temperature-only value in the abstract, or soften the sentence to "consistent with".
**Severity**: Major
**Confidence**: 3. Core expertise in calibration; I could not recompute matched values.

### W5: Headline share is for a surrogate statistic, not the official mean recall
**Problem**: The first sentence concerns the ten points of the official per-image mean recall (+0.1017 at K=50), but the 87% and its interval are for a micro-pooled version (+0.0972), which "tracks the official per-image average but is not it". No bound or bridge shows the share for the official statistic is similar; the paper cannot split it exactly.
**Evidence Anchor**: text: Sec. 1 "it tracks the official per-image average but is not it"
**Why it matters**: A reader will take "87% of the ten points" at face value. The gap between 0.0972 and 0.1017 is 0.0045, itself as large as the proper-score part discussed in W4.
**Suggestion**: Report the per-image-averaged share under an exact per-image split if one exists, or an explicit sensitivity (e.g. image-weighted pooling), and place the micro-pooled qualifier next to every use of 87%.
**Severity**: Minor
**Confidence**: 3. Methodology reading; per-image evaluation internals not reviewed.

### W6: Many configurations, no multiplicity accounting, and the abstract reads the favourable ones
**Problem**: Six recall protocols, two weightings, three matching families, two scores, three tasks and several controls. Table 2 shows that without the graph constraint TDE's case-level part against the control is positive at K=100 (+0.0148 [+0.0064,+0.0232]) and borderline at K=50 (+0.0072 [-0.0001,+0.0145]). The paper says it did not adjust the diagnostic p-values. The abstract restricts to "graph-constrained, micro-pooled" and the primary weighting, which is disclosed, but the equivalence claim holds only for one of two AUC weightings.
**Evidence Anchor**: table: Table 2 row ng-mR@100 "TDE vs LA case [CI] +.0148 [+.0064, +.0232]"
**Why it matters**: A reader cannot tell which readings are confirmatory. The abstract's conclusion is conditioned on choices (graph constraint, K=50, primary weighting) whose alternatives partly disagree.
**Suggestion**: Mark confirmatory versus exploratory analyses, state the family of tests for which the headline is claimed, and move the disagreeing configurations into the abstract-level qualification.
**Severity**: Minor
**Confidence**: 3. General statistical practice.

### W7: 90% equivalence interval is a Wald interval from a back-solved SE and is inconsistent with the table's 95% interval
**Problem**: In results/sgg_equivalence.json the relation-weighted TDE-vs-baseline 95% interval (percentile bootstrap) is [-0.00360,+0.00175], but the 90% interval used for TOST is [-0.00373,+0.00077]. The 90% lower bound lies below the 95% lower bound, which cannot hold for nested intervals of one method. The script derives SE as (hi-lo)/(2*1.96) and builds a symmetric Wald interval around the point estimate, discarding the asymmetry of the bootstrap interval.
**Evidence Anchor**: dataset: results/sgg_equivalence.json auc "TDE vs none" relation ci95 [-0.00360, 0.00175] vs ci90 [-0.00373, 0.00077]
**Why it matters**: The conclusion for the relation-weighted comparison survives (the margin is ±0.0063), but the two reported intervals disagree and the comparison-weighted verdict is near-boundary on the upper side.
**Suggestion**: Report the 90% percentile interval from the same bootstrap draws and state which interval method each table uses.
**Severity**: Minor
**Confidence**: 5. Directly recomputed from the committed file.

### W8: Randomization p-values ignore image clustering and test a sharp null
**Problem**: The cyclic within-cell test permutes labels across relations, including relations of one image, and tests label exchangeability relative to model outputs, a sharp null stronger than the weak null Cov = 0 that the interval addresses. With the p-values floored at .002 (499 shifts), tabulated values of ".002" are floor values, not estimates. The paper labels them diagnostic, but p = .002 appears in the text beside clustered intervals.
**Evidence Anchor**: text: supplement N.2 "smallest attainable p-value is 1/500 = .002"
**Why it matters**: Readers may treat it as a test of the same hypothesis as the interval.
**Suggestion**: Permute at image level where possible or drop p-values from the main text and rely on the clustered intervals.
**Severity**: Minor
**Confidence**: 4.

### W9: Asymptotic theory does not cover the regime used
**Problem**: Theorem 4 needs a fixed finite set of cells whose sizes all diverge; the paper's audits have 5,044 to 7,127 cells with a heavy tail, and the authors say this explicitly. Validity of intervals then rests on simulations whose clustering model is a per-image effect and whose cell structure is Zipf. They do not include identical-input pairs or label dependence within image (W1), and my probe found 92% coverage in such a design. At two-case cells coverage is 81.5%.
**Evidence Anchor**: text: Appendix J "the theorem does not describe the regime the paper’s own applications sit in"
**Why it matters**: Nominal coverage is the only guarantee behind every reported interval.
**Suggestion**: Add a parametric or semi-synthetic simulation built from the released audit (real cell sizes, real image multiplicities, duplicate boxes) and report coverage for ΔR and for the share.
**Severity**: Minor
**Confidence**: 4.

### W10: Mechanistic claim rests on a correlation of 0.75
**Problem**: "In PredCls TDE is to first order a learned logit adjustment of the context branch" is supported by one shared vector (99.96% energy) correlated +0.75 with the log training prior. A correlation of 0.75 explains about 56% of its variance; the rest is unexplained by the prior, and the control reproduces the mean-recall gain only at graph-constrained K=50.
**Evidence Anchor**: text: Sec. 5 "correlated +0.75 with the log training prior"
**Why it matters**: It is listed as a contribution ("the mechanism behind TDE’s").
**Suggestion**: Report the regression of that vector on the log prior with its residual, and show what the residual does to the split (e.g. an adjusted control using the fitted vector instead of τ=1).
**Severity**: Minor
**Confidence**: 3.

## Detailed Comments

### Research Questions and Hypotheses
The question (which part of a gain is group-level) is clear and answerable. The estimand is conditional on the declared grouping; the paper shows share = 87% / 90% / 18% under class-pair / refined / subject-only grouping, so "group-level share" is a property of the model pair and the declared grouping, not of the model pair alone.

### Research Design
Two-model paired design with controls is appropriate. The control structure (algebraic zero, operating-point control, prior-only) is better than most audit papers. The weakness is generalisation from one checkpoint (W3).

### Sampling and Data Collection
Test-set inference with image clusters. Singleton cells excluded (1.1% of relations; reported). Same-image and identical-input dependence is not modelled (W1). Checkpoint and baseline training is single-run (W3).

### Analysis Methods
Exact identity: verified. Hájek-cluster interval: derivation correct; analytic SE 0.00064 vs an 80-replicate image bootstrap SD 0.00073 on raw TDE vs baseline (not a discrepancy I can call, since duplicated images contaminate the bootstrap). Equivalence tests: see W2 and W7. Effect sizes are reported; power appears as MDC.

### Results Presentation
Results are complete and tabulated; disagreeing configurations are in Table 2 and the appendices. The abstract is more favourable than the full table (W6).

### Reproducibility
Strong. Code, results JSONs and per-checkpoint probability dumps are provided; unit tests pass. The "pre-declared" claims are not verifiable from the artefacts (W2).

### Methodological Fallacies Detected
- Possible forking paths in protocol and weighting choice (W6), disclosed but not accounted for.
- Equating "no detected change" with equivalence at an arbitrary margin (W2).
- Generalising from one trained model to a method (W3).
- No ecological, Simpson or survivorship problem identified in the PredCls design.

## Questions for Authors
1. What is the effect of restricting transport to other-image labels (and excluding identical-input pairs) on the matched +0.0045, on the 87% share and on its interval? Please give the numbers.
2. Where was the equivalence margin recorded before the audit, and why one tenth? How do conclusions change over a margin grid?
3. Do baseline and TDE trained from several seeds give the same group-level share and AUC difference?
4. Can the "confidence, not ranking" reading be shown directly, for example with a case-dependent monotone rescaling within cells?
5. What does the per-image official mean recall do under the same split, if only as a sensitivity?

## Minor Issues
- The AUC margin is cited as "(Sec. 6)" but the reference models are the MLP-SPATIAL-S and MLP-CLASS-S pair of the supplement.
- IETrans share 97% has a 95% interval that exceeds 1 ([0.90, 1.04]); say so in the main text.
- Main text states "interval 83-91%" for the share; clarify that it is a delta-method interval.
- The abstract phrase "equivalent to the baseline’s within a margin fixed in advance" should name the weighting.

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`. `criteria_binding_unavailable`. No total is derived from these judgements.

| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Estimator correctness and identity | Panel role definition (analysis method audit) | MEETS | text: Theorem 3; wager/antisymmetric.py | Identity exact; U-statistic and influence correct | Matched protocol not recomputed | no |
| Interval validity under dependence | Panel role definition (analysis method audit) | PARTLY_MEETS | text: Theorem 3 i.i.d. condition; W1 probe | Same-image/identical-input pairs bias small-cell parts; theory covers other regime | Probe on raw outputs only | yes, bears on small differences |
| Equivalence-testing design | Panel role definition (statistical reporting adequacy) | PARTLY_MEETS | text: experiments/sgg_equivalence.py header; Sec. 5 | Margins arbitrary, outcome-referenced, pre-specification unverifiable | History not inspected by design | yes |
| Generalisation of method-level claims | Panel role definition (results integrity) | PARTLY_MEETS | absence: Sec. 5/7 seed variation | One checkpoint per method; authors' own seed variation | Cannot know TDE seed variance | yes |
| Controls and negative checks | Panel role definition (research design) | EXCEEDS | text: Sec. 4 controls; Table 1 LA row | Controls that can fail, incl. thresholded-metric control | none identified | no |
| Reproducibility | Panel role definition (reproducibility) | MEETS | dataset: results JSONs, tests | Artefacts trace to numbers | Pre-declaration unverifiable | no |

The recommendation is Major Revision because the unresolved decision-bearing items (W1 to W4) are repairable by re-analysis and rewording, not by a redesign.

## Recomputation Log

Attestation: `no_recomputable_statistics`: the manuscript reports no test statistic with degrees of freedom and no mean/SD on an integer scale, so none of p_from_test_statistic, GRIM, GRIMMER or n_from_df applies (randomization p-values are Monte Carlo counts, floor 1/500). The checks below are my own recomputations.

| # | Claim or object | What I did | Result |
|---|---|---|---|
| 1 | Identity ΔT = ΔP + ΔR, ΔR as pairwise U-statistic | Brute-force enumeration on 60 points, 6 cells, K=4, versus `decompose_gain` | Match to 1e-15 |
| 2 | Unit tests | pytest on tests/test_antisymmetric.py (no cache written) | 21 passed |
| 3 | Table 1/2 parts sum to totals | Hand sums (e.g. .0841+.0130, .0802+.0139, .0039-.0008) | Consistent to rounding (some 0.0001 gaps) |
| 4 | Table 2 entries | Compared with results/sgg_recall_split*.json | All entries compared match (Table 2 and Table 1 case-level and total columns) |
| 5 | Shares 87%, 77% (K=20), 86% (K=100), CI 83-91% | .0841/.0972; .0462/.0598; .1099/.1280; sgg_share_intervals.json | 86.5%, 77.3%, 85.9%, [82.6%, 90.6%]: match |
| 6 | Grouping shares 90% and 18% | sgg_grouping_share.json | 89.7% and 18.1%: match |
| 7 | F@50 0.344 vs 0.322; R@50 cost 0.0175 vs 0.2023 | 2PR/(P+R) from quoted R@50, mR@50 | 0.3436 vs 0.3216; 0.0175 vs 0.2024 (input rounding): match |
| 8 | Equivalence entries (±0.0063, ±0.0032, ±0.0097, 90% intervals) | sgg_equivalence.json and script | Reproduced; 90% interval inconsistent with 95% (W7) |
| 9 | Margin vs estimand | 0.0097 / 0.0130 | 75% (W2) |
| 10 | Same-image structure (real audit, 183,642 relations) | Counted pairs and relations | 0.47% of ordered same-cell pairs same-image; 58.7% of relations with a same-image same-cell partner; 33.1% share image and boxes (W1) |
| 11 | Effect of same-image transport on raw case-level part | Re-estimated with other-image transport on variant_TDE vs variant_none | +0.02246 to +0.02444 (+0.0020); by cell size, see W1 |
| 12 | Cluster SE | Analytic 0.00064 vs 80-draw image bootstrap SD 0.00073 | Within Monte Carlo error; bootstrap duplicates images, so inconclusive |
| 13 | Coverage under shared-image latent | Own simulation, 30 cells, 8 relations per image, 300 runs | 92.0% (m=8), 95.7% (m=1) |
| 14 | Not recomputed | Matched/recalibrated protocols, hit-contrast evaluator replay, SGCls/SGDet, CLIP and CIFAR studies | Not checked; requires checkpoints or training |
