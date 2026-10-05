# Peer Review Report — Journal-Fit Reviewer (EIC seat)

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission (anonymous; repository commit 909e5a3)
- **Review Date**: 2026-10-05
- **Review Round**: Round 1 (simulated pre-submission panel, skill `academic-paper-reviewer` v1.11.1, mode `full`)

---

## Reviewer Information

### Reviewer Role
Journal-Fit Reviewer (internal role `EIC`)

### Reviewer Identity
A CVPR area chair for scene understanding and evaluation. I have handled scene-graph-generation (SGG) method papers, SGG debiasing papers, and benchmark-analysis and evaluation-metric papers at CVPR, ICCV and ECCV.

### Review Focus
Whether the paper fits the CVPR main conference. How significant and original it is compared with the SGG-debiasing and evaluation literature. Whether the empirical breadth is what CVPR reviewers expect, and how well the contribution is framed in 8 pages. What scores three typical CVPR reviewers would likely give, and what most likely sinks or carries the paper. I discuss methodology only where it changes how reviewers will see the headline result.

### Calibration and binding
- Calibration status: `NOT_CALIBRATED`
- `criteria_binding_unavailable`. No author-confirmed target context was supplied. The CVPR remarks below come from a configured reviewer perspective; they are not a venue-alignment determination.

### Recomputation performed (read-only)
1. I ran `python experiments/verify_manuscript_numbers.py --driver cvpr2027/main.tex`. Result: "all 298 manuscript numbers trace to committed results". 164 of them are printed in the paper itself. `git status` was the same before and after the run.
2. I recomputed the two headline shares from `results/sgg_recall_split.json` and `results/sgg_recall_split_ietrans_vs_none.json` (key `gc@50`, `mean_recall`):
   - TDE: group-level 0.08411 / total 0.09715 = 86.6%. The paper reports "87%".
   - IETrans: 0.21433 / 0.22036 = 97.3%. The paper reports "97%".
   - Logit-adjusted control (LA) minus TDE: TDE−LA case-level part −0.00084. The paper reports −0.0008.
3. I rendered pages 1, 6 and 7 of `cvpr2027/paper.pdf` to check how Figs. 1–3 read.

I did not re-run any model or the pytest suite. I did not re-derive the theorems.

---

## Overall Assessment

### Recommendation (skill scale)
**Major Revision.** In CVPR terms: not ready for the November deadline as framed. It could be competitive with the changes in W1–W4.

### CVPR-scale rating
**Borderline**. Confidence: **4/5** (core area: SGG evaluation and debiasing; I am less expert in U-statistic asymptotics).

Confidence is an uncertainty and scope disclosure only. It does not change severity, decision bearing or arbitration.

### Expected score distribution from three typical CVPR reviewers
This is a forecast of reviewer *perception*, not a base rate:

| Likely reviewer | Expected rating | What drives it |
|---|---|---|
| SGG methods reviewer (has trained MOTIFS/VCTree, knows the TDE/BGNN/PE-Net line) | **Weak Reject** (range Reject–Borderline) | "Only PredCls, only MOTIFS, two methods." "That TDE ≈ prior subtraction is folk knowledge (post-hoc frequency correction already matches debiasers)." "No new method, so what do I do with this?" |
| Evaluation / benchmark-analysis reviewer (likes metric papers, reads the supplement) | **Weak Accept** (range Borderline–Accept) | An exact, cheap, model-free split of mR itself. Honest nulls. A released-checkpoint replay that matches official numbers to 4 decimals. Validation against designed ground truth. This reviewer will still flag dependence on confidence matching and the operating-point control. |
| Generalist vision reviewer | **Borderline / Weak Reject** | Dense, number-heavy prose. The abstract is about 270 words with about 15 numbers. Interpretation leans on 15 appendix pointers. The CLIP "converse" result undercuts what case-level gain is supposed to mean. |

The modal outcome is **WR / BL / WA**. That lands in the AC discussion zone, and the rebuttal cannot fix the breadth complaint. Most likely to sink the paper: W1 (breadth), together with W3 (the TDE finding read as anticipated). Most likely to carry it: S2 and S4 (a split of the field's headline metric, applied to a famous released checkpoint and replayed exactly), plus Fig. 1.

### Summary Assessment
The paper proposes an exact decomposition of the score difference between two frozen models. It scores each prediction against the label of another case in the same declared group (here the subject–object class pair). This splits the gain into a group-level part and a case-level within-group covariance. The split holds for Bregman scores and for label-weighted hit rates, which includes micro-averaged mean recall. Intervals are image-clustered.

On TDE's released MOTIFS PredCls checkpoint, 87% of the mR@50 gain is group-level. A ranking-preserving logit adjustment matches TDE's case-level part, and the within-cell AUC shows no change. For IETrans, the gain is 97% group-level with a case-level loss on proper scores.

The idea is clean, well validated where ground truth is known, and unusually reproducible. The question is timely for a community that ranks debiasing methods by mR. As a CVPR submission, though, its empirical footprint is narrow: two methods, one backbone, PredCls only, VG150 only. Its central SGG finding will strike many SGG reviewers as partly anticipated by post-hoc frequency-correction work the paper does not discuss. The headline also depends on configuration in ways the paper concedes ("holds at the configuration we argue for").

The writing is precise but very dense for an 8-page vision paper. I recommend Major Revision. Broaden the audit into a multi-method, multi-backbone table, position the paper against post-hoc SGG debiasing, and reframe the TDE headline so that it survives the label-shift and log-score results already in the paper.

---

## Strengths

### S1: A sharp, timely question with a memorable visual hook
The title question, together with Fig. 1 (two VG relations sharing (man, surfboard) with labels swapped), explains the method in one glance. This is rare for an evaluation paper and will help with both reviewers and readers. The question fits a community that ranks debiasing methods almost entirely by mR.
**Evidence Anchor**: `figure: Fig. 1 — within-group relabelling of two (man, surfboard) relations, with the ΔT = ΔP + ΔR panel`

### S2: The split applies to mean recall itself, not only to a proxy score
Many decomposition papers split a proper score that nobody in the target community reports. This paper shows that the identity needs only a contrast that can be evaluated at a counterfactual label. It then splits micro-averaged mR@K, the metric SGG papers actually compete on, by replaying the benchmark's matching rules on cached scores. This is what makes the paper relevant to CVPR rather than only to a statistics audience.
**Evidence Anchor**: `text: §3 "Splitting mean recall" (p.4, l.291–300) "Nothing in Theorem 1 or the estimator uses properness"`

### S3: Validation where the answer is known
Sec. 4 runs several checks:
- Class-pair-only models give an algebraically zero case-level part.
- Box geometry produces a significant case-level gain that no aggregate score isolates.
- Simulations show the expected behaviour for a prior-only change, a within-cell shortcut and a calibration-only change. The calibration-only case is shown both before and after confidence matching.
- Clustered intervals cover at 94.0%.

Evaluation-metric papers at CVPR rarely validate against designed ground truth. Reviewer B will value this.
**Evidence Anchor**: `text: §4 (p.5, l.368–374) "That zero is algebraic, not empirical"`

### S4: Released-checkpoint audit with exact evaluator replay, an honest control and a mechanism
The authors re-run TDE's own released checkpoint and reproduce the official numbers to the fourth decimal. They add a training-free operating-point control (logit adjustment, τ = 1). They explain the result mechanistically: the averaged-context term is "to 99.96% of its energy, one vector", correlated +0.75 with the log-prior. I recomputed the 87% and 97% shares and the TDE−LA case-level value from the results files. This combination of a famous method, its own checkpoint, an exact replay and a "why" is the most CVPR-relevant part of the paper.
**Evidence Anchor**: `text: §5 (p.5, l.399–401) "The replay reproduces the official numbers to the fourth decimal"`

### S5: Candid scoping
The "What is not claimed" paragraph and the Limitations section state the PredCls restriction, the dependence on the grouping and on calibration, the shortcut exposure (an unrecorded covariate correlated at 0.061 would account for the whole controlled-predictor case-level gain), and the need for full score vectors. Reviewers tend to reward this. It also protects the paper against "overclaiming" reviews.
**Evidence Anchor**: `text: §1 (p.3, l.127–131) "Every scene-graph result is PredCls"`

### S6: Reproducibility well above CVPR norms
Every printed number traces to a committed results file through an automated checker. I ran it: 298 of 298 numbers pass. Scripts regenerate predictions, and the supplement is 31 pages. For an analysis paper whose value depends on trust in the numbers, this is a real asset. It should be stated in one sentence in the main paper.
**Evidence Anchor**: `dataset: results/*.json with experiments/verify_manuscript_numbers.py — 298/298 manuscript numbers trace (recomputed this review)`

---

## Weaknesses

### W1: Empirical breadth is below what CVPR reviewers expect of an audit paper
**Problem**: Every SGG conclusion rests on PredCls, one backbone (MOTIFS), one dataset (VG150) and two debiasing methods (TDE and IETrans). The pixel-reading "converse" comes from small predicate classifiers trained on a reconstructed split, not from an SGG model. SGG reviewers routinely expect results across MOTIFS / VCTree / Transformer backbones and the PredCls / SGCls / SGDet protocols. For an evaluation paper they expect a table of many methods. TDE itself is released in the standard codebase for more than one backbone, and many debiasing methods have public checkpoints.
**Evidence Anchor**: `text: §1 "What is not claimed" (p.3, l.127–130) "Every scene-graph result is PredCls, where object boxes and classes are given"`
**Why it matters**: This is the single most likely reason for Reject / Weak Reject scores, and it cannot be addressed in a rebuttal. With only two methods, the paper reads as a case study of TDE rather than a tool the field will adopt. The claim that the split "separates methods" rests on n = 2.
**Suggestion**: Add one main-paper table with the split (mR@50 group / case with CI, ΔAUC, and case-level part against the LA control) for 8–12 publicly released PredCls checkpoints across at least two backbones. Candidates: re-weighting, BGNN, PE-Net-style, other relabelling and post-hoc methods. Even one compact column per method would change the paper's character. For SGCls/SGDet, consider conditioning on the ground-truth cell among correctly detected pairs and reporting coverage, or explain in one paragraph why this is out of scope beyond the current sentence. Cost: mostly inference and replay, since the estimator is O(NK).
**Severity**: Major
**Confidence**: 5 — core expertise: SGG benchmarking norms at CVPR/ICCV/ECCV

### W2: The TDE headline depends on configuration, and the paper's own robustness results pull against it
**Problem**: The abstract and conclusion state that no within-group discrimination was gained behind TDE's points. The body shows several results that complicate this:
- Against the baseline, TDE's mR case-level part is +0.0130 with an interval excluding zero. The "null" exists only against the LA control.
- Against that control, the two proper scores disagree in sign, and both intervals exclude zero (−0.0040 quadratic, +0.0154 log).
- Under the paper's own label-shift reweighting, TDE's null becomes +0.01430 [+0.01144, +0.01632], and the authors conclude that "TDE gains discrimination between some predicate pairs and loses it between others".
- The paper concedes that the proper-score headline holds only at the configuration the authors argue for.

A careful reviewer will put these together and conclude that the headline is a configuration-specific reading.
**Evidence Anchor**: `text: §1 (p.3, l.141–143) "headline holds at the configuration we argue for, not at every configuration"`
**Why it matters**: The paper's SGG significance depends on the TDE verdict. Each qualification is reported honestly, but they are spread across Secs. 1, 5 and 6 and the appendices. Meanwhile the abstract states the strongest version. Reviewers who find this tension will read it as overclaiming. This is the most likely source of a "the conclusions are not robust" Weak Reject.
**Suggestion**: Reframe the headline around what *is* robust. For example: TDE's mR gain is overwhelmingly group-level, and its case-level part is matched by a ranking-preserving prior shift; the threshold-free AUC shows no net gain at either label mix. State the label-mix dependence in the abstract. Move a 4-row robustness strip into the main paper (raw vs matched, quadratic vs log, benchmark mix vs balanced mix, 20 calibration halves). Make the AUC the lead threshold-free statistic and the proper-score split secondary.
**Severity**: Major
**Confidence**: 4 — core expertise: SGG evaluation; adjacent: proper-score methodology

### W3: The paper is not positioned against post-hoc frequency-correction work in SGG, so the TDE finding risks reading as anticipated
**Problem**: The central SGG finding is that a one-line logit adjustment reproduces TDE's gain, its split and its tier profile, and that TDE's counterfactual is "to first order a learned logit adjustment". Several strands of SGG literature anticipate this: post-hoc label-frequency correction of a biased SGG model (for example Chiou et al., "Recovering the Unbiased Scene Graphs from the Biased Ones", ACM MM 2021), probabilistic debiasing via prior adjustment (Biswas & Ji, CVPR 2023), and the causal-effect / logit-adjustment discussion in long-tailed classification. None of these is discussed. The SGG debiasing citations in Sec. 2 stop at roughly 2022 (TDE, BGNN, the Desai et al. and Dong et al. papers, IETrans). The two "the line continues" citations [18, 25] are not SGG papers. Prominent 2022–2025 SGG debiasing methods are absent, including predicate-learning, prototype and noisy-label-correction lines.
**Evidence Anchor**: `absence: §2 Related work and reference list — expected discussion of post-hoc label-frequency / prior-adjustment SGG debiasing and post-2022 SGG debiasing methods; checked §1, §2, §5 "Why", references [1]–[44], supplementary bibliography`
**Why it matters**: An SGG reviewer who knows that frequency correction of MOTIFS already competes with TDE on mR will discount the TDE result as known and judge the contribution to be "only" the estimator. The paper's actual delta is the *exact attribution with inference*, applied to the released checkpoint. That delta is real, but the paper has to claim it explicitly against this literature. (Exact bibliographic details for the works named above should be checked by the authors. I name them from area knowledge, not from the manuscript.)
**Suggestion**: Add a paragraph in Sec. 2 that (i) acknowledges that post-hoc prior correction is known to deliver much of the mR gain of debiasing methods, and (ii) states precisely what the split adds: a decomposition of the gain itself, an operating-point-controlled test, and a threshold-free AUC. Choose W1's added methods partly from this recent literature.
**Severity**: Major
**Confidence**: 4 — core expertise: SGG debiasing literature; exact-citation details not verified in this review

### W4: The motivating definition ("case-level = better recognition") and the CLIP result conflict, which blurs what ΔR is for
**Problem**: The introduction presents the case-level route as "only the second is better recognition". The abstract then presents the CLIP model as a headline "converse". But Sec. 6 shows that the CLIP model carries more case-level covariance *without* being the better ranker (lower top-1, MRR and recall@5), and that the AUC does not separate it from geometry. Sec. 5 makes a related point: a case-level part of a thresholded metric is not by itself evidence of new discrimination.
**Evidence Anchor**: `text: §6 (p.8, l.536–537) "carries more case-level covariance without being the better ranker"`
**Why it matters**: Reviewers will ask what a practitioner should conclude from a large ΔR if it tracks neither ranking quality nor AUC. That weakens the proposal that benchmarks report the split. It also weakens the abstract's third headline, which rests on small non-SGG classifiers (W1).
**Suggestion**: Define ΔR in the introduction as within-group covariance of probability change with the label. Present "better recognition" as something that requires the AUC or ranking to agree, and present the three statistics as a triad with a clear decision rule. Then move the CLIP result out of the abstract, or present it as a cautionary example of ΔR and AUC disagreeing rather than as a positive "converse".
**Severity**: Major
**Confidence**: 4 — core expertise: evaluation-metric interpretation

### W5: Presentation density and dependence on the supplement are high for an 8-page CVPR paper
**Problem**: The abstract is about 270 words and carries about 15 numerical results, several to 4–5 decimals. The main text points to the supplement 15 times, and key interpretive devices are deferred there: the configuration sweep (Appendix O), calibration halves (Q.1), predicate merging (Q.2), label shift (Q.3), the shortcut bound (I) and the grouping choice (K). The supplement uses different names for the two parts ("transported gain", "within-group covariance gain") and names the estimator "WAGER", which the main paper never does. There is no algorithm box or "how to use the split" recipe.
**Evidence Anchor**: `text: Abstract (p.1, l.001–029) "a CLIP model reading image crops, ranked last on accuracy and on the proper score, carries more"`
**Why it matters**: CVPR reviewers are not required to read the supplement. A generalist reviewer will judge the 8 pages, find them hard to parse, and rate clarity low. This does not change the core claims, but it moves scores.
**Suggestion**: Cut the abstract to the problem, the split, and three rounded findings. Add a boxed 5-step protocol: declare the grouping, cache scores, compute ΔT/ΔP/ΔR with clustered CIs, match confidence, compare against the LA control and the AUC. Unify naming between paper and supplement, and either name the method in the paper or drop the name from the supplement. Round numbers to what the intervals support.
**Severity**: Minor
**Confidence**: 5 — core expertise: CVPR reviewing and AC practice

### W6: "87% of the ten points" mixes the official and micro-averaged metrics
**Problem**: The "ten points" is the official per-image mR@50 change (14.6 → 24.8, or 0.1017). The split, and therefore the 87%, is of the micro-averaged mR change of 0.0972. The paper explains this difference, but the abstract's sentence pairs the two.
**Evidence Anchor**: `text: §5 (p.6, l.415–417) "Pooled over identified relations, mean recall@50 rises by 0.0972 (0.1017 on the official per-image average)"`
**Why it matters**: A reviewer who checks the arithmetic will find it, and it invites "the split is not of the reported metric" criticism.
**Suggestion**: In the abstract, say "87% of its micro-averaged gain". Or note whether the per-image official mR is itself a label-weighted hit rate that the split can handle directly.
**Severity**: Minor
**Confidence**: 5 — recomputed from results/sgg_recall_split.json

### W7: The IETrans comparison is against a differently trained baseline in the main text
**Problem**: In the main text, IETrans's 21 points are split against the TDE paper's MOTIFS-SUM baseline. That baseline is trained separately from IETrans, so the gain mixes IETrans's relabelling with any training differences. IETrans also adds the training log-prior at test time. The cleaner comparison, IETrans against itself without the test-time prior, is only in the supplement (Table 23).
**Evidence Anchor**: `text: §5 (p.7, l.504–506) "compares it with a separately trained model of its family"`
**Why it matters**: SGG reviewers will see a 97% group-level share for a method that adds a log-prior at test time as unsurprising. They will discount the "the split separates methods" claim unless the cleaner contrast is shown.
**Suggestion**: Bring the "IETrans vs IETrans w/o prior" and "IETrans vs LA" rows into Table 1, and state what the relabelling itself contributes once the test-time prior is held fixed.
**Severity**: Minor
**Confidence**: 4 — core expertise: SGG methods

### W8: The adoption path rests on a recommendation, not a tool demonstration
**Problem**: The conclusion recommends that benchmarks report the split. It also concedes that most benchmarks archive only top-k predictions, so recovering full score vectors needed a rerun, "that, not compute, blocks routine use".
**Evidence Anchor**: `text: §7 (p.8, l.605–606) "that, not compute, blocks routine use"`
**Why it matters**: Without a demonstrated low-friction path (an evaluator hook in the standard SGG codebase used across many models), reviewers will judge impact as aspirational. This is tied to W1.
**Suggestion**: Describe the drop-in evaluator hook in a sentence or two, and show its use across the W1 table. That turns the recommendation into a demonstrated practice.
**Severity**: Minor
**Confidence**: 4 — core expertise: benchmark adoption at CVPR

### W9: Statistical lineage of within-group label transport is under-cited
**Problem**: The transport step is a within-stratum label permutation of the score contrast. The paper cites the Brier/Yates decomposition, Diebold–Mariano and DeLong lineages, but not permutation-based classifier testing or conditional (within-stratum) permutation importance. Ojala & Garriga's "Permutation Tests for Studying Classifier Performance" is in `ref.bib` but is cited nowhere in the paper or supplement.
**Evidence Anchor**: `absence: §2 "Comparing two predictors" — expected citation of permutation-test / conditional-permutation-importance lineage; checked §2, §3, supplementary text, cvpr2027/ref.bib (key ojala2010permutation uncited)`
**Why it matters**: A statistics-literate reviewer may say "this is a stratified permutation" and question the originality claim. Pre-empting that comparison strengthens the claim, because the paper's exact in-sample identity and U-statistic inference go beyond a permutation test.
**Suggestion**: Add two sentences that distinguish the exact decomposition and its inference from permutation-based importance and testing.
**Severity**: Minor
**Confidence**: 3 — adjacent field: statistical testing literature

---

## Detailed Comments

### Journal Fit (CVPR main conference)
- **In scope.** Evaluation methodology for a core CVPR task (SGG on Visual Genome), with an audit of a CVPR 2020 method (TDE) and an ECCV 2022 method (IETrans). CVPR regularly accepts analysis and "rethinking evaluation" papers when they (a) change how a sub-field reads its leaderboard and (b) show it across enough of the leaderboard. This paper does (a) and does not yet do (b) (W1).
- **Audience risk.** The technical lineage (Yates covariance, Bregman scores, Hájek projections, Diebold–Mariano) is from forecasting and statistics. Without W5's simplification, part of the vision audience will not follow Sec. 3. Some reviewers may suggest TMLR, NeurIPS (main or Datasets & Benchmarks) or ICLR as better homes for the estimator. Others may suggest a vision venue for the audit. The paper fits CVPR best if the SGG audit is the lead and the estimator is the instrument, which is the current framing in the title. Breadth must then match.
- **Length and format.** 8 content pages plus references, with a 31-page supplement. The format is compliant. The main text is self-contained for the TDE headline but not for its robustness (W2, W5).

### Originality
- **Estimator.** The covariance form is credited to Yates. The novelty is the two-model, within-group transport formulation, its exact finite-sample identity, its extension to thresholded label-weighted hit rates (mR), clustered U-statistic inference, and the operating-point control plus AUC pairing. As a combination applied to vision benchmarks, this is original. It is incremental relative to proper-score decomposition theory.
- **SGG finding.** That TDE's gain is largely a prior shift will be read as partly known (W3). The quantified, inference-backed attribution on the released checkpoint, together with the mechanism (one shared vector, correlated .75 with the log-prior), is new and citable.

### Significance
- If adopted, the split would change how SGG debiasing gains are reported. A gain that a ranking-preserving prior shift reproduces would no longer count as a recognition gain. That is a meaningful effect on the sub-field. Demonstrated significance currently rests on two methods. Significance beyond SGG (CIFAR-100-LT and text classification in the supplement) is mentioned in a paragraph and will carry little weight at CVPR.

### Structural Coherence
- The title, abstract, introduction and conclusion are consistent about the TDE headline. The tension is between the strong abstract statement and the qualified body (W2), and between the introduction's "better recognition" framing and Sec. 6 (W4). The Limitations section is strong and honest.

### Title & Abstract
- The title is memorable and accurate for the TDE audit. The subtitle names the contribution clearly. The abstract is overloaded with numbers and states the strongest form of each claim (W5, W6, W2).

### Conclusion
- The conclusion follows the evidence for the configuration the authors choose. The recommendation to report the split with declared grouping, coverage, matched rows and operating-point control is constructive. Its feasibility needs a demonstrated tool path (W8).

---

## Questions for Authors
1. Can you report the mR@50 split, with ΔAUC and the case-level part against the LA control, for a broader set of released PredCls checkpoints across at least two backbones? Does "almost entirely group-level" hold across the field, or is it specific to TDE and IETrans?
2. How does your result relate to post-hoc label-frequency correction of biased SGG models, which already reports mR gains comparable to TDE's? What does the split establish that those results did not?
3. Given that under balanced label weighting TDE's case-level part becomes significantly positive, and against the LA control the log score favours TDE, which single statement about TDE do you consider robust to every configuration in Appendix O and Q?
4. Is there a principled extension to SGCls/SGDet, for example conditioning on the ground-truth cell among correctly localized and classified pairs? If not, how should readers weigh a PredCls-only verdict, given that SGG papers typically report all three protocols?

---

## Minor Issues

### Language / Grammar
- Sentences in Secs. 5–6 often chain three or four numerical results joined by semicolons. Splitting them would help non-specialist readers.

### Citation Format
- [18] and [25] are cited as "the line continues" for SGG debiasing but are not SGG papers. Replace them with, or add, SGG-specific recent work.
- Several `ref.bib` entries are uncited (e.g. `gneiting2007proper`, `ojala2010permutation`, `hebert2018multicalibration`, `ferro2007comparing`, `duan2024longtailed`). This is harmless in the PDF, but worth tidying before archive release.

### Figures and Tables
- Fig. 2(a): the TDE row (about −0.18) dominates the x-axis and compresses the other rows. Consider a broken axis or per-row normalization.
- Table 1: add the official R@50 for each row, so the "under a tenth of TDE's cost in R@50" claim is visible in the table rather than only in the text.
- Fig. 3 is effective. Consider marking the 15 tail predicates explicitly, since the "none from the rarest predicates" claim is a headline.

### Layout
- Naming of the two parts differs between paper and supplement ("group-level" vs "transported", "case-level" vs "within-group covariance"). The supplement's opening note handles this, but a single vocabulary would be cleaner.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED` · `criteria_binding_unavailable`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | Reviewer configuration: originality relative to SGG-debiasing and evaluation literature | PARTLY_MEETS | text: §3 Theorem 1 and "Splitting mean recall"; absence anchor of W3 | The estimator's two-model exact split of mR with inference is new as applied. The core SGG finding is partly anticipated by post-hoc correction work the paper does not engage. | My knowledge of 2025–26 SGG preprints is incomplete | Yes: determines whether SGG reviewers credit the TDE result |
| Methodological Rigor | Reviewer configuration: methodology only where it shapes headline perception | MEETS | text: §4 validation; §5 evaluator replay; recomputed 298/298 numbers | Validation against designed ground truth, exact replay and clustered inference are well above CVPR norms | Proofs and asymptotics not re-derived; deferred to the methodology seat | No |
| Evidence Sufficiency | Reviewer configuration: empirical breadth as CVPR reviewers judge it | DOES_NOT_MEET | text: §1 "Every scene-graph result is PredCls"; Table 1 (2 methods) | Two methods, one backbone, one protocol and one dataset do not support field-level claims or "the split separates methods" | Repairable with inference-only runs | Yes: primary sink (W1) |
| Argument Coherence | CVPR clarity-of-claims expectation | PARTLY_MEETS | text: §1 l.141–143; §6 l.536–537; §6 l.569–571 | The abstract headline is stronger than the configuration-qualified body. The "better recognition" definition conflicts with the CLIP result. | none identified | Yes (W2, W4) |
| Writing Quality | CVPR 8-page self-containedness | PARTLY_MEETS | text: Abstract l.001–029; 15 appendix pointers | Precise but very dense, and robustness lives in the supplement | Perception varies by reviewer | Yes for scores, no for validity |
| Literature Integration | Reviewer configuration: SGG debiasing and evaluation literature | PARTLY_MEETS | absence anchors of W3 and W9 | Strong on the forecasting and statistics lineage. Thin and dated on SGG debiasing, and missing post-hoc frequency correction. | Exact bibliographic details of suggested works to be verified by the authors | Yes (W3) |
| Significance & Impact | CVPR significance criterion | PARTLY_MEETS | text: §7 recommendation; l.605–606 adoption barrier | Potentially changes how mR gains are read. Demonstrated on n = 2, with no tool path shown. | Depends on W1 outcome | Yes |

**Synthesis.** Positively verified: methodological rigor and reproducibility (S3, S4, S6), and a clear, timely question (S1, S2). Unresolved and decision-bearing: evidence breadth (W1), headline robustness and framing (W2, W4), and SGG literature positioning (W3). All are repairable in one revision cycle. W1 needs inference-only runs on released checkpoints. W2 to W4 need reframing and moving existing supplementary results into the paper. No weakness here is Critical: no single defect invalidates the core claim, which is the exact identity and its application to TDE. The strengths do not offset W1 for CVPR purposes. A field-level audit claim needs field-level coverage. Hence Major Revision on the skill scale, and **Borderline** on the CVPR scale, with an expected reviewer spread of about WR / BL / WA unless W1–W3 are addressed before the deadline.
