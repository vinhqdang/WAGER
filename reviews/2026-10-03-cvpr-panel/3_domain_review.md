# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission (anonymous, Paper ID *****)
- **Review Date**: 2026-10-03
- **Review Round**: Round 1 (pre-submission simulated panel, mode `full`)

---

## Reviewer Information

### Reviewer Role *
Peer Reviewer 2 (Domain), internal role `R2`

### Reviewer Identity *
I work on scene graph generation (SGG) and know the unbiased-SGG literature well: MOTIFS, VCTree, KERN, TDE, BGNN, PE-Net, IETrans and NICE; re-weighting, re-sampling and logit adjustment; the R@K, mR@K, ng-mR@K, zR@K and F@K metrics and the published critiques of them; and the PredCls / SGCls / SGDet protocols in the Scene-Graph-Benchmark.pytorch family of codebases.

### Review Focus *
I ask three things. Does the SGG community already know what this paper shows? Is TDE described correctly, and is the paper placed correctly in the SGG and VQA debiasing literature? Which comparisons, protocols and references would a CVPR SGG reviewer demand, and can one author get them done with public checkpoints in the six weeks before the deadline? Statistical validity of the estimator is Reviewer 1's remit, so I leave it aside.

---

## Overall Assessment *

### Recommendation *
- [ ] **Accept**
- [ ] **Minor Revision**
- [x] **Major Revision**
- [ ] **Reject**

**CVPR scale: Weak Reject** for the manuscript as it stands. It maps to the skill's **Major Revision**. If the top three remedies below are done, I would expect a domain reviewer to move to **Borderline or Weak Accept**.

### Confidence Score *
**4.** SGG evaluation and the TDE codebase are core expertise for me. I verified the TDE inference code and the public checkpoint releases during this review, as cited below. I am less sure how a mixed CVPR reviewer pool will weigh the statistics against the empirical breadth.

Confidence is an uncertainty/scope disclosure only; it never changes consensus counts, severity, decision bearing, or arbitration.

### Calibration Status
`NOT_CALIBRATED`

### Summary Assessment *
The paper proposes an exact split of the proper-score difference between two frozen models. It scores each prediction against the label of another relation in the same (subject, object) cell, which yields a group-level part and a within-cell covariance ("case-level") part, with image-clustered intervals. It applies the split to Tang et al.'s released Causal MOTIFS-SUM PredCls checkpoint. After temperature matching, the quadratic-score change from MOTIFS to MOTIFS-TDE is almost entirely group-level, with ΔR̂ = −0.00006 and an interval spanning zero. It also shows a frozen-CLIP predictor that ranks last overall but has the largest case-level gain.

From an SGG standpoint the instrument is clean, and the question is the right one. The field's main metric does reward reshuffling predicates within a pair. But the headline is close to what SGG researchers already believe: TDE trades R@K for mR@K and pushes head bias towards tail bias. It rests on one method, one base model and one protocol, and that method is post-hoc and inference-only, the case where nobody expected new recognition ability.

The paper also misdescribes how TDE works. In the released code the subtraction cancels the union-region visual branch, so TDE is not "group-level by construction". The title's question is never answered in mR units, even though the paper's own Theorem 1 allows it. And the paper does not engage with the SGG literature on label noise and predicate overlap, which a TDE author would raise first.

Every one of these gaps can be closed in six weeks, mostly with inference on checkpoints that are already public. I therefore recommend Weak Reject now, with a clear route to Borderline or better.

---

## Strengths *

### S1: Asks a question the SGG metrics genuinely cannot answer, and frames it in the field's own terms
The paper puts its finger on a real blind spot. mR@K credits a model the same whether it moves probability towards rare predicates for every (man, surfboard) relation or tells riding from carrying image by image. Recent SGG work acknowledges the trade-off but does not measure it. Framing the paper around a published ten-point gain is the right hook for CVPR.
**Evidence Anchor**: `text: §1, p.1, L.047-054 "There are two ways to raise mean recall, and the metric cannot tell them apart."`

### S2: The audit uses the authors' own released checkpoint and code, and the reproduction matches the published numbers
Both prediction sets come from one checkpoint, run through the original Scene-Graph-Benchmark evaluation, so they are aligned relation for relation. The reproduced mR@50 of 14.6 → 24.8 and zR@50 of 14.3 match Tang et al.'s published MOTIFS-SUM PredCls behaviour. An SGG reviewer will trust this setup.
**Evidence Anchor**: `text: §5, p.5, L.336-338 "the baseline reaches R@50 = 0.6612 with mR@50 = 0.1459, and TDE trades the former for the latter, reaching mR@50 = 0.2476"`

### S3: Treats calibration as part of the protocol, which matters a lot for TDE
TDE outputs differences of logits, so its "probabilities" have no natural calibration. The paper notices that the two models ship with very different temperatures (T\* = 2.50 against 0.92). It shows that the raw comparison manufactures a spurious case-level loss and reports raw and matched rows side by side. Most SGG papers never examine the scale of TDE's outputs.
**Evidence Anchor**: `table: Table 1 (p.5), raw quad. row ΔR̂ = −0.01355 against matched quad. row ΔR̂ = −0.00006`

### S4: Reports the configurations that cut against its headline
Table 1 gives all five configurations. The text says plainly that "overwhelmingly group-level" fails for two of them: raw log, and the subject-only grouping. That is honest and makes the paper harder to dismiss.
**Evidence Anchor**: `text: §5, p.5-6 "At two of the five, “overwhelmingly group-level” is false"`

### S5: Controls with a known answer on VG
When both models are functions of the class pair alone (MLP-CLASS against FREQ), ΔR̂ is exactly 0. Box geometry produces a significant case-level gain. This is a convincing sanity check that SGG readers will follow.
**Evidence Anchor**: `text: §4, p.4-5 "the case-level gain is 0.00000 with a zero-width interval"`

---

## Weaknesses *

### W1: The headline finding is close to SGG folk knowledge and rests on a single post-hoc method, base model and protocol
**Problem**: The only SGG audit is MOTIFS-SUM against MOTIFS-TDE, PredCls, one checkpoint. Yet the abstract, introduction and conclusion speak about "debiasing methods" and "the habit of reading a mean-recall gain as better recognition". TDE is also the least informative case. It is an inference-time logit subtraction applied to frozen features, so few SGG researchers would expect it to add instance-level recognition ability. The community already describes debiasing as trading head recall for tail recall. Recent work says outright that debiased methods turn "head bias" into "tail bias" (e.g., the HTCL paper, ScienceDirect PII S0262885624003883, 2024). IETrans introduced F@K precisely because methods sit at different points on the R@K/mR@K trade-off (Zhang et al., ECCV 2022, arXiv:2203.11654). A CVPR SGG reviewer will therefore read "TDE's gain is group-level" as confirming a suspicion, not as a discovery. The new and important finding would be a comparison across methods: which debiasing methods, if any, buy case-level gain, and how they rank on it. That is especially true for training-time methods (re-weighting, re-sampling, IETrans, BGNN), which do change the learned features.
**Evidence Anchor**: `table: Table 1 (p.5), every row is MOTIFS-TDE against MOTIFS-SUM on VG150 PredCls; no other debiasing method, base model or protocol appears in §5`
**Why it matters**: This is the decision-bearing gap for the domain contribution. As things stand, the empirical contribution is one data point on a 2020 method. The conclusion's recommendation that benchmarks report the split is argued from that single case.
**Suggestion** (feasible in six weeks; see the ranked remedy table below): add a multi-method table on canonical VG150 PredCls with at least:
1. post-hoc logit adjustment of the same MOTIFS-SUM baseline, τ tuned to match TDE's mR@50 (minutes of CPU time; a pure label-prior method, the natural control for TDE);
2. the TE and NIE effect types from the same released checkpoint (inference only);
3. one released training-time method, such as the IETrans Motif PredCls checkpoint (IETrans MODEL_ZOO) or BGNN (PySGG release);
4. a self-trained Motifs + re-weighting model in the same codebase (an estimated 1-2 GPU-days; not verified).

The space is there: the main text ends at the top of p.7, so about 1.5 pages of the 8-page limit are unused.
**Severity**: Major. Norm grounding: SGG debiasing papers compare across several methods and base models. Tang et al. evaluate MOTIFS, VCTree and VTransE under three protocols, as the codebase documents (`CONTEXT_LAYER` motifs/vctree/vtranse; PredCls/SGCls/SGDet). IETrans plugs into several base models.
**Confidence**: 4 (core expertise in the SGG debiasing literature)

### W2: TDE is misdescribed: in the released code it is not a group-level intervention "by construction"
**Problem**: The paper twice says that subtracting a context-only prediction is group-level by design, and calls ΔR̂ ≈ 0 confirmation that "it acts as designed". I checked the released `CausalAnalysisPredictor` (Scene-Graph-Benchmark.pytorch, `roi_relation_predictors.py`, the TDE branch and `calculate_logits`). With `FUSION_TYPE sum` the factual logits are `vis_dists + ctx_dists + frq_dists`. TDE computes `calculate_logits(union_features, post_ctx_rep, pair_obj_probs) − calculate_logits(union_features, avg_ctx_rep, pair_obj_probs)`. The frequency branch cancels; it is cell-constant in PredCls. The **union-region visual branch also cancels**, and that branch is image-specific evidence. The counterfactual `avg_ctx_rep` is itself image-dependent: in `model_motifs.py` with `ctx_average=True`, only the decoder input and edge input are replaced by running averages, while the object-context LSTM still runs on the image's features, boxes and labels. So TDE's MOTIFS-SUM logits equal the context branch minus an image-dependent counterfactual. Nothing in the method forces ΔR to be zero.
**Evidence Anchor**: `text: §5, p.5, L.379 "subtracting a context-only prediction is a group-level intervention by construction, and the split confirms that it acts as designed"`
**Why it matters**: ΔR̂ ≈ 0 is an empirical finding that needs explaining. TDE dropped the union-visual branch, a case-level signal, and something offset that loss. Calling it "by design" both understates the finding and gets TDE wrong. TDE's authors and SGG reviewers who know the code will catch it. The same claim appears in the introduction (p.1, L.085, "a group-level intervention by design").
**Suggestion**: Decompose by branch on the same checkpoint, inference only. Compare (a) baseline against baseline − frq, a pure cell-constant logit shift; (b) baseline against vis-only and ctx-only logits; (c) baseline against TDE, NIE and TE. Report which branch carries the group-level and case-level parts. Rewrite both sentences to describe what the code does. This takes a few GPU-hours and turns a factual error into a mechanistic explanation, which is a strength.
**Severity**: Major
**Confidence**: 4 (read the released source code directly; the PredCls one-hot handling of `pair_obj_probs` is inferred, but both terms use the same `pair_obj_probs`, so the frequency term cancels either way)

### W3: The title question is never answered in the field's units, though the paper's own theorem allows it
**Problem**: The paper declines to connect mR to its decomposition ("different units and we supply no bridge"). SGG readers judge by mR@K, ng-mR@K and F@K, so a paper titled "What did ten points of mean recall buy?" that answers only in quadratic-score units will feel like it changed the question. Theorem 1 is stated "for any integrable score contrast H", so the identity also holds for:
- a class-balanced quadratic or log score, weighting each case by 1/π_y. This is the proper-score analogue of mR;
- a per-relation hit contrast weighted by inverse predicate frequency, H_x(y) = w_y[1{y ∈ topK q₁(x)} − 1{y ∈ topK q₀(x)}], which is mR@K without the graph constraint at relation level.

The split would not be a proper-score statement for the second contrast, but the identity and the intervals still apply. The authors' own cached results already contain an SGG-native fact that supports their thesis and is not reported. Under the no-graph-constraint metric documented in the codebase's METRICS.md, TDE's mean recall falls: ng-mR@50 goes from 32.6 to 29.8 and ng-mR@100 from 44.3 to 39.7 (`results/sgg_audit_motifs.json`, `predcls_ng_mean_recall@K`). The ten-point mR@50 gain exists only under the graph-constrained top-1 rule. That is exactly what a within-pair argmax swap would produce.
**Evidence Anchor**: `text: §5, p.5, L.368 "Those are different units and we supply no bridge between them"`
**Why it matters**: This is the bridge between the instrument and the community's metric. Without it, SGG reviewers will say the paper changed the question.
**Suggestion**:
1. Add a short paragraph and a table row decomposing class-balanced Brier and inverse-frequency-weighted Recall@1 and Recall@5 for TDE against the baseline. This is CPU time only, on cached predictions.
2. Report R@K, mR@K, ng-mR@K, zR@K and F@K for both models in one table. F@50 can be derived from the paper's numbers: about 23.9 → 32.2.
3. State that TDE's mR gain disappears without the graph constraint.

**Severity**: Major
**Confidence**: 4 (core expertise in SGG metrics; the ng-mR numbers are read directly from the authors' committed results file)

### W4: No engagement with predicate ambiguity and label noise in VG, the first objection a TDE proponent will raise
**Problem**: The case-level part credits probability that rises on *the one annotated predicate*. On VG150, predicates overlap heavily: on / standing on / walking on / parked on, has / with, wearing / wears. Annotations are incomplete and noisy. A major strand of SGG work rests on exactly this:
- NICE (Li et al., CVPR 2022) corrects noisy positive labels;
- IETrans (Zhang et al., ECCV 2022) transfers head-predicate labels to fine-grained ones;
- DLFE (Chiou et al., ACM MM 2021) treats missing labels as reporting bias;
- PE-Net (Zheng et al., CVPR 2023) addresses semantic overlap between predicates.

Tang et al.'s own defence of TDE is that it outputs finer-grained predicates that are often right but unannotated. If TDE moves "on" to "parked on" for a car that is parked, and the label says "on", the split counts that as a case-level loss. The finding "no case-level gain" therefore rests on VG's single-label ground truth, and the paper never discusses this.
**Evidence Anchor**: `absence: §2 Related work and §7 Limitations — expected discussion of predicate semantic overlap, missing/noisy VG labels, and multi-label pairs as an alternative explanation of ΔR̂ ≈ 0; checked §1, §2, §5, §7 and supplementary App. A–K`
**Why it matters**: This is the most plausible SGG-domain alternative reading of the headline result. Unless it is addressed, reviewers sympathetic to debiasing can dismiss the audit.
**Suggestion** (in rising order of cost):
1. Multi-label scoring: treat the union of predicates annotated for the same (image, subject box, object box) as acceptable, and report how many test relations are such duplicates.
2. Rerun the split after merging predicates into a coarse hierarchy, e.g. the geometric / possessive / semantic groups used by several SGG papers, or a hand-made map of spatial specialisations into "on" or "near". If ΔR stays near zero, the ambiguity objection fails.
3. Replicate on PSG (Yang et al., ECCV 2022), whose predicate set was built to reduce this ambiguity. The OpenPSG repository releases trained IMP, MOTIFS, VCTree, GPSNet, PSGTR and PSGFormer checkpoints.

Cite NICE, IETrans, DLFE and PE-Net in §2 and §7.
**Severity**: Major. Norm grounding: label noise and predicate ambiguity in VG150 is the stated premise of NICE (CVPR 2022 oral), IETrans (ECCV 2022) and PE-Net (CVPR 2023), all verified.
**Confidence**: 4 (core expertise)

### W5: The novelty claim against prior work is too broad; the closest VQA precedents are missing
**Problem**: The paper says every existing analysis "characterises a single model" and that "none attributes the gain between two models to one route or the other". The VQA debiasing literature has already done comparative attribution of gains to non-visual mechanisms, by experiment rather than by decomposition:
- Teney et al., NeurIPS 2020 ("On the Value of Out-of-Distribution Testing: An Example of Goodhart's Law") show that VQA-CP gains can be obtained by exploiting the known shift in the test set.
- Shrestha, Kafle & Kanan, ACL 2020 ("A negative case analysis of visual grounding methods for VQA") show that grounding-based debiasing gains appear just as well with random cues, so they come from regularisation, not grounding.

These are the closest conceptual precedents for "the metric gain is not evidence of better recognition". The paper already cites VQA-CP-adjacent work (Agrawal et al. 2018; Kervadec et al. 2021) but not these two.
**Evidence Anchor**: `text: §2, p.2, L.139 "All of these characterise a single model. We attribute the gain between two."`
**Why it matters**: A reviewer who knows these papers will see the novelty sentence as overclaiming. The real novelty is the *exact, model-free decomposition* with inference, not the idea of asking whether a debiasing gain reflects better recognition. Saying so is both accurate and a stronger position.
**Suggestion**: Cite both papers. Restate the claimed gap as "no exact, inference-equipped attribution of a between-model gain to group-level and case-level parts". Use Teney et al. as motivation: the split makes their observation measurable.
**Severity**: Major. Norm grounding: CVPR reviewer guidelines ask reviewers to judge novelty against prior work, and both papers are verified and directly on point.
**Confidence**: 4 (core expertise in SGG and adjacent VQA debiasing literature)

### W6: SGG bibliography is thin and contains misattributions
**Problem**: Of 39 references, about six are SGG papers: Xu 2017, Zellers 2018, Tang 2020, Li 2022 BMVC, Li 2024 CVPR, Lu 2016. Missing:
- the origin of mR@K: KERN (Chen et al., CVPR 2019) and VCTree (Tang et al., CVPR 2019), which introduced it at the same time;
- BGNN (Li et al., CVPR 2021; bi-level re-sampling and head/body/tail-stratified mR);
- IETrans (ECCV 2022; F@K);
- GCL (Dong et al., CVPR 2022), PE-Net (CVPR 2023), NICE (CVPR 2022), DLFE (ACM MM 2021);
- logit-adjustment-style SGG debiasing such as TsCM (arXiv:2307.05276) and CAModule (arXiv:2503.17862);
- sample-level bias work (Li et al., ECCV 2024, "Fine-Grained Scene Graph Generation via Sample-Level Bias Prediction"), whose sample-level/class-level framing maps closely onto case-level/group-level.

Two attributions are inaccurate. Mean recall is credited to Tang et al. 2020 (p.1, L.034-035, "rewards getting the rare ones [29]"), though it predates TDE. "Frequency-stratified recall" is credited to Li et al. 2022 (BMVC), which proposes Independent Mean Recall (IMR) and weighted IMR (wIMR), not frequency stratification. Head/body/tail stratification is usually traced to BGNN.
**Evidence Anchor**: `text: §1, p.1, L.051-052 "Every existing remedy — frequency-stratified recall [17]"`
**Why it matters**: SGG reviewers judge whether an author knows the subfield partly from these signals. The fixes are cheap.
**Suggestion**: Add the references above (all verified in this review; see Missing Key References). Correct the two attributions. Organise §2's SGG paragraph by family: inference-time causal or post-hoc (TDE, DLFE, logit adjustment), training-time re-balancing (re-weighting, BGNN re-sampling, GCL), and label-centric (IETrans, NICE).
**Severity**: Minor
**Confidence**: 5 (core expertise; citations verified during review)

### W7: PredCls only, although SGCls and SGDet checkpoints for the same model are public
**Problem**: Tang et al. release Causal MOTIFS-SUM checkpoints for **PredCls, SGCls and SGDet** (Scene-Graph-Benchmark.pytorch README). The paper audits only PredCls. SGG reviewers routinely ask for all three. There is a conceptual subtlety the paper should face. In SGCls and SGDet the ground-truth class pair is not observed by the models. However, TDE alters only the relation logits, so the baseline and TDE share *identical object predictions*. The predicted pair is therefore a grouping both models observe, which keeps the split well defined on relations matched to ground truth.
**Evidence Anchor**: `text: §5, p.5 "Tang et al. [29] release a causal MOTIFS PredCls checkpoint"`
**Why it matters**: It is cheap, high-signal breadth evidence. The SGCls case also tests whether the conclusion holds once object recognition is uncertain.
**Suggestion**: Run both SGCls and SGDet checkpoints with `EFFECT_TYPE none/TDE` (inference only, a few GPU-hours each). Group by the shared predicted pair, restricted to relations matched to ground truth, and report coverage. Even one SGCls row in Table 1 helps.
**Severity**: Minor. Norm grounding: the three-protocol norm comes from method papers, and this is an evaluation paper whose claim is explicitly scoped to PredCls.
**Confidence**: 4 (checkpoint availability verified from the official README)

### W8: The CLIP "ranked last by every metric" claim rests on a home-built three-model pool on a reconstructed split, and the main text says otherwise
**Problem**: §4 says the controlled predictors are trained "on the VG150 PredCls split". The supplementary (App. J.1) says they are trained and audited on a VG150-*style* reconstruction with a 70/30 split, not the canonical release. §6's CLIP comparison adds a third constraint: a 100,000-relation subsample. "Every aggregate measure ranks last" therefore refers to three non-SGG predictors (FREQ-like MLPs and a frozen-CLIP MLP), none of which is a published SGG model. SGG readers will not treat this as a statement about SGG models.
**Evidence Anchor**: `text: §4, p.4, L.305-306 "We train predicate classifiers on the VG150 PredCls split whose inputs we control"`
**Why it matters**: It is a factual inconsistency between paper and supplementary, and it inflates how general the "reversal" sounds.
**Suggestion**: In the main text, call it a VG150-style reconstruction and give the reason. Retitle §6 to name the pool, e.g. "The model the aggregate metrics rank last among three controlled predictors". Optionally replace it with a canonical-split comparison: the MOTIFS-SUM visual branch against its frequency branch from the same checkpoint (see W2) gives a "pixels against prior" contrast on a real SGG model at no training cost.
**Severity**: Minor
**Confidence**: 4

### W9: How the background class is handled for the audited distribution is not stated in the paper
**Problem**: The Scene-Graph-Benchmark relation head produces a 51-way softmax that includes background. The audit script drops the background column and renormalises (`experiments/run_sgg_audit_wager.py`, docstring and `load()`), but neither the paper nor the supplementary says so. TDE subtracts logits for the background class too. Background mass can differ systematically between the two models and across cells, so renormalisation interacts with the temperature fit and with the group-level/case-level split.
**Evidence Anchor**: `absence: §5 and Table 1 caption — expected a statement of how the 51-way output (with background) is turned into a 50-way predictive distribution; checked §5, Table 1, supplementary App. E (implementation)`
**Why it matters**: SGG reviewers who know the codebase will ask. If the result is sensitive to this choice, the headline is fragile.
**Suggestion**: State the rule in one sentence. Add a sensitivity row in the supplementary: fit the temperature on the 51-way logits, then condition on non-background.
**Severity**: Minor
**Confidence**: 4

---

## Ranked remedies (by expected impact on an SGG reviewer, all feasible in six weeks for one author with cloud GPUs)

| Rank | Remedy | Addresses | Compute / effort (estimates, not verified) | Public resource (verified this review) |
|---|---|---|---|---|
| 1 | **Multi-method audit table on canonical VG150 PredCls**: TDE, TE, NIE; post-hoc logit adjustment of the MOTIFS-SUM baseline with τ matched to TDE's mR@50; ≥1 released training-time method (IETrans-Motif PredCls; BGNN); one self-trained Motifs + re-weighting model. Rank methods by ΔR̂ with intervals. | W1 (and novelty) | Inference: hours. Logit adjustment: CPU minutes. Re-weighting Motifs: ~1-2 GPU-days. | Tang release (MOTIFS-SUM PredCls/SGCls/SGDet); IETrans MODEL_ZOO (Motif PredCls/SGCls/SGDet); PySGG README (BGNN VG checkpoint); SGG-Benchmark (Maelic) MODEL_ZOO (Motifs, VCTree, PE-Net, SHA-GCL and others) |
| 2 | **Branch-level decomposition of TDE** (baseline − frq; vis-only; ctx-only; TDE/NIE/TE) and corrected description of TDE | W2 | GPU-hours, same checkpoint | Tang release + code |
| 3 | **mR-unit bridge**: class-balanced Brier and inverse-frequency-weighted hit contrast decompositions; full R/mR/ng-mR/zR/F@K table; report that ng-mR@50 falls 32.6 → 29.8 under TDE | W3 | CPU minutes on cached predictions | Authors' own `results/sgg_audit_motifs.json` |
| 4 | **Label-ambiguity robustness**: multi-label scoring for duplicate pairs; coarsened predicate hierarchy; optional PSG replication | W4 | CPU minutes; PSG inference a few GPU-hours | OpenPSG model zoo (IMP, MOTIFS, VCTree, GPSNet, PSGTR, PSGFormer) |
| 5 | **SGCls/SGDet rows** using the shared predicted pair as grouping | W7 | Few GPU-hours | Tang release |
| 6 | Re-position novelty against Teney 2020 / Shrestha 2020; expand and correct SGG bibliography | W5, W6 | Writing, 1-2 days | — |
| 7 | Fix split description; rescope §6 title; state background handling | W8, W9 | Writing, hours | — |

Remedies 1 to 3 together turn the paper from "TDE is group-level", which SGG reviewers will find unsurprising, into "here is which SGG debiasing methods buy recognition and which buy redistribution, measured in mR's own terms". That is a finding the community does not have and would cite.

---

## Detailed Comments *

### Title & Abstract
- The title promises an answer in mR terms that the paper explicitly withholds (W3). Either supply the bridge, or retitle to the proper-score claim.
- "Debiasing methods for scene graph generation are judged by mean recall" (Abstract, L.001) is dated. Since 2022 the field reports R@K, mR@K and F@K together, and IETrans introduced F@K precisely to judge the trade-off.

### Introduction
- The two routes to raising mR are explained well (L.047-054). That paragraph is the paper's best domain writing.
- The claim at L.085 that TDE is group-level "by design" needs correcting (W2).
- The contributions list frames the TDE audit as the lead contribution. With one method, that rests on the thinnest evidence in the paper (W1).

### Literature Review / Theoretical Framework
- **Coverage**: the forecasting and statistics lineage (Murphy, DeGroot–Fienberg, Bröcker, Yates, Diebold–Mariano, DeLong) is covered carefully. The SGG lineage is skeletal (W6), and the closest VQA precedents are missing (W5).
- **Integration**: the SGG paragraph lists papers rather than synthesising them. It never sorts debiasing methods by mechanism. That sorting is what would let the paper predict which methods should have a case-level gain, which turns the audit into a hypothesis test.
- **Research gap**: real, but claimed too broadly (W5).

### Methodology / Research Design (domain aspects only)
- Grouping by the ordered (subject, object) class pair is the natural SGG choice and matches the MOTIFS frequency baseline. The paper should say that in PredCls this is exactly the input of the MOTIFS frequency branch (`frq_dists`). That makes the group-level part interpretable as "what the frequency branch could in principle produce", a framing SGG readers will recognise.
- PredCls only (W7). Background handling not stated (W9). Multi-predicate pairs not discussed (W4).

### Results / Findings
- The reproduction is credible (S2).
- TDE's R@50 (45.9) and the ng-mR figures are in the results file but not in the paper, though they directly support the thesis (W3).
- The matched log row shows a significant positive ΔR̂ of +0.044. The SGG reading of that number, a small case-level gain under the log score, deserves one sentence of domain interpretation. Do any tail predicates drive it? A per-predicate breakdown of ΔR̂ for the top-10 and bottom-10 predicates would be very informative to SGG readers. It costs CPU minutes.

### Discussion / Limitations
- §7 is honest about dependence on the grouping and on calibration. It does not discuss label ambiguity (W4), which in SGG is the most important limitation.

### Conclusion
- "We suggest that benchmarks … report the split beside the headline metric" (L.470-473) is a reasonable proposal. It would be far more persuasive with a multi-method table showing that the split ranks methods differently from mR (W1).

### References
- See W6 and Missing Key References.

---

## Missing Key References
All of the following were verified to exist during this review (search results or official pages). Metadata is given only as far as it was verified.

- **Chen et al., "Knowledge-Embedded Routing Network for Scene Graph Generation", CVPR 2019** (KERN): introduced mR@K together with VCTree.
- **Tang et al., "Learning to Compose Dynamic Tree Structures for Visual Contexts", CVPR 2019** (VCTree): introduced mR@K together with KERN; a standard second base model.
- **Li, Zhang, Wan, He, "Bipartite Graph Network with Adaptive Message Passing for Unbiased Scene Graph Generation", CVPR 2021** (BGNN): bi-level re-sampling, a training-time debiasing method with a released checkpoint.
- **Zhang et al., "Fine-Grained Scene Graph Generation with Data Transfer", ECCV 2022** (IETrans, arXiv:2203.11654): introduces F@K; label-transfer debiasing; released Motif checkpoints for all three protocols.
- **Li, Chen, Huang, Zhang, Zhang, Xiao, "The Devil is in the Labels: Noisy Label Correction for Robust Scene Graph Generation", CVPR 2022** (NICE): label noise in VG.
- **Zheng, Lyu, Gao, Dai, Song, "Prototype-based Embedding Network for Scene Graph Generation", CVPR 2023** (PE-Net): predicate semantic overlap and intra-class variation.
- **Dong et al., "Stacked Hybrid-Attention and Group Collaborative Learning for Unbiased Scene Graph Generation", CVPR 2022** (SHA-GCL; official repository title verified).
- **Chiou, Ding, Yan, Wang, Zimmermann, Feng, "Recovering the Unbiased Scene Graphs from the Biased Ones", ACM MM 2021** (DLFE): an inference-time, label-frequency-based debiasing method; the closest SGG relative of a pure group-level adjustment.
- **Li et al., "Fine-Grained Scene Graph Generation via Sample-Level Bias Prediction", ECCV 2024**: its sample-level versus class-level bias framing parallels case-level versus group-level.
- **Yang et al., "Panoptic Scene Graph Generation", ECCV 2022** (PSG / OpenPSG): a cleaner predicate set with released checkpoints, for the replication in W4.
- **Teney et al., "On the Value of Out-of-Distribution Testing: An Example of Goodhart's Law", NeurIPS 2020**: the closest conceptual precedent (W5).
- **Shrestha, Kafle, Kanan, "A negative case analysis of visual grounding methods for VQA", ACL 2020**: debiasing gains that are not grounding gains (W5).
- Logit-adjustment-style SGG debiasing: **"Unbiased Scene Graph Generation via Two-stage Causal Modeling"** (TsCM, arXiv:2307.05276) and **"A Causal Adjustment Module for Debiasing Scene Graph Generation"** (arXiv:2503.17862). Titles were verified; I did not verify venues, so cite them as arXiv unless the authors confirm a venue.
- **[UNVERIFIED search lead]**: a 2025/2026 Springer chapter titled "Rethinking the Evaluation of Scene Graph Generation" (link.springer.com/chapter/10.1007/978-981-95-5679-3_28) appeared in search results. I could not open it, so authors, venue and content are unverified. Check it before citing: it may be recent work on the same evaluation question.

---

## Questions for Authors *
1. With `FUSION_TYPE sum`, the union-visual and frequency branches both cancel in TDE's logits. How much of the baseline's case-level signal sits in the union-visual branch? Once that branch is gone, what restores ΔR̂ to about zero rather than to a clear loss? (W2)
2. What fraction of the 183,639 audited test relations belong to (image, subject box, object box) pairs annotated with more than one predicate? How does ΔR̂ change under multi-label scoring? (W4)
3. Does the ranking of debiasing methods by ΔR̂ differ from their ranking by mR@50 or F@50? If even one training-time method shows a significant case-level gain, that contrast is the paper's strongest possible result. (W1)
4. Under a class-balanced proper score, which is the proper-score analogue of mR, is TDE's change still overwhelmingly group-level? (W3)

---

## Minor Issues

### Language / Grammar
- p.1, L.034-035: "the field now leads with mean recall" is fine, but date it ("since 2019").

### Citation Format
- Mean recall is attributed to [29] Tang 2020; it should be KERN/VCTree 2019 (W6).
- [17] Li et al. 2022 is described as "frequency-stratified recall"; it proposes IMR/wIMR (W6).

### Figures and Tables
- Table 1: add columns or a companion table for R@50, mR@50, ng-mR@50 and F@50 for both models, so SGG readers can see the trade-off at a glance.
- Figure 2 combines controlled predictors (reconstructed split) and the TDE audit (canonical split) in one panel. Mark which split each row comes from.

### Layout
- The main text ends near the top of p.7, leaving about 1.5 pages of the 8-page budget unused. Use it for the multi-method table (Remedy 1).

---

## Criterion-Bound Judgements *

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | `references/quality_rubrics.md`; R2 configuration (novelty relative to unbiased-SGG literature) | PARTLY_MEETS | `table: Table 1 (p.5)`; `text: §2, p.2, L.139` | The exact between-model decomposition is new to SGG. The empirical finding about TDE is close to SGG folk knowledge, and the novelty claim omits VQA precedents. | Depends on how reviewers weigh the instrument against the finding | yes: main domain driver of Weak Reject |
| Methodological Rigor | rubric | NOT_ASSESSED | — | Reviewer 1's remit | — | no |
| Evidence Sufficiency | rubric; SGG practice of multi-method, multi-model comparison (Tang et al. codebase; IETrans) | DOES_NOT_MEET | `table: Table 1 (p.5)` | One method, one base model, one protocol for a field-level claim | Cheap to repair with public checkpoints | yes: repairable within six weeks |
| Argument Coherence | rubric | PARTLY_MEETS | `text: §5, p.5, L.379` | The core argument is coherent, but the mechanistic reading of TDE is wrong (W2) and the title's question is left unanswered (W3) | — | yes |
| Writing Quality | rubric | MEETS | `text: §1, p.1, L.047-054` | Clear, well-motivated prose; honest limitations | Writing is not my primary remit | no |
| Literature Integration | rubric; R2 configuration | DOES_NOT_MEET | `absence: §2 Related work — expected SGG debiasing families, label-noise strand, VQA precedents; checked §1, §2, §7, ref.bib` | About six SGG references; misattributions; label-ambiguity strand missing | — | yes: repairable |
| Significance & Impact | rubric; R2 configuration (will CVPR SGG reviewers find it new and important) | PARTLY_MEETS | `text: §7, p.7, L.470-473` | The proposal that benchmarks report the split could matter, but one audit does not yet show it changes conclusions about SGG methods | It would rise sharply if the multi-method table shows rank reversals | yes |

The unresolved decision-bearing criteria are Evidence Sufficiency and Literature Integration, both repairable, and Originality of the empirical finding, which Remedy 1 repairs. None is fatal. Each has a concrete remedy that is feasible before 16 November 2026, mostly using released checkpoints (Tang et al.; IETrans; PySGG/BGNN; SGG-Benchmark; OpenPSG). That is why I recommend Major Revision (CVPR: Weak Reject) and not Reject.

---

### Sources consulted during review
- Scene-Graph-Benchmark.pytorch README and source (`roi_relation_predictors.py`, `model_motifs.py`): https://github.com/KaihuaTang/Scene-Graph-Benchmark.pytorch
- IETrans MODEL_ZOO: https://github.com/waxnkw/IETrans-SGG.pytorch ; arXiv:2203.11654
- PySGG README (BGNN checkpoints): https://github.com/SHTUPLUS/PySGG
- SGG-Benchmark (Maelic): https://github.com/Maelic/SGG-Benchmark
- OpenPSG model zoo: https://github.com/Jingkang50/OpenPSG
- PE-Net repository (no checkpoints in README at time of check): https://github.com/VL-Group/PENET
- KERN (CVPR 2019): https://openaccess.thecvf.com/content_CVPR_2019/papers/Chen_Knowledge-Embedded_Routing_Network_for_Scene_Graph_Generation_CVPR_2019_paper.pdf
- VCTree (CVPR 2019): https://openaccess.thecvf.com/content_CVPR_2019/papers/Tang_Learning_to_Compose_Dynamic_Tree_Structures_for_Visual_Contexts_CVPR_2019_paper.pdf
- BGNN (CVPR 2021): https://openaccess.thecvf.com/content/CVPR2021/html/Li_Bipartite_Graph_Network_With_Adaptive_Message_Passing_for_Unbiased_Scene_CVPR_2021_paper.html
- NICE (CVPR 2022): https://openaccess.thecvf.com/content/CVPR2022/html/Li_The_Devil_Is_in_the_Labels_Noisy_Label_Correction_for_CVPR_2022_paper.html
- PE-Net (CVPR 2023): https://openaccess.thecvf.com/content/CVPR2023/html/Zheng_Prototype-Based_Embedding_Network_for_Scene_Graph_Generation_CVPR_2023_paper.html
- DLFE (ACM MM 2021): https://github.com/coldmanck/recovering-unbiased-scene-graphs
- Li et al. BMVC 2022 (IMR/wIMR): https://arxiv.org/abs/2208.01909
- Sample-level bias (ECCV 2024): https://arxiv.org/pdf/2407.19259
- Teney et al. NeurIPS 2020: https://proceedings.neurips.cc/paper/2020/hash/045117b0e0a11a242b9765e79cbf113f-Abstract.html
- Shrestha et al. ACL 2020: https://aclanthology.org/2020.acl-main.727/
- HTCL (2024): https://www.sciencedirect.com/science/article/abs/pii/S0262885624003883
- TsCM: https://arxiv.org/abs/2307.05276 ; CAModule: https://arxiv.org/abs/2503.17862
