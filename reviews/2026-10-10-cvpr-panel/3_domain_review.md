# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 Submission #***** (anonymous)
- **Review Date**: 2026-10-10
- **Review Round**: Round 1 (simulated CVPR 2027 panel, full mode)

## Reviewer Information

### Reviewer Role
Peer Reviewer 2 (Domain)

### Reviewer Identity
Scene graph generation specialist: unbiased-SGG literature, metrics (R@K, mR@K, zR@K, F@K, PredCls/SGCls/SGDet, graph-constraint vs no-graph-constraint), the Scene-Graph-Benchmark.pytorch codebase and TDE/IETrans checkpoints, and open-vocabulary SGG.

### Review Focus
Whether the SGG-specific claims are accurate and adequately supported (TDE, IETrans, logit-adjustment control, metric semantics), whether the literature is covered, and how large and how general the contribution is for the SGG field. Statistical-estimator details are left to Reviewer 1.

Calibration status: `NOT_CALIBRATED`. No author-confirmed target context was supplied (`criteria_binding_unavailable`); no venue-alignment claim is made.

---

## Overall Assessment

### Recommendation
**Major Revision** (domain view). Confidence: 4 of 5.

Rationale in one line: a careful, reproducible, and useful audit of one released checkpoint, but the SGG claims in the abstract and conclusion are broader and firmer than the evidence (two Motifs-family checkpoints, one confounded comparison, selectively weighted AUC claims, micro-averaged rather than official mR).

### Summary Assessment
The paper proposes an exact decomposition of a score or mean-recall gain between two frozen models into a part that survives shuffling labels within an object-pair cell ("group-level") and a within-cell covariance ("case-level"). On the released TDE Motifs PredCls checkpoint it finds that 87% of the mR@50 gain is group-level and that a ranking-preserving logit adjustment recovers nearly all of it at a tenth of TDE's R@50 cost; a second released method (IETrans+Rwt) is 97% group-level with lower within-cell AUC.

I recomputed the headline numbers from the cached results and they agree with the manuscript. The TDE audit is the most convincing part: the replay of the official evaluator matches the released recalls, the control isolates the operating-point effect, and the branch-wise explanation (the averaged-context term is 99.96% one shared vector correlated +0.75 with the log prior) is clear and useful to the field. The weaknesses are domain-level. The conclusions are drawn from two methods of one backbone family on one dataset, but are phrased as statements about "debiasing methods" and "the field's metrics". The IETrans comparison is against a different, separately trained baseline. Several abstract-level statements ("under every measure", "gets worse") rest on one of two AUC weightings whose interval for the other weighting includes zero. The headline split is of micro-averaged recall, not the official per-image mR. Modern debiasing and open-vocabulary SGG methods are not audited, even though open-vocabulary SGG is invoked in related work. A Major Revision is appropriate; the core audit survives.

---

## Strengths

### S1: Exact, replayable audit of the TDE release
The offline replay of the official evaluator reproduces baseline R@50 0.6612 / mR@50 0.1459 and TDE 0.4588 / 0.2476, and my recomputation from `data/vg_motifs/motifs_*_recalls.json` agrees. The SGCls/SGDet replay reproduces the repository numbers (Table 33). This is rare in the SGG literature and makes every later split auditable.
**Evidence Anchor**: `text: §5 "The replay reproduces the official numbers to the fourth decimal: baseline R@50 = 0.6612 and mR@50 = 0.1459, TDE 0.4588 and 0.2476"`

### S2: The operating-point control is the right control for SGG
Subtracting tau*log pi from the baseline logits changes no within-pair ranking, so it separates "moved the operating point" from "learned to discriminate". The control reaches mR@50 0.2343 at R@50 0.6437, and F@50 of 0.344 vs TDE 0.322 (confirmed in `results/sgg_fk.json`: 0.3435 vs 0.3217). This sharpens a point the field knew qualitatively (DLFE, logit adjustment in SGG).
**Evidence Anchor**: `text: §5 "a one-line prior shift that ranks the relations of every cell exactly as the baseline did reproduces the gain, its split and its tier profile"`

### S3: Mechanistic explanation of TDE in PredCls
Under SUM fusion TDE reduces to ctx minus ctx_avg; Table 22 shows ctx_avg is 99.96% a single shared vector. This is a real insight about why TDE helps mean recall (predicates such as parked on move from 0.000 to 0.886 recall, per-predicate arrays in `results/sgg_recall_split.json`, index 35).
**Evidence Anchor**: `table: Supplement Table 22 — ctx(avg) global energy 0.9996, corr. with log pi +0.754`

### S4: Candid scope statements and protocol disclosure
The paper reports that the split is conditional on the declared grouping, that the within-cell part is not invariant to recalibration, that the IETrans comparison does not isolate relabelling, and that TDE's case-level sign depends on protocol (20 calibration halves, Table 26). Most SGG papers disclose far less.
**Evidence Anchor**: `text: §1 "What is not claimed" and §7 "Five bound what the split can say"`

---

## Weaknesses

### W1: Generality of the SGG conclusions rests on two Motifs-family checkpoints
**Problem**: The abstract and conclusion speak of "debiasing methods", "the field's metrics" and recommend benchmark reporting rules. The evidence is TDE (2020) on Motifs-SUM and one IETrans+Rwt Motifs checkpoint (2022), all VG150, all one backbone family. None of the later debiasing lines named in Related Work (BGNN [23], SHA+GCL [13], CogTree [47], PCPL [45], PE-Net/prototype [51], NICE [22], DLFE [6], RTPB [4]) is audited, and no one-stage or transformer SGG model is audited. Related Work also cites open-vocabulary SGG [24], but no open-vocabulary SGG model is audited (the zero-shot CLIP probe in Appendix Q is a classifier, not an open-vocabulary SGG method).
**Evidence Anchor**: `text: Abstract "TDE's ranking within pairs gets worse. A second released method, IETrans, gains 21 points, 97% group-level"` and `absence: §5-§7 and Appendix O-Q — expected an audit of any post-2022 debiasing or open-vocabulary SGG checkpoint; checked §5, §7, Appendix O, Q`
**Why it matters**: TDE's mechanism (a cell-constant shared counterfactual vector) is peculiar to its construction; it is a poor proxy for methods that re-weight losses or use prototypes, whose changes are not cell-constant. "Gains are group-level" may be close to definitional for TDE and a prior correction; it is an empirical question for the others.
**Suggestion**: Either (a) audit at least two to three further released checkpoints that are available in the public benchmark (for example a GCL/SHA-style and a prototype or hierarchical-loss method) and one open-vocabulary SGG model, or (b) retitle and rescope the abstract/conclusion to "TDE and IETrans+Rwt on Motifs". Recommend the benchmark-reporting proposal in §7 be presented as a proposal, not a finding.
**Severity**: Major
**Confidence**: 5 — core expertise: unbiased-SGG methods and their release status

### W2: The IETrans result is confounded and its "under every measure" wording is not supported
**Problem**: IETrans+Rwt is compared with a MOTIFS-SUM baseline that was trained separately, with a different fusion of the visual term (Supp. O.2). The released model also combines relabelling with a reweighted loss and adds a test-time log-prior. The abstract nevertheless presents IETrans as "loses within-pair discrimination under every measure". In the supplement, the comparison-weighted AUC change is -0.0093 with interval [-0.0181, +0.0004] (includes zero), the mR case-level part is +0.0060 [-0.0031, +0.0151], the no-graph-constraint case-level part is -0.0018 [-0.0134, +0.0099], and the case-level part against LA1 and TDE straddles zero. Only the relation/cell-weighted AUC and the matched proper-score parts exclude zero, and the latter are shown elsewhere to depend on temperature and class-bias matching (Table 32 shows -0.0168 with class bias, so it is stable there).
**Evidence Anchor**: `table: Supp. Table 19 — "IETrans vs base 0.5612 0.5705 -.0093 [-.0181, +.0004]"` and `text: Abstract "loses within-pair discrimination under every measure"`
**Why it matters**: IETrans is the paper's only evidence that a training-data-level method (as opposed to TDE) buys no discrimination; "loses" is a stronger claim than the intervals warrant, and the architectural/training mismatch means the loss cannot be assigned to IETrans.
**Suggestion**: Report that "point estimates are negative under all measures and interval excludes zero under X of Y"; delete "under every measure" from the abstract. If possible, train a matched Motifs-SUM baseline with the IETrans data pipeline (the IETrans code is public), or train the IETrans variants (internal transfer only, external transfer only, Rwt only) to isolate relabelling.
**Severity**: Major
**Confidence**: 4 — direct recomputation from Supp. Tables 19, 24 and 32 and familiarity with the IETrans training recipe

### W3: AUC-based claims depend on which of two weightings is quoted
**Problem**: The within-cell AUC is the paper's "threshold-free" evidence, but its two weightings disagree on significance in several places and the abstract quotes the one that supports the narrative. SGCls: relation-weighted change -0.0128 [-0.0171, -0.0074] (quoted in main text and abstract as "gets worse") versus comparison-weighted -0.0047 [-0.0122, +0.0031] (`results/sgg_sgcls_audit.json`, Table 34). IETrans: -0.0235 (cell-weighted, quoted) versus -0.0093 [-0.0181, +0.0004]. CLIP vs geometry: +0.0085 [-0.0062, +0.0214] versus -0.0067 [-0.0120, -0.0019]. The comparison weighting is dominated by head-head pairs (65% of weight, Table 31), where TDE's change is +0.0068 [-0.0003, +0.0134].
**Evidence Anchor**: `table: Supp. Table 34 — SGCLS TDE vs base ∆AUCc -.0047 [-.0122,+.0031], ∆AUCr -.0128 [-.0171,-.0074]`
**Why it matters**: Absence of detected change in TDE's within-cell ranking is also reported ("no measure detects"), yet the baseline within-cell AUC is only 0.5705, so the test has limited power; the confidence intervals on the TDE change are about +/-0.0055, which cannot rule out a change comparable to the CLIP-vs-geometry effects the paper treats as meaningful. "No change detected" is not "no change".
**Suggestion**: Pre-specify one primary weighting (justified in SGG terms: per-relation matches how mean recall counts relations) and state the other as secondary in every place it appears; add an equivalence-type statement (the smallest AUC change excluded by the interval) for TDE; in the abstract report both weightings for SGCls and IETrans.
**Severity**: Major
**Confidence**: 4 — metric-semantics expertise; numbers verified from `results/` files

### W4: The headline split is of micro-averaged recall, not the official mR, and the graph-constraint caveat is understated
**Problem**: The "87% (83-91%)" figure is for micro-pooled mean recall over identified relations (0.0972 total), while official per-image mR gives +0.1017; the paper says the two "track" each other but gives no decomposition of the official metric, no uncertainty on the discrepancy, and drops 1.1% of relations (singleton cells). More important for SGG: with the graph constraint, each pair contributes one predicate, so a mean-recall gain is almost by construction a change in which predicate wins within a cell. Without the graph constraint (the more permissive protocol, and the one used by several recent papers), TDE's mR@50 falls from 0.3260 to 0.2981, and the group-level part is -0.0464 (`results/sgg_recall_split.json`, ng@50). The paper reports this in one sentence in §5 but still frames "ten points" as TDE's gain throughout.
**Evidence Anchor**: `text: §5 "without the graph constraint TDE's mean recall falls, from 0.3260 to 0.2981"`
**Why it matters**: Whether "ten points" is a gain depends on the protocol; the title question is therefore partly a graph-constraint question. The conclusion is arguably stronger (and more interesting) than the paper makes it: a method whose mR gain flips sign without the graph constraint is not producing more discriminative scores.
**Suggestion**: Present both protocols side by side in Table 1 (ng-mR is in the supplement), say that TDE reports graph-constraint mR in its own paper, and report the official-metric decomposition (or at least bound the micro-vs-official difference with a bootstrap over images).
**Severity**: Major
**Confidence**: 4 — direct knowledge of the benchmark protocol; numbers recomputed

### W5: No headroom reference, so "87% group-level" cannot be interpreted
**Problem**: On the paper's own data the baseline's within-cell AUC is 0.5705 (comparison-weighted) and MOTIFS-style models gain at most about 0.01-0.02 of case-level quadratic score from geometry or pixels. Case-level signal available in VG150 PredCls is therefore tiny relative to group-level movement for any method that touches the predicate prior. A group-level share near 90% may then be the expected outcome of almost any debiasing method on this benchmark, and the paper gives no reference method that does gain case-level mR (for example a strong visual-relation model or an oracle that uses the true label within the cell).
**Evidence Anchor**: `table: Supp. Table 19 — baseline within-cell AUC 0.5705; TDE 0.5731; IETrans 0.5612` and `absence: §5 — expected a reference or upper-bound model for case-level mR gain; checked §3-§7 and Appendix N, O`
**Why it matters**: Without a reference the reader cannot tell whether 13 thousandths of case-level mR is small or typical, and the recommendation to "report the split" has no calibrating scale.
**Suggestion**: Add a reference point: the case-level mR obtained by adding a visual term to the class-pair-only model (the paper has such models for the quadratic score; carry them into mR), and an oracle bound; report case-level share per method relative to that.
**Severity**: Major
**Confidence**: 3 — inference from the paper's own AUCs; no external benchmark of case-level headroom exists

### W6: The normative reading of "case-level" as the real gain is not argued for VG label semantics
**Problem**: The framing treats case-level discrimination as what a debiasing method should buy and group-level movement as something lesser. In VG150, within-pair predicate choice (on vs parked on vs standing on) is largely annotator-driven and ambiguous, and the paper's AUCs (0.53-0.61) show little image-determined structure. A move from "on" to "parked on" for (car, street) may be what users of a scene graph want (more informative predicates), even if it is not image-conditional. The paper's own supplement says a transported gain is "a description of where score was earned, not an accusation", but the title, abstract and §1 tone read as one.
**Evidence Anchor**: `text: §1 "What did those ten points buy? A model can move probability towards rare predicates within each subject-object pair"` and `absence: §7 — expected a discussion of predicate ambiguity and informativeness as a legitimate target of debiasing; checked §1, §2, §7`
**Why it matters**: Domain readers (and TDE/IETrans authors) will contest the framing; zero-shot recall is also supported, and TDE raises zR@50 from 0.110 to 0.143 (`data/vg_motifs/motifs_*_recalls.json`), a result in the supplement only that bears directly on whether the method "bought" anything on unseen compositions.
**Suggestion**: Add a paragraph on the semantics of group-level movement in SGG (informativeness vs bias), and split zero-shot recall and F@K with the same estimator. Cite the source of F@K and of the head/body/tail protocol (see Minor Issues).
**Severity**: Minor — the weakness is one of framing and does not alter any number
**Confidence**: 4 — domain judgement; not a measurable defect

### W7: SGCls/SGDet audits cover a matched subset and the main text does not say so
**Problem**: In SGCls only 58% of relations (65% in SGDet) have a matched pair and enter the AUC and proper-score parts (Supp. Q.5, `results/sgg_sgcls_audit.json` "matched_fraction"). The main paper's "In SGCls ... 99% group-level" refers to mean recall (unmatched relations are misses for all models), but the AUC "gets worse" claim refers to the matched subset only, and the main text does not mention this. The grouping is the ground-truth class pair, which is not the pair the model predicted; case-level effects of detection errors are removed by design. In SGDet, the case-level mR part is +0.0041 with interval excluding zero and is matched exactly by the control, which the main text reports.
**Evidence Anchor**: `text: Supp. Q.5 "the AUC and the proper score use the relations with a matched pair (58% in SGCls)"` and `text: §5 "TDE's within-cell ranking gets worse, by -0.0128 of relation-weighted AUC"`
**Why it matters**: SGCls/SGDet are the settings in which object-level uncertainty interacts with predicate bias; conclusions drawn on the 58-65% subset may not carry to the full test set.
**Suggestion**: State the matched fraction wherever an SGCls/SGDet AUC or proper-score number appears in the main text; report selection sensitivity (the matched subset is chosen by object detection success, which correlates with easy, head pairs).
**Severity**: Minor
**Confidence**: 4 — verified in `results/sgg_sgcls_audit.json` and Supp. Q.5

### W8: Positioning relative to prior SGG findings is thin; novelty in SGG is mainly the accounting, not the finding
**Problem**: That a post-hoc prior correction matches or beats TDE-style debiasing is acknowledged as known ([6], [28], [42]) and the paper says so; the new SGG-specific content is therefore the exact accounting and the TDE mechanism. Missing context: work on mean-recall pathologies beyond [25] and on the head-versus-tail trade-off in R@K vs mR@K (F@K) is not engaged; the survey and benchmark literature is absent. See missing references.
**Evidence Anchor**: `absence: §2 Related work — expected prior SGG evaluation and survey work and recent open-vocabulary SGG; checked §1, §2, reference list [1]-[52]`
**Why it matters**: Readers need to see what is new for SGG relative to the existing known equivalence of prior correction and debiasing.
**Suggestion**: Add an explicit sentence in the contributions separating "known" (prior correction rivals debiasing) from "new" (exact two-way accounting; TDE reduces to ctx minus a shared vector; IETrans within-cell loss).
**Severity**: Minor
**Confidence**: 3 — based on my knowledge of the literature, one gap check by search

---

## Recomputation Log

All recomputation used read-only Python over `results/*.json` and `data/vg_motifs/*.json` (outside-repository scratch only).

| # | Claim (location) | Recomputed | Result |
|---|---|---|---|
| 1 | Baseline mR@50 14.6, TDE 24.8 (Abstract, §1) | `motifs_*_recalls.json`: 0.14589 / 0.24763 | Agrees |
| 2 | R@50 baseline 0.6612, TDE 0.4588 (§5) | 0.66116 / 0.45883; drop 0.2023 | Agrees |
| 3 | mR@50 gain pooled 0.0972, group +0.0841, case +0.0130 [0.0093, 0.0168] (Tab. 1) | `sgg_recall_split.json` gc@50: 0.09715, 0.08411, 0.01305 [0.00926, 0.01684] | Agrees |
| 4 | 87% group-level, interval 83-91% (Abstract) | 0.8657; `sgg_share_intervals.json` CI [0.8256, 0.9058] | Agrees (rounding) |
| 5 | Official-average gain 0.1017 vs pooled 0.0972 (§5) | official mR@50 0.24763-0.14589 = 0.10174 | Agrees; micro-vs-official gap 4.6% of the gain |
| 6 | Control +0.0941, group +0.0802, case +0.0139; TDE-LA case -0.0008 (Tab. 1) | `sgg_share_intervals.json` la1 total 0.0941, group 0.0802; difference of TDE and LA rows arithmetic | Agrees |
| 7 | "Nine of the ten points" (Abstract) | 0.0941/0.0972 = 96.8% | Agrees |
| 8 | Control cost 0.0175 vs TDE 0.2023 in R@50, under a tenth (§5) | 0.0175/0.2023 = 8.7% | Agrees |
| 9 | F@50 0.344 (control) vs 0.322 (TDE) (§5) | `sgg_fk.json`: 0.3435, 0.3217 | Agrees |
| 10 | Head -0.0255, body +0.1224, tail +0.0003 (§5) | `sgg_recall_split.json`: -0.02553, +0.12242, +0.00026 | Agrees |
| 11 | Tail: baseline recalls none, TDE one of 15 tail predicates (§5) | Official per-predicate arrays: 0 vs 1 nonzero, TDE recall 0.0164 | Agrees (tiers are 1-based) |
| 12 | parked on 0.000 to 0.886; on falls 0.558 (§5) | Official per-predicate arrays, index 35 and 31: +0.862 and -0.531 at the official per-image average | Does not match as written: 0.886/0.558 are quoted from the pooled version; official per-image differences are 0.862 and 0.531. Minor; state which version Fig. 3 uses |
| 13 | No-graph-constraint mR@50 0.3260 to 0.2981 (§5) | `ng@50`: 0.32605, 0.29807 | Agrees |
| 14 | TDE within-cell AUC +0.0026 [-0.0028, +0.0086] comparison; -0.0015 relation (Tab. 1) | `sgg_rank_contrast.json`, `sgg_auc_tde_la.json` | Agrees |
| 15 | SGCls TDE +0.0517, 99% group, control +0.0518, R@50 0.384 vs 0.263; AUC -0.0128 [-0.0171, -0.0074] (§5) | `sgg_sgcls_audit.json`: 0.05172, 0.9852, 0.05181, 0.3840/0.2631, -0.01280 | Agrees; comparison-weighted -0.0047 [-0.0122, +0.0031] not in main text; matched fraction 0.582 |
| 16 | SGDet control +0.0418 vs TDE +0.0310 at nearly twice the R@50 (§5) | `sgg_sgdet_audit.json`: 0.04184 vs 0.03101; R@50 0.3186 vs 0.1657 | Agrees; matched fraction 0.653 |
| 17 | IETrans +0.2204, 97% group-level, case +0.0060 [-0.0031, +0.0151] (§5) | `sgg_share_intervals.json` 0.97266, group 0.21433; Supp. Tab. 24 | Agrees; the share CI [0.902, 1.044] exceeds 1 |
| 18 | IETrans AUC "falls under every measure" (Abstract, §5) | Supp. Tab. 19: comparison -.0093 [-.0181, +.0004] | Interval includes zero; see W2 |
| 19 | TDE zero-shot recall (Supp. O) | `motifs_*_recalls.json`: zR@50 0.1102 to 0.1432 | Agrees with 0.1432; baseline value not stated in the paper |
| 20 | TDE top-1 accuracy 0.5577 vs 0.6981 (Supp. O) | `sgg_audit_motifs.json` | Agrees |
| 21 | Baseline within-cell AUC | `sgg_rank_contrast.json`: 0.5705 | Used in W5 |

Not recomputed (outside time budget or requires data not in the repository): the proper-score splits from raw logits (only cached result files were read), the tier counts (9/26/15) from raw training counts, and the coverage simulations.

---

## Detailed Comments

### Literature Review
- **Coverage**: Mainstream unbiased-SGG methods are cited (TDE, VCTree, KERN, BGNN, SHA+GCL, PCPL, CogTree, DLFE, RTPB, NICE, PE-Net, IETrans, Structured Sparse R-CNN) and the statistical literature is rich. Missing: SGG surveys/benchmarks, open-vocabulary SGG beyond one CVPR 2024 paper, and recent one-stage SGG.
- **Integration quality**: Related Work is well organised ("Bias and its evaluation", "Proper-score decompositions", "Comparing two predictors") and distinguishes the contribution from the reliability/resolution decomposition, the grouping loss and permutation importance.
- **Research gap argument**: Convincing in general ("none attributes the gain between two models to one route or the other"); in SGG specifically, the gap argument needs the "known versus new" separation of W8.

### Theoretical Framework
- **Appropriateness**: Proper-score and covariance decompositions are an apt framework for separating prior fit from per-case evidence.
- **Application depth**: Deep (formal results B.1-B.6). Domain caution: Prop. 1 says the group-level part is not "prior fit" (it includes a dispersion term); the main text still says "group-level" correctly.
- **Alternative frameworks**: An explicit conditional-independence or causal-mediation reading (what TDE itself claims to estimate) is not contrasted; an unbiased-SGG reader would want to know whether the split agrees with TDE's own direct-effect notion.

### Academic Argument Quality
- **Factual accuracy**: The SGG numbers I could check are accurate. Attribution of mean recall as headline metric to [5, 39] is reasonable. "Head/body/tail-stratified recall [23]" should be checked against the origin of that protocol ([13] and others); see Minor Issues.
- **Argument logic**: The step from "no measure detects a change" to "leaves within-group ranking unchanged as far as we can detect" is hedged correctly in the conclusion; the abstract is less careful (W2, W3).
- **Terminology precision**: "Group-level", "case-level", "WAGER" (supplement) and "transported/within-group covariance" (supplement) are different names for the same quantities; consistent in the paper but confusing across files. "Debiasing" is used for methods whose actual effect the paper argues is an operating-point shift.

### Contribution to the Field
- **Incremental contribution**: Methodological and empirical. For SGG: a precise explanation of what TDE's mR gain consists of; a reproducible audit tool; a recommended reporting protocol. Significant for evaluation practice if generalised.
- **Positioning**: Clear against statistics literature; thinner against SGG evaluation papers.
- **Overclaiming**: Moderate (abstract/conclusion generalise from two checkpoints; "under every measure"; "gets worse").

### Missing Key References
I can attest only to those marked verified; the rest are search leads.
- Chen, Wu, Lei, Zhang, Chen, "Expanding Scene Graph Boundaries: Fully Open-vocabulary Scene Graph Generation via Visual-Concept Alignment and Retention", ECCV 2024 (OvSGTR). Verified to exist by web search; relevant because the paper cites open-vocabulary SGG only through [24] and claims open-vocabulary methods "inherit" the metric pathologies.
- Source for F@K: [UNVERIFIED] a web search did not locate the paper that introduced F@K; the manuscript uses F@K in §5 without a citation and the authors should cite the original proposal.
- [UNVERIFIED] SGG survey literature, e.g. the comprehensive survey of scene graph generation by Li et al. (2022): a search lead for context on metrics and protocols.
- [UNVERIFIED] Work on predicate-ambiguity and multi-label relationship evaluation in VG (search lead: "multi-label" or "predicate ambiguity" relation prediction evaluation), relevant to W6.
- [UNVERIFIED] Recent one-stage / transformer SGG (SGTR, Pair-Net for PSG) as audit targets for W1.

---

## Questions for Authors

1. TDE's zero-shot recall rises from 0.110 to 0.143 (zR@50). How much of that zero-shot gain is group-level versus case-level under your estimator, and does the logit-adjustment control reproduce it? This bears directly on the "what did the points buy" question for compositions never seen in training.
2. Can the IETrans conclusion be made against a matched baseline (same Motifs-SUM trained with and without the IETrans data pipeline, or with and without Rwt)? If not, would the authors remove IETrans from the abstract's quantitative claims?
3. Which AUC weighting is the pre-specified primary in each setting, and what is the smallest within-cell AUC change for TDE that your intervals exclude? How does that compare with the CLIP-vs-geometry difference you call real?
4. What does the split give for the official per-image mR (not the micro-pooled version), and with the no-graph-constraint protocol in Table 1? Would you state that the "ten points" are a graph-constraint effect?
5. Do you expect the group-level share to be similar (about 90%) for a prototype or hierarchical-loss method that changes within-cell rankings? If so, why; if not, what is the evidence?

---

## Minor Issues

### Language / Grammar
- §1 and Fig. 1 use "group-level"/"case-level"; the supplement uses "transported gain"/"within-group covariance gain" and the name "WAGER"; add a one-line mapping in the main text or unify.

### Citation Format
- F@K (§5) has no citation to where it was introduced.
- "head/body/tail-stratified recall [23]": verify that [23] (BGNN) is the origin of this protocol, or cite the work that introduced it (candidate: [13]).
- [14] and [38] pages show "3, 2" and [32], [35] list pages beyond the main text; check back-reference numbering.

### Figures and Tables
- Fig. 3 predicate labels are small; state whether it uses pooled or official per-image recalls (item 12 in the log: 0.886 and 0.558 versus the official 0.862 and 0.531).
- Table 1 should show the no-graph-constraint row and the baseline and TDE R@50 beside the mR split.
- Report the baseline zR@50 alongside the TDE value 0.1432 (Supp. O).

### Layout
- The main paper is dense; the SGCls/SGDet paragraph carries several results and the matched-subset caveat is only in the supplement.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`. No author-confirmed target context supplied (`criteria_binding_unavailable`).

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | Seat configuration (domain) | MEETS | `text: Abstract "splits the difference between two frozen models ... exactly"` | New exact accounting of paired gains and a new explanation of TDE's gain; prior correction rivals debiasing was known | SGG-specific finding partly known | no |
| Methodological Rigor | Not in my remit (Reviewer 1) | NOT_ASSESSED | — | — | — | no |
| Evidence Sufficiency | Seat configuration (domain) | PARTLY_MEETS | `text: §5 and Supp. Tab. 19, 24, 34` | TDE evidence strong; IETrans confounded; AUC claims weighting-dependent; two methods only | Could not re-run models | yes |
| Argument Coherence | Seat configuration (domain) | PARTLY_MEETS | `text: Abstract "under every measure"` | Core argument coherent; abstract overstates | — | yes |
| Writing Quality | Seat configuration (domain) | MEETS | `text: §1` | Clear and candid; heavy density | — | no |
| Literature Integration | Seat configuration (domain) | PARTLY_MEETS | `absence: §2 — expected SGG evaluation/survey and open-vocabulary SGG; checked §1, §2, references` | Strong statistics side, thinner SGG evaluation side | Web check limited | yes |
| Significance & Impact | Seat configuration (domain) | PARTLY_MEETS | `text: §7 "We suggest that benchmarks ... report"` | Potentially influential for SGG evaluation; depends on generality (W1) | Depends on W1 | yes |

Unresolved decision-bearing criteria: Evidence Sufficiency (W1, W2, W3, W4, W5; repairable by additional audits and rescoping), Argument Coherence (W2, W3; repairable by rewording), Literature Integration and Significance (repairable). None appears to make the core TDE finding invalid, which is why the recommendation is Major Revision rather than Reject.
