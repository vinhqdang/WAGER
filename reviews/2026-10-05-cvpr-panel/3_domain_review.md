# Peer Review Report — Peer Reviewer 2 (Domain)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission (anonymous); repository commit 909e5a3
- **Review Date**: 2026-10-05
- **Review Round**: Round 1 (simulated pre-submission panel, `academic-paper-reviewer` v1.11.1, mode `full`)

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 2 (Domain), seat `R2`

### Reviewer Identity
I work on scene graph generation and know the unbiased-SGG literature (MOTIFS/Neural-Motifs, VCTree, TDE, PCPL, CogTree, BGNN, GCL, NICE, IETrans, PE-Net) and its metrics (R@K, mR@K, ng-mR@K, zR@K, F@K; PredCls/SGCls/SGDet). I also know the Scene-Graph-Benchmark.pytorch codebase (`CausalAnalysisPredictor`, SUM/GATE fusion, evaluator) and the open-vocabulary and VLM-based SGG work.

### Review Focus
I checked whether the TDE and IETrans audits match the released checkpoints and the official evaluator, and whether the mechanistic account of TDE is right. I also checked related-work coverage and citation accuracy, and whether two methods in PredCls support the conclusions the paper draws about the field. Finally, I read the zero-shot CLIP and label-shift results as an SGG reader would.

### Calibration and binding
Calibration status: `NOT_CALIBRATED`

criteria_binding_unavailable

The author has not confirmed a target context. My CVPR remarks are a configured perspective, not a venue-alignment determination.

---

## Overall Assessment

### Recommendation
- [x] **Major Revision** (skill scale)

**CVPR-scale rating: Borderline** (leaning Weak Reject in the current form). **Confidence: 4 / 5.**
I know the SGG side, the TDE codebase and the IETrans release well. I did not re-derive the asymptotic theory, which belongs to Reviewer 1.

Confidence only discloses uncertainty and scope. It does not change consensus counts, severity, decision bearing or arbitration.

### Summary Assessment
The paper proposes an exact two-model decomposition of a score or mean-recall gain into a group-level part, which survives shuffling labels within a subject–object cell, and a case-level covariance. It applies the split to the released causal MOTIFS checkpoint (TDE) and the released IETrans checkpoint in PredCls on VG150, adds a logit-adjustment control, and studies controlled predictors and a frozen-CLIP crop model.

The TDE audit is the strongest SGG content I have seen in a "what did debiasing buy" paper. The replay reproduces the codebase's published numbers exactly. The branch-level account (under SUM fusion TDE = ctx − ctx_avg, and ctx_avg is 99.96% a single shared vector correlated with the log prior) is correct against the code and is new to me in this form. A logit-adjusted baseline matches TDE's mR@50 split at a fraction of the R@50 cost. SGG readers will want to see that.

Four weaknesses keep it from a clear accept from the domain side:
1. The "IETrans" checkpoint is the IETrans+Rwt variant, and the comparison baseline is a different architecture. The attribution of a "case-level loss" to IETrans's relabelling is therefore not licensed.
2. The evidence is two methods, one backbone family and PredCls only. SGG debiasing papers report three backbones or more across all three protocols. Even so, the paper writes conclusions and a benchmark recommendation for "the field".
3. The verdict that TDE gained no case-level discrimination depends on the benchmark's head-heavy label mix. That mix is exactly what debiasing methods argue against. Under a within-cell-balanced mix, and under the log score, TDE shows a significant case-level gain.
4. The related work misses SGG papers that already showed post-hoc prior adjustments match debiasing methods (DLFE, RTPB). One citation has the wrong author list.

All four can be repaired, so I recommend Major Revision.

---

## Strengths

### S1: The TDE replay matches the released checkpoint and the official evaluator exactly
The replayed metrics match the official evaluator to the fourth decimal (Tab. "Official evaluator against the offline replay"). I checked them against the Scene-Graph-Benchmark.pytorch README's own table for the released causal MOTIFS-SUM PredCls checkpoint:
- `MOTIFS-PredCls-none`: R@50 66.11, mR@50 14.60. The paper gives 0.6612 / 0.1459.
- `MOTIFS-PredCls-TDE`: R@50 45.88, mR@50 24.75. The paper gives 0.4588 / 0.2476.

zR@50 for TDE is 0.1432, against the README's 14.31. The paper also models graph-constraint matching through duplicate boxes and unit-tests the rank function against the evaluator's code (supp. App. O "Replaying the evaluator"). An SGG reviewer cannot ask much more for fidelity to a released checkpoint.
**Evidence Anchor**: `table: supp. Tab. recall-validation — base 0.6612/0.1459, TDE 0.4588/0.2476 official = re-scored`

### S2: The mechanistic account of TDE is correct and grounded in the code
In `CausalAnalysisPredictor` with `FUSION_TYPE sum`, TDE's output is `calculate_logits(union, post_ctx, pair_pred) − calculate_logits(union, avg_post_ctx, pair_pred)`, so the union-visual and frequency terms cancel. The authors check this numerically (largest absolute difference 0). The branch path (drop frq → drop vis → subtract ctx_avg) adds up exactly. The energy table shows ctx_avg is 99.96% global with a 0.021-logit remainder, correlated +0.75 with log π. Together these make "TDE in PredCls is, to first order, a learned logit adjustment of the context branch" a precise and testable statement. It is also more informative than the usual "TDE removes context bias" reading.
**Evidence Anchor**: `table: supp. Tab. logit-energy — ctx(avg) global 0.9996, non-global rms 0.021, corr. with log π +0.754`

### S3: The logit-adjustment control is the right control, and the paper uses it well
LA with τ=1 changes no within-cell ranking, yet it reaches mR@50 0.2343 at R@50 0.6437. Its mean-recall split (+0.0802 group, +0.0139 case) mirrors TDE's. This is a useful baseline for the SGG community in its own right. By my computation F@50 is 0.344 for LA₁ against 0.322 for TDE. The paper also explains why a thresholded metric shows a case-level part under a pure operating-point move, which SGG papers that report "tail gains" rarely notice.
**Evidence Anchor**: `table: Tab. 1 — LA .2343, +.0941, group +.0802, case +.0139; TDE−LA case −.0008 [−.0050,+.0033]`

### S4: The per-predicate and tier analysis is what SGG readers want to see
The tiers follow the BGNN head/body/tail convention (>10k / 500–10k / <500 training instances). The per-predicate figure shows the familiar TDE pattern: `parked on` rises from 0 to 0.886 and `on` falls by 0.558, almost all group-level. I recomputed both from `results/sgg_recall_split.json`. The finding that TDE's released checkpoint recalls only `to` (0.016) among the 15 tail predicates under the graph constraint is useful, uncomfortable evidence.
**Evidence Anchor**: `figure: Fig. 3 — parked on, on, per-predicate group/case parts against LA total`

### S5: Careful handling of IETrans's test protocol
The authors noticed that IETrans's loader removes duplicate test relations (152,226 against 183,642). They mapped the two sets one-to-one and report both. On the authors' own test set the replay gives R@50 0.4858 and mR@50/100 0.3576/0.3905, which matches the IETrans paper's published Motif row to rounding (see W1 for which row).
**Evidence Anchor**: `table: supp. Tab. ietrans-protocols — IETrans's (152,226) R@50 0.4858, mR@50 0.3576, mR@100 0.3905`

### S6: Scope is stated honestly, and the robustness checks address SGG-specific confounds
The paper states that the work is PredCls-only, that the split is of micro-averaged mean recall, and that it depends on grouping and label mix. The synonym merge (32 classes) and three-family merge address the VG label-ambiguity objection that any SGG reviewer would raise first.
**Evidence Anchor**: `text: §1 "Every scene-graph result is PredCls, where object boxes and classes are given and every model sees the cell"`

---

## Weaknesses

### W1: The audited "IETrans" checkpoint is IETrans+Rwt, and the attribution to relabelling is confounded
**Problem**: The paper describes IETrans as a method that "relabels training data … within the same object pair, and adds the training log-prior at test time", and reads its 97%-group-level gain and case-level loss as properties of that relabelling. Three facts make this attribution unsafe:
- **The checkpoint is the reweighted variant.** The released checkpoint scores R@50 0.4858, mR@50 0.3576 and mR@100 0.3905 on the authors' test set. These match the **Motif-IETrans+Rwt** row of IETrans Table 1 (48.6 / 35.8 / 39.1). They do not match plain Motif-IETrans (54.7 / 30.9 / 33.6). I extracted that table from the arXiv PDF in this session. The evaluation command the authors reproduce (`cmds/50/motif/predcls/lt/combine/val.sh`, see `experiments/colab_ietrans_stage2.py` docstring) points at `OUTPATH=$EXP/50/motif/predcls/lt/combine/rwt`. That directory is the output of `train_rwt.sh` (`IETRANS.RWT True`, `WSUPERVISE.LOSS_TYPE ce_rwt`). The audited model therefore combines internal transfer, external transfer (relabelling unannotated NA pairs as positives) and a class-frequency re-weighted loss.
- **The description omits two of the three components.** It leaves out external transfer and the re-weighting entirely. A frequency re-weighted loss is a group-level intervention by design, so "97% group-level" partly restates what Rwt does.
- **The baseline is a different architecture.** It is the TDE codebase's causal MOTIFS-SUM (union-visual + ctx + frq), not IETrans's `MotifPredictor` (ctx + test-time frq). It was trained with a different train/val split (IETrans moved 5,000 training images to validation) and different settings. The quadratic −0.0162 and log −0.0544 case-level "loss" could come from Rwt, external transfer, internal transfer, or the architecture and training differences. The paper acknowledges only the last.

**Evidence Anchor**: `text: §5 "IETrans [43] relabels training data, moving general predicates to specific ones within the same object pair, and adds the training log-prior at test time"`

**Why it matters**: IETrans is half of the "two released methods" evidence. One of the three headline findings in the abstract ("loses case-level score under both proper scores") is attributed to a mechanism the experiment does not isolate.

**Suggestion**:
1. Label the model **IETrans+Rwt** throughout and describe all three components.
2. Train IETrans's own Motif baseline (`cmds/50/motif/predcls/sup/train.sh`) and the non-Rwt variant (`cmds/50/motif/predcls/lt/combine/train.sh`). Both run in the authors' released code, about 50k iterations on two GPUs each. With them, split baseline → IETrans → IETrans+Rwt within one architecture.
3. Until then, restrict the claim to "the released IETrans+Rwt checkpoint against a separately trained MOTIFS-SUM".

**Severity**: Major
**Confidence**: 5 — verified against the IETrans paper's Table 1 and the repository's `val.sh` / `train_rwt.sh` fetched in this session

### W2: Two methods, one backbone family and PredCls only cannot carry conclusions about the field
**Problem**: The conclusion states: "A ten-point mean-recall gain is two different achievements summed together, and the field's metrics report the sum". It then recommends that benchmarks report the split. The evidence is two checkpoints, both MOTIFS-family, in PredCls only. The SGG literature's own reporting norm covers several backbones and all three protocols:
- The TDE codebase ships causal MOTIFS checkpoints for SGDet, SGCls and PredCls, and its README tabulates TDE for all three (README lines 173–185).
- IETrans Table 1 reports four backbones (Motif, VCTree, GPS-Net, Transformer) across PredCls, SGCls and SGDet.

Both sources were checked in this session. A CVPR SGG reviewer would ask for, at minimum:
- **(a)** TDE on a second context model. VCTree-TDE and VTransE-TDE are one config flag away in the same codebase.
- **(b)** Two or three further debiasing families with released or easily trained checkpoints: a re-weighting or re-sampling method (BGNN bi-level sampling, GCL), a loss-based method (PCPL / CogTree), and a representation method (PE-Net).
- **(c)** SGCls and SGDet for the TDE contrast.

On (c), the paper's statement that "in SGCls and SGDet the cell is itself predicted, and the split as stated does not apply" is too strong for TDE. The baseline and TDE come from one forward pass of one checkpoint and share the same object predictions. The predicted subject–object pair is therefore a grouping both models observe, which is all Sec. 3 needs (it just "declares" the grouping). The released causal MOTIFS SGCls and SGDet checkpoints make this a direct extension.

**Evidence Anchor**: `text: §7 "A ten-point mean-recall gain is two different achievements summed together, and the field's metrics report the sum"`

**Why it matters**: Without breadth, a CVPR SGG reader will treat the paper as a careful TDE case study plus a statistical tool. That reader will not accept the field-level reading, which is what the title and conclusion imply.

**Suggestion**:
- Add at least VCTree-TDE plus two non-causal debiasing methods in PredCls.
- Add TDE in SGCls (and ideally SGDet), grouping by the shared predicted class pair and reporting coverage of matched GT relations.
- Otherwise, rewrite the conclusion to claim only what two PredCls checkpoints show.

Field norm grounded in the TDE README and IETrans Table 1, both read in this session.

**Severity**: Major
**Confidence**: 4 — core expertise: SGG evaluation practice

### W3: "No case-level discrimination gained" by TDE holds only at the benchmark's label mix and only for the quadratic score
**Problem**: The abstract and the conclusion say TDE has no case-level gain and that "no within-group discrimination was gained". The paper's own evidence is mixed:
- **Log score**: TDE's matched case-level part against the baseline is +0.04396, with CI [+0.04079, +0.04714]. It is significant in 20 of 20 calibration halves. Against LA₁ it is +0.01544, with CI excluding zero.
- **Balanced label mix**: under within-cell-uniform labels, the quadratic case-level part becomes +0.01430 [+0.01144, +0.01632] against the baseline and +0.00723 against LA₁ (supp. Tab. label-shift).
- **AUC**: the AUC "null" has CI [−0.0028, +0.0086] at the benchmark mix and [−0.0684, +0.0082] under the uniform mix. That is a failure to detect, not evidence of absence. The upper bound equals the CLIP-vs-geometry AUC gap that Sec. 6 treats as meaningful.

From the SGG side this matters especially. Debiasing methods explicitly argue that the benchmark's head-heavy predicate mix is the wrong target, and mean recall itself reweights predicates for that reason. Under the label mix that matches TDE's stated goal, the paper's own split credits TDE with case-level gain beyond the operating-point control. Sec. 5 qualifies the claim to "at the benchmark's label mix". The abstract and the conclusion do not.

**Evidence Anchor**: `table: supp. Tab. label-shift — TDE vs base, uniform within cells, case +0.01430 [+0.01144,+0.01632]; TDE vs LA₁ +0.00723`

**Why it matters**: The TDE audit is the paper's flagship result. As written, the abstract and conclusion will be read as "TDE gained no discrimination", a stronger claim than the evidence supports.

**Suggestion**:
- In the abstract, contributions and conclusion, state the verdict as conditional on the benchmark label mix and the quadratic score.
- Report the log-score and uniform-mix results alongside in the main text.
- Phrase the AUC result as "no detectable change (CI up to +0.009)".
- Discuss which label mix the SGG debiasing problem actually targets.

**Severity**: Major
**Confidence**: 4 — the numbers are the paper's own; the reading of debiasing goals is core expertise

### W4: Related work misses SGG work that anticipated the "logit adjustment matches debiasing" finding, and pads the SGG line with non-SGG citations
**Problem**: The paper presents "a one-line logit adjustment … recovers nine of the ten points … at under a tenth of TDE's cost" as a finding, and cites only Menon et al. as "outside scene graphs". Within SGG, several papers already showed that post-hoc or prior-based adjustments reach TDE-level mean recall:
- **DLFE** (Chiou et al., "Recovering the Unbiased Scene Graphs from the Biased Ones", ACM MM 2021) divides biased probabilities by estimated label frequencies at inference. IETrans Table 1 lists it at Motif PredCls R@50 52.5 / mR@50 26.9, against TDE's 46.2 / 25.5.
- **RTPB** (Chen et al., "Resistance Training using Prior Bias: Toward Unbiased Scene Graph Generation", AAAI 2022) builds the class prior into training as a resistance bias.

The paper's real contribution (the split and the demonstration that LA matches TDE's split) still stands. But the paper has to engage these and position itself against them.

The coverage of debiasing families is also thin. PCPL (ACM MM 2020), CogTree (IJCAI 2021), NICE (CVPR 2022, noisy-label correction, directly relevant to whether a VG label is the "right label on the right image"), PE-Net (CVPR 2023) and the F@K metric introduced with IETrans are all absent.

Meanwhile "the line continues [18, 25]" cites two papers that are not SGG papers: Kuang et al., spurious-correlation debiasing (arXiv:2405.15240), and Luo et al., long-tailed recognition, NeurIPS 2025. Both exist, which I checked, but neither continues the SGG debiasing line the sentence describes.

**Evidence Anchor**: `text: §2 "and, outside scene graphs, post-hoc logit adjustment [26]; the line continues [18, 25]"`

**Why it matters**: The paper's novelty relative to SGG is overstated, and SGG reviewers will notice that DLFE and RTPB are missing.

**Suggestion**:
- Cite and discuss DLFE and RTPB as SGG precedents for prior-based adjustment.
- Replace or supplement [18, 25] with SGG works (PCPL, CogTree, NICE, PE-Net).
- Mention F@K and ng-mR as existing aggregate responses.

**Severity**: Major
**Confidence**: 4 — DLFE, RTPB, PCPL, CogTree verified in IETrans Table 1 and by search in this session; NICE and PE-Net verified by search

### W5: Reference [22] has the wrong author list
**Problem**: [22], "Rethinking the evaluation of unbiased scene graph generation" (BMVC 2022), is attributed to Wei Li, Haiwei Zhang, Qijie Bai, Guoqing Zhao, Ning Jiang and Xiaojie Yuan. Those are the authors of **PPDL** (CVPR 2022). The BMVC 2022 paper, which introduced independent mean recall (IMR), is by Xingchen Li, Long Chen, Jian Shao, Shaoning Xiao, Songyang Zhang and Jun Xiao (arXiv:2208.01909).

**Evidence Anchor**: `text: References [22] "Wei Li, Haiwei Zhang, Qijie Bai, Guoqing Zhao, Ning Jiang, and Xiaojie Yuan. Rethinking the evaluation of unbiased scene graph generation"`

**Why it matters**: This is a verifiable citation error in the paper's most directly related metric-critique reference.

**Suggestion**: Correct the `li2022rethinking` entry in `cvpr2027/ref.bib`, then re-check all SGG entries against DBLP.

**Severity**: Minor
**Confidence**: 5 — verified by search in this session

### W6: Two SGG citations are mischaracterised
**Problem**: Two citations are described inaccurately:
- **Desai et al. [9]** is cited for "loss re-weighting and group-wise learning". Its method (DT2-ACBS, as listed in IETrans Table 1) is decoupled training with alternating class-balanced *sampling*.
- **PGSG [21]** is cited as showing that the metric-pathology diagnosis "recurs in open-vocabulary settings". It is an open-vocabulary SGG *method* paper, not an evaluation critique.

**Evidence Anchor**: `text: §2 "loss re-weighting and group-wise learning [9, 11]"`

**Why it matters**: SGG reviewers check how the debiasing taxonomy is described.

**Suggestion**: Describe [9] as class-balanced sampling. Either cite an actual open-vocabulary evaluation critique for the [21] claim, or reword it as "open-vocabulary methods inherit the same metrics [21]".

**Severity**: Minor
**Confidence**: 4 — core expertise; DT2-ACBS naming confirmed in IETrans Table 1

### W7: The mechanism is specific to SUM fusion, and "visual term" means the union-region term only
**Problem**: The cancellation "the visual and frequency terms enter both halves unchanged and cancel" holds for `FUSION_TYPE sum`. Under the GATE fusion that the TDE codebase also supports, the logit is `ctx · σ(vis + frq)`, nothing cancels, and the "learned logit adjustment" reading need not hold. In addition, the MOTIFS context term is itself computed from object ROI visual features. "Removing the visual term" therefore removes only union-box features, and TDE does not "remove … the image-specific visual term" in the broader sense a reader may infer.

**Evidence Anchor**: `text: §5 "In PredCls, TDE's counterfactual is to first order a learned logit adjustment of the context branch"`

**Why it matters**: Readers will generalise the mechanism to "TDE" in general.

**Suggestion**: Qualify the claim to the SUM-fusion MOTIFS checkpoint, and rename the term "union-region visual term". A one-line note on GATE fusion, or a VCTree-SUM check, would settle it.

**Severity**: Minor
**Confidence**: 4 — recalled from the codebase's `calculate_logits`; SUM vs GATE options confirmed in the README fetched in this session

### W8: Treating group-level gain as not "better recognition" ignores VG label ambiguity, which is what TDE and IETrans target
**Problem**: The introduction asserts that "only the second is better recognition". In VG the same image often legitimately supports `on` and `parked on`, and which label an annotator chose is largely not recoverable from the image. Both TDE ("more informative" scene graphs) and IETrans ("fine-grained" predicates) explicitly target moving probability from general to specific predicates within a pair. On that view, a group-level shift towards `parked on` for (car, street) is the intended improvement. A low within-cell AUC (MOTIFS 0.5705) may reflect irreducible label noise as much as poor recognition. The synonym-merge robustness check (32 classes and 3 families) partly addresses this. The framing in §1 and the conclusion does not.

**Evidence Anchor**: `text: §1 "The first is a change in the model's group-level predictions; only the second is better recognition"`

**Why it matters**: SGG readers who hold the informativeness view will reject the paper's normative reading even if they accept the decomposition.

**Suggestion**:
- Present the split as descriptive: group-level gain = predicting a different predicate mix per pair; case-level gain = image-specific discrimination.
- Discuss explicitly that under single-label annotation of ambiguous predicates (NICE; IETrans's motivation), group-level gain can be legitimate.
- Move the synonym-merge result into the main text as the response to this objection.

**Severity**: Major
**Confidence**: 3 — core expertise, but this is an interpretive disagreement rather than a factual error

### W9: The zero-shot CLIP baseline is too weak to represent "the vision–language model the audience uses"
**Problem**: The zero-shot model uses ViT-B/32, the union box and a single prompt template per predicate. It reaches 2.5% top-1 on 50 predicates, close to the uniform 2%. The literature already documents that class-name prompts with CLIP fail at fine-grained predicates and neglect spatial cues; RECODE (Li et al., NeurIPS 2023) proposes composite-cue prompts for exactly this reason. Current VLM-based SGG (e.g. PGSG [21]) fine-tunes rather than prompting zero-shot. The supplementary concludes that "the vision–language model the audience uses does not, zero-shot, rank predicates within an object pair the way a trained scene-graph model does".

**Evidence Anchor**: `text: supp. Q.4 "The vision–language model the audience uses does not, zero-shot, rank predicates within an object pair the way a trained scene-graph model does"`

**Why it matters**: The comparison supports a claim about VLMs in SGG that the experiment cannot carry.

**Suggestion**:
- Either add a stronger zero-shot baseline (prompt ensembles, ViT-L/14, separate subject/object/union crops, or a RECODE-style composite prompt), or restrict the claim to "single-prompt CLIP ViT-B/32".
- Cite RECODE and an open-vocabulary SGG model that is evaluated with the split.

**Severity**: Minor
**Confidence**: 4 — core expertise in VLM-based SGG

### W10: The "model every metric ranks last" is not a scene-graph model, but the abstract presents it as one of the headline SGG findings
**Problem**: The Sec. 6 "CLIP model" is an MLP on frozen CLIP crop embeddings plus class embeddings. It is trained on a 100k-relation subsample of a reconstructed VG150-style split that is not the canonical one. It is compared against an MLP on box geometry. Neither model is an SGG model, neither is evaluated with R@K/mR@K, and the within-cell AUC does not separate the two. The abstract and the conclusion nevertheless present it as "the converse" of the debiasing audits.

**Evidence Anchor**: `text: §7 "applied to a model every aggregate metric ranks last, it finds a case-level gain that the aggregates conceal"`

**Why it matters**: SGG readers will take "ranked last" to mean ranked last among SGG methods.

**Suggestion**: Describe it in the abstract as "a controlled frozen-CLIP predicate classifier". Ideally, run the same contrast between two real SGG models on the canonical split, for example MOTIFS against a VCTree or PE-Net checkpoint, where a case-level/aggregate disagreement would matter to the field.

**Severity**: Minor
**Confidence**: 4 — core expertise

### W11: The recall/mean-recall trade-off is not summarised in the field's standard way
**Problem**: The paper reports R@50 costs in prose ("under a tenth of TDE's cost") but no F@K. IETrans introduced F@K precisely to compare R/mR trade-offs, and F@K would let SGG readers place the three models immediately. From the paper's numbers I compute F@50 of 0.239 for the baseline, 0.322 for TDE, 0.344 for LA₁ and 0.414 for IETrans+Rwt.

**Evidence Anchor**: `absence: Tab. 1 and supp. Tab. recall-validation — expected F@50 (or F@100) per model; checked §5, Tab. 1, supp. App. O tables`

**Why it matters**: F@K would strengthen the paper's own point that LA dominates TDE.

**Suggestion**: Add an F@50/100 column to Tab. 1.

**Severity**: Minor
**Confidence**: 4 — F@K is defined and used in IETrans Table 1 (read in this session)

---

## Detailed Comments

### Title & Abstract
- The title is apt for the TDE audit. The abstract presents three findings (TDE, IETrans, CLIP). The IETrans one needs the "+Rwt" label (W1), the TDE one needs a label-mix qualifier (W3), and the CLIP one should say it is not an SGG model (W10).

### Introduction
- The motivation (mR cannot distinguish the two routes) is clear and well argued for SGG readers.
- Calling TDE "among the most cited" is fair.
- "In our evaluation of the released checkpoint" correctly distinguishes 24.8 from TDE's paper value of 25.5 mR@50. Adding one sentence that the released checkpoint's README reports 24.75 would pre-empt the obvious reviewer question.

### Literature Review / Theoretical Framework
- **Coverage**: Missing DLFE, RTPB, PCPL, CogTree, NICE and PE-Net, plus F@K (W4). The non-SGG fillers [18, 25] sit in the SGG paragraph.
- **Integration quality**: The SGG paragraph is a list. The proper-score and paired-comparison paragraphs are critically synthesised and well positioned (Yates covariance against Murphy resolution; DM and DeLong).
- **Research gap**: "All of these characterise a single model. We attribute the gain between two." This is a valid and well-stated gap for SGG. However, the gap claim should also acknowledge DLFE/RTPB-style comparisons, which do compare a debiasing method against a prior adjustment, though only on aggregates.

### Theoretical framework (domain reading)
- **Appropriateness**: Grouping by the ordered subject–object class pair is the natural cell for PredCls. It matches what the frequency baseline (MOTIFS) conditions on. Sound.
- **Application depth**: Deep. The grouping, the operating-point control and the AUC are all used to interpret the SGG results, not just named.
- **Alternatives**: Grouping by (subject, object, coarse geometry), as in spatially-aware frequency baselines, is a plausible finer cell that SGG reviewers would suggest. Appendix K discusses grouping choice in general. A concrete SGG variant would help.

### Academic Argument Quality
- **Factual accuracy**:
  - TDE replay: verified (S1).
  - TDE mechanism: correct for SUM fusion (S2, W7).
  - IETrans description: incomplete or wrong (W1).
  - Citation [22]: wrong authors (W5).
  - The tail-predicate statements (only `to` recalled, 0.016) and `parked on` / `on`: recomputed, correct.
- **Argument logic**: The step from "matched by LA at the benchmark mix" to "no within-group discrimination was gained" (W3) is the main leap.
- **Terminology**: "Zero-shot" in Q.4 clashes with SGG's zero-shot recall (zR@K, unseen triplets), which the same appendix also reports. Use "prompt-only" or "untrained-head".

### Contribution to the Field
- **Contribution**: An exact, cheap, model-free attribution of a mean-recall difference into within-pair predicate-mix change and within-pair discrimination. It comes with an operating-point control, and the paper shows that TDE's headline gain on its released checkpoint is reproduced by a ranking-preserving prior shift. For SGG this is a useful auditing tool and a sharp TDE case study.
- **Positioning**: Needs DLFE/RTPB (W4), and the IETrans attribution needs fixing (W1).
- **Overclaiming**: Field-level language (W2), the unconditional TDE verdict (W3), and the VLM claim (W9).

### Missing Key References
- Chiou, Ding, Yan, Wang, Zimmermann, Feng. *Recovering the Unbiased Scene Graphs from the Biased Ones* (DLFE). ACM MM 2021. Post-hoc label-frequency adjustment in SGG; direct precedent for the LA control.
- Chen, Zhan, Yu, Liu, Luo, Du. *Resistance Training Using Prior Bias: Toward Unbiased Scene Graph Generation* (RTPB). AAAI 2022. Prior-bias-based debiasing.
- Li, Chen, Huang, Zhang, Zhang, Xiao. *The Devil is in the Labels: Noisy Label Correction for Robust Scene Graph Generation* (NICE). CVPR 2022. Bears on W8.
- Zheng, Lyu, Gao, Dai, Song. *Prototype-based Embedding Network for Scene Graph Generation* (PE-Net). CVPR 2023. A strong recent method to audit.
- Li, Xiao, Chen, Shao, Zhuang, Chen. *Zero-shot Visual Relation Detection via Composite Visual Cues from Large Language Models* (RECODE). NeurIPS 2023. Bears on W9.
- PCPL (Yan et al., ACM MM 2020) and CogTree (Yu et al., IJCAI 2021) as debiasing families. Both are listed in IETrans Table 1; check the exact bibliographic metadata before citing.

---

## Questions for Authors
1. Can you confirm that the released IETrans PredCls checkpoint is the `combine/rwt` (IETrans+Rwt) model? Its numbers match IETrans Table 1's +Rwt row, and the `val.sh` you reproduce points at `combine/rwt`. If so, will you re-run the split with IETrans's own Motif baseline and the non-Rwt variant, so that the case-level loss can be attributed?
2. In SGCls/SGDet, the baseline and TDE share one checkpoint and therefore identical object predictions. Is there any obstacle to declaring the predicted class pair as the cell and running the split on the released SGCls/SGDet checkpoints?
3. Which label mix do you consider the right target for judging a debiasing method? Under the within-cell-uniform mix, TDE's case-level part beats both the baseline and LA₁. How should a reader reconcile that with the abstract's verdict?
4. Does the "learned logit adjustment" account survive under GATE fusion or for VCTree-TDE?

---

## Minor Issues

### Citation Format
- [22] has the wrong authors (W5). [20] BGNN page range: please verify against CVF Open Access.
- [43] IETrans should note that the evaluated model is the "+Rwt" variant wherever results are attributed.

### Terminology
- "Zero-shot CLIP" (Q.4) against SGG's "zero-shot recall" (zR@K): rename the former.
- "Visual term" → "union-region visual term" (W7).
- "MOTIFS" and "Neural-Motifs" are used interchangeably for two different predictor heads (CausalAnalysisPredictor-SUM vs MotifPredictor). Name them distinctly.

### Figures and Tables
- Tab. 1 would benefit from R@50 and F@50 columns beside mR@50 (W11).
- Fig. 2 mixes reconstructed-split predictors and canonical-split checkpoints in one panel. Mark which split each row uses.

---

## Criterion-Bound Judgements

| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | Reviewer configuration (SGG audit novelty against unbiased-SGG literature) | MEETS | `text: §2 "All of these characterise a single model. We attribute the gain between two."` | A two-model exact split with an operating-point control is new to SGG; the "LA matches debiasing" observation is partly anticipated (DLFE, RTPB) | Statistical novelty is assessed by R1 | Yes — the contribution survives, but positioning must change |
| Methodological Rigor (domain fidelity) | Reviewer configuration: faithfulness to released checkpoints and official evaluator | PARTLY_MEETS | `table: supp. Tab. recall-validation`; W1 anchor | TDE replay exact (S1); IETrans run faithful to the checkpoint but mislabelled, and baseline architecture confounded | Did not rerun the checkpoints myself | Yes — W1 |
| Evidence Sufficiency | SGG reporting norm (TDE README; IETrans Tab. 1: multi-backbone, three protocols) | DOES_NOT_MEET | W2 anchor | Two checkpoints, one family, PredCls only, against field-level conclusions | Field norm grounded in session-read sources | Yes — W2 |
| Argument Coherence | Reviewer configuration (mechanism and conclusions follow from evidence) | PARTLY_MEETS | W3 anchor; W8 anchor | TDE mechanism coherent and correct for SUM; verdict stated beyond label-mix and score dependence; normative framing contestable | W8 is interpretive | Yes — W3 |
| Writing Quality | General | MEETS | §5 "What that licenses" paragraph | Dense but precise; the SGG reader can follow; terminology clashes are minor | — | No |
| Literature Integration | Reviewer configuration (unbiased-SGG must-cite set) | PARTLY_MEETS | W4 anchor; W5 anchor | Statistics lineage excellent; SGG lineage thin, one wrong author list, non-SGG fillers | Recommended refs verified by search | Yes — W4 |
| Significance & Impact | Reviewer configuration (does it change how SGG debiasing is evaluated) | PARTLY_MEETS | `table: Tab. 1 — LA .2343 vs TDE .2476` | A sharp TDE finding and a practical tool; impact limited by breadth and by the label-mix dependence of the verdict | — | Yes, jointly with W2 |

I do not total, weight or average these judgements, and they are not mapped mechanically to the recommendation.

**Recommendation rationale**: Three criteria remain unresolved and decision-bearing: evidence sufficiency against the SGG reporting norm (W2), fidelity of the IETrans attribution (W1), and conservatism of the TDE verdict (W3). Literature integration (W4) is also unresolved. All are repairable within one revision:
- W1, W3 and W4 need relabelling, rewording and citations, plus two IETrans training runs.
- W2 needs roughly two to four further audits, which existing codebases and released checkpoints make feasible.

The strengths of the TDE audit (S1–S4) do not offset these. Hence Major Revision (skill scale) and Borderline (CVPR scale).

---

## Recomputation log
- Ran `python experiments/verify_manuscript_numbers.py --driver cvpr2027/main.tex`: "all 298 manuscript numbers trace to committed results".
- Recomputed:
  - group-level shares: 0.0841/0.0972 = 86.5% (TDE) and 0.2143/0.2204 = 97.2% (IETrans);
  - F@50 for base, TDE, LA₁, LA.5 and IETrans from the reported R@50/mR@50;
  - per-predicate recall for `parked on` (0 → 0.886), `on` (0.813 → 0.254) and `to` (0.016) from `results/sgg_recall_split.json`.
- Externally cross-checked:
  - the TDE replay against the Scene-Graph-Benchmark.pytorch README table (released causal MOTIFS-SUM PredCls, none/TDE);
  - the IETrans replay against IETrans (ECCV 2022) Table 1, extracted from the arXiv PDF;
  - the IETrans release against its MODEL_ZOO.md and `cmds/50/motif/predcls/lt/combine/{val,train,train_rwt}.sh`;
  - references [18], [21], [22] and [25], plus the recommended DLFE, RTPB, NICE, PE-Net and RECODE, by web search.
- Scratch files: `/tmp/claude-0/-home-user-WAGER/06889eb3-4869-50f6-bd62-a68f44e45a32/scratchpad/panel_R2/` (IETrans PDF text, SGB README). No repository file was modified apart from this report.
