# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 Submission #***** (anonymous); repository commit 9dad949
- **Review Date**: 2026-10-10
- **Review Round**: Round 1 (simulated panel, mode full)

## Reviewer Information

### Reviewer Role
Journal-Fit Reviewer (internal role EIC), configured as CVPR area chair for scene understanding and evaluation.

### Reviewer Identity
Area chair who has handled SGG method papers, SGG debiasing papers and benchmark-analysis papers.

### Review Focus
Bird's-eye assessment: does an exact-decomposition audit of two SGG debiasing checkpoints belong at CVPR, would the SGG and evaluation community care, how original is it relative to known results, and is the paper's scope and presentation proportionate to its claims. Methodological detail belongs to Reviewer 1 and is not scored here.

### Calibration Status
`NOT_CALIBRATED`

`criteria_binding_unavailable`

No author-confirmed target context was supplied. My CVPR remarks are a configured perspective, not a venue-alignment determination. I make no claim that the paper meets or fails any CVPR 2027 criterion as published.

---

## Overall Assessment

### Recommendation
**Major Revision** (CVPR-simulated reading: borderline, leaning toward acceptance if breadth and framing are repaired; Reject is not warranted on the evidence I examined).

### Confidence Score
4: within my area on SGG evaluation and debiasing; the proper-score and U-statistic theory is outside my remit and I did not verify the proofs.

### Summary Assessment
The paper asks what the roughly ten-point mean-recall gain of TDE on Visual Genome actually buys. It introduces an exact, model-free split of the gain between two frozen models into a group-level part and a case-level covariance, where a group is the ordered subject-object class pair. It applies the split to released TDE and IETrans checkpoints and reports that 87% (TDE) and 97% (IETrans) of the mean-recall gain is group-level. A ranking-preserving logit adjustment recovers nine of the ten points at under a tenth of TDE's R@50 cost, and within-pair AUC detects no change for TDE and a loss for IETrans.

This is the kind of benchmark-analysis paper the scene-graph community needs: it turns a long-standing suspicion (debiasing equals prior shifting) into a quantified, interval-bearing statement on released checkpoints. The numbers I recomputed trace to committed results (423 of 423). Weaknesses are in scope and proportion. The empirical audit covers exactly two methods that share the MOTIFS family, on one dataset and chiefly in PredCls. One headline claim about IETrans is stronger than its own table supports and rests on a non-isolating comparison. Much of the load-bearing evidence sits in a 36-page supplement. The main text is very dense for a CVPR reader. My recommendation is Major Revision because the contribution is real but the evidence base is narrower than the title and conclusion's benchmark-wide recommendations imply.

---

## Recomputation Log (what I ran, read-only)

1. `python experiments/verify_manuscript_numbers.py --driver cvpr2027/main.tex`: result "all 423 manuscript numbers trace to committed results; 211 printed in the paper, rest in supplement". All visible lines OK. This checks that printed numbers equal results-file values, not that the analysis is correct.
2. `results/sgg_share_intervals.json`: TDE total 0.09715, group 0.08411, share 0.8657, CI [0.8256, 0.9058]; LA share 0.852; IETrans share 0.9727, CI [0.9017, 1.0436]. Matches abstract (87%, 83-91%; 97%). Note the IETrans interval upper bound exceeds 100%.
3. `results/sgg_recall_split.json` (gc@50): official mR@50 TDE 0.2476, baseline 0.1459; case part 0.01305, CI [0.0093, 0.0168]; micro-averaged mR gain 0.0972 vs official per-image gain 0.1017, matching Sec. 5 text. TDE head-tier total -0.0255 matches. Pooled micro R@50 drop for TDE is 0.2195 (micro) while the paper's 0.2023 is the official-evaluator figure (0.6612 to 0.4588); consistent, but two R@50 conventions coexist.
4. `results/sgg_auc_tde_la.json`: TDE vs LA within-cell AUC difference +0.00255, CI [-0.0029, +0.0086] (comparison weighting) and -0.00183, CI [-0.0039, +0.0014] (relation weighting). Matches Table 1 (+.0026 / -.0015 for TDE vs baseline are from a different file; the TDE-vs-LA row is what I checked). The audit-half difference changes sign (-0.0010), which is consistent with "no change detected" but also shows the sign is unstable.
5. Table 1 internal check: IETrans AUC_c CI [-.0181, +.0004] and case-level mR CI [-.0031, +.0151] both include zero; only AUC_r [-.0275, -.0182] excludes zero. This is relevant to W2.
6. Skimmed `supp_text.txt` contents list and Appendix O/Q headings; did not re-derive proofs or re-run model inference (no cached full-score archives re-evaluated).

---

## Strengths

### S1: Question and framing of direct interest to the SGG community
The paper targets the dominant debiasing yardstick (mean recall) and a flagship method (TDE), and gives a quantitative answer instead of another stratified metric. For a venue whose SGG audience has repeatedly argued about frequency-prior exploitation, this is timely and useful.
**Evidence Anchor**: text: Sec. 1 "What did those ten points buy?" and "none attributes the gain between two models to one route or the other."

### S2: Exact, additive accounting with an operating-point control
The split is exact in-sample (Theorem 1), extends to thresholded metrics including mean recall, and the authors pair it with a control (logit adjustment that cannot change within-cell ranking) so that a nonzero case-level part of a thresholded metric is not misread as new discrimination. This control is the most transferable idea in the paper and the Sec. 5 result against it (TDE case-level -0.0008, CI straddling zero) is a clean, falsifiable finding.
**Evidence Anchor**: table: Table 1 rows TDE and TDE-LA, case column +.0130 versus -.0008

### S3: Validation on cases where the answer is known, and unusual honesty about limits
Sec. 4 uses simulation, algebraic zeros and controlled predictors; "What is not claimed" and Sec. 7 state conditionality on the grouping, non-invariance to calibration, and the two-case-cell under-coverage (81.5%). Negative and sign-unstable results (TDE's case-level part across protocols) are reported rather than hidden.
**Evidence Anchor**: text: Sec. 7 "It is not invariant to recalibration, to the operating point or to the label mix"

### S4: Reproducibility artifacts
All printed numbers trace to committed results via a checker I could run, and the evaluator replay reproduces official numbers to the fourth decimal (0.6612, 0.1459, 0.4588, 0.2476). This is stronger than the norm at CVPR.
**Evidence Anchor**: dataset: results/*.json with experiments/verify_manuscript_numbers.py (423 of 423 traced); text: Sec. 5 "The replay reproduces the official numbers to the fourth decimal"

### S5: Practical reporting recommendation
The concluding recommendation (declared grouping, signed parts, within-group AUC under both weightings, operating-point control) is concrete enough for a benchmark maintainer to adopt in part.
**Evidence Anchor**: text: Sec. 7 Conclusion "We suggest that benchmarks whose labels lean on a feature every model sees report, beside the headline metric"

---

## Weaknesses (ranked by decision impact)

### W1: Empirical scope is two MOTIFS-family checkpoints on one dataset, yet conclusions are framed for the field and for benchmarks
**Problem**: The "audits of two released debiasing checkpoints" cover TDE (MOTIFS-SUM, PredCls main; SGCls/SGDet in one paragraph) and IETrans+Rwt (Neural Motifs). No transformer/DETR-style, one-stage, or post-2022 debiasing methods, no VG-based SGG benchmark beyond VG150, and no panoptic SGG or open-vocabulary SGG evaluation is audited, although related work cites open-vocabulary SGG [24]. The title and conclusion ("the field's metrics report the sum"; recommendations to benchmarks) generalise from n = 2. The mechanism offered for TDE ("to first order a learned logit adjustment of the context branch") is specific to SUM-fusion MOTIFS, so it cannot be assumed for other debiasing families. The paper's own limitation that most benchmarks archive only top-k predictions means that broader audits are hard, but the authors already re-ran two checkpoints and could re-run others whose code is public.
**Evidence Anchor**: text: Contributions "(i) Audits of two released debiasing checkpoints that split their mean-recall gains exactly"; absence: Sec. 5 and Sec. 6 — expected audit of any non-MOTIFS-family or post-2022 debiasing method; checked paper Secs. 1, 5, 6, 7 and supplement table of contents
**Why it matters**: A CVPR reader will ask whether "group-level" is a property of debiasing in general or of two MOTIFS-style, prior-indexed models. The strongest version of the paper would show a method that is not a prior shift (the finding would then have discriminative power), which the current evidence cannot.
**Suggestion**: Add at least two more released methods from different families (e.g., a class-balanced or hierarchical-loss method and a recent transformer-based or PSG debiasing method), reporting the same split, control and AUC. If checkpoints cannot be obtained, rewrite the title and conclusion to scope the claim to "two released MOTIFS-family checkpoints" and move recommendations to a labelled position statement.
**Severity**: Major
**Confidence**: 4: SGG breadth and expectations are core to my remit

### W2: IETrans claim in abstract and conclusion is stronger than Table 1 supports and rests on a non-isolating comparison
**Problem**: The abstract says IETrans "loses within-pair discrimination under every measure". Table 1 shows its case-level mean-recall part (+.0060, CI [-.0031, +.0151]) and its AUC_c change (-.0093, CI [-.0181, +.0004]) both include zero; only AUC_r excludes zero. The comparison is between IETrans+Rwt (relabelling plus reweighting plus a test-time log-prior) and a separately trained baseline that differs in the fusion of the visual term; Sec. 5 concedes that it "does not isolate the effect of relabelling". The "97%" share has a CI of [0.90, 1.04], above 100%.
**Evidence Anchor**: table: Table 1 row IETrans, columns case [CI] and ∆AUCc; text: Sec. 5 "this compares two separately trained models and does not isolate the effect of relabelling"
**Why it matters**: One of two headline audits carries an overstated sentence in the abstract, and the caveat appears only in Sec. 5, so a skim reader leaves with a stronger conclusion than the data warrant.
**Suggestion**: Qualify the abstract ("loses within-pair discrimination on the relation-weighted AUC and the matched proper-score parts"); state the baseline mismatch in the abstract or Sec. 1; if feasible, train IETrans-style relabelling from the same baseline code to isolate it; cap the share interval at 100% or explain it.
**Severity**: Major
**Confidence**: 4: read the table and text against each other directly

### W3: The central TDE "no change in ranking" conclusion is an absence of detection under a protocol-dependent split
**Problem**: The paper says TDE's case-level part "changes sign with the calibration protocol and the label mix" (-0.0184 to +0.0440 across protocols; -0.00006 to +0.0143 across label mixes) and that the AUC separates TDE from the baseline at neither end. The conclusion therefore rests on non-significant AUC differences with CIs spanning roughly +/-0.006-0.009, i.e., a lack of power to detect small changes rather than evidence of none. The abstract wording ("No measure detects...") is accurate but the Sec. 5 heading "What that licenses" and conclusion ("leaves within-group ranking unchanged as far as we can detect") invite a stronger reading. Equivalence testing or a stated minimal detectable AUC change would show what "unchanged" means.
**Evidence Anchor**: table: Table 1 TDE row ∆AUCc +.0026 [-.0028, +.0086] and ∆AUCr -.0015 [-.0036, +.0018]; text: Sec. 5 "The sign of TDE's case-level part depends on the protocol."
**Why it matters**: Venue readers will quote the "87% group-level" figure; the case-level reading, the part that matters for the claim "debiasing buys no discrimination", is the weakest-evidence half.
**Suggestion**: Report a minimal detectable effect or an equivalence (TOST) margin for AUC and the case-level part; present the group-level share as the robust finding and the case-level conclusion as bounded; add a one-sentence summary of the protocol spread to the abstract.
**Severity**: Major
**Confidence**: 3: inference/statistical power is adjacent to my remit

### W4: Contribution is partly known and the novelty claim over prior-correction work is under-positioned relative to recent SGG evaluation literature
**Problem**: That a logit-adjusted prior correction rivals SGG debiasing is acknowledged as known (DLFE [6], Structured Sparse R-CNN [42], Menon et al. [28]). The new element is the exact decomposition. The decomposition descends from Yates and from permutation-importance ideas ([46], [14], [38]) and the paper concedes "What the split adds is the exact additive accounting of a paired gain". Related work on SGG evaluation cites mostly 2019-2022 debiasing and metric papers and no post-2022 SGG evaluation, zero-shot or panoptic-SGG metric work. From my own recall (not verified) there is recent work on SGG metrics and open-vocabulary/PSG settings that should be contrasted. As a result, the CVPR-specific novelty (a new vision-evaluation insight versus a repackaged statistical tool) is not argued.
**Evidence Anchor**: text: Sec. 2 "What the split adds is the exact additive accounting of a paired gain, including thresholded metrics, and paired inference for it."; absence: Sec. 2 related work — expected comparison to post-2022 SGG/PSG evaluation and debiasing literature; checked Sec. 2 and reference list [1]-[52]
**Why it matters**: A CVPR area chair weighs originality against what the community learns that it did not know; the finding on TDE is new on released checkpoints, but the field-level insight is partly folklore.
**Suggestion**: Add a short paragraph stating what the SGG community can now do that it could not (e.g., which published mR gains survive the control) and update related work to 2023-2026 SGG evaluation and debiasing papers.
**Severity**: Major
**Confidence**: 3: literature recall is from memory and unverified

### W5: Presentation load: key evidence lives in appendices and the 8-page main text is very dense
**Problem**: Core protocols (confidence matching, evaluator replay, operating-point control, tier profiles, label-shift path, calibration alternatives) are in Appendices O, Q, N and are cited by letter. The main text carries two dozen numerical claims per page, a four-part "What is not claimed" paragraph in the introduction, and a Sec. 3 that combines theory, estimator, inference and mean-recall extension in under two pages. Figure 1 is explained in a long caption rather than visually. The "Beyond scene graphs" paragraph (CIFAR-100-LT, text, Waterbirds) appears only in one paragraph with no figure or table in the main text, which is neither SGG evidence nor sufficiently developed to count as breadth.
**Evidence Anchor**: text: Sec. 6 "Beyond scene graphs. Nothing in Sec. 3 is specific to relations; the supplementary applies the estimator to long-tailed image classification"; figure: Figure 1 caption
**Why it matters**: CVPR reviewers read the main paper first; a dense text invites misreading of the protocol-dependence results, and the other-domain claim is unsupported where reviewers will look.
**Suggestion**: Move the CLIP controlled study or the label-shift path to the supplement and use the space for a worked SGG example in plain terms and a main-text table of the control against TDE and LA; either give the beyond-SGG results a small main-text table or remove the paragraph.
**Severity**: Minor
**Confidence**: 4: standard venue-readability judgement

### W6: Practicality: the method needs full-score outputs that most benchmarks do not archive
**Problem**: The authors say the split needs scores for every label and that "recovering the rest took a rerun of the released checkpoint". Hence the proposed leaderboard additions (both matching protocols, two AUC weightings, label-mix path, operating-point control) cannot be applied to most existing submissions, and the paper's own audits needed re-execution and evaluator patching. The adoptability claim in the conclusion is therefore aspirational. Compute is described as O(NK), but the full protocol requires held-out calibration fits and 20 halves.
**Evidence Anchor**: text: Sec. 7 "most benchmarks archive only ranked top-k predictions, and recovering the rest took a rerun of the released checkpoint"
**Why it matters**: The practical impact for the benchmark community depends on a submission format change that the paper does not specify.
**Suggestion**: Provide a minimal reporting protocol (what to archive, file format, a one-script tool) and a reduced "lite" report that needs only top-k outputs, or state clearly that the recommendations apply to future submissions.
**Severity**: Minor
**Confidence**: 4: benchmark-organiser perspective

---

## Coverage Receipt (Strengths and Weaknesses both populated; no receipt required)

Not applicable: both lists are non-empty.

---

## Detailed Comments

### Title & Abstract
- The title poses a question and states the topic; it is memorable and accurate for the TDE finding but under-specifies the scope (two checkpoints). The abstract is dense, with about fifteen numeric claims and nested qualifiers; the IETrans sentence overreaches (W2). Consider dropping some numbers and naming the grouping explicitly in the first lines.

### Introduction
- Motivation (predicate lookup is competitive; mean recall credits prior shifting) is persuasive for the SGG audience. The "What is not claimed" paragraph is honest but front-loads limitations before the findings are digested; consider moving it after the results.

### Literature Review / Theoretical Framework
- Strong statistical lineage (Yates, DeLong, Diebold-Mariano, Hájek); thin on recent SGG evaluation (W4).

### Methodology / Research Design
- Not scored here (Reviewer 1). Fit note: the operating-point control and the validation hierarchy (simulation, algebraic zero, controlled predictors, released checkpoints) are well matched to a benchmark-analysis paper.

### Results / Findings
- Results for TDE are consistent across PredCls, SGCls, SGDet. The CLIP-crops study (Sec. 6) is a clever demonstration that aggregates and case-level covariance disagree, but it is a trained-on-100k-relation, frozen-CLIP model on a reconstructed split and is not the canonical benchmark; its tie to the paper's central claim (about debiasing methods) is indirect.

### Discussion
- Limitations are comprehensive and candid. Missing: explicit statement that the findings may not transfer to non-prior-indexed architectures (W1).

### Conclusion
- The first two sentences of the conclusion are crisp. "The field's metrics report the sum" and the benchmark recommendations extend beyond two audited checkpoints (W1, W6).

### References
- Mostly 2018-2022 for SGG; add 2023-2026. Item [34] (Sagawa et al.) has no back-reference page, which suggests it is cited only in the supplement or not at all in the main text.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`. No target criteria were supplied (`criteria_binding_unavailable`); the "criterion source" below is my configured area-chair perspective only.

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | Configured AC perspective | PARTLY_MEETS | text: Sec. 2 "What the split adds is the exact additive accounting" | New exact paired split with control; prior-correction finding is known (DLFE, LA) | Theory novelty outside my remit; related-work recall unverified | yes: novelty beyond known folklore is argued thinly (W4) |
| Methodological Rigor | Configured AC perspective | NOT_ASSESSED | none | Assigned to Reviewer 1; I only checked number tracing | Did not verify proofs | no |
| Evidence Sufficiency | Configured AC perspective | PARTLY_MEETS | table: Table 1; absence: Secs. 5-6 non-MOTIFS audit | Numbers trace and intervals reported; breadth is two checkpoints; IETrans claim overreaches | Cannot assess unseen appendices fully | yes (W1, W2, W3) |
| Argument Coherence | Configured AC perspective | PARTLY_MEETS | text: Abstract IETrans sentence | Consistent main thread; abstract/conclusion scope wider than evidence | none identified | yes (W2) |
| Writing Quality | Configured AC perspective | PARTLY_MEETS | figure: Figure 1 caption | Clear prose; extremely dense for 8 pages; heavy appendix dependency | Subjective | no (repairable) |
| Literature Integration | Configured AC perspective | PARTLY_MEETS | absence: Sec. 2 post-2022 SGG evaluation | Good statistical lineage, dated SGG coverage | Recall of missing works unverified | yes (W4) |
| Significance & Impact | Configured AC perspective | MEETS | text: Sec. 7 Conclusion reporting suggestions | Relevant to SGG evaluation practice; adoption limited by archived outputs | Impact depends on W1 outcomes | yes (W1, W6) |

The recommendation is driven by the unresolved decision-bearing items W1 (breadth, repairable with additional runs or rescoped claims), W2 (repairable wording/experiment) and W3 (repairable framing); none is fatal to the core contribution.

---

## Questions for Authors

1. Can you audit at least two further released debiasing methods of a different family (not prior-indexed MOTIFS) and one from 2023 or later? Would the finding that gains are almost entirely group-level hold, or is it specific to methods whose mechanism is a logit shift?
2. For IETrans, can you train a plain baseline with the same codebase and visual-term fusion so the relabelling effect is isolated from reweighting and from baseline differences? How does the abstract claim "under every measure" square with the AUC_c interval [-.0181, +.0004] and case-level mR interval [-.0031, +.0151]?
3. What minimal AUC or case-level change could your pipeline have detected for TDE (an equivalence margin)? Can you state "unchanged within +/- x"?
4. What exactly should a benchmark archive to make the recommended report possible for future submissions, and could a reduced report be computed from top-k outputs alone?

---

## Minor Issues

### Language / Grammar
- Abstract: sentences with stacked qualifiers ("so we read the remainder against a control") could be split.
- Sec. 5: "a better F@50" is introduced with no definition in the main text beyond the parenthetical.

### Citation Format
- Back-reference lists in the bibliography point to supplement pages (e.g., [17] "19", [31] "2, 7, 16, 35"), which makes the main-paper bibliography carry supplement page numbers; the venue style usually wants main-paper pages only. [34] has no cited page.

### Figures and Tables
- Figure 2(a) and (b) and Figure 3 use small text at print size; Table 1 mixes two weightings and units in one dense block; consider splitting AUC columns into a second table.
- Figure 1 relies on a long caption; a small worked numeric grid in the figure would help.

### Layout
- Figure 3 predicate labels overlap with the legend region in the extracted text; check legibility at 100% zoom.
- The supplement names the method "WAGER" (e.g., "WAGER already requires a bounded score", Appendix B.4) while the main paper is nameless and the repository is called WAGER; if the name is public, it may compromise anonymity. Replace with neutral wording in the supplement and in the shipped archive.
