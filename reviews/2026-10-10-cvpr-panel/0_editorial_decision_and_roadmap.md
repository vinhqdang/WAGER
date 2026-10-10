# Editorial Decision Package

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

`criteria_binding_unavailable`: no author-confirmed target context was bound to any seat, so this package makes no venue-alignment claim. "CVPR 2027" is a configured perspective. The sprint-contract arithmetic mode was not in force (no contract bound), so the standard Synthesis Protocol was used. No cross-model blind decision check was run.

All five seats share one model family and one provider with the orchestrator. See "Panel provenance" below and `_panel_provenance.md`. Agreement among the five seats is therefore not independent confirmation, and the consensus counts here must be read with that in mind.

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting "What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation" (CVPR 2027 simulated submission, anonymous; commit 9dad949; paper.pdf 8 pp + references, supp.pdf 36 pp). It was reviewed by five role-separated seats (Journal-Fit/EIC, R1 methodology, R2 domain, R3 perspective, Devil's Advocate).

### Decision: Major Revision

Simulated CVPR reading: borderline, weak-accept conditional on repair. Reject is not supported by any seat.

Decision confidence: medium-high. All four scoring seats independently recommend Major Revision, and no seat recommends Reject or a lighter outcome. The confidence is capped because the five seats are same-family. It is also capped because the proofs, coverage simulations and model re-execution were not re-run by any seat.

### Manuscript recomputation record (editor, read-only)

I recomputed the following from `results/*.json`. The working tree has later uncommitted edits, which I ignored, and I did not open `results/sgg_oracle_headroom.json`.

| # | Claim | Source file | Recomputed | Status |
|---|---|---|---|---|
| V1 | TDE vs LA1 case-level part, no graph constraint, mR@20/50/100 | `sgg_recall_split_TDE_vs_la1.json` `ng@*` | +0.0013 [-0.0035, +0.0060]; +0.0072 [-0.0001, +0.0145]; +0.0148 [+0.0064, +0.0232] | Verified. Only mR@100 excludes zero, and mR@50 misses by 0.0001. |
| V2 | Same comparison, graph-constrained | same, `gc@*` | +0.0013, -0.0008 [-0.0050, +0.0033], +0.0034 (all CIs cover 0) | Verified. 5 of 6 point estimates are positive, and the headline -0.0008 is the only negative cell (R3 W1c, DA M2). |
| V3 | IETrans AUC intervals (Table 1) | `sgg_rank_robustness.json` `sgg_auc` | comparison-weighted -0.0093 [-0.0181, +0.0004]; relation-weighted -0.0235 [-0.0275, -0.0182] | Verified. Only the relation-weighted interval excludes 0. |
| V4 | IETrans mR@50 case-level part | `sgg_recall_split_ietrans_vs_none.json` | +0.0060 [-0.0031, +0.0151] | Verified. The sign is positive and the interval covers 0. |
| V5 | 87% share and CI | `sgg_share_intervals.json` | TDE 0.8657 [0.8256, 0.9058]; LA 0.8524; IETrans 0.9727 [0.9017, 1.0436] | Verified. The IETrans upper bound exceeds 1. |
| V6 | TDE vs baseline mR@50 split | `sgg_recall_split.json` `gc@50` | total 0.09715 = group 0.08411 + case 0.01305 [0.00926, 0.01684] | Verified |
| V7 | Official vs pooled mR@50, graph vs no graph | same, `gc@50` / `ng@50` | official 0.1459 to 0.2476 (+0.1017) vs pooled +0.0972. Without the graph constraint, official mR@50 falls from 0.3260 to 0.2981 and the pooled total is -0.0337 (group -0.0464, case +0.0127). | Verified. The "ten points" and the 87% exist only under the graph constraint, so the share is undefined without it (R1 W2, R2 W4, R3 W7). |
| V8 | TDE vs LA1 within-cell AUC | `sgg_auc_tde_la.json` | +0.00255 [-0.0029, +0.0086] (comparison); -0.00183 [-0.0039, +0.0014] (relation); audit half changes sign | Verified |

I did not re-verify these items. They stay as seat-reported only:
- the DA's k=20 "77%" share figure (DA M2);
- Table 11 CIFAR means (R3 reproduced them; I did not);
- the Table 32, 28 and 29 protocol rows;
- the proofs;
- the coverage simulations;
- the same-image sibling counts (R1 R6).

### Consensus Analysis

Consensus is computed per sub-claim (Step 1b inventory, Appendix A) over the four non-DA seats, with `not-mentioned` read as silence and never as agreement.

#### Points of Agreement

- **[CONSENSUS-4] IETrans abstract wording and confound (SC-1, SC-2).** The abstract's "loses within-pair discrimination under every measure" is stronger than Table 1, and the baseline mismatch is not stated in the abstract. Seats: EIC W2, R1 W6, R2 W2, R3 W4. DA M4 corroborates. Verified in V3, V4 and V5.
- **[CONSENSUS-4] "No change in TDE's within-pair ranking" is a non-detection (SC-3).** There is no equivalence margin or minimum detectable effect, and the evidence depends on weighting, protocol and mix. Seats: EIC W3, R1 W2, R2 W3, R3 W1. DA M3 corroborates. Verified in V8 for the intervals.
- **[CONSENSUS-3] Evidence breadth is two MOTIFS-family checkpoints and a further audit of a different family is needed (SC-6a).** Seats: EIC W1, R2 W1, R3 W4. R1 is silent on breadth. DA M4 corroborates.
- **[CONSENSUS-3] Graph/no-graph and six protocol/k cells should sit in the main text (SC-4).** Seats: R1 W2, R2 W4, R3 W1(ii) and Q3. EIC is silent. DA M2 corroborates. Verified in V1, V2 and V7.
- **[CONSENSUS-3] AUC weighting must be pre-specified and both weightings reported (SC-10).** Seats: R1 W6, R2 W3, R3 W1 and W4. EIC is silent on this sub-claim. Verified in V3 and V8.
- **[CONSENSUS-3] Protocol dependence of the proper-score case-level part needs an ex-ante primary protocol or hierarchy (SC-9).** Seats: R1 W1, R3 W5, EIC W3. R2 is silent. DA M1 corroborates.
- **[CONSENSUS-3] No reference or positive control shows the split can return a large case-level share (SC-8).** Seats: R2 W5, EIC W1 (why-it-matters passage), R3 W2 (partial: "close to guaranteed by construction" for TDE). R1 is silent. DA M5 corroborates. R3's corroboration is about mechanism, not about a missing control, so treat it as partial.
- **[CONSENSUS-3] Presentation density and appendix dependence (SC-17).** Seats: EIC W5, R2 (Layout), R3 (Layout). R1 raises only table-labelling items.

Corroborated findings (2 non-DA seats, below the consensus bar):

- **SC-7: headline share is conditional on one grouping.** Seats: R1 W5, R3 W2. DA M6 corroborates. Both Major.
- **SC-12: CLIP "not better ranking" is applied asymmetrically.** Seats: R3 W3, R1 W6 (CLIP part). EIC notes the CLIP tie to the central claim is "indirect".
- **SC-14: normative reading of "group-level" is not argued.** Seats: R2 W6, R3 W6. DA m3 corroborates. Both Minor.
- **SC-18a: the report needs full-score archives most benchmarks lack.** Seats: EIC W6, R3 W5.

Single-reviewer findings (retained, not consensus): SC-13 interval validity and nuisance variance (R1 W4); SC-16 matched-subset fraction in SGCls/SGDet (R2 W7); SC-19 name "WAGER" in the supplement (EIC Layout); SC-21 proper score on TDE logits (R1 W9); SC-22 image-level permutation test (R1 W8); SC-23 zero-shot and F@K split (R2 W6, Q1).

#### Points of Disagreement (each is a SPLIT under precedence rule 1)

**Disagreement 1: Is the title/abstract/conclusion scope wording acceptable? (SC-6b)**
- **EIC W1, R2 W1, R3 W4 (DA M4):** the title, abstract and conclusion ("debiasing methods", "the field's metrics report the sum") generalise from two checkpoints.
- **R1 (Detailed Comments, Research Questions):** the main-text conclusions "are scoped as 'audits of two released checkpoints', which is the right scope". R1 does not raise breadth as a weakness.
- **Type:** severity/perspective difference. R1's remark concerns the audit statement in the research question, not the title, abstract or conclusion wording the others quote.
- **Resolution:** the EIC/R2/R3 reading is upheld. Evidence first: the quoted abstract and conclusion text is verbatim in EIC and R2. R2 holds the domain expertise on SGG breadth. R1's remark does not address those passages, so it is a narrower, compatible statement rather than a rebuttal.
- **Remedy:** author's choice. Either add audits (R3-6) or rescope the title, abstract and conclusion to the two checkpoints. The two remedies are compatible, so the author may pick either route.

**Disagreement 2: Graph-constraint presentation, Major or Minor? (SC-5b)**
- **R2 W4 (Major) and DA M2 (Major):** the ten points flip sign without the graph constraint, so the title question is partly a graph-constraint question.
- **R3 W7 (Minor):** protocol should be stated; no change to the finding.
- **R1 W2 (inside a Major):** the share is undefined without the graph constraint.
- **Type:** severity.
- **Resolution:** Major, and it merges into the main-table item R3-3. Recomputation V7 shows that without the graph constraint the total is -0.0337 and the TDE vs LA1 case part is positive at mR@100 (V1). Evidence outweighs the Minor rating.
- **Remaining dissent:** R3 rated the micro-vs-official labelling alone as Minor. That stays Minor and is carried as part of R3-3.

**Disagreement 3: Micro-averaged vs official mR (SC-5a)**
- **R2 W4 (bundled in a Major):** the official metric has no decomposition and no uncertainty on the 4.5% gap.
- **R1 W7, R3 W7, DA m1/m2 (Minor):** label the share and the "nine of ten points" claim with the statistic used.
- **Type:** severity.
- **Resolution:** Minor. V7 confirms the 0.0972 vs 0.1017 gap. A labelling fix plus a bootstrap bound is sufficient. It is folded into R3-3 as a sub-item.

**Disagreement 4: Beyond-SGG paragraph and CIFAR/text studies, Major or Minor? (SC-11)**
- **R1 W3 (Major):** the CIFAR-100-LT result contradicts the paper's own control logic. LA's matched covariance (+0.0324) exceeds DRW's (+0.0195) but DRW is called "genuine per-instance discrimination". The grouping is label-derived.
- **R3 W8 (Minor):** the studies are demonstrations under a different estimand and should be labelled.
- **EIC W5 (Minor):** give them a table or remove the paragraph.
- **Type:** severity.
- **Resolution:** split by obligation. A wording fix is must-fix: relabel as a different estimand and remove "genuine discrimination" unless the part exceeds the LA control. This is a sentence/section edit, backed by R1's methodology remit and by R3's independent reproduction of the Table 11 means. A re-run with temperature + class-bias matching and more seeds is should-fix (S item).
- **Not verified by the editor:** the Table 11 numbers themselves.

**Disagreement 5: Novelty/literature gap, Major or Minor? (SC-15)**
- **EIC W4 (Major):** novelty beyond known prior-correction results is argued thinly; related work is dated.
- **R2 W8 (Minor):** add a known-vs-new sentence.
- **DA m4 (Minor):** the contribution is the split, not the TDE finding.
- **Type:** severity.
- **Resolution:** Should-fix. EIC and R2 both mark their recall of missing literature as unverified, so a Major rating cannot rest on it. The known-vs-new sentence has corroboration from three seats and is cheap, so it is carried in R3-13. Of R2's missing-reference leads, only OvSGTR was marked verified; the F@K source is unlocated and all other leads are search leads only.

**Disagreement 6: Practicality of the reporting protocol (SC-18)**
- **EIC W6 (Minor):** archive requirements; adoption is aspirational.
- **R3 W5 (Major):** no adjudication rule when outputs disagree in sign; grouping is selectable.
- **Type:** severity, but the sub-claims differ. SC-18a (archive) is EIC and R3; SC-18b (no decision rule) is R3 only, with overlap from R1 W1 suggestion (b).
- **Resolution:** SC-18b is merged into R3-4 (must-fix: a hierarchy for contradictory signs, which R1 and R3 both propose in compatible form). SC-18a is should-fix (R3-15).

**Disagreement 7: Is the CLIP study a clever demonstration or an inconsistent one? (SC-12)**
- **EIC (Results):** "a clever demonstration" whose tie to debiasing is indirect.
- **R3 W3 and R1 W6:** the two AUC weightings disagree in sign, so "real covariance, not better ranking" is not established.
- **Type:** perspective difference.
- **Resolution:** both readings stand. The invariant AUC does not rank CLIP last, which R3 shows. R1's own recomputation R5 shows the CLIP covariance advantage survives temperature + class-bias matching, shrinking about 30%. So the covariance finding survives while the "not better ranking" wording does not. Must-fix wording (R3-10), should-fix ablations (R3-18).

#### DA CRITICAL adjudication

There are 0 DA CRITICAL findings. The DA's CRITICAL table contains a single row stating that no defect was found that invalidates the core claim, and the DA recomputed Table 1 successfully.

`da_critical_adjudications: []`

All six DA MAJOR items (M1 to M6) are corroborated by at least one scoring seat and are mapped in Appendix A.

### Decision Rationale

The core contribution is sound and valuable. The exact split is correct in the seats' checks and reproduces from committed results, with all 423 printed numbers traced (EIC and R1 logs), and I confirmed the headline numbers in V5 and V6. The operating-point control is the paper's most transferable idea. Unanimous strengths across seats are the reproducibility, the candour about limits, and the TDE audit with the replayed evaluator.

The panel's concern is what the evidence licenses. First, two headline sentences exceed the tables: IETrans "under every measure" and TDE's ranking "unchanged". Both are non-detections, and the IETrans comparison is confounded by a separately trained baseline. Second, the TDE case-level part is protocol-determined, and the primary protocol is the one the paper's own simulation shows to be inadequate (R1 W1). Third, the headline "ten points" and the 87% share exist under the graph constraint only (V7), and the five of six positive TDE-vs-control cells in V1 and V2 are not visible in the main table. Fourth, scope is two MOTIFS-family checkpoints, one grouping and no positive control.

Each problem is repairable. Most need re-analysis of cached outputs or rewording, not new training. A Major Revision, not Minor, is warranted because several of the repairs change headline sentences and the main-text table, and because the scope and grouping questions (R3-6 to R3-8) require analysis or an explicit rescoping that a reviewer should see. Reject is not warranted: no seat found a defect in the algebra or the reproducibility, and the DA found nothing CRITICAL.

### Blocking Issues (immutable source order)

| Transport ref | Blocking issue | Source seat(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| B1 | IETrans abstract claim exceeds Table 1 and rests on a non-isolating baseline | EIC, R1, R2, R3, DA | table: Table 1 IETrans row (case +.0060 [-.0031,+.0151]; ∆AUCc -.0093 [-.0181,+.0004]); verified V3, V4 | R3-1 |
| B2 | "No change in TDE ranking" is non-detection with no equivalence margin; protocol-, weighting- and mix-dependent | EIC, R1, R2, R3, DA | table: Table 1 TDE ∆AUCc +.0026 [-.0028,+.0086]; verified V8 | R3-2 (with R3-4) |
| B3 | Evidence base is two MOTIFS-family checkpoints while title, abstract and conclusion speak for "debiasing methods" and "the field's metrics" | EIC, R2, R3, DA | text: Abstract and Conclusion; absence: audit of any non-MOTIFS or post-2022 method | R3-6 |

---

## Part 2: Revision Roadmap

The `R3-n` ids are transport references, and the table is ordered by editorial priority at the editor's request. `Obligation` is the editorial gate and is separate from severity. Severity and per-finding confidence are transported unchanged from the cards. "Panel" means every non-DA seat that raised the sub-claim. All cost scopes are typed and none is a time estimate. `A` is the Appendix A sub-claim id. Proposed block targets are not enumerated, because no block manifest was bound.

### Required Revisions (Must Fix)

| Ref | Revision item | A | Severity | Evidence anchor | Conf. | Source seat | Obligation | Cost scope | Consequence |
|---|---|---|---|---|---|---|---|---|---|
| R3-1 | Reword the IETrans claim in abstract, Sec. 5 and conclusion. List the measures that exclude zero (relation-weighted AUC; matched proper scores) and those that do not. Name the IETrans+Rwt variant and the separately trained, different-fusion baseline in the abstract or Sec. 1. Cap or explain the share CI above 100%. | SC-1, SC-2 | major (EIC, R1, R2, R3) | text: Abstract "under every measure"; table: Table 1 IETrans; verified V3-V5 | EIC 4; R1 4; R2 4; R3 4 | EIC, R1, R2, R3 (DA M4) | must_fix | sentence + section (abstract, Sec. 5, Sec. 7) | claim_scope_narrowed: IETrans |
| R3-2 | Replace "unchanged / no measure detects" with a bounded statement. Pre-declare an equivalence margin or report a minimum detectable effect (AUC and case-level mR), under both weightings and at the uniform mix, anchored to a reference effect such as geometry vs class-only (+0.0323). Soften the Sec. 5 heading "What that licenses". | SC-3 | major (EIC, R1, R2, R3) | table: Table 1 TDE AUC columns; Supp. Tables 29, 30; verified V8 | EIC 3; R1 4; R2 4; R3 4 | EIC, R1, R2, R3 (DA M3) | must_fix | re_analysis (cached) + sentence | claim_scope_narrowed: TDE ranking |
| R3-3 | Put the six TDE-vs-LA1 mR cells (graph and no-graph, k = 20/50/100) and the no-graph baseline rows in the main text. State in the abstract and Sec. 5 that the "ten points" and 87% are graph-constrained, micro-averaged mR@50, and that official mR@50 falls without the graph constraint. Bound the micro-vs-official 4.5% gap (image bootstrap or per-predicate application). Use one statistic for "nine of ten points". | SC-4, SC-5a, SC-5b | major (R2, DA); minor (R1, R3) | text: Sec. 5 "mean recall falls, from 0.3260 to 0.2981"; Supp. Table 17; verified V1, V2, V7 | R1 4; R2 4; R3 4 | R1, R2, R3 (DA M2, m1, m2) | must_fix | section (Table 1, Sec. 5) + sentence | claim_scope_narrowed: protocol |
| R3-4 | State an ex-ante rule for the primary calibration protocol in Sec. 3 (the family that returns zero for a ranking-preserving class-wise shift, i.e. temperature + per-class bias). Show all families in Fig. 2. Add a protocol-envelope or spread statement. Give a reporting hierarchy for when signs disagree: the operating-point-matched comparison as primary, AUC with equivalence bounds as the invariant check, the other parts as diagnostics. Do not use the proper-score case-level part as inferential evidence for or against discrimination when protocols disagree in sign. | SC-9 | major (R1, R3); EIC lists protocol dependence under W3 | table: Supp. Table 32 TDE vs base quadratic (-0.00006 / -0.01839 / +0.00445); Table 26 | R1 4; R3 3; EIC 3 | R1, R3, EIC (DA M1) | must_fix | section + re_analysis (cached) | claim_scope_narrowed: case-level part |
| R3-5 | Pre-specify one primary AUC weighting, justified in SGG terms, and report the other as secondary wherever either is quoted. Give both in the abstract for SGCls, IETrans and CLIP-vs-geometry. | SC-10 | major (R1, R2, R3) | table: Supp. Table 34 SGCls -.0047 vs -.0128; Table 1; verified V3 | R1 4; R2 4; R3 4 | R1, R2, R3 (DA M1) | must_fix | sentence + table columns | claim_scope_narrowed: AUC claims |
| R3-6 | Resolve scope (author's choice of route). Route A: audit at least two further released methods of different families, one not prior-indexed (and a post-2022 or open-vocabulary SGG model where released), with the same split, control and AUC. Route B: retitle and rescope the abstract and conclusion to "two released MOTIFS-family checkpoints" and relabel Sec. 7 as a proposal. | SC-6a, SC-6b | major (EIC, R2, R3) | text: Contributions (i); Abstract; Conclusion; absence: non-MOTIFS audit | EIC 4; R2 5; R3 4 | EIC, R2, R3 (DA M4); R1 disputes SC-6b wording only | must_fix | new_data (Route A) or section (Route B) | claim_scope_narrowed: field-level |
| R3-7 | Add a headroom or positive control. Carry a model with a visual or geometry term (and, if feasible, an oracle bound) into the mean-recall split under the graph constraint, so the reader can tell whether 87% is a finding about TDE or a property of VG150 plus mR@50. | SC-8 | major (R2, DA); EIC W1 why-it-matters | table: Supp. Table 19 baseline AUC 0.5705; results/sgg_rank_robustness.json | R2 3; EIC 4 | R2, EIC, R3 (partial) (DA M5) | must_fix | re_analysis or new_data | evidence_added |
| R3-8 | Report the mean-recall share under at least two finer groupings (class pair x geometry bin; class pair x image-level feature) with a sensitivity band (Proposition 4 adapted to the hit contrast). Put the grouping into the abstract claim, and state that "case-level" means within-φ covariance, not "visual". Rewrite the contributions clause that the split "separates shortcut effects". | SC-7 | major (R1, R3) | table: Supp. Table 9, Table 3 (ρ† = 0.061); App. K | R1 3; R3 4 | R1, R3 (DA M6) | must_fix | re_analysis (cached) + sentence | evidence_added |
| R3-9 | Relabel the CIFAR-100-LT, 20 Newsgroups and Waterbirds material as demonstrations under a different estimand (label-derived grouping). Remove "genuine per-instance discrimination" and "LA changes rankings" unless stated for the part exceeding the LA control, and say which Sec. 3 and Sec. 5 statements do not transfer. | SC-11 | major (R1); minor (R3, EIC) | table: Supp. Table 11 (DRW +0.0195, LA +0.0324); text: Supp. N.5 | R1 4; R3 4; EIC 4 | R1, R3, EIC | must_fix | sentence + section | claim_scope_narrowed: beyond-SGG |
| R3-10 | Qualify Sec. 6, "The model every metric ranks last". Apply one pre-declared ranking criterion to TDE and CLIP alike, and state that the two AUC weightings disagree in sign for CLIP vs geometry. | SC-12 | major (R3, R1) | text: Sec. 6 "real covariance, not better ranking"; Supp. Table 25, Table 30 | R3 4; R1 4 | R3, R1 | must_fix | sentence | claim_scope_narrowed: CLIP |

### Suggested Revisions (Should Fix / Consider)

| Ref | Revision item | A | Severity | Evidence anchor | Conf. | Source seat | Obligation | Cost scope | Consequence |
|---|---|---|---|---|---|---|---|---|---|
| R3-11 | Isolate relabelling by training a matched baseline with the IETrans data pipeline (or the internal-transfer, external-transfer and Rwt-only variants). | SC-2 | major (EIC, R2, R3) | text: Sec. 5 "does not isolate the effect of relabelling" | EIC 4; R2 4; R3 4 | EIC, R2, R3 (DA M4) | should_fix | new_data | evidence_added |
| R3-12 | Interval validity. Add coverage simulations for the mR hit contrast and the share interval, use 1,000+ bootstrap replicates, and combine calibration-half variance with sampling variance. State that checkpoint-level inference is conditional on the released weights. | SC-13 | major (R1) | table: Supp. Table 26 (SD 0.00055); Table 4 | R1 4 | R1 | should_fix | re_analysis | evidence_added |
| R3-13 | Add a known-vs-new sentence (prior correction rivals debiasing is known: [6], [28], [42]). Update related work with post-2022 SGG evaluation and debiasing. Cite the F@K source and OvSGTR (ECCV 2024, verified to exist by R2). Other leads, including R3's cross-disciplinary references, are UNVERIFIED search leads and must be checked before use. | SC-15 | major (EIC); minor (R2, DA) | absence: Sec. 2 post-2022 SGG evaluation | EIC 3; R2 3 | EIC, R2 (DA m4) | should_fix | section | evidence_added |
| R3-14 | State what the paper argues is wrong with group-level gains (informativeness vs bias), separating "metric is gameable by prior shift" from "the gain has no worth". Add the zero-shot (zR@K) and F@K split with the same estimator. | SC-14, SC-23 | minor (R2, R3) | text: Sec. 1 "What did those ten points buy?"; Supp. O zR@50 0.110 to 0.143 | R2 4; R3 3 | R2, R3 (DA m3) | should_fix | sentence + re_analysis | claim_scope_narrowed |
| R3-15 | Specify a minimal archive format and a reduced "lite" report computable from top-k outputs, or say the recommendations apply to future submissions. | SC-18a | minor (EIC); major (R3 W5, which also holds SC-18b) | text: Sec. 7 "most benchmarks archive only ranked top-k predictions" | EIC 4; R3 3 | EIC, R3 | should_fix | section | claim_scope_narrowed |
| R3-16 | State the matched-pair fraction (58% SGCls, 65% SGDet) wherever an SGCls or SGDet AUC or proper-score number appears in the main text. Report selection sensitivity. | SC-16 | minor (R2) | text: Supp. Q.5; results/sgg_sgcls_audit.json | R2 4 | R2 | should_fix | sentence | evidence_added |
| R3-17 | Presentation. Move one-line definitions of the matching families, weightings and control into the main text. Split the AUC columns of Table 1. Make Figs. 2 and 3 legible at print size. Say whether Fig. 3 uses pooled or per-image recalls. | SC-17 | minor (EIC, R2, R3) | figure: Figure 1 caption; Figure 3 | EIC 4 | EIC, R2, R3 | should_fix | section | none |
| R3-18 | CLIP ablations: dimension-matched head (PCA to 64 d), context-masked crop control, and temperature + bias matching. R1's own check R5 reports the CLIP advantage shrinks about 30% under temperature + bias but survives. | SC-12 | major (R3) | text: Sec. 6; R1 recomputation R5 | R3 4 | R3 (R1 R5) | should_fix | new_data | evidence_added |
| R3-19 | CIFAR-100-LT and 20 Newsgroups: apply temperature + per-class-bias matching and within-superclass AUC, compare each method's covariance with the LA control, and add seeds. | SC-11 | major (R1) | table: Supp. Table 11 | R1 4 | R1 | should_fix | re_analysis + new_data | evidence_added |
| R3-20 | Anonymity check. The supplement uses the project name "WAGER" (Appendix B.4); replace it with neutral wording in the supplement and shipped archive. Confirm before submission. | SC-19 | minor (EIC) | text: Supp. Appendix B.4 | EIC 3 | EIC (R2 notes the name as terminology) | should_fix | sentence | none |
| R3-21 | Per-predicate coverage of excluded singleton relations, and a share sensitivity to the 4.5% micro/official difference. | SC-5a | minor (R1) | text: Sec. 5; R1 recomputation R7 | R1 4 | R1 | consider | re_analysis | none |
| R3-22 | State the background-column handling and renormalisation for TDE proper scores, and discuss what "proper score" means for logit differences. | SC-21 | minor (R1) | table: Supp. Table 20 | R1 3 | R1 | consider | sentence | none |
| R3-23 | Report p as "p <= .002", permute at the image level, and add a robustness row excluding same-image pairs. | SC-22 | minor (R1) | text: Sec. 4 "p = .002" | R1 3 | R1 | consider | re_analysis | none |
| R3-24 | Consistency tidy. Table 4 vs Sec. 4 (96.2% vs 96.3%). Eq. 27 vs Table 3 (0.01427 vs 0.01439). Fig. 3 quotes 0.886/0.558 against official 0.862/0.531. Bibliography back-reference pages point into the supplement, and [34] has none. State the alternative in p-value table captions. | — | minor (R1, R2, R3, EIC) | text: Supp. Table 4, Table 3; Fig. 3 | R1 4; R2 4; R3 4; EIC 4 | R1, R2, R3, EIC | consider | sentence | none |

### Source-Traceability Checklist

- [ ] R3-1 (must_fix): IETrans claim and baseline disclosure
- [ ] R3-2 (must_fix): equivalence margin or MDE for TDE non-detection
- [ ] R3-3 (must_fix): main-text protocol table and abstract protocol disclosure
- [ ] R3-4 (must_fix): ex-ante calibration protocol rule and reporting hierarchy
- [ ] R3-5 (must_fix): primary AUC weighting
- [ ] R3-6 (must_fix): breadth or rescope (author's route)
- [ ] R3-7 (must_fix): headroom or positive control
- [ ] R3-8 (must_fix): grouping sensitivity
- [ ] R3-9 (must_fix): relabel beyond-SGG studies
- [ ] R3-10 (must_fix): CLIP claim wording
- [ ] R3-11 to R3-20 (should_fix) and R3-21 to R3-24 (consider)

### Required Item Details

**R3-1: IETrans claim**
- **Problem**: the abstract says IETrans "loses within-pair discrimination under every measure", but the mR case-level part is +0.0060 [-0.0031, +0.0151] and the comparison-weighted AUC change is -0.0093 [-0.0181, +0.0004]. Only the relation-weighted AUC and the matched proper scores exclude zero.
- **Source**: EIC W2, R1 W6, R2 W2, R3 W4, DA M4; recomputed V3 to V5.
- **Requirement**: list which measures exclude zero, name the variant and baseline, and cap or explain the CI above 100%.
- **Acceptance criteria**: no sentence in the abstract, Sec. 5 or Sec. 7 uses "every measure" for IETrans, and the abstract names the baseline mismatch.

**R3-2: TDE non-detection**
- **Problem**: the "unchanged" reading has no equivalence margin, and the AUC interval half-width is about a quarter of the +0.0323 geometry effect.
- **Source**: EIC W3, R1 W2, R2 W3, R3 W1, DA M3; recomputed V8.
- **Requirement**: state a margin or MDE for each TDE-vs-control comparison under both weightings and at the uniform mix, and reword to "no change detected within +/- m".
- **Acceptance criteria**: the abstract and conclusion state the bound, and the Sec. 5 heading does not imply equivalence.

**R3-3: protocol disclosure**
- **Problem**: the "ten points" and the 87% are graph-constrained and micro-averaged. Without the graph constraint, official mR@50 falls and the pooled total is -0.0337. The five of six positive TDE-vs-LA1 cells are not in the main text.
- **Source**: R1 W2, R2 W4, R3 W1(ii), W7, DA M2, m1, m2; recomputed V1, V2, V7.
- **Requirement**: move the six-cell table into the main text and add the abstract disclosure.
- **Acceptance criteria**: the main text shows gc and ng at k = 20/50/100 with intervals, and the abstract states protocol and statistic.

**R3-4: calibration protocol**
- **Problem**: the primary protocol (per-model temperature) is the one under which TDE's quadratic case-level part is null (-0.00006). Under temperature + class bias it is +0.00445 [+0.00354, +0.00536].
- **Source**: R1 W1, R3 W5, EIC W3, DA M1.
- **Requirement**: ex-ante rule, all families in Fig. 2, a hierarchy for sign disagreements.
- **Acceptance criteria**: Sec. 3 states the rule, Fig. 2 shows every family, and Sec. 7 states which verdicts the hierarchy supports for TDE and IETrans.

**R3-5: AUC weighting**
- **Problem**: the two weightings disagree on significance for SGCls (-.0047 vs -.0128), IETrans and CLIP.
- **Source**: R1 W6, R2 W3, R3 W1, W4.
- **Requirement**: one primary weighting and both reported wherever quoted.
- **Acceptance criteria**: every AUC claim in the abstract names its weighting.

**R3-6: scope**
- **Problem**: n = 2 MOTIFS-family checkpoints on one dataset, with field-level wording.
- **Source**: EIC W1, R2 W1, R3 W4, DA M4. R1 disputes the wording point only.
- **Requirement**: Route A or Route B, as in the table.
- **Acceptance criteria**: either at least two further audits with the same outputs, or title, abstract and conclusion scoped to the two checkpoints.

**R3-7: headroom**
- **Problem**: no method is shown with a large case-level mR share, so 87% cannot be interpreted.
- **Source**: R2 W5, EIC W1, DA M5.
- **Requirement**: reference model and, where feasible, an oracle bound in the mR split.
- **Acceptance criteria**: a main-text or supplement row gives the case-level mR share of a reference model.

**R3-8: grouping**
- **Problem**: the share is conditional on one φ, and the paper itself reports that coarsening can flip the sign of the group-level part.
- **Source**: R1 W5, R3 W2, DA M6.
- **Requirement**: two finer groupings and a sensitivity band.
- **Acceptance criteria**: the abstract names φ and the supplement reports the share under at least two finer groupings.

**R3-9: beyond-SGG**
- **Problem**: LA's matched covariance exceeds DRW's, yet DRW is called "genuine"; groupings are label-derived.
- **Source**: R1 W3, R3 W8, EIC W5; the Table 11 numbers are seat-reported.
- **Requirement**: relabel as a different estimand and remove or qualify the "genuine discrimination" language.
- **Acceptance criteria**: the Sec. 6 paragraph and Supp. N.5 contain no claim of discrimination beyond the LA control.

**R3-10: CLIP**
- **Problem**: the AUC weightings disagree in sign, so "not better ranking" is not established.
- **Source**: R3 W3, R1 W6.
- **Requirement**: one pre-declared criterion for TDE and CLIP, plus a qualified title or heading.
- **Acceptance criteria**: Sec. 6 reports both weightings and applies the same standard it applies to TDE.

---

## Part 3: Reviewer Report Summary (Appendix)

| Seat | Role | Recommendation | Confidence | Questions | Minor issues |
|---|---|---|---|---|---|
| EIC (Journal-Fit) | AC for scene understanding and evaluation | Major Revision (borderline, leaning accept if repaired) | 4 | 4 | 7 bullets |
| R1 | Evaluation statistics (proper scores, U-statistics) | Major Revision | 4 | 5 | 6 sub-threshold bullets (plus W7 to W9 minor findings) |
| R2 | SGG domain specialist | Major Revision | 4 | 5 | 8 bullets |
| R3 | Outside-field evaluation scientist (long tail, shortcuts, label shift) | Major Revision (borderline) | 4 | 6 | 10 bullets |
| DA | Fixed adversarial seat | N/A, findings only | per-finding | n/a | 4 (m1 to m4) |

Key points:
- **EIC:** real contribution; breadth and the IETrans claim are the weak points; the proofs were not verified.
- **R1:** algebra and reproducibility are sound; protocol dependence, non-detection and grouping conditionality limit what the evidence licenses.
- **R2:** the TDE audit is convincing; the IETrans comparison is confounded, and the graph-constraint premise and the missing headroom matter.
- **R3:** the control is the best idea; the case-level reading is narrower than stated, and CLIP and the reporting protocol are inconsistent.
- **DA:** no CRITICAL defect; the strongest counter-argument is that the case-level part is overruled in each case where it disagrees with the thesis.

Panel provenance: five Phase 1 seats, each a fresh subagent launched concurrently with no peer or prior-panel visibility. All five share the orchestrator's single model family and provider. Provenance axes are recorded in `_panel_provenance.md`.

---

## Appendix A: Weakness Sub-Claim Inventory (Step 1b)

Positions: R = raised, C = corroborated, N = not-mentioned, D = disputed. Severity is transported from the parent finding as tagged by each seat, not re-derived. Seat severity and confidence per finding appear in the roadmap rows.

| SC | Sub-claim | EIC | R1 | R2 | R3 | DA | Disposition |
|---|---|---|---|---|---|---|---|
| SC-1 | IETrans "under every measure" exceeds Table 1 | R W2 | R W6 | R W2 | R W4 | M4 | CONSENSUS-4 |
| SC-2 | IETrans baseline separately trained; not stated in abstract | R W2 | R W6 | R W2 | R W4 | M4 | CONSENSUS-4 |
| SC-3 | TDE "unchanged ranking" is non-detection; no margin or MDE | R W3 | R W2 | R W3 | R W1 | M3 | CONSENSUS-4 |
| SC-4 | Six protocol/k cells and ng rows belong in the main text | N | R W2 | R W4 | R W1(ii), Q3 | M2 | CONSENSUS-3 (EIC silent) |
| SC-5a | 87% and "nine of ten points" are micro-averaged, not official | N | R W7 | R W4 | R W7 | m1, m2 | CONSENSUS-3 (EIC silent); severity split resolved in Disagreement 3 |
| SC-5b | Ten points exist only under the graph constraint | N | R W2 | R W4 | R W7 | M2 | CONSENSUS-3 (EIC silent); severity split resolved in Disagreement 2 |
| SC-6a | Add audits of other families | R W1 | N | R W1 | R W4 | M4 | CONSENSUS-3 (R1 silent) |
| SC-6b | Title, abstract and conclusion scope wording | R W1 | D (Detailed Comments, Research Questions) | R W1 | R W4 | M4 | SPLIT, arbitrated in Disagreement 1 |
| SC-7 | Share conditional on one grouping | N | R W5 | N | R W2 | M6 | corroborated (2) |
| SC-8 | No reference or positive control | C W1 | N | R W5 | C W2 (partial) | M5 | CONSENSUS-3 (R1 silent) |
| SC-9 | Case-level part is protocol-determined; primary protocol rule | C W3 | R W1 | N | R W5 | M1 | CONSENSUS-3 (R2 silent) |
| SC-10 | Pre-specify AUC weighting | N | R W6 | R W3 | R W1, W4 | M1 | CONSENSUS-3 (EIC silent) |
| SC-11 | Beyond-SGG language and label-derived grouping | R W5 (minor) | R W3 (major) | N | R W8 (minor) | N | SPLIT (severity), Disagreement 4 |
| SC-12 | CLIP "not better ranking" asymmetry | C (Results, "indirect") | R W6 | N | R W3 | N | corroborated (2); perspective split, Disagreement 7 |
| SC-13 | Interval validity and nuisance variance | N | R W4 | N | N | N | single-reviewer |
| SC-14 | Normative reading of "group-level" | N | N | R W6 | R W6 | m3 | corroborated (2) |
| SC-15 | Novelty positioning and related work | R W4 (major) | N | R W8 (minor) | N | m4 | SPLIT (severity), Disagreement 5 |
| SC-16 | Matched-subset fraction in SGCls/SGDet | N | N | R W7 | N | N | single-reviewer |
| SC-17 | Presentation density and appendix dependence | R W5 | C (table labelling) | C (Layout) | C (Layout) | N | CONSENSUS-3 (EIC, R2, R3; R1 partial) |
| SC-18a | Report needs full-score archives | R W6 | N | N | C W5 | N | corroborated (2) |
| SC-18b | No decision rule for contradictory outputs | N | C W1 suggestion (b) | N | R W5 | N | corroborated (2); merged into R3-4 |
| SC-19 | Project name "WAGER" in supplement | R (Layout) | N | C (terminology only) | N | N | single-reviewer |
| SC-21 | Proper score on TDE logits | N | R W9 | N | N | N | single-reviewer |
| SC-22 | Image-level permutation test, same-image siblings | N | R W8 | N | N | N | single-reviewer |
| SC-23 | Zero-shot and F@K split | N | N | R W6, Q1 | N | N | single-reviewer |

Surface-form parity check: no sub-claim was down-rated or credited for phrasing. The counterfactual test was applied to R1's technical register and to the DA's terse table style. Assessments rested on the cited paper values and on recomputation V1 to V8. No sub-claim was marked unevaluable.

---

## Panel provenance (summary)

- Five Phase 1 seats (EIC, R1, R2, R3, DA), each a fresh subagent, launched concurrently.
- No seat saw a peer's output, and no seat saw any prior panel.
- All five seats and the orchestrator share one model family and one provider. Distinctness on those two axes is `false`. No human reviewer sat on the panel.
- Persona and role diversity prove role separation only. They do not prove independent error processes, and no independence claim is made.
- A replay-valid typed provenance artifact was not produced, so the axis values are orchestrator-attested and not machine-verified. Details are in `_panel_provenance.md`.
- Correlated-error disclosure: because the seats share a model family, a misreading or blind spot common to the family would appear as apparent consensus here. The consensus counts above are therefore not an independent-replication count. For that reason the decision relies on the recomputation V1 to V8 and on the cards' paper-quoted evidence, not on the number of seats agreeing.
- Human accountable for the use of this review: Quang-Vinh Dang, British University Vietnam.

Calibration status of every seat and of this package: `NOT_CALIBRATED`.


## Status after the revision pass (2026-10-10)

| item | status |
|---|---|
| R3-1 IETrans wording, mismatched baseline | **Done.** Abstract, intro, Sec. 5 and conclusion now say the within-pair discrimination falls on the matched scores and the relation-weighted AUC (−0.0235 [−0.0275, −0.0182]), not detectably on the comparison-weighted one (−0.0093 [−0.0181, +0.0004]), and that no baseline was released. |
| R3-2 equivalence margin | **Partly done.** The abstract and intro state that the comparison-weighted AUC excludes a gain above 0.009 for TDE. No pre-registered margin; a benchmark would have to set one. |
| R3-3 protocols and graph constraint | **Partly done.** The abstract scopes the 87% to the graph-constrained, micro-pooled mean recall (the official statistic moves +0.1017 against +0.0972); Sec. 5 reports the no-graph rows (+0.0148 [+0.0064, +0.0232] at K=100; 77% at K=20). The six-cell table was not moved into the main text. |
| R3-4 primary calibration protocol | **Partly done.** The conclusion gives a rule for disagreement (report the interval over protocols and the within-group AUC, not a sign). No ex-ante primary protocol; Fig. 2 still shows one. |
| R3-5 primary AUC weighting | **Not done.** Both weightings remain reported side by side. |
| R3-6 breadth | **Rescoped, not extended.** Abstract and conclusion name the two Neural-Motifs checkpoints and say no later method is audited. Title unchanged. |
| R3-7 headroom | **Done.** An oracle gains +0.5068 in quadratic score, all case-level (+0.8041 against −0.2973). |
| R3-8 share under other groupings | **Done (supplement).** Finer cells keep it at 90% (position, size); the subject class alone gives 18%, because the object class becomes a within-cell signal. |
| R3-9, R3-10 | **Done.** SGCls matched fraction and comparison-weighted AUC in Sec. 5; the CLIP wording says the ranking reading depends on the weighting and that the CLIP model reads a wider input. |
| CIFAR/text DRW "genuine" reading | **Caveated (supplement).** Matching there is temperature only and the logit-adjusted baseline's matched covariance (+0.03241) exceeds DRW's (+0.01957). |
| R3-20 "WAGER" name | **Open, for the authors.** The name appears in the supplement and the code archive; check whether it points to the public repository before submission. |

Not done: coverage simulations for the mean-recall hit contrast and the share interval, and propagating calibration-half and checkpoint variability into the intervals (R1 W4).
