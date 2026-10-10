# Peer Review Report: Methodology (Peer Reviewer 1)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 Submission #***** (anonymous), paper.pdf (8 pp + references) and supp.pdf (36 pp)
- **Repository state reviewed**: commit 9dad949
- **Review Date**: 2026-10-10
- **Review Round**: 1 (simulated CVPR 2027 panel, mode full)

## Reviewer Information

### Reviewer Role
Peer Reviewer 1 (Methodology)

### Reviewer Identity
Expert in evaluation statistics for vision: calibration, proper scoring rules, U-statistics and uncertainty quantification on benchmark metrics.

### Review Focus
Whether the proposed exact split of a paired score gain (group-level part vs. case-level covariance) is statistically sound, whether its intervals and null behaviour are validated in the regimes where it is applied, and whether the scene-graph conclusions follow from the evidence, including the sensitivity of those conclusions to the calibration protocol, the declared grouping, and the choice of metric and weighting.

### Calibration Status
`NOT_CALIBRATED`. No author-confirmed target context was supplied (`criteria_binding_unavailable`); this report makes no venue-alignment claim.

---

## Overall Assessment

### Recommendation
**Major Revision**

### Confidence Score
4 (core expertise in proper scores, U-statistics and benchmark uncertainty; I did not re-run the Colab model passes, only the cached-output analyses)

### Summary Assessment
The paper proposes a label-transport decomposition of a paired score gain, within a declared grouping cell, into a group-level part and a within-cell covariance (an order-two U-statistic with Hájek influence functions and image-clustered intervals). It applies this to two released scene-graph debiasing checkpoints (TDE, IETrans) and to controlled predictors. The algebra is correct and unusually well checked: the identity is exact, the code reproduces the reported numbers, all 423 printed numbers trace to committed result files, and the authors are candid about several limits (the theorem's regime, the small-cell coverage, calibration dependence). The mean-recall extension, with an operating-point control (a logit adjustment that moves no within-cell ranking), is the most useful methodological idea.

My concerns are about what the evidence licenses. The proper-score case-level part is defined relative to calibration, and for TDE its sign depends on the matching protocol (four protocol/score combinations give -0.018, -0.00006, +0.0045 and +0.044). The primary protocol is the one the paper's own simulation shows to be inadequate. The "no change in TDE's within-pair ranking" conclusion rests on non-detection with no equivalence margin, while several reported measures do detect a change. The long-tailed-classification conclusions contradict the paper's own reading of the operating-point control. The inference is validated by simulation only, and the nuisance (calibration split, one checkpoint, grouping) variability is not propagated. Most of these are repairable with re-analysis and rewording rather than new training, so I recommend Major Revision rather than Reject.

---

## Criterion-Bound Judgements

| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Estimator correctness and exact identity | Reviewer-role configuration (methodology remit); no external criterion bound | MEETS | equation: Eq. (4)-(7) and Theorem 3; recomputation log R3, R2 | Identity holds exactly; code reproduces mR@50 split 0.0972 = 0.0841 + 0.0130 | Algebraic claims only; unbiasedness needs iid within-cell draws | no |
| Validity of inference (intervals) | Same | PARTLY_MEETS | text: Supp. J "VG150 does not meet it at its sample size"; table: Table 4 (81.5% coverage at n_c = 2); R4 | Theorem 4 does not cover the applied regime; coverage evidence is one synthetic DGP; calibration-split and checkpoint variability are not propagated | My bootstrap agrees with the analytic SE for mean recall (R4) | yes, via W4 |
| Construct validity of "case-level = discrimination" | Same | PARTLY_MEETS | table: Table 32 (TDE case part -0.018 / -0.00006 / +0.00445); table: Table 11 (LA +0.032 > DRW +0.0195) | Part is calibration- and operating-point-dependent; control interpretation inconsistent across sections | Authors disclose dependence for VG; not for CIFAR/text | yes, via W1, W3 |
| Support for headline scene-graph claims | Same | PARTLY_MEETS | table: Table 17, Table 19, Table 21, Table 29, Table 34 | 87% is one of six mean-recall protocols; "no measure detects" is non-detection without a margin | Point estimates mostly small; direction of conclusions plausible | yes, via W2 |
| Sensitivity to declared grouping | Same | PARTLY_MEETS | table: Table 9, Table 3 (rho dagger = 0.061), App. K toy example | Disclosed, but headline shares are not reported under alternative groupings | Single declared grouping is defensible for VG150 | yes, via W5 |
| Reproducibility | Same | EXCEEDS | recomputation log R1, R2 | Number-tracing script, tests, cached outputs, fixed seeds | Model training runs not re-executed by me | no |
| Statistical reporting (effect sizes, CIs, multiplicity) | Same | PARTLY_MEETS | text: Supp. N.1 "we do not additionally adjust the diagnostic p-values" | CIs everywhere; but many protocol variants and weightings with selective emphasis in text | p-values are secondary diagnostics | partly, via W2, W6 |

Do not total or average these judgements.

---

## Strengths

### S1: Exact, model-free identity with a verified implementation
The split is an algebraic identity in every sample (Theorem 3, Eq. 17) and the leave-one-out transport removes the (n_c-1)/n_c attenuation (Proposition 5). The code in `wager/antisymmetric.py` implements the pairwise kernel in O(NK), asserts the identity at run time, and the 32 unit tests pass.
**Evidence Anchor**: `equation: Eq. (4)-(7), Theorem 3 and Proposition 5; code wager/antisymmetric.py decompose_gain_matrix`

### S2: Mean recall is brought inside the framework, with an operating-point control
Because the identity needs no properness, a hit-rate contrast with label weights can be split, and the authors replay the official evaluator offline to make recall an exact function of the labelling (Supp. O; replay reproduces R@50/mR@50 to four decimals, Table 16). The logit-adjusted control (a constant shift per cell that changes no within-cell ranking) is the right device to separate "new discrimination" from "existing discrimination spent at a new threshold".
**Evidence Anchor**: `table: Table 16 (official vs re-scored recalls identical) and Table 1 rows TDE-LA`

### S3: Candid, quantitative reporting of limits
The paper reports where its own guarantees fail: Theorem 4's divergence condition is not met on VG150 (C/sqrt(N*) = 13.3), coverage drops to 81.5% when all cells have two cases, two equally fine partitions can disagree completely (App. K), and the sharp sensitivity bound gives rho dagger = 0.061. Several earlier overclaims are visibly corrected in the text.
**Evidence Anchor**: `text: Supp. J "VG150 does not meet it at its sample size", Table 4, App. K, App. I (rho dagger = 0.06127)`

### S4: Validation designs where the answer is known
Algebraic zero for class-pair-only models (MLP-CLASS vs FREQ), a within-cell shortcut that is credited to the case-level part, a calibration-only change that produces a spurious -0.488 on raw outputs, and a class-wise offset that survives temperature matching. These are well chosen and, notably, expose the method's own weaknesses.
**Evidence Anchor**: `text: Sec. 4 "A class-wise shift of the operating point ... survives temperature matching"`

### S5: Reproducibility infrastructure
`verify_manuscript_numbers.py` traces all 423 printed numbers to committed results; seeds are fixed; cached predictions are shipped.
**Evidence Anchor**: `dataset: results/*.json and experiments/verify_manuscript_numbers.py (423 of 423 numbers trace)`

---

## Weaknesses

### W1: The primary calibration protocol is the one the paper's own validation shows to be inadequate, so TDE's proper-score case-level part is protocol-determined
**Problem**: Section 4 shows that temperature matching leaves a class-wise operating-point shift in the case-level part (+0.0106 for a pure logit-offset change) and that "both protocols are therefore part of the procedure". Yet Sec. 5, Fig. 2 and Abstract use per-model temperature matching as primary, and it is the only protocol under which TDE's quadratic case-level part is null (-0.00006, CI [-0.00120, +0.00109]). Under the temperature + per-class-bias protocol, the one under which the paper's own logit-adjusted control becomes exactly the baseline (Table 32, case part 0.00000), TDE's case-level part is +0.00445 [+0.00354, +0.00536] (quadratic) and +0.02543 (log). Under a shared temperature it is -0.01839. So the quantity takes values of both signs and the paper says "the sign of TDE's case-level part depends on the protocol". Contribution (iii) ("validation that the case-level part ... separates calibration, prior and shortcut effects") is therefore only partly delivered: the part is not identified from the rankings alone.
**Evidence Anchor**: `table: Table 32 rows "TDE vs base, quadratic": temperature -0.00006, shared temperature -0.01839, temperature + class bias +0.00445`
**Why it matters**: The headline narrative ("its small case-level part changes sign with the calibration protocol") is honest, but the primary figure (Fig. 2b, "CI straddles 0") shows only the protocol that gives a null. A reader sees an apparently clean null that is a protocol artefact. Because the null is tested against a noise level of about 0.0012 while the protocol effect is about 0.005 to 0.02, the interval tells us little about whether TDE adds discrimination.
**Suggestion**: (a) Choose the primary protocol by an ex-ante criterion stated in Sec. 3 (for example, the matching family that returns exactly zero for a ranking-preserving class-wise shift, i.e. temperature + per-class bias), and show all families in Fig. 2. (b) State that the proper-score case-level part is not used as inferential evidence for or against new discrimination when protocols disagree in sign; rest the discrimination claim on the AUC and on the controlled mean-recall comparison. (c) Report the spread across protocols as part of the uncertainty (a protocol-envelope interval), not only the sampling interval.
**Severity**: Major
**Confidence**: 4 (core expertise: calibration and proper scores)

### W2: "No measure detects a change in TDE's ranking" and "87% group-level" are non-detections and single-protocol statements, with no equivalence margin and with detections elsewhere in the supplement
**Problem**: The conclusion that TDE's gain is group-level and leaves within-pair ranking unchanged rests on (i) intervals that include zero for the AUC and for the case-level part against the control, and (ii) one of six mean-recall protocols (graph-constrained mR@50). No equivalence margin or minimum detectable effect is stated; the comparison-weighted AUC change is +0.0026 [-0.0028, +0.0086], whose half-width is about a quarter of the +0.0323 that box geometry buys over the class-only model (Table 30). Several reported results do not fit the clean reading:
- TDE vs LA1, no graph constraint, mR@100: case-level +0.0148 [+0.0064, +0.0232] (Table 17), and mR@50 no-graph +0.0072 [-0.0001, +0.0145].
- In the no-graph protocol TDE's total mean recall change is negative (-0.0337 at @50), so a "share" is undefined there; the 87% applies to the graph-constrained protocol only.
- Along the label-mix path, TDE's case-level part against the baseline excludes zero from alpha = 0.25 (+0.00238 [+0.00092, +0.00385], Table 29), and against the control reverses sign (Table 28).
- Stepwise, subtracting the averaged context has an AUC change of +0.0016 [+0.0008, +0.0025] (Table 19, Table 21), which excludes zero.
- In SGCls the relation-weighted AUC change is -0.0128 [-0.0171, -0.0074] (Table 34), a detected loss.
The paper reads these as cancellation across predicate pairs ("gains discrimination between some predicate pairs and loses it between others"), which is a post hoc account that is not itself tested (Table 31 intervals all include zero).
**Evidence Anchor**: `table: Table 17 rows "TDE vs LA1 ng-mR@100: +.0148 [+.0064, +.0232]" and Table 30 row "TDE vs base comparison +.0026 [-.0028, +.0086]"`
**Why it matters**: Non-detection under wide intervals, in a paper whose method is about not crediting sums, is itself a composition problem. The abstract's strong statement ("No measure detects a change in TDE's ranking within pairs") is literally true for the quoted measures but invites a reading as "no change", and the supplement shows that the answer varies with protocol, weighting and grouping.
**Suggestion**: Pre-declare an equivalence margin (for example +/-0.005 AUC, justified against the +0.03 scale of geometry) and report two one-sided tests or a minimum detectable effect for each of the TDE-vs-control comparisons. Move the full six-protocol mean-recall table (Table 17) into the main paper, and state in the abstract that the 87% is for the graph-constrained, micro-averaged mR@50. Reword to "no change detected within +/- m".
**Severity**: Major
**Confidence**: 4 (core expertise: uncertainty on benchmark metrics)

### W3: The long-tailed classification and text results contradict the paper's own reading of the operating-point control
**Problem**: In Sec. 5 a logit adjustment is a change that moves no within-cell ranking, so its case-level part (+0.0139 of mR@50, +0.0039 quadratic) is "existing discrimination spent at a new operating point", not new discrimination. In Supp. N.5 the same logit adjustment applied on CIFAR-100-LT is described as "almost entirely covariance gain (+0.022 to +0.038)" that "changes rankings where the model already carried latent evidence", and the deferred-reweighting (DRW) covariance gain (+0.0195 on average, Table 11) is called "genuine per-instance discrimination". By the paper's own control the LA value (+0.0324 mean, Table 11) is the operating-point effect, and it exceeds DRW's. Within a superclass cell, adding a per-class constant to the logits leaves every pairwise log-odds ranking unchanged, so the statement that LA "changes rankings" does not hold for the within-cell AUC the paper treats as the invariant measure. The calibration-matched protocol in N.5 uses temperature only, so it cannot remove a class-wise shift, which is exactly what class-balanced reweighting and DRW are. Moreover, for CIFAR and 20 Newsgroups the grouping is a function of the label, not of the input, which the supplement notes; there the "group-level part" has no operational meaning as what a model that observes the cell could supply, so statements such as "CB lost within-superclass discrimination" and "DRW's gain is genuinely covariance-driven" are not supported. Only 3 seeds exist at ratio 100 and the DRW magnitude varies fourfold (+0.007 to +0.031).
**Evidence Anchor**: `table: Table 11 mean row "DRW +0.01953, LA +0.03241" and text: Supp. N.5 "it changes rankings where the model already carried latent evidence"`
**Why it matters**: The paper cites these studies for breadth ("Beyond scene graphs") and as evidence that the split transfers; they currently provide a conclusion in the opposite direction from the control logic of the main study.
**Suggestion**: Apply temperature + per-class-bias matching and the within-cell AUC to CIFAR-100-LT and 20 Newsgroups, and compare each method's covariance with the LA control's. Either delete the "genuine discrimination" language or state it only for the part exceeding the control. Treat label-derived groupings as a separate, clearly labelled illustration of the algebra. Report seed-level intervals or add seeds before ranking methods.
**Severity**: Major
**Confidence**: 4 (core expertise: calibration and logit adjustment)

### W4: Interval validity beyond the one simulated design, and nuisance variability that is not propagated
**Problem**: (a) Theorem 4 requires every cell's size to diverge; the paper acknowledges VG150 has C/sqrt(N*) = 13.3 and that the theorem "does not by itself license the reported intervals". The support is a coverage simulation (94.0% in 500 runs, so Monte Carlo SE about 1 pp; Table 4 gives 96.2% for VG150 cell sizes while Sec. 4 and App. J say 96.3%) under a single generative design (shared per-image effect, Zipf cell sizes, fixed label priors). No coverage check exists for the thresholded mean-recall contrast, for the share ratio interval, or for the 200-replicate percentile bootstrap on the AUC (the 2.5% tails rest on 5 replicates). (b) The intervals condition on one fitted temperature (or temperature + bias) from one random calibration half: over 20 halves the TDE case-level part has SD 0.00055 (Table 26), the same size as the sampling SE of about 0.0006, and 3 of 20 halves exclude zero; this variability is reported but not combined with the interval. (c) Each result is one trained checkpoint, so training variability is absent for TDE and IETrans (the CLIP study alone has five seeds, which share the training subsample and test set).
**Evidence Anchor**: `table: Table 26 row "TDE vs base quadratic: mean -0.00057, sd 0.00055, CI not containing 0 in 3/20" and Table 4 row "VG150 cell sizes 96.2%"`
**Why it matters**: Interval half-widths of 0.001 to 0.002 are compared with protocol effects of the same order, so understated uncertainty matters for the sign claims in W1 and W2.
**Suggestion**: Add coverage simulations for the mean-recall (hit-contrast, label-weighted) estimator and for the share and AUC intervals; use 1,000+ bootstrap replicates; combine the calibration-split variance with the sampling variance (cross-fitting over many halves with a pooled variance); state clearly that checkpoint-level inference is conditional on the released weights.
**Severity**: Major
**Confidence**: 4 (core expertise: U-statistics and variance estimation)
**Partial reproduction**: for mean recall, an image-cluster bootstrap with the label weights recomputed in each replicate (60 replicates, my code) gave an SD of 0.00185 for the case-level part against the paper's analytic SE of 0.00193 (log R4), so the omission of weight variability looks harmless at the pooled level.

### W5: The headline shares are conditional on a single declared grouping and are not reported under alternatives
**Problem**: The estimand is defined relative to the declared cell, and the supplement shows how much that matters: coarsening to subject-only changes the controlled-predictor case-level part by 52% (0.01439 to 0.02181, Table 9) and, for the TDE proper-score split, flips the sign of the group-level part (+0.10 vs -0.10, Table 20 "raw, subject only"); an unrecorded covariate correlated at 0.061 would account for the entire case-level gain (Eq. 27); and two equally fine partitions can disagree entirely (App. K). Yet the 87% (83-91%) share in the Abstract is reported for one grouping, the class pair, with an interval that captures sampling variability only. The paper candidly states it has "no procedure that resolves it".
**Evidence Anchor**: `table: Table 9 rows "Cell phi subject only 0.02181" and Table 3 row "Robustness value rho dagger 0.06127"`
**Why it matters**: A reader may take 87% as a property of TDE rather than of TDE under this grouping. Because the case-level part is bounded by what the grouping lets one see, a finer valid grouping (for example class pair x box-overlap bin, which the paper's own shortcut simulation shows is credited as case-level) would likely lower the group-level share.
**Suggestion**: Report the mean-recall share under at least two finer groupings (class pair x geometry bin, class pair x image-level feature), and give a sensitivity band for the share using Proposition 4 adapted to the hit contrast. Put "(grouping: subject-object class pair)" in the abstract's claim.
**Severity**: Major
**Confidence**: 3 (core expertise but the right alternative grouping is a domain judgement)

### W6: Selective wording of IETrans and CLIP conclusions against the tables
**Problem**: The abstract says IETrans "loses within-pair discrimination under every measure". The tables show mixed evidence: the mean-recall case-level point estimate is positive (+0.0060 [-0.0031, +0.0151], Table 1), and the comparison-weighted AUC change is -0.0093 [-0.0181, +0.0004] (Table 19), with the audit-half interval [-0.0272, +0.0020] (Table 30); the exclusion of zero occurs for the relation-weighted AUC (-0.0235) and for the matched proper scores. Further, IETrans is compared against a separately trained MOTIFS-SUM baseline with different fusion, so the comparison "does not isolate the effect of relabelling" (the paper says so in Sec. 5, but not in the abstract). For CLIP vs geometry the paper states "real covariance, not better ranking", but the comparison-weighted AUC difference is positive in all five seeds (+0.0048 to +0.0156) and excludes zero in one, while the relation-weighted version favours geometry (-0.0067 [-0.0120, -0.0019]); the weighting decides the sign (Table 30), so "not better ranking" is not established.
**Evidence Anchor**: `text: Abstract "loses within-pair discrimination under every measure" and table: Table 1 row IETrans (case +.0060 [-.0031,+.0151], AUC_c -.0093 [-.0181,+.0004])`
**Why it matters**: These are the second-method and the "model every metric ranks last" claims; the wording runs ahead of the intervals, and the pattern (the favourable weighting is quoted in the text) invites a forking-paths objection.
**Suggestion**: Replace "every measure" by the list of measures that exclude zero; state in the abstract that IETrans is compared with a different baseline and is the IETrans+Rwt variant; give both AUC weightings and a pre-declared primary one; for CLIP, report that the two rank-based summaries disagree in sign.
**Severity**: Major
**Confidence**: 4 (core expertise: reporting of paired metrics)

### W7: Micro-averaged mean recall is not the official metric the abstract quotes
**Problem**: The split is of micro-averaged mean recall over identified relations (+0.0972), whereas the abstract's "ten points" (14.6 to 24.8) is the official per-image-averaged metric (+0.1017); the 87% is computed on the former. The two differ by 4.5% of the change, and the official per-image average (a mean of per-image ratios) is not a label-weighted hit rate and so cannot be split. Rare predicates are excluded disproportionately (up to 8.3% of a predicate's relations in singleton cells in my count; mean 2.8% over the 15 rarest) although each predicate has equal weight in mean recall, so "99%" coverage understates the exclusion for the quantity of interest.
**Evidence Anchor**: `text: Sec. 5 "mean recall@50 rises by 0.0972 (0.1017 on the official per-image average)"`
**Why it matters**: A minor mismatch in the numerator, but the 87% appears next to the official ten points in the abstract.
**Suggestion**: State in the abstract that the share is for the micro-averaged version; report per-predicate coverage; give the share's sensitivity to the 4.5% difference (for example by applying the shares per predicate to the official per-image recall).
**Severity**: Minor
**Confidence**: 4 (verified from cached data)

### W8: Relation-level randomization p-values ignore image clustering and floor at .002; same-image siblings violate the iid-pair premise in small cells
**Problem**: The cyclic-shift test is relation-level and uses a subgroup of the permutation group, whereas the intervals are image-clustered; it is labelled "diagnostic" but the main text prints p = .002 beside intervals. The floor is 1/500 (stated in the supplement, not in the main text). The unbiasedness theorem needs independent within-cell draws; in my count only 0.47% of within-cell pairs share an image, but 37% of relations in cells with at most four members have a same-image sibling, which is where the small-cell coverage shortfall (Table 4) lives.
**Evidence Anchor**: `text: Sec. 4 "(CI [0.01373, 0.01504], p = .002)"; absence: Sec. 3 and Theorem 3 — expected exclusion or treatment of same-image pairs in the U-statistic; checked Sec. 3, Supp. B.5, F`
**Why it matters**: Low, but an image-aware permutation test (shift labels by whole images) and an estimator that drops same-image pairs would remove an avoidable objection.
**Suggestion**: Report p as "p <= .002", permute within cells at the image level, and add a robustness row that excludes same-image pairs.
**Severity**: Minor
**Confidence**: 3 (supporting computation was exploratory)

### W9: Proper scores on TDE outputs
**Problem**: The proper-score analyses treat softmax(TDE logits) as a predictive distribution, after dropping the background column and renormalising. TDE's output is a difference of logit branches that is not trained as a probabilistic predictor, and the paper's own Table 22 shows TDE's logits are dominated by a between-cell component. The group-level quadratic loss of -0.18 is largely a statement about this reparametrisation and is of little evidential value on its own.
**Evidence Anchor**: `table: Table 20 row "TDE vs base matched quad: dT -0.18264, dP -0.18258"; absence: Sec. 3/5 — expected statement of background-column handling and renormalisation; checked Sec. 3, Sec. 5, Supp. O`
**Suggestion**: State the treatment of the background class and discuss what a "proper score" means for logit differences; keep the weight of the argument on the mean-recall split and AUC.
**Severity**: Minor
**Confidence**: 3

### Minor Issues (below finding threshold)
- Table 4 gives 96.2% for VG150 cell sizes; Sec. 4 and App. J state 96.3%.
- Eq. (27) uses an estimate of 0.01427 whereas Table 3 lists 0.01439 for the same quantity; the verification script confirms both values but the text should explain the difference.
- Table 21 lower block reuses columns for "matched quadratic case-level part" and AUC without relabelling the header; hard to parse.
- Table 12 gives p = 1.000 for a one-sided test, and Table 14's p = .236; state the alternative hypothesis in the caption of every p column.
- Table 1 caption defines AUC weights as "(c)" and "(r)" before the notation is explained in the text.
- The main text sentence "interval straddling zero" should give the interval alongside the point estimate in the abstract's claims.

---

## Detailed Comments

### Research Questions and Hypotheses
The question (which part of a metric gain is group-level and which is case-level) is clear and answerable, and the exact decomposition is a good fit for it. The main-text conclusions are scoped as "audits of two released checkpoints", which is the right scope.

### Research Design
Paired comparison of frozen models on cached outputs, with validation by simulation, controlled predictors and a ranking-preserving control. The design is appropriate; the design weakness is that the case-level construct has three protocol dials (calibration family, score, weighting), each of which changes the sign for TDE.

### Sampling Strategy
Image-clustered resampling is correct for relations. Cells with one member are excluded and reported. Coverage differs for rare predicates (W7).

### Data Collection
Released checkpoints run once; evaluator replay reproduces official numbers (Table 16, Table 33 within 0.0007 for SGDet mR@50: 0.0894 released vs 0.0901 replayed, which is a small replay difference worth a sentence). Controlled predictors use a reconstructed VG150-style split, clearly separated from the canonical one.

### Analysis Methods
U-statistic with Hájek influence and one-way cluster sandwich: appropriate. Not covered: nuisance variation, ratio estimators, multiplicity across protocols (W2, W4). Effect sizes in score units are anchored against accuracy (Supp. N.2), which helps.

### Results Presentation
Tables are complete and signed; the supplement reports unfavourable rows (for example Table 17 no-graph, Table 29). The main text, however, quotes favourable weightings (W6), and Fig. 2 shows a single protocol (W1).

### Reproducibility
Strong (S5). The code runs; tests pass; numbers trace.

### Methodological Fallacies Detected
- Absence of evidence read as evidence of absence (W2).
- Forking paths and selective weighting in verbal summaries (W6), despite complete tables.
- Construct dependence on scale/calibration for a quantity called "discrimination" (W1, W3).
- Simpson-type reversal under coarsening of the grouping, disclosed (W5).
- Causal reading of a comparison between separately trained models (IETrans), disclosed in the body but not in the abstract (W6).

---

## Recomputation Log (read-only; scratch files kept outside the repository)

| # | Check | Command / method | Result |
|---|---|---|---|
| R1 | Number tracing | `python experiments/verify_manuscript_numbers.py --driver cvpr2027/main.tex` | "all 423 manuscript numbers trace to committed results" (211 in the paper, rest in supplement) |
| R2 | Unit tests | `python -m pytest tests -q` | 32 passed |
| R3 | Mean-recall split, TDE vs base, graph constraint, @50 | Own script on `data/vg_motifs/wager_sgg` using `decompose_gain_matrix` with the paper's weights | Total +0.09715 = group +0.08411 + case +0.01305, CI [0.00926, 0.01684]; group share CI 83.0% to 90.2%. Matches Table 1 (0.0972, 0.0841, 0.0130, [0.0093, 0.0168]); 183,642 relations, 181,559 identified (98.9%), 5,044 cells |
| R4 | Does ignoring variability of label weights n_y matter? | Image-cluster bootstrap (60 replicates, weights recomputed each time) | Bootstrap SD of case-level part 0.00185 vs analytic SE 0.00193; percentile interval [0.0091, 0.0155]. No evidence of anti-conservatism at the pooled level |
| R5 | Is the CLIP-vs-geometry case-level advantage an artefact of temperature-only matching? | Own temperature + per-class-bias fit (L-BFGS, same calibration half seed as the repository) on `data/vg_visual/vg_visual_models.npz`, audit on other half | Temperature only: +0.00476 [0.00322, 0.00630] (paper: +0.00464). Temperature + bias: +0.00331 [0.00185, 0.00477]. Pixels vs class-only: +0.01363 to +0.01254. Geometry vs class-only: +0.00887 to +0.00923. The CLIP advantage survives, shrinking about 30%: this supports the paper's claim, and the temperature + bias row should be reported for CLIP |
| R6 | Same-image siblings in cells | Counts on cached meta | 0.47% of within-cell pairs share an image; 59% of identified relations have a same-image same-cell sibling overall; 37% in cells with at most four members |
| R7 | Exclusion of rare predicates | Counts on cached meta | Overall 1.13% of relations in singleton cells; rarest 15 predicates mean 2.8%, max 8.3% |
| R8 | Arithmetic consistency of reported figures | Hand recomputation | 0.0841 + 0.0130 = 0.0971 (reported 0.0972, rounding); 0.0130/0.0972 = 13.4% so group 86.6% (87%); 0.0175/0.2023 = 8.7% ("under a tenth"); 227,337/229,605 = 99.0%; 6,346 + 2,268 = 8,614 cells; 6,346 - 4,060 = 2,286 cells under five; 0.02181 - 0.01439 = 0.00742; 14.00/0.00742 = 1,887; rho dagger = 0.01427/0.23284 = 0.0613; share 0.01439/0.00885 = 1.63; Table 11 CB mean -0.25108 and SD 0.01124, DRW mean +0.01953 and SD 0.01188 recomputed from the three seed values; M sqrt(K-1) = 2 sqrt(49) = 14.0. All consistent |
| R9 | Bounded arithmetic procedures (p from test statistic, GRIM, GRIMMER, n from df) | Scanned paper and supplement | `no_recomputable_statistics`: the manuscript reports intervals and score differences, no test statistics with df, no means of bounded integer scales with n, and p-values only as randomization p at the 1/500 floor, so none of the four bounded procedures applies |

---

## Questions for Authors

1. Why is per-model temperature matching the primary protocol for TDE when Sec. 4 and Table 32 show it leaves a class-wise operating-point effect, and under the protocol that makes your own logit-adjusted control exact (temperature + per-class bias) TDE's quadratic case-level part is +0.00445 [+0.00354, +0.00536]? What is the pre-declared criterion for the primary protocol, and would you present all families in Fig. 2?
2. What equivalence margin for the within-cell AUC would you consider meaningful, and what is the minimum detectable AUC change for the TDE-vs-baseline comparison at the present sample size? Does the no-graph mR@100 case-level part against the control (+0.0148, [+0.0064, +0.0232]) change your reading?
3. In CIFAR-100-LT and 20 Newsgroups, the LA control's matched covariance (+0.032 on CIFAR) exceeds DRW's (+0.0195). By the logic of Sec. 5 this is an operating-point effect. On what basis is DRW's covariance gain called "genuine per-instance discrimination", and does it survive temperature + class-bias matching and a within-superclass AUC?
4. How does the 87% group-level share (and the 99% in SGCls) change if the grouping is refined by a box-geometry bin or by a coarse spatial-relation indicator, which your shortcut simulation shows are credited to the case-level part?
5. Can you provide a coverage simulation for the mean-recall hit contrast (label-weighted, discontinuous) and for the share interval, with calibration-half variability included, rather than relying on the Gaussian-score coverage study?

---

## Verdict Rationale

Unresolved decision-bearing criteria: construct validity of the proper-score case-level part (W1, W3), support for the headline non-detection claims (W2, W6), conditionality on the declared grouping (W5) and validity of intervals outside the simulated regime (W4). All are repairable by re-analysis of cached outputs and rewording, without new data collection; none of the estimator's algebra or the reproducibility is in doubt, which is why this is Major Revision rather than Reject. Strengths in reproducibility and candour do not offset the construct-validity concerns; they only make the repair path short.
