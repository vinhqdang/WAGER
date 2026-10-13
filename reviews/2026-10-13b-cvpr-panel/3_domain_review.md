# Peer Review Report: Peer Reviewer 2 (Domain: Scene Graph Generation)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission #***** (anonymous), repo commit 2da86a9
- **Review Date**: 2026-10-13
- **Review Round**: 1

Calibration Status: `NOT_CALIBRATED`
`criteria_binding_unavailable` (no venue-criteria binding supplied; no venue-alignment claim is made.)

## Reviewer Information
**Role**: Peer Reviewer 2 (Domain). **Identity**: SGG specialist (unbiased SGG, TDE/IETrans/DLFE, SGB codebase, PredCls/SGCls/SGDet, mR@K/F@K, open-vocabulary SGG). **Focus**: domain accuracy, SGG literature coverage, whether the SGG claims are properly scoped, and contribution to the field. Statistical-method detail is left to Reviewer 1.

## Overall Recommendation
**Major Revision** (borderline weak accept / weak reject on a CVPR scale). Confidence: **4/5** (core SGG expertise; the statistical-theory proofs are outside my remit).

## Recomputation Log (read-only, from repo artifacts)
| Claim | Source | Result |
|---|---|---|
| Replay reproduces official baseline/TDE: R@50 .6612/.4588, mR@50 .1459/.2476, ng-mR@50 .3260/.2981 | data/vg_motifs/motifs_*_recalls.json | Matches (.14589, .24763, .32605, .29807) |
| mR@50 gain TDE 0.0972 micro / 0.1017 official; 87% group-level | results/sgg_recall_split.json | total .09715, group .08411, share .8657; official diff .10174. Matches |
| Share interval [83,91]% | results/sgg_share_intervals.json | [.826,.906]. Matches |
| Independent split recomputed from raw ranks (data/vg_motifs/wager_sgg/variant_*.npz, cells = subj x obj, w=1/(50 n_y), cells n>=2) | my own script | TDE vs base: T .0956 / P .0828 / R .0128 (share .867); LA1 vs base: .0926/.0790/.0136; TDE vs LA1 case-level -.0008. Agrees with paper up to my normalisation (~1.6% lower total) |
| Within-cell AUC, comparison-weighted, recomputed from stored probs | my own script | base .57054, TDE .57308, LA1 .57054 (paper: +.0026 for TDE, ~0 for LA). Matches |
| F@50: LA .344 vs TDE .322 | results/sgg_fk.json; R,mR from Tab. 17 | .3435 vs .3216. Matches |
| LA R@50 cost .0175 vs TDE .2023-.2024 | Tab. 17 (official R@50 .6612, .6437, .4588) | Matches; note the micro-pooled R@50 in results JSON gives a different gap (.0161 vs .2183), so "cost" figures mix the official statistic with the micro-pooled split (disclosed, but easy to confuse) |
| TDE vs LA1 by K (Tab. 2) | results/sgg_recall_split_TDE_vs_la1.json | gc@20 -.0234, gc@50 +.0031, gc@100 +.0300; ng@20/50/100 -.0792/-.1272/-.1549. Matches |
| Published-number sanity (MOTIFS-SUM mR@50 ~14.6, TDE ~24.8-25.5, IETrans+Rwt mR@50 ~35.8, F@50 ~41) | my knowledge of Tang'20 / Zhang'22; not re-fetched | Consistent (IETrans F@50 .414 in sgg_fk.json) |

I found no numerical discrepancy in the SGG headline numbers. I did not re-verify SGCls/SGDet, the DLFE rerun or the CIFAR/Waterbirds parts.

## Summary Assessment
The paper proposes an exact, model-free decomposition of a paired score gain into a group-level part and a case-level covariance, and applies it to released MOTIFS-family checkpoints (TDE, DLFE, IETrans) on VG150. Its SGG conclusion is that most mean-recall gain is a within-object-pair shift of predicate preference that a training-free logit adjustment reproduces at K=50 with the graph constraint, with no detectable change in within-pair ranking. The auditing effort is unusually careful for SGG: the offline evaluator replay reproduces the official numbers, the control is clean, and I could reproduce the key figures from the shipped arrays. As a metric-hygiene contribution the work is useful and the writing is candid about limits. My concerns are domain scope and interpretation: the audited methods are all 2020-2022 and post-hoc or loss-level, the headline control match is specific to one (K, constraint) cell, the "case-level" reading depends on a single-label view of an ambiguous annotation, SGCls/SGDet coverage is thin, and a recent literature on post-2022 unbiased SGG and on multi-label predicate evaluation is not engaged. I think the contribution is real but narrower than the title and abstract suggest.

## Strengths
### S1: Exact replay of the official SGG evaluator enabling counterfactual recall
Evidence Anchor: text: Appendix O, Table 17 "re-scored" rows equal "official" rows for R@50, mR@50, ng-R@50, ng-mR@50, mR@100; confirmed by me from data/vg_motifs/motifs_*_recalls.json.
Matching through duplicate boxes, graph constraint and the zero-for-absent-predicate rule are handled; this is the hard engineering step most SGG metric critiques skip.

### S2: Training-free logit-adjusted control and within-pair AUC separate "operating point" from "ranking"
Evidence Anchor: table: Tab. 1, TDE-LA row, case-level -.0008 [-.0050,+.0033]; AUC change for LA +.0001.
Independently reproduced (AUC .5705 / .5731 / .5705). It correctly tells the field that a thresholded case-level part can be spent discrimination, which is a real pitfall for mR@K users.

### S3: Candid scoping of what the audit shows
Evidence Anchor: text: Sec. 5 "The control's match of TDE's gain is specific to K = 50 under the constraint"; Sec. 7 Limitations.
Reports K=20/100 and the no-graph-constraint protocol (Tab. 2), where TDE and the control diverge, and states IETrans is compared with a separately trained baseline.

### S4: Useful negative finding on the graph constraint
Evidence Anchor: table: Tab. 2, ng-mR@50 TDE vs baseline -.0337; Appendix Tab. 17 ng-mR@50 .3260 to .2981.
TDE's mean-recall gain reverses without the graph constraint while LA1 reaches ng-mR@50 .4173. This is substantive domain information.

## Weaknesses (ranked)

### W1: Headline "a ranking-preserving logit adjustment recovers TDE" is true only at one (K, constraint) cell, but is stated unconditionally in the abstract and conclusion
**Problem**: At K=20 the control trails/leads in the opposite direction (TDE trails by .0234), at K=100 TDE leads by +.0300 with case-level +.0034, and without the graph constraint the control exceeds TDE by .08-.15 mR with case-level +.0148 [+.0064,+.0232] at K=100 (my recompute of Tab. 2 confirms). The abstract says LA "recovers +0.094 of its +0.097 at under a tenth of TDE's cost in recall" and the Conclusion says "TDE's is matched by a ranking-preserving logit adjustment". The caveat sits in a parenthetical and in Sec. 5.
**Evidence Anchor**: text: Abstract "a logit adjustment that changes no ranking within any pair recovers +0.094 of its +0.097"; table: Tab. 2 ng-mR@100 row and TDE vs LA mR@100 +.0300.
**Why it matters**: Mean recall at K=20/50/100 with and without constraint are all standard SGG reporting cells; an abstract claim must hold across them or be explicitly restricted. The no-constraint results also show LA, not TDE, is the stronger debiasing there, which changes the narrative about what TDE "bought".
**Suggestion**: State in the abstract and conclusion "at K=50 with the graph constraint" and add a one-sentence summary of the other cells; add a main-text figure with all six protocols for TDE and LA; consider tuning tau for LA across K only as a sensitivity row (the paper's fixed tau=1 is conservative for TDE, which is good, but state it).
**Severity**: Major | **Confidence**: 5 — core SGG expertise, recomputed.

### W2: "Case-level" and "ranking" are measured against single-label VG150 annotations, so predicate synonymy and multi-label ambiguity are conflated with discrimination
**Problem**: VG150 predicates are heavily overlapping (on / parked on / standing on / sitting on; has / wearing). The within-pair AUC uses log q(y) - log q(z) against the one recorded label. A method whose purpose is to prefer specific predicates over generic ones (IETrans, relabelling) will necessarily "lose" AUC versus original labels (-.0235), and the paper reads this as ranking falling. The paper notes merging synonymous predicates "changes none of this" (Sec. 5), but merging by what scheme is not specified in the main text. Absolute AUC levels are near chance (.57 comparison-weighted, .61 relation-weighted for MOTIFS; .53 for the geometry MLP), so the instrument has little dynamic range: most of what any model does within a pair is invisible to it.
**Evidence Anchor**: table: Tab. 1 IETrans row, "∆AUCr -.0235 [-.0275,-.0182]"; dataset: results/sgg_rank_contrast.json (auc_new .5731, auc_old .5705; geometry MLP .5323 in results/vg_visual_rank.json).
**Why it matters**: The claim that IETrans "falls" in within-group ranking is a statement about agreement with noisy original labels, not about worse visual discrimination, and the SGG community has argued precisely this (IETrans's own motivation). The reader could wrongly infer that relabelling hurts the model.
**Suggestion**: Add a main-text analysis on a predicate-merged or multi-label-annotated evaluation (e.g., the paper's own synonym merge, or a hierarchy such as generic vs specific predicates), report AUC separately for generic-vs-specific pairs and specific-vs-specific pairs, and tone down "its within-pair ranking falls" for IETrans. Report absolute AUCs in the main text.
**Severity**: Major | **Confidence**: 4 — field knowledge of VG label ambiguity; no external norm needed here since this is an interpretation issue.

### W3: Audited method set is dated and narrow for a 2027 claim about "debiasing methods"
**Problem**: Three MOTIFS-based, 2020-2022 methods, one checkpoint each ("we audit no later method"). Title and abstract speak of "Debiasing methods for scene graph generation". Post-2022 unbiased-SGG work (query/transformer-based and VLM-based, e.g., the SQUAT line and the Vision Relation Transformer line, plus open-vocabulary SGG work) operates with different training recipes and may show case-level gains. The paper cites open-vocabulary SGG [24] only as a footnote on metrics. TDE, DLFE and (by the paper's own account) the IETrans test-time prior are all per-pair/per-predicate prior corrections, so "group-level" is close to built in for this family.
**Evidence Anchor**: text: Sec. 7 "we audit no later method"; absence: Related work and Sec. 5 — expected any post-2022 unbiased-SGG checkpoint (transformer/one-stage or VLM-based) or a discussion of why none is auditable; checked Sec. 2, Sec. 5, Sec. 7 and the reference list [1]-[53].
**Why it matters**: The generalisation "mean-recall gains of debiasing are almost entirely group-level" is not supported beyond prior-correcting methods; a result that methods designed as prior corrections gain from prior correction is less surprising than the framing implies.
**Suggestion**: Either (a) audit at least one method that is not a prior/loss reweighting on MOTIFS (many recent ones release PredCls checkpoints with logits obtainable from the SGB-style code) or (b) retitle and scope the claims to "post-hoc and loss-level prior correction of MOTIFS-family models". Say explicitly which methods in Sec. 2 are expected to behave differently.
**Severity**: Major | **Confidence**: 4 — field coverage, though I cannot verify checkpoint availability.

### W4: Dependence of the 87% share on the grouping is a first-order result, not a limitation
**Problem**: Grouping by subject class alone gives 18% group-level (case .0794 vs .0130 in results/sgg_grouping_share.json, which I read), by class-pair 87%, by class-pair x position 90%. The text justifies the class pair as what "the benchmark's construction defends". In PredCls the frequency baseline conditions on exactly that pair, which makes it natural, but object class conditioned predicate choice (man-riding-surfboard vs man-carrying-surfboard) is also real scene understanding in many users' eyes; the class-pair cell classifies it as "free".
**Evidence Anchor**: dataset: results/sgg_grouping_share.json "subject class" share 18% (group .0175 of total .0970) versus "class pair (paper)" .0841; text: Sec. 7 "dropping the object class takes it to 18%".
**Why it matters**: The paper's practical recommendation ("the benchmark should declare phi") shifts the problem rather than solving it. For SGG specifically, whether the object-conditioned prior counts as a "bias" is the central debate of the unbiased-SGG literature.
**Suggestion**: Promote the grouping-share table (subject, object, pair, pair x geometry) to the main paper, and say plainly that the 87% statement is "relative to the frequency-baseline's own conditioning". Add a version grouped by the full visual-free baseline's input (class pair + box geometry bins) as the reference.
**Severity**: Major | **Confidence**: 4.

### W5: SGCls and SGDet evidence is too thin to support "replications agree"
**Problem**: SGCls: only 58% of relations have a matched pair (Sec. 5), TDE case-level +.0008 CI [-.0024,+.0040] (results/sgg_sgcls_audit.json). SGDet: one comparison reported (control +.0418 vs TDE +.0310) and only TDE, not DLFE or IETrans. In detection modes the objects (hence cells) are predicted, and recall depends on detection; which relations are lost is selection-dependent.
**Evidence Anchor**: text: Sec. 5 "58% of relations have a matched pair"; dataset: results/sgg_sgcls_audit.json matched_fraction .5823.
**Why it matters**: SGDet is the metric most of the SGG community reports; claims limited to PredCls with GT boxes and labels should be advertised as such.
**Suggestion**: State "PredCls" in the title/abstract; add the SGCls/SGDet group-level share intervals to a main-text table, and state how matched-pair selection could bias the share (e.g., re-weighting by inverse matching probability).
**Severity**: Minor | **Confidence**: 4.

### W6: Terminology and framing around "bought"
**Problem**: "Group-level" is defined as constant within an object-pair cell, but the text frames it as "not earned at the level of individual cases" and elsewhere says "Group-level is not a lesser gain". Readers from the unbiased-SGG community will read the title as a verdict that TDE-style gains are cosmetic. The "case-level" part of a thresholded metric also includes "existing discrimination spent at a new operating point" (Sec. 5), so neither part is labelled by what it means in SGG terms (predicate prior vs visual evidence).
**Evidence Anchor**: text: Sec. 5 "Group-level is not a lesser gain"; text: Intro "What did those ten points buy?".
**Suggestion**: Use SGG terms in the abstract: "pair-conditional predicate-prior shift" vs "within-pair discrimination". Add a short statement of which is desirable for which downstream use (captioning/VQA vs retrieval).
**Severity**: Minor | **Confidence**: 4.

### W7: Single released checkpoints and cross-recipe comparisons limit what can be said per method
**Problem**: One TDE run, one DLFE pair, IETrans+Rwt vs a separately trained baseline (disclosed). Method-level claims in the abstract ("IETrans ... 97% group-level, and its within-pair ranking falls") are stated as properties of the method although the comparison also differs in loss (Rwt) and training data.
**Evidence Anchor**: text: Sec. 5 "this compares two separately trained models and does not isolate the effect of relabelling"; absence: Abstract — expected the same caveat for IETrans; checked Abstract, Intro contributions, Conclusion.
**Suggestion**: Carry the caveat into the abstract and conclusion; if feasible, train IETrans with Rwt but without relabelling on the same MOTIFS-SUM recipe, or drop the IETrans mechanism claim.
**Severity**: Minor | **Confidence**: 5.

## Missing References (all marked where unverified)
- Jung, Kim, Kim, Cho, "Devil's on the Edges: Selective Quad Attention for Scene Graph Generation", CVPR 2023 (arXiv 2304.03495; verified to exist via web search). Recent SGG baseline with mR gains; candidate for the audit or at least for related work.
- Sudhakaran et al., "Vision Relation Transformer for Unbiased Scene Graph Generation", ICCV 2023 (verified to exist via search; authors list not checked in full).
- A 2025 paper on a causal/per-triplet adjustment module, arXiv 2503.17862 (found via search; title "A Causal Adjustment Module for Debiasing Scene Graph Generation"); it reports that vanilla logit adjustment has almost no effect, which would contradict this paper's LA result and should be discussed. Content not read in full; treat the specific claim as [UNVERIFIED].
- Open-vocabulary / VLM-based SGG beyond [24] (e.g., work from the Lin/Li et al. groups on open-vocabulary SGG and predicate debiasing with VLMs, arXiv 2403.16184 appeared in my search) [UNVERIFIED as to relevance].
- [UNVERIFIED search lead] Multi-label or hierarchical predicate evaluation for VG (e.g., work on predicate ambiguity and "scene graph evaluation with predicate hierarchies"), relevant to W2.
- [UNVERIFIED search lead] SGG evaluation critiques (triplet-level/PairNet-style recall, "SGG metric" papers beyond [25]).

## Detailed Comments
- **Literature review**: Related work is organised by theme and cites the main unbiased-SGG families to 2023; the statement that prior correction rivals debiasing is properly attributed to [6, 43]. Coverage after 2023 is absent.
- **Framework**: The Yates covariance lineage and its relation to proper-score reliability/resolution is well positioned; domain-wise, positioning relative to prior-correction explanations of TDE (Structured Sparse R-CNN notes TDE/TE resemble logit adjustment but lack the temperature) is fair, though this paper's "to first order TDE is a learned logit adjustment of the context branch" should cite that remark explicitly.
- **Argument accuracy**: Numerics reproduce. One interpretive stretch: "TDE ranks the relations as the baseline did" rests on a TOST-style bound (0.0034 relation-weighted, 0.0077 comparison-weighted); the authors correctly report the wider comparison-weighted bound.
- **Contribution**: Primarily methodological/diagnostic, with a bounded empirical finding for MOTIFS-family PredCls at K=50. Incremental-to-solid; novelty over the "prior correction rivals debiasing" knowledge is the exactness and the inference tooling.
- **Overclaiming risk**: moderate (W1, W3, W6).

## Questions for Authors
1. With the graph constraint removed, LA1 reaches ng-mR@50 .4173 against TDE .2981. Does your decomposition change which method you would call the better debiaser, and why is the constrained K=50 cell treated as primary?
2. How do the AUC conclusions change on a synonym-merged or hierarchy-aware label set, in particular for IETrans? Which merge scheme was used in Appendix Q.2?
3. Can you audit one non-prior-correcting, post-2022 method with a released PredCls checkpoint, or state why none is feasible?
4. What is the share when the cell is the class pair plus box-geometry bins, i.e., the finest conditioning of the best visual-free predictor, and is that what you would propose for a leaderboard?
5. In SGCls/SGDet, how would the 58% matched-pair selection bias the group-level share?

## Minor Issues
- Intro and abstract mix micro-pooled and official statistics (.0972 vs .1017; R@50 cost .0175/.2023 from official vs .0161/.2183 micro); give one consistent convention per sentence.
- State PredCls in the title or first sentence of the abstract.
- Table 1 caption is long and crowded; Fig. 3's predicate labels overlap the legend.
- Cite the observation that TDE resembles logit adjustment without temperature where [43] is invoked.

## Criterion-Bound Judgements
Calibration status: `NOT_CALIBRATED`
| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | Reviewer configuration (domain contribution) | MEETS | text: Contributions (i)-(iii) | Exact paired-gain decomposition applied to SGG is new in framing; prior-correction finding partly known | Statistical novelty is Reviewer 1's remit | no |
| Evidence sufficiency (SGG scope) | Reviewer configuration | PARTLY_MEETS | W1, W3, W5 | Numbers reproduce; scope is one family/mode/cell | Only released checkpoints | yes (repairable by scoping or extra audit) |
| Argument coherence | Reviewer configuration | PARTLY_MEETS | W2, W4, W6 | Interpretation of "case-level" depends on single-label annotation and chosen cells | none identified | yes |
| Literature integration | Reviewer configuration | PARTLY_MEETS | absence: references after 2023 | SGG literature stops at 2023 citations of 2022-era methods | Some leads UNVERIFIED | no |
| Significance & impact | Reviewer configuration | MEETS | S2, S4 | Practical guidance on reporting mR@K is valuable | Depends on adoption | no |
