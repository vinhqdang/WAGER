# Peer Review Report: Perspective Review (Peer Reviewer 3)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 Submission #***** (anonymous)
- **Review Date**: 2026-10-13
- **Review Round**: Round 1 (panel seat 4, mode full). Repository commit 2da86a9.

## Reviewer Information
### Reviewer Role
Peer Reviewer 3 (Perspective)

### Reviewer Identity
ML evaluation scientist from outside scene graph generation. Long-tail recognition, VQA bias, shortcut learning, grouping loss, label shift and distribution shift. I read the paper as an outsider to SGG conventions; where a point may be standard SGG practice I say so.

### Review Focus
Whether the "group-level vs case-level" accounting is the right lens when compared with neighbouring evaluation literatures, what it licenses as a claim about debiasing methods, and whether its conditionality (grouping, calibration, operating point, label mix) is stated in proportion to the headline.

## Overall Assessment

### Recommendation
**Weak Accept / Minor-to-Major Revision (borderline accept)**. Mapped to the template enum: **Major Revision** if the venue has no accept-with-conditions option. The contribution is real. The headline wording overstates what a grouping-conditional, calibration-conditional and label-mix-conditional quantity can say about "what the ten points bought".

### Confidence Score
3. Statistics and SGG internals are partly outside my expertise. The evaluation-design, shortcut and label-shift angle is within it.

Confidence is an uncertainty/scope disclosure only; it never changes consensus counts, severity, decision bearing, or arbitration.

### Calibration Status
`NOT_CALIBRATED`

`criteria_binding_unavailable` (no #684 criteria authority was supplied to this seat, so no venue-alignment claim is made).

### Criterion-Bound Judgements
| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Fit with adjacent evaluation literatures (long-tail, shortcut, grouping loss) | reviewer-assigned remit (no external criteria bound) | PARTLY_MEETS | text: Sec. 2 "The grouping loss [31] is the single-model relative of our case-level part" | Related work names the right neighbours but treats them as single-model cousins. It does not engage the transport/label-shift and worst-group literatures where the conclusion would be most useful | Not a systematic literature audit (R2's job) | no |
| Generality of the claim beyond three SGG checkpoints | reviewer-assigned remit | PARTLY_MEETS | text: Sec. 7 "we audit no later method"; Sec. 6 "The supplement applies the split to CIFAR-100-LT, long-tailed text and Waterbirds" | Three PredCls checkpoints, each one training run. Other domains are in the supplement and the body only gestures at them | Supplement read in part | yes: scope of the title claim |
| Interpretability of "group-level" as a verdict | reviewer-assigned remit | PARTLY_MEETS | text: Sec. 5 "Group-level is not a lesser gain"; Fig. 1 caption | The paper says group-level is not lesser, but the framing ("what did ten points buy") invites a deflationary reading the data do not fully support | none identified | yes |
| Robustness to label shift / deployment mix | reviewer-assigned remit | PARTLY_MEETS | text: Sec. 6 "seven of the eight group-level parts of Sec. 5 and this section change sign" | Honestly disclosed, but the headline shares are all computed at the benchmark's own label mix | none identified | yes |
| Practical value for benchmark practice | reviewer-assigned remit | MEETS | text: Sec. 7 "We suggest reporting, beside the headline metric, the declared grouping, both parts with intervals" | Concrete, cheap reporting recommendation with a stated archival requirement | Feasibility depends on archived logits | no |

Do not total, weight, average, or mechanically map these judgements to the recommendation.

### Summary Assessment
The paper gives an exact, model-free split of a paired score gain into a part that survives within-group label transport and a within-group covariance, extending Yates' Brier covariance decomposition to a two-model, thresholded, clustered-inference setting. It applies this to three released SGG debiasing checkpoints and finds the mean-recall gains are 87% (TDE), 94% (DLFE) and 97% (IETrans) group-level. My recomputation from the repository results agrees with the reported numbers. The instrument is careful. The validation designs (prior-only, shortcut, calibration-only, class-wise shift) are what a reader from the shortcut-learning literature wants to see, and the limitations paragraph is unusually frank. My concerns are about the distance between what is measured and what the title and abstract say. The measured quantity is conditional on a declared grouping, on a recalibration protocol, on an operating-point control and on the benchmark's own label mix, and each of these moves the headline share. It is also computed on single training runs. I recommend the claims be restated as conditional, the label-mix dependence be moved into the main argument, and one outside-SGG result be promoted to the body.

## Strengths

### S1: Validation designs that probe the failure modes an outsider would ask about
Four controlled constructions show where the split can and cannot be trusted. It is credited correctly for a prior-only change, a recorded-nowhere shortcut is credited to the case-level part, a calibration-only change is flagged, and a class-wise offset is separated.
**Evidence Anchor**: text: Sec. 4 "a calibration-only change ... is credited a large spurious case-level loss of −0.488 on raw outputs"

### S2: The operating-point control is a genuinely good evaluation idea
A training-free logit-adjusted baseline that changes no within-cell ranking reproduces +0.0941 of TDE's +0.0972, and the paper correctly concludes that a thresholded metric's case-level part is not by itself evidence of new discrimination. This transfers directly to long-tail recognition practice. I recomputed 0.0972 − 0.0941 = 0.0031 and 0.0841/0.0972 = 0.866 from results/sgg_share_intervals.json and results/sgg_grouping_share.json.
**Evidence Anchor**: text: Sec. 5 "So a case-level part of a thresholded metric is not by itself evidence of new discrimination."

### S3: Disclosed conditionality, and a case where aggregates mislead in the opposite direction
The CLIP-crop model is last on every aggregate yet carries more case-level covariance than geometry. The paper also reports where its own result flips (grouping, protocol, label mix). A reader from the shortcut literature will value that the paper does not treat the split as invariant.
**Evidence Anchor**: text: Sec. 7 "dropping the object class takes it to 18%"

### S4: Practical reporting proposal and exact, cheap computation
O(NK) on cached predictions, image-clustered intervals, with an honest note that most benchmarks do not archive the needed logits.
**Evidence Anchor**: text: Sec. 7 "archived top-k logits suffice for the AUC and the control, not for the exact split"

## Weaknesses

### W1: The headline share is conditional on four analyst choices, yet the abstract states it as a property of the method
Where: Abstract and Sec. 1 ("87% of the mean-recall@50 gain ... is group-level").
What is wrong: the 87% holds for one grouping (class pair), K = 50, the graph constraint, the micro-pooled (not official per-image) statistic, and the benchmark's label mix. The paper's own numbers move with each. With the subject class alone the share is 18%. Across protocols it runs 77% to 86% (Table 2). Without the graph constraint TDE's mean recall falls (ng-mR@50 −0.0337). The official per-image statistic gives 84%. The abstract carries the 87% and gives the 83–91% interval, which covers test sampling only. From the outside, an evaluation-bias reader will read "87% group-level" as a fact about TDE. It is a fact about TDE under one declared coordinate system.
Fix: put the share range across declared groupings and K/constraint in the abstract sentence (for example "77–86% across K; 18% if the grouping omits the object class"), and state that the interval is conditional on the grouping. Report the grouping sensitivity table in the body, not only Appendix K.
**Severity**: Major
**Evidence Anchor**: text: Abstract "87% of the mean-recall@50 gain (graph-constrained, micro-pooled; interval 83–91%) is group-level when cells are subject–object class pairs"
**Confidence**: 4 — adjacent field: evaluation-design and distribution-shift reading of the abstract; numbers checked against results/sgg_grouping_share.json.

### W2: "Group-level" is label-mix-dependent, so "what the ten points bought" is a statement about the benchmark's test distribution
Where: Sec. 6 "Under a label shift".
What is wrong: the paper shows that seven of eight group-level parts change sign along a path to uniform predicate frequencies within each pair. Mean recall already reweights by 1/n_y, so it is a partial label-shift correction itself. If the group-level gain is what a deployment with a different predicate mix would not receive, then the 87% is the part least transferable, and the 13% case-level part is the part that travels (Sec. 3 argues exactly this). The paper makes this point in Sec. 3 and Sec. 6 but the conclusion and abstract do not draw the consequence, and the intro's rhetorical question invites the reading that group-level gain is hollow. Conversely, for a user who wants rare predicates predicted more often (a legitimate goal), group-level movement is the product. The paper says "Group-level is not a lesser gain" once, in Sec. 5.
Fix: add a short "what to conclude" paragraph in the Conclusion that separates two practical questions (will it help under my label mix? does it discriminate better?) and states which part answers which. Promote the label-shift sign-flip result to the main text with its headline number for TDE and for the CLIP comparison.
**Severity**: Major
**Evidence Anchor**: text: Sec. 6 "seven of the eight group-level parts of Sec. 5 and this section change sign"
**Confidence**: 4 — core expertise: label shift and distribution shift.

### W3: The "null" on TDE's ranking is an equivalence claim whose margin was chosen after the fact and is not margin-invariant
Where: Abstract and Sec. 5 (within-cell AUC).
What is wrong: the abstract says AUC "excludes a change in TDE's ranking larger than 0.0034 ... but only one larger than 0.0077" under the two weightings. The margins are defined as fractions (5%, 10%, 25%) of the geometry-over-class-pair AUC gain, and results/sgg_equivalence.json shows equivalence at the 10% margin holds under relation weighting only (largest change excluded 0.00338 against a 10% margin of 0.00626), while under comparison weighting TDE is equivalent only at 25% (0.0077 against 0.0081) and fails 10% (0.00323). The reference gain itself is from a different, reconstructed model family and split (Sec. 4), not the released checkpoint. This is a reasonable reference scale from a shortcut-learning point of view, but the claim "TDE's ranking matches the baseline's within a tenth" is true under one weighting and "within a quarter" under the other. These choices were not pre-registered in the text, and the two weightings give opposite-sign point estimates (−0.0015 and +0.0026). The abstract does disclose both bounds, which is to the authors' credit, but the conclusion states "moves by less than 0.0034 under the split's weighting" without the second bound.
Fix: state the margin and its source before the result, give both weightings together in the Conclusion, and report the bound relative to the same fixed reference (the gain a case-level feature actually buys on this benchmark) for DLFE as well, where the AUC interval [−0.0004, +0.0056] is not an equivalence result at all.
**Severity**: Minor
**Evidence Anchor**: dataset: results/sgg_equivalence.json — TDE vs none, "tost" 10% margin equivalent under relation weighting, not under comparison weighting
**Confidence**: 3 — adjacent field: equivalence testing applied from general standards.

### W4: Generalisation beyond three released PredCls checkpoints rests on single training runs and a reconstructed split, and is under-reported in the body
Where: Sec. 5, Sec. 7 Limitations, Sec. 6 "Beyond scene graphs".
What is wrong: each released model is one training run, so the interval covers test sampling only; the TDE comparison shares weights with its baseline but DLFE and IETrans are not seed-controlled (IETrans is against a separately trained baseline, so the paper itself says it "does not isolate the effect of relabelling"). The 97% for IETrans therefore mixes a method effect with a training-run effect and should not sit beside TDE's 87% as if comparable. The controlled-predictor results (Sec. 4, 6) are on a VG150-style reconstruction, and the CLIP-versus-geometry result uses five seeds. The most transferable evidence to my field (Waterbirds, CIFAR-100-LT, text LT) is one paragraph in Sec. 6. A reader outside SGG would want to see at least one of these in the body, because it is the evidence that the split is useful for the broader "gain attribution" question the intro frames via VQA and long-tail citations. The repository numbers are informative here. In results/waterbirds_audit.json the group-reweighted model's Brier gain is +0.0637 with a group-level part of −0.0277 and case-level of +0.0914, i.e. a debiasing method whose gain is almost entirely case-level, the opposite of SGG's TDE. In results/cifar_lt_results.json the class-balanced model's case-level change is large and negative (about −0.196) while the group-level is about +0.197, with near-zero total. These are the strongest demonstrations that the split distinguishes methods, and they are not in the body.
Fix: move one cross-domain result (Waterbirds, with worst-group accuracy and recalibration caveat) into the body as a contrast; label IETrans in the abstract and Table 1 as "different training run, not a paired comparison"; add seed-to-seed variability for at least the baseline-versus-TDE comparison, or say clearly that the 87% has no training-variance interval.
**Severity**: Major
**Evidence Anchor**: text: Sec. 7 "Each released model is one training run: the intervals cover test sampling, not training variability"
**Confidence**: 4 — core expertise: long-tail and shortcut evaluations.

### W5: The case-level part is a mixed quantity (new discrimination, shortcuts, operating point), and the paper's own control shows it cannot be read as "better reasoning"
Where: Sec. 3 ("what the split means"), Sec. 4 shortcut design, Sec. 5 control, Sec. 7.
What is wrong: Sec. 4 shows a within-cell binary shortcut earns +0.041 case-level credit, and Sec. 7 says an unrecorded covariate with correlation 0.061 would account for the whole case-level gain of Sec. 4. The control then shows a purely operating-point change earns +0.0139 case-level credit under mean recall. So the case-level part cannot separate learning from shortcut exploitation or from threshold movement. The paper says this. The title-level framing and the naming "case-level" still suggest a cleaner reading ("telling which individual relations carry them"). From the shortcut-learning literature the standard remedy is a counterfactual or intervention-based probe. Here the natural one is to test whether the case-level part survives swapping or masking the features suspected of carrying the shortcut (e.g. the subject-size or position features Sec. 5 already uses for refinements), not only refining the grouping with them.
Fix: add one feature-ablation check on the best candidate shortcut (box geometry feeds the covariance in Sec. 4: MLP-SPATIAL buys +0.014 case-level, which a pure position prior would also buy) and report whether the case-level share for TDE survives it. Rename or gloss the term in the abstract as "within-pair covariance (including any shortcut)".
**Severity**: Minor
**Evidence Anchor**: text: Sec. 4 "the split measures all within-cell signal relative to the declared grouping, short-cut or not"
**Confidence**: 3 — adjacent field: shortcut-learning practice, not SGG internals.

### W6: Sensitivity to recalibration is handled by protocol choice, and the proper-score verdict flips sign with the protocol
Where: Sec. 5 "The proper score, matched".
What is wrong: TDE's matched quadratic case-level part is +0.00445 under the primary protocol (temperature plus per-class bias), −0.00006 with temperature alone, and −0.0184 with one shared temperature. The paper pre-declares the primary protocol by a stated criterion, which is good practice, and then reads the AUC instead. Two things remain. First, the recalibration is fitted on half the test images, so the primary number depends on a random split (the paper reports the cross-fit +0.00399 and 20 halves). Second, in the grouping-loss literature [31] the cross-calibration issue is precisely why single numbers are unstable. The proper-score claim in Sec. 5 is therefore best reported as sign-uncertain and the verdict carried by the AUC, as the paper does, but the abstract cites "+0.0045 under the pre-declared protocol" without the sign flip.
Fix: in the abstract replace the single value by the range across protocols, and add held-out calibration data if any exist for the reconstructed models in Sec. 4 (the authors note none exist for the released ones).
**Severity**: Minor
**Evidence Anchor**: text: Sec. 5 "with a temperature alone the part is −0.00006, [−0.00120, +0.00109], and with one temperature shared by both models −0.0184"
**Confidence**: 3 — adjacent field: calibration and grouping-loss literature.

### W7: Stakeholder and downstream framing is absent
Where: Sec. 7, whole paper.
What is wrong: the paper recommends reporting the split in benchmarks but does not discuss who is affected if a benchmark adopts it. Examples: method authors whose released checkpoints do not archive logits (the paper's own rerun was needed), downstream users of scene graphs (captioning, retrieval, VQA, robotics) for whom predicting "parked on (car, street)" more often may be exactly the intended utility, and leaderboards that could be gamed by choosing the declared grouping (the paper itself shows 18% to 90% for different groupings). A recommendation to "declare ϕ before the leaderboard opens" is the right idea but is stated as one clause.
Fix: add two or three sentences on grouping governance (who declares ϕ, how to prevent post-hoc selection), and on the user-facing meaning of group-level gain.
**Severity**: Minor
**Evidence Anchor**: absence: Sec. 7 — expected discussion of benchmark governance and downstream users of group-level gains; checked Sec. 1, Sec. 7, supplement keyword search for societal, deploy, governance
**Confidence**: 3 — adjacent field: evaluation practice.

## Detailed Comments

### Assumption Audit
- **Explicit assumptions**: grouping declared before the audit; image-clustered independence across images; non-dominating clusters; bounded scores; cells of at least three cases for nominal coverage (81.5% for two-case cells). All stated.
- **Implicit assumptions**: (i) that the object-pair cell is the right "what the model sees" variable in PredCls; the paper's own refinements show the verdict depends on it (90% vs 18%). (ii) That the micro-pooled mean recall is an acceptable proxy for the official per-image statistic; the paper says it "tracks" it, and reports 84% under official per-image shuffling. (iii) That relations within a cell are exchangeable apart from the label; Appendix text recognises duplicated-box and same-image pairs (0.9% of comparisons) and gives a cross-image check, which does not change signs.
- **Paradigmatic assumptions**: the paper adopts a "gain = prior movement + discrimination" ontology from forecast verification. For recognition users, a third item (operating-point choice) is already accommodated through the control. I would add that "group-level gain" is a feature of a label-distribution-matching goal, which the long-tail literature treats as the objective, not as a confound.

### Cross-Disciplinary Connections
- **Parallel research**: (a) Logit adjustment and balanced error in long-tail learning (Menon et al., cited), which the paper uses as its control. (b) Grouping loss (Perez-Lebel et al., cited) and the calibration-versus-refinement literature. (c) Worst-group robustness (Sagawa et al., cited in the supplement only), where the question "did the gain come from a group-level prior shift or from within-group discrimination" is routine. (d) Label-shift correction (Saerens et al.; Lipton et al., cited in the supplement). The paper cites these but treats them mainly as cousins.
- **Borrowing opportunities**: a Shapley-style or path decomposition over protocol choices (grouping, K, matching) would turn the sensitivity ranges into one reported "robustness set" rather than one primary number plus appendices. Reporting a worst-case over declared groupings, in the spirit of worst-group evaluation, is a natural analogue.
- **Methodological borrowing**: counterfactual or interventional probes from the shortcut literature (masking or swapping candidate shortcut features) would complement the transport counterfactual, which intervenes on labels but not on inputs.

### Practical Impact
- **Real-world application**: a reviewer or benchmark maintainer can use the operating-point control (a log-prior shift) as a cheap baseline that any debiasing paper must beat on both mean recall and within-cell AUC. This is the most actionable outcome of the paper.
- **Implementation feasibility**: requires full or top-k logits; most released checkpoints do not provide them.
- **Stakeholders**: see W7.

### Broader Implications
- **Ethical dimensions**: no direct ethical issues. Visual Genome relations are annotation-level, no personal data audit is claimed, and none is needed for this contribution.
- **Social impact**: low and indirect. The main risk is metric theatre: a new reporting standard that, if the grouping is chosen post hoc, can be used to reframe any gain as "case-level".
- **Future directions**: apply the split to open-vocabulary SGG and VLM-based relation prediction (acknowledged as not audited); extend to a hierarchy of groupings and report a lattice of shares.

## Cross-Disciplinary Reading Recommendations
Only items I can attest, all already cited in the manuscript or well established:
- Perez-Lebel, Le Morvan and Varoquaux on grouping loss (cited as [31]); a direct comparison of their estimator against the case-level part on one shared model pair would sharpen the stated relation.
- Sagawa et al. on group DRO (cited as [35]); worth moving from the supplement to the main text.
- [UNVERIFIED] search lead: literature on "decomposing the gain between two models" in forecast verification and in the model-comparison-under-shift literature, to check whether a paired-gain Yates decomposition has precedent beyond [47]. I cannot attest a specific reference.

## Questions for Authors
1. If a reader redefines the grouping as the class pair refined by the predicate-informative features a deployment would plausibly observe (position, size), the share stays near 90%. Is there any natural grouping a practitioner might pick under which TDE's share falls below 50%, and is the object-class-only 18% the only one found? A table of all tried groupings, in the body, would answer this.
2. For a deployment whose predicate mix within each pair is closer to uniform, what does the paper predict about the ranking of TDE, the logit-adjusted control and the baseline? Sec. 6 shows sign changes for group-level parts, but the actual ordering of the three models under, say, alpha = 0.5 of the label-shift path is not stated in the body.
3. For IETrans, how much of the 97% would remain if a baseline were trained with the same recipe and seed as the released checkpoint's training run? If this cannot be done, can the abstract flag IETrans as a different-run comparison?
4. The Waterbirds result shows group reweighting gaining almost entirely at case level while TDE gains at group level. Is this the contrast the authors want readers to take away about debiasing in general, and if so why is it absent from the main paper?

## Minor Issues
- Abstract is dense with parenthetical qualifiers; it carries about a dozen numbers. Consider moving the DLFE and IETrans numbers to the body and stating the headline conditionality in one sentence.
- Sec. 5 "Mean recall, split" uses "ng-mR" and "gc" abbreviations (ng, gc in the data files) that are defined only in a table caption.
- Reference [14] and [39] page lists show "3, 2" back-reference formatting that looks like a rendering artefact.
- The phrase "what is not claimed" in the intro is helpful; the same box could list "not a claim that group-level gain is of lower value" explicitly.

## Recomputation Log
Read-only recomputation against /home/user/WAGER/results (commit 2da86a9):
| Claim | Source | Result |
|---|---|---|
| TDE share group-level 87% | sgg_grouping_share.json, sgg_share_intervals.json | 0.0841/0.0972 = 0.8657, interval [0.826, 0.906] matches 83–91%; group + case − total = 0.0 |
| DLFE share 94% | Table 1 values | 0.1046/0.1112 = 0.941 OK |
| IETrans share 97% | Table 1, sgg_share_intervals.json | 0.972 OK; the stored interval [0.902, 1.044] exceeds 1, so a share interval cap is not applied, and the paper's abstract does not quote it |
| LA control reproduces gain | Table 1 | 0.0941 of 0.0972; TDE − LA = 0.0031 OK |
| SGCls TDE 99% group-level | sgg_sgcls_audit.json | 0.9852 OK; TDE-vs-LA share is −30 and not meaningful (total near zero), a ratio the paper correctly does not quote |
| TDE within-cell AUC bounds 0.0034 / 0.0077 | sgg_equivalence.json | 90% upper bounds 0.00338 (relation), 0.00771 (comparison) OK; at 10% margin only relation weighting is equivalent (see W3) |
| Waterbirds / CIFAR-LT contrasts (W4) | waterbirds_audit.json, cifar_lt_results.json | GRW Brier total +0.0637 = group −0.0277 + case +0.0914 (check: sums to total within rounding); CB total +0.0014, group ≈ +0.197, case ≈ −0.196 |
I found no arithmetic discrepancy in the quantities I checked. I did not rerun the model-fitting code and did not verify the proofs.

## Scope Note
This report covers the perspective of an evaluation scientist outside SGG. It does not assess proofs, estimator asymptotics (Reviewer 1's remit) or citation completeness (Reviewer 2's remit). Findings are independent of any other seat's report, which I did not read.
