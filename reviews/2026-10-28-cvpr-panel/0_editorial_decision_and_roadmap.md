# Editorial Decision Package (Round 4)

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

`criteria_binding_unavailable`: no target-criteria binding was supplied and all five cards disclose this. No venue-alignment claim is made. The standard Synthesis Protocol was used (no sprint contract), so no scoring matrix or failure-condition arithmetic applies.

Same-model-family panel: all five Phase 1 seats ran on one model family (Sonnet) from one provider, and this synthesis is by an agent whose runtime identifies it as the same family. Agreement among seats is weaker evidence than agreement among independent reviewers, and repeated findings may reflect one shared reading of the same passage. Full provenance is in `_panel_provenance.md`. Because of this limit, the claims that decide the outcome were rechecked against `results/*.json`, the committed arrays under `data/vg_motifs/`, the experiment scripts and the text extracts (section "Verification"). Seat claims that were not rechecked are marked **[UNVERIFIED]**.

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Venue configuration**: simulated CVPR 2027 panel (configured perspective only)
- **Review target**: `cvpr2027/paper.pdf` (8 pp body + references; 10 pages in all) and `cvpr2027/supp.pdf` (40 pp), repository commit `ea0efe7` (the round-3 revision; the "Status after the round-3 revision" table at the end of `reviews/2026-10-14-cvpr-panel/0_editorial_decision_and_roadmap.md`).
- **Decision date**: 2026-10-28
- **Review round**: 4 (mode full, Phase 2). Round-3 package: `reviews/2026-10-14-cvpr-panel/` (commit `6b8f1b9`; roadmap IDs `R6-n`). Round-4 IDs are `R7-n`. The dispatcher instructed each seat not to read other panels' or seats' outputs.
- **Submission deadline**: 16 Nov 2026 (19 days from the decision date); 8-page body limit.

## Review Panel Provenance (summary)

Five role-separated seats (EIC, R1, R2, R3, DA), each a fresh AI subagent run on Sonnet, launched concurrently by an Opus orchestrator, each instructed not to read other panels' or seats' outputs. The instruction is recorded as given; this synthesizer cannot confirm compliance. Accountable human: Quang-Vinh Dang (British University Vietnam). No typed `review-panel-provenance/1.0` artifact or digests were supplied, so none are reported. Axes: role-separated true; blind to peer outputs true (as instructed); model-family distinct **false**; provider distinct **false**; human-reviewer distinct false. No binary independence claim is made. No cross-model decision check was run. R1 reported its checkout as HEAD `2300e8e`, not the requested `ea0efe7`; the dispatcher did not explain this (see provenance file).

---

## Decision

### Minor Revision (accept with conditions)

**Confidence in the decision: medium-low.** Two of the four scoring seats recommend Major Revision (EIC: borderline, leaning Weak Accept on the contribution; R2: "accept in principle if M1 and M3 are fixed"), and two recommend Weak Accept conditional on claim edits (R1, R3). The Devil's Advocate raised 0 CRITICAL issues (7 MAJOR, 6 MINOR). Seat recommendations were not counted as votes; the category was set from the evidence below.

All six round-3 must-fix items (R6-1 to R6-6) were acted on; four are resolved as requested and two (R6-5, R6-6) are partly resolved (table below). No seat or check found an arithmetic defect: R1 rebuilt the headline split, the AUC changes under four weightings and the cross-release floor from the shipped arrays; the EIC ran `experiments/verify_manuscript_numbers.py` (89 numbers trace; not rerun by me); DA and R2 spot checks agree; my checks (a) to (e) agree with the stored JSON.

What changed in round 4 is where the problem sits. The TDE results (87% group-level, the K = 50 control, the AUC bounds with their weightings) are no longer the target. The new decision-bearing finding is about PE-Net, the one method the paper uses to show the instrument can find case-level gain:

1. PE-Net is scored on its own graph-constrained path with relation-level NMS (`rel_nms`), and the TDE-release baseline is not. The repository's own no-NMS replay lowers PE-Net's mR@50 from 0.3142 to 0.2961 and R@50 from 0.6523 to 0.6302 (about 11% of the official mR gain). The paper never reports these numbers (check (a)). This is the item round 3 asked for as a should-fix under R6-14 ("report `recalls_without_rel_nms`"); it was not done.
2. PE-Net's case-level part is read against the wrong null: one realised difference between two MOTIFS baselines, not an operating-point control built from PE-Net's own scores (check (e)).
3. Two labels in the abstract and conclusion overreach: IETrans+Rwt is called a "prior correction" (check (c)), and the "floor" is a single realised difference whose interval, like DLFE's "training difference", excludes zero (check (d)).

I chose Minor over Major because every must-fix item below is a wording change, a re-labelling, or one re-analysis of PE-Net on a single method; the qualitative PE-Net result (a case-level part above the baseline pair's) does not depend on the NMS path (check (a): the no-graph-constraint protocols, which `rel_nms` does not touch, give +0.0190, +0.0216 and +0.0346 against a baseline-pair value near zero or negative); and the decomposition, the TDE audit and the control are correct. I chose Minor over Accept because R7-1 and R7-2 change what the abstract may say about PE-Net. **If the next version keeps "PE-Net ... +0.170, 86% group-level, case-level +0.024 far exceeds ..." without the evaluator caveat and the operating-point qualification, the editor would move to Major.** Two seats already hold Major; this is a medium-low-confidence call.

Editorial lines for the sprint/audit trail:
- `da_critical_adjudications: []` (the DA's CRITICAL list is empty; its stated reason is that every central claim is stated with its condition)
- `editorial_decision=minor_revision`

---

## Round-3 items: status at commit ea0efe7

"Resolved" means the change is in the paper and no round-4 seat re-raises it as a defect. "Partly" means the change is in the paper and a seat raises a residual or a narrower form of the same concern. "Re-raised" means a seat raises the item against the current text and the authors' status table does not claim it. The authors' status table (end of the round-3 letter) claims R6-1 to R6-6 only; R6-7 to R6-19 were should-fix or consider and were not claimed. Evidence is the round-4 cards plus checks of the text extracts and results files.

| Ref | Status | Evidence at ea0efe7 | Residual routes to |
|---|---|---|---|
| R6-1 noise floor for cross-release comparisons | **Partly** | Done as requested: `baseD` row in Tab. 1 (mR@50 +0.0206, case-level +0.0007 [-0.0016, +0.0030]; AUC -0.0060 [-0.0099, -0.0011] relation, +0.0017 comparison); "its within-pair AUC rises" and "where a method does gain discrimination, the split shows it" are gone; DLFE's +0.0029 is described as a training difference with the same-network contrast `dlfe` vs `dlfe_soft` (AUC exactly 0, `sgg_cross_release_floor.json`). Residual: the abstract still uses the floor as a noise null ("far exceeds the +0.001", "does not exceed their 0.006 spread"); R1 W1-W3, R2 M4, R3 F8, EIC W3, DA M4, M5 all say one realised difference cannot bound training variability. R1 W2: the AUC half is selective across baselines and weightings. | R7-2, R7-3, R7-10 |
| R6-2 TDE ranking sentence | **Resolved** | Weighting beside each bound in Sec. 5 and the abstract ("0.0038 to 0.028 under four weightings, tightly only under the two that favour head predicates"); equivalence margins and the post-hoc status disclosed; pair-weighted fall called exploratory. Verified (check (f)). The predicate weighting still passes no margin, which the paper says. Residual (EIC W2, R1 W4, DA M3): power and the yardstick, i.e. R6-8, which was should-fix and not done. | R7-9 |
| R6-3 declaration consistency | **Resolved** | Sec. 3 no longer says the family was fixed before any gain was read; Sec. 5 (lines 365-369 of `paper_text.txt`) says declared after TDE and IETrans, before DLFE outputs existed. No seat re-raises the textual tension. R1 W7 and DA M7 still note that the primary family is post hoc for TDE, which is disclosed. | none (R7-8 for multiplicity) |
| R6-4 scope of the case-level reading | **Resolved** | "How to read the split" (lines 460-463): the AUC audits predicate order for a labelled pair; mass given to no relation 0.855 / 0.021 / 0.651 (verified, `sgg_cross_release_floor.json` `background_mass`). No seat re-raises. The pair-ranking audit R6-10 remains undone and unmentioned by round-4 seats. | R7-18 (consider) |
| R6-5 expected-by-construction vs informative; share with its grouping range; checkpoint count | **Partly** | Abstract says four checkpoints, one run each, and carries 18% (subject cells) beside 87%. Residual: EIC W3, W4, R2 M6, R3 F3, DA M1 and M5 still read the 87% as conditional on the class-pair cell and the title as field-level; R2 M3 finds IETrans mislabelled (check (c)). | R7-4, R7-5, R7-11 |
| R6-6 abstract density and bases | **Partly** | Abstract shortened, one basis for gains (micro-pooled decimals), acronyms defined. Residual: EIC W1, R3 F7, DA m4 still count about 20 to 25 numerals; N = 183,642 (text) vs 183,639 (the AUC and floor analyses; verified in `sgg_cross_release_floor.json`, `n_relations: 183639`) still not unified (R1 M1). | R7-5, R7-17 |
| R6-7 multiplicity | **Re-raised** | Not done. Only "one secondary interval excluding zero is not read as a finding" (line 370-372). R1 W11 lists the secondary results that are read as findings (IETrans fall, unseen-triplet AUC, DLFE +0.0029, TDE ng@100 case-level). | R7-8 |
| R6-8 power of the AUC bound | **Re-raised** | Not done. EIC Q1, R1 W4, DA M3. | R7-9 |
| R6-9 control grid: tau sweep, cell-wise prior | **Re-raised** | Not done. R1 W5, R2 M5, DA M2 and alt. path 1 and 2 (a tau = 0.5 control exists in `sgg_recall_split_la0.5_vs_none.json` but is not reported). | R7-6 |
| R6-10 pair-ranking audit | **Not done; not re-raised** | No round-4 seat mentions it; R2 m1 (SGDet matched-pair choice) is an adjacent concern. | R7-18 |
| R6-11 AUC at finer groupings | **Partly re-raised** | Not done. R1 W9 and DA M1 re-raise the dependence of the share on the cell. | R7-5 |
| R6-12 non-SGG breadth / Waterbirds | **Partly** | The Waterbirds AUC +0.0031 [+0.0008, +0.0056] is now in the body (line 581). R3 F2 still reads the gain as calibration-dominated, wants a prior-shift control and a worst-group decomposition (F6: no DFR/last-layer comparison); DA m6; EIC does not raise it. | R7-13 |
| R6-13 quantitative positioning | **Re-raised** | Not done. R3 F1 (Oaxaca-Blinder, Ferro-Fricker), EIC W5. | R7-14 |
| R6-14 SGCls/SGDet; PE-Net rel-NMS path and `recalls_without_rel_nms` | **Re-raised, escalated** | Not done: the no-NMS replay is stored but never reported (check (a)). R2 M1 and R1 W1(d) re-raise it as a major finding. | R7-1 (must-fix) |
| R6-15 zero-shot reporting | **Partly** | The "Appendix Q.11" cross-reference is fixed (line 486 now cites Q.7). R1 W6 (post hoc subset, one weighting quoted) and R2 m2 (PE-Net absent from Tab. 36; its zR@50 is 0.1713 against 0.1102, both in the stored official printouts) remain. | R7-12 |
| R6-16 reading rule, terminology, downstream claim | **Partly** | The "group-level is not a lesser gain" paragraph stays; EIC W6, W7, R3 F4, F5, F9, DA M6 re-raise terminology, the normative payoff and a minimal protocol. | R7-16 |
| R6-17 reproducibility package | **Not claimed; partly re-raised** | EIC desk check: no names, no URLs, LLM statement present; archive metadata not inspected. R1 M5: replay needs Colab. | R7-20 |
| R6-18 interval validity | **Re-raised** | R1 W8: delete-a-group jackknife 7% to 25% wider than Tab. 1 **[UNVERIFIED]**; paper's own jackknife (+0.0088, +0.0173) is closer to R1's than Tab. 1's. | R7-15 |
| R6-19 small items | **Partly** | Q.11 reference fixed; R1 W10 (label ambiguity), R1 M2 to M4, DA m1 to m3, R3 F9, F10 re-raise most of the rest. | R7-19, R7-20 |

---

## Verification (read-only checks of the claims that decide the outcome)

No file other than the two deliverables was modified. The checks read `results/*.json`, `data/vg_motifs/wager_penet/summary.json`, `experiments/colab_sgg_rank.py`, `experiments/expand_penet_to_standard.py`, `experiments/run_sgg_penet_audit.py` and the text extracts, and ran short Python arithmetic on stored values. The repository working tree at HEAD (`a6c16c6`) differs from the reviewed commit `ea0efe7` only in files under `reviews/` (`git diff --name-only ea0efe7 HEAD`), so the manuscript, results and code are the reviewed ones.

### (a) R2: PE-Net is scored with `rel_nms`, the baseline is not

**Verified in the stored results, with one external premise unverified; implication: the headline PE-Net recall numbers mix evaluator and model, and the paper does not say so.**

- `results/penet_official_recall.json`, `models.penet`: official path (with `rel_nms`) mR@50 = 0.3142, R@50 = 0.6523; `replayed_without_rel_nms` mR@50 = 0.2961 (0.29606), R@50 = 0.6302. Differences -0.0181 and -0.0221. Against the baseline's official mR@50 of 0.1459 the official gain is 0.1683 and the no-NMS gain 0.1502, so about 10.8% of PE-Net's official mR gain is the evaluator path. Other protocols: mR@20 0.2583 to 0.2455, mR@100 0.3348 to 0.3131. The no-graph-constraint (ng) values are identical with and without `rel_nms` (the script comment says the same: "the no-graph-constraint recall is not affected").
- Does the paper mention it? Only that PE-Net's evaluator "applies a relation-level non-maximum suppression" and that a row-blocked version was used (supp. Q.6, lines 1879-1881; no mention in `paper_text.txt`). A search of both extracts for 0.2961, 0.6302, "without rel_nms" and "non-max" finds no no-NMS numbers. The stored replay exists in `results/penet_official_recall.json` and `data/vg_motifs/wager_penet/summary.json` (`recalls_without_rel_nms`) and is not cited.
- Does the audit use the NMS ranks? **Mean-recall split: yes.** `experiments/colab_sgg_rank.py` (PE-Net config `"rel_nms": True`, lines 115-128 and 357-372) builds the PE-Net `gc_rank` on the `rel_nms` path, `expand_penet_to_standard.py` says the stored `gc_rank` is "on the rel_nms path", and `run_sgg_penet_audit.py` records `"the variant's gc_rank follows it"`. So the +0.1703 / +0.1460 / +0.0243 gc@50 values and the 86% share are NMS-path numbers. **AUC and proper-score parts: no.** They use the raw softmax rows (`probs`, the `p[own]` array) and never see the NMS. The AUC side is NMS-free by construction, which is also why R2 W5 of round 3 said the two paths differ. The within-cell AUC for PE-Net is therefore unaffected by this confound; the recall split is.
- The baseline and the other checkpoints: in `colab_sgg_rank.py` only the `penet` configuration sets `rel_nms`. Whether the original TDE-release (Scene-Graph-Benchmark) evaluator has `rel_nms` at all is R2's premise ("to my knowledge no") and I did not check it externally: **[UNVERIFIED]**. The code path shows the baseline is not given it in the audit.
- What survives: the case-level part of PE-Net's mean recall in the protocols `rel_nms` does not touch. `results/sgg_recall_split_penet_vs_none.json`: ng@20 +0.0190, ng@50 +0.0216 [+0.0148, +0.0285], ng@100 +0.0346 [+0.0256, +0.0437]; the baseline-pair case-level values in `sgg_recall_split_dlfe_base_vs_none.json` at the same protocols are +0.0013, -0.0044 [-0.0087, -0.0002], -0.0021. So the direction "PE-Net's case-level part exceeds the baseline pair's" does not depend on NMS. The NMS-free gc@50 split itself cannot be recomputed from committed arrays: `variant_penet.npz` holds `probs`, `gc_rank`, `ng_rank` only, and the no-NMS ranks (`extra_gc`) are computed in the script but only their aggregate recalls are saved. R1's argmax-only proxy (PE-Net ΔmR 0.1703 to 0.1546, case-level 0.0250, and 9.7% of rows with two or more predicate hits against 0.7% for the baseline) is **[UNVERIFIED]**; I did not repeat it.
- Implication: the abstract's "+0.170" and "86% group-level" are protocol-dependent by about 10% of the gain; the "far exceeds" sentence needs the NMS-free protocols beside it, or a rerun that saves the no-NMS ranks. The AUC conclusions for PE-Net stand as far as they go.

### (b) R1: IETrans's "four times" the floor

**Verified; the ratio holds for one weighting only. Implication: the sentence needs its weighting or must go.**

- Where: "IETrans's relation-weighted fall, −0.0238, is four times it" is in supp. Q.6 (line 1900), not in the main text; the main text (lines 505-512) states the fall and its synonymy confound without a ratio.
- Numbers, `results/sgg_auc_label_weighting.json` (IETrans vs none, B = 1,000) against `results/sgg_cross_release_floor.json` (`dlfe_base` vs none): relation -0.0238 [-0.0272, -0.0187] vs -0.0060 [-0.0099, -0.0011], ratio 3.97; pair -0.0274 [-0.0521, -0.0160] vs -0.0181 [-0.0356, -0.0058], ratio 1.51, intervals overlap; predicate -0.0362 [-0.0888, +0.0060] vs -0.0256 [-0.0557, +0.0075], ratio 1.41, both cover zero; comparison -0.0093 [-0.0185, -0.0001] vs +0.0017 [-0.0072, +0.0109], opposite sign (ratio meaningless). R1's "about 1.5 times under pair and predicate" is right.
- Implication: "four times" is a statement about the relation weighting. Under the weightings closest to mean recall the IETrans fall is within what two separately trained baselines differ by. Together with the paper's own point that IETrans has no baseline of its own and that a fall may be synonymy, the IETrans AUC fall is not a finding at this evidence level. The abstract does not state it; the body should carry the floor beside it.

### (c) R2: IETrans+Rwt called a "prior correction"

**Verified as an inconsistency between the abstract/conclusion and the body. Implication: relabel.**

- Abstract line 022: "DLFE and IETrans, also prior corrections"; Conclusion (lines 600-601): "On three released prior-correcting PredCls checkpoints the gains are almost entirely group-level".
- Body (lines 497-501, supp. O.2 and Q.8): IETrans "relabels training data from general to specific predicates ... and adds the training log-prior at test time; its released ... checkpoint is the IETrans+Rwt variant, also trained with a reweighted loss". The supplement says its effect "cannot be attributed to relabelling" and there is no IETrans baseline.
- Reading: the released system does include a test-time prior term, so "prior-correcting" is not false, but it is a relabel + reweight + prior system compared against a differently fused, separately trained baseline. Only TDE (same weights) and DLFE against `dlfe_soft` are controlled comparisons. The 97% share is expected for a cell-indexed correction (R6-5) and the AUC fall is uninterpretable (b). Wording fix, not a new experiment (R7-4).

### (d) R1: the floor is one realised difference; DLFE's +0.0029 and the -0.0060 spread both have intervals excluding zero

**Verified; the paper already concedes the first half. Implication: the floor shows that cross-release differences of this size occur; it cannot be used as a noise bound or a test.**

- Floor AUC (relation) -0.0060, 95% [-0.0099, -0.0011] (B = 1,000); excludes zero. DLFE vs its release baseline +0.0029 [+0.0001, +0.0055] (B = 1,000); excludes zero, and the paper itself says the correction is ranking-preserving so the AUC change against its own network is exactly 0 (`dlfe` vs `dlfe_soft`: 0 under all four weightings) and the +0.0029 "is a training difference". Pair weighting: floor -0.0181 [-0.0356, -0.0058] also excludes zero.
- Paper's own wording: supp. Q.6 "one realised difference, not a variance estimate"; Tab. 1 caption "a floor for such comparisons. One released run each; intervals ... cover test sampling only". So the disclosure exists in the table caption and supplement. The abstract (lines 024-027) does not carry it: "far exceeds the +0.001 between two separately trained baselines" and "does not exceed their 0.006 spread" read as a noise bound.
- Consequences: (i) an interval that excludes zero around a difference the authors call training noise shows the intervals measure test sampling for one pair of networks, not training variability; (ii) the sign of the spread flips with the weighting (-0.0060, +0.0017, -0.0181, -0.0256) and with the baseline used (PE-Net vs `dlfe_base` is +0.0110, +0.0038, +0.0368, +0.0202), so "+0.0050 does not exceed 0.006" is one cell of a sign-unstable table (R1 W2; numbers verified in `sgg_cross_release_floor.json`); (iii) the case-level floor (+0.0007) is a single draw; the same file shows the baseline pair's case-level part moves from +0.0018 (gc@20) to -0.0044 (ng@50), which is a second hint of its spread. TDE is unaffected, since TDE and its baseline share weights.
- Implication for the paper: say "exceeds the one observed cross-release difference", give the signs under all four weightings in Tab. 1 or its caption, and do not describe PE-Net's AUC change as "within noise" in either direction. The multi-seed experiment (R7-10) would turn the example into a spread.

### (e) R1/R2: no operating-point control for PE-Net

**Verified for R1 (and the DA); R2 asks for something adjacent, not this. Implication: the PE-Net case-level claim is not separated from an operating-point shift.**

- `results/` holds `sgg_recall_split_penet_vs_none.json` and `sgg_recall_split_penet_vs_dlfe_base.json` only; there is no PE-Net vs control split, and the paper's own control (log-prior logit adjustment, tau = 1) was built for TDE (`la1`) and for IETrans (`sgg_recall_split_ietrans_vs_la1.json`), not for PE-Net or DLFE.
- R1's ratio: case-level over group-level is 0.0243 / 0.1460 = 0.166 for PE-Net against 0.0139 / 0.0802 = 0.173 for the LA control (TDE 0.155). I reproduced the arithmetic from the stored split values. The ratio does not prove PE-Net's case-level part is an operating-point effect; it shows the data cannot exclude it, as R1 says. PE-Net also gives much less mass to no relation than the baseline (0.560 vs 0.855, verified), so operating-point movement is plausible.
- Seat attribution: R1 W1(c) and Q1 and DA M4 and alt. path 7 ask for a PE-Net-vs-control split. R2 M4 and M6 ask for multi-seed baselines or no variance-based claim about PE-Net, and for a trainable non-prior method; R2 does not ask for an operating-point control. The EIC raises the floor (W3, Q3), not the control.
- Practicality: the control needs PE-Net's per-pair scores for every candidate pair (the `dump_penet` output of `colab_penet_stage2.py`), which is not in the repository; `variant_penet.npz` has only the ground-truth pair's probability row and precomputed ranks. So the LA control needs a Colab rerun of the PE-Net dump plus `colab_sgg_rank.py` (R7-7). The wording fix (R7-2) needs no run.
- Implication: "PE-Net's case-level part is not training noise" is true against the floor and silent on the more relevant null. The conclusion line "PE-Net ... has a case-level part well above the spread between separately trained baselines" should add "an operating-point control for PE-Net was not run".

### Other checks

| Check | Status | How |
|---|---|---|
| (f) TDE AUC bounds and margins | **Verified** | `results/sgg_auc_label_weighting.json`, TDE vs none: relation -0.0018 [-0.0043, +0.0016], 90% bound 0.0038, equivalent at 10% and 25%; comparison +0.0025, bound 0.0077, equivalent at 25% only (margin 0.00808; the near-tie R1 notes); pair -0.0153 [-0.0249, -0.0004], bound 0.0229, 25% only; predicate -0.0038 [-0.0339, +0.0211], bound 0.0279, **equivalent at no margin** (25% margin 0.0173). Weight on head-head: comparison 0.649, relation 0.572, pair 0.038, predicate 0.032. So the abstract's "tightly only under the two that favour head predicates" is accurate, and the pair weighting, which puts 4% on head-head, supports only the loosest margin. |
| (g) Control grid (Table 2) | **Verified (round 3, unchanged)** | TDE minus LA total: gc@20 -0.0234, gc@50 +0.0031, gc@100 +0.0300, ng@20/50/100 -0.0792 / -0.1272 / -0.1549 (R1's list). The abstract's "0.02 to 0.15" omits the +0.0031 protocol it highlights, fine as written. |
| (h) Background mass | **Verified** | `background_mass` in `sgg_cross_release_floor.json`: none 0.855, TDE 0.021, LA1 0.651, `dlfe_base` 0.682, PE-Net 0.560. |
| (i) N inconsistency | **Verified** | `sgg_cross_release_floor.json` `n_relations: 183639`; text says 183,642 in Sec. 5 and Q.6 (R1 M1). Three relations dropped in the AUC paths. Minor. |
| (j) PE-Net replay equals the evaluator | **Verified** | `max_abs_difference_replayed_vs_stored: 0.0`; printed and replayed R@50 0.6523, mR@50 0.3142 (R2). The replay validates the NMS-path number; it does not remove the evaluator confound. |
| (k) DLFE baseline zero-shot | **Verified** | `results/dlfe_official_recall.json` printed zR@50 0.0334 (R2 m2); PE-Net zR@50 0.1713 in `penet_official_recall.json`. The 0.1102 baseline value is from supp. Q.7. |
| (l) R1's checkout HEAD `2300e8e` | **Explained by history, not by the dispatcher** | `ea0efe7` is an ancestor; `git diff --name-only ea0efe7 HEAD` lists only review files, so a checkout at `2300e8e` holds the same manuscript, code and results as `ea0efe7`. Which commit R1 actually viewed was not stated by the dispatcher; the seats' findings are not affected by what I can see. |
| (m) DB-SGG reference | **Conflict between rounds** | Round-3 letter (R6-19) said arXiv:2308.05286 is withdrawn per R2 and must not be cited; round-4 R2 recommends it as "Gao et al., Informative Scene Graph Generation via Debiasing" [verified by R2]. Not checked by me. **[UNVERIFIED]**: the authors should check the arXiv record before citing. |

Not verified by me (taken from the cards): the EIC's run of `verify_manuscript_numbers.py` (89 numbers trace), R1's own reimplementation checks (all rows of its recomputation log; matches my spot checks of the stored JSON), R1's jackknife widening (7% to 25%), the argmax-only proxy and the 9.7% multi-hit rate, R1's head-head subgroup (+0.0067 [-0.00004, +0.0146]), R1's zero-shot subset weight (11%), R1's claim that 33.1% of relations have an exact twin (`sgg_cross_image.json`), R2 M2 (self-test on random logits), R2 m1 (SGDet matched-pair choice), R2 m3 (dedup), R3's Waterbirds matched value, R3's and R2's and the EIC's reference leads (R2 verified Knyazev et al. BMVC 2020 arXiv:2005.08230, Gao et al. arXiv:2308.05286, Biswas et al. arXiv:2211.06444 and arXiv:2308.12048 by web search; the EIC verified Tang et al. NeurIPS 2020 and Knyazev et al.; R3 verified Blinder 1973, Ferro and Fricker 2012, Idrissi et al. 2022, Kirichenko et al. 2023), any proof, any checkpoint replay, the CVPR 2027 supplement-size rules, and whether the declaration preceded the data.

---

## Blocking Issues (3, immutable source order)

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| B1 | PE-Net's graph-constrained recall figures (+0.170, 86%, case-level +0.024) come from an evaluator path with relation NMS that the baseline does not get; the no-NMS replay (mR@50 0.2961, R@50 0.6302) is stored and not reported | R2, R1 | `results/penet_official_recall.json` `replayed_without_rel_nms`; `experiments/colab_sgg_rank.py`; supp. Q.6; abstract (check (a)) | R7-1 |
| B2 | The abstract reads one realised cross-release difference as a noise floor ("far exceeds", "does not exceed their 0.006 spread"), and PE-Net's case-level part is not compared with an operating-point control | R1, R2, R3, EIC, DA | `results/sgg_cross_release_floor.json`; abstract lines 023-027; conclusion lines 603-605 (checks (d), (e)) | R7-2, R7-3 |
| B3 | IETrans is described as a "prior correction" in the abstract and conclusion while the body says relabel + reweight + test-time prior against a different baseline; the "four times the floor" sentence is true for one weighting only | R2, R1 | abstract line 022; conclusion line 600; supp. Q.6 line 1900 (checks (b), (c)) | R7-3, R7-4 |

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence (self-reported scope disclosure) | Questions | Minor issues |
|---|---|---|---|---|---|
| Journal-Fit Reviewer (EIC) | CVPR area-chair perspective, SGG and evaluation methodology | Major Revision (Borderline; 3/5; leaning Weak Accept on contribution, Weak Reject on the 8-page presentation) | 4 | 5 | 5 (W5-W9) |
| Reviewer 1 | Methodology: proper scores, U-statistics, equivalence testing | Weak Accept (borderline-accept, conditional on toning down cross-release claims or adding a multi-seed floor); mapped to Minor Revision | 4 arithmetic, 3 interpretive | 4 | 6 (M1-M6) |
| Reviewer 2 | Domain: scene graph generation, unbiased SGG | Major Revision ("accept in principle if M1 and M3 are fixed and M4/M5/M6 are rescoped") | not stated numerically | 0 listed (questions folded into findings) | 10 (m1-m10, of which 4 labelled minor) |
| Reviewer 3 | Perspective: robustness, group shift, forecast verification (outside SGG) | Borderline / Weak Accept (advisory, conditional); mapped to Minor Revision | moderate | 5 | 6 (F5-F10 by its own severity tags: 5 M, 5 m) |
| Devil's Advocate | Fixed adversarial seat | N/A, findings only | per-finding | n/a | 6 minor, 7 major, 0 critical |

Confidence values are disclosures only and were not used to weigh, count or resolve anything. Tensions recorded: R1 recommends Weak Accept but lists six Major weaknesses and says its cross-release readings "are not safe as stated"; R2 recommends Major Revision while describing the statistics as "careful and unusually honest". The synthesizer relied on the findings, not the labels. R3's F-ids carry their own severity tags (F1 to F5 major, F6 to F10 minor); the question and minor counts above are the seats' own and are given as reported.

Key strengths agreed across seats: exact identity and clean implementation (R1 rebuilt every headline number from the shipped arrays; the EIC's script traces 89 manuscript numbers); the offline evaluator replay matches the printed values to four decimals for all four checkpoints (R2 verified `max_abs_difference_replayed_vs_stored` is 0.0); the ranking-preserving control and the within-cell AUC as a falsifiable pair (all five); candour about protocol, post-hoc status, grouping dependence, single runs and the cases that cut against the story (EIC, R1, R3, DA); the controlled-predictor and CLIP demonstrations (R3, DA).

---

## Step 1b: Weakness Sub-Claim Inventory

Severity is transported from the seat's per-finding tag. Positions: R = raised, C = corroborated, N = not mentioned (silence, not opposition), D = disputed. DA is tracked separately and is not counted in the 4. Every sub-claim is split from a weakness a seat wrote; none was introduced by the synthesizer.

| SC | Sub-claim | Parent weaknesses | EIC | R1 | R2 | R3 | DA | Transported severity |
|---|---|---|---|---|---|---|---|---|
| SC-1 | PE-Net's graph-constrained recall is scored with relation NMS the baseline does not get | R2 M1; R1 W1(d) | N | R | R | N | N | Major (R2, R1) |
| SC-2 | The cross-release floor is one realised difference between two networks of different forks, not a variance estimate; PE-Net's case-level and AUC statements lean on it; seeds requested | R1 W1(a), W3; R2 M4; R3 F8; EIC W3, Q3; DA M5 | R | R | R | R | M5 | Major (R1, R2, EIC); Minor (R3) |
| SC-3 | PE-Net's case-level part is read against a training-noise null, not an operating-point control; PE-Net AUC sentence is selective across baselines and weightings | R1 W1(b)(c), W2; DA M4 | N | R | N (adjacent: M4, M6) | N | M4 | Major (R1, DA) |
| SC-4 | IETrans+Rwt is not a "prior correction"; no baseline of its own; "four times the floor" holds for one weighting | R2 M3; R1 W3; EIC W8 | R (minor) | R | R | N | N | Major (R2); within Major (R1); Minor (EIC) |
| SC-5 | TDE "no AUC gain" bounds are post hoc, head-weighted, and the weighting nearest mean recall passes no margin; no power analysis | EIC W2, Q1; R1 W4; DA M3 | R | R | C (M5) | N | M3 | Major (EIC, R1, DA) |
| SC-6 | The LA match is one operating point (K = 50, graph constraint, tau = 1); no tau sweep or tuned prior-only control | R1 W5; R2 M5; DA M2 | N | R | R | N | M2 | Major (R1, R2, DA) |
| SC-7 | The 87% (and 94%, 97%) share is conditional on the class-pair cell and near-mechanical for pair-indexed corrections; the dichotomy is a dial | EIC W4; R1 W9; R3 F3; R2 m5; DA M1 | R | R | R | R | M1 | Major (EIC, R3, DA); Moderate (R1, R2) |
| SC-8 | Scope and title: four checkpoints, one run each, PredCls, 2018-2023 models, no one-stage or VLM model | EIC W3; R2 M6; DA M5 | R | N | R | N | M5 | Major (EIC, R2, DA) |
| SC-9 | Body is not self-contained; abstract density; figures illegible; terminology load | EIC W1, W6; R3 F7; DA m4; R1 M1 | R | R (N inconsistency) | N | R | m4 | Major (EIC); Minor (R3, DA, R1) |
| SC-10 | Multiplicity of positive secondary results; post-hoc subsets (zero-shot AUC, DLFE +0.0029, ng@100) | R1 W6, W11; DA M7 | N | R | N | N | M7 | Major (R1 W6 and W11); Major (DA) |
| SC-11 | Interval construction: n_y in mean-recall intervals, official-statistic share via label shuffle, shares above 100% | R1 W8, M3; R2 m4; DA m4 | N | R | R | N | m4 | Moderate (R1); Minor (R2, DA) |
| SC-12 | Non-SGG breadth: Waterbirds AUC +0.003, calibration-dominated; CIFAR/text use label-derived cells; no DFR comparison | R3 F2, F6; DA m6 | N | N | N | R | m6 | Major (R3 F2); Minor (R3 F6, DA) |
| SC-13 | Novelty positioning (Yates, Oaxaca-Blinder, Brier decomposition, permutation importance) and missing references | R3 F1; EIC W5, missing references; R2 s.4 | R (minor) | N | R | R | N | Major (R3); Minor (EIC) |
| SC-14 | Normative payoff and minimal reporting protocol: "group-level is not lesser", downstream use asserted, who declares phi, heavy report | EIC W7; R3 F4, F5, F9; DA M6 | R (minor) | N | N | R | M6 | Major (R3, DA); Minor (EIC) |
| SC-15 | Zero-shot and SGDet: PE-Net absent from the zero-shot table; SGDet matched-pair choice; unseen subset post hoc | R2 m1, m2; R1 W6 | N | R | R | N | N | Moderate |
| SC-16 | Label ambiguity: merges, AUC ceiling from duplicates only, noisy labels | R1 W10; R3 F10; DA m3 | N | R | N | R | m3 | Moderate (R1); Minor (R3, DA) |
| SC-17 | Implementation and reproducibility details: NMS self-test on random logits, dedup, reproduction needs Colab, anonymity of archive, singular "The author" | R2 M2, m3; R1 M5; EIC desk table | R | R | R | N | N | Minor |
| SC-18 | Cell-size and twin-relation diagnostics; CLIP demonstration rhetoric; simulation precision | DA m1, m2, m5; R1 M2, M4 | N | R | N | N | m | Minor |

## Step 2: Consensus Analysis

### Points of Agreement (Consensus)

**[CONSENSUS-4]** (EIC, R1, R2, R3 all raise it, no conflict)
1. SC-2 (the cross-release floor is a single draw; training seeds wanted): EIC W3/Q3, R1 W1 and W3, R2 M4, R3 F8; DA M5 corroborates. Verified (checks (d), (e)).
2. SC-7 (the share is a function of the declared cell and near-mechanical for pair-indexed corrections): EIC W4, R1 W9, R2 m5, R3 F3; DA M1 and its strongest counter-argument. Verified as stated in the paper (18% / 84% / 87% / 90%).

**[CONSENSUS-3]**
3. SC-5 (TDE AUC bound is post hoc, head-weighted, unpowered where mean recall lives): EIC W2, R1 W4, R2 M5 in part; DA M3. Verified (check (f)).
4. SC-6 (single control at one operating point): R1 W5, R2 M5, DA M2; EIC W3 notes the protocol dependence.
5. SC-8 (scope and title outrun four checkpoints): EIC W3, R2 M6, DA M5.

### Corroborated findings (2 seats, no conflict)
SC-1 (R2, R1 on the PE-Net NMS path; verified in the stored results), SC-4 (R2, R1 on IETrans), SC-9 (EIC, R3 on density), SC-10 (R1, DA on multiplicity), SC-11 (R1, R2 on intervals and the official statistic), SC-13 (EIC, R3 on positioning), SC-14 (EIC, R3, DA on the normative payoff), SC-15 (R1, R2), SC-16 (R1, R3).

### Single-reviewer findings (retained, no consensus label)
SC-3 (R1 W1(c); DA M4 corroborates the control gap; the premise is verified, check (e)), SC-12 (R3), SC-17, SC-18.

### DA CRITICAL adjudication

There are **0 DA CRITICAL issues**. Nothing to validate, reject or leave unresolved, and no `[DA-CRITICAL-VS-ACCEPT]` condition arises. The seven MAJOR items were treated as findings tracked outside the 4-seat count and routed to the roadmap: M1 to R7-5, M2 to R7-6, M3 to R7-9, M4 to R7-2 and R7-7, M5 to R7-10 and R7-11, M6 to R7-16, M7 to R7-8.

## Points of Disagreement and Arbitration

**A1. Does the PE-Net NMS confound change the paper's PE-Net conclusion? (R2: "not secure"; R1: case-level survives the proxy, headline protocol-dependent; paper and R3: PE-Net illustrates the instrument.)**
- R1's proxy says the case-level part is robust (0.0250 vs 0.0243) while the total falls about 9%; my check (a) agrees on size (10.8% of the official gain) from the stored no-NMS recalls and adds that the NMS-free ng protocols give a case-level part (+0.0190 to +0.0346) well above the baseline pair's.
- **Resolution**: R2 is right that the abstract's gc@50 numbers mix evaluator and model; R1 is right that the qualitative case-level result survives. The remedy is to state the NMS path beside the numbers and show the ng-protocol values (R7-1), and to rerun the no-NMS gc split only if the Colab job is cheap. **Rationale**: evidence first; the claim that matters (case-level part above the floor) does not rest on the confounded protocol, so this is a wording and reporting fix, not grounds for Major.

**A2. Category: two seats Major (EIC, R2), two Weak Accept (R1, R3).**
- **Resolution**: Minor Revision with a tripwire. The Major recommendations rest on R2 M1 to M6 and on EIC W1 to W4. M1 (evaluator) is a reporting fix as shown in A1. M3 (IETrans label) is one word. M4 to M6 and EIC W3 are scope and wording, not errors. EIC W1 (a body that cannot stand without the supplement) is a presentation concern already in R6-6. **Rationale**: no seat or check found a numerical or logical defect that invalidates a central claim; every must-fix is bounded. The tripwire is stated in the decision. Dissent is recorded, not counted.

**A3. How to treat the floor: add seeds (R1, R3, EIC, DA) or reword (R2: "train 3+ seeds or state that no variance-based claim is made").**
- **Resolution**: reword is must-fix (R7-3); seeds are should-fix with a go/no-go in the first week (R7-10), since several seats ask for it but it needs GPU days. **Rationale**: the paper already says "one realised difference, not a variance estimate"; the only gap is the abstract's use. A seed spread would be the best fix and is the most expensive item in the roadmap.

**A4. R1's "operating-point control for PE-Net" vs R2's silence on it; user-supplied attribution "R1/R2".**
- R1 W1(c), Q1 and DA M4 ask for it; R2 asks for multi-seed baselines and a non-prior method. **Resolution**: record the request as R1 and DA; R2 supports the underlying concern (cross-architecture spread unknown). Must-fix is wording (R7-2); the control run is should-fix (R7-7) and needs the PE-Net score dump.

**A5. R3 F3 ("the control, not the split, carries the main practical value") vs the EIC's advice to lead with the mean-recall split and AUC.**
- **Resolution**: author's positioning choice. Both agree the abstract must say the share is conditional on the cell, and both want a profile over groupings (Tab. 1 lower panel) rather than a single number. Routed to R7-5 and R7-16. **Rationale**: author autonomy; the evidence supports both readings.

**A6. R3 F2 (Waterbirds gain is mostly calibration) vs round-2 and round-3 adjudication to keep it in the body.**
- **Resolution**: the body now reports the AUC (+0.0031), which answers part of the earlier request; keep it and add the worst-group decomposition or a one-line caveat (R7-13). Not must-fix.

**A7. DB-SGG reference.** Round-3 letter said not to cite arXiv:2308.05286 (withdrawn per R2); round-4 R2 recommends it. Cannot be settled here (no external lookup). Left to the authors to check the arXiv record; marked **[UNVERIFIED]** in R7-14.

**A8. Unresolved dissent.** (i) Whether the TDE-release SGB evaluator has `rel_nms` (R2's premise; code shows the audit does not apply it to the baseline). (ii) Whether a pair-ranking contribution exists in TDE's case-level part (carried from round 3, untested). (iii) R1's jackknife and proxy figures are unverified. (iv) Whether the primary protocol was fixed before the data were seen (not checkable from artifacts). (v) Whether the instrument's value is "primarily an evaluation methodology" or a general diagnostic is a positioning choice for the authors.

---

## Decision Rationale

Relative to round 3 the panel's concerns moved from what the abstract says about the AUC to what the abstract says about the one non-prior method. The TDE and DLFE results, the control and the AUC bounds hold on every check I ran. The PE-Net result does not carry the weight the abstract puts on it: its graph-constrained recall figures come from an NMS path the baseline does not use (about 11% of the mean-recall gain), its AUC change is not distinguishable from a sign-unstable cross-release floor, and its case-level part has not been compared with an operating-point control. The IETrans label in the abstract and conclusion does not match the body. These are the four things a CVPR reader who knows SGG would catch in the first read, and each can be fixed in a sentence or a table row. I chose Minor Revision because the fixes are wording, labelling and one bounded re-analysis, and because the qualitative PE-Net signal is visible in the NMS-free protocols. I did not choose Accept because the abstract currently overstates PE-Net and the floor, and because two seats recommend Major.

---

## Part 2: Revision Roadmap

> IDs `R7-n` are transport references for items new or re-raised in round 4; the round-3 ID is given where one exists. They are not a work rank (the editor's priority view below is). Tiers are editorial gates. Severity is transported from the driving finding. `proposed_targets`: unavailable, because no bound block manifest was supplied; targets are given as sections. Effort is in person-days for one author who has the repository, the cached arrays and (where stated) a Colab GPU; "feasible" means feasible by 16 Nov 2026 (19 days) under the 8-page limit. Effort estimates are the synthesizer's, not the seats'. Author triage is not collected here.

Page-budget note: the body is at 8 pages and dense (EIC: check that no spacing or font tweak was used). Net additions in the must-fix tier are one or two Tab. 1 rows (NMS-free PE-Net protocols; floor signs) and clause-level edits to the abstract, Sec. 5 and Sec. 7. Offsetting cuts: the abstract's numeric chain (R7-5), the Sec. 6 non-SGG paragraph (R7-13), and the Tab. 1 second AUC weighting column (EIC W1). The supplement has room.

### Required Revisions (Must Fix)

| Ref | Revision item (fix) | Type | Sub-claims | Severity (transported) | Source seats | Effort | Feasible by 16 Nov, 8 pp | Round-3 link |
|---|---|---|---|---|---|---|---|---|
| R7-1 | PE-Net evaluator confound. State in Sec. 5 and the abstract that PE-Net is scored with its relation NMS and the baseline is not; report `replayed_without_rel_nms` (mR@50 0.2961, R@50 0.6302, official gain 0.1502 vs 0.1683) next to the official numbers; report the PE-Net split in the NMS-free ng protocols (ng@50 case-level +0.0216 [+0.0148, +0.0285]) beside gc@50 and restate the "far exceeds" claim on those; if the Colab job is affordable, rerun `colab_sgg_rank.py` for PE-Net saving the no-NMS `gc_rank` and report the no-NMS split, or apply the same suppression to the baseline; add one sentence that the AUC and proper-score parts use the raw softmax and are unaffected. State R2's premise (the baseline's evaluator has no `rel_nms`) as checked or drop it. | re-framing + re-analysis | SC-1 | Major | R2 M1; R1 W1(d) | 0.5 (wording and ng table row, cached results) to 2 (rerun with saved no-NMS ranks, Colab GPU) | Yes; wording path needs no GPU | R6-14 |
| R7-2 | PE-Net's case-level part: right null. Replace "far exceeds the +0.001 ... between two separately trained baselines" and "not training noise" by a statement that PE-Net's case-level part exceeds the one observed cross-release value and that an operating-point control for PE-Net was not run; state that PE-Net's case-over-group ratio (0.166) equals the control's (0.173) on TDE, so an operating-point account is not excluded; move "a prototype-based method ... changes features instead" (conclusion) to "may change features". Replace "AUC +0.005 does not exceed their 0.006" by the AUC changes under all four weightings against both baselines (or drop the sentence and keep "we claim no AUC gain"). | re-framing | SC-3, SC-2 | Major | R1 W1(b)(c), W2; DA M4; R2 M4 | 0.5 | Yes; no page cost (abstract shortens) | R6-1 |
| R7-3 | Floor and the "four times" sentence. Call the quantity "one observed cross-release difference" in the abstract, Tab. 1 caption and Sec. 7; give its four AUC signs (-0.0060, +0.0017, -0.0181, -0.0256) and mean-recall case-level range across protocols (+0.0018 to -0.0044) so a reader sees it is sign-unstable; say that intervals cover test sampling for that pair, so a floor interval and DLFE's +0.0029 [+0.0001, +0.0055] excluding zero is expected; in supp. Q.6 restrict "four times" to the relation weighting and state 1.5 (pair), 1.4 (predicate), opposite sign (comparison); add `dlfe_base` vs `dlfe_soft` (case-level +0.0011, mR@50 equal to four decimals per R1 **[UNVERIFIED]**) as a second datum. | re-framing + re-analysis (table rows from cached JSON) | SC-2, SC-4 | Major | R1 W3; R2 M4; R3 F8; EIC W3 | 0.5 | Yes | R6-1 |
| R7-4 | Method labels. Replace "also prior corrections" (abstract) and "three released prior-correcting PredCls checkpoints" (conclusion) by wording that matches the body: DLFE is a per-predicate correction against its own baseline; IETrans+Rwt is a released relabel + reweight + test-time-prior system against a separately trained, differently fused baseline; TDE and DLFE (against `dlfe_soft`) are the controlled comparisons. Add "separately trained baseline" beside IETrans and PE-Net in the abstract. | re-framing | SC-4 | Major (R2); Minor (EIC) | R2 M3; EIC W8 | 0.25 | Yes | R6-5 |
| R7-5 | Abstract as the conditioned claim. Put the grouping condition and the protocol condition in the 87% and +0.094 sentences (class-pair cell, K = 50, graph constraint); cut to three findings and one condition clause (target: under 15 numerals), moving the DLFE, IETrans and PE-Net numbers to Tab. 1; one basis for "points"; define cell, group-level and case-level in plain words in the abstract; unify N (183,642 vs 183,639: say three relations drop out of the AUC paths); present the share as a profile over declared groupings (18%, 84%, 87%, 90%) in the main text and say what one would stop at. | re-framing | SC-7, SC-9 | Major (EIC, R3, DA); Minor (R1) | EIC W1, W4; R3 F3, F7; DA M1, m4; R1 M1, W9; R2 m4, m5 | 1 | Yes; this is the vehicle that pays for R7-1 to R7-4 | R6-5, R6-6, R6-11 |

### Suggested Revisions (Should Fix)

| Ref | Revision item (fix) | Type | Sub-claims | Severity | Source seats | Obligation | Effort | Feasible by 16 Nov, 8 pp | Round-3 link |
|---|---|---|---|---|---|---|---|---|---|
| R7-6 | Control grid. Report LA at tau in {0.5, 1, 1.5} with the split at all six protocols (tau = 0.5 exists in `results/sgg_recall_split_la0.5_vs_none.json`), and a tuned prior-only control (tau per K, or a per-class bias maximising mean recall, or matched on R@50 or no-relation mass) as the fair competitor; or state that LA matches TDE's kind of gain, not its operating point, outside K = 50 with the graph constraint. | re-analysis | SC-6 | Major | R1 W5; R2 M5; DA M2, alt. path 1, 2, 5 | should_fix | 2 to 3 (TDE logits cached; evaluator replay) | Yes | R6-9 |
| R7-7 | PE-Net operating-point control. LA (and a cell-wise prior) applied to PE-Net's own scores and the split of PE-Net vs control, as for TDE; report PE-Net R/P against the control. Needs the PE-Net per-pair dump (`dump_penet`), which is not in the repository. | new experiment | SC-3 | Major (R1, DA) | R1 W1(c), Q1; DA M4, alt. path 7 | should_fix | 1 to 2 plus a Colab session | Likely; decide in the first week | new |
| R7-8 | Multiplicity. Define a confirmatory set (K = 50 gc mean-recall split; relation AUC) and a family for the rest; report Holm or adjusted limits for the secondary results that are quoted (IETrans fall, unseen-triplet AUC, DLFE +0.0029, TDE ng@100 case-level +0.0148); label unseen-triplet AUC as post hoc and report both weightings together. | re-analysis + re-framing | SC-10 | Major (R1, DA) | R1 W6, W11; DA M7 | should_fix | 0.5 to 1 | Yes | R6-7 |
| R7-9 | Power and the yardstick of the AUC bound. Planted-signal simulation at VG150 cell sizes: detection probability of a true ranking gain of 0.01 or 0.02 under each weighting; state the bound in absolute AUC points beside the baseline AUC (0.61 / 0.57); report the head-head subgroup interval in the main text; consider tying the margin to the observed cross-release spread (EIC W2). | new experiment (simulation) + re-framing | SC-5 | Major | EIC W2, Q1; R1 W4; DA M3 | should_fix | 2 | Yes | R6-8 |
| R7-10 | Training-seed spread. Two or three seeds of the MOTIFS baseline and TDE (or LA), to turn "one observed difference" into a spread for the case-level part and each AUC weighting. Five seats ask. Go/no-go within the first week; if not started by day 7, rely on R7-3 and drop the seed claim. | new experiment (GPU) | SC-2, SC-8 | Major | EIC Q3; R1 W3, Q2; R2 M4; R3 F8; DA M5 | should_fix | 3 to 6 (GPU days) | Uncertain; only if a Colab GPU is available now | R5-13 |
| R7-11 | Scope and title. Rescope the title or the first line ("for four released PredCls checkpoints", define "ten points" as TDE's mR@50 with the graph constraint); add "no one-stage or VLM model audited" to the Limitations list. Adding a rebalancing or resampling method (R2, EIC) is optional (see R7-19). | re-framing | SC-8 | Major (EIC, R2, DA) | EIC W3; R2 M6, m8; DA M5 | should_fix | 0.25 | Yes | R6-5 |
| R7-12 | Zero-shot and SGDet. Add PE-Net (zR@50 0.1713) and DLFE rows to the zero-shot table and AUC; state which training split defines "unseen" for IETrans; report the raw zero-shot gain with its 50% case-level share and soften "not a better ranking" under the comparison weighting (interval covers zero). | re-analysis | SC-15 | Moderate | R1 W6; R2 m1, m2 | should_fix | 1 | Yes | R6-15 |
| R7-13 | Non-SGG breadth. State in the main text that the Waterbirds AUC gain is +0.0031, one probe pair and one seed, calibration-dominated per the supplement; add a worst-group decomposition or a per-background prior control; label CIFAR-100-LT and 20 Newsgroups as estimator behaviour under label-derived cells. Cut Sec. 6 text to pay. | re-framing + small analysis | SC-12 | Major (R3 F2); Minor | R3 F2, F6; DA m6 | should_fix | 1 to 2 | Yes | R6-12 |
| R7-14 | Positioning. One sentence in contribution (i) of what is new relative to Yates, grouping loss and permutation importance; a short related-work paragraph on Oaxaca-Blinder (Blinder 1973 verified by R3) and the bias-corrected Brier decomposition (Ferro and Fricker 2012, R3-verified abstract only); add Knyazev et al. BMVC 2020 (verified by EIC and R2) and Tang et al. NeurIPS 2020 (verified by EIC). Do not cite arXiv:2308.05286 until the authors check its status (conflict between rounds, A7; **[UNVERIFIED]**). | re-framing | SC-13 | Major (R3); Minor (EIC) | R3 F1; EIC W5, missing references; R2 s.4 | should_fix | 0.5 to 1 | Yes | R6-13 |
| R7-15 | Intervals. Use the refit delete-a-group jackknife as the primary interval where wider (R1: 7% to 25% wider, **[UNVERIFIED]**); report the official-statistic split for all four methods in one table; truncate or flag share intervals above 1 (IETrans [0.90, 1.04]); one sentence on tail-tier coverage. | re-framing + re-analysis | SC-11 | Moderate | R1 W8, M3; R2 m4; DA m4 | should_fix | 0.5 to 1 | Yes | R6-18 |
| R7-16 | Reading rule and minimal protocol. A numbered three-step reporting checklist with defaults (cell, weighting), a decision table including "undetermined" as an outcome and how often it occurs among the audited methods; a note that group-level can be the intended target of the metric; R@50 beside the control in Tab. 1; a broader-implications sentence on shortcut crediting and gaming; soften the downstream claim or cite evidence. | re-framing | SC-14 | Major (R3, DA); Minor (EIC) | R3 F4, F5, F9; EIC W7; DA M6 | should_fix | 1 | Yes | R6-16 |
| R7-17 | Self-contained body. Make Fig. 3 and Fig. 2(b) legible at print size; split the Tab. 1 caption (definitions to the text); one worked four-point example of the split in the body if a half page can be found; use one name set (group-level / case-level vs transport / covariance) and cite the terminology table once. | editorial | SC-9 | Major (EIC) | EIC W1, W6; R3 F7 | should_fix | 1 | Tight at 8 pp; pay with R7-5 and R7-13 cuts | R6-6 |

### Consider

| Ref | Revision item (fix) | Type | Sub-claims | Severity | Source seats | Effort | Feasible |
|---|---|---|---|---|---|---|---|
| R7-18 | Pair-ranking and hit-pair audits (carried): mean-recall split with pair ranks frozen at the baseline's (TDE, LA1); SGDet: how often the hit pair differs from the largest-IoU pair and the case-level part restricted to images where they coincide (R2 m1). | new analysis | SC-15 | Major (carried R1 round 3); Moderate (R2) | R2 m1; round 3 R1 W4 | 2 to 3 | Check in week one; evaluator replay needs a rank-freezing option |
| R7-19 | Label ambiguity and extra method: an AUC that treats other recorded labels of the same input as non-negatives (33.1% of relations have an exact twin per `sgg_cross_image.json`, **[UNVERIFIED]**) and a ceiling in the main text; optional added method (CFA, GCL, SHA-GCL, relabelling or resampling) if a checkpoint with cacheable logits exists, else say why not; an extra Waterbirds ERM / GRW / DFR comparison (R3 F6). | new analysis | SC-8, SC-12, SC-16 | Moderate | R1 W10; R3 F6, F10; DA m3; EIC W3 | 2 to 4 | Partly |
| R7-20 | Small items: NMS self-test on real PE-Net outputs (R2 M2: the 300-image test uses random logits; the end-to-end match to the printed values is the real validation); one sentence on the IETrans dedup (152,226 vs 183,642 rows) and that no other model's official numbers change (R2 m3); a baseline column in Tab. 1 (R2 m9); cell-size and within-cell entropy distribution (DA m1); main text mentions twin relations (DA m2); CLIP rhetoric softened (DA m5); simulation precision of the null size and coverage (R1 M2); a test that counterfactual hit_i(y_j) from stored ranks matches the evaluator for pairs with two recorded predicates (R1 M4); five seeds vary the head only (R1 round 3); archive metadata check for names and paths; "The author" vs the author list in the LLM statement (EIC); dated pre-declaration file (R1 M5); verify that CVPR 2027 supplement rules allow 40 pages (EIC could not check). | editorial and small analyses | SC-9, SC-17, SC-18 | Minor | EIC, R1, R2, DA | 1 to 2 in total | Yes |

### Source-Traceability Checklist (not a work order)

- [ ] R7-1 must_fix: PE-Net evaluator (rel_nms) confound; no-NMS numbers; ng-protocol values
- [ ] R7-2 must_fix: PE-Net case-level null; AUC sentence
- [ ] R7-3 must_fix: floor wording; "four times"; signs under all weightings
- [ ] R7-4 must_fix: "prior correction" label for IETrans
- [ ] R7-5 must_fix: abstract conditions; density; N; grouping profile
- [ ] R7-6 to R7-17 should_fix; R7-18 to R7-20 consider (as in the tables)

### Editor's priority view (advisory)

Ordered by decision weight and by how much each unblocks; the author may order differently.
1. R7-1 and R7-2 together (the gating items; the first is mostly reporting from stored results, plus an optional Colab rerun; start the rerun decision on day 1).
2. R7-3 and R7-4 (small edits that finish the cross-release story; R7-3 uses cached JSON).
3. R7-5 (the abstract rewrite; do it after R7-1 to R7-4 since it absorbs them and pays for them in space).
4. R7-8, R7-9, R7-6 (multiplicity, power and the control grid; the most-cited analysis gaps for the TDE claims).
5. R7-7 and R7-10 (the two experiments that need a Colab GPU; run only if started in the first week).
6. R7-11 to R7-17 as time allows.

Suggested schedule against 16 Nov (19 days): days 1 to 2 decide on the PE-Net rerun (R7-1 saved no-NMS ranks, R7-7 control dump in the same Colab session) and the seed run (R7-10); days 2 to 6 R7-1 to R7-4 wording and table rows; days 6 to 9 R7-5 abstract; days 9 to 13 R7-6, R7-8, R7-9, R7-12; days 13 to 16 R7-11, R7-13 to R7-17; keep the last three days for compile, page-limit checks and a re-review. Nothing in the must-fix tier needs a retrained model; R7-1's rerun and R7-7 need a Colab session; R7-10 needs GPU days and should be dropped if it cannot start in week one.

### Response Letter Template
Use `templates/revision_response_template.md` to respond to every item R7-1 to R7-20, including a stated decision for each should_fix and consider item. Where the author declines an item, say so; a decline stays visible and unresolved. Round-3 items marked "Partly" or "Re-raised" in the status table should be answered under their R7 item.

---

## Part 3: Reviewer Report Summary (Appendix)

- **Journal-Fit Reviewer (EIC)**: Major Revision (Borderline; 3/5; leaning Weak Accept on contribution) | Confidence 4. Right question and exact accounting; concerns are a body that cannot stand without the 40-page supplement, a TDE "no gain" claim stronger than the head-weighted bounds support, narrow scope against the title, and a share that depends on the declared cell. Desk-rejection risk low (limit, LLM statement and anonymity checked; archive metadata and 2027 supplement rules not checked). Strongest: SC-9, SC-5, SC-8, SC-7.
- **Reviewer 1 (Methodology)**: Weak Accept (borderline-accept; conditional) | Confidence 4 arithmetic, 3 interpretive. Rebuilt all headline numbers from the shipped arrays and found no numerical error; the PE-Net case-level claim tests the wrong null, the AUC sentence is selective, the evaluator differs for PE-Net, the bounds are post hoc, and positive secondary results are uncorrected. Strongest: SC-2, SC-3, SC-1, SC-5, SC-6, SC-10.
- **Reviewer 2 (Domain)**: Major Revision (accept in principle if M1 and M3 are fixed) | confidence not stated. Clean evaluator replay; PE-Net `rel_nms` confound (verified in the stored numbers), IETrans mislabel, floor is not a noise floor, K = 50 coincidence, narrow scope. Strongest: SC-1, SC-4, SC-2, SC-6, SC-8.
- **Reviewer 3 (Perspective)**: Borderline / Weak Accept (advisory, conditional) | Confidence moderate (outside SGG; proofs not read). The negative-control idea is the contribution; the generality claim outruns the non-SGG evidence, the dichotomy is a dial over the declared cell, the reporting recommendation is heavy, positioning against Oaxaca-Blinder and Brier decompositions is thin. Strongest: SC-12, SC-7, SC-13, SC-14.
- **Devil's Advocate**: findings only. Key challenge: the 87% is a statement about the declared grouping, the AUC null is uninformative where mean recall lives, the PE-Net contrast uses the wrong null, and the normative payoff is asserted; 0 Critical, 7 Major, 6 Minor.

## Closing

We invite a revised manuscript that addresses the five required items and states a decision on each suggested item. The audit is careful and candid, and the instrument holds on every number we rechecked. The revision is mostly a matter of making the abstract and Sec. 5 say what the evidence supports about the one method that is not a prior correction: which of PE-Net's recall figures depend on its evaluator path (R7-1), what a single cross-release difference can and cannot bound (R7-2, R7-3), and what the released IETrans checkpoint is (R7-4). A further review will be needed after the revision.

*Synthesis scope note: this letter synthesizes and arbitrates the five Phase 1 reports; it adds no new review comments beyond the verification of claims the seats made. Checks (a) to (e) are reads of stored results and code plus arithmetic on stored values, no checkpoint was rerun, and implications are the synthesizer's reading and are labelled as such. Effort and feasibility figures are the synthesizer's estimates.*

## Status after the round-4 must-fix revision (2026-10-28)

| Ref | Status | What changed |
|---|---|---|
| R7-1 | Done (text); NMS-free graph-constrained split not recomputed | Sec. 5 says PE-Net is evaluated with the relation-level NMS its authors prescribe, which the baselines do not use, and gives the NMS-free mR@50 (0.2961 against 0.3142); supplement `app:penet` gives the NMS-free R@50 and mR@50 and says the split uses the suppressed ranks. Without the graph constraint, where NMS plays no part, PE-Net's case-level part is +0.0216 at K=50 against -0.0044 between the two baselines. Abstract mentions the 0.314 to 0.296 drop. |
| R7-2 | Done | PE-Net's case-level part is stated together with the absence of an operating-point control and the fact that its case-level share (14%) equals the logit-adjusted control's on TDE (15%); no AUC gain is claimed. |
| R7-3 | Done | The two-baseline comparison is called "one observed cross-release difference, not a noise bound" in Table 1 and the supplement; all four AUC signs are given; "four times" is restricted to the relation weighting (1.5x per pair, 1.4x per predicate, overlapping intervals). |
| R7-4 | Done | IETrans is no longer called a prior correction in the abstract, intro or conclusion (relabelling and reweighting). |
| R7-5 | Partly | Abstract rewritten: four checkpoints, 87% conditioned on class-pair cells and K=50 with the graph constraint, 84% and 18% alongside, caveats for PE-Net; N = 183,639 for AUC and proper scores stated in Sec. 5 next to 183,642. A grouping profile across a hierarchy of cells is not added. |

## Status after the round-4 should-fix pass (2026-10-28)

| Ref | Status | What changed |
|---|---|---|
| R7-6 | Partly | Control at tau = 0.5 and 1 reported (+0.0419 and +0.0941 of TDE's +0.0972); a tau tuned per cut-off or a control matched on R@50 needs an evaluator replay and was not run, so the text says the control matches TDE's kind of gain, not its operating point, outside K = 50 with the graph constraint. |
| R7-7 | Not done | PE-Net's per-pair dump is not in the repository, so no operating-point control for PE-Net; stated in Sec. 5. |
| R7-8 | Done | Confirmatory set declared; six secondary AUC results with Holm-adjusted p (under 0.001 for IETrans and the unseen-triplet fall, 0.028 to 0.043 for the other four, not read as findings). `experiments/sgg_secondary_adjust.py`. |
| R7-9 | Done (analytic) | Detectable changes at 80% power from the bootstrap standard errors (0.0042, 0.0082, 0.018, 0.039) beside baseline AUCs; head-head subgroup interval in the supplement. A planted-signal simulation was not run. |
| R7-10 | Not done | No training seeds (GPU days); stated in the limitations and the abstract. |
| R7-11 | Partly | Limitations name the absence of one-stage and vision-language models; title unchanged. |
| R7-12 | Done | `experiments/sgg_zeroshot_more.py`: PE-Net's zero-shot recall rises (+0.0611 per image) with AUC on unseen-triplet comparisons -0.0027 [-0.0116, +0.0097]; DLFE and IETrans fall; TDE's raw zero-shot gain is 55% case-level (37% against the control); the comparison-weighted unseen-triplet AUC covers zero and the text says so. |
| R7-13 | Partly | Main text states the Waterbirds AUC gain (+0.0031), the dependence on recalibration (-0.0456) and one probe pair and seed; CIFAR-100-LT and text described as estimator checks. No worst-group decomposition or per-background prior control. |
| R7-14 | Done | Oaxaca-Blinder and bias-corrected Brier decompositions in related work (Blinder 1973; Ferro and Fricker 2012, no page range given); Knyazev et al. (BMVC 2020) and Tang et al. (NeurIPS 2020) added; arXiv:2308.05286 not cited. |
| R7-15 | Partly | `experiments/sgg_official_split_all.py`: official per-image split for all eight comparisons in one supplementary table (group shares 0.82 to 0.95 outside TDE and LA, 0.84 for both); intervals above 1 clipped. The jackknife is not made the primary interval. |
| R7-16 | Partly | Three-step reporting list with "undetermined" as an admissible outcome in the conclusion; no decision table. |
| R7-17 | Not done | Figure sizes unchanged; body still not self-contained beyond what the page limit allows. |
