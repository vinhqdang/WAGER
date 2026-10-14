# Editorial Decision Package (Round 3)

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

`criteria_binding_unavailable`: no target-criteria binding was supplied and all five cards disclose this. No venue-alignment claim is made. The standard Synthesis Protocol was used (no sprint contract), so no scoring matrix or failure-condition arithmetic applies.

Same-model-family panel: all five Phase 1 seats ran on one model family (Sonnet) from one provider, and this synthesis is by an agent whose runtime identifies it as the same family. Agreement among seats is weaker evidence than agreement among independent reviewers, and repeated findings may reflect one shared reading of the same passage. Full provenance is in `_panel_provenance.md`. Because of this limit, the claims that decide the outcome were rechecked against `results/*.json`, the committed prediction arrays under `data/vg_motifs/` and the text extracts (section "Verification"). Seat claims that were not rechecked are marked **[UNVERIFIED]**.

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Venue configuration**: simulated CVPR 2027 panel (configured perspective only)
- **Review target**: `cvpr2027/paper.pdf` (8 pp + references) and `cvpr2027/supp.pdf`, repository commit `6b8f1b9`. This is the version after the round-2 must-fix and should-fix passes (the "Status after ..." sections at the end of `reviews/2026-10-13b-cvpr-panel/0_editorial_decision_and_roadmap.md`).
- **Decision date**: 2026-10-14
- **Review round**: 3 (mode full, Phase 2). Round-2 package: `reviews/2026-10-13b-cvpr-panel/` (commit `2da86a9`; roadmap IDs `R5-n`). Round-3 IDs are `R6-n`. The dispatcher instructed each seat not to read other panels' or seats' outputs.
- **Submission deadline**: 16 Nov 2026 (33 days from the decision date); 8-page body limit.

## Review Panel Provenance (summary)

Five role-separated seats (EIC, R1, R2, R3, DA), each a fresh AI subagent run on Sonnet, launched concurrently by an Opus orchestrator, each instructed not to read other panels' or seats' outputs. The instruction is recorded as given; this synthesizer cannot confirm compliance. Accountable human: Quang-Vinh Dang (British University Vietnam). No typed `review-panel-provenance/1.0` artifact or digests were supplied, so none are reported. Axes: role-separated true; blind to peer outputs true (as instructed); model-family distinct **false**; provider distinct **false**; human-reviewer distinct false. No binary independence claim is made. No cross-model decision check was run.

---

## Decision

### Minor Revision (accept with conditions)

**Confidence in the decision: medium.** Three of the four scoring seats recommend Weak Accept (borderline), each conditional on scope and claim edits (R1, R2, R3); the EIC recommends Major Revision (borderline, leaning Weak Accept on the contribution, Weak Reject "as currently packaged"). The Devil's Advocate raised 0 CRITICAL issues (6 MAJOR, 6 MINOR) and states that nothing it lists invalidates a central claim as stated. Seat recommendations were not counted as votes; the category was set from the evidence below.

Round-2 asked for eight must-fix items and expected, if they landed, a Minor Revision or an accept-with-conditions. All eight landed (table below): six are resolved as stated, two (R5-5 equivalence wording and R5-6 method labels) are resolved in the text but each has a residual that a seat has sharpened. The round-3 seats find no arithmetic defect; R1 recomputed the headline split, the TDE AUCs and the LA control from the shipped arrays, and the EIC, R2 and DA spot checks agree. The decision therefore rests on a different question from round 2: not "was the analysis done" but "which of the paper's positive statements survive a noise floor and a multiplicity check".

One finding is new and decision-bearing. R1 compared two separately trained MOTIFS baselines that the repository already holds and found a relation-weighted AUC difference of -0.0060, larger in magnitude than the +0.0050 the abstract reports as PE-Net's rise and the +0.0029 reported for DLFE. I reproduced it (check (e)). The group-level shares and the TDE results are not affected, because TDE is evaluated on the same network as its baseline. The PE-Net "gains discrimination" statement, the DLFE "small AUC gain" and the IETrans AUC "fall" under two of its weightings are not distinguishable from cross-release variation. This is a claim to remove or requalify, not a new experiment, so it does not move the category to Major. It does make R6-1 below a gating item: if the abstract and Sec. 5 keep "its within-pair AUC rises" without the noise floor, the editor would move to Major.

What keeps this from Accept: the six must-fix items below (all re-framing or small re-analysis on cached arrays), of which R6-1 and R6-2 touch the abstract's positive and bound claims. If R6-1 to R6-6 land as written, the editor expects the next round to be an accept.

Editorial lines for the sprint/audit trail:
- `da_critical_adjudications: []` (the DA's CRITICAL list is empty, with the stated reason that scoping is careful and no single MAJOR invalidates a central claim)
- `editorial_decision=minor_revision`

---

## Round-2 items: status at commit 6b8f1b9

"Resolved" means the change is in the paper text and no round-3 seat re-raises it as a defect. "Partially resolved" means the change is in the text and one or more seats raise a residual. "Re-raised" means a seat raises the concern against the current text. Evidence is the round-3 cards plus the text extracts; results in the right-hand column were rechecked where marked.

| Round-2 item | Status | Evidence at 6b8f1b9 | Residual routes to |
|---|---|---|---|
| R5-1 scope | **Resolved as wording; residual minor.** | Abstract: "three released Neural-Motifs checkpoints of prior-correcting methods, one run each"; intro "What is not claimed" (lines 098-103) covers four checkpoints (three prior corrections and one prototype-based) and disclaims one-stage and VLM models. EIC W3, R2 W2 and DA m1 still read the title and opening as field-level. The abstract says "three" and then reports four methods, and the intro says "four": a count inconsistency (verified in `paper_text.txt` lines 013 and 098). | R6-5 (expected-by-construction framing), R6-6 (abstract) |
| R5-2 protocol conditions | **Resolved; two analysis residuals.** | Abstract carries "At K = 50 with the graph constraint ... elsewhere the two differ by 0.02 to 0.15" and 84% beside 87%. Table 2 grid verified (check (b)). Residual: R1 W3(a), R2 W3 and EIC Q2 want a tau sweep and a cell-wise-prior control so the K=50 match is not one lucky operating point. | R6-9 |
| R5-3 grouping range | **Partially resolved.** | Abstract states 18% (subject classes) and Table 1 lower panel has 90% and 84%. Residual: EIC W1 and the DA's strongest counter-argument say a large share is near-mechanical for corrections indexed by the object pair; R1 W6 notes no AUC is computed at the finer groupings. | R6-5, R6-11 |
| R5-4 AUC weighting | **Resolved as re-analysis; verdict wording re-raised.** | Pair and predicate weightings added at 1,000 replicates, tie-floor fixed (R1 confirmed: no zeros or denormals, min 1.8e-20). TDE verdicts verified (check (c)). R1 W1, DA M2, EIC W2: the two headline weightings put 57% and 65% of weight on head-head pairs; the predicate weighting, the one closest to mean recall, establishes equivalence at no margin (check (d)); no power analysis. | R6-2, R6-8 |
| R5-5 equivalence wording | **Partially resolved.** | "Excludes changes above X under weighting W" is in the abstract and Sec. 5; post-hoc declaration disclosed; baseline AUC 0.61/0.57 given. Residual: margins come from a different model family (box geometry on a reconstructed split) and were set after the TDE result (R1 W1, EIC W2); Sec. 3 says the recalibration family "is fixed before any gain is read" while Sec. 5 says the primary protocol was declared after TDE and IETrans (verified, check (h)). | R6-2, R6-3 |
| R5-6 method labels | **Partially resolved; re-raised in a stronger form.** | Table 1 caption now says one released run each, test sampling only; IETrans is flagged as unisolated. Abstract still says PE-Net's "within-pair AUC rises (the last two against a separately trained baseline)"; Sec. 5 says "Where a method does gain discrimination, the split shows it". R1's baseline-to-baseline finding (check (e)) shows this is not identified; R2 W1, DA M4, R3 W7, EIC W3 re-raise. | R6-1 |
| R5-7 proper-score claims | **Resolved.** | +0.0045 is out of the abstract; contribution (ii) no longer claims to separate calibration, prior and shortcut effects; primary-protocol randomization p = .001 verified (`results/sgg_primary_randomization.json`, 999 randomizations). Residual: R1 W11 (randomization ignores image clusters; floor .001 not noted), DA m2. | R6-19 (consider) |
| R5-8 reading rule | **Resolved; framing residual.** | "How to read the split" paragraph and label-mix result are in Sec. 5. R3 W3 and W9 ask for a sign-reading rule outside SGG and a terminology note; DA M6 and EIC say the downstream payoff (captioning, VQA) is asserted. | R6-16 |
| R5-10 density | **Partially resolved; re-raised.** | Abstract is shorter than in round 2 but all four seats still count about 20 to 25 numerals (EIC W7, R2 W9, R3 W8, DA m6). | R6-6 |
| R5-11 interval validity | **Resolved.** | Delete-a-group jackknife reported; headline case-level interval [+0.0088, +0.0173] in Sec. 5; the 88% real-data bootstrap result is disclosed. R1 W5 recomputed a refit-jackknife SE ratio of 1.055 to 1.07 versus the paper's 1.09 to 1.13 **[UNVERIFIED by me]**; the direction agrees, so nothing is contradicted. Residual: calibrator fitted on half the images is conditioned on, not propagated. | R6-18 |
| R5-12 pair-indexed family | **Wording route accepted.** | Sec. 5 states ranking is read from the AUC alone. R1 W3(a) now asks for a cell-wise-prior control instead. | R6-9 |
| R5-13 training seeds | **Wording route; re-raised (EIC Q3, R1 W2, R2 W1/Q3, R3 W7, DA M4).** | The paper states one run each. The new finding supplies a cheap partial substitute: the repository already holds two separately trained baselines. | R6-1 |
| R5-14 non-prior method (PE-Net) | **Done; created the R6-1 issue.** | PE-Net row, Sec. 5 paragraph and App. replay are present and reproduce published R@50/mR@50 (R2 confirmed in `results/penet_official_recall.json`). Its comparison is against the TDE-release MOTIFS baseline, a different codebase. R2 W5: PE-Net's rel-NMS recall path and its raw-probability AUC path differ. | R6-1, R6-14 |
| R5-15 Waterbirds | **Partially resolved.** | Contrast is in Sec. 6 with worst-group accuracy; verified round 2. R3 W2: AUC moves only +0.0031, the supplement concedes much of the gain is calibration, the matched case-level part is +0.1138 not +0.0914, one probe pair and one seed, no worst-group decomposition. | R6-12 |
| R5-16 label ambiguity | **Partially resolved.** | Synonym-merge analysis present. R1 W9: the merge folds "parked on", "walking on" into "on", which is TDE's largest movement, so it removes the boundary under test; for IETrans a recorded-label AUC penalises relabelling by construction (DA stakeholder note). | R6-19 |
| R5-17 positioning | **Partially resolved.** | Head/body/tail and zero-shot comparison added; SQUAT, VRT and arXiv 2503.17862 cited. EIC W12 and R3 W4: still no case where Murphy resolution or per-model conditional permutation importance would conclude differently from the split. | R6-13 |
| R5-19 SGDet fraction | **Resolved.** | PredCls in the first sentence; 58% and 65% matched fractions stated. R2 W4: the replay claim "reproduces released numbers" should read "to within 0.0007" for SGDet **[UNVERIFIED; Tab. 37 values are R2's reading]**. | R6-14 |
| R5-20 declaration | **Resolved as disclosure; multiplicity re-raised.** | "Post hoc for TDE and IETrans" and a multiplicity sentence are in Sec. 5. R1 W7: no family-wise treatment of the positive claims that are quoted (pair-weighted TDE fall, PE-Net rise, DLFE +0.0029, zero-shot AUC fall). | R6-7 |
| R5-21 feature ablation | Not done; optional in round 2. | Not re-raised. | none |
| R5-22 governance | **Not done; partly re-raised.** | EIC Q7 and R3 W10 ask who declares the grouping and for an impact paragraph (gaming the case-level part). | R6-19 |
| R5-23 shares above 1 | **Partially resolved.** | Shares are suppressed when the total gain is negative. R1 W10: IETrans share upper limit 1.04. | R6-19 |
| R5-24 typos, Table 2 | **Resolved for Table 2 (not re-raised by any seat); typos re-raised.** | R1 and EIC list cross-reference errors: the main text cites "Appendix Q.11" for the zero-shot AUC but Q.7 is the zero-shot recall section and Q.11 is zero-shot CLIP (verified in `paper_text.txt` line 486 and `supp_text.txt` lines 2445 and 2592). I did not re-render the PDF. | R6-19 |

---

## Verification (read-only checks of the claims that decide the outcome)

No file other than the two deliverables was modified (the working tree was clean after the checks). One small Python run (prediction arrays under `data/vg_motifs/`, scripts in the session scratchpad outside the repository) reproduced R1's finding; the other checks read `results/*.json` and the text extracts.

| # | Claim | Source seat | Status | How |
|---|---|---|---|---|
| (a) | Headline split: +0.0972 = +0.0841 group + +0.0130 case; 87% | all seats | **Verified** | `results/sgg_recall_split.json`, gc@50. Share 0.8657 is the EIC and DA spot check of `sgg_share_intervals.json` (not re-read by me). |
| (b) | Control grid (Table 2): TDE minus LA | R1, R2, DA, EIC | **Verified** | `results/sgg_recall_split_TDE_vs_la1.json` mean recall: gc@20 total -0.0234 [-0.0285, -0.0182]; gc@50 +0.0031, case -0.0008 [-0.0050, +0.0033]; gc@100 +0.0300; no-graph (ng) @20/50/100 -0.0792 / -0.1272 / -0.1549; ng@100 case +0.0148 [+0.0064, +0.0232]; ng@50 case +0.0072 [-0.0001, +0.0145]. Matches the abstract's "0.02 to 0.15". |
| (c) | TDE within-cell AUC changes (1,000 replicates) | R1, DA, EIC | **Verified** | `results/sgg_auc_label_weighting.json`, TDE vs none, 95% intervals: relation -0.0018 [-0.0043, +0.0016]; comparison +0.0025 [-0.0028, +0.0087]; pair -0.0153 [-0.0249, -0.0004]; predicate -0.0038 [-0.0339, +0.0211]. LA vs none is 0 to 1e-6 under all four weightings. R1's recomputation (relation -0.0018, comparison +0.0025, pair -0.0153) agrees. |
| (d) | The abstract's "0.0038 to 0.028" bounds and what they establish | R1 W1, DA M2 | **Verified (new detail)** | Same file, `largest_change_excluded` / equivalence at 5%, 10%, 25% of the geometry gain: relation 0.0038 (equivalent at 10% and 25%); comparison 0.0077 (25% only); pair 0.0229 (25% only); predicate 0.0279 (**not equivalent at any margin**; reference gain 0.0694, 25% margin 0.0174). Weight on head-head pairs 0.649 (comparison), 0.572 (relation) (`weight_share`). So the abstract's range spans a weighting under which equivalence holds at 10% and one under which it holds at none. |
| (e) | **R1's baseline-to-baseline finding**: two separately trained MOTIFS baselines differ in relation-weighted AUC by about -0.0060 | R1 W2 (also R2 Q4, EIC Q3 as a question) | **Verified, and extended** | Recomputed with `experiments/sgg_variants.load_variant` for `none` (TDE release baseline) and `dlfe_base` (DLFE release baseline), raw probabilities renormalised over the 50 predicates as `experiments/run_sgg_rank_robustness.sgg_data` does, `wager.rank.within_cell_auc_contrast`, n_boot = 200, image-clustered. Detail below the table. |
| (f) | The background-column mass differs strongly across variants (pair ranking, R1 W4) | R1 W4 | **Verified** | Mean column-0 (background) probability over the 183,642 rows: none 0.855, TDE 0.021, LA1 0.651, DLFE baseline 0.682, PE-Net 0.560. R1's 0.85 / 0.02 / 0.65 agree. The consequence (some of TDE's mean-recall case-level part may be pair-ranking change that no AUC measures) is R1's reading and was **not tested** by anyone (**[UNVERIFIED]** as a mechanism). |
| (g) | Sec. 3 "the family is fixed before any gain is read" conflicts with Sec. 5 "declared after the TDE and IETrans results were seen" | R1 W3(b) | **Verified as a textual tension** | `paper_text.txt` line 245 (Sec. 3) and lines 340-370 (Sec. 5 "Protocol"). They may concern different objects (family choice criterion vs primary quantities), but a reader cannot tell; one sentence fixes it. |
| (h) | The abstract mixes bases for "points" | R1 W13 | **Verified** | Paper text: TDE 14.6 to 24.8 is the official per-image statistic; IETrans official mR@50 0.3587 less 0.1459 = 0.2128 (the abstract's "21") while Table 1's micro-pooled gain is +0.2204 ("22"); DLFE micro +0.1112 ("11"), official +0.1039 per R1 **[UNVERIFIED]**. PE-Net 17 points holds on either basis (official 0.3142 - 0.1459 = 0.1683). |
| (i) | TDE's raw zero-shot recall gain is 50% case-level, but the main text reports only the control-adjusted +0.0131 | R1 W8 | **Verified** | `results/sgg_zeroshot_split.json`: direct change +0.0339; identified change +0.0369 with case-level +0.0186 [+0.0142, +0.0230] (50%). |
| (j) | DLFE's AUC change against its baseline cannot be a method effect | R1 W2 | **Verified from the paper's own text** | Supp. line 1851: "The correction is exactly ranking-preserving: against the same network before the correction the AUC change is 0"; `experiments/expand_dlfe_to_standard.py` names `variant_dlfe_soft` as "MOTIFS-DLFE before the correction". So the +0.0029 against `dlfe_base` is a difference between two trained networks. The main text (line 488-490) calls this comparison "controlled". |
| (k) | IETrans and PE-Net AUCs | EIC, R1, DA | **Verified** | `results/sgg_auc_label_weighting.json` and `results/sgg_penet_audit.json` (1,000 replicates): IETrans relation -0.0238 [-0.0272, -0.0187], comparison -0.0093 [-0.0185, -0.0001], pair -0.0274 [-0.0521, -0.0160]; PE-Net relation +0.0050 [+0.0008, +0.0091], comparison +0.0055 [-0.0033, +0.0149], pair +0.0187 [+0.0037, +0.0337]. DLFE vs dlfe_base relation +0.0029 [+0.0001, +0.0055] at B = 1,000; my B = 200 run gave [-0.0004, +0.0056], so the lower limit sits on the zero boundary, as R1 reported. |

**Detail for (e), baseline-to-baseline AUC differences** (difference = new minus old; 95% intervals; B = 200 for my runs, 1,000 for values marked J from the committed JSON):

| Contrast | Relation weighting | Comparison weighting | Pair weighting |
|---|---|---|---|
| `dlfe_base` minus `none` (two separately trained MOTIFS baselines) | **-0.0060 [-0.0099, -0.0017]** | +0.0017 [-0.0069, +0.0130] | **-0.0181 [-0.0346, -0.0062]** (not reported by R1) |
| TDE minus none (same weights; no training difference) | -0.0018 [-0.0043, +0.0016] (J) | +0.0025 [-0.0028, +0.0087] (J) | -0.0153 [-0.0249, -0.0004] (J) |
| PE-Net minus none | +0.0050 [+0.0006, +0.0089] | +0.0055 [-0.0040, +0.0151] | +0.0187 [+0.0033, +0.0324] |
| DLFE minus `dlfe_base` | +0.0029 [-0.0004, +0.0056] | +0.0018 [-0.0041, +0.0064] | +0.0024 [-0.0099, +0.0135] |
| IETrans minus none | -0.0238 [-0.0277, -0.0185] | -0.0093 [-0.0182, +0.0002] | -0.0274 [-0.0508, -0.0162] |

R1's relation and comparison values for the baseline pair reproduce exactly (-0.0060 [-0.0099, -0.0017]; +0.0017 [-0.0069, +0.0130]). R1's mR@50 figures for the same pair (total +0.0206, group +0.0199, case +0.0007 [-0.0016, +0.0030]) were **not recomputed** by me; the official mR@50 difference of 0.1647 - 0.1459 = +0.0188 is consistent with them and comes from numbers the paper states.

**What the finding implies for the claims** (my reading; labelled as such):

1. **What it shows and what it does not.** It is one realised difference between two trained networks from two releases and codebases. It is evidence that cross-release AUC differences can reach 0.006 (relation weighting) and 0.018 (pair weighting). It is not an estimate of run-to-run spread, and the interval is test-sampling uncertainty about that one pair. Because PE-Net and IETrans are also compared against the TDE-release baseline, which is a different release from both, the floor applies to them directly.
2. **PE-Net.** The relation-weighted rise (+0.0050) is smaller in magnitude than the baseline-to-baseline difference (0.0060). Against `dlfe_base` as the reference instead, the same PE-Net AUCs would give increases of about +0.0110 (relation), +0.0038 (comparison) and +0.0368 (pair) by simple subtraction of the point values in the table above. The sign and size of the "rise" depend on which baseline is used, and neither is the PE-Net baseline. So "PE-Net gains within-pair discrimination" is **not identified**, and "a twelfth of what box geometry buys" (Sec. 5) is a number without a stated noise level. The PE-Net mean-recall case-level part (+0.0243 [+0.0197, +0.0289]) is larger than R1's baseline-to-baseline case-level part (+0.0007) and may survive; that comparison needs recomputation by the authors (R6-1) before the paper uses it.
3. **DLFE.** The correction is ranking-preserving, so the AUC change against its own network before correction is exactly 0. The +0.0029 against `dlfe_base` is therefore entirely training difference, smaller than the 0.0060 floor, with a lower limit that moves across zero with the replicate count. The paper's wording "released with the baseline it was trained against, so this comparison is controlled" holds for the release but not for the weights. The clean control, `dlfe` against `dlfe_soft`, is already in the repository. The DLFE group-level share (94%) is robust to this (gain 0.11 against a 0.02 floor, R1's decomposition **[UNVERIFIED]**), but it is computed against a different network than the one the correction was applied to.
4. **IETrans.** The relation-weighted fall (-0.0238) is about four times the floor and survives. The pair-weighted fall (-0.0274) is of the same size as the floor (-0.0181) and the comparison-weighted one (-0.0093) has the opposite sign to it. The abstract no longer states the fall; the body does and should carry the floor.
5. **TDE.** Unaffected: TDE is an inference-time change on the same checkpoint as its baseline, so there is no training difference. One consequence worth stating in the paper is that TDE's 0.0038 bound (relation) is tighter than the cross-release floor, which supports using it as a bound. A second is that the abstract's pair-weighted fall for TDE (0.015) is smaller than the floor under the same weighting, so it is a same-network result, not noise, but its upper limit is -0.0004 and it is one of four weightings (R6-2, R6-7).
6. **Group-level shares.** Unaffected in size (gains of 11 to 22 points against a floor of about 2); they are still cross-release quantities and should be labelled so.

Not verified by me (taken from the cards): R1's jackknife and half-sample checks, R1's mR split for the baseline pair, R1's proper-score, SGCls/SGDet, CIFAR, text, Waterbirds and simulation reruns (R1 did not rerun them either, per its log), R2's reading of the PE-Net NMS code and of the SGDet replay deviation (0.0894 vs 0.0901), R2's reference leads (CFA ICCV 2023, the survey and DB-SGG are marked VERIFIED by R2; RA-SGG and the TDE-variant lead are marked UNVERIFIED by R2), the EIC's reference leads (SGTR marked verified by the EIC; RelTR and HiLo marked UNVERIFIED by the EIC), R3's references (Kirichenko et al., Yang et al., Gneiting and Raftery marked VERIFIED by R3; Oaxaca-Blinder, Idrissi et al., JTT marked UNVERIFIED by R3), R1's archive-contents claims, any proof, any checkpoint replay, and whether the primary protocol was declared before the data were seen.

---

## Blocking Issues (3, immutable source order)

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| B1 | The cross-release AUC statements (PE-Net "rises", DLFE "gains", IETrans "falls" under two weightings) are not distinguishable from the difference between two separately trained baselines (-0.0060 relation, -0.0181 pair) | R1, R2, DA, R3, EIC | dataset: `data/vg_motifs/wager_sgg` and `wager_dlfe` (check (e)); text: abstract, Sec. 5 "Two more methods", "Where a method does gain discrimination, the split shows it" | R6-1 |
| B2 | The abstract's TDE ranking sentence mixes four weightings, post-hoc margins and an exploratory "falls by 0.015" without naming the weighting beside each bound; the predicate weighting establishes equivalence at no margin | R1, DA, EIC, R2 | dataset: `results/sgg_auc_label_weighting.json` (check (d)); text: abstract | R6-2, R6-3 |
| B3 | The case-level part of mean recall is read as "an operating point spent on existing predicate discrimination", but the AUC audits only predicate order given the labelled pair; pair ranking and foreground/background mass move strongly (background mass 0.855 to 0.021) and are untested | R1 | dataset: mean background mass per variant (check (f)); text: Sec. 5 "What that licenses" | R6-4, R6-10 |

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence (self-reported scope disclosure) | Questions | Minor issues |
|---|---|---|---|---|---|
| Journal-Fit Reviewer (EIC) | CVPR area-chair perspective, evaluation and scene understanding | Major Revision (borderline; leaning Weak Accept on the contribution, Weak Reject as packaged) | 4 | 7 | 7 (W7-W13) |
| Reviewer 1 | Methodology: proper scores, U-statistics, equivalence testing | Weak Accept (borderline; conditional on W1-W4); mapped to Minor Revision | 4 | 7 | 6 (W8-W13) |
| Reviewer 2 | Domain: scene graph generation, unbiased SGG | Weak Accept (borderline), conditional on W1-W4; mapped to Minor Revision | 4 SGG, 3 statistics | 6 | 5 (W5-W9) |
| Reviewer 3 | Perspective: long-tail, shift, shortcut evaluation | Weak Accept (borderline-positive); mapped to Minor Revision | 3 | 6 | 6 (W6-W11) |
| Devil's Advocate | Fixed adversarial seat | N/A, findings only | per-finding | n/a | 6 minor, 6 major, 0 critical |

Confidence values are disclosures only and were not used to weigh, count or resolve anything. One tension is recorded: R1 recommends Weak Accept while stating that "the AUC conclusions are not safe" and listing seven Major weaknesses. The synthesizer relied on R1's findings, not its label.

Key strengths agreed across seats: exact identity and implementation (R1 reproduced the headline split, the TDE AUCs and the control from the shipped arrays); offline replay of the official evaluator to four decimals for the PredCls checkpoints (R2, EIC); the training-free operating-point control and the within-cell AUC as a falsifiable pair (all four); candour about protocol, grouping, post-hoc status and single-run limits (all five); every headline number traces to committed JSON (R1: 629 of 629 numbers trace).

---

## Step 1b: Weakness Sub-Claim Inventory

Severity is transported from the seat's per-finding tag. Positions: R = raised, C = corroborated, N = not mentioned (silence, not opposition), D = disputed. DA is tracked separately and is not counted in the 4. Every sub-claim is split from a weakness a seat wrote; none was introduced by the synthesizer.

| SC | Sub-claim | Parent weaknesses | EIC | R1 | R2 | R3 | DA | Transported severity |
|---|---|---|---|---|---|---|---|---|
| SC-1 | Cross-release comparisons (PE-Net, IETrans, DLFE) confound method with training run; no training-variance reference; R1's baseline pair puts a number on it | R1 W2; R2 W1; R3 W7; EIC W3, Q3; DA M4 | R | R | R | R | M4 | Major (R1, R2, DA); within Major (EIC); Minor (R3) |
| SC-2 | TDE "no discrimination" rests on post-hoc margins from another model family, head-heavy weights, no power; weighting should sit beside each bound | R1 W1; DA M2; EIC W2; R2 W9 | R | R | R | N | M2 | Major (R1, EIC, DA); Minor (R2) |
| SC-3 | Positive findings are exploratory and uncorrected: pair-weighted TDE fall, PE-Net rise, DLFE, zero-shot AUC fall | R1 W7; DA m2; R3 W11 | N | R | N | R | m2 | Major (R1); Minor (DA, R3) |
| SC-4 | Sec. 3 "fixed before any gain is read" vs Sec. 5 post-hoc declaration | R1 W3(b) | N | R | N | N | m2 | within Major (R1) |
| SC-5 | Case-level part of mean recall also credits pair ranking and foreground/background movement, which the AUC does not audit | R1 W4 | N | R | N | N | N | Major (R1) |
| SC-6 | LA is not a matched control for a pair-varying prior shift; control match is one (K, constraint) cell; no tau sweep or cell-wise prior | R1 W3(a); R2 W3, Q2; EIC Q2; DA M3, alt. path 2 | R | R | R | N | R | Major (R1, R2); question (EIC) |
| SC-7 | Group-level share is near-mechanical for prior-indexed corrections; the informative result is TDE's mechanism; share depends on grouping | EIC W1; R2 W2; R3 W5; DA M1 and strongest counter-argument | R | C | R | R | M1 | Major (EIC, R2, R3, DA) |
| SC-8 | Verdicts not checked at finer groupings (position, size) for the AUC | R1 W6; DA M1; EIC W1 | C | R | N | N | M1 | Major (R1) |
| SC-9 | Case-level part is protocol-sensitive; proper-score sign changes with matching family; reporting standard is heavy | EIC W4; R3 W5; DA M5 | R | R (W3b) | N | R | M5 | Major (EIC, R3, DA) |
| SC-10 | Normative payoff and downstream relevance asserted, not shown; terminology collision ("group-level") | DA M6; R3 W3, W9; EIC W5 | R | N | N | R | M6 | Major (DA); Minor (R3 W9) |
| SC-11 | Breadth claims outrun evidence: CIFAR and text use label-derived cells; Waterbirds is one probe pair, AUC +0.003, calibration-dominated | R3 W1, W2; EIC W11 | R (minor) | N | N | R | N | Major (R3) |
| SC-12 | Relation to Murphy resolution, grouping loss, permutation importance is argued, not demonstrated | R3 W4; EIC W12 | R (minor) | N | N | R | N | Major (R3); Minor (EIC) |
| SC-13 | Scope: four checkpoints of MOTIFS-family models, PredCls, 2020-2023 methods; no modern or one-stage model | EIC W3; R2 W2; DA m1 | R | N | R | N | m1 | Major (EIC, R2); Minor (DA) |
| SC-14 | SGCls/SGDet matched subset (58%, 65%); replay "to the fourth decimal" is looser for SGDet; PE-Net AUC on pre-NMS probabilities | R2 W4, W5; R3 W6; EIC W9 | R (minor) | N | R | R | N | Major (R2 W4); Minor (R2 W5) |
| SC-15 | Zero-shot: raw 50% case share unreported in main text; "not a better ranking" too strong; IETrans/DLFE zR drops in supplement only; wrong cross-reference | R1 W8; R2 W6 | N | R | R | N | N | Minor |
| SC-16 | Abstract and Sec. 5 density; bases mixed in one sentence ("11 and 21 points") | EIC W7; R2 W9; R3 W8; DA m6; R1 W13 | R | R | R | R | m6 | Minor (all) |
| SC-17 | Interval validity: refit jackknife, calibrator conditioning, 88% real-data coverage | R1 W5; DA m5; R3 W11 | N | R | N | R | m5 | Major (R1); Minor (R3, DA) |
| SC-18 | Reproducibility: anonymous archive lacks the arrays, supplement paths follow the renamed archive, version pins, repository README | R1 detailed comments | N | R | N | N | N | Minor (R1) **[UNVERIFIED]** |
| SC-19 | Impact and gaming of the case-level part; heavy-tailed cells; randomization p floor; label multi-label ceiling; shares above 1 | R3 W10, W11; R1 W9-W11; DA stakeholder section | N | R | N | R | R | Minor |

## Step 2: Consensus Analysis

### Points of Agreement (Consensus)

**[CONSENSUS-4]** (EIC, R1, R2, R3 all raise it, no conflict)
1. SC-1 (separately trained comparisons confound the method effect): EIC through W3 and Q3, R1 W2, R2 W1, R3 W7; DA M4 corroborates. Verified, with a measured floor (check (e)).
2. SC-16 (density of the abstract and Sec. 5): all four, severity Minor; DA m6 corroborates.

**[CONSENSUS-3]**
3. SC-7 (share is near-mechanical for pair-indexed corrections): EIC W1, R2 W2, R3 W5; R1 corroborates through W6; DA M1 and its strongest counter-argument.
4. SC-2 (TDE AUC bound and its post-hoc margins): EIC W2, R1 W1, R2 W9 (as presentation); DA M2.
5. SC-9 (protocol sensitivity of the case-level part and the weight of the reporting protocol): EIC W4, R1 W3(b), R3 W5; DA M5.

### Corroborated findings (2 seats, no conflict)
SC-3 (multiplicity: R1, R3; DA m2); SC-6 (control grid: R1, R2; EIC Q2); SC-11 (Waterbirds and breadth: R3, EIC W11); SC-12 (positioning against existing diagnostics: R3, EIC); SC-13 (scope: EIC, R2); SC-14 (SGCls/SGDet: R2, R3); SC-15 (zero-shot: R1, R2); SC-17 (intervals: R1, R3).

### Single-reviewer findings (retained, no consensus label)
SC-4 (R1 W3(b); the text tension is verified, check (g)); SC-5 (R1 W4; the background-mass premise is verified, the consequence is not tested); SC-8 (R1 W6); SC-10 (DA M6, R3 W9); SC-18 (R1; **[UNVERIFIED]**); SC-19.

### DA CRITICAL adjudication

There are **0 DA CRITICAL issues**. Nothing to validate, reject or leave unresolved, and no `[DA-CRITICAL-VS-ACCEPT]` condition arises. The six MAJOR items were treated as findings tracked outside the 4-seat consensus count and routed to the roadmap: M1 to R6-5 and R6-11, M2 to R6-2 and R6-8, M3 to R6-9 (control grid) and R6-14, M4 to R6-1, M5 to R6-3, R6-16 and R6-17, M6 to R6-16.

## Points of Disagreement and Arbitration

**A1. Is the PE-Net AUC "rise" a finding? (R1 W2 says not identified; the paper, R3 and the DA's Observations section treat it as evidence that the instrument can detect gains.)**
- DA's Observations note that "the PE-Net result shows the split can detect gained discrimination when it exists, which is what makes the TDE null informative". R1 shows that two nominally exchangeable baselines differ by more than the PE-Net rise.
- **Resolution**: R1 is right on the evidence and the DA's argument cannot stand on the current numbers. The instrument's ability to detect a gain is then not shown by PE-Net; it is shown by the simulations and by the controlled CLIP-versus-geometry study, where the models share a training procedure. **Rationale**: evidence first. The finding reproduces on the committed arrays (check (e)). Remedy is wording plus one re-analysis (R6-1); the PE-Net mean-recall case-level part may still be a real signal against the floor, which the authors can test. Not a reason to drop PE-Net from the paper (R6-1 keeps it as an exploratory, system-level comparison).

**A2. Severity of the AUC-bound problem: Major (R1, DA, EIC) or presentation (R2 W9, R3 not raised).**
- **Resolution**: Must-fix, but as wording (R6-2). The abstract must name the weighting beside each bound, state which weightings establish equivalence at which margin (check (d)) and drop "falls by 0.015" as a finding. A power curve (R6-8) is should-fix. **Rationale**: the arithmetic is verified and the cost is a sentence; the power analysis is R1's request and valuable but not needed for an honest bound.

**A3. Is the headline 87% "close to a restatement of how the baseline is built" (DA strongest counter, EIC W1, R2 W2)?**
- R2 adds that DLFE and IETrans are explicit per-predicate or prior-adding corrections, so their 94% and 97% are expected by construction, and only TDE's was non-obvious. R1 and R3 are neutral; R1 notes that the paper's own Prop. 1 shows group-level is not "prior fit", and the oracle contrast (+0.5068, all case-level) shows the share is not forced by the metric.
- **Resolution**: partly accepted. The share is a result about a cell-indexed prior only if the reader knows the correction is cell-indexed; the paper should say that plainly and put the informative content (the mechanism, the control and the AUC) first (R6-5). I do not adopt the DA's claim that the decomposition "adds nothing beyond the logit analysis": the logit analysis explains TDE, while the split is what lets DLFE, IETrans and PE-Net be compared by the same rule, and R1 confirms the oracle contrast is not mechanical. **Rationale**: expertise and evidence; the DA's reading is a judgement and **not verified**.

**A4. Scope remedy (carried from round 2, A3): narrow or extend?**
- EIC: add a modern debiasing method and one end-to-end model, or retitle. R2: add a from-scratch rebalancing method (CFA, GCL). DA: scope is honest. R3: scope the generality claim in the non-SGG studies.
- **Resolution**: no further extension is required for this decision; PE-Net was the extension requested in round 2. Floor is wording (R6-5, R6-6); an additional method is a consider item (listed under R6-12/R6-19 as optional). **Rationale**: author autonomy and feasibility; the added value of one more checkpoint is lower than that of the noise-floor analysis.

**A5. LA as an operating-point control (R1 W3(a): "LA is not a control for TDE's operating-point movement") versus the paper's use of it.**
- R1 shows that removing the cell-varying frequency branch gives a significant mean-recall case-level part (+0.0053) with an AUC change of -0.00001, so a global LA does not reproduce TDE's pair-varying movement. R2 W3 wants a tau sweep. EIC wants the tau choice justified.
- **Resolution**: should-fix (R6-9). The paper already says the match is specific to K=50 under the constraint; what is missing is evidence that a matched control exists at the other protocols and a cell-wise-prior version. **Rationale**: the claim as worded is already scoped; this strengthens, not repairs.

**A6. R3's view that Waterbirds is weaker than Sec. 6 states, versus the round-2 decision to promote it.**
- **Resolution**: keep it in the body (round-2 adjudication stands: it is the positive case) and add its caveats (R6-12). R3's own numbers are consistent with the supplement; the matched case-level value +0.1138 and the AUC +0.0031 are in the paper's supplement per R3 (**[UNVERIFIED]** by me for the matched value; the AUC and unmatched values are verified in the paper text).

**A7. Unresolved dissent.** (i) Whether the "primary" protocol and weighting were fixed before the gain was seen cannot be resolved from artifacts; the paper now discloses post-hoc status for TDE and IETrans, and DLFE and PE-Net are out-of-sample for the protocol (R3, DA). (ii) Whether a pair-ranking contribution exists in TDE's mean-recall case-level part is untested (R1 W4). (iii) R1's jackknife and half-sample figures are unverified. (iv) Whether the instrument's value for the SGG community is "primarily an evaluation methodology" (R2) or a general diagnostic (R3's requirement) is a positioning choice for the authors.

---

## Decision Rationale

Relative to round 2 the panel's concerns have moved from what the analysis covers to what the abstract and Sec. 5 say about three kinds of result. First, the TDE results (87% group-level, the K=50 control, the AUC bounds) hold on the evidence I rechecked, and the paper states their conditions. Second, the cross-release results (PE-Net, DLFE, IETrans AUCs) are not separable from training and codebase differences: the committed arrays contain two separately trained MOTIFS baselines whose relation-weighted AUC differs by -0.0060 and whose pair-weighted AUC differs by -0.0181, larger than PE-Net's +0.0050 and DLFE's +0.0029 and on a par with the pair-weighted TDE fall the abstract reports. Third, the claim that the case-level part is an operating point spent on existing predicate discrimination does not cover pair ranking and foreground/background movement, which R1 shows are large (background mass 0.855 to 0.021 for TDE) and which no analysis audits. I chose Minor over Major because every remaining must-fix is a wording change or a small re-analysis on arrays already in the repository, the decomposition and the TDE audit are correct, and no seat or check found an arithmetic discrepancy. I chose Minor over Accept because R6-1 and R6-2 change what the abstract may say, and a revision that keeps "its within-pair AUC rises" unqualified would move the decision to Major. The paper's candour is a reason to expect a clean revision.

---

## Part 2: Revision Roadmap

> IDs `R6-n` are transport references in immutable source-traceability order (first source seat in panel order EIC, R1, R2, R3, DA, then within-card order) for items new or re-raised in round 3; the round-2 ID is given where one exists. They are not a work rank. The obligation class is an editorial gate. Severity is transported from the driving finding. `proposed_targets`: unavailable, because no bound block manifest was supplied; targets are given as sections. Effort is in person-days for one author who has the repository and a working environment, and "feasible" means feasible by 16 Nov 2026 under the 8-page limit; effort estimates are the synthesizer's, not the seats'. Author triage is not collected here.

Page-budget note: the body is at 8 pages. Net additions in the must-fix tier are about one table row group (the noise-floor rows) and clause-level edits to the abstract, Sec. 3, Sec. 5 and Sec. 7. Offsetting cuts: the abstract's numeric chain (R6-6), the Sec. 6 non-SGG paragraph (R6-12) and the "Why" mechanism text if needed; the supplement has room (40 pages).

### Required Revisions (Must Fix)

| Ref | Revision item (fix) | Type | Sub-claims | Severity (transported) | Source seats | Effort | Feasible by 16 Nov, 8 pp | Round-2 link |
|---|---|---|---|---|---|---|---|---|
| R6-1 | Noise floor for cross-release comparisons. Report the between-baseline differences (`dlfe_base` minus `none`: AUC under all four weightings, mean-recall split) as an empirical floor next to PE-Net, DLFE and IETrans; state PE-Net's AUC change as "within the range of two separately trained baselines" unless it exceeds it under a stated weighting, and drop "its within-pair AUC rises" from the abstract and "Where a method does gain discrimination, the split shows it" from Sec. 5 (or mark them exploratory and system-level); replace the DLFE "controlled" description by the same-network contrast `dlfe` against `dlfe_soft` (AUC change 0 by construction) and report the DLFE mean-recall split against `dlfe_soft`; recompute and report PE-Net's mean-recall case-level part against the baseline pair's case-level part (R1: +0.0007 [-0.0016, +0.0030], **[UNVERIFIED]**). Also say the baselines come from different releases, so the floor is an example, not a variance estimate. | re-analysis + re-framing | SC-1 | Major | R1 W2; R2 W1, Q4; DA M4; R3 W7; EIC W3, Q3 | 1 to 2 (arrays cached; code `wager.rank.within_cell_auc_contrast`; my check ran in minutes at B = 200) | Yes; about 4 table rows, offset by R6-6 | R5-6, R5-13, R5-14 |
| R6-2 | TDE ranking sentence. State the weighting beside each bound (relation 0.0038, comparison 0.0077, pair 0.0229, predicate 0.0279) and which margin each passes (check (d)); say the predicate weighting, the one nearest mean recall, establishes equivalence at no margin; say the two head-heavy weightings carry the narrow bounds; present the pair-weighted fall (-0.0153, upper limit -0.0004) as exploratory and as smaller than the cross-release floor under the same weighting (R6-1); give the margin's provenance (geometry on a reconstructed split) in the main text; align the conclusion ("no weighting of TDE's within-pair AUC shows a gain") with the abstract. | re-framing | SC-2 | Major (R1, EIC, DA); Minor (R2) | EIC W2; R1 W1; R2 W9; DA M2 | 0.5 | Yes; no page cost | R5-4, R5-5 |
| R6-3 | Declaration consistency. Reconcile Sec. 3 ("the family is fixed before any gain is read") with Sec. 5 (primary quantities declared after the TDE and IETrans results were seen); say which analyses are confirmatory (DLFE, PE-Net, run after the declaration) and which are post hoc (TDE, IETrans); keep the sentence that the declaration was made before DLFE outputs existed. | re-framing | SC-4 | within Major (R1); Minor (DA) | R1 W3(b); DA m2 | 0.25 | Yes | R5-5, R5-20 |
| R6-4 | Scope of the case-level reading. Restate that the AUC audits predicate order given the labelled pair; that mean recall's case-level part also credits pair ranking and foreground/background movement; and replace "operating point spent on existing predicate discrimination" accordingly. Give the background-mass numbers as the reason (none 0.855, TDE 0.021, LA1 0.651, `dlfe_base` 0.682, PE-Net 0.560; check (f)). The audit itself is R6-10. | re-framing | SC-5 | Major (R1) | R1 W4 | 0.5 | Yes | R5-8 |
| R6-5 | What is expected by construction and what is informative. State that DLFE and IETrans apply explicit per-predicate or prior-adding corrections and that a high group-level share is expected for any correction indexed by the cell; present the informative results (TDE's mechanism: one shared vector, +0.75 with the log prior; the control; the AUC) first; carry the grouping dependence (18%, 87%, 90%) in the same sentence as the 87%; fix the "three" versus "four" checkpoint count between the abstract and the intro; keep the title decision with the author. | re-framing | SC-7, SC-13 | Major (EIC, R2, R3, DA) | EIC W1, W3; R2 W2; R3 W5; DA M1, m1 | 0.5 to 1 | Yes | R5-1, R5-3 |
| R6-6 | Abstract and bases. Cut the abstract to three findings plus one protocol clause; use one basis for "points" (the abstract's "11 and 21 points" mixes micro-pooled and official: IETrans is +0.2204 micro and +0.2128 official, check (h)); move the AUC bounds and the DLFE/IETrans/PE-Net numbers to Table 1; define ng, gc, r, c in captions; give N once (183,642 versus 183,639 in the proper-score analyses). | re-framing | SC-16 | Minor (all); Major (EIC) | EIC W7; R1 W13; R2 W9; R3 W8; DA m6 | 1 | Yes; this is the vehicle that pays for R6-1 and R6-2 | R5-10 |

### Suggested Revisions (Should Fix)

| Ref | Revision item (fix) | Type | Sub-claims | Severity | Source seats | Obligation | Effort | Feasible by 16 Nov, 8 pp | Round-2 link |
|---|---|---|---|---|---|---|---|---|---|
| R6-7 | Multiplicity. Define a family (methods x weightings x subsets), apply Holm or report adjusted limits, and label as exploratory every positive claim that does not survive: the pair-weighted TDE fall, PE-Net, DLFE (+0.0029, lower limit moves across zero with the replicate count), the zero-shot AUC fall (relation weighting only; R1 reports that weighting carries 11% of the weight in that subset, **[UNVERIFIED]**). Do not use a post-hoc subset in the main text with only the weighting that excludes zero. | re-analysis + re-framing | SC-3 | Major (R1); Minor (R3, DA) | R1 W7; R3 W11; DA m2 | should_fix | 0.5 to 1 | Yes | R5-20 |
| R6-8 | Power of the AUC bound. Planted-signal simulation at VG150 cell sizes: with what probability does each weighting flag a true ranking gain of 0.01 or 0.02? Report the minimal detectable effect per weighting. | new experiment (simulation) | SC-2 | Major (R1) | R1 W1, Q4; R2 detailed | should_fix | 2 | Yes | R5-4 |
| R6-9 | Control grid. A tau sweep for LA (0.25 to 1.5) at all six protocols (results for tau = 0.5 exist in `results/sgg_recall_split_la0.5_vs_none.json`), and a cell-wise-prior control (baseline logits minus tau times the cell-conditional log prior) as the matching reference for a pair-varying shift; or state in Sec. 5 that LA matches TDE's group-level kind, not its operating point. | re-analysis | SC-6 | Major (R1, R2) | R1 W3(a); R2 W3, Q2; EIC Q2; DA alt. path 2 | should_fix | 2 to 3 | Yes | R5-2, R5-12 |
| R6-10 | Pair-ranking audit. Mean-recall split with pair ranks frozen at the baseline's, or a within-image AUC of annotated pairs against background, for TDE and LA1; report how much of TDE's +0.0130 case-level part survives. | new analysis | SC-5 | Major (R1) | R1 W4, Q3 | should_fix | 2 to 3 (evaluator replay code exists; needs a rank-freezing option) | Likely; check feasibility in the first week | new |
| R6-11 | AUC at the finer groupings. Within-cell AUC change for TDE (and PE-Net) at the class-pair x position and class-pair x size-tercile refinements already built for the share analysis. | re-analysis | SC-8 | Major (R1) | R1 W6, Q5; EIC W1 | should_fix | 1 | Yes | R5-3 |
| R6-12 | Non-SGG breadth. State in the main text that the Waterbirds AUC gain is +0.0031, that the matched case-level part is +0.1138 (R3; **[UNVERIFIED]**), and that it is one probe pair and one seed; add per-(label x background) contributions or a worst-group decomposition; label CIFAR-100-LT and 20 Newsgroups as estimator behaviour under label-derived cells, not audits, and move them out of the argument for breadth. | re-framing + small analysis | SC-11 | Major (R3); Minor (EIC) | R3 W1, W2, W3; EIC W11 | should_fix | 1 to 2 | Yes, with offsetting cut of Sec. 6 text | R5-15 |
| R6-13 | Positioning, quantitatively. Add one table row group comparing the split with Murphy resolution change (or per-model conditional permutation importance difference) for TDE, PE-Net and Waterbirds; say which conclusions are shared. Add the references the seats propose that exist (see R6-19), checking each. | re-analysis + re-framing | SC-12 | Major (R3); Minor (EIC) | R3 W4; EIC W12 | should_fix | 1 to 2 | Yes | R5-17 |
| R6-14 | SGCls/SGDet and PE-Net protocol. Say "to within 0.0007" for the SGDet replay (R2's Tab. 37 reading, **[UNVERIFIED]**) instead of "reproduces"; state that the AUC claims in SGCls/SGDet are on the matched subset; add one sentence on PE-Net's relation NMS versus the raw-probability AUC path and report `recalls_without_rel_nms`. | re-framing | SC-14 | Major (R2 W4); Minor (R2 W5) | R2 W4, W5; R3 W6; EIC W9 | should_fix | 0.5 | Yes | R5-14, R5-19 |
| R6-15 | Zero-shot reporting. Give the raw zero-shot gain with its 50% case-level share (check (i)); soften "not a better ranking" to "no detected improvement in ranking" for the comparison weighting (interval covers zero); move the DLFE and IETrans zR@50 drops (-0.0279, -0.0779 per R2, **[UNVERIFIED]**) into the main text; fix the "Appendix Q.11" cross-reference to Q.7. | re-framing | SC-15 | Minor (R1, R2) | R1 W8; R2 W6 | should_fix | 0.5 | Yes | R5-17 |
| R6-16 | Reading rule and terminology. A two-line note that "group-level" means "survives within-cell shuffling", not a demographic or subpopulation group; how to read the signs outside SGG (Waterbirds negative group-level part); soften the downstream claim (captioning, VQA) or cite evidence; one sentence that the split is descriptive and can be optimised. | re-framing | SC-10 | Major (DA); Minor (R3) | DA M6; R3 W3, W9, W10; EIC W5 | should_fix | 0.5 | Yes | R5-8, R5-22 |
| R6-17 | Reproducibility package. If R1's findings hold (**[UNVERIFIED]**: archive without prediction arrays, supplement paths following the renamed archive, lower-bound-only requirements, repository README and working name not scrubbed), ship the arrays or a checksum-verified download, align file names, pin Python and numpy, and confirm the anonymised bundle carries no repository README. | editorial | SC-18 | Minor (R1) | R1 detailed | should_fix | 0.5 to 1 | Yes | new |
| R6-18 | Interval validity. Use the refit delete-a-group jackknife as the primary interval for cell-based quantities where it is wider; state that matched-protocol intervals condition on the fitted calibrator; one sentence on the 88% real-data coverage in the main text. | re-framing | SC-17 | Major (R1); Minor (R3, DA) | R1 W5; R3 W11; DA m5 | should_fix | 0.5 | Yes | R5-11 |

### Consider

| Ref | Revision item (fix) | Type | Sub-claims | Severity | Source seats | Effort | Feasible |
|---|---|---|---|---|---|---|---|
| R6-19 | Small items: (a) randomization p floor note (999 shifts give .001) and that the cyclic shift ignores image clusters (R1 W11); (b) the synonym merge removes TDE's largest movement and a recorded-label AUC penalises relabelling by construction; use the multi-label structure or an annotator-agreement ceiling (R1 W9; DA); (c) one sentence that the audited gain is body-predicate gain and tail effects are unassessed (EIC W10; R2 detailed); (d) heavy-tailed cell caveat and a minimum-cell sensitivity for the TDE share (R3 W11; DA m5); (e) truncate or flag share intervals above 1 (R1 W10); (f) a governance sentence on who declares the grouping (EIC Q7); (g) align CLIP-versus-geometry text in the supplement with the main text and note that the five seeds vary the head only (R1 W12); (h) typos and cross-references ("Appendix Q.11" is in R6-15; also "merging synonymous predicates ... Q.1, Q.2, Q.4" should be Q.2 and Q.8); (i) optional additional method (CFA, GCL or SHA-GCL) if a released checkpoint with cacheable logits exists, otherwise state why not; (j) references that exist per the seats: CFA (ICCV 2023), Scene Graph Generation survey (Neurocomputing 2024), Generative Compositional Augmentations (ICCV 2021), SGTR (CVPR 2022), Kirichenko et al. (ICLR 2023), Yang et al. (ICML 2023), Gneiting and Raftery (2007); treat every [UNVERIFIED] seat lead (RelTR, HiLo, RA-SGG, Oaxaca-Blinder, Idrissi et al., JTT) as unconfirmed until the authors check it; DB-SGG (arXiv:2308.05286) is withdrawn per R2 and should not be cited as a baseline. | editorial and small analyses | SC-9, SC-13, SC-15, SC-17, SC-19 | Minor | R1, R2, R3, EIC, DA | 1 to 2 in total | Yes |

(ID R6-n numbering is in source order: R6-1 to R6-6 must-fix, R6-7 to R6-18 should-fix, R6-19 consider.)

### Source-Traceability Checklist (source order, not a work order)

- [ ] R6-1 must_fix: noise floor; PE-Net, DLFE, IETrans AUC statements; DLFE against `dlfe_soft`
- [ ] R6-2 must_fix: TDE AUC sentence (weighting beside each bound)
- [ ] R6-3 must_fix: Sec. 3 versus Sec. 5 declaration; confirmatory versus post hoc
- [ ] R6-4 must_fix: scope of the case-level reading (pair ranking, background mass)
- [ ] R6-5 must_fix: expected-by-construction versus informative; share with its grouping range
- [ ] R6-6 must_fix: abstract density; one basis for "points"
- [ ] R6-7 to R6-18 should_fix; R6-19 consider (as in the tables)

### Editor's priority view (advisory; not part of the immutable core)

Ordered by decision weight and by how much each unblocks; the author may order differently.
1. R6-1 (the only gating item; also supplies the numbers R6-2 and R6-7 need, and a one-day re-analysis on cached arrays)
2. R6-2 (wording once R6-1 is in)
3. R6-4 and R6-3 (two short re-framing edits)
4. R6-5 and R6-6 (re-framing of the abstract; do these last among the must-fix items because they absorb the others)
5. R6-7 and R6-10 (should-fix with decision value: multiplicity, and the one untested mechanism)
6. R6-9, R6-8, R6-11 (control grid, power, finer groupings)
7. R6-12 to R6-18 as time allows

Suggested schedule against 16 Nov (33 days): days 1 to 3 R6-1 and the R6-10 feasibility check; days 4 to 10 the remaining must-fix wording (R6-2 to R6-6) with the abstract rewrite last; days 11 to 20 R6-7, R6-9, R6-11, R6-12, R6-14, R6-15; days 21 to 26 R6-8, R6-10 if feasible, R6-13, R6-16 to R6-18; keep the last week for compile, page-limit checks and a re-review. Nothing in the must-fix tier needs a GPU, a retrained model or a new checkpoint. R6-10 is the only item whose feasibility I would not assert (it needs an option in the evaluator replay).

### Response Letter Template
Use `templates/revision_response_template.md` to respond to every item R6-1 to R6-19, including a stated decision for each should_fix and consider item. Where the author declines an item, say so; a decline stays visible and unresolved. Round-2 items marked "partially resolved" or "re-raised" in the status table should be answered under their R6 item.

---

## Part 3: Reviewer Report Summary (Appendix)

- **Journal-Fit Reviewer (EIC)**: Major Revision (borderline; leaning Weak Accept on the contribution) | Confidence 4. Original and correct on the numbers checked; concerns are the near-mechanical 87% for pair-indexed corrections, the K and protocol dependence of the control, a narrow dated base, a protocol-sensitive reporting standard and density. Strongest: SC-7, SC-2, SC-13, SC-16.
- **Reviewer 1 (Methodology)**: Weak Accept (borderline; conditional) | Confidence 4. Reproduced the headline split, TDE AUCs and control from the shipped arrays; found that two separately trained MOTIFS baselines differ by -0.0060 in relation-weighted AUC (verified here), that the case-level part also credits untested pair-ranking movement (premise verified), and that positive claims are uncorrected for multiplicity. Strongest: SC-1, SC-2, SC-5, SC-3.
- **Reviewer 2 (Domain)**: Weak Accept (borderline) | Confidence 4 (SGG), 3 (statistics). Clean evaluator replay; the control match is one protocol cell; separately trained comparisons; DLFE and IETrans shares expected by construction; SGCls/SGDet subset; post-2023 references. Strongest: SC-1, SC-7, SC-6, SC-14.
- **Reviewer 3 (Perspective)**: Weak Accept (borderline-positive) | Confidence 3. The SGG findings are persuasive and the negative-control design is the contribution; the generality claim outruns the non-SGG evidence; Waterbirds is weaker than Sec. 6 states; the reporting protocol is heavy; "group-level" may be misread. Strongest: SC-11, SC-12, SC-9.
- **Devil's Advocate**: findings only. Key challenge: the 87% is close to a restatement of how the baseline is built, the ranking null rests on post-hoc margins, and the normative payoff is asserted; 0 Critical, 6 Major, 6 Minor.

## Closing

We invite a revised manuscript that addresses the six required items and states a decision on each suggested item. The audit is careful and candid. The revision is mostly a matter of making the abstract and Sec. 5 say what the evidence supports about three things: which AUC changes exceed the difference between two separately trained baselines (R6-1), what the TDE bounds do and do not establish (R6-2), and what the case-level part of mean recall does and does not measure (R6-4). A further review will be needed after the revision.

*Synthesis scope note: this letter synthesizes and arbitrates the five Phase 1 reports; it adds no new review comments beyond the verification of claims the seats made (the baseline-to-baseline AUC check is a reproduction of R1's finding, extended by the pair weighting and the implications section, which is the synthesizer's reading and is labelled as such). Effort and feasibility figures are the synthesizer's estimates.*


## Attachment: Acronym Check (advisory, #849)

```
### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not in this input: English abstract, Chinese abstract.
Not checked:
- Body, line 303: FREQ (the initials before its parentheses do not spell it)

| Scope | Line | Rule | Acronym | Uses |
|---|---|---|---|---|
| Body | 1 | Not defined | CVPR | 48 |
| Body | 3 | Not defined | COPY | 10 |
| Body | 3 | Not defined | DO | 10 |
| Body | 3 | Not defined | NOT | 10 |
| Body | 3 | Not defined | REVIEW | 10 |
| Body | 13 | Not defined | ID | 1 |
| Body | 28 | Defined after first use | TDE | 52 |
| Body | 40 | Not defined | AUC | 27 |
| Body | 46 | Not defined | DLFE | 7 |
| Body | 46 | Not defined | IETran | 11 |
| Body | 48 | Not defined | PE | 5 |
| Body | 77 | Defined again | TDE | 52 |
| Body | 78 | Not defined | MOTIFS | 7 |
| Body | 79 | Not defined | VG150 | 5 |
| Body | 91 | Not defined | SGCl | 3 |
| Body | 92 | Not defined | SGDet | 3 |
| Body | 131 | Not defined | CNN | 2 |
| Body | 132 | Not defined | RTPB | 1 |
| Body | 136 | Not defined | HX | 4 |
| Body | 136 | Not defined | VQA | 2 |
| Body | 137 | Not defined | EH | 1 |
| Body | 137 | Not defined | EY | 1 |
| Body | 179 | Not defined | ROC | 1 |
| Body | 284 | Not defined | LA | 6 |
| Body | 298 | Not defined | AUCc | 1 |
| Body | 298 | Not defined | AUCr | 1 |
| Body | 303 | Not defined | MLP | 10 |
| Body | 305 | Not defined | CLASS | 6 |
| Body | 327 | Not defined | SGG | 1 |
| Body | 330 | Not defined | SUM | 1 |
| Body | 368 | Not defined | CLIP | 9 |
| Body | 514 | Not defined | MO | 1 |
| Body | 515 | Not defined | TIFS | 1 |
| Body | 528 | Not defined | ERM | 1 |
| Body | 534 | Not defined | CIFAR | 1 |
| Body | 534 | Not defined | LT | 1 |
| Body | 540 | Not defined | ViT | 1 |
| Body | 566 | Not defined | MRR | 1 |
| Body | 588 | Not defined | AAAI | 1 |
| Body | 595 | Not defined | ACM | 2 |
| Body | 596 | Not defined | ICML | 3 |
| Body | 620 | Not defined | BMVC | 1 |
| Body | 624 | Not defined | ICCV | 2 |
| Body | 631 | Not defined | ECCV | 2 |
| Body | 638 | Not defined | ICLR | 1 |
| Body | 653 | Not defined | PCPL | 1 |
| Body | 662 | Not defined | IJCAI | 1 |
| Body | 690 | Not defined | BMC | 1 |
```
