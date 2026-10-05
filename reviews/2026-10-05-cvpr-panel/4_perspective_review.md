# Peer Review Report — Peer Reviewer 3 (Perspective)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission (anonymous); repository commit 909e5a3
- **Review Date**: 2026-10-05
- **Review Round**: Round 1 (simulated panel, `academic-paper-reviewer` v1.11.1, mode `full`)

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 3 (Perspective)

### Reviewer Identity
I work on ML evaluation outside scene graph generation (SGG): long-tailed recognition, language-prior bias in VQA, shortcut learning, calibration and grouping loss, and label shift. I am not an SGG specialist. My comments on SGG conventions should be read with that in mind.

### Review Focus
I ask four things. Is the group-level/case-level split a new instrument, or a known decomposition in new clothes (Murphy/Yates, grouping loss, permutation importance, label-shift estimation)? Do the paper's lessons travel beyond SGG, and do the long-tailed image and text studies show that they do? What does a practitioner actually get from the label-shift test and the proposed reporting standard? How likely is a practitioner to misread the case-level part?

### Calibration and binding status
Calibration status: `NOT_CALIBRATED`

criteria_binding_unavailable

There is no author-confirmed target context. The CVPR remarks below are a configured perspective. They are not a venue-alignment determination.

---

## Overall Assessment

### Recommendation (skill scale)
- [ ] Accept
- [ ] Minor Revision
- [x] **Major Revision**
- [ ] Reject

### CVPR-scale rating
**Weak Accept**. Reviewer confidence (CVPR 1–5): **3**.

### Confidence Score (skill scale)
**3**: about half of this is my area. The evaluation science, the calibration and decomposition literature, long-tail and label-shift work are mine. SGG-specific conventions (PredCls protocol, the TDE/IETrans codebases) are not.

Confidence is an uncertainty/scope disclosure only; it never changes consensus counts, severity, decision bearing, or arbitration.

### Summary Assessment
The paper takes the difference between two frozen classifiers and splits it into two parts with a within-group label swap. The group-level part is what survives scoring each prediction against another case's label from the same subject–object cell. The case-level part is the within-cell covariance that remains. The split applies to Bregman scores and to mean recall, and it comes with image-clustered intervals. Applied to released TDE and IETrans checkpoints, it finds their mean-recall gains are 87% and 97% group-level. A ranking-preserving logit adjustment reproduces most of TDE's effect. A CLIP-feature model ranked last on every aggregate carries more within-cell covariance than a geometry model.

As evaluation science outside SGG, the paper is careful, unusually candid and reproducible. The operating-point control and the label-shift test are practices other fields should copy.

The main weakness from my angle is positioning and payoff, not correctness:
- The split is exactly a difference of per-model within-group permutation importances. I recomputed this on the cached outputs. The paper never says so, and its claim to be the first two-model attribution partly rests on not saying so.
- The long-tailed image and text studies use groupings derived from the label. They show that the estimator runs. They do not show that the SGG lessons travel.
- The proposed reporting standard leaves out the within-cell AUC and the label-mix check. The paper itself needed both to interpret its own case-level numbers.

All of this is repairable without new SGG experiments. One input-grounded, non-SGG audit would make the paper much more compelling. Hence Weak Accept on the CVPR scale and Major Revision on the skill scale, because the contribution statement needs substantive rewriting.

---

## Strengths

### S1: An operating-point control and a threshold-free test that other fields can reuse
Every recognition claim is read against two things. One is a ranking-preserving logit-adjusted baseline. The other is a within-cell AUC that no recalibration or cell-constant shift can move. The paper reports the uncomfortable result openly: the control alone produces a significant case-level part of mean recall. Long-tail and VQA debiasing papers rarely include this control-and-invariant pairing, and it is the most transferable part of the paper.
**Evidence Anchor**: `table: Table 1 — LA row (case-level +.0139, ∆AUC +.0001) beside the TDE and TDE−LA rows`

### S2: The label-shift test makes a falsifiable prediction that the data confirm
Sec. 3 predicts that group-level parts are directly exposed to the label mix, while case-level parts are only reweighted. Reweighting the test set so that predicates are uniform within each cell flips the group-level sign in 7 of 8 comparisons. Five of the six case-level parts that excluded zero keep their sign. The aggregate ranking of CLIP versus geometry reverses (+0.02478). This is exactly the deployment question long-tail practitioners care about, answered without retraining.
**Evidence Anchor**: `table: Supp. Table 27 — group-level parts change sign in 7 of 8 comparisons under uniform-within-cell weights`

### S3: Additive per-predicate and per-tier accounting
The split is exact and linear, so the mean-recall change can be attributed predicate by predicate and tier by tier, and the parts add up. No rank metric or stratified recall does this. Figure 3 shows the mechanism ("parked on" for (car, street)) at a granularity that stratified mean recall cannot.
**Evidence Anchor**: `figure: Figure 3 — per-predicate group-level/case-level split of TDE's recall@50 change with the logit-adjustment total`

### S4: Self-applied sensitivity analysis and candid limits
The authors apply their own omitted-covariate bound to their own positive result. They report that a covariate correlated at 0.061 would explain it away. They also show that equally fine partitions can disagree completely (Supp. K). Few evaluation papers say this about themselves.
**Evidence Anchor**: `text: §7 Limitations "our own bound on that exposure is not reassuring"`

### S5: Reproducibility
The evaluator replay matches the official numbers exactly. All cached outputs ship with the code. The bundled checker traced all 298 printed numbers to committed results when I ran it. I independently reproduced the raw CLIP-versus-geometry split (see Recomputation).
**Evidence Anchor**: `table: Supp. Table 15 — official vs re-scored R@50/mR@50/ng-mR@50/mR@100 identical for baseline and TDE`

### S6: A useful caution for vision–language evaluation
Zero-shot CLIP has within-cell AUC 0.5164 against MOTIFS's 0.5705 on the canonical relations. That is concrete, cell-controlled evidence that a widely used VLM does not rank predicates within an object pair the way a trained SGG model does. It is relevant well beyond SGG.
**Evidence Anchor**: `table: Supp. Table 28 — zero-shot CLIP within-cell AUC 0.5164 vs MOTIFS 0.5705; case-level part over FREQ +0.00046 vs +0.02943`

---

## Weaknesses

### W1: The split is a difference of per-model within-group permutation importances, which undercuts the "two-model" novelty claim and hides a simpler reporting route
**Problem**: The transported score of model m is the score of its prediction for case i averaged over the other labels in i's cell, (Σ_{j≠i} S(q_m(x_i), y_j))/(n_c−1). Swapping labels within a cell is the same as swapping the non-group part of the input within the cell. That is the "switch" U-statistic behind permutation-based model reliance, in its conditional (within-stratum) form. Because H = S(q1) − S(q0) and the estimator is linear in H:
- ∆P̂ is the difference of the two models' within-cell permuted scores.
- ∆R̂ is the difference of their within-cell permutation importances. In my notation, R̂(q) = mean_i[S(q_i, y_i) − mean_{j≠i in cell} S(q_i, y_j)].

I verified this on the cached CLIP-study outputs (Recomputation). Per-model values are 0.00000 (class-only), 0.01023 (geometry) and 0.01663 (CLIP). Their difference, 0.01663 − 0.01023 = 0.00640, is exactly the reported case-level gain.

The paper's positioning, "All of these characterise a single model. We attribute the gain between two", therefore overstates the novelty. The two-model part lies in the paired, cluster-robust interval, not in the point decomposition. The permutation-importance and model-reliance literature is never cited. Supp. Table 4 mentions "permutation within blocks" only as a synonym.
**Evidence Anchor**: `text: §2 Related work, p.3 l.170–171 "All of these characterise a single model. We attribute the gain between two."`
**Why it matters**: A non-SGG CVPR reader who knows conditional permutation importance (Strobl et al. 2008) or model reliance (Fisher, Rudin & Dominici 2019) will read the contribution as a repackaging unless the paper states the equivalence and says what it adds. The equivalence also has an upside the paper misses. Leaderboards could report one per-model number, "within-group reliance", next to the headline metric, so no pairwise audit is needed for each comparison. That is much easier to adopt than a pairwise split.
**Suggestion**:
- State the equivalence as a proposition: ∆R̂ = R̂(q1) − R̂(q0), with R̂ the within-cell label-permutation importance.
- Cite the permutation-importance and model-reliance lineage.
- Restate the contribution as: an exact additive accounting of a paired gain into two per-model terms; an unbiased leave-one-out estimator (Prop. 4); paired cluster-robust inference; and extension to thresholded metrics.
- Propose the per-model column as the leaderboard-friendly form of the reporting standard.
**Severity**: Major
**Confidence**: 4 (core expertise: permutation importance and evaluation; the equivalence is recomputed, not inferred)

### W2: The long-tailed image and text studies do not test the paper's lesson, because their groupings are derived from the label
**Problem**: The paper defines the group-level part through "a discrete grouping both models observe" (Sec. 3). Both non-SGG studies instead group by coarse superclass or topic, which is a function of the label, not the input. The supplement concedes this. In that setting, transport keeps each case's superclass, so the "group-level" part includes the model's skill at recognising the superclass, which is a per-image skill. The interpretation of the paper's title ("earned at the level of the group") therefore does not carry over. The only input-grounded grouping used outside SGG is the trivial global cell. In addition:
- The text study is single-seed and raw (not confidence-matched).
- The two domains reach opposite verdicts on CB versus DRW.

The main text still says "Nothing in Sec. 3 is specific to relations" and presents these studies as the evidence for that.
**Evidence Anchor**: `text: Supp. N.5, l.1382–1383 "the superclass rows show how the estimator behaves under a label-derived grouping, not an audit of a feature both models condition on"`
**Why it matters**: The reason a non-SGG CVPR reader would care is that SGG's object-pair prior is one case of a general pattern. Other cases are the question prior in VQA, the background in Waterbirds and the site or scanner in medical imaging. The paper names these settings in Related Work but never audits one. As it stands, the generality claim is a statement about the algebra, not evidence about how the lessons transfer.
**Suggestion**:
- Run one input-grounded, non-SGG audit. Option (a): VQA-CP or GQA-OOD, grouping by question type or by the normalised question string (both models observe it), comparing a debiased VQA model (e.g., a RUBi- or LMH-style model) with its base. Option (b): Waterbirds/CelebA with the spurious attribute as the cell, comparing ERM with GroupDRO. In (b), the case-level part reads directly as within-background use of the core feature.
- If space does not allow, reword "Beyond scene graphs" to say the supplementary studies show estimator behaviour under label-derived groupings, not that the findings transfer.
**Severity**: Major
**Confidence**: 4 (core expertise: long-tailed recognition and VQA bias)

### W3: The proposed reporting standard leaves out the instruments the paper itself needed to interpret the case-level part
**Problem**: The conclusion asks benchmarks to report the grouping and its coverage, both signed parts, the confidence-matched row and the operating-point control. It does not include:
- **The within-cell AUC.** The paper calls this the "direct test" of new discrimination, and it alone decides the CLIP case.
- **A label-mix sensitivity row.** TDE's case-level null becomes +0.01430 under uniform within-cell labels.
- **The within-cell label heterogeneity** that Supp. K says must be reported, because coverage cannot detect a nearly label-homogeneous grouping.

Under the standard as written, a leaderboard would publish a case-level column whose positive values the paper shows can come from:
- an operating-point move (LA control: +0.0139 of mean recall, with no ranking change);
- a temperature (−0.488 in the controlled check);
- a modest unrecorded covariate (ρ† = 0.061).
**Evidence Anchor**: `text: §7 Conclusion, p.8 l.619–623 "the declared grouping and its coverage, both signed parts with the case-level interval, the confidence-matched row, and, for a thresholded metric, the operating-point control"`
**Why it matters**: Practitioners will read "case-level gain" as "better recognition". Shortcut-learning research shows how fast such a column becomes a target (Goodhart; Teney et al. [37]). A standard that publishes the misreadable number without the companions needed to read it does more harm than good.
**Suggestion**:
- Add three items to the standard: the within-cell AUC difference with its interval; the case-level part under at least one declared alternative label mix (or its range, see W5); and a within-cell label-heterogeneity statistic.
- State a decision rule in the main text, e.g. "claim a recognition gain only if ∆R exceeds the operating-point control's ∆R and the ∆AUC interval excludes zero".
- Use the neutral supplementary name ("within-group covariance") in any leaderboard column.
**Severity**: Major
**Confidence**: 4 (core expertise: evaluation reporting practice and calibration)

### W4: Every headline recognition verdict comes from the control and the AUC, not from the split
**Problem**:
- **TDE.** TDE's case-level part of mean recall (+.0130) is no larger than that of the ranking-preserving control (+.0139). The verdict "no discrimination gained" rests on the TDE−LA contrast and the within-cell AUC, which straddles zero.
- **CLIP.** The case-level advantage exists, but the AUC cannot separate the models, and accuracy, MRR and recall@5 disagree with the split.
- **IETrans.** The mean-recall case-level part is null and only the proper scores show a loss. The two proper scores disagree in sign for TDE against the control.

So in each headline case, the case-level part on its own did not decide the question. The split's distinctive contributions are elsewhere: exact additive accounting (S3), and a prediction about which comparisons a label shift will reverse (S2, e.g. CLIP overtaking geometry). The paper presents the second as a robustness check rather than as the main payoff.
**Evidence Anchor**: `table: Table 1 — LA row case-level +.0139 [+.0101, +.0176] vs TDE row +.0130 [+.0093, +.0168]; TDE ∆AUC +.0026 [−.0028, +.0086]`
**Why it matters**: A CVPR reader will ask what the split tells them that "add a logit-adjusted control and a within-group AUC" does not. Long-tail work has already shown that post-hoc logit adjustment matches many training-time remedies (Menon et al. [26]). The answer that survives is accounting plus label-shift exposure. The current framing ("we give an exact way to tell them apart") promises a recognition test the split cannot deliver alone.
**Suggestion**: Reframe the split as the accounting and exposure instrument, and the AUC with the operating-point control as the recognition test. Make the label-shift prediction prospective in the main text: state from the split which comparisons should reverse under a declared target mix, then show that they do.
**Severity**: Major
**Confidence**: 3 (adjacent: depends partly on how SGG readers weigh the TDE audit itself)

### W5: The label-shift test uses one extreme mix and does not use the label-shift toolkit
**Problem**: The only shift tested is "every predicate of an object pair equally frequent". That is an extreme point of the simplex, not a plausible deployment mix. The paper's own pairwise form, ∆R_c = Σ_{y<z} p(y)p(z) D(y,z), lets the case-level part be computed for any target mix once the D(y,z) are estimated. So the sign-stability region, or a worst case over a neighbourhood of the benchmark mix, is available at no extra cost. The paper also does not connect group-level deficits to post-hoc label-shift correction. Its own result that prior correction halves the CLIP model's aggregate deficit (Supp. N.3) suggests that much of a group-level gap can be repaired after training.
**Evidence Anchor**: `text: Supp. Q.3, l.1642–1643 "This is the test set a deployment with uniform within-pair predicate frequencies would see."`
**Why it matters**: For a practitioner, the payoff of the label-shift test is to know which gains survive their deployment mix, and which gaps a post-hoc prior correction (Saerens EM, BBSE [23,31]) would close. Long-tail work already evaluates across several test label distributions (e.g., test-agnostic LT protocols). Aligning with that work would make the payoff clear to non-SGG readers.
**Suggestion**: Report the case-level and group-level parts over a one-parameter path from the benchmark mix to the uniform mix, or over a Dirichlet neighbourhood of it. Report the fraction of mixes on which each sign holds. Add one sentence saying that group-level deficits are the part an estimated-prior correction targets.
**Severity**: Minor
**Confidence**: 4 (core expertise: label shift)

### W6: Calling only case-level gains "better recognition" sits awkwardly with ambiguous Visual Genome labels
**Problem**: The introduction says only case-level gains are "better recognition". But many VG relations admit several valid predicates. Moving probability from "on" to "parked on" for (car, street) may be what a downstream consumer such as captioning or robotics wants, and it is the stated aim of IETrans. The supplement already says a transported gain is "a description of where score was earned, not an accusation", but the main text does not carry that nuance. The synonym merges (Supp. Q.2) address recognisability, not informativeness.
**Evidence Anchor**: `text: §1, p.2 l.052–054 "The first is a change in the model's group-level predictions; only the second is better recognition."`
**Why it matters**: Practitioners may read group-level gains as illegitimate and discard methods that do make outputs more informative for their use.
**Suggestion**: Bring the supplement's "not an accusation" sentence into Sec. 1 or Sec. 7. Distinguish recognition (case-level) from preference or informativeness (group-level), and note that which one matters depends on the downstream user.
**Severity**: Minor
**Confidence**: 3 (adjacent: VG annotation practice is outside my core)

### W7: The Yates lineage is credited in Related Work but missing from the abstract and contributions
**Problem**: Under the quadratic score, ∆R_c (Eq. 3) is the cell-wise difference of Yates's covariance term between two models. ∆P_c (Prop. 1) is the difference of Yates's bias and scatter terms. Sec. 2–3 say this. The abstract ("We give an exact way to tell them apart") and the contribution bullet ("An exact, model-free decomposition") do not.
**Evidence Anchor**: `equation: Eq. (3) and Supp. Prop. 1 Eq. (8) — stratified two-model differences of Yates's covariance term and of the bias/scatter terms`
**Why it matters**: Forecast-verification and calibration readers will recognise the decomposition at once. Stating the lineage up front builds credibility and points readers to what is new: stratification, the two-model contrast, the leave-one-out estimator, clustered inference, Bregman scores and hit-rate metrics.
**Suggestion**: Add one clause to the contribution bullet, e.g. "extending Yates's covariance decomposition to a stratified two-model contrast, every Bregman score and label-weighted hit rates".
**Severity**: Minor
**Confidence**: 4 (core expertise: proper-score decompositions)

### W8: The text study calls a raw-output result "genuine" although the paper shows raw outputs can invert
**Problem**: On 20 Newsgroups-LT, CB is said to buy "genuine" within-topic covariance gain. That rests on one seed with raw outputs. Yet on CIFAR-100-LT, the paper shows calibration matching inverts DRW's raw composition, and that recalibration alone moves the channels by +0.380 and −0.175.
**Evidence Anchor**: `text: Supp. N.6, l.1478–1479 "it is class-balanced re-weighting from initialization, not the deferred schedule, that buys genuine within-topic covariance gain"`
**Why it matters**: This contradicts the paper's own protocol, and it is the evidence offered for breadth (W2).
**Suggestion**: Run the matched protocol over several seeds on the text task, or drop "genuine" and mark the text result as raw and provisional.
**Severity**: Minor
**Confidence**: 4 (core expertise: long-tail re-weighting and calibration)

### W9: The reporting standard covers only the protocol furthest from deployment
**Problem**: The split does not apply to SGCls or SGDet. It also needs full score vectors, and most benchmarks archive only top-k. Both limits are conceded, but the conclusion addresses the recommendation to "benchmarks whose labels lean on a feature every model sees" without saying it is restricted to PredCls-type protocols.
**Evidence Anchor**: `text: §1 "What is not claimed", p.3 l.129–130 "in SGCls and SGDet the cell is itself predicted, and the split as stated does not apply"`
**Why it matters**: Benchmark maintainers deciding whether to adopt the standard need to know its scope, and what archiving it requires (full per-label scores).
**Suggestion**: Scope the recommendation explicitly. Add a short "what a benchmark must archive" note, e.g. full per-label probabilities for all identified relations and image IDs for clustering.
**Severity**: Minor
**Confidence**: 3 (adjacent: SGG protocol details)

### W10: The Figure 1 caption describes the case-level part more strongly than the paper's evidence allows
**Problem**: The caption says ∆R̂ is "the part that needs the right label on the right image". The ranking-preserving control earns a significant case-level part of mean recall and of both proper scores without changing any within-cell ranking, so this description is not accurate in general.
**Evidence Anchor**: `figure: Figure 1 caption — ∆R described as "the part that needs the right label on the right image"`
**Why it matters**: Figure 1 is what most readers will remember, and it builds in the misreading that W3 warns about.
**Suggestion**: Reword it to "the part that depends on which case carries which label within its group; read it against an operating-point control".
**Severity**: Minor
**Confidence**: 4 (direct reading against Table 1 and Supp. Table 19)

---

## Detailed Comments

### Assumption audit
- **Explicit assumptions.** The grouping is declared in advance and observed by both models. Labels within a cell are exchangeable with independent draws (Thm. 3). Images are independent clusters. The authors handle all of these with care, and Supp. J is unusually honest that the limit theorem does not describe their own finite-sample regime.
- **Implicit assumptions.**
  - (i) The benchmark's label mix is the right reference for judging a method. The label-shift test shows the verdict depends on it (S2, W5).
  - (ii) Group-level change is not what users want (W6).
  - (iii) A two-model contrast is a different kind of object from single-model diagnostics. W1 shows it is a difference of single-model terms.
- **Paradigm.** The paper treats evaluation as forecast verification with proper scores. That is a healthy import into CVPR. The cost is that the headline SGG metric is thresholded, which forces the operating-point machinery. The paper handles this honestly, but it adds steps a practitioner must follow correctly.

### Cross-disciplinary connections
- **Parallel work.**
  - Permutation importance and model reliance: within-stratum permutation is the conditional variant (W1).
  - Grouping-loss decompositions (Kull & Flach; Perez-Lebel et al. [28]).
  - Multicalibration, fairness and xAUC: grouping by a protected attribute and splitting a gain into base-rate fit versus within-group ranking is exactly this construction.
  - VQA bias-only branches (RUBi, LMH): their "bias-only model" plays the role of FREQ.
- **What to borrow.**
  - Report the sign-stability of case-level parts over a set of label mixes, as in distributionally robust and test-agnostic long-tail evaluation (W5).
  - Report the within-cell AUC as a stratified version of the Hand–Till multiclass AUC, which gives readers a familiar reference point.
- **Methods to borrow.** Contrast sets and minimal-pair evaluation from NLP are the dataset-side counterpart of the within-cell counterfactual. A small set of relabelled (man, surfboard) pairs would provide ground truth for the case-level part.

### Practical impact
- **Real-world use.** For SGG, the most actionable result is that a one-line logit adjustment recovers about 97% of TDE's mean-recall gain (0.0941 against 0.0972) at 8.6% of its R@50 cost (0.0175/0.2024, recomputed). Any SGG debiasing paper should now include that control. The split adds per-predicate accounting and a label-shift exposure readout.
- **Feasibility.** Blocked by archiving (full score vectors) and by protocol (PredCls only), as W9 notes. The per-model form (W1) lowers the barrier, since each submission could report its own within-group reliance once.
- **Stakeholders.**
  - Downstream consumers of scene graphs, whose preference between informativeness and recognition (W6) decides whether a group-level gain is good.
  - Benchmark maintainers, whom the paper asks to declare the grouping before a leaderboard opens. That is a governance task that needs a concrete proposal: who declares the grouping, how it is versioned, and how it is changed.

### Broader implications
- **Ethics.** None specific to this paper. The same construction applied to demographic groupings would separate base-rate fitting from within-group discrimination. A one-sentence pointer would help, with a caution that the case-level part also credits proxies.
- **Misuse risk.** A positive case-level column could be gamed by sharpening predictions after a temperature change, or by within-cell shortcuts (W3, W10).
- **Future directions.** An input-grounded VQA or spurious-attribute audit (W2). A per-model leaderboard column (W1). Prospective label-shift predictions (W4, W5).

---

## Cross-Disciplinary Reading Recommendations
- Fisher, A., Rudin, C., Dominici, F. (2019). "All Models are Wrong, but Many are Useful: Learning a Variable's Importance by Studying an Entire Class of Prediction Models Simultaneously." *JMLR* 20(177). Model reliance and the all-pairs "switch" U-statistic; this is the per-model term behind ∆P/∆R. [verify the section number for their conditional, within-group variant]
- Strobl, C., Boulesteix, A.-L., Kneib, T., Augustin, T., Zeileis, A. (2008). "Conditional variable importance for random forests." *BMC Bioinformatics* 9:307. Within-stratum permutation importance.
- Hand, D. J., Till, R. J. (2001). "A simple generalisation of the area under the ROC curve for multiple class classification problems." *Machine Learning* 45:171–186. Pairwise multiclass AUC, the unstratified relative of the within-cell AUC.
- Kull, M., Flach, P. (2015). "Novel decompositions of proper scoring rules for classification: score adjustment as precursor to calibration." *ECML PKDD*. Grouping loss in the proper-score partition.
- Alexandari, A., Kundaje, A., Shrikumar, A. (2020). "Maximum likelihood with bias-corrected calibration is hard-to-beat at label shift adaptation." *ICML*. Calibration as a prerequisite for prior correction, which parallels the confidence-matching protocol.
- Garg, S., Wu, Y., Balakrishnan, S., Lipton, Z. (2020). "A unified view of label shift estimation." *NeurIPS*.
- Hong, Y., et al. (2021). "Disentangling label distribution for long-tailed visual recognition." *CVPR*; and Zhang, Y., Hooi, B., Hong, L., Feng, J. (2022). "Self-supervised aggregation of diverse experts for test-agnostic long-tailed recognition." *NeurIPS*. Long-tail evaluation across several test label distributions (W5).
- Kang, B., et al. (2020). "Decoupling representation and classifier for long-tailed recognition." *ICLR*. Classifier-level rebalancing recovers much of long-tail gains, the long-tail analogue of the group-level finding.
- Sagawa, S., Koh, P. W., Hashimoto, T., Liang, P. (2020). "Distributionally robust neural networks for group shifts." *ICLR*. Waterbirds/CelebA as an input-grounded grouping (W2).
- Cadene, R., et al. (2019). "RUBi: Reducing unimodal biases for visual question answering." *NeurIPS*; Clark, C., Yatskar, M., Zettlemoyer, L. (2019). "Don't take the easy way out: ensemble based methods for avoiding known dataset biases." *EMNLP*. Debiased VQA models that would make a natural W2 audit.
- Hébert-Johnson, U., Kim, M., Reingold, O., Rothblum, G. (2018). "Multicalibration." *ICML*; Kallus, N., Zhou, A. (2019). "The fairness of risk scores beyond classification: bipartite ranking and the xAUC metric." *NeurIPS*. Within-group versus between-group accounting in fairness.
- Gardner, M., et al. (2020). "Evaluating models' local decision boundaries via contrast sets." *Findings of EMNLP*. Dataset-side within-group counterfactuals.

---

## Questions for Authors
1. Do you agree that ∆R̂ = R̂(q1) − R̂(q0), where R̂ is each model's within-cell label-permutation importance? If so, would you endorse a per-model leaderboard column instead of pairwise splits? What would be lost?
2. Can you name one decision about TDE, IETrans or CLIP that the split makes and that the logit-adjusted control plus the within-cell AUC would not? Is the label-shift reversal of CLIP over geometry that decision, and could you state it prospectively?
3. In the CIFAR-100-LT and 20 Newsgroups studies, the grouping is a function of the label. How much of the "group-level" part is superclass recognition? Would you expect the CB/DRW conclusions to survive an input-observed grouping?
4. Who should declare the grouping for a public SGG leaderboard, and how should a change in the grouping be versioned so that old and new splits stay comparable?

---

## Minor Issues
- §6 "Beyond scene graphs" mentions "label-derived superclasses" but not the consequence, namely that the grouping is no longer observed by both models. One clause would prevent over-reading.
- The supplement uses "transported gain" and "within-group covariance gain"; the main text uses "group-level" and "case-level" (mapped in Supp. A and Table 4). Prefer the neutral supplementary names in Figure 1 and the reporting standard (see W10).
- Supp. N.5 says "the decomposition supplies ... how much of a long-tail gain is real". "Real" implies that group-level gains are not, which the paper itself disclaims a few lines earlier.

---

## Recomputation (read-only; scratch under `panel_R3/`)
- **CLIP split.** I recomputed the raw CLIP-versus-geometry split from `data/vg_visual/vg_visual_models.npz` with `wager.decompose_gain`. Result: ∆T −0.04642, ∆P −0.05282, ∆R +0.00640, CI [0.00513, 0.00767], coverage 99.01%. This matches Supp. Table 7.
- **Per-model permutation importance.** I computed it independently of the estimator, as the observed quadratic score minus the score against the other labels in the same cell (all pairs i≠j). Results: class-only −0.00000, geometry 0.01023, CLIP 0.01663. Their difference, 0.00640, equals ∆R̂. The difference of within-cell permuted scores, −0.05282, equals ∆P̂. This confirms W1.
- **Label heterogeneity.** In the same audit, 2.5% of identified relations sit in label-homogeneous cells. The relation-weighted mean within-cell Gini impurity is 0.449, and the mean majority-label share is 0.686. This is the heterogeneity statistic Supp. K recommends but the main text does not report.
- **Number checker.** I ran `python experiments/verify_manuscript_numbers.py --driver cvpr2027/main.tex`: "all 298 manuscript numbers trace to committed results".
- **Headline ratios** (correct):
  - TDE group share 0.0841/0.0972 = 86.5%.
  - IETrans group share 0.2143/0.2204 = 97.2%.
  - Logit adjustment recovers 0.0941/0.0972 = 96.8% of TDE's gain.
  - Its R@50 cost is 0.0175/0.2024 = 8.6% of TDE's.
  - 20NG DRW transported share is 98.65%.
- No repository file was modified.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | Review criteria framework §1; R3 configuration (new tool vs known decomposition) | PARTLY_MEETS | `text: §2 "All of these characterise a single model..."`; recomputation | The SGG audits are new and valuable. The decomposition is a stratified two-model Yates split and a difference of conditional permutation importances, neither of which is acknowledged (W1, W7). | Novelty relative to the SGG literature itself is R2's remit. | Yes: the contribution statement needs rewriting. |
| Methodological Rigor | Framework §1 | NOT_ASSESSED | — | R1's remit. From my angle, the controls are well designed (S1). | Outside the seat. | No |
| Evidence Sufficiency | Framework §2.1 External validity | PARTLY_MEETS | `text: Supp. N.5 "...label-derived grouping..."` | Evidence for SGG is strong. Evidence that the lessons generalise is weak: label-derived groupings, and an uncalibrated single-seed text study (W2, W8). | Depends on how strongly the authors keep the generality claim. | Yes |
| Argument Coherence | Framework §1 | MEETS | `table: Table 1` | The conclusions about TDE and IETrans follow from the control-plus-AUC chain. Framing overstates what the split alone decides (W4). | Logic audit is the DA's remit. | Partly |
| Writing Quality | Framework §1 | MEETS | `figure: Figure 1` | Clear and precise. Figure 1's caption invites misreading (W10). | — | No |
| Literature Integration | R3 configuration (adjacent fields) | PARTLY_MEETS | `absence: §2 Related work — expected permutation-importance/model-reliance and test-agnostic long-tail/label-shift evaluation; checked §2, §3, Supp. A–Q, references` | Strong on forecast verification and VQA bias. Missing the closest adjacent constructions (W1, W5). | Systematic coverage is R2's remit. | Yes (via Originality) |
| Significance & Impact | Framework §1; R3 configuration (practical payoff, misreading risk) | PARTLY_MEETS | `text: §7 Conclusion "the declared grouping and its coverage..."` | Clear SGG payoff: the LA control, per-predicate accounting and label-shift exposure. The reporting standard as written risks spreading a misreadable column (W3). The per-model form would raise adoptability (W1). | Adoption by benchmarks is speculative. | Yes |

**Recommendation rationale.** The decision-bearing items that remain unresolved are Originality (W1, W7), external-validity evidence (W2) and Significance via the reporting standard (W3, W4). All are repairable: W1, W3, W4 and W7 by rewriting and one proposition, and W2 by one input-grounded non-SGG audit or by rescoping the generality claim. The SGG findings themselves are well supported and reproducible. On the CVPR scale this is **Weak Accept** (confidence 3). On the skill scale it is **Major Revision**, because the contribution statement and reporting standard need substantive revision before the paper is ready.
