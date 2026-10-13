# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 Submission #***** (anonymous)
- **Review Date**: 2026-10-13
- **Review Round**: Round 1 (simulated CVPR 2027 panel)

## Reviewer Information
### Reviewer Role
Peer Reviewer 2 (Domain)

### Reviewer Identity
Scene graph generation specialist. Familiar with the unbiased-SGG literature (TDE, IETrans, DLFE, PCPL, BGNN, PENET), the Scene-Graph-Benchmark.pytorch evaluator (PredCls/SGCls/SGDet; R@K, mR@K, zR@K, F@K), and open-vocabulary SGG.

### Review Focus
Whether the SGG claims are accurate and adequately supported for the benchmark practice they address, whether the literature is covered, and how large and how general the contribution is. Statistical-methodology detail is left to Reviewer 1.

## Overall Assessment
### Recommendation
**Major Revision** (borderline accept if the scope is narrowed or the audit is extended).

### Confidence Score
4. Core SGG expertise. Proofs and U-statistic theory are outside my remit and I did not check them. I did not run the checkpoints.

### Calibration Status
`NOT_CALIBRATED`

`criteria_binding_unavailable` (no target-criteria binding was supplied; no venue-alignment claim is made).

### Summary Assessment
The paper proposes an exact additive split of the score difference between two frozen models. Labels are transported within a declared group (here the ground-truth subject-object class pair). The gain divides into a group-level part and a within-group covariance. It is applied to mean recall of released Neural-Motifs checkpoints on VG150. For TDE (PredCls), 87% of the +10 mR@50 points is group-level. A training-free logit adjustment (LA) that changes no within-pair ranking recovers most of it. TDE's within-pair AUC is statistically equivalent to the baseline's under one weighting. IETrans+Rwt is 97% group-level.

The recomputation is clean (log below). The paper is candid about its limits (grouping dependence, calibration dependence, micro versus official mR). The SGG finding is valuable as a caution. It is not new in kind: that TDE is close to a prior correction in PredCls, and that logit adjustment rivals debiasing, is already known (the paper cites [6, 42, 28]), and the TDE authors describe TDE as removing a context-induced bias. The new part is the accounting.

My concerns are about scope. The empirical SGG evidence rests on one backbone (MOTIFS-SUM), one dataset, one checkpoint pair per method, and two methods. Yet the title and abstract frame it as a statement about what mean-recall gains buy. The framing treats group-level gain as less informative than case-level gain, which conflicts with what debiasing aims at. The SGCls/SGDet extension drops 35-42% of relations. The IETrans comparison is confounded. The CLIP study is a toy and not an SGG system. Several arguably decisive choices (equivalence margin, "primary" weighting and protocol) cannot be verified as pre-declared from the manuscript.

## Strengths
### S1: Exact replay of the official evaluator
The replay reproduces published numbers to four decimals (baseline R@50 0.6612, mR@50 0.1459; TDE 0.4588, 0.2476; no-graph-constraint mR 0.3260 and 0.2981), and the SGCls/SGDet inline replay reproduces the README recalls. This turns mean recall into a function of a counterfactual label with duplicate-object matching. It is a real engineering contribution for anyone auditing SGG metrics.
**Evidence Anchor**: table: Supp. Table 17 and Table 34 — re-scored equals official for R@50, mR@50, ng-mR@50; results/sgg_sgcls_audit.json and results/sgg_sgdet_audit.json "released" versus "recall"

### S2: A useful operating-point control for a thresholded metric
The mean-recall case-level part is not credited as new discrimination, because the training-prior logit shift leaves within-cell ranking unchanged. LA reproduces +0.0941 of +0.0972 and a case part of +0.0139 against TDE's +0.0130, at 0.0175 R@50 cost versus 0.2023. The paper reports F@50 0.344 (LA) versus 0.322 (TDE), which I confirmed. This is the right control and a sharper statement than "logit adjustment rivals debiasing".
**Evidence Anchor**: text: §5 "a one-line prior shift that ranks the relations of every cell exactly as the baseline did reproduces the gain"

### S3: Candid reporting of fragility
The paper reports protocol-dependent sign (temperature-only −0.00006; shared temperature −0.0184; per-class bias +0.00445), the comparison-weighted AUC non-detection, the no-graph-constraint reversal (TDE mR falls), and the grouping dependence (share 18% when the object class is dropped, 90% when position or size is added).
**Evidence Anchor**: text: §7 "dropping the object class takes it to 18%"; Table 2 ng-mR rows

### S4: Beyond-aggregate demonstration
The CLIP-crop model, last on every aggregate yet with a larger case-level part, makes the conceptual point concretely.
**Evidence Anchor**: table: results/vg_metric_bridge.json — MLP-VISUAL-S vs MLP-SPATIAL-S dT −0.0464, dR +0.0064, d_acc −0.0311

## Weaknesses

### W1: Empirical SGG scope is much narrower than the framing, and the one audit that exists in code is not reported
**Problem**: The conclusions rest on MOTIFS-SUM only, VG150 only, one released checkpoint per method ("we ran it once"), and two methods (TDE, IETrans+Rwt). The abstract and conclusion generalize ("the field's metrics report the sum"; benchmark-reporting recommendations). TDE is a 2020 PredCls method whose mechanism (subtracting an averaged-context counterfactual) is structurally close to a prior shift. Later methods that act differently were not audited: HiLo/PENET-style feature-level and prototype methods, FGPL, SQUAT, Transformer or one-stage SGG, and the VCTree/Transformer backbones of the same TDE release. The repository contains `experiments/run_sgg_dlfe_audit.py` and Colab DLFE scripts, but there is no DLFE result in the paper or results/. DLFE is the closest prior-correction method and the one most likely to confirm or refute the generalization. The paper says only "we audit no later method".
**Evidence Anchor**: text: §7 "On two released Neural-Motifs checkpoints on Visual Genome the gains are almost entirely group-level"; absence: results/ — expected a DLFE (or any third-method) split; checked results/*.json, paper §5, Supp. Q.5-Q.7
**Why it matters**: A reader cannot tell whether "mean-recall gain is mostly group-level" is a property of metric plus dataset or of TDE and IETrans. The recommendation to benchmark designers depends on it.
**Suggestion**: Report the DLFE audit (or state why it was dropped). Add at least one method that changes the representation or architecture and releases logits (or can be rerun). Otherwise retitle and scope the abstract to "two prior-correcting methods", and move the benchmark recommendation to a hypothesis. Report training-seed variance of baseline and TDE (a single checkpoint pair gives image-clustered test sampling error only).
**Severity**: Major
**Confidence**: 4 — core expertise: unbiased SGG literature and evaluator

### W2: The normative reading of "group-level" versus "case-level" is in tension with SGG's debiasing goal and with predicate-label semantics
**Problem**: In VG150, many within-pair choices (on vs parked on vs standing on; riding vs sitting on; has vs wearing) are annotator and vocabulary choices over near-synonyms, and the benchmark's stated goal is to make the model say the more informative predicate for the pair. A group-level shift to "parked on" for (car, street) is exactly the intended effect of debiasing, and the paper itself says "group-level is not a lesser gain". Yet the title, the "what did ten points buy" framing, and the CLIP section treat case-level covariance as the real achievement. The cell is the pair, so any recorded or unrecorded signal inside a pair counts as case-level, including annotator-style and image-source shortcuts. This is noted, but the paper then names the CLIP model's covariance "real" while its ranking is worse. The paper does not engage with the long-standing argument that VG's predicate labels are biased or noisy (the motivation for [22, 50]) and that mR rewarding informative predicates is by design.
**Evidence Anchor**: text: §5 "Group-level is not a lesser gain (mean recall rewards moving rare predicates within a pair by design)"; text: §1 "without becoming any better at deciding which relations are a man carrying rather than riding"
**Why it matters**: The headline can be read as "TDE bought nothing", when the data say "TDE bought predicate informativeness at a cost in R, not discrimination". The rhetoric invites over-reading by SGG readers.
**Suggestion**: Reframe: the split tells which part of a gain is available to a prior-correcting post-hoc shift, and which requires pair-conditional evidence. Add a qualitative or human study of a sample of within-pair label flips (is "parked on" more correct?). Discuss synonym and hierarchy structure (the predicate-merge analysis in the supplement, `predicate_merge.json`, should be surfaced in the main text).
**Severity**: Major
**Confidence**: 4 — core expertise: VG150 label semantics, unbiased SGG motivation

### W3: SGCls/SGDet extension conditions on a non-observed grouping and on a selected subset
**Problem**: The cell is the ground-truth class pair, but in SGCls/SGDet the models observe predicted classes and boxes. The condition "grouping both models observe" (§3) is therefore not met; the paper argues it is common to both models. The audit also keeps only "relations with a matched pair" (58% in SGCls, 65% in SGDet). Relations on which the detector failed are excluded, so the split describes the easy subset, and the effect of TDE on the recall deficit (the main SGDet loss) is outside the decomposition. The ΔAUC SGCls claim in the abstract ("TDE's ranking within pairs gets worse") is significant only under one weighting (−0.0128 vs −0.0047, CI crossing zero), and in SGDet both are null.
**Evidence Anchor**: text: §5 "58% of relations have a matched pair"; table: Supp. Table 35 SGCls ∆AUC −.0128 [−.0171, −.0074] versus comparison-weighted −.0047 [−.0122, +.0031]
**Why it matters**: SGDet is the practically relevant setting; the abstract's "99% group-level" in SGCls reads as covering all relations.
**Suggestion**: State the matched fraction in the abstract; report the split on all relations using predicted-pair grouping as a sensitivity; temper the SGCls AUC sentence to the weighting that supports it.
**Severity**: Major
**Confidence**: 3 — SGCls/SGDet evaluator expertise; I did not rerun inline replay

### W4: The IETrans comparison cannot support claims about IETrans's mechanism
**Problem**: The released checkpoint is IETrans+Rwt (internal and external transfer plus a reweighted loss), not relabelling alone. No IETrans baseline was released, so the comparison is against a separately trained baseline, and the authors' test set differs (0.3587 vs 0.3576 mR@50; duplicates). The paper admits this, but the abstract says IETrans "gains 21 points, 97% group-level; its within-pair discrimination falls", and the Conclusion states "IETrans's lowers it on most measures". Under the shared-baseline caveat, a separately trained baseline plus loss reweighting plausibly differ in calibration and training noise. The case part for mR is not different from zero ([−0.0031, +0.0151]). The ∆AUC (weighted as the split weights cells) is the only significant measure.
**Evidence Anchor**: text: Abstract "gains 21 points, 97% group-level; its within-pair discrimination falls on the matched scores and the relation-weighted AUC"; table: Table 1 IETrans case [−.0031,+.0151], ∆AUCc [−.0181,+.0004]
**Suggestion**: Either train IETrans (with and without Rwt) and the baseline under the same recipe in SGB, or remove IETrans-specific mechanism conclusions and call it a second checkpoint with a confounded reference. Check the 97% share is not driven by the Rwt loss (which acts on class priors by construction).
**Severity**: Major
**Confidence**: 4 — core expertise: IETrans pipeline

### W5: Headline "87%" is a micro-pooled, graph-constrained quantity; the dependence on the protocol is larger than the abstract suggests
**Problem**: The official mR is per-image-averaged (+0.1017), while the split is of a pooled version (+0.0972). The 87% share holds only for the graph-constrained protocol; in my recomputation from results/sgg_recall_split.json the share is 77% at K=20, 87% at K=50, 86% at K=100, and for no-graph-constraint the share is meaningless (total −0.0337 with group −0.0464 and case +0.0127; share 138%). Against the LA control, case-level is significantly positive at ng-mR@100 (+0.0148 [+0.0064, +0.0232]). The abstract's "nine of the ten points" and "87%" read as protocol-free; SGB papers frequently quote both protocols, and mR@100 and F@K. Also the "equivalent within a margin" statement is for AUC, not for mR.
**Evidence Anchor**: table: Table 2 ng-mR@50 ∆mR −.0337, group −.0464, case +.0127; ng-mR@100 TDE vs LA +.0148 [+.0064,+.0232]
**Suggestion**: Qualify the abstract with "graph-constrained, micro-pooled"; report shares only where total gain is positive; add the per-image official-statistic split (even approximate, e.g. by per-image-weighted transport) so the headline is about the metric the field reports.
**Severity**: Minor
**Confidence**: 4 — recomputed from results/

### W6: Equivalence margin and "primary" choices are not verifiable as pre-declared, and the margin is borrowed from a non-SGG probe
**Problem**: The paper stresses "fixed in advance" (margin = 0.1 × the AUC gain of box geometry over class pair in an MLP on a reconstructed 70/30 split; weighting; calibration protocol). Nothing in the manuscript lets a reviewer verify the order of events (UNVERIFIED), and the resulting margin (±0.0063 / ±0.0032) is tied to a toy predictor rather than to an SGG-meaningful difference. Under the comparison weighting TDE is not equivalent (a non-detection with MDC 0.008); the abstract names the equivalence under the primary weighting only.
**Evidence Anchor**: text: §5 "A null needs a margin, so we fixed one in advance: a tenth of what box geometry buys over the class pair"; table: results/sgg_equivalence.json TDE vs none comparison "equivalent": false
**Suggestion**: Provide a timestamped declaration, or call the margin a sensitivity analysis. Report the equivalence result across a range of margins. Anchor the margin in a field quantity such as the within-pair AUC difference between published baselines.
**Severity**: Minor
**Confidence**: 3 — methodology adjacent

### W7: The "model the aggregates rank last" study is not an SGG system and does not support SGG conclusions
**Problem**: The three compared models are MLPs on class embeddings, 12 box features, and frozen CLIP ViT-B/32 crops of subject and object (not union region, no context, no message passing), trained on a 100,000-relation subsample. The conclusion that pixels carry more case-level covariance while the aggregates rank them last is about this probe. Real SGG backbones (Faster R-CNN union features with contextual encoding) are the object of the paper's title. The finding that CLIP has "more covariance but not better ranking" depends on protocol, on label mix (it flips under label shift), and on a weighting that disagrees in sign.
**Evidence Anchor**: text: §6 "All three compared models are retrained on one fixed subsample of 100,000 training relations"
**Suggestion**: Move this section to the supplement or frame it as a controlled illustration. If kept, repeat with the released MOTIFS visual branch (the `vis`, `ctx`, `frq` logits already stored, so the path analysis is available).
**Severity**: Minor
**Confidence**: 4 — core expertise

### W8: Related work on unbiased SGG and its metrics is incomplete
**Problem**: Coverage is solid on TDE, IETrans, DLFE, PCPL, BGNN, but thin on 2022-2024 debiasing methods and on SGG evaluation. Specific gaps are listed in "Missing Key References". F@K (the harmonic mean of R@K and mR@K) is used in §5 without a citation or a note on where it was introduced. Open-vocabulary SGG gets one citation ([24]); relevance of the split to open-vocabulary predicate settings, where the predicate set per pair is much larger and zero-shot ranking matters, is not discussed. The paper does not discuss the "independent mR" and zero-shot recall (zR) metrics of [25, 27] beyond naming them, although the audit reports zR@50 = 0.1432 only in the supplement.
**Evidence Anchor**: absence: Related work (§2) — expected FGPL, SQUAT, PENET/HiLo-class methods and an F@K source; checked §1-§2 text and reference list [1]-[52]
**Suggestion**: Add the references below, cite the F@K source, and state which families of method the split could and could not audit (logit-releasing versus end-to-end).
**Severity**: Minor
**Confidence**: 4 — core expertise

### W9: Practicality of the proposed reporting standard
**Problem**: The recommendation (report both signed parts, AUC under two weightings, label-mix path, operating-point control, equivalence margin) needs dense per-pair scores for every label, which SGB-style code does not archive and which for SGDet exceed storage (up to 6,320 pairs per image). The paper says recovery required rerunning the checkpoint. A leaderboard-level adoption is unlikely without a lightweight protocol.
**Evidence Anchor**: text: §7 "it needs scores for every label, which most benchmarks do not archive; recovering them took a rerun of the released checkpoint"
**Suggestion**: Offer a minimal reporting subset (group-level share under LA control, within-pair AUC) and a hook for SGB's evaluator to dump top-k logits.
**Severity**: Minor
**Confidence**: 3

## Detailed Comments
### Literature Review
- **Coverage**: Good on classical debiasing and on statistics; missing recent SGG debiasing and any F@K attribution.
- **Integration quality**: Fair; the related work is organised by theme and ties each family to the contribution.
- **Research gap argument**: Persuasive for "no one attributes a gain between two models"; less so for "SGG audits are lacking" because prior-correction equivalence is already in [6, 42].

### Theoretical Framework
- **Appropriateness**: The covariance decomposition (Yates) is the right tool. Properness is correctly not needed for hit rates.
- **Application depth**: Deep and honest about the grouping dependence.
- **Alternative frameworks**: Possible comparisons to Shapley-style or counterfactual-evaluation attributions in the SGG context are absent.

### Academic Argument Quality
- **Factual accuracy**: Recomputed numbers match (log below). I found no numerical error.
- **Argument logic**: "TDE's gain is group-level" is supported; "TDE buys no discrimination" is supported only up to an equivalence margin under one weighting.
- **Terminology precision**: "case-level" and "group-level" are well defined. "Ranking within pairs" is used for both AUC and the matched quadratic part, which are different quantities.

### Contribution to the Field
- **Incremental contribution**: A methodological audit tool with SGG-specific evidence; incremental in SGG findings, new in accounting.
- **Positioning**: Clear relative to [25, 6, 42, 28].
- **Overclaiming**: Moderate (W1, W3, W4).

### Missing Key References
- Lyu et al., "Fine-Grained Predicates Learning for Scene Graph Generation" (FGPL), CVPR 2022; arXiv 2204.02597 (verified by search). Debiasing method whose gains the split could audit.
- SQUAT (Jung et al., CVPR 2023, stacked-query Transformer for SGG) [UNVERIFIED search lead; not located by my search].
- HiLo (Zhou et al., ICCV 2023, panoptic scene graph) [UNVERIFIED search lead].
- Gao et al., "Informative scene graph generation via debiasing" (DB-SGG) [UNVERIFIED search lead; not located by my search].
- Source of F@K (harmonic mean of R@K and mR@K) [UNVERIFIED; I believe it appears in the 2022-23 unbiased-SGG literature, check attribution].
- Open-vocabulary SGG/relationship detection (e.g. RLIP, OvSGTR) [UNVERIFIED search leads].

### Questions for Authors
1. Why is the DLFE audit (present in the repository) not reported? What is its split?
2. Do TDE on VCTree/Transformer backbones (same release) and a second training seed give the same share (87%) and AUC equivalence?
3. For SGCls/SGDet, what is the split on all relations with predicted-pair grouping?
4. Is the IETrans+Rwt group-level share driven by Rwt? Can IETrans without Rwt be trained against a same-recipe baseline?
5. When were the equivalence margin, the primary weighting, and the primary calibration protocol fixed relative to seeing the data? Can this be evidenced?
6. How should a reader weigh the case-level covariance against label ambiguity among near-synonymous predicates inside a pair?

### Minor Issues
- Abstract and Intro mix micro-pooled (+0.0972) and official (+0.1017) figures; "nine of the ten points" should state which.
- "Fig. 2" caption refers to a "T only (square)" marker; legend is hard to read in grayscale.
- §5 "Table 2 gives all six recall protocols" but the within-text share "from 77% at K = 20 to 86% at K = 100" skips the 87% at K = 50 (minor clarity).
- Reference [14] and [38] page lists show "3, 2" (back-reference formatting).
- The sentence "...but excludes zero in one.." in Seeds has a double full stop.

## Criterion-Bound Judgements
Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | reviewer-assigned domain remit (no venue binding) | PARTLY_MEETS | text: §2 "Our case-level term is not that resolution term" | New exact attribution for paired gains; SGG finding itself partly known | none identified | yes: conditional on W1 |
| Literature Integration | domain remit | PARTLY_MEETS | absence: §2 — FGPL, SQUAT-class methods, F@K source | Missing recent debiasing methods | references partly UNVERIFIED | no |
| Evidence Sufficiency (SGG claims) | domain remit | PARTLY_MEETS | table: Table 1, Table 35; absence: results/ DLFE | One backbone, two methods, one checkpoint pair | I did not rerun checkpoints | yes |
| Argument Coherence | domain remit | PARTLY_MEETS | text: §5 "Group-level is not a lesser gain" | Framing versus debiasing goal | none identified | yes |
| Significance and Impact | domain remit | PARTLY_MEETS | text: §7 reporting suggestions | Useful audit tool; adoption cost and scope narrow | none identified | yes |
| Methodological Rigor | not in remit (Reviewer 1) | NOT_ASSESSED | — | Statistical theory not assessed | — | no |
| Writing Quality | domain remit | MEETS | — | Dense but precise | — | no |

## Recomputation Log
Recomputed from `results/*.json` (read-only Python; I did not rerun checkpoints or code):
- results/sgg_recall_split.json, gc@50: total 0.09715, group 0.08411, case 0.01305, CI [0.00926, 0.01684]; share 86.6%. Matches paper (+.0972 / +.0841 / +.0130 / 87%). Official mR 0.2476 vs 0.1459 gives +0.1017, matches.
- Table 2: gc@20 0.0598/0.0462/0.0135 (77%); gc@100 0.1280/0.1099/0.0182 (86%); ng@20/50/100 totals −0.0037/−0.0337/−0.0489, case +0.0096/+0.0127/+0.0236. All match. Share for ng is >100% or undefined (see W5).
- TDE vs LA, gc@50: total +0.0031, case −0.0008 [−0.0050, +0.0033]. Matches. ng@100 vs LA +0.0148 [+0.0064, +0.0232]. Matches.
- LA1 vs none: total 0.0941, group 0.0802, case 0.0139 [0.0101, 0.0176]. Matches Table 1.
- IETrans vs none: total 0.2204, group 0.2143 (97.2%), case 0.0060 [−0.0031, +0.0151]. Matches.
- Tier split: body +0.1224 (group +0.1082), head −0.0255, tail +0.0003. Matches.
- F@50 (results/sgg_fk.json): TDE 0.3217, LA1 0.3435; paper "0.322 vs 0.344". Matches. R@50 costs 0.6612−0.4588 = 0.2024 (paper 0.2023, rounding) and 0.6612−0.6437 = 0.0175. Match.
- SGCls (sgg_sgcls_audit.json): TDE group share 98.5%, relation-AUC −0.0128 [−0.0171, −0.0074], comparison −0.0047 [−0.0122, +0.0031], matched fraction 58.2%. SGDet: total 0.0310, share 86.7%, matched 65.3%. Match.
- results/sgg_equivalence.json: relation-weighted TDE vs none equivalent=true, comparison-weighted equivalent=false. Matches text.
- results/vg_metric_bridge.json: MLP-VISUAL-S vs MLP-SPATIAL-S dR 0.0064 (raw), accuracy −0.0311 (CLIP 0.6156 vs 0.6467). Matches.
- Grouping dependence (results/sgg_grouping_share.json): class pair case 0.0130; subject-class-only case 0.0794 (group share about 18%). Consistent with the paper.
- Not verified: proofs, simulation coverage, the claims of pre-declaration, supp Q.1-Q.4 values beyond those above, citations other than FGPL.

No discrepancy between paper and stored results was found.

## Overall rationale
Unresolved decision-bearing criteria: scope and generality of evidence (W1, repairable by adding methods or narrowing claims), framing versus debiasing goal (W2, repairable by rewriting), subset and grouping validity in SGCls/SGDet (W3), and the IETrans confound (W4). Strengths on one criterion do not offset these. The statistical core is sound by my recomputation; the weaknesses are about SGG scope and interpretation.
