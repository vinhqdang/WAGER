# Peer Review Report (Journal-Fit Reviewer seat, CVPR 2027 panel)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 Submission #***** (anonymous); repository commit 18a72c9
- **Review Date**: 2026-10-13
- **Review Round**: Round 1 (simulated panel, mode full)

## Reviewer Information
- **Reviewer Role**: Journal-Fit Reviewer (internal role EIC), contributing one review card. The editorial decision belongs to the synthesizer.
- **Reviewer Identity**: Configured perspective of a CVPR area chair for scene understanding and evaluation, with experience handling SGG method, SGG debiasing and benchmark-analysis papers.
- **Review Focus**: Fit to CVPR and its readership, originality, significance, structural coherence, and whether claims match what is delivered. Methodological detail is left to other seats.
- **Calibration Status**: `NOT_CALIBRATED`
- **Binding**: `criteria_binding_unavailable`. There is no author-confirmed target context. The CVPR remarks below are a configured perspective, not a venue-alignment determination.

## Overall Assessment

### Recommendation: **Major Revision** (borderline with Minor Revision on content, held back by scope and presentation)
### Confidence: 4/5 (core area: SGG evaluation and debiasing; I did not re-derive the proofs, which belong to the methodology seat)

### Recomputation log (read-only)
- `python experiments/verify_manuscript_numbers.py --driver cvpr2027/main.tex` printed "all 479 manuscript numbers trace to committed results". It listed 224 numbers printed in the paper and the rest in the supplement. This checks number-to-result provenance only, not whether the claim built on a number is sound.
- By hand from the paper's own figures:
  - TDE share: 0.0841/0.0972 = 86.5%, reported as 87%. Parts: 0.0841 + 0.0130 = 0.0971, a rounding match.
  - Control (logit adjustment, LA): 0.0802 + 0.0139 = 0.0941. TDE minus LA: 0.0972 − 0.0941 = 0.0031, as in Table 1.
  - R@50 cost: baseline 0.6612 − control 0.6437 = 0.0175, and 0.6612 − TDE 0.4588 = 0.2024. The paper says 0.2023, which is consistent given rounding.
  - F@50 (harmonic mean of R@50 and mR@50): TDE 0.322, LA 0.344. Both match the paper.
  - IETrans share: 0.2143/0.2204 = 97.2%. SGCls share: 0.0510/0.0517 = 98.6%. Both are reported as 97% and 99%.
- `results/sgg_equivalence.json`: the margin (0.1 × geometry-vs-class AUC gain) is 0.0063 for relation-weighted and 0.0032 for comparison-weighted AUC. The relation-weighted result is flagged `equivalent: True`, with a 90% CI of [−0.0037, +0.0008]. The comparison-weighted result is `equivalent: False`, with a minimal detectable change (MDE) of 0.0082, which is above the margin. So the equivalence headline holds for one of two weightings and is a non-detection for the other. The paper discloses this in Sec. 5, but the abstract and conclusion lead with "equivalent".
- `results/sgg_grouping_share.json`: grouping by class pair gives case-level 0.0130 of 0.0972. Grouping by subject class alone gives case-level 0.0794, which is a group-level share of about 18%. This matches Limitations ("dropping the object class takes it to 18%"). The headline therefore rests on one declared grouping.
- No numerical discrepancy was found between the paper and the committed results. My concerns are about scope, framing and presentation, not arithmetic.

### Summary Assessment
The paper asks what a ten-point mean-recall gain actually buys. It proposes an exact, model-free split of a score gain between two frozen models into a group-level part and a case-level covariance. The split works by scoring each prediction against another relation's label from the same subject-object pair. It applies the split to the mean-recall gain of two released SGG checkpoints. Of TDE's gain, 87% is group-level. A training-free logit adjustment that cannot change within-pair ranking recovers 0.0941 of the 0.0972 points. IETrans's gain is 97% group-level. A CLIP-crop model ranked last by every aggregate shows more case-level covariance than a geometry model.

This is a thoughtful evaluation paper on a topic CVPR readers care about, and the numbers trace to committed results. The empirical SGG content is narrow for an audit with a general claim. It covers two 2020-2022 Neural-Motifs checkpoints on VG150, mostly PredCls, with one grouping, and no current SGG method. The central conclusion (a logit adjustment rivals TDE) is already known and cited. The decomposition itself descends from Yates, and its value to the field depends on the broader audit that the paper explicitly declines to do. The 8-page body is extremely dense, and key evidence sits in a 36-page supplement. I recommend Major Revision, aimed at breadth of audit and at presentation.

## Strengths

### S1: Timely, well-posed question for the SGG community
The question of what a mean-recall gain buys fits CVPR's evaluation and scene-understanding scope. The paper identifies a concrete, testable ambiguity: a model can move probability toward rare predicates within each object pair, or it can discriminate individual relations, and mean recall credits both.
**Evidence Anchor**: text: Sec. 1 "The metric credits both alike."

### S2: Exact additive accounting extended to thresholded metrics, with an operating-point control
The split covers proper scores and mean recall itself, with image-clustered intervals. The operating-point control is a no-training logit adjustment that changes no within-pair ranking. This addresses the obvious objection that a thresholded metric earns covariance from a moved threshold.
**Evidence Anchor**: table: Table 1, LA row: +.0941 total, +.0802 group, +.0139 case, against TDE +.0972, +.0841, +.0130

### S3: Validation designs, honest scope statements and reproducible provenance
Sec. 4 checks zero-by-construction cases, null coverage, and an unrecorded shortcut that is credited to the case-level part. The paper states the split is grouping-conditional and not recalibration-invariant, and notes that no IETrans baseline was released. The paper's numbers all trace to committed JSON results.
**Evidence Anchor**: text: Sec. 1 "What is not claimed." and Sec. 7 Limitations; recomputation log above

### S4: Pixel-model counterexample shows the split separates things the aggregates cannot
A model ranked last by accuracy and by quadratic score carries a larger case-level part, and the paper checks that this is not better ranking with within-cell AUC.
**Evidence Anchor**: text: Sec. 6 "The CLIP model's case-level advantage is real covariance; under the primary weighting it is not better ranking."

## Weaknesses (ranked by decision impact)

### W1: Empirical scope is too narrow for the audit-style title and for CVPR's evaluation standard
**Problem**: The SGG audits cover two released Neural-Motifs checkpoints, TDE (2020) and IETrans (2022), on VG150. SGCls and SGDet appear only as a replication of TDE. The paper says "we audit no later method." The conclusion proposes benchmark-reporting changes and states the finding in field-level terms ("the field's metrics report the sum"). No current SGG method is audited, including transformer or DETR-style one-stage models, long-tail methods from 2023-2026, or VLM/open-vocabulary SGG, which the paper itself cites as inheriting these metrics [24]. Panoptic scene graph (PSG) or other benchmarks with different label structure are not examined. For IETrans there is no matching baseline, so the 97% figure compares two separately trained models and "does not isolate the effect of relabelling."
**Evidence Anchor**: text: Sec. 7 Conclusion "On two released Neural-Motifs checkpoints on Visual Genome the gains are almost entirely group-level"
**Why it matters**: A CVPR reader will ask whether this is a property of debiasing methods in general or of two checkpoints. The generalisation sentences outrun the evidence. The method contribution is statistical, so its value to this venue depends on the SGG audit being broader than a single known case.
**Suggestion**: Either add at least a few audits of released checkpoints that ship baseline and debiased pairs, or retitle and reframe the paper as a method plus a case study of TDE. Reword the conclusion to checkpoint-level claims.
**Severity**: Major
**Confidence**: 4/5 (core area: SGG debiasing and evaluation)

### W2: Novelty of the SGG finding is limited and the decomposition's novelty is partly derivative
**Problem**: The paper states that prior correction rivals debiasing "is known [6, 42]". It also credits the covariance form to Yates [46] and notes the case-level term is a conditional permutation importance [38] or model reliance [14]. What remains new is the accounting for a gain between two frozen models, including thresholded metrics, plus paired inference. That is a genuine but incremental combination, and the paper does not argue why a CVPR audience should expect it to change practice, for example by showing that the split alters a method ranking or a conclusion in a published comparison.
**Evidence Anchor**: text: Sec. 5 "That a prior correction rivals debiasing is known [6, 42]; the split shows which part of TDE's gain it reproduces."
**Why it matters**: The headline claim that the logit adjustment matches TDE is the most memorable and the least new. The distinctive result is the exact split.
**Suggestion**: Reorder the contributions to lead with the decomposition and the cases where aggregates mislead (the Sec. 6 CLIP example). Add one case where the split would change a published method ranking.
**Severity**: Major
**Confidence**: 3/5 (novelty judgements from familiarity with the SGG debiasing literature, not a full prior-art search)

### W3: Headline conclusions depend on a single declared grouping and on protocol choices that move the sign
**Problem**: The split is conditional on the class-pair grouping. Dropping the object class takes the group-level share from 87% to 18%. The proper-score case-level part is +0.0045 under the primary protocol and −0.00006 under a temperature alone, and with one shared temperature −0.0184. The equivalence margin is set at one tenth of the geometry gain, and the comparison-weighted AUC is not equivalent. The paper discloses all of this, but the abstract and conclusion state the favourable readings (87%, "equivalent... within a margin fixed in advance") more prominently than the dependence.
**Evidence Anchor**: table: Table 1, TDE row, ∆AUCc +.0026 [−.0028, +.0086] versus ∆AUCr −.0015 [−.0036, +.0018]; absence: Abstract — expected the 18% alternative-grouping share and the comparison-weighted non-equivalence; checked Abstract and Sec. 1 contributions
**Why it matters**: A reader who stops after the abstract takes away a strong "TDE buys no discrimination" message that the evidence supports for one weighting and one grouping.
**Suggestion**: State in the abstract that the share is grouping- and protocol-conditional and name the weighting for which equivalence holds. Report the object-class-dropped share beside the headline.
**Severity**: Major
**Confidence**: 4/5

### W4: Presentation is too dense for the 8-page format and carries load-bearing evidence in the supplement
**Problem**: Sections 4-7 compress dozens of numbers, three or four protocols and several weightings into running prose. Many key claims cite appendices: Q.1, Q.2 and Q.4 for protocol sensitivity, Appendix O for evaluator replay, Appendix I for the omitted-covariate bound. The Q.1/Q.2/Q.4 appendices carry the evidence that the case-level part's sign survives protocol changes. Appendix I carries the shortcut-sensitivity bound behind the 0.061 correlation claim. Appendix J carries the small-cell coverage failure. The body reads as a statistics paper, and a CVPR reader scanning for what to do differently on a benchmark gets it only in the last paragraph. Figure 1 carries no image content in the text dump. Figure 3 packs many predicates into a small panel. Table 1 and Table 2 each mix three or four effect columns with unexplained abbreviations (r/c weightings).
**Evidence Anchor**: text: Sec. 5 "The audit covers 183,642 relations over 26,446 images in 7,127 cells; 98.9% fall in the 5,044 cells holding at least two."
**Why it matters**: The review burden is high and a reviewer may miss the caveats that sit in the appendices. The "What is not claimed" paragraph is helpful, but it too points to appendices.
**Suggestion**: Move one worked example and the operating-point control into a single figure. Cut secondary numbers (Sec. 6 seeds, Sec. 7 label shift path) to the supplement with one summary sentence each. Put the benchmark-reporting recommendation earlier.
**Severity**: Major
**Confidence**: 4/5

### W5: Breadth claim "Beyond scene graphs" is supplement-only
**Problem**: Sec. 6 says the estimator applies to long-tailed image and text classification and to Waterbirds, but these appear only in one paragraph with no numbers in the body. The paper uses the paragraph to support generality without evidence a reviewer can check from the 8 pages.
**Evidence Anchor**: text: Sec. 6 "the supplementary applies the estimator to long-tailed image classification (CIFAR-100-LT, across seeds and imbalance ratios)"
**Why it matters**: Either the generality is a contribution and needs body evidence, or it is a side remark and should be shortened.
**Suggestion**: Put one headline number per extra domain in the body, or drop the paragraph from the body.
**Severity**: Minor
**Confidence**: 4/5

### W6: Related-work coverage of recent SGG evaluation and a few typos
**Problem**: The SGG references stop at about 2023 for methods, with [24] (2024) as the latest. Recent mean-recall and zero-shot critiques and recent VLM-based SGG evaluation are not discussed. Text slips: Sec. 5 "(the baseline recalls no tail predicate and TDE one, to, at 0.016)" is garbled, Sec. 6 ends with "one..", and some references carry odd back-reference lists ([14] "3, 2", [38] "3, 2").
**Evidence Anchor**: text: Sec. 5 "the baseline recalls no tail predicate and TDE one, to, at 0.016"
**Why it matters**: Minor polish, but it gives the impression of an unfinished draft in a dense submission.
**Suggestion**: Update related work through 2026 SGG evaluation work and proofread the body.
**Severity**: Minor
**Confidence**: 4/5

## Detailed Comments

#### Journal Fit
Within CVPR scope: scene graph generation, evaluation methodology, and robustness of benchmark conclusions. A CVPR reader will see this as an evaluation-methodology paper. The statistical machinery (U-statistics, Hajek projection, cluster-robust intervals) is heavier than typical for the venue but legitimate. The paper is in the 8-page limit with references on pages 9-10. The supplement is 36 pages, which is long for a venue where reviewers are not required to read it. I found no anonymity breaches in the paper or supplement text (no repository URL, names or acknowledgements in either dump).

#### Originality
New combination: exact additive transport split for a paired gain, extended to mean recall and with paired inference. The SGG finding that a prior correction rivals TDE is known (W2). The CLIP counterexample is the freshest empirical contribution.

#### Significance
If it holds across methods, the result would change how SGG debiasing is reported and would matter well beyond TDE. On two checkpoints it is a careful case study with a useful tool attached (W1).

#### Structural Coherence
Title, abstract, introduction and conclusion are consistent. The title promises a general separation for SGG; the evidence is two checkpoints. The abstract compresses many results into one long paragraph (W3, W4).

#### Title & Abstract
The title is memorable and accurate about the question. The abstract carries about thirty numbers and is difficult to parse; it should state the grouping- and protocol-conditionality.

#### Conclusion
Reasonably hedged in places ("we audit no later method") but concludes with field-level reporting recommendations that the evidence base does not yet support.

## Questions for Authors
1. Are there released baseline-and-debiased checkpoint pairs for any post-2022 SGG method, or for a one-stage or VLM-based SGG model, on which the split could be run? If not, what is the minimal set that would convince you the finding is not specific to TDE and IETrans?
2. Under what conditions would the split change a published method ranking? One example would show that the tool has practical value beyond reproducing the known TDE-versus-prior-correction conclusion.
3. The abstract states TDE's ranking within pairs is equivalent to the baseline's. Would you restate this as holding for the relation-weighted AUC only, given the comparison-weighted result is a non-detection with an MDE of 0.008?
4. The class-pair grouping gives 87% and subject-class-only gives 18%. What principle, declared before the audit, selects the class pair, and could a benchmark owner apply it to a dataset with a different label structure such as PSG?

## Minor Issues
- Sec. 5 garbled phrase "TDE one, to, at 0.016".
- Sec. 6 sentence ends with "one.." (double period).
- Reference back-reference lists "3, 2" for [14] and [38] look wrong.
- Table 1 and 2 abbreviations (r, c, ng-mR, LA) should be defined in the captions.
- Figure 1 and Figure 3 are hard to read at print size.
