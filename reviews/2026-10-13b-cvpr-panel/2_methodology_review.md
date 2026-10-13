# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission #***** (anonymous), 8 pages plus references, 38-page supplement; repository commit 2da86a9
- **Review Date**: 2026-10-13
- **Review Round**: Round 1 (simulated CVPR 2027 panel, mode full)

## Reviewer Information

### Reviewer Role
Peer Reviewer 1 (Methodology)

### Reviewer Identity
Evaluation-statistics reviewer for vision benchmarks: calibration, proper scores, U-statistics, equivalence testing, and uncertainty on benchmark metrics.

### Review Focus
Whether the exact two-part gain decomposition, its estimator and intervals, its validation, and the ranking-equivalence ("null") claims support the audit conclusions about TDE, DLFE and IETrans. Literature coverage and cross-disciplinary significance are left to other seats.

### Calibration Status
`NOT_CALIBRATED`

`criteria_binding_unavailable` (no venue criteria were supplied to this seat, so no venue-alignment claim is made).

---

## Overall Assessment

### Recommendation
**Major Revision** (confidence 4 of 5: core expertise in proper scores, U-statistics and equivalence testing; I did not verify every supplementary proof line by line).

### Summary Assessment
The paper gives an exact, model-free split of a paired metric gain into a part that survives within-cell label transport and a within-cell covariance, with an O(NK) unbiased U-statistic estimator and image-clustered intervals. The algebra (Theorem 1) and the implementation are sound. From the released logits and the repository code I reproduced the headline TDE mean-recall split exactly (+0.09715 = +0.08411 group + 0.01305 case), the share (86.6%, interval [82.6%, 90.6%]) and the Table 2 and Table 1 entries I checked. The validation by designed nulls, algebraic zeros and a ranking-invariant control is the paper's best methodological feature, and the authors report protocol sensitivity candidly.

My concerns are about what the numbers can support. (1) The "ranking is unchanged" claim rests on an AUC whose weighting puts about 65% of the comparison weight on head–head predicate pairs and almost none on the rare predicates that mean recall rewards. The equivalence margin is post hoc and borrowed from a different model family. With a mean-recall-aligned weighting, my own recomputation gives an interval about four times wider. (2) The headline "87% group-level" is statistically indistinguishable from what a no-discrimination control yields (85%), is undefined or above 100% without the graph constraint, and ranges from 18% to 90% across defensible groupings. (3) The proper-score case-level part is protocol-identified only; it changes sign across three recalibration families. (4) Method-level attributions come from single released runs, and the IETrans comparison is not controlled. The inferential theorem does not apply to VG150, so the intervals rest on simulation. I recommend major revision: most fixes are re-analysis and re-framing, not new theory.

---

## Recomputation Log (read-only, outside the repository)

| # | Claim | Source | What I did | Result |
|---|-------|--------|-----------|--------|
| R1 | TDE mR@50 split +0.0972 = +0.0841 + 0.0130, case CI [+0.0093, +0.0168] | `experiments/run_sgg_recall_split.py`, `data/vg_motifs/wager_sgg` | Re-ran the split from cached ranks with `wager.antisymmetric.decompose_gain_matrix` | Exact match: 0.097154 / 0.084107 / 0.013048; Hájek SE 0.001933 |
| R2 | Share 87%, interval [83%, 91%] | `results/sgg_share_intervals.json` | Divided; checked the stored interval | 0.8657, [0.8256, 0.9058]. IETrans share 0.973, interval [0.902, 1.044] (exceeds 1) |
| R3 | Table 2 shares 77% (K=20) to 86% (K=100); TDE vs LA row | `results/sgg_recall_split*.json` | Recomputed | 0.773, 0.866, 0.858 match. Without the graph constraint the "share" is 3.58, 1.38, 1.48 (total gain negative). TDE vs LA: −0.0234 (K=20), +0.0031 (K=50), +0.0300 (K=100); no-constraint −0.0792, −0.1272, −0.1549 |
| R4 | Abstract: LA recovers +0.094 of +0.097 at under a tenth of R@50 cost; F@50 0.344 vs 0.322 | `results/sgg_fk.json`, Table 1 | Recomputed | 0.0941 of 0.0972; R@50 cost 0.0175 vs 0.2023 (8.6%); F@50 0.3435 vs 0.3217 |
| R5 | Coverage 94.0% vs 88.6%; null type-I 0.030; 81.5% at n_c=2; 96.3% (hit sim) | `results/antisymmetric_simulation.json`, `sim_small_cells.json`, `sim_hit_coverage.json` | Read stored values | Match. Replications are 200–500, so Monte Carlo SE is 1.0–1.5 points; "from three up it is nominal" rests on 200 runs per cell size |
| R6 | Within-cell AUC change, TDE vs baseline: relation-weighted −0.0015, comparison-weighted +0.0026; 90% bounds ±0.0034 / 0.0077 | `results/sgg_equivalence.json`; own AUC code | Re-derived AUCs from cached probabilities on all identified relations; 100-replicate image bootstrap | Relation −0.0018 (90% [−0.0038, +0.0011]); comparison +0.0025 (90% [−0.0023, +0.0078]). Agrees with the paper within bootstrap and subsample differences |
| R7 | Ranking claim under other weightings (new) | own computation | (a) 318 predicate pairs with at least 500 comparisons, equal weight; (b) comparison weights times (1/n_y + 1/n_z), a mean-recall-aligned weighting with 86% of weight on pairs that involve a body or tail predicate | (a) ΔAUC −0.0040, 90% [−0.0117, +0.0016]; (b) +0.0018, 90% [−0.0082, +0.0136]. Equal-weight mean over all 957 predicate pairs: −0.0153. Exploratory, 100 replicates |
| R8 | Hájek cluster SE vs delete-a-group jackknife for the headline mean-recall case-level part (new) | own computation, 100 image groups, one seed | Re-ran `decompose_gain_matrix` per deleted group, with weights re-estimated and with weights held fixed | Jackknife SE 0.002186 (re-estimated weights) and 0.002182 (fixed weights) vs Hájek 0.001933: the Hájek SE is 11.5% smaller. Weight estimation is not the cause. Share jackknife SE 0.02045 matches the stored 0.02046 |
| R9 | p = .555 for TDE's matched quadratic case-level part (Supp. O, Table 21 text) | `experiments/run_sgg_audit_wager.py`, `results/sgg_audit_motifs.json` | Traced the test | The p = .555 belongs to the temperature-only matching (case-level −0.00006, CI [−0.00120, +0.00109]). No randomization p is stored for the primary temperature-plus-class-bias protocol |
| R10 | p = .002 for case-level gains | Supp. line 1068 | Checked the floor | Equals 1/(499+1), the granularity floor; consistent |
| R11 | Bounded arithmetic procedures (p from a test statistic, GRIM, GRIMMER, n from df) | whole manuscript | Scanned | None applicable: no t/F/chi-square statistics with df, and no integer-scale means. `no_recomputable_statistics` |

Not verified: proofs of Theorems 2–3 and Propositions 1–5 (I checked the Theorem 1 identity, the estimator identity enforced in code, and the Eq. (19) influence function against the code and the jackknife only). The CIFAR, text and Waterbirds supplementary studies were not re-run.

---

## Strengths

### S1: Exact additive identity with an implementation that enforces it
Theorem 1 gives ΔT = ΔP + ΔR for any integrable contrast, including thresholded hit contrasts. The estimator raises an error if the identity fails, and I reproduced the headline split to six digits from the released logits.
**Evidence Anchor**: text: "These satisfy ∆Td c = ∆P d c + ∆Rd c exactly in every sample" (Sec. 3, Eq. 4–6) and `wager/antisymmetric.py` `decompose_gain_matrix`

### S2: Validation against known truth, including algebraic and designed nulls
Class-pair-only models receive exactly zero case-level gain (Theorem 1 forces it). The simulations include a prior-only improvement, an unrecorded shortcut, a calibration-only change and a within-cell null (type-I 0.030 over 200 runs). They show where the split does and does not separate effects, including its failure under raw-output calibration differences (−0.488).
**Evidence Anchor**: dataset: `results/antisymmetric_simulation.json` (null_type1_alpha_005 = 0.03; coverage_clustered = 0.94 vs coverage_iid_naive = 0.886)

### S3: A training-free operating-point control that falsifies the naive reading of a thresholded case-level part
Subtracting the training log-prior changes no within-cell ranking, yet it reproduces TDE's mean-recall gain, group-level part and tier profile at K=50. This shows that a thresholded metric's case-level part is not evidence of new discrimination, and it is the most informative design choice in the paper.
**Evidence Anchor**: table: Table 1 rows TDE and LA (case-level +.0130 vs +.0139; TDE−LA case-level −.0008 [−.0050, +.0033])

### S4: Candid reporting of protocol, weighting and grouping sensitivity
The paper reports sign changes under three recalibration families, six recall protocols, two AUC weightings, label-mix paths and groupings. It also states that no equivalence margin was registered and that the control's match is specific to K=50.
**Evidence Anchor**: text: Supp. Q.4 "No margin was registered before the audit; the grid shows how the verdict depends on it."

### S5: Reproducible audit artifacts
Cached logits, rank files, scripts and per-result JSON allow exact recomputation (R1–R4 reproduced without access to any private artifact).
**Evidence Anchor**: dataset: `results/sgg_recall_split.json` and `data/vg_motifs/wager_sgg/`

---

## Weaknesses (ranked by decision impact)

### W1: The "TDE's ranking is unchanged" claim rests on an AUC weighting that is not aligned with mean recall, a post hoc margin and a margin scale from a different model family
**Problem**: The primary null is a within-cell AUC change, bounded by a 90% bootstrap interval. The relation weighting is nc(y)nc(z)/nc and the comparison weighting is nc(y)nc(z). By the paper's own Table 33, head–head predicate pairs carry 0.649 of the comparison weight, tail–tail pairs about 0.000, and TDE's tail-pair interval is [−.1918, +.0494]. Mean recall instead weights every predicate equally (w(y) = 1/(K n_y)), so the rare predicates the metric rewards are almost invisible to the AUC used to certify "no ranking change". In my recomputation (R7), a pair-balanced AUC over 318 well-populated predicate pairs gives −0.0040 with 90% interval [−0.0117, +0.0016], and a mean-recall-aligned weighting gives +0.0018 with 90% interval [−0.0082, +0.0136]. The headline exclusion bound of 0.0034 becomes 0.0117–0.0136 under these weightings. The paper itself says TDE "gains discrimination between some predicate pairs and loses it between others", and an average of mixed-sign changes is not evidence that rankings did not change. The margins (5/10/25% of the AUC gain of box geometry over the class pair) are unregistered and come from the controlled VG150-style predictors, not from the released checkpoints. The equivalence calls are therefore weighting- and margin-specific, yet the abstract states the bound without the weighting caveat.
**Evidence Anchor**: table: Supp. Table 33 head-head weight 0.649, tail-tail weight 0.000, TDE vs base tail-tail −.0675 [−.1918, +.0494]
**Why it matters**: It is the evidence for the central reading that TDE's gain is "a change in which predicates the model favours within each object pair" and not better case-level discrimination.
**Suggestion**: Report the AUC with the same predicate weighting as mean recall (and per tier) as a primary or co-primary quantity, with a TOST at margins defined before looking at TDE (for example from the baseline's seed-to-seed AUC variation or from the measured AUC change between two independently trained baselines). Report per-predicate-pair changes with a multiplicity-adjusted display, and use more than 200 bootstrap replicates for 5%/95% bounds. Reword the abstract to name the weighting.
**Severity**: Major
**Confidence**: 4 — core expertise: equivalence testing and U-statistics; the recomputation is exploratory (100 replicates)

### W2: The headline "87% group-level" is not a share attributable to non-discrimination and is not stable across the choices that define it
**Problem**: The ranking-invariant control already earns +0.0139 of case-level credit (a share of 85%, Table 1 row LA), so a case-level part of 13% is the value an intervention with no new discrimination produces. The authors say as much, but the abstract leads with "87% of the mean-recall@50 gain (graph-constrained, micro-pooled) is group-level". Without the graph constraint the total gain is negative, and the "share" is 358%, 138% and 148% at K = 20, 50, 100 (R3). The control matches TDE only at K=50 under the constraint (TDE−LA ranges −0.0234 to +0.0300 with the constraint, and −0.0792 to −0.1549 without it), yet the abstract states the match without that qualifier. The share also depends on the grouping: 18% (subject class), 87% (class pair), 90% (class pair refined by position or size), and the supplement's four-case example gives ΔR of 1.600 and 0.000 under two equally fine partitions, with "we do not have a procedure that resolves it". The micro-pooled statistic is not the official per-image mean recall (+0.0972 vs +0.1017; share 84%). Intervals for a ratio that can exceed 1 (IETrans: [90.2%, 104.4%]) should not be read as shares.
**Evidence Anchor**: text: abstract "recovers +0.094 of its +0.097 at under a tenth of TDE’s cost in recall" with Table 2 row TDE vs LA at K=100 (+0.0300) and ng-mR@100 (+0.0148 case-level, [+0.0064, +0.0232])
**Why it matters**: A reader will take "87%" as the portion of the gain that is not discrimination. The correct reading is that the control reaches the same group-level fraction, and that the fraction is a property of one declared grouping, one cut-off, one constraint and one pooling.
**Suggestion**: Lead with the control-referenced quantity (TDE minus LA, per cut-off, with and without the graph constraint) and the AUC null, and demote the share to a descriptive statistic that is reported only where total gain is positive and with its grouping named. Report the official per-image statistic's split as primary or alongside, and add a within-cell label-heterogeneity diagnostic for each grouping (the authors already identify this as the missing piece).
**Severity**: Major
**Confidence**: 4 — core expertise: metric decomposition and benchmark estimands

### W3: Method-level conclusions about TDE, DLFE and IETrans rest on one released run each, and the IETrans comparison is not controlled
**Problem**: Each model is one training run, and the intervals cover test sampling only. The abstract and conclusion nonetheless state method-level findings ("DLFE ... its within-pair ranking does not move detectably; IETrans ... its within-pair ranking falls"). IETrans is compared with a separately trained baseline (the released checkpoint is the IETrans+Rwt variant with a reweighted loss), so a fall in AUC or a case-level loss cannot be attributed to relabelling, as Sec. 5 concedes ("does not isolate the effect of relabelling"). For DLFE, the mean-recall case-level part is +0.0065 [+0.0010, +0.0120], which excludes zero, while the abstract reports "no detected change in within-pair ranking" without saying that the covariance part is detected. Seed variability is measured only for the CIFAR and CLIP-head studies (and there it varies roughly fourfold in CIFAR), so there is no estimate of how much training variation alone moves group share or within-cell AUC for a MOTIFS-family model.
**Evidence Anchor**: text: Sec. 5 "so this compares two separately trained models and does not isolate the effect of relabelling"; Sec. 7 "the intervals cover test sampling, not training"
**Why it matters**: Without a training-variation reference, a null or a decline in AUC cannot be separated from the difference between two independent training runs of the same architecture.
**Suggestion**: Train (or obtain) several MOTIFS-SUM baselines and report the spread of group share and AUC change between them; use it as the reference for IETrans and as the margin scale in W1. In the abstract, state "released checkpoint" for each method and that IETrans is uncontrolled. Say explicitly that DLFE's covariance part is detected.
**Severity**: Major
**Confidence**: 4 — core expertise: uncertainty on benchmark metrics

### W4: The proper-score case-level part is identified only up to a protocol choice, and the stated criterion does not remove the ambiguity
**Problem**: TDE's quadratic case-level part is −0.00006 (temperature), −0.0184 (shared temperature) and +0.00445 (temperature plus per-class bias), with log-score values +0.04396, −0.0928 and +0.02543 (Table 34). The group-level part moves from −0.183 to −0.014 across the same families. Sec. 3 chooses the third family by the criterion that it must absorb a cell-constant log-odds shift, and Supp. Q.4 itself shows that a ranking-invariant, pair-varying shift (removing the frequency prior) earns +0.00817, more than TDE's +0.00445, because a per-class bias cannot absorb it. So the primary-protocol value cannot be read as evidence about ranking, as the paper says, but contribution (ii) still claims the split "separates calibration, prior and shortcut effects". The data show it does not separate pair-varying calibration. The family is described as "fixed before any gain is read", which a reader cannot check, and the calibration and audit halves come from one random image split (20 halves are reported in the supplement, but intervals treat the fitted calibration as fixed). The only stored randomization p (.555) is for the temperature-only protocol, not for the primary one (R9), and the supplement sentence does not say which protocol it concerns.
**Evidence Anchor**: table: Supp. Table 34, TDE vs base, quadratic: temperature −0.00006, shared temperature −0.01839, temperature + class bias +0.00445
**Why it matters**: The abstract reports "+0.0045 under the pre-declared matching protocol" for TDE. A reader needs to see that the sign is a property of the recalibration family, and that a ranking-invariant intervention exceeds it.
**Suggestion**: Make the AUC (or a rank-based contrast) the primary case-level statistic for released checkpoints and present the proper-score case-level part as a protocol-indexed diagnostic. Add a family that allows cell-specific shifts (for example a per-cell offset fitted on the calibration half, or a cell-by-class bias with shrinkage), report the randomization p for the primary protocol, and give a timestamped record of the declaration.
**Severity**: Major
**Confidence**: 4 — core expertise: proper scores and calibration

### W5: Theorem 4 does not license the reported intervals; coverage rests on simulations with limited replication, and the headline Hájek SE is below a jackknife SE
**Problem**: The theorem needs a fixed finite support for ϕ with every cell diverging, and the supplement states that VG150 fails the cell-count condition (C/√N* ≈ 13.3). The intervals are therefore supported by simulation, with 200–500 replicates (Monte Carlo SE 1–1.5 points), a fixed-design hit simulation (cells and priors held fixed across replicates), and 1.0% of audited relations in two-case cells where coverage is 81.5%. On the real headline quantity (R8), the delete-a-group jackknife SE for the mean-recall case-level part is 0.00219 against 0.00193 from the Hájek influence function (about 12% smaller; one jackknife seed, so roughly ±7% noise). That implies roughly 92% actual coverage for a nominal 95% interval if the jackknife is right. The qualitative conclusion survives (0.0130 ± 1.96 × 0.00219 still excludes zero). Finer groupings in Supp. K, which are used to argue robustness of the 90% share, contain many more small cells, where the paper's own simulation shows under-coverage.
**Evidence Anchor**: text: Supp. J "the theorem does not by itself license the reported intervals"
**Why it matters**: The intervals carry every inference in the paper, and the stated validation is the simulation, which is not run on the real estimand with its heavy-tailed cells, hit contrasts and recalibration.
**Suggestion**: Use the delete-a-group jackknife (already implemented in `cross_image_split`) for the headline intervals, or report both. State the finite-sample coverage in the main text as simulation-supported. Run a parametric bootstrap on VG150's own cell structure with TDE-like hit contrasts and at least 1,000 replicates. The condition C = o(√N*) appears stronger than needed for mean-zero independent degenerate terms (their sum is O_p(√C/N*)); a sharper statement would let the theorem cover VG150.
**Severity**: Minor
**Confidence**: 3 — adjacent depth on the degenerate-term argument; the jackknife check is a single seed

### W6: Forking paths and multiplicity are acknowledged but not controlled
**Problem**: The audit spans six recall protocols, two scores, three recalibration families, two AUC weightings, two matching halves, label-mix paths and groupings. A "primary" configuration is named for each, but no registry or timestamp exists, and the abstract's selection (K=50 with graph constraint, micro pooling, class-pair cells, temperature plus per-class bias) is the one at which the control matches TDE. The sign change across protocols is reported honestly, so this is a framing and verification issue more than a hidden analysis.
**Evidence Anchor**: absence: manuscript and supplement — expected a dated record of which configuration was declared primary before gains were read; checked abstract, Sec. 3, Sec. 5, Supp. Q.4 and Supp. K
**Why it matters**: With this many configurations, the reader cannot tell which agreement is a finding and which is selection.
**Suggestion**: Provide an anonymized, timestamped declaration (or state that it is post hoc), tabulate every configuration's headline statistic in one figure, and flag which abstract numbers are not stable across configurations.
**Severity**: Minor
**Confidence**: 3 — core expertise, but no history was inspected by design

---

## Detailed Comments

### Research Questions & Hypotheses
The question (which part of a gain is group-level) is well posed and answerable for a declared grouping. The estimand's dependence on ϕ is the main interpretive risk (W2).

### Research Design
Design is a paired audit of frozen models with cached full-label scores. Appropriate, and the exact identity avoids a fitted reference model. The controlled predictors on a reconstructed VG150-style split are used for validation and for equivalence-margin scales, but they are a different data split and model family from the released checkpoints (W1).

### Sampling Strategy
Test relations only; singletons are excluded and reported (about 1.1% of relations; 99.0% / 98.9% coverage). The identified subpopulation changes with the grouping.

### Data Collection
Released checkpoints re-run once with the authors' code, with an offline evaluator replay reproducing official numbers to four decimals (the stored recalls are consistent with this). Recalibration is fitted on a random half of test images because no validation outputs were released.

### Analysis Methods
Hájek influence functions with image clustering; delete-a-group jackknife for shares and label-shift paths; percentile image bootstrap for AUC; cyclic randomization as a secondary diagnostic. See W1, W4, W5. A minor point: the log-score results use a probability floor of 1e-6, so the boundedness condition of Theorem 4 holds only with M ≈ 13.8, and results depend on the floor.

### Results Presentation
Tables are complete, and non-significant and sign-changing results are shown. The abstract compresses several protocol-specific statements into unqualified sentences (W2, W4).

### Reproducibility
Strong. I reproduced the headline split and several stored numbers directly from the repository data (R1–R6).

### Methodological Fallacies Detected
- Estimand dependence on the partition (a Simpson-type ambiguity across equally fine partitions) is acknowledged but unresolved (W2).
- Averaging mixed-sign pairwise AUC changes into a single "ranking unchanged" statement (W1).
- Single-run attribution of a method effect (W3).
- No p-hacking found in the reported numbers; multiplicity is uncontrolled and disclosed (W6).

---

## Questions for Authors

1. Under the mean-recall predicate weighting (each predicate equally), what is the within-cell AUC change for TDE and its 90% interval, overall and for body and tail pairs? Does the equivalence claim at the 10% margin survive?
2. What does the headline mean-recall split look like with the delete-a-group jackknife in place of the Hájek interval, and what is its coverage in a simulation that uses VG150's own cell structure and TDE's hit contrasts?
3. Can you obtain two or more independently trained MOTIFS-SUM baselines, so that the spread of group share and AUC change from training variation alone sets the scale for the TDE, DLFE and IETrans comparisons?
4. Was the choice of the temperature-plus-class-bias family and of the 90%/95% interval pair timestamped before gains were read, and what is the randomization p for the primary protocol?
5. Is the TDE-vs-control match at K=50 a robust finding or a coincidence of the cut-off, given the −0.0234 to +0.0300 range of TDE−LA across K with the constraint?

---

## Minor Issues

### Language / Grammar
- The abstract is a single long paragraph packing about fifteen numbers; separating the control-referenced result from the share would help.

### Citation Format
- None from the methodology angle.

### Figures and Tables
- Table 2's intervals are truncated in the text dump ("iny[…"); check that the PDF shows full intervals.
- Shares that exceed 100% (IETrans interval upper bound 104.4%) and shares for negative total gains should be flagged or suppressed in tables.
- State the number of bootstrap replicates (200) and jackknife groups (100) in the main-text table captions, not only in the supplement.

### Layout
- None.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Methodological Rigor | `references/quality_rubrics.md` (rubric applied qualitatively; no venue criteria bound) | PARTLY_MEETS | table: Table 34; table: Supp. Table 33; dataset: `results/sgg_equivalence.json` | Exact identity, validation and control are strong; the ranking null (W1) and protocol-identified proper-score part (W4) are not yet rigorous | Proofs of Theorems 2–3 and Props 1–5 not verified; recomputations R7–R8 exploratory | yes: W1 and W4 bear on the central reading |
| Evidence Sufficiency | same | PARTLY_MEETS | text: abstract "recovers +0.094 of its +0.097"; table: Table 2 | Headline share and equivalence bound are supported only under named weightings, cut-offs and groupings (W1, W2); single runs (W3) | Statements are caveated in the body | yes: W2, W3 |
| Argument Coherence | same | MEETS | text: Sec. 5 "What that licenses" | Conclusions are mostly hedged consistently in the body; abstract compresses | none identified | no: framing only |
| Originality | same | NOT_ASSESSED | — | Outside this seat's remit | Literature novelty belongs to Reviewer 2 | no |
| Writing Quality | same | NOT_ASSESSED | — | Outside this seat's remit | — | no |
| Literature Integration | same | NOT_ASSESSED | — | Outside this seat's remit | — | no |
| Significance & Impact | same | NOT_ASSESSED | — | Outside this seat's remit | — | no |

The recommendation rests on the unresolved decision-bearing items W1–W4. All four are repairable by re-analysis and re-framing (weighting, control-referenced reporting, baseline-variation reference, protocol-indexed proper-score claims); none requires new theory.
