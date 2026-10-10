# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 Submission #***** (anonymous), paper.pdf (8 pages + references) and supp.pdf (36 pages)
- **Review Date**: 2026-10-10 (submission deadline context: 16 Nov 2026)
- **Review Round**: Round 1, simulated panel, full mode
- **Repository state read**: commit 9dad949 (code, results/*.json, cached outputs; no history read)

## Reviewer Information

### Reviewer Role
Peer Reviewer 3 (Perspective)

### Reviewer Identity
ML evaluation scientist from outside scene graph generation (SGG). Working areas: long-tail recognition, VQA answer-prior bias, shortcut learning, grouping loss and calibration, label shift and distribution shift. I do not know the SGG method literature beyond what the paper cites, and I have not re-run the released checkpoints. Where SGG conventions differ from my field's, I say so.

### Review Focus
Whether the group-level / case-level split supports the interpretations the paper puts on it (what a "case-level" gain is, what a "group-level" gain is worth, what "no change in ranking" means), how far the conclusions travel under shift in label mix, calibration, operating point and grouping, and whether the recommended reporting practice is usable by a benchmark.

### Calibration Status
`NOT_CALIBRATED`

No author-confirmed target context was supplied.

criteria_binding_unavailable

I make no venue-alignment claim.

---

## Overall Assessment

### Recommendation
**Major Revision** (borderline: the exact accounting and the operating-point control are real contributions, but several headline interpretations are stated more firmly than the evidence in the paper's own appendices allows).

### Confidence Score
4. Evaluation methodology, shortcut and label-shift reasoning are within my expertise. SGG specifics (VG150 annotation practice, the TDE and IETrans codebases) and the U-statistic theory are partly outside it. Confidence is a scope disclosure only.

### Summary Assessment
The paper gives an exact additive split of the gain between two frozen models into a part that survives within-group label transport (group-level) and a within-group covariance (case-level). It applies the split to two released debiasing checkpoints. On TDE it finds that 87% of the mean-recall gain is group-level, and that a ranking-preserving logit adjustment reproduces the gain at a small cost in R@50. I recomputed the headline arithmetic from results/*.json and it matches. The operating-point control is the best idea in the paper: it separates "a thresholded metric moved" from "the model learned something". The authors also disclose unusually many weaknesses of their own estimator.

My concerns are about interpretation. The case-level part credits any within-cell signal, shortcuts included, and depends on the declared grouping, the confidence protocol, the operating point and the label mix. The central claim that TDE leaves within-pair ranking unchanged rests on an invariant test whose power is weak under one weighting and nil under the label mix that mean recall targets. The CLIP study treats the same AUC evidence in opposite ways for TDE and CLIP. The abstract's IETrans sentence ("under every measure") is not what the tables show. The recommended reporting protocol returns contradictory signs and offers no rule for resolving them. I would accept a version that scopes the claims to what the tables support.

---

## Criterion-Bound Judgements

Criterion source for every row: reviewer configuration for Peer Reviewer 3 (no external criteria supplied; `criteria_binding_unavailable`). Judgements are not totalled or mapped to the recommendation.

| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Assumption soundness (what a case-level gain means) | reviewer configuration | PARTLY_MEETS | text: Sec. 1 "any signal varying inside a pair, including a shortcut nobody recorded"; table: Supp. Table 3 robustness value 0.061 | Authors state the shortcut caveat and show the sensitivity bound is unreassuring; headline readings still treat case-level as "new discrimination". | I did not re-derive the bound. | yes: affects W2 |
| Robustness to label, calibration and operating-point shift | reviewer configuration | PARTLY_MEETS | table: Supp. Tables 28, 29, 32; text: Sec. 5 "case-level part depends on the protocol" | Group-level parts flip sign in 7 of 8 comparisons; TDE case-level sign differs across protocols. Reported honestly, but conclusions are not stated conditionally. | The label-shift path is a sensitivity analysis under a fixed P(X given Y, C), not real shift data. | yes: W1, W4 |
| Evidence for "no ranking change" claims | reviewer configuration | PARTLY_MEETS | table: Table 1 ΔAUC columns; table: Supp. Table 29 uniform-end AUC CI [-.0684, +.0082] | Null claims without a power statement or equivalence margin. | Relation-weighted AUC is tight; comparison-weighted and uniform-mix AUC are not. | yes: W1 |
| Generality beyond the audited checkpoints | reviewer configuration | PARTLY_MEETS | text: Sec. 5 "this compares two separately trained models"; table: Supp. Table 11 seed spread | Two checkpoints, single seeds, one benchmark. | Cannot assess unreleased methods. | yes: W4 |
| Practical usability for benchmarks | reviewer configuration | PARTLY_MEETS | text: Sec. 7 "both signed parts with intervals under both matching protocols"; text: Supp. App. K "we do not have a procedure that resolves it" | Reporting list is long, requires full softmax scores and a declared grouping, and has no rule for contradictory outputs. | Adoption is a judgement about future behaviour. | yes: W5 |
| Soundness of the exact decomposition and replay | reviewer configuration | MEETS | table: Supp. Table 16 (replay matches official to 4 d.p.); text: Sec. 4 "rejects in 0.030 of 200 datasets at level 0.05" | The algebra is exact and my additivity recomputation passed on every table I checked. | Proofs not independently verified (Reviewer 1 remit). | no: informs strengths |

---

## Recomputation Log

Read-only Python over results/*.json plus arithmetic on the numbers printed in the paper and supplement. Scratch work outside the repository.

| # | Claim | Recomputation | Result |
|---|---|---|---|
| R1 | "87% of the mean-recall gain (83-91%) is group-level" | results/sgg_share_intervals.json: share 0.8657, CI [0.8256, 0.9058]; 0.0841/0.0972 | Reproduced |
| R2 | LA control "under a tenth of TDE's cost in R@50 (0.0175 against 0.2023)" | 0.6612-0.6437 = 0.0175; 0.6612-0.4588 = 0.2024; ratio 0.086 | Reproduced (0.2024 vs printed 0.2023, rounding) |
| R3 | F@50 0.344 (LA) vs 0.322 (TDE) | 2RM/(R+M): 0.3436 and 0.3216 | Reproduced |
| R4 | "nine of the ten points" | Official-metric gains: TDE 0.2476-0.1459 = 0.1017; LA 0.2343-0.1459 = 0.0884 (87%). Pooled: 0.0941/0.0972 (97%) | Holds, but the ten points are an official-metric number and the 87% group share is for the pooled micro-average (0.0972, not 0.1017) |
| R5 | Additivity ΔT = ΔP + ΔR | Supp. Tables 7, 8, 20 (TDE matched), 24 (IETrans), 35 (Waterbirds), CIFAR Table 12 and the main text numbers | All sum within rounding |
| R6 | "Seven of eight group-level parts change sign" under uniform label mix (Table 28) | Compared signs row by row | Reproduced (class-vs-FREQ shrinks from -0.01432 to -0.00241) |
| R7 | CLIP beats geometry "by +0.02981" at the uniform end | 0.02365 + 0.00615 | Reproduced |
| R8 | TDE matched quadratic case-level over 20 halves in [-0.00131, +0.00059], interval excludes zero in 3 | results/sgg_split_robustness.json | Reproduced; the three are negative; three halves have positive point estimates with CI covering zero |
| R9 | TDE vs LA1 case-level part, mR across six protocol/k cells (Supp. Table 17) | +.0013, **-.0008**, +.0034, +.0013, +.0072, +.0148 | 5 of 6 point estimates positive; ng-mR@100 interval excludes zero. The headline -0.0008 is the only negative cell |
| R10 | IETrans "loses within-pair discrimination under every measure" | Table 1 and Supp. Tables 24, 28, 30: mR case +.0060 [-.0031,+.0151]; AUC comparison -.0093 [-.0181,+.0004]; audit-half comparison -.0114 [-.0272,+.0020]; uniform-mix AUC +.0082 [-.0471,+.0607]; relation-weighted AUC -.0235 [-.0275,-.0182]; matched proper score negative | Not "every measure": two are significantly negative (relation-weighted AUC, matched proper score); others null or positive in sign |
| R11 | Abstract: in SGCls "TDE's ranking within pairs gets worse" | Supp. Table 34: relation-weighted -.0128 [-.0171,-.0074]; comparison-weighted -.0047 [-.0122,+.0031] | True under one weighting only |
| R12 | Robustness value ρ† = 0.06127 (Supp. Eq. 27, Table 3) | 0.01427/0.23284 = 0.06129; but Table 3 lists ΔR = 0.01439 (0.01439/0.23284 = 0.0618). results/sensitivity_bound.json holds 0.014267 | Numerically consistent with the JSON; Table 3 and Eq. 27 use two slightly different ΔR values (immaterial, flag for tidiness) |
| R13 | Power of TDE's AUC null | Comparison-weighted upper bound +0.0086 is 27% of the geometry-vs-class AUC gain (+0.0323); relation-weighted upper bound +0.0018 is 3% of +0.0626 | Weighting changes the conclusion: informative under relation weighting, weak under comparison weighting |
| R14 | CIFAR-100-LT Table 11 means and SDs | CB -0.25108 (0.01124), DRW +0.01953 (0.01188), LA +0.03241 (0.00498) | Reproduced |
| R15 | AUC share carried by the largest cell | Supp. Q.4: 27% of comparison weight in one cell, 2.5% of relations | Taken from text; not independently re-derived |

Not recomputed: the U-statistic variance, the proofs, the coverage simulations, the released-checkpoint replays (cached logits not examined), anything under experiments/ beyond reading the results files.

---

## Strengths

1. **S1: Operating-point control arm (logit adjustment) turns an ambiguous remainder into a testable one.** A thresholded metric earns case-level credit when its operating point moves. The paper builds a control with identical within-cell ranking that reproduces TDE's gain and its split. This is the right structure for evaluation claims in long-tail work, where "prior correction" is the null that most debiasing results should beat. 
   **Evidence Anchor**: table: Table 1, LA row — ∆mR +.0941, group +.0802, case +.0139 against TDE +.0972, +.0841, +.0130

2. **S2: Validation in settings with known truth, including the failure modes.** The simulation checks the null (rejects in 0.030 of 200 datasets at level 0.05), the injected shortcut is credited to the case-level part, and a calibration-only change produces a spurious -0.488 that the matching protocol removes. Reporting that a class-wise offset survives temperature matching (+0.0106) is the kind of negative result evaluation papers usually omit. 
   **Evidence Anchor**: text: Sec. 4 "rejects in 0.030 of 200 datasets at level 0.05"

3. **S3: Candid scope disclosure.** The paper says the split is conditional on the grouping, credits shortcuts, is not invariant to calibration, operating point or label mix, and that its own sensitivity bound is not reassuring. Supp. Appendix K gives a four-case example where two equally fine partitions disagree completely. This lets a reader locate the problems in W1 to W3 without extra work. 
   **Evidence Anchor**: text: Sec. 7 "our own bound on that exposure is not reassuring"

4. **S4: Paired design on identical weights and an exactly replayed evaluator.** TDE and its baseline come from one set of weights and share object predictions; the offline evaluator reproduces official R@50 and mR@50 to four decimals. That removes most implementation confounds from the TDE comparison. 
   **Evidence Anchor**: table: Supp. Table 16 — base and TDE official versus re-scored rows identical (0.6612/0.1459 and 0.4588/0.2476)

5. **S5: Label-shift path analysis shows which gains an evaluation-mix change can reverse.** The group-level part flips sign in 7 of 8 comparisons when predicates are reweighted to uniform within pairs, and the CLIP head goes from last to first in total score, while most case-level parts keep their sign. For readers from the distribution-shift literature this is the most transferable use of the split. 
   **Evidence Anchor**: table: Supp. Table 28 — CLIP vs geometry group -0.04705 to +0.02365, case +0.00464 to +0.00615

---

## Weaknesses (ranked by decision impact)

1. **W1: The "TDE leaves within-pair ranking unchanged" conclusion is a null without a power statement, and the evidence is weighting-, k-, protocol- and mix-dependent.** The abstract and conclusion state it as the outcome ("as far as we can detect"; "no measure detects a change"). Three issues. (a) The within-cell AUC is the only invariant test, yet its comparison-weighted version is dominated by one cell (27% of the weight, 2.5% of relations); TDE's comparison-weighted change is +.0026 [-.0028,+.0086] and relation-weighted -.0015 [-.0036,+.0018]. The comparison-weighted upper bound is about a quarter of the AUC gain geometry features bring (R13), so "unchanged" is not established under that weighting. (b) At the uniform within-pair mix, which is the weighting mean recall itself applies, TDE's AUC interval is [-.0684,+.0082] (uninformative), while the proper-score case-level part against the LA control is +0.00723 [+0.00436,+0.01011] and the authors' own reading is that TDE gains discrimination between some predicate pairs and loses it between others. (c) Across the six mR protocol/k cells TDE-minus-LA1 case-level is positive in five (R9); the -0.0008 shown in Table 1 is the one negative cell. None of this contradicts the 87% group-level share, which is exact. It does mean "no change in ranking" is a statement about power at one mix, not a property of TDE. 
   - **Why it matters**: this is the paper's mechanistic claim about TDE, and a reader will quote it.
   - **Suggestion**: (i) declare an equivalence margin in AUC units, anchored to a reference effect (for example the geometry-vs-class gain in the same cells), and report TOST-style bounds or minimum detectable effects under both weightings and at the uniform end; (ii) put all six mR cells for TDE-vs-LA1 in the main table; (iii) add an evaluation in which both models receive the same validation-fitted per-class offset before recall is computed, so the thresholded metric is compared at matched operating points rather than against a single untuned tau = 1 control; (iv) soften the abstract to "no change detected at the benchmark's mix, with the bounds given".
   - **Severity**: Major | **Evidence Anchor**: text: Sec. 5 "No measure we tried detects a change in within-cell ranking" | **Confidence**: 4 — core expertise: distribution-shift evaluation and equivalence reasoning

2. **W2: What the case-level part measures is narrower than how it is read, and the headline split is reported for one grouping chosen by the authors.** The paper acknowledges that the case-level part credits any signal varying inside a pair, shortcuts included, and that its own sensitivity bound would let a covariate with correlation 0.061 explain the whole VG estimate. The headline reading remains "new discrimination" (Sec. 5, "bought with discrimination the baseline had") and "pixels buy case-level gain" (Sec. 6). Separately, the SGG grouping is the object-class pair, which is exactly the index of the MOTIFS frequency prior that TDE's counterfactual subtracts; for TDE a near-pure group-level result is close to guaranteed by construction (Supp. Table 22: the averaged-context term is 99.96% one shared vector). Supp. Table 20 shows subject-only grouping moves TDE's raw case-level part from -0.0136 to -0.217, and Appendix K says the paper has no procedure for choosing among equally fine partitions. "Declared before the audit" cannot be checked for an audit run by the authors after seeing the benchmark's construction. The contribution list also says the split "separates calibration, prior and shortcut effects", whereas Sec. 4 shows a shortcut is credited as case-level. 
   - **Why it matters**: for shortcut-prone benchmarks the case-level part cannot separate learned visual evidence from, say, annotator-style or scene-context regularities. The 87% figure is a statement about this ϕ.
   - **Suggestion**: (i) report the headline split on a nested family of groupings (class pair; class pair crossed with coarse box-overlap/size bins; class pair crossed with an image-scene cluster) and say which conclusions survive; (ii) report within-cell label heterogeneity beside every ϕ, as Appendix K itself recommends; (iii) rewrite the shortcut clause in the contributions; (iv) state in the main text that "case-level" means "within-ϕ covariance", not "visual".
   - **Severity**: Major | **Evidence Anchor**: text: Sec. 1 "any signal varying inside a pair, including a shortcut nobody recorded" | **Confidence**: 4 — core expertise: shortcut learning and grouping loss

3. **W3: The CLIP study applies the AUC evidence asymmetrically, and its title claim conflicts with the paper's own invariant diagnostic.** Section 6 is titled "The model every metric ranks last" and concludes that the CLIP head's advantage is "real covariance, not better ranking". The evidence for "not better ranking" is top-1, MRR and recall@5 after prior matching (all operating-point-sensitive in the paper's own framework) and an AUC difference of +0.0085 [-0.0062,+0.0214]. The within-cell AUC by comparison favours CLIP in all five seeds (+.0085, +.0092, +.0093, +.0156, +.0048; Supp. Table 25) and, on the audit half, with an interval excluding zero (+.0214 [+.0001,+.0435]); by relation weighting it favours geometry. So the invariant diagnostics do not rank CLIP last; they disagree with each other. TDE's +.0026 is read as "no change" while CLIP's +.0085 is read as "not better". Further, the CLIP head's group-level deficit has an untested explanation (1024 CLIP dimensions against 64 class-embedding dimensions, offered as a hypothesis), and the combined CLIP-plus-geometry head also loses at group level, so the "case-level gain with group-level loss" pattern may reflect head capacity and subsampling to 100k relations rather than pixels. "Real pixels" also conflates object appearance with scene context inside the crops. 
   - **Why it matters**: this is the paper's demonstration that the split "disagrees" with aggregates in a useful direction; if the disagreement is a training artefact the demonstration weakens.
   - **Suggestion**: (i) pre-declare one ranking criterion and apply it to TDE and CLIP alike; (ii) run an ablation that equalises the input dimensions (PCA of CLIP to 64 d, or a width-matched class embedding); (iii) add a context-ablated crop control (masked background, or a crop from a different relation's box in the same image) so pixel evidence is separated from scene context; (iv) retitle Sec. 6 or qualify it ("by the aggregate measures").
   - **Severity**: Major | **Evidence Anchor**: text: Sec. 6 "real covariance, not better ranking" | **Confidence**: 4 — core expertise: shortcut and spurious-feature evaluation

4. **W4: Method-level wording outruns two single-seed checkpoints, and the IETrans sentence in the abstract is not supported by the tables.** The abstract says IETrans "loses within-pair discrimination under every measure", and Sec. 5 repeats it. In the paper's own tables the mean-recall case-level part for IETrans is positive in point estimate (+.0060), the comparison-weighted AUC interval and the audit-half interval cover zero, and the AUC change at the uniform mix is +.0082; only the relation-weighted AUC and the matched proper scores are significantly negative (R10). The comparison is also against a separately trained baseline with a different visual-term fusion, as the authors say, so the loss cannot be attributed to relabelling. The SGCls statement "TDE's ranking within pairs gets worse" holds only under relation weighting (R11). More broadly, the audits cover two released checkpoints, each from one training run, and the supplement itself shows seed-to-seed magnitude can vary about fourfold (CIFAR DRW, +0.007 to +0.031). The title and abstract speak about "debiasing methods for scene graph generation". 
   - **Why it matters**: a reader will carry "TDE and IETrans are group-level; IETrans loses discrimination" into the literature.
   - **Suggestion**: restate IETrans as "matched proper scores and relation-weighted AUC decrease; mean-recall case-level and comparison-weighted AUC are not distinguishable from zero; baseline differs"; qualify SGCls similarly; scope the title or abstract to "two released checkpoints", or add at least one further method where the authors can retrain with several seeds (for example a training-time re-weighting method with its own plain baseline), which would also isolate method effects from baseline mismatch.
   - **Severity**: Major | **Evidence Anchor**: table: Table 1 — IETrans row, case-level +.0060 [-.0031,+.0151], ∆AUCc -.0093 [-.0181,+.0004] | **Confidence**: 4 — core expertise: reading claim-versus-table consistency in long-tail debiasing audits

5. **W5: The recommended reporting protocol has no decision rule when its own outputs disagree, and the grouping can be chosen to favour a result.** The conclusion asks benchmarks to report the declared grouping, both signed parts under both matching protocols, the AUC under both weightings, the parts along a label-mix path and an operating-point control. On the paper's own data these outputs conflict: TDE's matched quadratic case-level part is -0.0184 (shared temperature), -0.00006 (per-model temperature) and +0.00445 (temperature plus class bias); the log-score part is +0.044 and -0.093 under the first two; the two AUC weightings differ in sign for TDE and for CLIP-vs-geometry. A leaderboard row that carries conflicting signs does not tell a user whether to prefer a method. Because the grouping is a modelling decision and equally fine partitions can disagree entirely (Appendix K), an author can select the partition that suits the claim. The method also needs full probability vectors, which most benchmarks do not archive (acknowledged), and the temperature fit uses half of the test images because released checkpoints ship no validation outputs. 
   - **Why it matters**: the paper's practical contribution is the reporting suggestion, and a suggestion without an adjudication rule invites cherry-picking.
   - **Suggestion**: propose a minimal reporting set with a stated hierarchy (for example: ϕ and its label heterogeneity fixed by the benchmark organisers; the operating-point-matched comparison as primary; AUC under both weightings with equivalence bounds as the invariant check; the other parts as appendix diagnostics) and show it applied to the TDE and IETrans rows, with an explicit statement of which verdicts it supports. Describe how a benchmark would register ϕ in advance.
   - **Severity**: Major | **Evidence Anchor**: text: Sec. 7 "both signed parts with intervals under both matching protocols" | **Confidence**: 3 — adjacent field: benchmark governance, applying general evaluation practice

6. **W6: The framing treats group-level gain as the lesser achievement without arguing the normative case.** "What did those ten points buy?" and "two achievements summed" imply that moving probability within a pair is less valuable than discriminating individual relations. Mean recall, however, is itself a reweighting of the test labels towards a uniform predicate mix (weight 1/(K n_y)), and in the long-tail and label-shift literature correcting the train-to-test prior is the intended effect, not an artefact. The authors say in the supplement that "a transported gain is a description of where score was earned, not an accusation", but the main text does not carry that nuance and offers no evidence on whether the group-level change helps a downstream user (for example the more specific predicate "parked on" for (car, street) in Fig. 3). The paper also does not distinguish the case where the benchmark's test labels reflect annotator habit from the case where they reflect scene content. 
   - **Why it matters**: the reader's takeaway ("TDE bought nothing real") depends on a value judgement that the exact split does not itself license.
   - **Suggestion**: state in the introduction which part a benchmark should reward and why, separate "metric is gameable by prior shift" (a claim the paper supports) from "the gain has no worth" (a claim it does not), and, if possible, add one downstream measure of predicate specificity.
   - **Severity**: Minor | **Evidence Anchor**: text: Sec. 1 "What did those ten points buy?" | **Confidence**: 3 — adjacent field: label-shift and long-tail evaluation norms

7. **W7: The "ten points" and the headline shares are protocol-specific and are decomposed on a different object than the leaderboard metric.** TDE's mean recall rises 10.17 points under the graph constraint and falls from 0.3260 to 0.2981 without it (Table 16), so the premise is one of two official protocols; the abstract does not say so. The split is of micro-averaged recall (+0.0972) while the official per-image average rises 0.1017; the paper notes "it tracks the official per-image average but is not it", so the 87% share is not a statement about the official metric. 
   - **Why it matters**: smaller than W1 to W5, but readers will quote "87% of ten points".
   - **Suggestion**: put the protocol and the micro/official distinction in the abstract or the first paragraph of Sec. 5, and give the no-graph-constraint split next to Table 1.
   - **Severity**: Minor | **Evidence Anchor**: text: Sec. 5 "mean recall falls, from 0.3260 to 0.2981" | **Confidence**: 4 — core expertise: metric protocol sensitivity

8. **W8: The long-tailed classification and text studies use a label-derived grouping and so are not instances of the construct the main text defines.** The main text defines the cell as a discrete feature "both observe"; the supplement states that for CIFAR-100-LT "a superclass is a function of the label, not of the input", and the same holds for the 20 Newsgroups topics. Under such a grouping the statement that logit adjustment "changes no ranking within any group" no longer holds (LA reads as covariance in Supp. Table 11), and the text study has one trained pair per schedule. Sec. 6's closing paragraph presents these as applying the same estimator "beyond scene graphs". 
   - **Why it matters**: an outsider reading Sec. 6 may take the other domains as replications.
   - **Suggestion**: label them as demonstrations under a different estimand in the main text, and report which statements of Sec. 3 and Sec. 5 do not transfer.
   - **Severity**: Minor | **Evidence Anchor**: text: Supp. App. N.5 "a superclass is a function of the label, not of the input" | **Confidence**: 4 — core expertise: long-tail classification benchmarks

---

## Detailed Comments

### Assumption Audit
- **Explicit assumptions**: The grouping is declared in advance; cells are label-heterogeneous enough to identify a within-cell counterfactual; images are independent clusters; confidence is matched by a temperature (and optionally a per-class bias) fitted on held-out images. The paper checks several of these in simulation. The "declared in advance" assumption cannot be verified for an author-run audit.
- **Implicit assumptions**: (i) that within-pair signal is the thing a better model should add (it may also be annotator style or scene context); (ii) that VG test labels are an unbiased reference for "which relation carries which predicate" (many near-synonymous predicates; the merging study in Supp. Q.2 helps but does not answer this); (iii) that fitting a temperature on half the test images does not perturb the audited half's verdict (the 20-halves study supports this for TDE under one protocol only); (iv) that label shift acts with P(X given Y, C) fixed, which is the weakest assumption in the path analysis because real train-test differences in VG also change what the predicate looks like.
- **Paradigmatic assumptions**: the paper assumes a benchmark's job is to attribute a scalar gain to a route. A distribution-shift evaluator would ask instead for performance under a family of test mixes (worst-group or mix-robust reporting), and would treat "which part of the gain is prior" as one summary of that family. The label-mix path in Supp. Table 29 is the closest the paper gets, and it is where the TDE conclusion changes.

### Cross-Disciplinary Connections
- **Parallel research**: Long-tail recognition has asked this question in a different form: decoupling the representation from the classifier prior, and evaluating after classifier re-adjustment (Kang et al., "Decoupling representation and classifier for long-tailed recognition", ICLR 2020 [UNVERIFIED: recalled from memory, not checked in this session]). The result that a cheap prior correction rivals a trained debiasing method has an analogue in last-layer retraining for spurious correlations (Kirichenko, Izmailov and Wilson, ICLR 2023 [UNVERIFIED]). Effective robustness (Taori et al., NeurIPS 2020; Miller et al., "Accuracy on the line", ICML 2021 [UNVERIFIED]) compares a model to the trend of baselines, which is a different way to say "gain beyond the expected prior-shift route".
- **Borrowing opportunities**: the group-level / case-level accounting resembles the Kitagawa and Oaxaca-Blinder decompositions of an outcome gap into composition and structure terms (Blinder 1973; Oaxaca 1973 [UNVERIFIED]); the economics literature has long worked on the non-uniqueness and path-dependence the authors meet in Appendix K and in Supp. Table 21 (order-dependent attribution). Naming this lineage would help readers outside SGG and may supply tools for the choice-of-reference problem.
- **Methodological borrowing**: equivalence testing (two one-sided tests, Schuirmann 1987 [UNVERIFIED]) for the "no change in ranking" claims; an "oracle-offset" evaluation in which each model's per-class bias is fitted on validation data before recall is computed, which directly yields the representation-versus-prior comparison without the covariance machinery.

### Practical Impact
- **Real-world application**: A benchmark maintainer can immediately use the logit-adjustment control and the within-cell AUC; those are cheap and robust. The proper-score covariance requires full score vectors and a protocol that, on this paper's data, returns conflicting signs.
- **Implementation feasibility**: requires patching released code to dump all logits (the authors did so); most leaderboards archive top-k only. The 81.5% coverage in all-two-case cells means finer groupings need a different variance.
- **Stakeholders**: benchmark organisers (who must own ϕ), authors of debiasing methods (who face a new axis that is protocol-sensitive), and downstream users of scene graphs, whose interest in predicate specificity is not measured.

### Broader Implications
- **Ethical dimensions**: none specific. The Waterbirds audit suggests use on fairness interventions where cells are demographic groups; the same caveats on grouping choice would apply and should be stated before such use.
- **Social impact**: low. The main risk is that a reported split is taken as a verdict on a method's worth.
- **Future directions**: nested groupings; seeded retrains of one training-time debiasing method with its plain baseline; a downstream specificity measure; an equivalence-style reporting card.

---

## Cross-Disciplinary Reading Recommendations

All entries below are search leads from my own recollection, not verified in this session.

- Kang et al., Decoupling representation and classifier for long-tailed recognition, ICLR 2020 [UNVERIFIED]. Relevance: separates classifier prior from representation, the same two routes the paper tries to split.
- Kirichenko, Izmailov, Wilson, Last layer re-training is sufficient for robustness to spurious correlations, ICLR 2023 [UNVERIFIED]. Relevance: a cheap post-hoc fix matching a trained method; protocol for such controls.
- Taori et al., Measuring robustness to natural distribution shifts in image classification, NeurIPS 2020; Miller et al., Accuracy on the line, ICML 2021 [UNVERIFIED]. Relevance: comparing a model to the baseline trend as a way to define "gain beyond the expected route".
- Blinder 1973 and Oaxaca 1973 on wage-gap decomposition [UNVERIFIED]. Relevance: composition versus structure accounting and its path dependence.
- Schuirmann 1987, two one-sided tests for equivalence [UNVERIFIED]. Relevance: formalises "no change detected" claims.

---

## Questions for Authors

1. For TDE against the LA control, which AUC change can the data exclude under each weighting and at the uniform mix, stated as a fraction of the geometry-versus-class AUC gain? If the authors had to state a margin before looking, what would it be?
2. If both TDE and the baseline were given the same validation-fitted per-class offset before recall is computed, how much of TDE's mR@50 advantage remains? Is the untuned tau = 1 control the best prior-only competitor?
3. Why are the six TDE-vs-LA1 mR cells (Supp. Table 17) not shown in the main paper, given five of six are positive? Would the headline "-0.0008" read the same with all six?
4. For the CLIP study, does the case-level advantage survive when CLIP features are reduced to the class-embedding dimensionality and when crops are context-masked? Which single ranking criterion would the authors have named before the experiment, and what does it say for both CLIP and TDE?
5. What does the headline 87% become when the grouping is the class pair crossed with a coarse box-size or overlap bin?
6. Would the authors support a version of the abstract that states the checkpoints, the protocol (graph-constrained, micro-averaged) and the weighting each AUC claim refers to?

---

## Minor Issues

### Language / Grammar
- Abstract and Sec. 1 pack many numbers into long sentences; the "What is not claimed" paragraph in Sec. 1 is useful but dense, and an outsider cannot follow the AUC weighting and per-class-bias matching without the supplement.
- "Nine of the ten points" is 8.84 of 10.17 on the official metric and 9.41 of 9.72 pooled; say which.

### Citation Format
- Reference [34] (Sagawa et al.) has no page back-reference in the bibliography, unlike the others; check the back-reference list.
- The decomposition's relation to the economics literature on gap decompositions is not mentioned.

### Figures and Tables
- Figure 2(b): the TDE and CLIP rows are very small against the geometry row; consider a separate scale or numeric labels.
- Table 1 mixes pooled and per-image quantities and has two AUC columns with different weightings; a footnote with the weights' share of cells would help (the largest cell carries 27% of comparison weight).
- Supp. Table 3 lists ΔR = 0.01439 while Eq. (27) uses 0.01427; harmonise (R12).
- Supp. Table 6 accuracies (0.6564, 0.6545, 0.6554, 0.6639, 0.6674) are for the reconstructed split and are easy to confuse with the 0.6981 baseline accuracy on the canonical split; label the split in the caption.

### Layout
- The main paper depends on the supplement for protocol definitions that determine its conclusions (matching families, weightings, the control); move a one-line definition of each into the main text.
- Pooling many protocol variants on one test set without adjustment is stated, but a short table of "which verdicts survive which variant" in the main text would reduce forking-path concerns.
