# Peer Review Report — Methodology (Peer Reviewer 1, seat R1)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission (anonymous; repository commit 909e5a3)
- **Review Date**: 2026-10-05
- **Review Round**: Round 1 (simulated panel, `academic-paper-reviewer` v1.11.1, mode `full`)

Calibration status: `NOT_CALIBRATED`

criteria_binding_unavailable

There is no author-confirmed target context. Remarks about CVPR are a configured perspective, not a determination that the paper fits the venue.

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 1 (Methodology)

### Reviewer Identity
Evaluation statistician for vision: calibration, proper scores, U-statistics, and uncertainty quantification on benchmark metrics.

### Review Focus
I checked three things. First, whether the estimator and its theorems are correct, in the supplementary proofs and in `wager/`. Second, whether the inference procedures cover at their nominal rate: the image-clustered Hájek interval, the image bootstrap, the randomization test, and the within-cell AUC. Third, whether each claim is as strong as its evidence. For the third I looked at the confidence-matching protocol and its alternatives, the operating-point control, the label-shift reweighting, the predicate merges, the IETrans comparison, and the zero-shot CLIP audit.

---

## Overall Assessment

### Recommendation
- [ ] Accept
- [ ] Minor Revision
- [x] **Major Revision**
- [ ] Reject

**CVPR-scale rating**: Borderline. **Confidence**: 4/5.

### Confidence Score
4. The estimator, U-statistic inference, proper scores and calibration are my core expertise. I have less expertise in the scene-graph-generation evaluator internals. I relied on the paper's replay validation for those and spot-checked it by reproducing the official numbers from cached outputs.

Confidence describes my uncertainty and scope only. It never changes consensus counts, severity, decision bearing or arbitration.

### Summary Assessment
The paper scores each prediction against the label of another case in the same subject–object cell. This splits the gain between two frozen models, under a proper score or under micro-averaged mean recall, exactly into a group-level part and a case-level within-cell covariance (a U-statistic). The paper then audits TDE, IETrans and a CLIP-crop predictor.

The construction is correct. I checked Theorem 1, the Bregman generalisation, the finite-sample identity and the attenuation result line by line. The code matches the equations. The headline mean-recall split reproduces to four decimals from the cached outputs, and an image bootstrap I ran confirms its interval. The finding that 87% of TDE's mR@50 gain is group-level is solid: I computed a 95% interval of [83%, 90%] for that share.

The weaker part is how far the paper reads the case-level part as "discrimination". Three recomputations moved conclusions:
1. A slightly richer ranking-preserving recalibration (temperature plus a per-class bias) turns TDE's matched quadratic null into a significant case-level gain under both proper scores.
2. The within-cell AUC weights cells by n_c², not n_c as stated. Re-weighting it consistently with the split reverses the sign of the CLIP-versus-geometry AUC difference.
3. The IETrans "case-level loss" is measured against a separately trained baseline.

Several abstract-level "no gain" statements also rest on intervals that include zero, with no equivalence margin.

All of these can be repaired within one revision cycle with the authors' own cached outputs. Hence Major Revision, and Borderline on the CVPR scale.

---

## Strengths

### S1: The decomposition and its proofs are correct and exactly implemented
Theorem 1 follows from expanding ΔT_c − ΔP_c over labels. The quadratic and Bregman forms are correct because the label-free part B(X) has zero covariance with Σ_y 1{Y=y} = 1. The finite-sample identity, the (n_c−1)/n_c attenuation and the coarsening identity (law of total covariance) all check. `wager/antisymmetric.py` computes P_i as in Eq. (linear), and the code's mean kernel Ā_i matches the appendix formula term by term. It also asserts T̂ = P̂ + R̂ at run time. `pytest` passes (30 tests), and `verify_manuscript_numbers.py` reports "all 298 manuscript numbers trace to committed results".
**Evidence Anchor**: `equation: Sec. 3, Eq. (3)–(6) and supp. "Proofs" (proof of Theorem 1, Theorem 3, Proposition 6)`

### S2: The headline mean-recall split reproduces, and its interval holds up
From `data/vg_motifs/wager_sgg` I recomputed the following.

| Comparison | ΔmR@50 | Group-level | Case-level, 95% CI |
|---|---|---|---|
| TDE vs base | +0.0972 | +0.0841 | +0.0130 [+0.0093, +0.0168] |
| LA vs base | +0.0941 | +0.0802 | +0.0139 |
| TDE vs LA | — | — | −0.0008 [−0.0050, +0.0033] |

All of these match Table 1. An image-cluster bootstrap with 200 replicates gives standard deviations within 4% of the paper's Hájek cluster standard errors (ratios 0.958, 1.033 and 0.976). The 87% group share has a delta-method interval of [83.0%, 90.2%], and IETrans's 97% has [93.2%, 101.3%].
**Evidence Anchor**: `table: Table 1 — TDE row ΔmR +.0972, group +.0841, case +.0130 [+.0093,+.0168]`

### S3: The TDE design is clean and the evaluator is replayed exactly
TDE and the baseline come from one set of released weights, so differences in training run cannot confound this comparison. Every branch's logits were dumped. The supplement reports that the returned logits equal the branch identity with a maximum difference of exactly 0, and that the replay reproduces the official recall. The three-step attribution along the branches (Table "TDE along its branches") adds up exactly.
**Evidence Anchor**: `text: Sec. 5, L387–405 "We ran the released checkpoint once with the authors' code on the canonical VG150 test split, saving every branch's logits"`

### S4: The operating-point control is a well-chosen negative control
A logit adjustment by the training prior cannot change any within-cell ranking. Using it as a control for a thresholded metric correctly shows that a case-level part of mean recall is not, on its own, evidence of new discrimination. This is a useful methodological contribution beyond scene graphs.
**Evidence Anchor**: `text: Sec. 5, "An operating-point control" — "whatever case-level part it shows is existing discrimination spent at a new operating point"`

### S5: The robustness programme is extensive, and the CLIP sign survives an independent check
The paper reports 20 calibration halves, a shared temperature, two predicate merges, single-annotation pairs, a label-shift reweighting and five training seeds. I independently refitted the CLIP-versus-geometry comparison with two other ranking-preserving recalibrations. With temperature plus per-class bias, the case-level advantage was +0.00331 [+0.00185, +0.00477]. With per-cell prior matching plus temperature, it was +0.00479 [+0.00288, +0.00670]. The sign of that covariance is therefore not an artefact of the temperature family, although its size moves by about 30%.
**Evidence Anchor**: `table: supp. Table "The matched split over 20 calibration halves" and Table "Matched quadratic-score split ... for five training seeds"`

### S6: The limitations are stated frankly
The supplement reports a robustness value of 0.061 for the controlled-predictor gain. It also says the CLT does not describe the finite-sample regime, that equally fine partitions can disagree, and that the split is not invariant to recalibration. This candour is uncommon and valuable.
**Evidence Anchor**: `text: Sec. 7 "an unrecorded covariate correlated at 0.061 with both parts would account for the entire case-level gain"`

---

## Weaknesses

### W1: TDE's proper-score "null" depends on the recalibration family
**Problem**: The paper's matched protocol fits one temperature per model. Under that protocol, TDE's quadratic case-level part against the baseline is −0.00006 [−0.00120, +0.00109], and Sec. 5 heads this paragraph "The proper score agrees". Two observations undercut it.

1. Under the same protocol the log score already gives TDE a significant case-level gain, +0.04396 [+0.04079, +0.04714]. It is positive in 20/20 calibration halves.
2. I refitted both models with temperature plus a per-class logit bias, by maximum likelihood on the same calibration half (seed 20260811). This family preserves every within-cell ranking, so it leaves the within-cell AUC unchanged. Under it:
   - LA_1 becomes identical to the baseline (case-level part exactly 0.00000). This is a sanity check: LA is the baseline plus a class bias.
   - TDE's case-level part against the baseline becomes +0.00445 [+0.00354, +0.00536] under the quadratic score and +0.02543 [+0.02287, +0.02800] under the log score. Both are significantly positive.

So whether TDE shows a proper-score case-level gain is decided by the analyst's choice of calibration family, not by the data. IETrans's loss is robust: −0.01679 quadratic and −0.06609 log under the richer family.
**Evidence Anchor**: `table: supp. Table "Proper-score split of TDE and of the logit-adjusted baseline" — TDE vs base, matched, log: ΔR̂ = +0.04396 [+0.04079,+0.04714]`
**Why it matters**: The abstract and conclusion say the case-level part TDE gained is nil. The proper-score half of that evidence is not robust to a choice the paper does not justify. The one family I tried that absorbs the operating-point control exactly reverses the conclusion.
**Suggestion**:
- Treat the recalibration family as part of the declared protocol and justify it.
- Report the split under at least temperature, temperature plus class bias (vector-bias scaling), and per-cell prior matching.
- Retitle "The proper score agrees" and rest the TDE "no new discrimination" claim on rank-based evidence only, with the scope stated.
- Since temperature plus class bias makes LA identical to the baseline, it is arguably the family that matches the paper's own operating-point logic.

**Severity**: Major
**Confidence**: 5 — core expertise: calibration and proper scores; recomputed from `data/vg_motifs/wager_sgg` (`panel_R1/tde_calfam.py`)

### W2: The within-cell AUC is not weighted like the split, and the CLIP verdict depends on that weighting
**Problem**: Sec. 3 and `wager/rank.py` describe the AUC as averaged "with weight n_c(y)n_c(z) as in the pairwise form above". Within a cell this matches the split's p(y)p(z). Across cells, however, it weights cell c by about n_c², whereas the split weights by n_c.

On the canonical test set:
- The largest cell carries 26.9% of the AUC weight but 2.5% of the split's relation weight.
- The top 10 cells carry 54.7% of the AUC weight against 10.3% of the split's weight.

I recomputed the AUC with weight n_c(y)n_c(z)/n_c, which is consistent with the split, and image-bootstrapped it (200 replicates):

| Comparison | Paper's weighting | Split-consistent weighting |
|---|---|---|
| TDE vs base | +0.0026 [−0.0028, +0.0086] (reproduced as +0.0025) | −0.0018 [−0.0038, +0.0014] |
| CLIP vs geometry, full test set | +0.0085 [−0.0062, +0.0214] (paper) | −0.0067 [−0.0120, −0.0019] |
| CLIP vs geometry, audit half | — | 0.0000 [−0.0067, +0.0068] |

TDE stays null, and the interval is tighter. For CLIP versus geometry the difference becomes significantly negative on the full test set. The paper's own AUC is also computed on the full test set while the matched split uses the audit half (I reproduced 0.5408 and 0.5323 on the full set), so the two quantities refer to different relations.
**Evidence Anchor**: `text: Sec. 3, L312 "averaged with weight nc(y)nc(z) as in the pairwise form above"`
**Why it matters**: The AUC is the paper's arbiter of "discrimination", and it is paired with the split as its threshold-free check. With weighting consistent with the split, the CLIP model the paper says "carries more case-level covariance" ranks within cells worse than geometry (full set) or no better (audit half). The "converse" in the abstract therefore rests on a covariance that a split-consistent rank test does not support.
**Suggestion**:
- Weight the AUC across cells by n_c (or report both weightings) and say which matches the split.
- Compute the AUC and the split on the same relations.
- Report how concentrated the AUC weight is in the largest cells.
- Revise the abstract's CLIP sentence accordingly.

**Severity**: Major
**Confidence**: 4 — core expertise: rank statistics and U-statistics; recomputed with `wager.rank._blocks` (`panel_R1/auc_nc.py`, `auc_nc_clip.py`)

### W3: Several "no gain" claims are absence-of-evidence statements with no equivalence margin
**Problem**: The abstract says the AUC "finds no discrimination that TDE gained". The contributions say TDE has "no gain in within-group discrimination". Sec. 5 says the case-level part is "matched by the control". Each rests on an interval that contains zero; no equivalence margin or two one-sided test (TOST) is declared. The inconsistency is visible in the paper's own numbers:
- TDE's AUC interval has an upper limit of +0.0086. That equals the CLIP-versus-geometry point difference (+0.0085), which Sec. 6 calls inconclusive rather than evidence of "no difference".
- The AUC also fails to detect a gain the authors believe is real. For CLIP+geometry versus geometry, the case-level part is +0.008 to +0.009 in every seed, yet the AUC interval includes zero in 3 of 5 seeds (supp. seeds table).
- Under the label shift, TDE's case-level part against the baseline becomes +0.01430 [+0.01144, +0.01632]. The "null" is therefore a cancellation at one label mix, which the paper itself concedes.

**Evidence Anchor**: `text: Abstract L021–022 "a threshold-free within-group AUC finds no discrimination that TDE gained"`
**Why it matters**: A non-significant result from a low-power statistic is presented as evidence of absence in the abstract and contributions. That is the claim a CVPR reader will cite.
**Suggestion**:
- Declare an equivalence margin, for example a fraction of the baseline's AUC excess over 0.5 or of LA's case-level part, and report TOST.
- The split-consistent AUC of W2 (upper limit +0.0014) may well support a genuine equivalence claim for TDE. Use it.
- Otherwise phrase the claims as "no detectable gain, interval [a, b], at the benchmark's label mix".

**Severity**: Major
**Confidence**: 5 — core expertise: inference and claim calibration

### W4: The IETrans "case-level loss" is measured against a separately trained baseline
**Problem**: IETrans released no baseline. The comparison is with the MOTIFS-SUM baseline from TDE's codebase, which "differs from IETrans's Motifs predictor in its fusion of the visual term". The paper's own branch analysis shows that the visual term alone moves the within-cell AUC by −0.0127 (vis vs base). No reference shows how far case-level parts differ between two independently trained MOTIFS-family models. Despite this, the abstract and contributions attribute the case-level loss (−0.0162 quadratic, −0.0544 log) to IETrans.
**Evidence Anchor**: `text: Sec. 5, L505 "this compares it with a separately trained model of its family"`
**Why it matters**: The paper's second audited method, and its claim that "the split separates the two methods", depend on separating the effect of the method from the effect of the training run and architecture. The current design cannot do that.
**Suggestion**:
- Train a plain Motifs predictor in the IETrans codebase without relabelling (the codebase supports this) and compare against it.
- Alternatively, report the case-level part between two or more independently trained MOTIFS baselines as a null reference.
- Until then, describe the IETrans result as a comparison of checkpoints, not of methods.

**Severity**: Major
**Confidence**: 4 — core expertise: experimental design for model comparison

### W5: The Hájek cluster variance omits a second-order term that matters for fine groupings, and the stated conditions are inconsistent
**Problem**: The variance estimator uses only the first-order Hájek projection. In a cell of two, the U-statistic equals its kernel A_12, and the omitted degenerate component is of the same order as the projection.

I simulated cells of i.i.d. relations, each in its own image, with 400 replicates:

| Regime | SE / empirical SD | Coverage of nominal 95% |
|---|---|---|
| All n_c = 2, with signal | 0.71 | 83.8% |
| All n_c = 2, near the null | 0.68 | 80.2% |
| All n_c = 4 | 0.88 | 91.2% |
| 70% pairs | 0.83 | 89.5% |
| All n_c = 20 | 1.00 | 95.5% |

The paper's coverage simulation says "most cells holding two cases" and reports 94.0%. That figure reflects relation mass sitting in a few large Zipf cells, not small-cell performance.

The formal statements also disagree with each other:
- The Theorem 7 condition (iv) assumes a fixed, finite set of cells.
- The influence appendix requires C = o(√N*) and concedes it fails (C/√N* ≈ 13.3).
- The CLT appendix instead says C = o(N*) suffices, "comfortably".

On VG150 itself the problem is minor: only 1.0% of identified relations sit in two-case cells, and my image bootstrap matches the Hájek standard errors (W2/S2).
**Evidence Anchor**: `text: Sec. 4, L336–339 "most cells holding two cases: the image-clustered interval covers in 94.0% of 500 runs"`
**Why it matters**: Interval validity is a stated contribution, and the paper advises using "the finest grouping that the benchmark's construction defends". That advice pushes users into exactly the small-cell regime where the interval under-covers.
**Suggestion**:
- Add the second-order term to the variance, or use a delete-a-group jackknife over images.
- Report the relation-weighted cell-size distribution with every audit.
- Make the remainder condition the same in the two appendices; the variance argument gives a ratio of about C/N* times (ζ₂/ζ₁).
- Re-describe the simulation regime by relation mass rather than by cell count.

**Severity**: Minor
**Confidence**: 5 — core expertise: U-statistic asymptotics; simulation in `panel_R1/cov_sim.py`

### W6: The image bootstrap biases the case-level part toward zero
**Problem**: When images are resampled with replacement, duplicated relations land in the same cell. A pair made of a relation and its own copy has kernel A_ii' = 0, so the bootstrapped U-statistic is shrunk toward zero.

In my bootstrap of the TDE mean-recall split, the percentile interval [0.0084, 0.0150] is centred about 10% below the estimate of 0.0130. The paper's label-shift table shows the same asymmetry:
- LA vs base: +0.00392 [+0.00316, +0.00419]
- geometry vs class: +0.00882 [+0.00762, +0.00897]
- IETrans vs base: −0.01623 [−0.01668, −0.01341]

**Evidence Anchor**: `table: supp. Table "The split under a label shift" — LA1 vs base case +0.00392, CI [+0.00316,+0.00419]`
**Why it matters**: The intervals are mis-centred, and the bias is toward the null. No reported sign flips, but magnitudes and coverage are distorted.
**Suggestion**: Exclude pairs that are copies of the same original relation when computing the bootstrapped U-statistic, or use the Hájek interval (or a jackknife) for the reweighted estimator.
**Severity**: Minor
**Confidence**: 4 — core expertise: resampling for U-statistics

### W7: The calibration-only validation is tautological
**Problem**: In the simulation, the "new" model is an exact power transform of the "old" one (`_softmax_power(q_old, 1/3)`). Per-model temperature fitting inverts a power transform by construction, so the reported −0.0003 shows only that the protocol undoes the one distortion it can parameterise. The confounds that matter in practice are different: TDE versus the baseline, and CLIP versus geometry, differ in the shape of their miscalibration (class-wise or per-cell biases). The protocol is not validated on those.
**Evidence Anchor**: `text: Sec. 4, L348–352 "a calibration-only change, where the new model is a temperature-softened copy of an overconfident one"`
**Why it matters**: The simulation is cited as the reason the protocol is "part of the procedure", but it cannot detect the failure W1 exposes.
**Suggestion**: Add arms where the two models carry identical within-cell rankings but differ by a class-wise bias, or by a non-power monotone map. Report how the temperature-only protocol and richer families behave.
**Severity**: Minor
**Confidence**: 5 — core expertise: calibration

### W8: The label-shift analysis is presented as a test, but it is an identity of the reweighted estimator
**Problem**: Sec. 6 says "We test this" (that a label shift moves only the group-level part). The reweighted estimator weights pairs by w_i w_j with w = 1/(L_c p̂_c(y)). That construction targets Σ_{y<z} D(y,z)/L_c², so "fixed D, reweighted" holds by construction. The empirical content is only the sign heterogeneity of D. In addition:
- Temperatures are not refitted at the new mix.
- Weights of 1/p̂ for rare labels in large cells make the estimator unstable: the uniform-mix AUC interval for TDE is [−0.0684, +0.0082], and for IETrans [−0.0471, +0.0607].

**Evidence Anchor**: `text: Sec. 6, L559 "We test this by weighting the test relations so that every predicate of an object pair is equally frequent"`
**Why it matters**: Describing an algebraic consequence as a test overstates its validating force.
**Suggestion**: Present it as a sensitivity analysis of D-heterogeneity. Report effective sample sizes per cell, and consider trimmed weights.
**Severity**: Minor
**Confidence**: 4 — core expertise: importance weighting

### W9: The match between LA and TDE is specific to mR@50 with the graph constraint
**Problem**: "Everything they did ... a one-line prior shift ... also does" and "recovers nine of the ten points" hold at the standard mR@50 graph-constrained setting. The supplementary table shows they do not hold elsewhere:

| Setting | TDE | LA_1 |
|---|---|---|
| mR@20 | +0.0598 | +0.0831 |
| mR@100 | +0.1280 | +0.0981 |
| ng-mR@50 | −0.0337 | +0.0935 |

TDE's case-level part against LA does stay null at every k except ng-mR@100, where it is +0.0148 [+0.0064, +0.0232].
**Evidence Anchor**: `table: supp. Table "Mean-recall split for every protocol and k" — TDE vs base mR@100 +.1280 vs LA1 vs base +.0981`
**Why it matters**: The general statement overreaches. The robust finding is that TDE's extra gain over LA is group-level, not that LA reproduces TDE.
**Suggestion**: Scope the sentence to mR@50, or state the k-dependence and the ng-mR@100 exception in the main text.
**Severity**: Minor
**Confidence**: 5 — direct reading of the authors' table

### W10: The worked example conflates the estimator with the estimand
**Problem**: The main text says model B gains +3/8 "with a case-level part of +1/2". In the population (a cell with label law (3/4, 1/4) and B's predictions), the case-level part is 2Σ_y Cov(Δq_y, 1{Y=y}) = 3/8 and the group-level part is 0. The +1/2 (and −1/8) are the leave-one-out U-statistic values for one four-case sample. The appendix describes the difference as removing "attenuation", but for a finite cell treated as the population the plug-in 3/8 is exact.
**Evidence Anchor**: `text: Sec. 3, L244–246 "pointed at each case's own label gains +3/8, with a case-level part of +1/2"`
**Why it matters**: The example motivates the claim that "aggregate scores ... understate case-level gains". The understatement here is finite-sample noise, not a property of model B.
**Suggestion**: State the population values (P = 0, R = 3/8) in the main text, and give the U-statistic values as an estimate from n = 4.
**Severity**: Minor
**Confidence**: 5 — recomputed by hand

### W11: The zero-shot CLIP audit is too weak to support its general conclusion
**Problem**: The audit uses one prompt template, union-box crops and ViT-B/32. Top-1 accuracy is 2.5%, close to the 2% of uniform guessing over 50 predicates. No prompt ensembling, no prompt-prior correction (other than multiplying by FREQ) and no stronger backbone was tried. The supplement nonetheless concludes about "the vision–language model the audience uses".
**Evidence Anchor**: `table: supp. Table "Zero-shot CLIP on the canonical relations" — zero-shot CLIP top-1 acc. 0.0253`
**Why it matters**: A near-chance zero-shot pipeline cannot show that vision–language models lack within-cell ranking ability.
**Suggestion**: Either scope the claim to this configuration, or add prompt ensembles, subject/object-crop variants and a larger CLIP.
**Severity**: Minor
**Confidence**: 3 — adjacent field: vision–language zero-shot protocols

### W12: Headline shares are reported without uncertainty
**Problem**: "87%" and "97%" appear in the abstract with no interval, although `GainDecomposition.share_ci` already computes one. My intervals: TDE group share [83.0%, 90.2%]; IETrans [93.2%, 101.3%].
**Evidence Anchor**: `text: Abstract L016 "87% of the mean-recall gain is group-level"`
**Why it matters**: These are the most-quoted numbers in the paper. Their intervals are tight, which helps the paper.
**Suggestion**: Report the share intervals beside the shares.
**Severity**: Minor
**Confidence**: 5 — recomputed

---

## Detailed Comments

### Research Questions & Hypotheses
The question — how much of a between-model gain survives within-cell label transport — is precise and answerable. The paper is clear that the answer depends on the declared grouping φ, and its partition counterexample is a model of honest disclosure. The interpretive question it then poses, whether the case-level part is better recognition, is not one the covariance can answer alone (W1–W3). The paper partly concedes this for CLIP but not for TDE.

### Research Design
- **TDE.** The design is strong: the same weights, a branch dump and an exact replay (S3).
- **IETrans.** The design is confounded (W4).
- **Controlled VG predictors.** These provide the necessary known-answer checks. The MLP-CLASS vs FREQ zero is algebraic, as the paper says.
- **Validation simulations.** These cover recovery, a prior-only change and a shortcut well. The calibration arm is tautological (W7), and the coverage arm does not represent the small-cell regime it describes (W5).

### Sampling Strategy
The canonical VG150 test set has 183,642 relations; 98.9% are identified, in 5,044 eligible cells. The independence assumption behind Theorem 3's unbiasedness is technically violated by cell-mates from the same image. I checked: 59% of relations have a same-image cell-mate, but only 0.47% of within-cell pairs share an image. Transporting only across images changes TDE's mR@50 case-level part from +0.0130 to +0.0138 and LA's from +0.0139 to +0.0149. The violation is immaterial here, but a sentence saying so belongs in the supplement.

### Data Collection
All data come from released checkpoints re-run once; the stored per-label ranks make the analysis reproducible. The calibration halves use test images, because no validation outputs were saved. This is disclosed and does not leak labels into the audited half. The 100k-relation subsample for the CLIP study matches training data across models, which is good design.

### Analysis Methods
- **Estimator.** Correct and O(NK) (S1).
- **Inference.** Valid on VG150 (S2), less so in general (W5, W6).
- **Randomization test.** Cyclic within-cell shifts are a subgroup of the within-cell permutations, so the test is exact under within-cell exchangeability. Reporting p = .724 for a statistic that is algebraically zero (L371) is meaningless: it reflects floating-point ties. Drop it.
- **Confidence matching.** The central fragility (W1).
- **AUC.** Mis-weighted relative to the split (W2).
- **Multiplicity.** Many intervals are reported (3 k values × 2 protocols × tiers × predicates × 2 scores × raw/matched). There is no family-wise control. The paper names a primary configuration (mR@50 with graph constraint; matched quadratic), which mitigates this. Pre-specifying it in the main text and labelling the rest as exploratory would remove the concern.

### Results Presentation
Tables are complete and generated from results files; I spot-verified the TDE and IETrans rows. Two configurations go against the headline and appear only in the supplement: the matched log score (+0.044) and the shared temperature (−0.019). The main text mentions them but under a heading ("The proper score agrees") that reads as the opposite (W1).

### Reproducibility
Excellent. Code, cached outputs, a number verifier and tests are included. I could rerun every analysis in this review from the archive in minutes.

### Methodological Fallacies Detected
- **Absence of evidence read as evidence of absence** (W3).
- **Simpson-type cancellation.** TDE's benchmark-mix null is a cancellation of mixed-sign pairwise contrasts, which the label-shift analysis exposes. The paper acknowledges this in Sec. 6 but not in the abstract.
- **Confounded comparison** for IETrans (W4).
- **Selective generalisation from a single k** (W9).

---

## Questions for Authors
1. Why is a single per-model temperature the right recalibration family? Under temperature plus per-class bias, fitted on the same calibration half, LA becomes identical to the baseline and TDE's case-level part is significantly positive under both proper scores (W1). Which result should a reader believe, and why?
2. Will you re-weight the within-cell AUC by n_c, as the split does, and compute it on the audited half? Under that weighting the CLIP-versus-geometry AUC difference is −0.0067 [−0.0120, −0.0019] on the full test set (W2). How would that change the CLIP paragraph of the abstract?
3. Can you train a plain Motifs predictor in the IETrans codebase, or report the case-level part between two independently trained MOTIFS models, so that IETrans's case-level loss can be attributed to its relabelling rather than to a different training run (W4)?
4. What equivalence margin would you defend for "no discrimination gained", and does the TDE AUC interval exclude it (W3)?

---

## Minor Issues
- L371: drop the randomization p = .724 for an algebraically zero statistic.
- The influence-function appendix gives the VG150 cell count as C = 6,346 against N* = 227,337, but those are the reconstructed-split figures. The canonical audit has 5,044 eligible cells. Say which split each figure refers to.
- `cvpr2027/supp/2_appendix.tex` (lines 1–4) has a LaTeX comment naming earlier venues (TMLR, Pattern Recognition). It does not appear in the PDF. If the LaTeX sources go into the anonymized archive, remove it: in a double-blind setting it reveals the paper's history.
- The comparison-weighted AUC values (0.5705 and so on) are barely above 0.5. Report the class-only floor and the per-cell distribution so readers can judge magnitudes.
- Table 1 caption: give the AUC bootstrap's replicate count (200) in the main text.

---

## Arithmetic Recompute (#610) and Recomputation Log

**Bounded procedures.** No statistic the bounded procedures cover (`p_from_test_statistic`, `grim`, `grimmer`, `n_from_df`) appears. The manuscript reports no t, F or χ² statistics with degrees of freedom, and no Likert-type means. Its p-values come from randomization and its intervals from influence functions or bootstraps. So no bounded receipt applies: `no_recomputable_statistics: checked main text Secs. 3–7, Tables 1–2 and supplementary tables; all inference is randomization, Hájek-influence or bootstrap based, outside the four bounded procedures`.

**Estimator-level recomputations.** All scripts are under `/tmp/claude-0/-home-user-WAGER/06889eb3-4869-50f6-bd62-a68f44e45a32/scratchpad/panel_R1/`. No repository file was modified.

| # | Recomputation | Result | Bearing |
|---|---|---|---|
| R1 | `pytest tests`; `verify_manuscript_numbers.py --driver cvpr2027/main.tex` | 30 tests passed; 298/298 numbers traced | S1 |
| R2 | TDE / LA / TDE−LA mR@50 split from cached ranks | Reproduces Table 1 to four decimals | S2 |
| R3 | Image-cluster bootstrap, 200 replicates, of the R2 case-level parts | SD / Hájek SE = 0.958, 1.033, 0.976; percentile CIs about 10% low | S2, W6 |
| R4 | Delta-method interval for the group share | TDE 86.6% [83.0, 90.2]; IETrans 97.3% [93.2, 101.3] | W12 |
| R5 | Coverage simulation with small cells (400 replicates each) | Coverage 80–84% when n_c = 2; 95.5% when n_c = 20 | W5 |
| R6 | Same-image transport partners; cross-image-only transport | 0.47% of pairs; TDE case-level +0.0130 → +0.0138 | Sampling Strategy comment |
| R7 | TDE, LA, IETrans matched split under temperature vs temperature + class bias | TDE: −0.00004 → +0.00445 (quadratic), +0.04388 → +0.02543 (log); LA ≡ base; IETrans robust | W1 |
| R8 | CLIP vs geometry under three recalibration families | Case-level part +0.00476 / +0.00331 / +0.00479, all CIs exclude zero | S5 |
| R9 | AUC weight concentration; AUC with split-consistent weighting | Top cell 26.9% of AUC weight vs 2.5% of split weight; TDE −0.0018 [−0.0038, +0.0014]; CLIP vs geometry −0.0067 [−0.0120, −0.0019] (full set), 0.0000 (audit half) | W2, W3 |
| R10 | Worked example by hand | Population R = 3/8, P = 0; U-statistic R = 1/2, P = −1/8 | W10 |

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | quality_rubrics.md Dim. 1 | NOT_ASSESSED | — | Outside the methodology remit (Reviewer 2) | — | no — another seat's remit |
| Methodological Rigor | quality_rubrics.md Dim. 2; reviewer configuration (calibration, U-statistics, inference) | PARTLY_MEETS | S1, S2, S3; W1, W2, W5, W6, W7 | The estimator, proofs and TDE design are sound. The confidence-matching family and the AUC weighting are under-justified, and in recomputation each changes a conclusion. | Recomputation covers the VG analyses; CIFAR and text not rechecked | yes — W1 and W2 bear on headline interpretations |
| Evidence Sufficiency | quality_rubrics.md Dim. 3 | PARTLY_MEETS | S2, S5; W3, W4, W11 | The headline group-level share is well supported. "No discrimination gained", the IETrans case-level loss and the zero-shot conclusion lack the evidence their wording implies. | Equivalence margins are domain judgements | yes — abstract-level claims |
| Argument Coherence | quality_rubrics.md Dim. 4 | PARTLY_MEETS | W1 (the "proper score agrees" heading vs the log-score table), W9, W10 | The narrative is mostly traceable, but several headings and summary sentences say more than the supplementary tables. | — | yes, jointly with W1 and W3 |
| Writing Quality | quality_rubrics.md Dim. 5 | MEETS | Sec. 3 setup; supp. "Formal results" | Precise and checkable; definitions are consistent across main text and supplement (with a glossary). | Methodology view only | no |
| Literature Integration | quality_rubrics.md Dim. 6 | NOT_ASSESSED | — | Reviewer 2's remit | — | no |
| Significance & Impact | quality_rubrics.md Dim. 7 | NOT_ASSESSED | — | Reviewer 3's remit; I note only that S4's operating-point control is a transferable contribution | — | no |
| Statistical reporting (Step 4a) | statistical_reporting_standards.md | PARTLY_MEETS | W3, W5, W6, W12; Analysis Methods (multiplicity) | Intervals are given throughout and effect sizes are in natural units. Missing: equivalence testing, share intervals, multiplicity framing, and a small-cell variance correction. | — | yes, through W3 |

**Recommendation rationale.** Two decision-bearing criteria are unresolved: Methodological Rigor (W1, W2) and Evidence Sufficiency (W3, W4). Each can be repaired with the authors' cached outputs:
- re-run the matched split under two or three recalibration families;
- re-weight the AUC across cells and compute it on the audited half;
- add equivalence tests;
- add a same-codebase baseline for IETrans, or state the confound in the abstract.

None invalidates the core estimator or the 87% group-level finding, which I verified. Together, however, they change what the abstract may say about TDE's discrimination and about the CLIP "converse". The strengths do not offset these, so the recommendation is **Major Revision**, and **Borderline** on the CVPR scale.
