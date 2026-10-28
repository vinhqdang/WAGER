# Journal-Fit (Venue-Fit) Review, CVPR 2027 simulated panel, round 4, seat 1 (EIC / area chair)

Status: `NOT_CALIBRATED`, `criteria_binding_unavailable`. No venue criteria were supplied. Nothing below is a venue-alignment claim beyond expert judgement.

## Manuscript Information
- Title: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- Submission: anonymous CVPR 2027; target commit ea0efe7
- Materials read: paper_text.txt in full, paper.pdf (10 pages, pages 1 and 6 viewed as images), supp.pdf (40 pages, text skimmed, front matter and Appendix Q headers read), results/*.json listing, and `experiments/verify_manuscript_numbers.py` (executed: "all 89 manuscript numbers trace to committed results").

## Reviewer Information
- Role: Journal-Fit Reviewer / area chair. Background: scene graph and visual-relationship evaluation, evaluation methodology.
- Confidence: 4/5. I am confident on fit, originality, SGG context and clarity. I did not re-derive the proofs (Appendix E) or re-run the checkpoints.

## Overall Assessment
- Recommendation: **Major Revision** (CVPR terms: **Borderline**, leaning weak accept on contribution and weak reject on the current 8-page presentation).
- Rating: 3/5 on a Strong Reject / Weak Reject / Borderline / Weak Accept / Accept scale (Borderline).
- Confidence: 4/5.

In one paragraph. The question is real and important to the SGG community. Mean recall is the headline number for debiasing, and asking which part of a gain is group-level and which is case-level is new and useful. The audit of TDE, DLFE, IETrans and PE-Net is the kind of evaluation work CVPR benefits from. Three things keep it at the bar's edge. (1) The 8-page body is a compressed digest of a 40-page supplement, and a reader who only has the body cannot follow the argument. (2) The headline claims are heavily hedged (four checkpoints, one run each, a protocol chosen post hoc for TDE and IETrans), so the empirical contribution is narrower than the title implies. (3) The central claim about TDE ("no discrimination gain") rests on a null that is only tight under weightings the paper itself calls head-heavy.

## Summary
The paper proposes an exact additive split of the score difference between two frozen models into a group-level part (the gain that survives shuffling labels within a declared cell, here the subject-object class pair) and a case-level covariance part (Theorem 1; Yates-style). It extends the split to label-weighted hit rates, so mean recall@K itself can be decomposed, via a replay of the official evaluator at counterfactual labels. It adds image-clustered U-statistic intervals, an operating-point control (logit adjustment by the training log-prior, LA), a within-cell AUC and a confidence-matching protocol. Validation uses simulation and controlled VG150 predictors (FREQ, MLP-CLASS, MLP-SPATIAL, CLIP crops). Audits of released checkpoints find that 87% of TDE's +0.097 mR@50 is group-level and that LA recovers +0.094 of it. DLFE and IETrans are 94% and 97% group-level. PE-Net is 86% group-level with a case-level part (+0.024) above the spread between two separately trained baselines (+0.001), but without a supported AUC gain. A Waterbirds example shows a debiasing gain that is case-level.

## Strengths
1. **Right question for the field.** Mean recall is credited to a method regardless of mechanism, and the paper gives a concrete, reproducible way to say which mechanism. The headline "LA with no within-pair ranking change recovers +0.0941 of TDE's +0.0972" is memorable and checkable.
2. **Exact accounting, not a heuristic.** Theorem 1 is an identity with no fitted reference model, O(NK) cost on cached predictions, and the same machinery works for mean recall (Sec. 3, "Splitting mean recall").
3. **Honest scope and unusually good self-critique.** The "What is not claimed" paragraph, the dated protocol declaration (post hoc for TDE/IETrans, prior for DLFE/PE-Net), the reporting of Table 27, and the refusal to read one secondary interval as a finding are all good practice. Results where the control does not match (K=20, K=100, no graph constraint) are reported, not buried.
4. **Validation where truth is known.** Simulations (nominal coverage 94.0%, undercoverage at two cases per cell reported at 81.5%), controlled predictors with forced zero (MLP-CLASS vs FREQ), and the CLIP case where aggregates rank the model last but the case-level part credits it.
5. **Reproducibility.** An archive with results files and a script that checks every quoted number. I ran it: 89 values trace to committed results. The evaluator replay reproduces the official R@50 and mR@50 to four decimals (0.6612/0.1459 baseline, 0.4588/0.2476 TDE).
6. **Breadth beyond SGG** (Waterbirds, CIFAR-LT, text) supports significance for the wider evaluation-methodology audience.

## Weaknesses

### Major

**W1. The 8-page body is not self-contained; the paper leans on a 40-page supplement for claims that carry the conclusions.**
- Anchor: Sec. 4-6 cite Appendices I, J, K, N, O, P, Q and "Tab. 27" (not in the body) for nearly every decisive number. Examples: the coverage claim (l. 296-302, Appendix J), the AUC weightings Q.4 (l. 412-427), the recalibration protocols Q.1/Q.2/Q.4 (l. 443-444), and the PE-Net and IETrans caveats (Appendix O.2, Q.6, Q.8). The abstract carries about 25 numbers.
- Problem: At CVPR the body is the reviewed unit; the supplement is optional reading. A reader of the body alone cannot judge the split's validity, the post-hoc protocol choice, or the weighting sensitivity. The text is also compressed: the confidence-matching paragraph (l. 237-252) and the AUC weighting paragraph (l. 397-427) read as dense lists. Fig. 3 labels are unreadable at print size (viewed page 6), and Fig. 2(b) annotations ("T only (square); shared T: -0.018, off scale") are tiny.
- Fix: Cut the abstract to the three or four numbers that carry the argument (87%, 0.0941/0.0972, the AUC null with its bound, PE-Net's case-level part against the baseline spread). Move Waterbirds and the DLFE/IETrans/PE-Net paragraphs to a single compact table plus two sentences each. Free about one page for a worked four-point example of the split (now Appendix C), which is the single best intuition aid and does not appear in the body. Enlarge Fig. 3 (fewer predicates or a two-column figure) and make Table 1 readable by dropping the second AUC weighting from the body.

**W2. The "TDE shows no discrimination gain" conclusion is stronger in the abstract than the evidence in the body supports.**
- Anchor: Abstract l. 19-21 ("excludes changes above 0.0038 to 0.028 under four weightings, tightly only under the two that favour head predicates"); l. 413-423: per-predicate weighting, "the closest to mean recall, passes none" (-0.097, [-0.228, +0.024]); margins "set after TDE's results were seen"; against the control, the case-level part "excludes only changes above 0.0043, a third of TDE's own, too wide to call it zero" (l. 428-430).
- Problem: The paper's own tightest bounds hold under head-heavy weightings, while mean recall weights predicates equally and that is where the bound fails. The "no gain" claim is therefore a result about head-predicate ordering. The paper also states both "no weighting shows TDE gaining discrimination" and "the case-level part is too wide to call zero", two readings the title audience will not reconcile quickly.
- Fix: State the claim as "no detected AUC gain; equivalence established only for head-weighted comparisons" in the abstract and Conclusion. Move the per-predicate result (the weighting that matches mean recall) into the body table, since it is the one that matters to the headline metric. Pre-register the margin for the next round (for example, tie the margin to the 0.006 or 0.018 spread between separately trained baselines, as already used for PE-Net) so the equivalence test is not post-hoc.

**W3. Scope of the empirical evidence is narrower than the framing (title, "what did ten points buy", proposal to report the split beside mean recall).**
- Anchor: four released PredCls checkpoints, one run each (Sec. 1 "What is not claimed"; Limitations l. 595-597: intervals cover "test sampling, not training"); IETrans and PE-Net use a separately trained baseline, so the comparison "does not isolate the effect of relabelling" (l. 509-511); SGCls/SGDet match only 58% / 65% of relations (l. 529-534); the control matches TDE only at K=50 with the graph constraint (l. 455-459).
- Problem: The most reported SGG setting is SGDet. For the reader the new claim is "most mean-recall gains of prior-correcting debiasers are group-level", resting on three such methods in PredCls, in addition to a prototype method. No recent one-stage or VLM-based SGG is audited, so the proposal to adopt the split as a standard report has thin support. The K=20/100 and no-constraint rows (Table 2) also show the "control matches" finding is protocol-specific, which the abstract acknowledges only in half a sentence.
- Fix: Either narrow the title/abstract to "prior-correcting debiasers in PredCls" or add at least one more family (a training-time reweighting method such as the class-balanced or group-collaborative learners the paper cites [11, 13], where the split should show a different profile, and one recent model). Report training-seed variance for at least the baseline and one debiased model, since "separately trained baselines differ" is the only noise estimate and it is a single pair (+0.0206 mR@50, case-level +0.0007).

**W4. The central quantity depends on a declared grouping and a recalibration protocol, which makes the headline share (87%) fragile as a number.**
- Anchor: with subject class alone as cell, the group-level share is 18% (l. 384-385) against 87% for class pairs; refining by position/subject size gives 90%, the per-image statistic 84%; the sign of the quadratic case-level part flips with protocol (-0.00006 temperature alone, +0.00445 temperature plus per-class bias, -0.0184 shared temperature; l. 441-444).
- Problem: A reader will quote "87% group-level", but the paper itself shows the number ranges from 18% to 90% across defensible cells and the quadratic-score sign changes with calibration. The paper defends the class pair as the finest defensible cell, but does not say how a practitioner should choose when benchmark construction does not declare a grouping. The mean-recall split (the primary object) avoids recalibration, which is a strength, but the paper still leads with proper-score results (Fig. 2, Sec. 4) that depend on it.
- Fix: Lead the SGG narrative with the mean-recall split and the AUC (both protocol-light) and present the proper-score split as the validation instrument. Add one table row set (body) listing share under: class pair, class pair plus position, subject only, per-image statistic, so the 18% to 90% range appears next to the 87%. Give a one-sentence recommendation rule for ϕ (for example, finest cell with at least a stated median cases per cell, since coverage falls to 81.5% at two per cell).

### Minor

**W5. Novelty positioning versus the proper-score and permutation-importance literature should be sharper in the body.** Anchor: Related work, l. 137-157. The covariance form is credited to Yates [50], and the case-level part is "the difference of two models' conditional permutation importances" (Proposition 2). The new content is the paired-gain accounting, mean-recall extension, clustered inference and the controls. A CVPR reader needs this stated as the contribution in one sentence in the Introduction, not discovered in related work. Fix: add "what is new relative to [50], [14], [41], [33]" to contribution (i).

**W6. Terminology load.** Anchor: group-level ΔP̂ vs "transported gain"; case-level ΔR̂ vs "within-group covariance gain" (supplement Sec. A renames them); "cell", "control", "matched", "primary protocol", "by comparison weighting", "relation-weighted AUC". Problem: two vocabularies across body and supplement, and six "weightings" in the body. Fix: use one name set throughout, keep the Appendix L terminology table but cite it once in the body.

**W7. "Group-level is not a lesser gain" is stated (l. 465-468) but not demonstrated for the SGG downstream tasks it names (retrieval, captioning).** For a CVPR audience this is the question that determines whether group-level gains are "worthless". Fix: either add a one-line pointer to measurable downstream evidence or soften to "may be exactly what retrieval wants".

**W8. Interpretation of IETrans AUC fall.** Anchor: l. 504-510. The paper itself notes synonymy as a confound for the −0.0238 AUC change and that no baseline was released. The abstract nonetheless lists IETrans as 97% group-level without that qualifier. Fix: add "(separately trained baseline)" in the abstract for IETrans and PE-Net, as done for PE-Net already.

**W9. Reporting precision.** Four to five decimals throughout, with CIs to four digits, and 90% intervals mixed with 95% (l. 412-413 vs Sec. 4 "All intervals are 95%"). Fix: state interval level in every table caption; round to three decimals in the body.

## Desk-rejection risk check (from the PDFs)

| Item | Finding | Risk |
|---|---|---|
| 8-page limit, excluding references and the LLM Usage Statement | Body (title through Conclusion, l. 001-608) ends on page 8; LLM statement starts at the bottom of page 8, references on pages 9-10 (10 pages in total). Letter size, two-column, CVPR template, line numbers present, Nimbus/CM fonts embedded. | Low. I measured nothing that crosses the limit; the body is very dense (small Fig. 3, tight Table 1), so check that no vertical-spacing or font-size tweak was used to fit. |
| Mandatory LLM Usage Statement | Present, placed after the conclusion, before references. It names the tools, scope (writing, code, checking numbers, simulated reviews) and author responsibility. | Low. Wording is "The author" (singular) in a possibly multi-author submission: check against the author list. |
| Anonymity | Header reads "Anonymous CVPR submission"; no author, affiliation, acknowledgement or self-citation by name found in the body text. Supplement front matter has no names. PDF metadata Title/Author fields are empty. The statement names the vendor of the LLM tools (Anthropic/Claude Code), which identifies a tool, not an author. | Low. Confirm that the code archive metadata (zip comments, git config, paths such as /home/user) contains no identifying strings; I did not inspect the archive. |
| External links | No URLs in the body; the supplement mentions third-party authors' "Google Drive" model zoo (a description of how a third party released a checkpoint, not a link). Code is described as an "anonymized archive alongside this document". | Low. Ensure the archive is supplied in the permitted supplementary channel and is not a live repository link. |
| Formatting | Template, line numbers and header intact. Fig. 3 and Fig. 2(b) text is very small; Table 1 is crowded. | Medium for readability, low for rejection. |
| Supplement length | 40 pages, compiled with the main paper's numbering (the supplement says both are compiled as one document; main-paper back-references list pages up to 40). | Low for desk rejection if the venue puts no cap on supplements; check the 2027 supplementary-material rules, which I could not verify. The risk is perceptual: a body that cannot stand without it (W1). |
| Dual submission / prior work | Cites no own prior work; the Introduction says "our evaluation of the released checkpoint". | None seen. |

Items I could not check from these materials: the exact CVPR 2027 supplement size/page rules and file-size limit, and whether author-list length matches the singular "The author".

## Questions for the authors
1. Under the per-predicate weighting, the one closest to mean recall, no bound is passed (−0.097, [−0.228, +0.024]). What is the smallest AUC gain for TDE the audit could detect there, and how many tail-tail comparisons does that depend on?
2. How should a benchmark user pick ϕ when no grouping was declared? Is "finest cell with at least n cases per cell" the proposed rule?
3. Training-seed variance: can you rerun TDE and the baseline with two or three seeds so that the 0.006 (AUC) and 0.0007 (case-level) "spreads between baselines" are not single-pair estimates?
4. For SGDet only 65% of relations are matched. Does the group-level share change if unmatched relations are scored as misses rather than excluded?
5. Does the split distinguish TDE's gain from a pure label-frequency reweighting of the loss (class-balanced training) in the same cell structure? A positive control with a known training-time reweighting would help.

## Missing references
Each was checked by web search unless marked.
- Tang, Huang, Zhang. "Long-Tailed Classification by Keeping the Good and Removing the Bad Momentum Causal Effect." NeurIPS 2020 (arXiv 2009.12991). Verified via the NeurIPS proceedings page. It applies the same counterfactual/TDE idea to long-tailed classification and is directly relevant to the paper's claim that TDE reduces to a logit adjustment and to its CIFAR-LT study.
- Knyazev, de Vries, Cangea, Taylor, Courville, Belilovsky. "Graph Density-Aware Losses for Novel Compositions in Scene Graph Generation." BMVC 2020 (arXiv 2005.08230). Verified (arXiv and BMVC listing). It argues existing SGG metrics are hard to use for zero- and few-shot evaluation and introduces a weighted metric; relevant to the paper's related work on metric critique and its zero-shot paragraph.
- Oaxaca-Blinder / Kitagawa-type gain decompositions as precedent for exact additive accounting of a gap into between-group and within-group components: [UNVERIFIED], I did not search for a specific citation. The authors may find an appropriate reference themselves.

## Detailed comments
- Sec. 1, l. 42-52: the sentence "none attributes the gain between two models to one route or the other" is the paper's novelty claim. Say which of the four cited remedies is closest (head/body/tail recall slices) and why a slice of a single model's recall cannot do this.
- Contributions (ii) lists "a map of what it does not separate". This is a strength; move the one-line list (calibration, operating point, label mix, pair-varying prior shifts) into the abstract in place of some numbers.
- Sec. 3 "Choosing the grouping": the "robustness value of Cinelli and Hazlett" sensitivity (Proposition 4) is a nice touch, but a CVPR reader will need one concrete number (the elicited correlation at which TDE's verdict would change) in the body.
- Sec. 5 l. 365-372: the protocol-declaration timing is excellent practice. Put it in a short boxed list or footnote of Tab. 1 for visibility, and note in the abstract that for TDE and IETrans the protocol is a post-hoc choice.
- Tab. 1 caption is long and carries definitions (baseD, LA, ∆AUCr/c). Split the definitions into the text.
- Fig. 1 is clear and effective; keep it. Fig. 2(a) is legible but the "T only (square)" and "shared T" legend in 2(b) is not.
- The oracle line (l. 472-473, +0.5068 all case-level) is a helpful sanity bound and should be kept; it shows the share is not forced by the metric.
- Conclusion: proposes reporting "the declared grouping, both parts with intervals, the within-group AUC and, for a thresholded metric, the operating-point control". Good, concrete. Add a pointer to the released code as the means of adoption.
- Sec. 7 Limitations are candid; add "no one-stage / VLM SGG audited" explicitly (it is in "What is not claimed" but not the limitations list).
- Citation hygiene: [17] (He et al.) and [22] (Lang) appear only through supplement back-references, fine; check that the main bibliography does not show uncited entries when the supplement is excluded.

## Fit and significance verdict (expert judgement only)
- Fit: an evaluation-methodology paper about SGG is a reasonable CVPR submission, in the tradition of metric-critique papers; the statistical machinery is heavier than usual but is directly applied to a widely used metric.
- Originality: new accounting of paired gains, new use of within-cell label transport for mean recall, new audit findings on TDE/DLFE/IETrans/PE-Net. The underlying identity is classical (Yates) and the paper says so.
- Significance: moderate to high if the finding that prior-correcting debiasers gain mostly at the group level generalises beyond PredCls and three methods; currently demonstrated for a narrow set.
- Clarity: the weakest dimension (W1, W6).
- Clears the CVPR bar: borderline; a clearer body, a narrower or better-supported claim set and one more method family would move it to weak accept. No venue criteria were supplied (`criteria_binding_unavailable`), so this is expert judgement only and `NOT_CALIBRATED`.
