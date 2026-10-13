# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 Submission #***** (anonymous)
- **Review Date**: 2026-10-13
- **Review Round**: Round 1 (simulated panel, mode full; repository commit 2da86a9)

## Reviewer Information

### Reviewer Role
Journal-Fit Reviewer (internal role EIC), seat 1 of 5.

### Reviewer Identity
CVPR area chair for scene understanding and evaluation; has handled SGG method papers, SGG debiasing papers and benchmark-analysis papers.

### Review Focus
Fit with CVPR, originality, significance to the SGG and benchmark-evaluation community, structural coherence from claims to evidence, and whether the 8-page paper carries its own weight apart from the 38-page supplement. Methodological detail (estimator proofs, coverage) is left to the methodology seat.

Status lines: `NOT_CALIBRATED`. `criteria_binding_unavailable` (no #684 criteria authority was supplied, so no venue-alignment claim is made against a named criteria set; "fit" below is my own area-chair judgement of CVPR practice).

---

## Overall Assessment

### Recommendation
**Major Revision** (CVPR equivalent: borderline, leaning accept only if the framing and scope issues below are repaired; as written I would not champion it).

### Confidence Score
4 — high confidence on venue fit, SGG debiasing literature and evaluation practice; moderate on the finer statistical claims, which I did not re-derive.

### Calibration Status
`NOT_CALIBRATED`

### Recomputation log (read-only, from committed artefacts)

| Check | Paper claim | Recomputed | Result |
|---|---|---|---|
| `python experiments/verify_manuscript_numbers.py --driver cvpr2027/main.tex` | all manuscript numbers trace to results | "all 532 manuscript numbers trace to committed results; 247 printed in the paper" | OK |
| `results/sgg_recall_split.json`, gc@50 (graph-constrained, K=50) | mR@50 +0.0972 = +0.0841 group + +0.0130 case; 87% | total 0.09715, group 0.08411, case 0.01305; share 86.6% | matches |
| same file, official statistic | "official statistic moves +0.1017"; official mR 0.1459 -> 0.2476 | official_mR_none 0.14589, official_mR_TDE 0.24763; difference 0.1017 | matches |
| same file, K=20 and K=100 shares | 77% at K=20, 86% at K=100 | 0.0462/0.0598 = 77.3%; 0.1099/0.1280 = 85.8% | matches |
| same file, no graph constraint (ng@50) | TDE mean recall falls (0.3260 to 0.2981) | official ng@50: 0.32605 to 0.29807; micro total -0.0337, group -0.0464, case +0.0127 | matches |
| control cost | LA control costs 0.0175 R@50 vs TDE 0.2023 ("under a tenth") | 0.0175/0.2023 = 8.7% (R@50 values as printed in Sec. 5) | consistent |
| body-tier split | body +0.1224, group +0.1082; head -0.0255; tail +0.0003 | mean_recall_body total 0.12242, group 0.10819; head -0.02553; tail 0.00026 | matches |

I found no numerical discrepancy. My concerns are about scope, framing and presentation, not arithmetic. I did not re-run the checkpoints or the estimator.

### Summary Assessment
The paper proposes an exact, model-free split of the score difference between two frozen predictors into a group-level part (survives within-group label transport) and a case-level covariance (the paired-gain form of Yates's decomposition), extends it to mean recall via counterfactual-label hit indicators, and adds image-clustered inference, an operating-point control and a within-cell AUC. It validates the split in simulation and on controlled VG150 predictors, then audits released Neural-Motifs checkpoints: for TDE, 87% of the mR@50 gain is group-level and a training-prior logit adjustment recovers +0.0941 of +0.0972; DLFE and IETrans are 94% and 97% group-level.

This is a careful, unusually transparent evaluation paper with a clean central idea (Fig. 1) and a real finding about the most-cited debiasing method. The numbers reproduce. For CVPR the weaknesses are about reach and framing: the empirical audit covers three 2020-2022 checkpoints of one architecture family, the headline findings are specific to K=50 with the graph constraint and to the declared grouping, the interpretive stance is ambiguous, and the 8-page paper leans on a 38-page supplement and is hard to read. These are repairable, mostly without new science, but they bear on whether the paper delivers what its title and abstract promise.

---

## Strengths

### S1: A crisp, falsifiable question with an exact accounting answer
The idea of scoring each prediction against another relation's label from the same subject-object pair, so that group-level gain survives and case-level gain does not, is explained in one figure and one identity, and answers a question the field has circled (what did mean recall reward?) without a fitted reference model.
**Evidence Anchor**: figure: Figure 1 and Theorem 1 (Eq. 2-3), Sec. 3 — "split their score gain exactly"

### S2: Validation where ground truth is known, including honest negative controls
The paper tests the split in simulation and on controlled predictors where the answer is algebraically known (class-pair-only MLP gives case-level exactly 0.00000), shows that an unrecorded shortcut is credited to the case-level part, and shows that raw outputs produce a spurious -0.488 under pure recalibration that the matching protocol removes. It states what the split does not measure.
**Evidence Anchor**: text: Sec. 4 "the split measures all within-cell signal relative to the declared grouping, shortcut or not"

### S3: The central empirical result is checked against a matched, training-free control
Reproducing TDE's gain, tier profile and per-predicate behaviour with a one-line prior subtraction that changes no within-cell ranking is a concrete, reviewer-checkable finding, and Table 1 / Fig. 3 show the mechanism predicate by predicate (parked on, on).
**Evidence Anchor**: table: Table 1, rows TDE and LA — case-level +.0130 vs +.0139; TDE−LA case −.0008 [−.0050,+.0033]

### S4: Unusually candid scope statements and reproducibility
The paper states the K=50 specificity of the control match, that IETrans is compared with a separately trained baseline, that intervals cover test sampling not training variance, and that the split is of the micro-averaged recall. Every manuscript number traces to a committed result file (recomputation log above).
**Evidence Anchor**: text: Sec. 5 "The control's match of TDE's gain is specific to K = 50 under the constraint"

### S5: Constructive, practical reporting recommendation
The closing proposal (declare grouping, report both parts with intervals, within-group AUC, operating-point control) is actionable and notes that archived top-k logits suffice for AUC and control.
**Evidence Anchor**: text: Sec. 7 "archived top-k logits suffice for the AUC and the control, not for the exact split"

---

## Weaknesses (ranked by decision impact)

### W1: The empirical audit is too narrow for the scope the title, abstract and conclusion imply
**Problem**: The "audit of debiasing" is three released Neural-Motifs-family checkpoints (TDE 2020, DLFE 2021, IETrans 2022), one run each, PredCls only for DLFE and IETrans, with the statement "we audit no later method." No CVPR-era SGG model (DETR/one-stage, VLM or open-vocabulary SGG, 2023-2026) is split, and SGCls/SGDet are a TDE-only replication. The title and abstract generalise to "Debiasing methods for scene graph generation" and "Scene Graph Generation", and the abstract's first sentence frames the field's practice. The DLFE and IETrans numbers (11 and 21 points, 94% and 97%) appear in the abstract as findings about those methods although DLFE's is a single-checkpoint pair and IETrans is, by the authors' own words, a comparison of two separately trained models that "does not isolate the effect of relabelling".
**Evidence Anchor**: text: Sec. 7 "we audit no later method"; Sec. 5 "this compares two separately trained models and does not isolate the effect of relabelling"
**Why it matters**: A CVPR reader in 2027 will ask whether the group-level finding is a property of the 2020-2022 logit-adjustment family (where a prior shift is expected to reproduce the gain, a point the paper itself calls "known [6, 43]") or of SGG debiasing broadly. The paper cannot currently distinguish these.
**Suggestion**: Either (a) narrow the title/abstract to "logit-adjustment-type and resampling debiasing of Neural Motifs", or (b) add at least two methods trained differently (for example one recent one-stage or VLM-based SGG model whose scores can be cached, and one training-based method with its own released baseline). Move IETrans out of the abstract's headline numbers or flag the confound there. A discussion of which method families the split predicts to be group-level (prior-shift) versus case-level (new features) would give readers a use for it.
**Severity**: Major
**Confidence**: 4 — core expertise: SGG debiasing literature and benchmark practice

### W2: The headline numbers hold under one protocol and the abstract does not say so
**Problem**: The 87% share and the "+0.094 of +0.097" control match are for graph-constrained micro-pooled mR@50. The paper's own Sec. 5 and Table 2 show that the match is "specific to K = 50 under the constraint": the control trails TDE by 0.0234 at K=20, is 0.0300 behind at K=100, and trails by 0.08-0.15 without the constraint, where TDE's mean recall actually falls (ng-mR@50 -0.0337) and its case-level part against the control is +0.0148 [+0.0064, +0.0232] at K=100. The abstract states the K=50 conditions for the share but presents the control result ("recovers +0.094 of its +0.097 at under a tenth of TDE's cost in recall") without the K/constraint caveat; its parenthetical caveat sits only in the introduction. The split also analyses the micro-pooled recall, not the official per-image average (the official statistic moves +0.1017; the per-image split is 84% group-level).
**Evidence Anchor**: table: Table 2 — ng-mR@100 TDE vs LA case-level +.0148 [+.0064,+.0232]; mR@20 ∆mR TDE vs LA −.0234
**Why it matters**: The title question ("what did ten points buy?") is answered for one operating point of one evaluation protocol; on the other five protocols the answer differs, and the abstract's strongest sentence is the one least robust to protocol.
**Suggestion**: Put the protocol dependence into the abstract in one clause (K=50, graph-constrained, micro-pooled; control match does not hold at other K or without the constraint). Report the per-image official statistic's split alongside Table 1 in the main text since that is what the community's leaderboards report. Consider reframing the claim as "at the community's standard operating point".
**Severity**: Major
**Confidence**: 4 — evaluation-protocol expertise; numbers verified in results/sgg_recall_split.json

### W3: The conclusion's normative message is ambiguous
**Problem**: The title and introduction invite the reading that group-level gain is a deflated or lesser gain ("what did those ten points buy?"), yet Sec. 5 states "Group-level is not a lesser gain (mean recall rewards moving rare predicates within a pair by design)", and Sec. 6 shows that case-level part and ranking can disagree (CLIP model has more case-level covariance but worse top-1 accuracy and within-cell AUC). The split is conditional on a declared grouping, credits shortcuts, is not invariant to recalibration, and is described as "a modelling decision the benchmark should make". The paper never says what a practitioner should conclude about TDE, or what a reviewer of a new debiasing paper should do on seeing a high group-level share. The recommended reporting list has six items.
**Evidence Anchor**: text: Sec. 5 "Group-level is not a lesser gain"; Sec. 7 "declaring ϕ is a modelling decision the benchmark should make"
**Why it matters**: A benchmark-analysis paper earns CVPR significance by changing how people evaluate. If the claim is "mean recall confounds two things", the paper should say which one downstream users care about and why, or the evaluation proposal reads as a decomposition without a decision rule.
**Suggestion**: Add a short, explicit "how to read the split" paragraph in Sec. 7: which downstream uses want group-level gain (calibrated predicate selection in fixed pair contexts) and which want case-level gain (image-grounded relation decisions). Reduce the reporting recommendation to a minimal two- or three-item protocol with a worked example, and say what outcome would change a method's ranking.
**Severity**: Major
**Confidence**: 4 — area-chair judgement on evaluation-paper significance

### W4: Result sensitivity to the declared grouping is large and under-weighted for a paper whose headline is a share
**Problem**: The share is 87-90% with the class-pair cells (or refinements by position/size) but 18% when cells are the subject class alone, and "two equally fine partitions of the same cases can disagree" (Sec. 7). In SGCls only 58% of relations have a matched pair and in SGDet the grouping depends on object detections. The paper presents the pair as the natural benchmark-defended grouping but gives no argument beyond "the finest grouping the benchmark's construction defends" for why the community should accept it for the headline.
**Evidence Anchor**: text: Sec. 5 "with the subject class alone 18%"; Sec. 7 "dropping the object class takes it to 18%"
**Why it matters**: A reader can accept the 87% only conditional on the grouping; the paper's own range (18% to 90%) is wider than the effect being reported, and the headline sentence does not carry the range.
**Suggestion**: Move the grouping-sensitivity result (Appendix K) into the main text as a small table or panel next to Table 1, and state the share as a function of the grouping in the abstract or the first claim in Sec. 5.
**Severity**: Major
**Confidence**: 3 — adjacent field: statistical conditioning argument, judged from a venue-fit standpoint

### W5: The 8-page paper is dense to the point of impeding its readership, and key evidence lives in the supplement
**Problem**: The introduction runs to roughly 70 numeric claims before the method is defined; the abstract is a single block of about 20 figures, thresholds and intervals. Sec. 3 packs setup, transport, theorem, estimator, inference, confidence-matching, mean-recall splitting and AUC weightings into two columns; notation switches between ΔP, ∆Pc, ∆P-hat, and between "case-level" and "covariance". The six-protocol Table 2 is the evidence for the central robustness claim yet sits in the main text with a clipped right-hand panel (see W6). Proofs, the SGDet/SGCls replication (Appendix Q.6, Tables 35-36), the grouping sensitivity (Appendix K), cross-seed stability (P) and every alternative protocol (Tab. 27) are supplementary. The paper repeatedly defers "Appendices O and Q report every configuration".
**Evidence Anchor**: text: Sec. 1 "Appendices O and Q report every configuration"; absence: main paper — expected a single table of the primary quantities with their protocol labels; checked Sec. 5, Table 1, Table 2
**Why it matters**: CVPR reviewers read the 8 pages; a reader who cannot find the claim, protocol and caveat in one place cannot verify the paper's conclusions within the review window, and a result that depends on 38 pages of supplement is exposed to the "supplement as a second paper" objection.
**Suggestion**: Cut the abstract to the three headline findings with one protocol statement; move the intro's number list into Table 1. Add a one-paragraph "protocol card" (grouping, score, matching, K, constraint) before Sec. 5 and tag every number with it. Move Sec. 4's simulation details to the supplement and use the space for the SGCls/SGDet result and the grouping-sensitivity panel.
**Severity**: Major
**Confidence**: 4 — core expertise: CVPR review load and readership

### W6: Table 2 is clipped and has overlapping text in the submitted PDF
**Problem**: In the page-7 rendering of the paper PDF, Table 2's right-hand block (TDE vs LA) runs past the column edge, and the case-level confidence intervals are truncated and overprinted with the literal artefact "iny" (for example "+.0135 iny[+.0101,+.0170]"). The "TDE vs LA" intervals are cut off at the margin ("[−.0024,+.0"). This is the table supporting the "six recall protocols" claim.
**Evidence Anchor**: table: Table 2 (page 7) — rows mR@20 to ng-mR@100, right panel "TDE vs LA" intervals cut off; "iny[" overprint in the CI column
**Why it matters**: Intervals needed to check the TDE-vs-control claim (e.g. K=100 +0.0148, [+0.0064, +0.0232], quoted only in text) are unreadable in the table; it also signals an unfinished layout.
**Suggestion**: Rebuild Table 2 within the column width (drop the ∆mR column for the LA block or use two stacked panels), remove the stray markup, and recompile; check every table against the page frame.
**Severity**: Minor
**Confidence**: 5 — direct inspection of the rendered PDF

### W7: Positioning relative to the SGG debiasing and evaluation literature is thin where it matters most to this audience
**Problem**: Related work cites TDE, DLFE, IETrans, [25] (metric pathologies), [23] (bipartite graph network), but treats the prior-correction result as "known to rival them [6, 43]" without quantifying how much of the present TDE finding is new beyond that. The paper discusses statistical decompositions (Yates, Murphy, DeLong, Diebold-Mariano) in depth and SGG evaluation critiques in a few lines; there is no comparison to existing SGG diagnostic protocols (zero-shot recall, per-predicate and head/body/tail breakdowns are mentioned in a clause), and no demonstration that the split changes the ranking of any existing methods in a way those diagnostics do not. The abstract's claim that "none attributes the gain between two models to one route or the other" is carried by the introduction only.
**Evidence Anchor**: text: Sec. 1 "none attributes the gain between two models to one route or the other"; absence: Sec. 2 and Sec. 5 — expected a direct comparison against head/body/tail or zero-shot recall on the same checkpoints; checked Sec. 2, Sec. 5, Table 1, Fig. 3
**Why it matters**: For an evaluation-paper contribution the question is what the new tool shows that the existing tools do not. Fig. 3 (per-predicate view) and the tier profile partly answer this, but no explicit side-by-side is given.
**Suggestion**: Add a half-page comparison on TDE and LA: what head/body/tail and zero-shot recall say, what the split adds. State clearly the novelty relative to [6, 43] that a prior-shift rivals TDE.
**Severity**: Major
**Confidence**: 4 — core expertise: SGG evaluation literature

### W8: Single-run checkpoints and a reconstructed split limit how far the controlled study transfers
**Problem**: Each released model is one training run; intervals cover test sampling only (stated in Sec. 7). The controlled predictors and CLIP study use a VG150-style split reconstructed from annotations (70/30), trained on a 100,000-relation subsample, with a frozen CLIP ViT-B/32 head, not a scene-graph system; the paper says so ("not an SGG system"). The CLIP result (more case-level covariance, worse overall) is used as a headline illustration of the converse, but it compares pipelines that read different inputs.
**Evidence Anchor**: text: Sec. 1 "a controlled illustration on real pixels, not an SGG system"; Sec. 7 "the intervals cover test sampling, not training variability"
**Why it matters**: This is acknowledged, so it is not hidden, but the abstract does not mention the CLIP study and the introduction advances it as the "converse", leaving the main-text reader to weigh a non-SGG toy against the audited checkpoints.
**Suggestion**: Label the controlled studies as validation, not evidence about SGG methods, in the contributions list; if compute allows, retrain TDE and its baseline for 3 seeds to bound training variance on the group/case share.
**Severity**: Minor
**Confidence**: 3 — adjacent field: training-variance expectations differ between venues

---

## Coverage Receipt
Not required: both the Strengths and Weaknesses lists are populated.

---

## Detailed Comments

### Journal Fit
CVPR 2027 welcomes evaluation and benchmark-analysis work, and SGG debiasing is a recurring CVPR topic, so the scope is in. The paper reads, however, closer to a statistics-and-evaluation contribution (an exact decomposition, U-statistic inference, coverage simulation) than to a vision contribution; the vision content is the TDE/DLFE/IETrans audit and the CLIP-crop illustration. That is acceptable at CVPR if the audit result is general enough to change how SGG results are read (W1, W3), and the paper should not rely on the supplementary statistical material to make the case. Length: 8 pages plus references meets the format; the 38-page supplement is large and carries claims the main text leans on (W5). Anonymity looks intact. A statistics or evaluation venue (a journal or an ICLR/NeurIPS datasets-and-benchmarks track) would be a natural alternative; for CVPR the vision relevance must be argued.

### Originality
The decomposition is a paired-gain form of Yates's covariance decomposition, and the paper says so (Sec. 2-3); the novelty is the within-group label-transport device applied to the difference between two models, extension to thresholded metrics such as mean recall, an operating-point control, and clustered inference. I know of no SGG paper that splits a mean-recall gain this way. The finding that a prior-shift reproduces TDE's headline is partly anticipated ([6, 43] and the logit-adjustment literature), as the paper acknowledges; what is new is the exact accounting and the cell-level mechanism.

### Significance
Potentially high for the debiasing-evaluation sub-community: it questions what mean recall measures and offers a reproducible way to check. Limited by the narrow set of methods (W1), protocol specificity (W2) and the lack of a decision rule (W3). If the next generation of SGG models also shows high group-level shares, the paper will become a reference; if not, it is a careful case study of 2020-2022 methods.

### Structural Coherence
The title question, the abstract, Sec. 5 and the conclusion line up on TDE. Over-promising shows in two places: the abstract's generalising first sentence and the "controls" framing compared with the K=50 specificity, and the CLIP "converse" which is outside SGG. Sec. 6-7 (CLIP, label shift, other domains) dilute the narrative; the paper has two papers in it (the decomposition and the SGG audit), and the 8-page limit forces compression of both.

### Title & Abstract
The title is a good question but slightly long and the subtitle commits to "Scene Graph Generation" generally. The abstract is a dense list of numbers and intervals, hard to parse, and carries the protocol-specific headline without its condition (W2, W5).

### Conclusion
Consistent with the evidence for TDE; "the gains are almost entirely group-level" over three checkpoints is correct as stated for these (with IETrans's confound flagged in parentheses). It ends with a reporting recommendation but no verdict on what the findings mean for the field's practice (W3).

---

## Questions for Authors

1. Under which protocol (K, graph constraint, micro versus per-image average) do you want a reader to treat the "87% group-level" figure as the community's reference number, given that the control match fails at K=20, K=100 and without the constraint? Would you put that in the abstract?
2. Have you applied the split to any SGG model released after 2022 (one-stage, VLM-based or open-vocabulary) for which top-k logits or full scores can be cached? What do you expect to see, and does your framework predict which methods should show a higher case-level share?
3. For a benchmark designer, what is the decision rule: if a new method's gain is 90% group-level, is it to be discounted, reported differently, or ranked separately? Please state the claim that a reviewer should be able to make from the split.
4. The share moves from about 90% to 18% as the grouping coarsens. Why is the object-pair cell the right headline grouping for scene graphs, and would a leaderboard that fixed it in advance change the comparison of any existing methods?
5. Can the DLFE and IETrans results be tied to a training-based method with its own released baseline, so the abstract's "21 points, 97% group-level" is not a comparison of separately trained models?

---

## Minor Issues

### Language / Grammar
- Abstract and Sec. 1 pack many parenthetical intervals into single sentences; split them (Abstract, lines 015-026).
- Notation drift between ∆P, ∆Pc and the hatted versions, and "case-level" versus "covariance", in Sec. 1 and Sec. 3.

### Citation Format
- Reference [14] and [39] list page "3, 2" in the back-reference field, probably a supplement page; check that back-references are consistent with the final pagination.
- [21] (Newsweeder) and [17] (ResNet) are cited only from the supplement pages; fine, but confirm that the main paper's reference list is meant to include them.

### Figures and Tables
- Table 2 right panel clipped and overprinted (W6).
- Fig. 2(b) caption relies on marker conventions ("square", "triangle") that are hard to follow at print size; add a legend in the panel.
- Fig. 3 lists 20 predicates with a diamond for the LA total; consider a smaller set (the top 8 movers) with the rest in the supplement.

### Layout
- The review-copy line numbers run through the margin text; ensure the final camera-ready template is applied consistently.
