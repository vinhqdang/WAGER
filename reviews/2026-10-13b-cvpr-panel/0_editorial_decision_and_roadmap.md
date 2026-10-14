# Editorial Decision Package (Round 2)

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

`criteria_binding_unavailable`: no target-criteria binding was supplied and all five cards disclose this. No venue-alignment claim is made. The standard Synthesis Protocol was used (no sprint contract), so no scoring matrix or failure-condition arithmetic applies.

Same-model-family panel: all five Phase 1 seats ran on one model family (Sonnet) from one provider, and this synthesis is by an agent whose runtime identifies it as the same family. Agreement among seats is weaker evidence than agreement among independent reviewers, and repeated findings may reflect one shared reading of the same passage. Full provenance is in `_panel_provenance.md`. Because of this limit, the claims that decide the outcome were rechecked against `results/*.json`, the text extracts and (for one external claim) the cited source (section "Verification").

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Venue configuration**: simulated CVPR 2027 panel (configured perspective only)
- **Review target**: `cvpr2027/paper.pdf` (8 pp + references) and `cvpr2027/supp.pdf`, repository commit `2da86a9`. The Table 2 rendering defect flagged by the EIC (W6) was fixed afterwards in commit `5d69361` and is marked resolved below.
- **Decision date**: 2026-10-13
- **Review round**: 2 (mode full, Phase 2). The seat cards label themselves "Round 1" because the seats saw no earlier panel; this synthesis counts the panel as round 2 on the dispatcher's instruction. The round-1 package is `reviews/2026-10-13-cvpr-panel/` (commit `18a72c9`; roadmap IDs `R4-n`). Round-2 IDs are `R5-n`.
- **Submission deadline**: 16 Nov 2026 (34 days from the decision date); 8-page body limit.

## Review Panel Provenance (summary)

Five role-separated seats (EIC, R1, R2, R3, DA), each a fresh AI subagent run on Sonnet launched by an Opus orchestrator, no peer visibility. Whether the seats could see the round-1 panel was not stated by the dispatcher and is recorded as `unknown`. Accountable human: Quang-Vinh Dang (British University Vietnam). No typed `review-panel-provenance/1.0` artifact or digests were supplied, so none are reported. Axes: role-separated true; blind to peer outputs true; model-family distinct **false**; provider distinct **false**; human-reviewer distinct false. No binary independence claim is made. No cross-model decision check was run.

---

## Decision

### Major Revision

**Confidence in the decision: high for the category; medium that the revision is smaller than in round 1.** All four scoring seats recommend Major Revision (R3 states "weak accept / minor-to-major, borderline accept" and maps to Major; EIC says borderline, leaning accept only if framing and scope are repaired). The Devil's Advocate raised 0 CRITICAL issues (7 MAJOR, 5 MINOR). The round-1 decision-bearing re-analyses (same-image sensitivity, proper-score reading, margin, both AUC weightings, DLFE as a controlled pair) were done and no seat disputes the arithmetic. What keeps the decision at Major is: (i) one decision-bearing re-analysis that is new in this round, an AUC weighted like mean recall (R5-4), without which the ranking claim in the abstract is not shown to cover the predicates mean recall rewards; (ii) a cluster of abstract/conclusion statements that every seat finds stronger than the paper's own Table 2, Sec. 7 and Appendix K support; (iii) a method scope that all five seats flag. Items (ii) and (iii) are re-framing, not new science. If R5-1 to R5-8 land as written, the editor would expect the next round to be a Minor Revision or an accept-with-conditions on this simulated scale.

Editorial lines for the sprint/audit trail:
- `da_critical_adjudications: []` (the DA's CRITICAL table is empty, with the stated reason that none of M1 to M7 alone invalidates the central identity or the TDE numbers)
- `editorial_decision=major_revision`

---

## Round-1 items: status at commit 2da86a9

Status is the synthesizer's reading of the five round-2 cards plus the text extract; "re-raised" means one or more seats raise the same concern again against the current text.

| Round-1 item | Round-2 status | Evidence in round 2 |
|---|---|---|
| R4-1 scope narrowed to audited checkpoints | **Partially resolved.** Abstract now names three released Neural-Motifs PredCls checkpoints and "we audit no later method" is in Sec. 7. Re-raised: the audited family is prior-correcting, so the generalisation to "debiasing methods" and the benchmark message remain (EIC W1, R2 W3, DA M7). | R5-1 |
| R4-2 IETrans uncontrolled | **Partially resolved.** "Against a separately trained baseline" is in the abstract. Re-raised: the abstract still says "its within-pair ranking falls" as a method finding (EIC W1, R1 W3, R2 W7, R3 W4, DA M4). | R5-6 |
| R4-3 grouping dependence | **Partially resolved.** Abstract says "when cells are subject-object class pairs"; 90% and 18% are in Sec. 5 and Sec. 7. Re-raised: the 18% to 90% range is not at the headline and the grouping table is in Appendix K (EIC W4, R1 W2, R2 W4, R3 W1, DA M6). | R5-3 |
| R4-4 protocol qualifiers | **Partially resolved.** Abstract says graph-constrained, micro-pooled, @50 for the share, and the intro says the control match is specific to K=50. Re-raised: the abstract's control sentence carries no cut-off or constraint caveat (EIC W2, R1 W2, R2 W1, R3 W1, DA M2). | R5-2 |
| R4-5 both AUC weightings | **Resolved as wording.** Abstract gives 0.0034 (split's weighting) and 0.0077 (every comparison counts once). Residual is the weighting itself (R1 W1), see R5-4. | R5-4 |
| R4-6 margin and 90% interval | **Partially resolved.** The fixed-margin claim is replaced by "largest change excluded", a 5/10/25% grid is in the supplement, and the 90% intervals are now nested in the 95% ones (verified below). Re-raised: the grid reference gain comes from a different model family, 10% passes under one weighting only, and no dated declaration exists (R1 W1, R1 W6, R3 W3, DA M3, DA m4). | R5-5, R5-20 |
| R4-7 same-image and identical-input dependence | **Resolved as analysis.** `cross_image_split` reported, no sign or verdict changes (R3 notes it). Not re-raised as a blocking item. A related, smaller interval-validity point is new (R1 W5). | R5-11 |
| R4-8 proper-score reading | **Mostly resolved.** "Confidence, not ranking" removed; abstract now states the +0.0082 frequency-prior removal. Re-raised: abstract still quotes +0.0045 as the protocol value, contribution (ii) says the split "separates calibration, prior and shortcut effects", and no pair-indexed family or primary-protocol randomization p exists (R1 W4, R3 W6, DA M1). | R5-7, R5-12 |
| R4-9 reframe and label-mix figure | **Partially resolved.** Abstract states the case-level part grows under a uniform label mix. The label-mix figure is still not in the body, and no "how to read the split" rule is stated (EIC W3, R2 W6, R3 W2, DA M5). | R5-8 |
| R4-10 SGCls/SGDet matched fraction | **Resolved in Sec. 5**, minor residual: abstract says "SGCls and SGDet replications of TDE agree" without the matched fraction (R2 W5). | R5-19 |
| R4-11 seeds / second method | **Partially resolved.** DLFE added as a controlled released baseline/debiased pair (three checkpoints now). Training seeds still absent and stated as a limitation; re-raised (EIC W8, R1 W3, R3 W4, DA m2). | R5-13, R5-14 |
| R4-12 DLFE | **Resolved.** DLFE result in abstract, Table 1 and supplement. | none |
| R4-13 held-out calibration | **Resolved as cross-fitting** (R4-13 status table). R1 W4 and R3 W6 note the primary value still depends on a random half. | R5-7 |
| R4-14 CLIP framing | **Resolved** (controlled illustration; not re-raised as blocking). | none |
| R4-15 confirmatory/exploratory | **Partially resolved.** Two primary quantities named and a supplement table of all configurations; no dated declaration (R1 W6, DA m4). | R5-20 |
| R4-16 predicate merge | **Re-raised.** Label ambiguity limits what "within-pair ranking falls" can mean (R2 W2, DA alternative path 2). | R5-16 |
| R4-17 density | **Re-raised** (EIC W5; R1, R3, DA on the abstract). | R5-10 |
| R4-18 credit and contributions | **Resolved** (Yates and [6, 43] credited); EIC W7 asks for a side-by-side with existing diagnostics. | R5-17 |
| R4-19, R4-21, R4-22 | **Resolved** (predicted-pair argument, minimal tier, per-image official split). DA m1 asks that the official-statistic share (84%) be headlined beside 87%. | R5-2 |
| R4-20 related work, typos | **Partially resolved.** FGPL and F@K source done; post-2023 literature still absent (R2) and the back-reference lists for [14] and [39] ("3, 2") are re-raised by EIC and R3. | R5-17, R5-24 |
| R4-23 beyond scene graphs | **Re-raised in a stronger form** by R3 W4: a positive case-level contrast exists in the repository and is absent from the body. | R5-15 |
| R4-24 case-level naming | **Re-raised** (R2 W6, R3 W5, DA M1). | R5-8 |
| R4-25, R4-26, R4-27, R4-28 | Not re-raised as such, except: no randomization p for the primary protocol (R1, see R5-7); label ceiling (R2 W2, DA, see R5-16); a case where the split changes a conclusion (EIC W7, see R5-17). | as noted |
| EIC W6 Table 2 clipped, "iny[" overprint | **Already resolved** in commit `5d69361` (the `\tiny` macro was written as a tab; table scaled to the column). The seat read the pre-fix PDF. The synthesizer did not re-render the PDF; confirm in the next compile. | R5-24 (confirm only) |

---

## Verification (read-only checks of the claims that decide the outcome)

No file other than the two deliverables was modified. One download was made into the session scratchpad (outside the repository) for item (g).

| # | Claim | Source seat | Status | How |
|---|---|---|---|---|
| (a) | Headline split: +0.0972 = +0.0841 group + +0.0130 case, 87% | all seats | **Verified** | `results/sgg_recall_split.json`, gc@50: total 0.097154, group 0.084107, case 0.013048, share 0.8657; official mR 0.14589 to 0.24763 (+0.1017). Matches every seat's log. |
| (b) | Equivalence verdicts depend on weighting and margin | R3 W3, DA M3 | **Verified** | `results/sgg_equivalence.json`, TDE vs none. Relation: difference -0.00148, 90% CI [-0.00338, +0.00149], equivalent at 10% (margin 0.00626) and 25%, not at 5%. Comparison: +0.00261, 90% CI [-0.00216, +0.00771], equivalent only at 25% (margin 0.00808), not at 5% or 10% (0.00323). The abstract's 0.0034 and 0.0077 are exactly the two `largest_change_excluded` values. TDE vs LA1 shows the same pattern. |
| (c) | Round-1 W7 defect (90% bound outside the 95% bound) is fixed | round-1 R1 | **Verified fixed** | Same file, relation, TDE vs none: 95% CI [-0.003603, +0.001752] contains 90% CI [-0.003378, +0.001494]. |
| (d) | The AUC weighting puts almost no weight on rare predicates | R1 W1 | **Verified as stated from the paper's own table; R1's re-weighted AUCs NOT verified** | Supp. Table 33: head-head weight 0.649, head-body 0.317, tail-tail 0.000; TDE tail-tail change -.0675 [-.1918, +.0494]. R1's alternatives (pair-balanced -0.0040 [-0.0117, +0.0016]; mean-recall-aligned +0.0018 [-0.0082, +0.0136]; equal-weight mean over 957 pairs -0.0153) are R1's own exploratory 100-replicate computations and were not re-run here. They need confirmation before the abstract's bound is revised (R5-4). |
| (e) | IETrans "ranking falls" depends on weighting | EIC, R1, R2, DA | **Verified (new detail)** | `results/sgg_equivalence.json`, ietrans vs none: relation -0.02349, 95% CI [-0.02750, -0.01820]; comparison -0.00926, 95% CI [-0.01811, +0.00037] (includes zero; 90% CI [-0.01663, -0.00098] excludes it). The abstract states the fall without a weighting. |
| (f) | Interval theory does not cover VG150 | R1 W5 | **Verified as the paper's own statement; R1's jackknife-vs-Hajek gap NOT verified** | Supp. lines 1104-1108 and 1246-1254: C/sqrt(N*) is about 13.3 and "the theorem does not by itself license the reported intervals". The headline case-level 95% interval [+0.0093, +0.0168] implies SE about 0.0019, consistent with R1's Hajek value 0.001933; R1's delete-a-group jackknife SE 0.002186 (12% larger, one seed) was not recomputed. |
| (g) | arXiv 2503.17862 reports that vanilla logit adjustment has almost no effect on SGG | R2 (marked UNVERIFIED) | **Partially verified; relevance unresolved** | The paper exists: "A Causal Adjustment Module for Debiasing Scene Graph Generation" (Liu et al., March 2025). Its Table 7 and text do state that a "vanilla logit adjustment method has almost no effect" (MotifsNet PredCls mR@20/50/100 12.2/15.4/16.7). Its vanilla LA sets the adjustment A to the inverse predicate frequency, inside its own pipeline and setting. This repository's LA1 subtracts tau log pi(y) from the baseline logits with tau=1, and R1 and R2 reproduced its mR@50 gain (+0.0941) from cached arrays. The two operations may or may not be the same, and the cited paper's evaluation details were not checked. So the claim exists as R2 reported it, but whether it contradicts this paper's control is not established. See R5-17. |
| (h) | Waterbirds contrast: group reweighting gains almost entirely at case level | R3 W4 | **Verified for Waterbirds** | `results/waterbirds_audit.json`, scene cells, Brier, GRW vs ERM: total +0.06373 = group -0.02766 + case +0.09139, case CI [+0.0849, +0.0979]. R3's CIFAR-LT numbers (class-balanced case about -0.196) were not checked. |
| (i) | Randomization p = .555 is attributed to a protocol the text does not name | R1 R9 | **Ambiguity verified; protocol identity NOT verified** | Supp. line 1659 gives "matched quadratic case-level part ... cyclic randomization p = .555" without naming the family. R1's trace that it is the temperature-only family was not repeated. |
| (j) | Without the graph constraint the "share" exceeds 100% | R1 W2 | **Consistent** | EIC's totals for ng@50 (total -0.0337, group -0.0464, case +0.0127) give 138%, matching R1's 1.38. |
| (k) | DA M2 / round-1 verification: the abstract now carries the +0.0082 frequency-prior removal | DA | **Verified in text** | `paper_text.txt` intro lines 088-090 and abstract; round-1 recomputation of +0.0077 to +0.0080 stands. |

Not verified by me (taken from the cards): R1's weighting alternatives, R1's jackknife SE, R2's reference leads other than the one in (g) (SQUAT, Vision Relation Transformer, arXiv 2403.16184 are R2's search results; R2 marks the last as [UNVERIFIED] for relevance), R3's CIFAR-LT figures, the cited papers' protocol details, any proof, any checkpoint replay, and whether the "primary" protocol was declared before the data were seen (the artifacts cannot show it).

---

## Blocking Issues (3, immutable source order)

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| B1 | Method-level and field-level statements outrun the evidence: three single-run released checkpoints of one architecture family, all prior-correcting, one with a confounded baseline; the abstract's IETrans claim and the abstract's control sentence omit the conditions that Table 2 and Sec. 5 state | EIC, R1, R2, R3, DA | text: Sec. 7 "we audit no later method"; text: Sec. 5 "does not isolate the effect of relabelling"; dataset: `results/sgg_recall_split_TDE_vs_la1.json` (K=20 -0.0234, K=100 +0.0300, no-graph -0.0792 to -0.1549) | R5-1, R5-2, R5-6 |
| B2 | "TDE's ranking is unchanged" rests on an AUC that weights head-head predicate pairs at 0.649 and tail-tail at 0.000, with equivalence at the 10% margin under one weighting only | R1, DA, R3 | dataset: `results/sgg_equivalence.json` tost; table: Supp. Table 33 | R5-4, R5-5 |
| B3 | The headline share is conditional on the declared grouping (18% to 90%) and is not stated with that range where the claim is made | EIC, R1, R2, R3, DA | dataset: `results/sgg_grouping_share.json`; text: Sec. 7 "dropping the object class takes it to 18%" | R5-3 |

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence (self-reported scope disclosure) | Questions | Minor issues |
|---|---|---|---|---|---|
| Journal-Fit Reviewer (EIC) | CVPR area-chair perspective, evaluation and scene understanding | Major Revision (borderline; leaning accept only if framing and scope are repaired) | 4 | 5 | 6 (incl. layout) |
| Reviewer 1 | Methodology: proper scores, U-statistics, equivalence testing | Major Revision | 4 | 5 | 3 |
| Reviewer 2 | Domain: scene graph generation, unbiased SGG | Major Revision (borderline weak accept / weak reject) | 4 | 5 | 4 |
| Reviewer 3 | Perspective: long-tail, shift, shortcut evaluation | Weak Accept / Minor-to-Major (borderline accept); mapped to Major Revision | 3 | 4 | 4 |
| Devil's Advocate | Fixed adversarial seat | N/A, findings only | per-finding | n/a | 5 minor, 7 major, 0 critical |

Confidence values are disclosures only and were not used to weigh, count or resolve anything.

Key strengths agreed across seats: exact identity and implementation (R1 reproduced the headline split to six digits); evaluator replay to four decimals (R2); the training-free operating-point control (all four); designed nulls and algebraic zeros that can fail (R1, R3, DA); candour about protocol, grouping and single-run limits (all four); every number traces to committed JSON and no seat or recheck found an arithmetic discrepancy (EIC log: 532 manuscript numbers trace to results).

---

## Step 1b: Weakness Sub-Claim Inventory

Severity is transported from the seat's per-finding tag. Positions: R = raised, C = corroborated, N = not mentioned (silence, not opposition), D = disputed. DA is tracked separately and is not counted in the 4.

| SC | Sub-claim | Parent weaknesses | EIC | R1 | R2 | R3 | DA | Transported severity |
|---|---|---|---|---|---|---|---|---|
| SC-1 | Scope: three 2020-2022 checkpoints of one architecture family; claims reach "debiasing methods for SGG" | EIC W1; R2 W3; R1 W3 (part); R3 W4 (part) | R | C | R | C | M7 | Major (EIC, R2); within Major bundles (R1, R3) |
| SC-2 | Audited methods are all prior-correcting, so "mostly group-level" is the expected outcome; no positive demonstration in SGG | R2 W3; DA M7; EIC W1 | C | N | R | N | M7 | Major (R2, DA) |
| SC-3 | No training-variance interval; single runs; IETrans separately trained | R1 W3; R3 W4; EIC W8; R2 W7; DA m2, M4 | R (Minor) | R | R | R | M4, m2 | Major (R1, R3, DA M4); Minor (EIC, R2) |
| SC-4 | Abstract's control sentence and "recovers +0.094" omit K=50, graph-constraint and the other protocols | EIC W2; R1 W2; R2 W1; R3 W1; DA M2 | R | R | R | R | M2 | Major (EIC, R1, R2, R3, DA) |
| SC-5 | Headline share conditional on grouping (18%/87%/90%); table in appendix | EIC W4; R1 W2; R2 W4; R3 W1; DA M6 | R | R | R | R | M6 | Major (EIC, R2, R3, DA); within Major (R1) |
| SC-6 | Micro-pooled vs official per-image statistic; mixed conventions in one sentence | EIC W2; R1 W2; R2 minor; R3 W1; DA m1 | R | R | R | R | m1 | Within Major bundles; Minor (DA, R2) |
| SC-7 | AUC weighting is not aligned with mean recall; averaging mixed-sign pair changes | R1 W1; DA M3(c) | N | R | N | N | C | Major (R1) |
| SC-8 | Equivalence margin: reference gain from a different model family; 10% passes under one weighting only; "pre-declared" unverifiable | R1 W1, W6; R3 W3; DA M3, m4 | N | R | N | R | M3, m4 | Major (R1, DA M3); Minor (R3, R1 W6) |
| SC-9 | Proper-score case-level part is protocol-identified; abstract quotes +0.0045; contribution (ii) overclaims separation; no pair-indexed family; no primary-protocol p | R1 W4; R3 W6; DA M1 | N | R | N | R | M1 | Major (R1, DA); Minor (R3) |
| SC-10 | Case-level covariance is read as discrimination but also credits shortcuts, operating point and label noise; the conclusion rests on the control and the AUC | DA M1; R3 W5; R2 W6 | N | N | R | R | M1 | Major (DA); Minor (R2, R3) |
| SC-11 | Normative reading: "what did ten points buy" vs "Group-level is not a lesser gain"; no decision rule | EIC W3; R2 W6; R3 W2; DA M5 | R | N | R | R | M5 | Major (EIC, R3, DA); Minor (R2) |
| SC-12 | Label-mix dependence (seven of eight group-level parts change sign) not carried into the conclusion | R3 W2 | N | N | N | R | N | Major (R3) |
| SC-13 | IETrans: "ranking falls" is a statement about agreement with original labels; confounded training and relabelling; comparison-weighted interval includes zero | EIC W1; R1 W3; R2 W2, W7; R3 W4; DA M4 | R | R | R | R | M4 | Major (R1, R3, DA); Minor (R2 W7) |
| SC-14 | Within-pair label ambiguity (near-synonyms) limits what the AUC measures; baseline AUC 0.57/0.61 leaves little headroom | R2 W2; DA M3(c), alt. path 2 | N | N | R | N | R | Major (R2); within M3 (DA) |
| SC-15 | Interval validity: Theorem 4 does not cover VG150; Hajek SE may be about 12% below a jackknife; 200-500 simulation replicates | R1 W5 | N | R | N | N | N | Minor (R1); jackknife gap unverified |
| SC-16 | Forking paths: many protocols and weightings; no dated declaration | R1 W6; R3 W6; DA m4 | N | R | N | C | m4 | Minor (R1, DA) |
| SC-17 | Positioning: head/body/tail and zero-shot recall side-by-side; post-2023 literature; arXiv 2503.17862 | EIC W7; R2 refs | R | N | R | N | N | Major (EIC); related work Minor |
| SC-18 | Density: abstract carries about 15 to 20 numbers; evidence in supplement | EIC W5; R1, R3, DA m5 minor | R | R (minor) | N | R (minor) | m5 | Major (EIC); Minor (others) |
| SC-19 | Best cross-domain contrast (Waterbirds) absent from the body; "Beyond scene graphs" has no body number | R3 W4; DA M7 (part) | N | N | N | R | C | Major (R3) |
| SC-20 | SGCls/SGDet coverage thin (58% matched); abstract "replications agree" | R2 W5 | N | N | R | N | N | Minor (R2) |
| SC-21 | Stakeholder/governance of the declared grouping | R3 W7 | N | N | N | R | N | Minor (R3) |
| SC-22 | Table 2 clipped, "iny" overprint | EIC W6; R1 minor | R | C | N | N | N | Minor; **resolved in 5d69361** |
| SC-23 | Typos and presentation: back-references "3, 2" for [14], [39]; abbreviations ng/gc; Fig. 2b legend; Fig. 3 too many predicates; shares above 100% | EIC minor; R1 minor; R3 minor; DA m3 | R | R | N | R | m3 | Minor |

Decomposition discipline: every sub-claim above is split from a weakness a seat wrote. No sub-claim was introduced by the synthesizer.

## Step 2: Consensus Analysis

### Points of Agreement (Consensus)

**[CONSENSUS-4]** (EIC, R1, R2, R3 all agree, no conflict)
1. SC-4 (abstract/conclusion control claim lacks the K, constraint and protocol conditions). DA M2 corroborates. Table 2 numbers verified in (a) and the round-1 recheck.
2. SC-5 (headline share conditional on the grouping, appendix-only range). DA M6 corroborates.
3. SC-13 (IETrans ranking claim; EIC through W1, R1 W3, R2 W2/W7, R3 W4). DA M4 corroborates. Verified (e).
4. SC-3 (single runs, no training-variance interval; severity differs, see below). DA M4, m2 corroborate.

**[CONSENSUS-3]**
5. SC-1 (scope): EIC W1, R2 W3, and R1 W3 and R3 W4 in part. DA M7 corroborates.
6. SC-11 (normative reading): EIC W3, R2 W6, R3 W2; R1 silent. DA M5 corroborates.
7. SC-9 (proper-score protocol dependence): R1 W4, R3 W6; EIC silent as a weakness; R2 silent. DA M1 corroborates.

### Corroborated findings (2 seats, no conflict)
SC-8 (margin and reference gain; R1, R3; DA M3); SC-10 (case-level reading; R2, R3; DA M1); SC-14 (label ambiguity; R2; DA M3(c) and alternative path); SC-16 (forking paths; R1, R3; DA m4); SC-17 (positioning; EIC, R2); SC-18 (density; EIC plus minor mentions in R1, R3, DA).

### Single-reviewer findings (retained, no consensus label)
SC-7 (R1 W1; the paper's own Table 33 supports the weights, DA M3(c) points at the same low headroom); SC-12 (R3 W2); SC-15 (R1 W5; unverified jackknife gap); SC-19 (R3 W4; Waterbirds numbers verified); SC-20 (R2 W5); SC-21 (R3 W7).

### DA CRITICAL adjudication

There are **0 DA CRITICAL issues**. Nothing to validate, reject or leave unresolved, and no `[DA-CRITICAL-VS-ACCEPT]` condition arises. The seven MAJOR items were treated as findings tracked outside the 4-seat consensus count and routed to the roadmap: M1 to R5-7/R5-8, M2 to R5-2, M3 to R5-4/R5-5, M4 to R5-6, M5 to R5-8, M6 to R5-3, M7 to R5-1/R5-14/R5-15.

## Points of Disagreement and Arbitration

**A1. Is the ranking-equivalence problem a margin problem or a weighting problem? Severity: Major (R1, DA) or Minor (R3).**
- R3 W3 argues the margin was chosen after the fact but credits the abstract for stating both bounds. R1 W1 argues the weighting does not match mean recall and the margin comes from a different model family. DA M3 adds that equivalence fails at 5% and, by comparison weighting, at 10%.
- **Resolution**: treat the margin as a wording issue (R5-5, must-fix, cheap) and the weighting as a re-analysis (R5-4, must-fix). **Rationale**: evidence first. Check (b) confirms the grid and that the abstract states exactly the two excluded bounds, so R3 is right that the abstract is candid. Check (d) confirms R1's premise from the paper's own Table 33 (head-head 0.649, tail-tail 0.000). R1's alternative numbers are exploratory and unverified, so the panel does not adopt them as findings; it requires the authors to run the aligned weighting and report whichever way it falls. Expertise: equivalence testing defers to R1.

**A2. Is the abstract's control sentence misleading or merely compressed? Severity: Major (EIC, R1, R2, R3, DA M2).**
- The abstract's sentence on 87% carries "(graph-constrained, micro-pooled; interval 83-91%)", and the control sentence follows within the same sentence chain; the intro states "at K = 50 ... the control's match is specific to that cut-off".
- **Resolution**: a disclosure gap, not a defect in the analysis; must-fix as one clause plus a protocol card (R5-2). **Rationale**: all five seats read the abstract as unconditional, and the checks show the six-protocol range of TDE-minus-LA is -0.0234 to +0.0300 with the constraint and -0.0792 to -0.1549 without (round-1 recheck of `sgg_recall_split_TDE_vs_la1.json`, consistent with R1's and R2's logs). The cost of the fix is a clause, so the severity label is secondary.

**A3. Remedy for scope: narrow or extend?** (carried over from round 1, A2; direction disagreement on remedy)
- EIC: narrow the title, or add two differently trained methods. R2: audit a non-prior-correcting post-2022 method, or retitle. DA M7: audit one method designed to improve relation ranking. R1: train several baselines for a variance reference. R3: label IETrans as a different-run comparison and move one cross-domain contrast into the body.
- **Resolution**: the floor is narrowing (R5-1, must-fix). Extension is should_fix (R5-13 seeds, R5-14 additional method) and the author's choice; R5-15 (promote Waterbirds) is a cheap partial answer to DA M7's "no positive case" because the repository already holds a case-level-dominated contrast (check (h)). **Rationale**: author autonomy and feasibility. Checkpoint and logit availability for post-2022 methods is unverified (R2 says many release PredCls checkpoints; nobody checked), and DLFE alone cost a Colab run in the previous cycle.

**A4. Does the framing need to change? (EIC, R2, R3, DA M5 vs the paper's own "Group-level is not a lesser gain")**
- DA argues the contrast tests a claim nobody made. R3 argues group-level movement is exactly what a long-tail user may want. EIC calls the title a good question.
- **Resolution**: keep the title decision with the author; require a "how to read the split" paragraph, the label-mix result in the body, and glossing "case-level" as within-pair covariance that also credits shortcuts and operating-point movement (R5-8). DA's claim that "debiasing methods never claimed better within-pair discrimination" is a judgement and is **not verified**; the author may answer it by citing a paper that does make the claim, or by reframing the intro. **Rationale**: round-1 arbitration A4 stands; no seat argues the framing is harmless, and the paper's own Sec. 5 concedes the point.

**A5. Is the proper-score "+0.0045" a protocol artefact? (R1 W4, DA M1 Major; R3 W6 Minor)**
- **Resolution**: wording must-fix (R5-7), with the pair-indexed family as should_fix (R5-12). **Rationale**: the paper already discloses the sign changes and the +0.0082 frequency-prior removal in the abstract and intro (check (k)). What remains is that the abstract and contribution (ii) still point at the +0.0045 and at "separates calibration, prior and shortcut effects". Severity Major because contribution (ii) is a stated contribution, effort small.

**A6. Where does arXiv 2503.17862 matter? (R2, marked [UNVERIFIED])**
- Checked: see (g). The paper exists and says vanilla LA "has almost no effect" in its setting. Whether that conflicts with this repository's LA1 (+0.0941 of +0.0972, reproduced by R1 and R2) turns on how each defines and applies the adjustment, which is not established. **Resolution**: do not cite it as contradicting the control and do not revise the LA result on its strength; cite and discuss it, and state the exact LA operation (what is subtracted, from which logits, with or without the background class and graph constraint) in the main text so a reader can see why the results differ (R5-17).

**A7. Unresolved dissent.** (i) Whether the "primary" protocol and weighting were fixed before the gain was seen cannot be resolved from the artifacts (R1 W6, R3 W6, DA m4); the author must supply a dated record or call it post hoc (R5-20). (ii) Whether the three audited methods are a fair test or a foregone conclusion (DA M7 vs EIC/R2 who ask for breadth) is not settled until R5-14 or R5-15 is done. (iii) R1's claim that the Hajek interval understates the case-level SE by about 12% is unverified and single-seed (R5-11).

---

## Decision Rationale

Four seats recommend Major Revision and none disputes another's numbers; the DA found no CRITICAL defect. Relative to round 1 the panel is less worried about analysis and more worried about what the abstract and conclusion say. The identity is exact, the numbers trace to committed results, the control is a real contribution, and the round-1 re-analyses (same-image sensitivity, matching and AUC reporting, DLFE as a controlled pair) are in. What the seats still find: the control sentence and the IETrans sentence in the abstract state more than Table 2, Sec. 5 and Sec. 7 support (all five seats); the 87% is stated without its 18% to 90% range (all five); the ranking evidence rests on an AUC whose weights almost exclude the rare predicates mean recall rewards (R1, with the weights verified), under a margin whose reference comes from a different model family and which passes at the 10% level under one weighting only (verified); the proper-score +0.0045 is still quoted beside a +0.0082 that comes from an operation that changes no ranking (verified in the paper); and the audited family is prior-correcting, which makes the group-level result the expected one (EIC, R2, DA). I chose Major over Minor because one decision-bearing item needs new analysis (R5-4), one needs a small rerun (R5-7), several should-fix items need re-analysis (R5-11, R5-12, R5-16), and the wording changes are many and interact under an 8-page limit. I chose Major over Reject because every remaining must-fix is a wording change or a bounded re-analysis on cached arrays. The paper's candour is a reason to expect a clean revision.

---

## Part 2: Revision Roadmap

> IDs `R5-n` are transport references in immutable source-traceability order (first source seat in panel order EIC, R1, R2, R3, DA, then within-card order) for items new or re-raised in round 2; the round-1 ID is given where one exists. They are not a work rank. The obligation class is an editorial gate. Severity and confidence are transported from the driving finding. `proposed_targets`: unavailable, because no bound block manifest was supplied; targets are given as sections. Effort is in person-days for one author who has the repository and a working environment, and "feasible" means feasible by 16 Nov 2026 under the 8-page limit; effort estimates are the synthesizer's, not the seats'. Author triage is not collected here.

Page-budget note for every item that adds text: the body is at 8 pages with references on the extra page(s). Net additions in the must-fix tier are one protocol card (about 6 lines), one grouping/protocol table (about 8 rows), and clause-level edits to the abstract, Sec. 1, Sec. 5 and Sec. 7. They need offsetting cuts; candidates (from EIC W5, R3, DA m5) are the intro's number list into Table 1, Sec. 4 simulation detail to the supplement, and Fig. 3 reduced to the top eight predicates (R5-10).

### Required Revisions (Must Fix)

| Ref | Revision item (fix) | Type | Sub-claims | Severity (transported) | Evidence anchor | Source seats | Effort | Feasible by 16 Nov, 8 pp | Round-1 link | Consequence if unaddressed |
|---|---|---|---|---|---|---|---|---|---|---|
| R5-1 | Restate title/abstract/conclusion scope: three released Neural-Motifs-family PredCls checkpoints, all prior-correcting (TDE, DLFE, IETrans), one run each; say the result is expected to hold for prior-shift methods and say which families (feature-changing, prototype/hierarchical, one-stage, VLM) it does not cover. Present the reporting proposal as a proposal. Title change is the author's choice. | re-framing | SC-1, SC-2 | Major | text: Sec. 7 "we audit no later method" | EIC 4, R2 4, R1 4, R3 4, DA 4 | 0.5 | Yes; no page cost | R4-1 | claim_scope_unsupported: abstract |
| R5-2 | Carry the protocol conditions where the control is claimed: in the abstract and conclusion add "at K = 50 with the graph constraint" to the LA sentence and one clause on the other protocols (TDE minus LA -0.0234 at K=20, +0.0300 at K=100, -0.0792 to -0.1549 without the constraint); add a protocol card (grouping, score, matching, K, constraint, pooling) before Sec. 5 and tag headline numbers with it; give the official per-image split (84%) beside 87%; flag or suppress shares when the total gain is negative or the interval passes 100%. | re-framing | SC-4, SC-6 | Major | dataset: `results/sgg_recall_split_TDE_vs_la1.json`; text: Sec. 5 "specific to K = 50 under the constraint" | EIC 4, R1 4, R2 5, R3 4, DA 5 | 0.5 | Yes; about 6 lines, offset by R5-10 | R4-4 | claim_scope_unsupported: abstract |
| R5-3 | Put the grouping range at the headline: in the abstract or first claim of Sec. 5 state 87% (class pair), about 90% (pair x position/size), 18% (subject class), and what rule fixes the grouping without reference to the outcome; move the grouping table (Appendix K) into the body as a small table or panel. | re-framing + move | SC-5 | Major | dataset: `results/sgg_grouping_share.json` (0.866 / 0.181 / 0.897); text: Sec. 7 | EIC 3, R1 4, R2 4, R3 4, DA 4 | 0.5 to 1 | Yes if paired with R5-10 cuts (about 8 rows) | R4-3 | claim_scope_unsupported: abstract |
| R5-4 | Within-cell AUC aligned with mean recall: report the AUC with each predicate weighted as mean recall weights it (and a pair-balanced version) overall and by tier pair, with 90% and 95% intervals from the same bootstrap and at least 1,000 replicates for the tail quantiles; confirm or refute R1's exploratory values (pair-balanced -0.0040 [-0.0117, +0.0016]; mean-recall-aligned +0.0018 [-0.0082, +0.0136]); restate the abstract's ranking bound under the weighting(s) that remain. Report results whichever way they fall. | re-analysis | SC-7, SC-14 | Major | table: Supp. Table 33 (head-head 0.649, tail-tail 0.000); dataset: `results/sgg_equivalence.json` | R1 4, DA 4 | 2 to 3 (AUC and bootstrap code exist: `experiments/sgg_equivalence.py`) | Yes | R4-5, R4-6 (residual) | method_reproducibility_unresolved: Sec. 5 |
| R5-5 | Equivalence wording: say "excludes a change larger than X under weighting W" rather than "equivalent"; state in the body that the 10% margin passes under the relation weighting only, the comparison weighting passes at 25% only, and neither at 5%; give the reference gain's source (reconstructed MLPs on a VG150-style split, not the audited model) and the baseline AUC levels (0.57 comparison, 0.61 relation) as headroom; either supply a dated declaration of the primary protocol or call it post hoc. | re-framing | SC-8 | Major (R1, DA); Minor (R3) | dataset: `results/sgg_equivalence.json` tost, check (b) | R1 4, R3 3, DA 4 | 0.5 | Yes | R4-6 | interpretive_ambiguity_remains: Sec. 5 |
| R5-6 | Method-level numbers: label each of the three methods "released checkpoint, single run, no training-variance interval" in the abstract; for IETrans state that the baseline is a separately trained model with a reweighted loss and relabelled data, that the relation-weighted fall (-0.0235) holds but the comparison-weighted 95% interval [-0.0181, +0.0004] includes zero, and that a fall measures agreement with the recorded labels; say explicitly that DLFE's mean-recall covariance part is detected ([+0.0010, +0.0120]) while its AUC is not. Drop "its within-pair ranking falls" as a method property unless a matched baseline is trained. | re-framing | SC-3, SC-13 | Major | text: Sec. 5 "does not isolate the effect of relabelling"; dataset: `results/sgg_equivalence.json` ietrans | EIC 4, R1 4, R2 5, R3 4, DA 5 | 0.5 | Yes | R4-2, R4-11 | claim_scope_unsupported: abstract |
| R5-7 | Proper-score claims: replace "+0.0045 under the pre-declared protocol" in the abstract by the protocol range (-0.0184, -0.00006, +0.0045) or drop it; reword contribution (ii) so it does not claim to "separate calibration, prior and shortcut effects" (it does not separate a pair-varying shift: +0.0082 for the frequency-prior removal exceeds TDE's +0.0045); make the within-cell AUC the stated evidence for ranking; name the protocol behind p = .555 and report the randomization p for the primary protocol. | re-framing + small rerun | SC-9 | Major (R1, DA); Minor (R3) | dataset: Supp. Table 34; text: Supp. line 1659 (protocol unnamed), check (i) | R1 4, R3 3, DA 4 | 0.5 to 1 (p-value is one run of the existing randomization script) | Yes | R4-8, R4-13 | interpretive_ambiguity_remains: abstract |
| R5-8 | Reading rule and terms: add a short "how to read the split" paragraph (which uses want group-level gain, which want case-level gain; what outcome would change a method's ranking); state that the conclusions rest on the control and the AUC and that the covariance also credits shortcuts, operating-point movement and label noise; gloss or rename "case-level" in the abstract ("within-pair covariance"); move the label-mix result (seven of eight group-level parts change sign) into the body with one number for TDE; respond to DA M5 by citing a source that credits TDE-style methods with better within-pair discrimination or by softening the intro's question. | re-framing | SC-10, SC-11, SC-12 | Major (EIC, R3, DA M5); Minor (R2, R3 W5) | text: Sec. 5 "Group-level is not a lesser gain"; text: Sec. 6 "seven of the eight group-level parts" | EIC 4, R2 4, R3 4, DA 4 | 1 | Yes; net-neutral if the label-mix sentence replaces a Sec. 6 sentence | R4-9, R4-24 | interpretive_ambiguity_remains: abstract |

### Suggested Revisions (Should Fix / Consider)

| Ref | Revision item (fix) | Type | Sub-claims | Severity | Source seats | Obligation | Effort | Feasible by 16 Nov, 8 pp | Round-1 link |
|---|---|---|---|---|---|---|---|---|---|
| R5-10 | Abstract and density plan: cut the abstract to three findings plus one protocol sentence (move DLFE/IETrans numbers to Table 1); move the intro's number list into Table 1; Sec. 4 simulation detail to the supplement; Fig. 3 to the top eight movers; define ng, gc, r, c in captions; Fig. 2b legend. This is the vehicle that pays for R5-2, R5-3, R5-8. | re-framing | SC-18 | Major (EIC); Minor (R1, R3, DA) | EIC, R1, R3, DA | should_fix (treat as prerequisite to must-fix items) | 1 to 2 | Yes | R4-17 |
| R5-11 | Interval validity for the headline: use the delete-a-group jackknife (already in `cross_image_split`) for the headline case-level interval or report both; run a coverage simulation on VG150's own cell sizes and hit contrasts with at least 1,000 replicates; state in the main text that coverage is simulation-supported and that Theorem 4 does not cover VG150. R1's 12% SE gap is unverified: confirm before acting. | re-analysis | SC-15 | Minor (R1) | R1 | should_fix | 1 to 2 | Yes | R4-7 (residual) |
| R5-12 | Add a pair-indexed (cell-wise, shrunk) matching family and report TDE's and the frequency-prior removal's case-level parts under it; or state the limit plainly in Sec. 5 and drop any "separates" wording. | re-analysis | SC-9 | Major (R1, DA) | R1, DA | should_fix | 2 | Yes, if cell-offset fitting is not heavy; else take the wording route in R5-7 | R4-8 |
| R5-13 | Training-variance reference: train 2 to 3 further MOTIFS-SUM baselines (or obtain published seed spread) and report the spread of group share and AUC change; otherwise keep the limitation in the abstract (R5-6). | new experiment | SC-3 | Major (R1, R3) | R1, R3, DA, EIC | should_fix | 5 to 10 GPU-days; uncertain | **Uncertain**; do not count on it. The fallback (R5-6 wording) is feasible | R4-11 |
| R5-14 | Audit one method that is not a prior correction (for example a prototype-based, hierarchical, one-stage or VLM-based model) with a released PredCls checkpoint and cacheable logits, to show whether the tool reports case-level gain in a real SGG system; or state why none is auditable. | new experiment | SC-2 | Major (R2, DA); within Major (EIC) | EIC, R2, DA | should_fix | 3 to 7; availability of checkpoints and logits **unverified** | **Uncertain**; check availability in the first two days, then decide. The fallback is R5-1 plus R5-15 | R4-11 |
| R5-15 | Promote one cross-domain contrast into the body (Waterbirds: group reweighting Brier gain +0.0637 = group -0.0277 + case +0.0914, check (h)), with the recalibration caveat and worst-group accuracy, as the positive case the SGG audit lacks. The five-seed CLIP result is the other candidate. | re-framing + move | SC-19 | Major (R3); partly DA M7 | R3, DA | should_fix | 0.5 to 1 | Yes if swapped against Sec. 4 detail | R4-23 |
| R5-16 | Label ambiguity: report AUC on a predicate-merged label set (`results/predicate_merge.json`) and for generic-vs-specific pairs, especially for IETrans; give absolute AUC levels in the body; state the merge scheme. | re-analysis | SC-14, SC-13 | Major (R2) | R2, DA | should_fix | 1 to 2 | Yes | R4-16, R4-27 |
| R5-17 | Positioning: add a half-page or table row comparing the split with head/body/tail and zero-shot recall on TDE and LA, and one case where the split changes a conclusion those diagnostics do not; add post-2023 related work (SQUAT, Vision Relation Transformer: R2's leads, existence checked by R2 only); add arXiv 2503.17862 (existence and the "almost no effect" statement verified, check (g)) and explain the difference between its vanilla LA and the control here by stating the exact LA operation; cite the TDE-resembles-logit-adjustment observation where [43] is invoked. Treat any statement that those papers contradict the control as **[UNVERIFIED]** until a like-for-like LA is run on the same checkpoint. | re-framing + small check | SC-17 | Major (EIC); Minor (R2) | EIC, R2 | should_fix | 1 to 2 | Yes | R4-18, R4-20, R4-28 |
| R5-19 | State PredCls in the title or first abstract sentence and the matched fraction (58% SGCls, 65% SGDet) where "replications agree" appears; say how matching selection could bias the share. | re-framing | SC-20 | Minor (R2) | R2 | should_fix | 0.25 | Yes | R4-10 |
| R5-20 | Provide an anonymized, timestamped record of the primary protocol and weighting (for example commit dates of the declaration in the repository), or call them post hoc; add one sentence on multiplicity and a pointer to the all-configurations table. | re-framing | SC-16 | Minor (R1, DA); Minor (R3 W6) | R1, R3, DA | should_fix | 0.25 | Yes | R4-15 |

### Consider

| Ref | Revision item (fix) | Type | Sub-claims | Severity | Source seats | Effort | Feasible |
|---|---|---|---|---|---|---|---|
| R5-21 | Feature-ablation check on the strongest candidate shortcut (box geometry, subject size or position): does TDE's case-level part survive masking or swapping it? | new analysis | SC-10 | Minor (R3) | R3 | 1 to 2 | Yes, optional |
| R5-22 | Two or three sentences on grouping governance (who declares the grouping, how to prevent post-hoc choice) and on the user-facing meaning of group-level gain (captioning, retrieval, VQA). | re-framing | SC-21 | Minor (R3) | R3 | 0.25 | Yes |
| R5-23 | Show bootstrap replicate and jackknife group counts in main-text captions; truncate or flag share intervals above 1 (IETrans [0.902, 1.044]); report the share only where the total gain is positive. | re-framing | SC-6, SC-23 | Minor (R1, DA) | R1, DA | 0.25 | Yes (overlaps R5-2) |
| R5-24 | Typos and layout: back-reference lists for [14] and [39] ("3, 2"); confirm in the next compile that Table 2 renders at the column width without "iny[" (fix in `5d69361`, **already resolved**); check every table against the page frame. | editorial | SC-22, SC-23 | Minor | EIC, R1, R3 | 0.25 | Yes |


(IDs R5-9 and R5-18 are unused; numbering is kept stable.)

### Source-Traceability Checklist (source order, not a work order)

- [ ] R5-1 must_fix: scope restated to prior-correcting released checkpoints
- [ ] R5-2 must_fix: protocol conditions at the control claim; protocol card; official-statistic share
- [ ] R5-3 must_fix: grouping range at the headline; table in the body
- [ ] R5-4 must_fix: mean-recall-aligned AUC (re-analysis)
- [ ] R5-5 must_fix: equivalence wording, margin source, headroom, declaration
- [ ] R5-6 must_fix: single-run labels; IETrans and DLFE statements
- [ ] R5-7 must_fix: proper-score abstract claim, contribution (ii), primary-protocol p
- [ ] R5-8 must_fix: reading rule, case-level gloss, label-mix result in the body
- [ ] R5-10 to R5-20 should_fix; R5-21 to R5-24 consider (as in the tables)

### Editor's priority view (advisory; not part of the immutable core)

Ordered by decision weight and by how much each unblocks; the author may order differently.
1. R5-4 (the only new analysis in the must-fix tier; its result may change the abstract's ranking sentence, so do it first and do the wording after)
2. R5-7 (small rerun plus wording; removes the weakest remaining abstract number)
3. R5-2 (one clause and a protocol card; all five seats)
4. R5-6 (IETrans and single-run labels; all five seats)
5. R5-3 (grouping range and table)
6. R5-5 (equivalence wording; depends on R5-4)
7. R5-1 (scope)
8. R5-8 (reading rule and label-mix result)
9. R5-10 (density; pays the page budget for 2, 3, 8)
10. R5-15 and R5-14 check (cheap positive case now; decide on a further method after the availability check)

Suggested schedule against 16 Nov (34 days): days 1 to 4 R5-4, R5-7 and the R5-14 availability check; days 5 to 12 wording items R5-1, R5-2, R5-3, R5-5, R5-6, R5-8 with R5-10 cuts; days 13 to 20 R5-11, R5-12, R5-15, R5-16, R5-17; keep the last two weeks for compile, page-limit checks and a re-review. R5-13 and a full R5-14 audit are the only items that could miss the deadline; neither is required for the must-fix tier.

### Response Letter Template
Use `templates/revision_response_template.md` to respond to every item R5-1 to R5-24, including a stated decision for each should_fix and consider item. Where the author declines an item, say so; a decline stays visible and unresolved. Round-1 items listed in the status table above that remain "partially resolved" should be answered under their R5 item.

---

## Part 3: Reviewer Report Summary (Appendix)

- **Journal-Fit Reviewer (EIC)**: Major Revision | Confidence 4. Question and numbers sound; scope (three prior-correcting checkpoints), protocol-specific abstract, ambiguous normative message, grouping sensitivity and density are the concerns. The Table 2 defect is resolved. Strongest: SC-1, SC-4, SC-5, SC-11, SC-18.
- **Reviewer 1 (Methodology)**: Major Revision | Confidence 4. Identity and estimator correct; the AUC weighting, post hoc margin, protocol-identified proper-score part and single runs bound what the numbers support; interval theory does not cover VG150. Strongest: SC-7, SC-8, SC-9, SC-3.
- **Reviewer 2 (Domain)**: Major Revision | Confidence 4. Clean replay; the control match is one (K, constraint) cell; label ambiguity; dated, narrow method set; post-2023 literature missing (leads partly UNVERIFIED). Strongest: SC-4, SC-14, SC-2, SC-5.
- **Reviewer 3 (Perspective)**: Weak Accept / Minor-to-Major, mapped to Major Revision | Confidence 3. Headline conditional on grouping, protocol, label mix and single runs; the best cross-domain contrast is absent from the body. Strongest: SC-5, SC-11/12, SC-19.
- **Devil's Advocate**: findings only. Key challenge: the covariance part is not discrimination by the paper's own evidence, so the conclusion stands on the control and the AUC, which are the weak points (M1 to M3); no unresolved Critical challenge.

## Closing

We invite a revised manuscript that addresses the eight required items and states a decision on each suggested item. The audit is careful and candid, and most of the revision is making the abstract, Sec. 5 and the conclusion say what the evidence supports, plus one re-analysis (R5-4) and one small rerun (R5-7). A further review will be needed after the revision.

*Synthesis scope note: this letter synthesizes and arbitrates the five Phase 1 reports; it adds no new review comments. The checks above were used only to adjudicate claims the seats made. Effort and feasibility figures are the synthesizer's estimates.*

---

## Status after the must-fix revision (2026-10-14)

| Ref | Status | What changed |
|---|---|---|
| R5-1 | Done | Abstract, intro ("What is not claimed") and conclusion scope the audit to three released Neural-Motifs PredCls checkpoints of prior-correcting methods, one run each; no claim about feature-, prototype-, one-stage or VLM-based methods. |
| R5-2 | Done | Abstract and intro state that the LA match holds at K=50 under the graph constraint and that the two differ by 0.02 to 0.15 elsewhere; a "Protocol" paragraph opens the Sec. 5 results; the official per-image share (84%) is in the abstract and Table 1; shares are not reported when the total gain is negative. |
| R5-3 | Done | Table 1 has a lower panel for TDE under subject-class cells (18%), class pair x position (90%) and the official per-image statistic (84%); the range is in the abstract. |
| R5-4 | Done (re-analysis) | New `pair` weighting in `wager/rank.py`, `experiments/sgg_auc_label_weighting.py`, supp Table `tab:labelweighting`, 1,000 replicates. While doing it we found that clipping log q at 1e-12 tied about a fifth of the baseline's stored probabilities, so the ranking-preserving control showed a spurious AUC change; the floor is now 1e-300 and every AUC was recomputed (Table 1 and all AUC tables at 1,000 replicates). Result: TDE's 90% bounds are 0.0038 (relation), 0.0077 (comparison), 0.028 (predicate); under the pair weighting TDE's AUC falls, -0.0153 [-0.0249, -0.0004]. R1's exploratory values are superseded. DLFE's relation-weighted AUC now excludes zero narrowly (+0.0029 [+0.0001, +0.0055]); the text says so. |
| R5-5 | Done | Bounds stated as "excludes a change larger than X under weighting W"; margins against the geometry gain under each weighting; baseline AUC levels (0.61, 0.57) given as headroom; the primary protocol is declared post hoc for TDE and IETrans. |
| R5-6 | Done | Table 1 caption: one released run each, intervals cover test sampling only. IETrans: separately trained baseline, relabelling confound, synonymy caveat; the abstract no longer states its ranking change. DLFE: covariance and the small AUC gain stated separately. |
| R5-7 | Done | +0.0045 removed from the abstract and intro; contribution (ii) no longer claims to separate calibration, prior and shortcut effects; randomization p under the primary protocol is .001 (control .236), and the .555 is labelled as the temperature-only protocol (`experiments/run_sgg_primary_randomization.py`). |
| R5-8 | Done | "How to read the split" paragraph in Sec. 5 (who wants which part; what would change the verdict; label-mix dependence with TDE's number); case-level glossed as a within-pair covariance; intro's question tied to TDE's stated motivation. |

Page budget: the paper stays at 8 pages; offsetting cuts were made in Sec. 2-4, 6 and 7 (the worked example moved to the supplement's existing Appendix A). Verifier: all checks pass, with new checks for every number added, signed comparison for signed literals, and an assertion that the control's AUC change is zero to 1e-6.

## Status after the should-fix pass (2026-10-14)

| Ref | Status | What changed |
|---|---|---|
| R5-10 | Done (partly) | Abstract and intro shortened; related work, Sec. 4, Sec. 6 and the conclusion condensed; Fig. 3 reduced. Fig. 2b legend unchanged. Paper at eight pages. |
| R5-11 | Done | `experiments/sgg_interval_and_diagnostics.py`: delete-a-group image jackknife SE 9-13% above the influence-function SE, headline interval [+0.0088, +0.0173] (in Sec. 5); image-bootstrap check on VG150 (1,000 replicates): SE/SD 0.97 but coverage of the full-sample value 88%, attributed to duplicated images forming zero-kernel pairs; reported as such in App. C, no claim of certified nominal coverage. |
| R5-12 | Wording route | Sec. 5 states that a per-class bias cannot absorb a pair-varying shift and that ranking is read from the AUC alone; no pair-indexed family added. |
| R5-13 | Wording route | Single released run stated in the abstract, Table 1 caption and limitations. |
| R5-14 | Done | PE-Net (prototype-based, CVPR 2023) released PredCls checkpoint re-run on Colab, evaluator reproduces the published R@50 0.6523 / mR@50 0.3142; against the separately trained MOTIFS baseline its mR@50 gain is 86% group-level, case-level +0.0243 [+0.0197, +0.0289], and its within-cell AUC rises (+0.0050 [+0.0008, +0.0091] relation-weighted, +0.0187 per pair). New Table 1 row, Sec. 5 paragraph, App. `app:penet`. Deviation: relation NMS evaluated with a row-blocked re-implementation (memory), identical on 300 images. |
| R5-15 | Done | Waterbirds contrast in Sec. 6 (group reweighting: worst-group accuracy 0.643 to 0.854, case-level +0.0914, AUC +0.0031). |
| R5-16 | Done | `experiments/sgg_auc_label_ambiguity.py`, App. `app:ambiguity`: synonym merging leaves TDE's null and IETrans's loss in place; IETrans's loss concentrates in within-synonym-group pairs (-0.0177 vs -0.0071). |
| R5-17 | Done | SQUAT, VRT and arXiv 2503.17862 cited; the control is distinguished from that paper's inverse-frequency logit scaling. App. `app:zeroshot` compares the split with head/body/tail and zero-shot recall: tiers cannot tell TDE from the control; zero-shot recall can (+0.033 vs -0.004), and its case-level part over the control (+0.0131) comes with an AUC that falls on unseen-triplet comparisons (-0.0149 [-0.0203, -0.0056]). |
| R5-19 | Done | PredCls in the abstract's first sentence; SGDet matched fraction (65%) and a selection-effect note. |
| R5-20 | Done | Declaration timing stated (post hoc for TDE and IETrans); multiplicity sentence pointing to the all-configurations table. |
