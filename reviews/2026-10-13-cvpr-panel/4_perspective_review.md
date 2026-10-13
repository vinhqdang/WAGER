# Peer Review Report: Perspective Seat (Peer Reviewer 3)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 Submission #***** (anonymous)
- **Review Date**: 2026-10-13
- **Review Round**: 1 (simulated panel, mode full)
- **Repository state**: commit 18a72c9; paper.pdf (8 pp + refs), supp.pdf (36 pp)

## Reviewer Information
### Reviewer Role
Peer Reviewer 3 (Perspective)

### Reviewer Identity
ML evaluation scientist from outside scene graph generation (SGG): long-tail recognition, VQA answer-prior bias, shortcut learning, grouping loss, label/distribution shift. I do not know the SGG literature beyond what the paper cites. I do not judge the proofs or the statistical-inference machinery (other seats do); I judge what the decomposition licenses, how it behaves under distribution shift, and what practitioners can do with it.

### Review Focus
Whether the headline interpretation ("87% of TDE's gain is group-level, i.e. prior-like, not discrimination") survives the change of label mix, grouping choice and calibration protocol that an evaluation scientist would apply. Also whether the transfer to other long-tail and shortcut settings is established, and whether the proposed reporting standard is feasible.

### Calibration Status
`NOT_CALIBRATED`. Final panel topology is unknown to this seat. No candidate profile is applied.

### Criteria binding
`criteria_binding_unavailable`. No venue-criteria binding manifest was supplied, so I make no venue-alignment claim.

---

## Overall Assessment

### Recommendation
**Major Revision** (borderline; I would move to Minor/Accept if the framing in the abstract and Sec. 7 is brought in line with the label-mix and weighting results the supplement already contains).

### Confidence Score
3 of 5. The evaluation-methodology and distribution-shift issues are my core expertise. I am outside SGG, and I did not audit the proofs or the checkpoint replay (I recomputed only what the stored result JSONs allow).

### Summary Assessment
The paper gives an exact, model-free accounting of a paired score gain into a part that survives within-group label permutation (group-level) and a within-group covariance (case-level). It applies this to two released SGG checkpoints and finds that TDE's mean-recall gain is mostly group-level and is reproduced by a ranking-preserving logit adjustment. The idea is clean, the identity is simple and useful, and the controls (operating-point control, confidence matching, simulated nulls) are more careful than is usual for an audit paper. It is a good fit for an evaluation-methodology contribution.

My concerns are about interpretation, not arithmetic. First, "group-level" is a statement about the test label mix, and the paper's own label-shift path shows that TDE's headline reading changes under a different mix. Second, the answer depends on a grouping the authors choose (18% to 90%) and on a recalibration protocol fitted on test labels. Third, equivalence and "pre-declared" claims rest on a margin and weighting selected within the paper, and the abstract states them more firmly than the supplement does. Fourth, the evidence is two checkpoints of one architecture, yet the paper proposes a reporting standard for benchmarks. The recommendation reflects framing and generalisation gaps that are fixable with text and a small number of additional analyses.

---

## Recomputation Log (read-only, from results/*.json)

| Claim | Source | Recomputed | Verdict |
|---|---|---|---|
| TDE mR@50 gain 0.0972, group 0.0841, case 0.0130, share 87%, CI [83%, 91%] | sgg_recall_split.json, sgg_share_intervals.json | total 0.09715, group 0.08411, case 0.01305; share 0.8657, CI [0.8256, 0.9058] | matches |
| Tier profile: body +0.1224 (group +0.1082), head -0.0255, tail +0.0003 | sgg_recall_split.json | body 0.12242/0.10819; head -0.02553; tail 0.00026 (sum 0.0972) | matches |
| IETrans 97% group-level, case interval [-0.0031, +0.0151] | sgg_share_intervals.json | share 0.9727, CI [0.902, 1.044]; the share CI exceeds 100% | matches; note the share is not bounded in [0,1] and its interval spans 100% |
| Grouping sensitivity: subject-only 18%, pair x position/size about 90% | sgg_grouping_share.json | 0.181 (150 cells), 0.897, 0.902; class pair 0.866 | matches |
| Seven of eight group-level parts change sign toward uniform-within-pair mix | label_shift.json | 7 of 8 flip; only class-only vs FREQ does not (its case part is 0 by construction) | matches |
| TDE vs baseline case-level part under label shift: -0.00006 to +0.01430 | label_shift.json | -5.8e-5 to +0.01430 (CI [0.0112, 0.0174]) | matches |
| TDE vs control case-level: -0.00398 to +0.00723 | label_shift.json | -0.00398 to +0.00723 | matches |
| AUC equivalence margins +-0.0063 (relation) and +-0.0032 (comparison); TDE relation-weighted 90% CI [-0.0037, +0.0008] inside margin; comparison-weighted not equivalent, MDE 0.008 | sgg_equivalence.json | margins 0.00626, 0.00323; ci90 [-0.00373, +0.00077]; comparison-weighted `equivalent: false`, mde80 0.00815 | matches |
| SGCls: TDE +0.0517, 99% group-level; case CI includes zero | sgg_sgcls_audit.json | 0.05172, share 0.9852, case CI [-0.0024, +0.0040] | matches. TDE vs control share is -30 (undefined), which is expected for a near-zero total |
| SGDet: TDE case-level +0.0041 [+0.0013, +0.0070]; control +0.0418 vs TDE +0.0310 | sgg_sgdet_audit.json | case 0.00413 [0.00128, 0.00698]; 0.04184 vs 0.03101 | matches. The case-level CI excludes zero, which the main text does not state; the control matches it |
| F@50 0.344 (LA) vs 0.322 (TDE); R@50 cost 0.0175 vs 0.2023 | paper Sec. 5 numbers | 2PR/(P+R) from 0.6437/0.2343 and 0.4588/0.2476 gives 0.3435 and 0.3216; R@50 drops 0.0175 and 0.2024 | matches |
| CLIP vs geometry matched case-level, five seeds +0.00413 to +0.00474 | vg_visual_seeds.json | 0.00464, 0.00474, 0.00450, 0.00413, 0.00441, all intervals above 0 | matches. The comparison-weighted AUC difference is positive in all five seeds (+0.005 to +0.016), which bears on W3 |
| Sensitivity robustness value rho = 0.0613 | sensitivity_bound.json | 0.06127; bound B 0.2328 | matches |
| Waterbirds GRW vs ERM: group -0.0277, case +0.0914; AUC 0.9723 to 0.9754 | waterbirds_audit.json, supp Table 36 | group -0.02766, case +0.09139 | matches |

I found no arithmetic discrepancy in the quantities I could recompute. The weaknesses below concern what the numbers mean.

---

## Strengths

### S1: An exact, additive, model-free accounting of a paired gain
The identity is the right object for an evaluation audience. It needs no fitted reference model, covers thresholded metrics (mean recall), and is paired with clustered intervals. Related decompositions I know (grouping loss, reliability-resolution) are single-model or need a fitted regressor.
**Evidence Anchor**: text: Sec. 1 "an exact, model-free decomposition of the difference between two frozen models"

### S2: Negative controls and a known-zero validation, with a transparent failure case
The paper checks that the case-level part is zero when both models are functions of the cell (MLP-CLASS vs FREQ, algebraic 0.00000). It shows that a pure calibration change produces a spurious -0.488 on raw outputs, and that the matched protocol removes it. It also reports that coverage falls to 81.5% when every cell has two cases. Reporting where the tool fails is rare and valuable.
**Evidence Anchor**: text: Sec. 4 "credited a large spurious case-level loss of -0.488 on raw outputs, which the confidence-matching protocol of Sec. 3 reduces to -0.0003"

### S3: The operating-point control separates "ranking changed" from "threshold moved"
Subtracting the log training prior from the baseline logits changes no within-pair ranking, yet reproduces +0.0941 of the +0.0972. This isolates what a thresholded metric credits. It makes the paper's claim concrete (a label-prior change, not a ranking change) and ties to known logit-adjustment results from long-tail recognition.
**Evidence Anchor**: table: Table 1 rows LA and TDE-LA (case-level -0.0008, interval [-0.0050, +0.0033])

### S4: Candour about conditionality and about the proper-score sign
Sec. 7 and the introduction state that the split is conditional on the declared grouping, credits shortcuts, and is not invariant to recalibration or label mix. The paper also reports that the proper-score case-level part changes sign with protocol (+0.00445, -0.00006, -0.0184). A reader can see the fragility without digging.
**Evidence Anchor**: text: Sec. 1 "the part changes sign with the protocol and the label mix"

### S5: Reproducibility surface
All stored results regenerate from committed scripts, and the replayed evaluator reproduces the official TDE numbers to four decimals (R@50 0.4588, mR@50 0.2476). Auditing released checkpoints rather than retrained ones is the right design for this question.
**Evidence Anchor**: table: Appendix Table 17 official vs replay (supp.pdf, Sec. O)

### S6: A model the aggregates rank last carries more case-level covariance
The CLIP-crop result is a useful illustration that an aggregate can hide positive within-group information. It is reproduced over five seeds and the paper is explicit that "covariance" is not "better ranking".
**Evidence Anchor**: text: Sec. 6 "carries more case-level covariance without being the better ranker"

---

## Weaknesses

### W1: "87% group-level" is a statement about the benchmark's predicate mix, yet the headline and the abstract do not carry that conditioning
**Problem.** From my angle (long-tail recognition, label shift), a group-level gain in mean recall is exactly what a balanced objective rewards. The paper's own path to uniform-within-pair predicate frequencies (Appendix Q.3) shows seven of eight group-level parts change sign. TDE's case-level part against the baseline moves from -0.00006 (CI spans zero) to +0.01430 (CI [+0.0112, +0.0174]). The part against the control goes from -0.0040 to +0.0072. Under the label mix a practitioner would deploy for tail predicates, the proper-score evidence that TDE has no case-level component disappears. The abstract and conclusion state "almost entirely group-level" as a property of TDE, with the mix dependence only in Sec. 7 and Q.3. The title question ("what did ten points buy") is also normatively loaded, while the text elsewhere says "Group-level is not a lesser gain".
**Why it matters.** A reader will take away "TDE's gain is prior shift" as a model property. The evidence supports "under the VG150 test mix and this protocol". Under a different test prior the split reverses, so the headline is a benchmark-conditional statement, not a claim about what TDE learned. The AUC then bears the full weight of the "no new ranking" claim, and the AUC has low power (W3).
**Suggestion.** (a) Move the label-mix path into the main text (one figure: share and case-level part vs alpha for TDE, LA, IETrans, CLIP vs geometry). (b) Reword the abstract and conclusion to "on the VG150 mix and under the matched protocol". (c) State what test prior the benchmark is meant to represent, and which side of the group/case line is the intended target of mean recall. (d) Soften the title framing or add the conditioning.
- **Severity**: Major | **Evidence Anchor**: text: Sec. 7 "seven of the eight group-level parts of Sec. 5 and this section change sign"; table: label_shift.json TDE vs MOTIFS case -0.00006 to +0.01430 | **Confidence**: 4 — core expertise: label shift

### W2: The group/case split is not identified without a declared grouping, and the grouping is chosen by the authors with an unreported-selection risk
**Problem.** The group-level share is 87% under the class-pair grouping, 18% under subject class, and about 90% under pair x position or pair x size (sgg_grouping_share.json). The text argues that "the finest grouping the benchmark's construction defends is the conservative choice." Refinement is not neutral for coverage: relations in singleton cells are excluded, and those cells are disproportionately rare object pairs, which is where rare predicates live. Coverage drops from 99.0% (class pair) to 96.8% (pair x position). The supplement confirms that "two equally fine partitions of the same cases can disagree" (Appendix K) and the sensitivity bound shows that an unrecorded covariate correlated at 0.061 would account for the whole case-level gain of Sec. 4. So the case-level evidence for geometry (+0.0144) is not robust evidence of "reasoning", and the paper uses "reasoning_gain" in its result files.
**Why it matters.** This is the grouping-loss/shortcut problem, and it is not resolved by a pre-declared rule alone. A reader cannot tell a case-level gain from a shortcut in the data. The one-column "within-group reliance" leaderboard summary proposed in the conclusion inherits this.
**Suggestion.** (a) Report the share as a function of grouping depth (class pair, + position, + size) in one table, with coverage and the excluded relation mix by predicate tier. (b) Rename "case-level" in the main text and code to "within-group covariance" and say explicitly that it credits shortcuts (the paper does so in Sec. 7 but the name carries a reasoning connotation). (c) Show for which singleton-excluded relations the group share could change (an extreme-case bound).
- **Severity**: Major | **Evidence Anchor**: dataset: sgg_grouping_share.json — share 0.866 (class pair, 5,044 cells), 0.181 (subject class), 0.897 (pair x position, coverage 0.968) | **Confidence**: 4 — core expertise: grouping loss and shortcut learning

### W3: Equivalence and "pre-declared" claims depend on a margin and weighting chosen within the paper, and the abstract omits the weighting under which equivalence fails
**Problem.** (i) The equivalence margin is "a tenth of what box geometry buys over the class pair". That margin is computed from this paper's own reconstructed split and its own models, so it is data-derived, not external. (ii) The "primary" weighting (relation-weighted AUC) is the one under which TDE is equivalent (90% interval [-0.0037, +0.0008] within +-0.0063). Under comparison weighting the interval does not fit the margin (+-0.0032), the minimal detectable change is 0.0082 (2.5 times the margin), and the result is a non-detection. The abstract states equivalence for TDE without that qualification. (iii) For CLIP vs geometry the primary weighting says geometry ranks better (-0.0067), the comparison weighting says CLIP is better in all five seeds (+0.005 to +0.016, vg_visual_seeds.json), and the paper takes the primary one. (iv) Six recall protocols, two AUC weightings, two proper scores, three recalibration variants and several groupings are all reported. "Pre-declared" cannot be verified from an anonymised submission (no registry timestamp or hash of the protocol).
**Why it matters.** With this many forks, a null that holds under the chosen weighting and fails under the other is weak support for "TDE's within-pair ranking is equivalent to the baseline's". The paper itself says "a null needs a margin", and the margin's provenance matters.
**Suggestion.** (a) In the abstract and Sec. 5 say "equivalent under relation-weighted AUC; not distinguishable under comparison-weighted AUC (MDE 0.008)". (b) Justify the margin from an external, predeclared reference (e.g. a margin set by the benchmark's variation across seeds of one method, or across published methods). (c) Provide the time-stamped protocol (anonymous commit hash or archived file) so "declared in advance" is checkable. (d) Give one summary table of all weighting/protocol combinations for the TDE-vs-baseline comparison.
- **Severity**: Major | **Evidence Anchor**: table: sgg_equivalence.json — comparison-weighted TDE vs none `equivalent: false`, mde80 0.00815 vs margin 0.00323 | **Confidence**: 4 — core expertise: evaluation methodology

### W4: The confidence-matching protocol that sets the sign of the proper-score case-level part is fitted on test labels
**Problem.** Matching fits a temperature and a per-class bias for each model by maximum likelihood on one random half of the test images and evaluates on the other half (Sec. 3). The per-class bias (K parameters) is a label-prior correction learned from test labels, so the "frozen model" comparison is made after a data-dependent label-shift correction on the same test distribution. The paper shows that the sign is protocol-dependent (+0.00445 primary, -0.00006 temperature-only, -0.0184 shared temperature). Over 20 calibration halves the primary part stays positive, but the repeated halves share one test set, so this measures split noise, not protocol validity.
**Why it matters.** The headline proper-score statement "TDE is more certain where it is right" rests on a protocol whose choice decides the sign, and the criterion that selects it ("must give zero case-level part to a constant shift of within-cell log-odds") is satisfied by the per-class-bias family by construction, not by an independent check.
**Suggestion.** (a) Fit the calibration on a held-out set not used for the audit (e.g. VG validation split) as the primary protocol; report the test-half variant as secondary. (b) Rest the main text's TDE conclusion on the rank-based quantities (within-cell AUC, operating-point control) and present the proper-score matched part as supporting, with its sign sensitivity stated beside the number.
- **Severity**: Major | **Evidence Anchor**: text: Sec. 3 "fit each model a recalibration by maximum likelihood on one half, and split the gain on the other" | **Confidence**: 3 — adjacent expertise: calibration under shift

### W5: Two checkpoints from one architecture do not support a field-wide reporting standard, and the IETrans comparison is not controlled
**Problem.** The scene-graph audit is TDE on Motifs (PredCls, with SGCls/SGDet replication from the same release) and one IETrans+Rwt checkpoint with "no baseline released", so IETrans is compared against a separately trained baseline. The conclusion nonetheless recommends that "such benchmarks report" eight items, and the text says "the field's metrics report the sum". Outside SGG, Waterbirds contains a single model pair, and the CIFAR-100-LT cell is a superclass, a function of the label, not "a feature both models condition on" (supp N.5: "not an audit of a feature both models condition on"). So the cross-domain support is for the estimator's behaviour, not for the claim that debiasing methods generally earn group-level credit.
**Why it matters.** The most striking claim, that mean recall cannot tell prior correction from discrimination, is shown for one method family and one test mix. Waterbirds actually shows the opposite pattern (GRW is case-level, group-level -0.0277), which underlines that conclusions are method- and benchmark-specific.
**Suggestion.** (a) Limit the conclusion to "for the audited checkpoints". (b) If more checkpoints are public, add two or three (other released SGG debiasers, or class-balanced and logit-adjusted baselines in CIFAR-LT with input-grounded cells). (c) Mark the IETrans row clearly as uncontrolled in Table 1, not only in prose.
- **Severity**: Major | **Evidence Anchor**: text: Sec. 5 "No IETrans baseline was released, so this compares two separately trained models and does not isolate the effect of relabelling" | **Confidence**: 4 — core expertise: long-tail evaluation

### W6: The estimand is the micro-pooled mean recall, not the official per-image statistic
**Problem.** The split is of "the micro-averaged version, which pools relations across images; it tracks the official per-image average but is not it" (+0.0972 vs +0.1017; about 5% apart). The 87% share is a ratio of the surrogate's parts. Section 5's "ten points" are the official number.
**Why it matters.** Small for TDE but unquantified for IETrans (official 0.3576 vs 0.3587 on a different test set) and for other methods; the headline ties a surrogate's share to the official gain.
**Suggestion.** Report the official-statistic change beside each split, and state the surrogate-to-official gap per row of Tables 1 and 2.
- **Severity**: Minor | **Evidence Anchor**: text: Sec. 1 "it tracks the official per-image average but is not it" | **Confidence**: 3 — adjacent field: SGG metric conventions

### W7: Practical adoption cost of the proposed reporting standard is not assessed
**Problem.** The method needs the model's score for every label on every test case; the paper says "most benchmarks do not archive" these and that recovery "took a rerun of the released checkpoint". The proposed report has about eight elements (grouping, coverage, cell sizes, both parts with intervals under two protocols, AUC under two weightings with a margin, label-mix path, operating-point control, reliance column). A leaderboard maintainer, or a method author with a closed model, cannot supply this from the usual submission format.
**Why it matters.** The value of the paper to practitioners depends on a minimal version being adoptable. As written it is a research protocol.
**Suggestion.** Define a minimal tier (e.g. top-k logits per case, one grouping, the operating-point control, relation-weighted AUC), and say what is lost relative to the full tier.
- **Severity**: Minor | **Evidence Anchor**: text: Sec. 7 "it needs scores for every label, which most benchmarks do not archive" | **Confidence**: 3 — practitioner view, no direct SGG deployment experience

---

## Detailed Comments

### Assumption Audit
- **Explicit assumptions**: The grouping is declared in advance and observed by both models; cells are not tiny; clusters do not dominate. All are stated. The cell-size condition is tested (81.5% coverage at two cases per cell).
- **Implicit assumptions**: (1) That the test label mix is the object of interest. Mean recall is built to reweight rare predicates, so a label-prior-driven gain is by design not a defect; the split describes where a gain was earned, but the paper's wording ("what did ten points buy") invites a verdict that the text then disclaims. (2) That the relation-weighted AUC is the right arbiter of "ranking". It weights cells by comparisons and depends on the cell-size distribution. (3) That within-cell covariance reflects model information about the case, rather than label noise structure. VG predicates are known to be noisy and near-synonymous (the paper merges synonyms in Q.2); within-pair noise interacts with AUC.
- **Paradigmatic assumptions**: The decomposition treats the benchmark's test distribution as the reference. Long-tail research typically evaluates across a family of test priors (balanced vs natural); the paper's path in Q.3 is the right direction and should be the primary view.

### Cross-Disciplinary Connections
- **Parallel research**: In long-tail recognition, the equivalence between post-hoc logit adjustment and training-time rebalancing (Menon et al., ICLR 2021, cited) and the prior-shift view of balanced error are the closest parallels. The paper cites them and builds on them. In VQA, shortcut-versus-reasoning attribution under changing answer priors (VQA-CP, cited as Agrawal et al.) shows how a gain credited to a method can come from the prior. Subpopulation-shift benchmarks (Waterbirds, cited; WILDS, Koh et al., ICML 2021) face the same separation.
- **Borrowing opportunities**: The group/case split is an explained/unexplained decomposition in the Oaxaca-Blinder tradition from labour economics (Oaxaca 1973; Blinder 1973; both attestable). That literature has worked on how the split depends on the reference group and on the index-number problem. That is precisely the grouping and label-mix dependence here, and it provides vocabulary (reference-weight sensitivity) for W1 and W2.
- **Methodological borrowing**: Report results across a one-parameter family of test priors rather than one, as in cost-curve and prior-shift evaluation, and give the crossing points between methods.

### Practical Impact
- **Real-world application**: The operating-point control is immediately usable by anyone proposing a debiasing method: before claiming new discrimination, subtract the training log-prior and compare. That alone is a worthwhile takeaway.
- **Implementation feasibility**: See W7.
- **Stakeholders**: Method authors whose methods are audited (TDE, IETrans) have no reply channel in a paper like this. The wording "what did ten points buy" can read as accusatory, and the paper's own caveats (group-level is a legitimate gain under mean recall) should lead.

### Broader Implications
- **Ethical dimensions**: Low risk. One consideration is fairness to audited authors: the audit uses released checkpoints on one run each ("We ran it once"), with no seed variance for the checkpoint itself.
- **Social impact**: Not applicable beyond benchmark hygiene.
- **Future directions**: A benchmark-side recommendation of a family of test priors; extend to open-vocabulary SGG, where the paper cites that metrics inherit the same pathologies.

---

## Cross-Disciplinary Reading Recommendations
- Oaxaca, R. (1973), "Male-female wage differentials in urban labor markets", International Economic Review; and Blinder, A. (1973), "Wage discrimination: reduced form and structural estimates", Journal of Human Resources. Explained/unexplained decomposition and its reference-group dependence, relevant to W1 and W2.
- Koh, P. W. et al. (2021), "WILDS: A benchmark of in-the-wild distribution shifts", ICML. Cross-benchmark evaluation of subpopulation shift, relevant to W5.
- Quinonero-Candela, J., Sugiyama, M., Schwaighofer, A., Lawrence, N. (eds.) (2009), Dataset Shift in Machine Learning, MIT Press. Prior-shift and evaluation under shifted priors, relevant to W1.
- [UNVERIFIED] Search lead: work on "accuracy on the line" and agreement-on-the-line style predictors of out-of-distribution behaviour from in-distribution metrics, for the question of whether the group/case split predicts behaviour under a different label mix.

---

## Questions for Authors
1. For the audience that wants mean recall to reward tail predicates, which side of the split is the intended target? If group-level gains are legitimate under that metric, what is the decision the audit changes (rank of methods, claim about "reasoning", or cost of the gain)?
2. TDE's case-level part against the baseline is -0.00006 on the benchmark mix and +0.0143 at the uniform end, with a CI excluding zero. Which statement should a reader take as the answer about TDE, and does the AUC-based "no new ranking" claim hold at the uniform end with the same margin?
3. How was the equivalence margin and the primary weighting fixed relative to the first look at TDE's AUC? Can you provide an archived, dated protocol file?
4. If the calibration halves for confidence matching come from the validation split rather than from the test set, do the signs and sizes in Tab. 2 and Fig. 2 persist?
5. For relations in singleton cells (1.1% in PredCls, 42% unmatched in SGCls), what is the extreme-case bound on the group share if they were case-level?

## Minor Issues
- Abstract: "equivalent to the baseline's within a margin fixed in advance" should name the weighting. "TDE's ranking within pairs gets worse" (SGCls) holds for relation-weighted AUC only; comparison-weighted is -0.0047 with CI [-0.0122, +0.0031].
- Group-level share can lie outside [0,1] (IETrans 97%, CI [90%, 104%]; TDE vs control -30). Say how a share is to be read when the total is near zero, or report only signed parts there.
- Result files and appendix code use "reasoning_gain" for the case-level part, which contradicts the paper's own caution that it credits shortcuts.
- Sec. 5 SGDet: state that the TDE case-level interval [+0.0013, +0.0070] excludes zero and is matched by the control.
- Table 1: indicate by a mark that the IETrans row is against a separately trained baseline.
- Sec. 6 closes with a stray double period ("excludes zero in one..") in the seeds paragraph.
