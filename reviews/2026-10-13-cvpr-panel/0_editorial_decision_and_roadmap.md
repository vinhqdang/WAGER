# Editorial Decision Package

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

`criteria_binding_unavailable`: no target-criteria binding was supplied and all five cards disclose this. No venue-alignment claim is made. The standard Synthesis Protocol was used (no sprint contract), so no scoring matrix or failure-condition arithmetic applies.

Same-model-family panel: all five Phase 1 seats ran on one model family (Sonnet) from one provider, and this synthesis is by the same family. Agreement among seats is weaker evidence than agreement among independent reviewers, and repeated findings may reflect one shared reading of the same passage. Full provenance is in `_panel_provenance.md`. Because of this limit, the claims that decide the outcome were recomputed (section "Verification").

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Venue configuration**: simulated CVPR 2027 panel (configured perspective only)
- **Review target**: `cvpr2027/paper.pdf` (8 pp + references) and `cvpr2027/supp.pdf` (36 pp), commit `18a72c9`
- **Decision date**: 2026-10-13
- **Review round**: 1 (mode full, Phase 2)

## Review Panel Provenance (summary)

Five role-separated seats (EIC, R1, R2, R3, DA), each a fresh subagent run on Sonnet launched concurrently by an Opus orchestrator, no peer visibility, no prior-panel visibility, single provider, `NOT_CALIBRATED`. Phase 0 cards carried over unchanged from the 2026-10-05 panel. Accountable human: Quang-Vinh Dang (British University Vietnam). No typed `review-panel-provenance/1.0` artifact or digests were supplied, so none are reported. Axes: role-separated true; within-panel invocation-context separation true (scope `within_panel_attempt_only`); blind to peer outputs true; model-family distinct **false**; provider distinct **false**; human-reviewer distinct false. No binary independence claim is made. No cross-model decision check was run.

---

## Decision

### Major Revision

**Confidence in the decision: high for the category, medium for how large the revision is.** All four scoring seats independently recommend Major Revision. Two of them call it borderline (R1, R3) and one says borderline with Minor on content (EIC). The Devil's Advocate raised 0 CRITICAL issues. The decision-bearing items can be repaired by re-analysis and narrower wording, not by a redesign, so Reject is not warranted. It is not Minor Revision because at least two items need new analysis (R4-7 same-image sensitivity, R4-8 proper-score protocol), not text alone.

Editorial lines for the sprint/audit trail:
- `da_critical_adjudications: []` (0 DA CRITICAL issues; the DA card's CRITICAL table is empty and states no single defect met the singleton bar)
- `editorial_decision=major_revision`

---

## Verification (read-only recomputation of the claims that decide the outcome)

No file other than the two deliverables was modified. A scratch script was kept outside the repository.

| # | Claim | Source seat | Status | How |
|---|---|---|---|---|
| (a) | 33% of audited relations share image and identical boxes with another relation in the same cell | R1 W1 | **Verified (prevalence). Effect on estimates NOT verified.** | Counted from `data/vg_motifs/wager_sgg/meta.npz` (183,642 relations): 60,811 relations (33.11%) share image, both boxes and class-pair cell with another relation; 60,813 (33.11%) share image and boxes regardless of cell (R1 states 60,813 / 33.1%). 58.72% have a same-image same-cell partner; 0.474% of ordered same-cell pairs are same-image; 5,044 cells with at least two relations cover 98.87%. These match R1. R1's consequence (other-image transport moves the raw case-level part by +0.0020, about 9%) requires the transport variant and was not re-run here. |
| (b) | Removing TDE's frequency prior gives a positive case-level part of about +0.008 under the primary temperature + per-class-bias protocol, leaving AUC unchanged | DA M2 | **Verified** | Re-ran the repository's own `fit_family`/`apply_family`/`decompose_gain` on `variant_vis_ctx` vs `variant_none` (3 missing-pair rows dropped as the repository loader does), the repository's own splits (seeds 1000-1002), quadratic score. Primary protocol case-level: +0.00773 [+0.00714, +0.00833], +0.00792 [+0.00735, +0.00850], +0.00795 [+0.00737, +0.00854]. Temperature-only: +0.00878, +0.00881, +0.00903. All three equal DA's +0.0077 to +0.0080 and +0.0088 to +0.0090. AUC change for this step, from `results/sgg_tde_path.json`: +0.0000556, 95% CI [-0.0000377, +0.000145]. Arithmetic: +0.0079 / +0.00445 = 1.8 times TDE's whole primary case-level part (the +0.00445 value is the paper's, quoted by R1/R3/DA; not recomputed here). Limit: the step compares two different models (`vis_ctx` vs `none`), and the "pair-indexed, constant within cell" property of the frequency branch rests on the paper's own description (Tab. 22 and Appendix O.1), not on a code check by me. |
| (c) | Comparison-weighted AUC equivalence fails | EIC, R1, R2, R3, DA | **Verified** | `results/sgg_equivalence.json`, TDE vs none. Relation-weighted: difference -0.00148, 90% CI [-0.00373, +0.00077], margin 0.00626, `equivalent: true`. Comparison-weighted: difference +0.00261, 90% CI [-0.00218, +0.00739], margin 0.00323, MDE(80%) 0.00815, `equivalent: false`; the MDE is 2.5 times the margin, so the test cannot support equivalence under that weighting. TDE vs la1 shows the same split. |

Further checks made because they bear on the arbitration:
- R1 W7 (inconsistent intervals): **verified**. In the same file, relation-weighted TDE vs none has 95% interval [-0.003603, +0.001752] but 90% interval [-0.003726, +0.000768]; the 90% lower bound lies below the 95% lower bound, which cannot hold for nested intervals of one method. The verdict is unchanged for the relation-weighted case (still inside +-0.00626).
- DA M5 (protocol dependence of "nine of ten"): **verified** from `results/sgg_recall_split_TDE_vs_la1.json`. TDE minus LA total: -0.0234 (graph-constrained K=20), +0.0031 (K=50), +0.0300 (K=100); without graph constraint -0.0792, -0.1272, -0.1549. Case-level part without graph constraint at K=100: +0.0148 [+0.0064, +0.0232].
- Grouping dependence (EIC W3, R1, R2, R3, DA M3): **verified** from `results/sgg_grouping_share.json`. Class pair: group 0.0841 of 0.0972 (86.6%), case 0.0130. Subject class only: group 0.0175 of 0.0970 (18.1%), case 0.0794. Class pair x position: group share about 90%.
- CLIP vs geometry weighting (R3 W3(iii) and DA m5 look inconsistent but are both right): **verified** from `results/vg_visual_seeds.json`. Matched case-level part is positive with interval above zero in all five seeds (+0.00413 to +0.00474). The comparison-weighted AUC difference is positive in all five seeds (+0.0048 to +0.0156) but its interval excludes zero only in seed 3.
- DLFE (R2 W1, DA m1): **verified as stated**. `experiments/run_sgg_dlfe_audit.py` and the DLFE Colab scripts exist; `results/` holds no DLFE result file and `data/vg_motifs/` has no `wager_dlfe` directory. Why the run was dropped cannot be told from the repository.
- Headline arithmetic (EIC, R1, R2, R3 all recomputed): 0.0841/0.0972 = 86.5%, LA 0.0941 of 0.0972, TDE minus LA +0.0031, case-level TDE vs LA -0.0008 [-0.0050, +0.0033]. I re-read the relevant JSON fields and found no discrepancy.

Not verified by me (taken from the cards, with the seat named in the roadmap): R1's other-image transport effect and synthetic coverage (92.0%), the 20-half calibration stability, proofs, checkpoint replay, SGCls/SGDet inline replay, CIFAR/Waterbirds/CLIP training results, reference lists (R2's missing-reference leads are marked UNVERIFIED by R2 except FGPL, which R2 reports verifying by search), and whether the equivalence margin was fixed before the data (nobody can tell from the artifacts, and this is itself a finding).

---

## Blocking Issues (3, immutable source order)

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| B1 | Method-level and field-level claims (TDE, IETrans, "the field's metrics", benchmark recommendation) rest on two single-run released checkpoints of one architecture, with IETrans compared to a separately trained baseline | EIC, R1, R2, R3, DA | text: Sec. 7 "On two released Neural-Motifs checkpoints on Visual Genome the gains are almost entirely group-level"; text: Sec. 5 "does not isolate the effect of relabelling" | R4-1, R4-2 |
| B2 | The ranking-null and "confidence, not ranking" readings are stated more firmly than the evidence: equivalence holds under one of two AUC weightings, the margin is unjustified and unverifiable as pre-declared, and the primary matching protocol leaves +0.0079 of case-level part from a ranking-preserving step | EIC, R1, R2, R3, DA | dataset: `results/sgg_equivalence.json` comparison `equivalent: false`, MDE 0.00815 vs margin 0.00323; dataset: re-run of `variant_vis_ctx` vs `none`, primary protocol, +0.0077 to +0.0080 | R4-5, R4-6, R4-8 |
| B3 | Interval validity for the small effects the conclusions rest on is untested under same-image and identical-input dependence (33.1% of relations) | R1 | dataset: `data/vg_motifs/wager_sgg/meta.npz` 60,811 relations share image, boxes and cell; text: Theorem 3 (supp. B.5) "when the cell's examples are drawn i.i.d. from the cell population" | R4-7 |

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence (self-reported scope disclosure) | Questions | Minor issues |
|---|---|---|---|---|---|
| Journal-Fit Reviewer (EIC) | CVPR area-chair perspective, evaluation and scene understanding | Major Revision (borderline Minor on content) | 4 | 4 | 5 |
| Reviewer 1 | Methodology: proper scores, U-statistics, equivalence testing | Major Revision (borderline) | 4 | 5 | 4 |
| Reviewer 2 | Domain: scene graph generation, unbiased SGG | Major Revision (borderline accept if scope narrowed or audit extended) | 4 | 6 | 5 |
| Reviewer 3 | Perspective: long-tail, shift, shortcut evaluation | Major Revision (borderline; would move to Minor/Accept with reframing) | 3 | 5 | 6 |
| Devil's Advocate | Fixed adversarial seat | N/A, findings only | per-finding | n/a | 6 minor, 7 major, 0 critical |

Confidence values are disclosures only and were not used to weigh, count or resolve anything.

Key strengths agreed across seats: exact identity confirmed (R1 brute force, 21 tests pass); evaluator replay to four decimals (R2, R3); the logit-adjustment operating-point control (all four); negative controls that can fail (R1, R3); candour about fragility (all four); every number traces to committed JSON (all four, no arithmetic discrepancy found by any seat or by me).

---

## Step 1b: Weakness Sub-Claim Inventory

Severity is transported from the seat's per-finding tag. Positions: R = raised, C = corroborated, N = not-mentioned (silence, not opposition), D = disputed. "p" marks a partial mention. DA is tracked separately and is not counted in the 4.

| SC | Sub-claim | Parent weaknesses | EIC | R1 | R2 | R3 | DA | Transported severity |
|---|---|---|---|---|---|---|---|---|
| SC-1 | Claims about methods and the field outrun two single-run checkpoints of one architecture on one dataset | EIC W1; R1 W3; R2 W1; R3 W5 | R | C | R | R | M4 | Major (all) |
| SC-2 | No training-seed variance for baseline/TDE; intervals cover test sampling only | R1 W3; R2 W1 (suggestion), Q2; R3 (ethics note) | N | R | C | C | M4 | Major (R1, R2); not tagged (R3 detail) |
| SC-3 | Abstract/conclusion state equivalence without naming the relation-weighted AUC; comparison-weighted test fails (MDE 0.0082 > margin 0.0032) | EIC W3; R1 W2; R2 W6; R3 W3; DA M1 | R | R | C | R | M1 | Major (EIC, R1, R3, DA); Minor (R2) |
| SC-4a | Equivalence margin is arbitrary, borrowed from other models/split, outcome-referenced; no sensitivity to the 1/10 | R1 W2; R2 W6; R3 W3; DA M1 | Np (lists margin among protocol choices) | R | R | R | M1 | Major (R1, R3, DA); Minor (R2) |
| SC-4b | "Fixed in advance" cannot be verified from the artifacts | R1 W2(c); R2 W6, Q5; R3 W3, Q3; DA | N | R | R | R | dim 3 | Major (R1, R3); Minor (R2) |
| SC-4c | 90% TOST interval inconsistent with the 95% interval (Wald from back-solved SE) | R1 W7 | N | R | N | N | N | Minor (verified) |
| SC-5 | Headline 87% is conditional on the declared class-pair grouping (18% subject-only, 90% with position/size); abstract does not carry it; no rule fixes the grouping | EIC W3; R1 detail; R3 W2; DA M3 | R | C | N (praises candour) | R | M3 | Major (EIC, R3, DA) |
| SC-6a | 87% and the "ten points" are micro-pooled (+0.0972) vs official per-image (+0.1017); not stated at point of use | R1 W5; R2 W5; R3 W6; DA m4 | N | R | R | R | m4 | Minor (R1, R2, R3, DA) |
| SC-6b | "Nine of ten points" / 87% hold for graph-constrained K=50 only; other protocols disagree (K=20, K=100, no-graph) | R1 W6; R2 W5; R3 W3(iv); DA M5 | N | R | R | C | M5 | Minor (R1, R2); Major (DA) |
| SC-7a | Proper-score case-level +0.0045 as "confidence, not ranking" is protocol-dependent (+0.00445 / -0.00006 / -0.0184), indirectly inferred | EIC W3; R1 W4; R3 W4; DA M2 | R | R | N | R | M2 | Major (EIC, R1, R3, DA) |
| SC-7b | Matching is fitted on test labels (no held-out split); calibration-fit uncertainty not propagated | R1 W4; R3 W4; DA m2 | N | R | N | R | m2 | Major (R1, R3); Minor (DA) |
| SC-7c | Primary family does not remove a ranking-preserving pair-indexed shift (dropping the frequency prior scores +0.0077 to +0.0080) | DA M2 (R1 W4 states the limit: no per-class family removes a model-specific within-cell confidence pattern) | N | C | N | N | M2 | Major (DA); verified |
| SC-8 | IETrans comparison confounded (separately trained baseline, Rwt loss); method-level wording unsupported; share CI exceeds 100% | EIC W1; R1 W3; R2 W4; R3 W5; DA M6 | R | C | R | R | M6 | Major (R2, R3, DA); within Major bundles (EIC, R1) |
| SC-9 | SGCls/SGDet split covers only matched pairs (58%/65%); abstract "99%" and the SGCls AUC sentence overreach | R2 W3; R3 Q5/minor; DA m3 | N | N | R | C | m3 | Major (R2); Minor (R3, DA) |
| SC-10 | "What did ten points buy" reads as a verdict although group-level gain is what mean recall rewards by design | R2 W2; R3 W1; DA dim 1 | N | N | R | R | dim 1 | Major (R2, R3) |
| SC-11 | Group/case reading depends on the label mix; the label-mix path (Q.3) is only in the supplement | R3 W1; DA counter-argument | N | N | N | R | C | Major (R3) |
| SC-12 | i.i.d. assumption violated by same-image and identical-input pairs (33.1% of relations); interval and unbiasedness untested for it | R1 W1, W9 | N | R | N | N | N | Major (R1); prevalence verified |
| SC-13 | Case-level naming and the `reasoning_gain` field name imply reasoning though the part credits shortcuts | R3 W2(b), minor | N | N | N | R | N | Major bundle (R3 W2); naming part not separately tagged |
| SC-14 | DLFE audit code in the repository, no result reported | R2 W1, Q1; DA m1 | N | N | R | N | m1 | Major bundle (R2 W1); Minor (DA) |
| SC-15 | Related-work gaps, F@K source, typos (garbled "to, at 0.016", "one..", back-reference lists "3, 2") | EIC W6; R2 W8; R3 minor; DA m6 | R | N | R | R | m6 | Minor (all) |
| SC-16 | Body too dense, load-bearing evidence in supplement; benchmark recommendation arrives late | EIC W4 | R | N | N | N | N | Major (EIC) |
| SC-17 | Proposed reporting standard needs dense scores; no minimal tier | R2 W9; R3 W7 | N | N | R | R | N | Minor (R2, R3) |
| SC-18 | Mechanism claim rests on correlation 0.75 with the log prior | R1 W10 | N | R | N | N | N | Minor |
| SC-19 | Many protocols/weightings, no confirmatory-vs-exploratory labelling or multiplicity accounting | R1 W6; R3 W3(iv); DA M1, M5 | N | R | N | R | C | Minor (R1); Major (R3 W3 bundle) |
| SC-20 | Randomization p-values ignore image clustering; sharp null | R1 W8 | N | R | N | N | N | Minor |
| SC-21 | Within-pair label ambiguity (near-synonyms) may cap case-level signal; ceiling not estimated | R2 W2; R3 assumption audit; DA M7 | N | N | R | C | M7 | Major (R2 bundle); DA conf. 3 |
| SC-22 | Novelty of the SGG finding limited; contributions should lead with decomposition; no case where the split changes a published ranking | EIC W2; R2 summary/overclaiming; DA M7 | R | N | C | N | M7 | Major (EIC) |
| SC-23 | "Beyond scene graphs" paragraph has no body numbers; cross-domain support is for estimator behaviour only | EIC W5; R3 W5 | R | N | N | C | N | Minor (EIC) |
| SC-24 | CLIP vs geometry ranking verdict flips with AUC weighting; stated firmly in the intro | R1 W4; R3 W3(iii); DA m5; R2 W7 | N | C | C (demote to supp) | R | m5 | Minor (DA, R2); inside Major bundles (R1, R3) |
| SC-25 | Single-reviewer minor: mean-recall margin is 75% of TDE's whole case-level part | R1 W2(b) | N | R | N | N | N | Major bundle (R1 W2) |

Decomposition discipline: every sub-claim above is split from a weakness a seat actually wrote. No sub-claim was introduced by the synthesizer.

## Step 2: Consensus Analysis

### Points of Agreement (Consensus)

**[CONSENSUS-4]** (EIC, R1, R2, R3 all agree, no conflict)
1. SC-1 (scope): claims outrun two single-run released checkpoints of one architecture. EIC W1, R1 W3, R2 W1, R3 W5; the DA's M4 corroborates. The remedies differ (extend the audit or narrow the wording) but are alternatives, not opposites; see arbitration A2.
2. SC-8 (IETrans): the comparison is against a separately trained baseline and the checkpoint adds a reweighted loss, so IETrans-specific or relabelling claims are unsupported. EIC W1, R1 W3, R2 W4, R3 W5; DA M6 corroborates.
3. SC-3 (equivalence stated under one weighting only): EIC W3, R1 W2, R2 W6, R3 W3. Verified (c). DA M1 corroborates.

**[CONSENSUS-3]** (three agree, the fourth silent; no seat disputes)
4. SC-4a (margin arbitrary or unjustified): R1, R2, R3; EIC silent on the margin's arbitrariness (it lists the margin among protocol choices only). DA M1 corroborates.
5. SC-4b ("fixed in advance" unverifiable): R1, R2, R3; EIC silent.
6. SC-5 (headline conditional on declared grouping): EIC, R1, R3; R2 silent as a weakness (R2 praises the candour). DA M3 corroborates. Verified.
7. SC-6a (micro-pooled vs official): R1, R2, R3; EIC silent. DA m4 corroborates.
8. SC-6b (protocol dependence of the headline): R1, R2, R3; EIC silent. DA M5 corroborates. Verified.
9. SC-7a (+0.0045 "confidence, not ranking" overread): EIC, R1, R3; R2 silent. DA M2 corroborates.
10. SC-2 (no training-seed variance): R1, R2, R3; EIC silent. DA M4 corroborates.
11. SC-15 (related work, F@K, typos): EIC, R2, R3; R1 silent. DA m6 corroborates.

### Corroborated findings (2 seats, no conflict; below the consensus bar)
SC-7b (test-label calibration; R1, R3; DA m2); SC-9 (SGCls/SGDet subset; R2, R3; DA m3); SC-10 (normative reading; R2, R3; DA dim 1); SC-17 (adoption cost; R2, R3); SC-19 (forking paths; R1, R3; DA); SC-21 (label ambiguity ceiling; R2, R3; DA M7); SC-22 (novelty; EIC, R2; DA M7); SC-23 (beyond-SG; EIC, R3); SC-24 (CLIP weighting; R1, R3, with R2 W7 in a related direction, see arbitration A5).

### Single-reviewer findings (retained, no consensus label)
SC-4c (R1, verified); SC-11 (R3; DA corroborates); SC-12 (R1; prevalence verified); SC-13 (R3); SC-14 (R2; DA m1; existence verified); SC-16 (EIC); SC-18 (R1); SC-20 (R1); SC-25 (R1). SC-7c is a DA finding (R1 W4 states the same limit in general terms); I re-ran it and it reproduces.

### DA CRITICAL adjudication

There are **0 DA CRITICAL issues** (the CRITICAL table in `5_devils_advocate_review.md` is empty, with a stated reason). Nothing to validate, reject or leave unresolved, and no `[DA-CRITICAL-VS-ACCEPT]` condition arises. The DA's seven MAJOR issues (M1 to M7) and six MINOR issues were treated as findings tracked outside the 4-seat consensus count, and each is routed to a roadmap item below. DA M2 and M5 were recomputed and reproduce; M7 is a DA-confidence-3 reasoning item with no new data and is handled as should_fix/consider.

## Points of Disagreement and Arbitration

**A1. Is the case-level evidence a text problem or an analysis problem?** (severity/remedy disagreement)
- R3: borderline; would move to Minor/Accept if the abstract and Sec. 7 are brought in line with results the supplement already contains.
- R1, R2, EIC: new analysis is needed (R1: other-image transport, margin grid, seeds; R2: DLFE or another method, IETrans control; EIC: breadth of audit).
- **Resolution**: Major Revision stands. **Rationale**: evidence first. R3's text fixes are necessary (R4-1, 3, 4, 5, 9) but not sufficient, because two decision-bearing points reproduce only by re-analysis: the pair-indexed shift under the primary protocol (verified, +0.0079 with AUC +0.00006) and same-image dependence (prevalence verified at 33.1%). Expertise: methodology items defer to R1, which also holds the recompute.

**A2. Remedy for scope: extend the audit or narrow the claims?** (direction disagreement on remedy, not on existence)
- EIC: add released baseline/debiased pairs, or retitle and frame as method plus case study. R2: report DLFE, add one architecture-changing method, or retitle. R1: retrain seeds, or rephrase to the released checkpoint. R3: limit the conclusion; add checkpoints if public.
- **Resolution**: the minimum obligation is narrowing (R4-1, must_fix). Extension (seeds, a second method) is should_fix (R4-11) and is the author's choice. **Rationale**: author autonomy; the four seats' remedies are alternatives, and the evidence-supported floor is the same for all of them. If the author keeps the field-level benchmark recommendation, extension becomes the only evidence-based route, and the author should say which route was chosen.

**A3. Severity of the protocol/estimand qualifications (SC-6a, SC-6b)** (severity disagreement)
- R1 W5/W6, R2 W5 and R3 W6 rate Minor. DA M5 rates Major.
- **Resolution**: the wording fix is must_fix (R4-4); the added sensitivity analyses are should_fix (R4-22). **Rationale**: evidence first. The DA's numbers are verified (TDE minus LA -0.0234 at K=20, +0.0300 at K=100, -0.1272 at no-graph K=50), and the paper's Table 2 already reports them, so this is a disclosure problem fixable in one sentence, not a defect in the analysis. Cheap to fix and a reader who stops at the abstract is misled, hence the must_fix on wording only.

**A4. Does the framing ("what did ten points buy") need to change?** (perspective difference)
- R2 W2 and R3 W1 call the framing normative and in tension with what mean recall rewards; the DA's dimension-1 judgement agrees. EIC calls the title "memorable and accurate about the question" while also saying it promises more than two checkpoints show.
- **Resolution**: no seat argues the framing is harmless, so the EIC statement is recorded as a difference of emphasis, not a dispute. Must_fix is text only (R4-9): state in abstract and Sec. 1 that group-level gain is what mean recall rewards by design, and carry the label-mix conditioning. Whether the title changes is left to the author. **Rationale**: the paper's own Sec. 5 sentence "Group-level is not a lesser gain" already concedes the point; the title and intro should not imply otherwise.

**A5. Role of the CLIP-versus-geometry study** (direction disagreement)
- EIC: the freshest empirical contribution; lead with it (W2 suggestion, S4). R3 S6: useful illustration. R2 W7: an MLP-on-embeddings probe, not an SGG system; move to the supplement or repeat with MOTIFS branches.
- **Resolution**: keep it as a controlled illustration, neither promote it to lead contribution nor demote it. Must-do (should_fix R4-14) is to state the ranking verdict with its weighting: matched case-level part positive in all five seeds (verified), relation-weighted AUC favours geometry (-0.0067), comparison-weighted AUC favours CLIP in all five seeds but with an interval excluding zero in one (verified). **Rationale**: evidence first. Promotion by EIC would rest on the part of the result that flips with weighting; demotion by R2 undervalues the five-seed case-level result. Not resolved on the placement question; left to the author.

**A6. Unresolved dissent.** Whether the equivalence margin and "primary" weighting were fixed before the TDE AUC was seen cannot be resolved from the artifacts (R1 W2(c), R2 W6, R3 W3). The panel does not resolve it. The author must either supply a dated artifact or describe the margin as a sensitivity choice (R4-6). Whether the "confidence, not ranking" reading is true for TDE is also left unresolved: the evidence does not show it and does not refute it (R4-8).

---

## Decision Rationale

Four seats recommend Major Revision, none disputes another's finding, and the DA found no CRITICAL defect. The core is sound: the identity is exact (R1 brute force), every checked number traces to committed results (all seats, and my re-reads), and the logit-adjustment operating-point control is a real contribution. What fails is the distance between what is measured and what is stated. The equivalence headline holds for one of two AUC weightings, and the comparison-weighted test cannot detect an effect of 0.0082 against a margin of 0.0032 (verified). The margin has no outcome-independent justification and cannot be shown to be pre-declared. The 87% share depends on the declared grouping (18% to 90%), the protocol (K=50, graph constraint, micro-pooled), and the label mix. The proper-score "confidence, not ranking" reading is the weakest point: the primary matching protocol, justified by a criterion that a ranking-preserving within-cell shift leaves no case-level part, still returns +0.0077 to +0.0080 when TDE's frequency prior is removed with no AUC change (verified), about 1.8 times TDE's whole primary part. Separately, a third of relations share image and boxes with another relation (verified), which the unbiasedness and interval claims do not address. The generalisation from two single-run checkpoints, one with a confounded baseline, to the field and to a benchmark standard is agreed by all four. I chose Major over Minor because two items need new analysis, and Major over Reject because each item is repairable by re-analysis or narrower claims. The paper's candour about its limits is a reason to expect a clean revision.

---

## Part 2: Revision Roadmap

> IDs `R4-n` are transport references in immutable source-traceability order (first source seat in panel order EIC, R1, R2, R3, DA, then within-card order). They are not a work rank. The obligation class is an editorial gate. Severity and confidence are transported from the driving finding (never re-derived). `proposed_targets`: unavailable, because no bound block manifest for the manuscript was supplied; targets are given as sections. Consequence codes are from the roadmap schema's closed set. Author triage is not collected here.

### Required Revisions (Must Fix)

| Ref | Revision item (fix) | Sub-claims | Severity (transported) | Evidence anchor | Confidence (transported) | Source seats | Obligation | Cost scope | Consequence if unaddressed |
|---|---|---|---|---|---|---|---|---|---|
| R4-1 | Restate title/abstract/conclusion/benchmark recommendation as claims about the audited checkpoints (two released Neural-Motifs checkpoints, VG150, PredCls plus a TDE-only SGCls/SGDet replication). Remove "the field's metrics report the sum" and present the reporting standard as a proposal. | SC-1 | Major | text: Sec. 7 "we audit no later method" | EIC 4, R1 4, R2 4, R3 4, DA 5 | EIC, R1, R2, R3, DA | must_fix | section: abstract, Sec. 1, Sec. 7 | claim_scope_unsupported: Sec. 7 |
| R4-2 | Mark IETrans as uncontrolled (separately trained baseline, Rwt loss) in Table 1 and the abstract; drop "IETrans's lowers it" and relabelling or mechanism wording, or train a matched baseline; state that the share interval [0.90, 1.04] exceeds 100%. | SC-8 | Major | text: Sec. 5 "does not isolate the effect of relabelling"; dataset: `results/sgg_share_intervals.json` ietrans share_ci [0.9017, 1.0436] | EIC 4, R1 4, R2 4, R3 4, DA 5 | EIC, R1, R2, R3, DA | must_fix | sentence: abstract, Table 1, Sec. 5 (new data only if a matched baseline is trained) | claim_scope_unsupported: Table 1 |
| R4-3 | Carry the grouping dependence where the 87% is stated: give 87% (class pair), 18% (subject class) and about 90% (pair x position/size) side by side with coverage, and state the rule that fixes the grouping without reference to the outcome. | SC-5 | Major | dataset: `results/sgg_grouping_share.json` (0.866 / 0.181 / 0.897) | EIC 4, R3 4, R1 4 (detail), DA 5 | EIC, R1, R3, DA | must_fix | section: abstract, Sec. 5 table | claim_scope_unsupported: abstract |
| R4-4 | Qualify "87%" and "nine of the ten points" at point of use as graph-constrained, K=50, micro-pooled (+0.0972, official per-image +0.1017); add the TDE-minus-LA totals for all six protocols (K=20 -0.0234, K=100 +0.0300, no-graph -0.0792/-0.1272/-0.1549). Say how a share reads when the total is near zero or negative. | SC-6a, SC-6b | Minor (R1, R2, R3); Major (DA M5) | dataset: `results/sgg_recall_split_TDE_vs_la1.json` gc@20, gc@100, ng@50 | R1 3, R2 4, R3 3, DA 5 | R1, R2, R3, DA | must_fix | sentence: abstract, Sec. 1, Sec. 5; one table row set | claim_scope_unsupported: abstract |
| R4-5 | State in abstract and Sec. 5/7 that TDE's ranking is equivalent to baseline's under the relation-weighted AUC (90% CI [-0.0037, +0.0008] inside +-0.0063) and is not established under the comparison-weighted AUC (MDE 0.0082 > margin 0.0032). | SC-3 | Major (EIC, R1, R3, DA); Minor (R2) | dataset: `results/sgg_equivalence.json` TDE vs none comparison `equivalent: false` | EIC 4, R1 4, R2 3, R3 4, DA 4 | EIC, R1, R2, R3, DA | must_fix | sentence: abstract, Sec. 5, Sec. 7 | claim_scope_unsupported: abstract |
| R4-6 | Margin: justify 1/10 from a quantity internal to the MOTIFS audit or decision-relevant (not from the MLP probe), show the verdicts over a margin grid (for example 5%, 10%, 25%), give the mean-recall case-level margin as a fraction of its own total (0.0097 vs 0.0130, about 75%), either supply a dated artifact or drop "fixed in advance", and report the 90% interval from the same bootstrap draws as the 95% (current 90% lower bound -0.00373 lies below the 95% lower bound -0.00360). | SC-4a, SC-4b, SC-4c, SC-25 | Major (R1, R3, DA); Minor (R2, R1 W7) | text: `experiments/sgg_equivalence.py` header "(R3-2)"; dataset: `results/sgg_equivalence.json` | R1 4, R2 3, R3 4, DA 4, R1 W7 5 | R1, R2, R3, DA (EIC partial) | must_fix | re_analysis: `experiments/sgg_equivalence.py`, Sec. 5 | method_reproducibility_unresolved: Sec. 5 |
| R4-7 | Same-image and identical-input dependence: report the split with transport restricted to other-image labels (and identical-input partners excluded) for the matched +0.0045, the 87% share and the intervals; run a coverage simulation built from the real cell sizes, image multiplicities and duplicate boxes. Report results whichever way they fall. | SC-12 | Major | dataset: `meta.npz` 60,811 of 183,642 relations share image, boxes and cell; text: Theorem 3 i.i.d. condition | R1 4 | R1 | must_fix | re_analysis: `wager/antisymmetric.py` estimator variant, Appendix J | method_reproducibility_unresolved: Appendix J |
| R4-8 | Proper-score reading: either add a pair-indexed (cell-wise, shrunk) matching family or run the Appendix Q.4 simulation with a cell-indexed offset, and report TDE's residual; test "confidence, not ranking" directly (for example a within-cell monotone, case-dependent rescaling); otherwise remove the sentence from the abstract. Present +0.00445 beside -0.00006 and -0.0184, and rest the main-text TDE conclusion on rank-based quantities. | SC-7a, SC-7c | Major | dataset: re-run `variant_vis_ctx` vs `none`, primary protocol, +0.00773/+0.00792/+0.00795; dataset: `results/sgg_tde_path.json` AUC +0.0000556 | EIC 4, R1 3, R3 3, DA 4 | EIC, R1, R3, DA | must_fix | re_analysis: `experiments/run_sgg_rank_robustness.py`, Sec. 5, Appendix Q.4 | interpretive_ambiguity_remains: abstract |
| R4-9 | Reframe: state that group-level gain is what mean recall rewards by design and that the split describes the VG150 label mix and matched protocol; move one label-mix-path figure (Q.3: share and case part against mix for TDE, LA, IETrans, CLIP vs geometry) into the body. Title wording is the author's choice. | SC-10, SC-11 | Major | text: Sec. 5 "Group-level is not a lesser gain"; dataset: `results/label_shift.json` TDE vs MOTIFS case -0.00006 to +0.01430 | R2 4, R3 4 | R2, R3, DA | must_fix | section: abstract, Sec. 1, Sec. 5, one figure | interpretive_ambiguity_remains: abstract |
| R4-10 | State the matched fraction (58% SGCls, 65% SGDet) wherever "99% group-level" appears; restrict the SGCls "ranking gets worse" sentence to the relation-weighted AUC (comparison-weighted -0.0047 [-0.0122, +0.0031]). | SC-9 | Major (R2); Minor (R3, DA) | dataset: `results/sgg_sgcls_audit.json` matched_fraction 0.5823, share_group 0.9852 | R2 3, R3 3, DA 5 | R2, R3, DA | must_fix | sentence: abstract, Sec. 5 | claim_scope_unsupported: abstract |

### Suggested Revisions (Should Fix / Consider)

| Ref | Revision item (fix) | Sub-claims | Severity | Source seats | Obligation | Cost scope | Consequence |
|---|---|---|---|---|---|---|---|
| R4-11 | Extend the evidence: retrain baseline and TDE over a few seeds and report the spread of the split and AUC change, and/or audit one released post-2022 baseline/debiased pair. If the benchmark recommendation stays, this becomes the route that supports it. | SC-1, SC-2 | Major | R1, R2, R3, EIC, DA | should_fix | new_data: training runs or released checkpoints | evidence_gap_remains: Sec. 5 |
| R4-12 | Report the DLFE audit or state why it was dropped; otherwise remove `run_sgg_dlfe_audit.py` and the DLFE Colab scripts from the archive. (Verified: script exists; no result file and no `wager_dlfe` data directory.) | SC-14 | Major bundle (R2); Minor (DA) | R2, DA | should_fix | sentence: Sec. 7 or supplement | reader_traceability_reduced: archive |
| R4-13 | Calibrate on a held-out split (not the audit's test images) as the primary matching protocol, with the test-half variant secondary; propagate calibration-fit uncertainty by cross-fitting. | SC-7b | Major (R1, R3); Minor (DA) | R1, R3, DA | should_fix | re_analysis: Sec. 3, Appendix Q.1 | method_reproducibility_unresolved: Sec. 3 |
| R4-14 | Give the CLIP-vs-geometry ranking verdict with its weighting (relation -0.0067 favours geometry; comparison +0.0085 seed 0, positive in five seeds, interval excludes zero in one). Keep it as a controlled illustration and say it is not an SGG system. | SC-24 | Minor | R1, R2, R3, DA | should_fix | sentence: Sec. 1, Sec. 6 | interpretive_ambiguity_remains: Sec. 6 |
| R4-15 | Label analyses as confirmatory or exploratory, state the family of tests behind the headline, and add one summary table of all weighting/protocol combinations for TDE vs baseline. | SC-19 | Minor (R1); Major bundle (R3) | R1, R3, DA | should_fix | section: Sec. 5 table | reporting_requirement_unmet: Sec. 5 |
| R4-16 | Surface the predicate-merge analysis (`results/predicate_merge.json`) and discuss near-synonym label ambiguity as a ceiling on within-pair signal. | SC-21 | Major bundle (R2) | R2, R3, DA | should_fix | section: Sec. 5 or Sec. 7 | interpretive_ambiguity_remains: Sec. 7 |
| R4-17 | Reduce density: move one worked example and the operating-point control into a single figure, cut secondary numbers (seeds, label-shift path) to the supplement with one sentence each, define r/c/ng-mR/LA in captions, move the reporting recommendation earlier. | SC-16 | Major | EIC | should_fix | section: Sec. 4-7, Tables 1-2, Figs. 1 and 3 | reader_traceability_reduced: Sec. 5 |
| R4-18 | Reorder contributions to lead with the decomposition and where aggregates mislead; state the credit to Yates [46] and to [6, 42] where the logit-adjustment result first appears. | SC-22 | Major | EIC, R2, DA | should_fix | section: Sec. 1 | acceptance_criterion_unmet: Sec. 1 |
| R4-19 | For SGCls/SGDet, report the split on all relations with predicted-pair grouping as a sensitivity. | SC-9 | Major (R2) | R2 | should_fix | re_analysis: Sec. 5, Table 35 | evidence_gap_remains: Sec. 5 |
| R4-20 | Update related work (R2's leads, of which only FGPL was reported verified by R2; the rest UNVERIFIED), cite the F@K source, fix typos ("to, at 0.016", "one..", back-reference lists for [14] and [38]). | SC-15 | Minor | EIC, R2, R3, DA | should_fix | sentence: Sec. 2, Sec. 5, Sec. 6, references | editorial_conformance_unmet: manuscript |
| R4-21 | Define a minimal reporting tier (top-k logits, one grouping, operating-point control, relation-weighted AUC) and say what it loses. | SC-17 | Minor | R2, R3 | should_fix | section: Sec. 7 | reporting_requirement_unmet: Sec. 7 |
| R4-22 | Add a per-image official-statistic sensitivity (for example image-weighted pooling) beside each split. | SC-6a | Minor | R1, R2, R3 | should_fix | re_analysis: Sec. 5 | evidence_gap_remains: Sec. 5 |
| R4-23 | Give one headline number per extra domain in the body for the "beyond scene graphs" paragraph, or cut it. | SC-23 | Minor | EIC, R3 | consider | sentence: Sec. 6 | claim_scope_unsupported: Sec. 6 |
| R4-24 | Rename "case-level" to "within-group covariance" in the main text and drop `reasoning_gain` from result files, since the part credits shortcuts. | SC-13 | Major bundle (R3 W2) | R3 | consider | other: text and result-file keys | interpretive_ambiguity_remains: Sec. 7 |
| R4-25 | Permute at the image level or drop randomization p-values from the main text. | SC-20 | Minor | R1 | consider | sentence: Sec. 4, Appendix N.2 | reporting_requirement_unmet: Appendix N.2 |
| R4-26 | Regress the shared TDE vector on the log prior, report the residual, and show its effect on the split. | SC-18 | Minor | R1 | consider | re_analysis: Sec. 5 | interpretive_ambiguity_remains: Sec. 5 |
| R4-27 | Estimate a label-agreement ceiling (multi-annotator subset or human check of within-pair flips) and report the share against it. | SC-21 | Major bundle (R2) | R2, DA | consider | new_data: annotation | evidence_gap_remains: Sec. 7 |
| R4-28 | Add one case where the split changes a published method ranking or conclusion. | SC-22 | Major (EIC) | EIC | consider | re_analysis: Sec. 5 | acceptance_criterion_unmet: Sec. 1 |

### Source-Traceability Checklist (source order, not a work order)

- [ ] R4-1 must_fix: narrow scope claims to the audited checkpoints
- [ ] R4-2 must_fix: IETrans marked uncontrolled, method-level wording removed
- [ ] R4-3 must_fix: grouping dependence carried at the 87% claim
- [ ] R4-4 must_fix: protocol and estimand qualification of 87% and "nine of ten"
- [ ] R4-5 must_fix: equivalence stated with its weighting
- [ ] R4-6 must_fix: margin justification, grid, pre-declaration, 90% interval
- [ ] R4-7 must_fix: same-image / identical-input sensitivity and coverage
- [ ] R4-8 must_fix: pair-indexed matching family or drop the "confidence" sentence
- [ ] R4-9 must_fix: reframe group-level reading, label-mix figure in body
- [ ] R4-10 must_fix: SGCls/SGDet matched-fraction qualifier
- [ ] R4-11 to R4-22 should_fix; R4-23 to R4-28 consider (as in the table)

### Editor's priority view (advisory; not part of the immutable core)

Requested prioritisation, ordered by decision weight and by how much each unblocks. The author may order differently.
1. R4-8 (verified, decides the proper-score reading; needs analysis)
2. R4-6 (margin; blocks the equivalence claim)
3. R4-5 (wording; one sentence, verified)
4. R4-1 (scope; all four seats)
5. R4-7 (same-image sensitivity; the only unexamined validity threat to the intervals)
6. R4-2 (IETrans; all four seats)
7. R4-3 (grouping)
8. R4-4 (protocol and estimand)
9. R4-9 (framing and label-mix figure)
10. R4-11 (seeds or second method; decides whether the benchmark recommendation can stay)

### Response Letter Template
Use `templates/revision_response_template.md` to respond to every item R4-1 to R4-28, including a stated decision for each should_fix and consider item. Where the author declines an item, say so; a decline stays visible and unresolved.

---

## Part 3: Reviewer Report Summary (Appendix)

- **Journal-Fit Reviewer (EIC)**: Major Revision | Confidence 4. Question and numbers are sound; scope (two checkpoints), novelty and density are the concerns. Strongest sub-claims: SC-1, SC-5, SC-7a, SC-16.
- **Reviewer 1 (Methodology)**: Major Revision | Confidence 4. Identity and estimator correct; same-image dependence, margin design, single checkpoint and the proper-score reading are overstated. Strongest: SC-12, SC-4a/b, SC-7a.
- **Reviewer 2 (Domain)**: Major Revision | Confidence 4. Clean replay; narrow SGG scope, IETrans confound, SGCls/SGDet subset, normative framing. Strongest: SC-1, SC-8, SC-9, SC-10.
- **Reviewer 3 (Perspective)**: Major Revision | Confidence 3. Interpretation depends on label mix, grouping and test-label calibration; the decomposition and control are praised. Strongest: SC-5, SC-7b, SC-10, SC-11.
- **Devil's Advocate**: findings only. Key challenge: the case-level part is not what the paper names it for (M2 verified, M5 verified); no unresolved Critical challenge.

## Closing

We invite a substantially revised manuscript that addresses the ten required items and states a decision on each suggested item. The revised version will need another review. The audit is careful and candid; the revision is mostly about making the abstract and conclusion say what the evidence supports, plus two pieces of re-analysis (R4-7, R4-8).

*Synthesis scope note: this letter synthesizes and arbitrates the five Phase 1 reports; it adds no new review comments. The recomputations above were used only to adjudicate claims the seats made.*

## Status after the revision pass (2026-10-13)

| item | status |
|---|---|
| R4-8 proper-score reading | **Done.** "Confidence, not ranking" removed. New check: removing TDE's frequency prior (AUC change +0.00006) gives +0.00817 [+0.00757, +0.00877] under temperature + per-class bias, so ranking is read from the within-cell AUC only (Sec. 5, App. Q). |
| R4-6 margin | **Done.** Fixed-margin claim replaced by the largest change each 90% percentile interval excludes (0.0034 relation, 0.0077 comparison); 5/10/25% margin grid in the supplement; "fixed in advance" removed; the 90% intervals are now percentile intervals from the same bootstrap, nested in the 95% ones. |
| R4-5 both weightings | **Done** in abstract, intro, Sec. 5 and conclusion. |
| R4-1 scope | **Done.** Abstract names the two Neural-Motifs PredCls checkpoints; conclusion says "mean recall reports the sum" and "we audit no later method"; recommendations narrowed. |
| R4-7 same-image pairs | **Done.** `cross_image_split` (transport only across images, image jackknife), reviewed; no sign or verdict changes (App. on calibration halves). |
| R4-2 IETrans | **Done.** "Against a separately trained baseline" in abstract, intro, Sec. 5, conclusion; method-level wording removed. |
| R4-3 grouping dependence | **Done.** 87% / 90% / 18% stated in Sec. 5 at the headline; abstract names the class-pair grouping. |
| R4-4 qualifiers | **Done.** Abstract says graph-constrained, micro-pooled, @50; Sec. 5 gives TDE-minus-LA over all six protocols. |
| R4-9 reframe / label mix | **Done (text).** Abstract states the case-level part grows under a uniform label mix; label-mix figure not moved into the body (page limit). |
| R4-10 SGCls qualifier | **Done** (matched fraction and comparison-weighted AUC in Sec. 5). |
| R4-11 seeds / second method | **In progress.** DLFE (released baseline + debiased pair) running on Colab; training seeds not possible for released checkpoints — stated as a limitation. |
| R4-13 held-out calibration | **Limitation stated** (no validation outputs released). |
| R4-20 related work | **Partly done.** FGPL cited; F@K attributed to IETrans. |
| R4-12 DLFE | **In progress** (see R4-11). |
| R4-14..R4-28 others | Not done in this pass unless listed above. |

## Status after the should-fix pass (2026-10-13, later)

| item | status |
|---|---|
| R4-13 held-out calibration | **Done as cross-fitting** (no validation outputs were released): halves swapped and averaged; TDE primary-protocol case part +0.00399 [+0.00334, +0.00463]; IETrans +Rwt −0.01723 [−0.01817, −0.01630]. Sec. 5 and supplement. |
| R4-14 CLIP framing | **Done.** Called a controlled illustration, not an SGG system; ranking verdict stated per weighting. |
| R4-15 confirmatory/exploratory | **Done.** Two primary quantities named in Sec. 5 (graph-constrained mR@50 split, relation-weighted AUC); everything else secondary, collected in a supplement table of every protocol/weighting/score. |
| R4-16 predicate merge | Already surfaced in Sec. 5 (one sentence) with the synonym/coarse merges and single-annotation subset in the supplement. |
| R4-17 density | **Partial** (abbreviations defined in captions; further moves blocked by the 8-page limit). |
| R4-18 contributions and credit | **Done.** Decomposition first, credited to Yates; logit-adjustment result credited to [6, 42] where it first appears. |
| R4-19 predicted-pair grouping | **Done (argument).** Matching requires both labels to equal the ground truth, so predicted-pair and ground-truth-pair grouping coincide on matched relations; unmatched relations have no predicted pair. |
| R4-20 related work and typos | **Done** (FGPL, F@K source, "to, at 0.016" fixed). |
| R4-21 minimal tier | **Done** (conclusion). |
| R4-22 official per-image statistic | **Done.** Split by within-cell label shuffles: TDE 84% group-level, case +0.0168 [+0.0111, +0.0226]; TDE vs control +0.0026 [−0.0028, +0.0080]; a floor-weight shortcut reverses the sign (−0.0216) and is reported as such. |
| R4-11 / R4-12 DLFE | **In progress** on Colab. |

## DLFE (R4-11 / R4-12), 2026-10-13

**Done.** The released MOTIFS-DLFE checkpoint and the MOTIFS baseline it was trained against (one recipe, so the comparison is controlled) were re-run on Colab and re-scored on the same 183,642 relations; replayed recall equals the evaluator's to float precision. DLFE vs its baseline: mR@50 +0.1112 = +0.1046 group-level (94%) + +0.0065 [+0.0010, +0.0120] case-level; within-cell AUC +0.0029 [−0.0004, +0.0056] relation-weighted, +0.0018 [−0.0041, +0.0064] by comparison. The test-time correction is exactly ranking-preserving (AUC change 0 vs the uncorrected network). Added to abstract, intro, Sec. 5 and Table 1, and a supplement subsection. The audit now covers three released checkpoints; seeds remain impossible for released checkpoints (stated as a limitation).
