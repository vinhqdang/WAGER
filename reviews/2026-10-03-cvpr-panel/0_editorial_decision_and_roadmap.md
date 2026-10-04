# Editorial Decision and Revision Roadmap — 2026-10-03 CVPR panel

**Manuscript.** *What Did Ten Points of Mean Recall Buy? Separating Group-Level from
Case-Level Gains in Scene Graph Generation*, commit `d227e40` (8 pp. + 23 pp. supplementary).
**Target.** CVPR 2027 main conference, deadline 16 November 2026.
**Panel.** Five role-separated seats committing blind; same model family throughout, so
correlated errors are likely. Provenance: `_panel_provenance.md`. `NOT_CALIBRATED`; no
venue-alignment claim (`criteria_binding_unavailable`).

---

## Decision: **Major Revision** — on the CVPR scale, **Weak Reject as it stands**

| Seat | Configured identity | CVPR scale | Skill scale | Confidence |
|---|---|---|---|---|
| Venue-fit (`EIC`) | CVPR area chair, scene understanding and evaluation | Weak Reject | Major Revision | 4 |
| R1 Methodology | evaluation statistics for vision | Weak Reject | Major Revision | — |
| R2 Domain | scene graph generation specialist | Weak Reject | Major Revision | 4 |
| R3 Perspective | ML evaluation science, outside SGG | Borderline | Major Revision | 4 |
| Devil's Advocate | fixed seat | findings only: 1 CRITICAL, 7 MAJOR, 8 MINOR | — | — |

Unanimous among the four scoring seats. Venue-fit and Domain each say, independently, that
their top remedies done would move the paper to **Borderline–Weak Accept**. Nobody judges the
paper out of scope or unsalvageable; everybody judges it under-evidenced for a field-level
claim at CVPR.

**What the panel agrees is right.** The estimator is exact and correctly implemented (R1
checked the code). The question and Figure 1 are, in the area chair's words, "among the best
framings I have seen for an evaluation paper in this area" (EIC S1). The paper reports the
configurations that cut against it (EIC S3, R1 S2, R2 S4, R3 S4). The algebraic zero for two
class-pair-only models is the right negative control (EIC S4, R1 S1, R3 S3). Printed numbers
match the results files (EIC S5, R2 S2).

**What blocks acceptance** is not an error in the method. It is that the paper asks a
question about the field in mean-recall units and answers it about one checkpoint in
proper-score units.

---

## Consensus

Counting rule: denominator is the four non-DA seats; silence is not agreement.

### CONSENSUS-4 (all four scoring seats)

**A. The title's question is answered in the wrong units, and the paper's own theorem allows
the right ones.** EIC W3, R1 W2, R2 W3, R3 W4; DA C1 independently. Theorem 1 holds "for any
integrable score contrast H", and within-cell relabelling preserves every predicate's test
count, so a per-relation, micro-averaged mean recall@K splits exactly into group-level and
case-level *mean-recall points*. The graph-constrained variant fits too, since whether pair
*i*'s predicate *y* ranks inside the image's top-K is defined for any counterfactual *y*. Two
seats caution that the codebase's *official* mR averages per image first, which changes the
weights; it may not split exactly, so the micro-averaged variant must be shown to track it
(EIC W3, Q1).

**B. One released checkpoint cannot carry a field-level claim.** EIC W1, R1 W4, R2 W1, R3 W3;
DA M1. One method, one backbone, one fusion type, one protocol (PredCls). The supplementary's
own standard says "a method-level claim needs replication rather than a single audit" (DA M1).
The area chair calls this "the main reason I would expect Weak Reject scores".

**C. The CLIP reversal is weaker than presented.** Every seat raises a different aspect: toy
predictors on a non-canonical split (EIC W6), one training run headlined on raw outputs (R1 W7),
the "ranked last by every metric" claim rests on a home-built pool (R2 W8), and "better
recogniser" is untested against scene-context shortcuts (R3 W6). DA M6 adds that after prior
matching the CLIP model is still worse on top-1, MRR and recall@5.

### CONSENSUS-3

**D. The headline depends on configuration; a calibration-free companion is needed.** EIC W4,
R1 W1 and W3, R3 W7 (R2 silent; R2 S3 praises treating calibration as protocol). DA M3 adds a
specific mechanism: separate temperatures on two models sharing one logit space inject a term
proportional to the baseline's own case-informative logits. All three seats and the DA name
the same remedy: the within-cell rank (AUC) contrast the supplementary already recommends but
never computes.

**E. The main text does not disclose that Sections 4 and 6 use a reconstructed VG150 split.**
EIC W8, R1 W15, R2 W8 (R3 silent); DA m1. Two different test-set sizes are both called VG150.

### Two-seat findings

- **Predicate ambiguity and label noise** (R1 W6, R2 W4). TDE's stated aim is to move mass from
  "on" to finer predicates that annotators often did not use; the case-level part counts that
  as a loss. The first objection a TDE proponent would raise, and the paper is silent on it.
- **Literature** (EIC W5, R2 W5–W6). Missing SGG debiasing families (BGNN, GCL, IETrans, NICE,
  PE-Net), the origin of mR@K (KERN, VCTree), the grouping-loss line, and the closest VQA
  precedents (Teney et al. 2020; Shrestha et al. 2020). Two misattributions.
- **PredCls only** (EIC W12, R2 W7). Should be stated as the scope.
- **Unused 1.4 pages; statistics-paper register** (EIC W10, R3 W2).
- **Selective confidence matching** (EIC W7, R1 W9; DA M4). The text says "every comparison
  here is confidence-matched"; the CLIP and geometry headlines are raw.

### Single-seat findings worth keeping

- **R3 W1.** The generality evidence (CIFAR-100-LT superclasses, 20-Newsgroups topics) uses
  groupings derived from the *label*, which the paper's own setup rules out.
- **R1 W5.** The abstract says each prediction is scored "against the label of a different
  image"; the estimator transports to every other case in the cell, same image included.
- **R1 W14.** The reproducibility claim is inaccurate: the per-relation predictions are not
  shipped.
- **EIC W11.** The supplementary still carries revision-history language ("earlier drafts of
  this paper asserted").

---

## Facts re-verified by the synthesiser before adjudication

Each was checked against a primary source, not taken from the reports.

| # | Claim (source) | Check | Verdict |
|---|---|---|---|
| V1 | TDE drops the image-specific visual logits too, so it is not group-level "by construction" (R2 W2) | Upstream `roi_relation_predictors.py` l. 631 with `FUSION_TYPE sum`: TDE = `[vis(union)+ctx(post_ctx)+frq(pair)] − [vis(union)+ctx(avg_ctx)+frq(pair)]`. The frequency **and** the union-region visual logits cancel exactly; `avg_ctx` is the context encoder re-run over the same image's proposals. | **Validated.** The paper's description is wrong. |
| V2 | TDE lowers no-graph-constraint mR@50 (R2 W3, DA m2) | `results/sgg_audit_motifs.json`: ng-mR@50 0.3260 → 0.2981 | **Validated.** The ten points exist only under the graph constraint, and the paper reports neither number. |
| V3 | The case-level part is not shift-invariant (R3 W5) | Repository estimator, one three-label cell, p(x\|y) fixed, only p(y) changed: −0.16754 → **+0.20919**. Two-label cells: 0 sign flips in 2,000 trials. | **Validated.** True for two labels only; §3's "a case-level gain is not [contingent]" is false in general. |
| V4 | "At most a twelfth" fails at the interval bound (R1 W3) | Matched log: point 0.0803 ≤ 0.0833, interval bound 0.0861 > 0.0833 | **Validated.** True of the point estimate only. |
| V5 | Transport includes same-image partners (R1 W5) | `decompose_gain` transports to "every other label j in the same cell" | **Validated.** The abstract's "different image" is inaccurate. |
| V6 | Per-relation predictions are not shipped (R1 W14) | `data/vg_motifs/motifs_{none,TDE}_predcls.npz`, which the audit reads, does not exist in the repository or the archive | **Validated** — and it gates the roadmap (see below). |

---

## Adjudication of the CRITICAL finding

### DA C1 — **VALIDATED (open; blocks Accept)**

*"The ten-point gain is therefore not evidence that the debiased model recognises individual
relations better" does not follow.* Mean recall averages per predicate; the audited case-level
part is weighted per relation, so head predicates dominate it. A pooled zero is compatible
with real case-level gains on the tail predicates that drive mean recall, offset by losses on
the head. The paper's own CIFAR and 20-Newsgroups tier tables show exactly that
head-loses/tail-gains signature; no tier breakdown exists for TDE.

Corroborated by all four scoring seats as consensus finding A. The inference gap is real; the
direction of any cancellation is unknown until the split is run per predicate. V1 sharpens it:
since TDE discards the visual logits that carry case-level evidence, a negative head-predicate
case-level part is mechanistically plausible, and a positive tail one cannot be ruled out.

**Required response.** Split mean recall itself and report the case-level part per predicate
tier. If the tail is ≈ 0, the title is answered directly and this becomes the paper's
strongest figure. If the tail is significantly positive, the headline must change.

### Disagreement: is the TDE result expected by construction?

- **EIC W2 and DA M2:** yes — the paper calls TDE "a group-level intervention by design", and by
  Theorem 2 a cell-dependent logit offset gives a log-score case-level part of exactly zero.
- **R2 W2:** no — in the released code TDE also removes image-specific visual logits.
- **Resolution: R2 is right on the facts (V1).** The premise of EIC W2 and DA M2 is the
  paper's own misdescription. Their *conclusion* survives in part — the frequency term TDE
  removes is cell-constant in PredCls and contributes exactly zero to the log-score case-level
  part — but the visual term it removes is case-level evidence, so a near-zero case-level
  result is a finding to explain, not an identity. This turns a weakness into an opportunity:
  splitting TDE's logit change by branch (frequency / visual / context) explains *why* the
  case-level part is near zero, which no seat thinks the SGG literature knows.

---

## The panel's answer to "how do we get a better contribution"

Every scoring seat converges on the same transformation: from **a tool plus one audit** to
**a field audit that answers the title in mean-recall points**. The area chair's suggested
title if it lands: *"What Did a Decade of Mean-Recall Gains Buy?"*

## Revision Roadmap

`must_fix` items gate acceptance; `should_fix` items are expected; `consider` items are
optional. Order is source order, not a ranking of effort.

| ID | Item | Class | Sources | What resolves it |
|---|---|---|---|---|
| REV-1 | **Split mean recall itself.** Micro-averaged graph-constrained recall@50 with per-relation weight 1/(K·n_y); verify it tracks the official mR@50; report group-level and case-level mR points; case-level part per predicate and per head/body/tail tier with clustered intervals. | must_fix | CONSENSUS-4 A; DA C1 | A table row in mR points for every audited pair; tier breakdown for TDE |
| REV-2 | **Audit the field, not one checkpoint.** MOTIFS / VCTree / VTransE × {plain, TDE, TE, NIE} from released checkpoints; a zero-training post-hoc frequency-subtraction / logit-adjustment sweep on the plain baseline; one or two training-time methods with public checkpoints (BGNN, IETrans — R2 reports both verified public). Each row against its own baseline and against FREQ. | must_fix | CONSENSUS-4 B; DA M1, M2 | A leaderboard-shaped table; at least one row where the split separates methods |
| REV-3 | **Calibration-free companion and a declared protocol.** Within-cell rank (AUC) contrast for every row; temperatures fitted on the validation split, full test set audited; a common-temperature variant for weight-sharing pairs; ≥20 splits or a pipeline bootstrap. | must_fix | CONSENSUS-3 D; DA M3, M5 | The TDE null either survives a scale-free statistic or is replaced by what it shows |
| REV-4 | **Correct the six validated factual errors** (V1–V5 and the reproducibility claim V6), the two misattributions, the selective-matching sentence, and the undisclosed reconstructed split. | must_fix | V1–V6; CONSENSUS-3 E; EIC W7; R2 W6 | Text matches code and results |
| REV-5 | **Explain TDE mechanistically.** Split its logit change by branch — frequency, visual, context — under the same estimator. | should_fix | R2 W2; disagreement above | A sentence saying *why* TDE's case-level part is near zero |
| REV-6 | **Predicate ambiguity.** Rerun the split with a declared predicate merge (geometric / possessive / semantic) and with multi-label credit for duplicate annotations. | should_fix | R1 W6, R2 W4 | Null survives coarsening, or the claim is narrowed |
| REV-7 | **Strengthen or replace the reversal.** Matched numbers primary; several seeds; a context-only control; or zero-shot CLIP/SigLIP prompt scoring on the canonical split. | should_fix | CONSENSUS-4 C; DA M6 | A reversal on models the audience uses, robust to seeds and context |
| REV-8 | **Show the operational payoff on real data.** A label-shifted VG test (within-cell reweighting to uniform predicate frequencies), stated honestly given V3. | should_fix | DA M7; R3 W5 | Evidence that the split predicts which gains survive a shift |
| REV-9 | **Related work for a CVPR audience.** SGG debiasing by family; mR origin; grouping loss; Teney 2020 and Shrestha 2020. Each reference verified before it is added. | should_fix | EIC W5; R2 W5–W6 | A §2 an SGG reviewer recognises |
| REV-10 | **Scope and generality.** State PredCls scope; drop or re-ground the label-derived groupings in the long-tail studies (global cell, or an input-measurable grouping). | should_fix | EIC W12, R2 W7; R3 W1 | No claim the setup rules out |
| REV-11 | **Use the page budget for vision readers.** Move inference detail to the supplementary; fill the freed space with REV-1/2 tables. Remove revision-history language from the supplementary. | consider | EIC W10–W11; R3 W2 | 8 full pages in a vision register |

## Critical path

**Every must_fix item except REV-4 needs the per-relation predictions of each audited model,
and none are in this environment (V6).** They were produced on Google Colab. The first task
is therefore to restore the GPU pipeline — download the released Scene-Graph-Benchmark
checkpoints and the VG150 data, re-run inference, and **commit or archive the prediction
arrays this time** — after which REV-1, REV-3 and REV-5 are CPU work in hours.

A six-week plan consistent with the seats' estimates: week 1, REV-4 text fixes and restore
the pipeline on TDE; week 2, REV-1, REV-3, REV-5 on TDE (this alone answers DA C1); weeks 2–4,
REV-2 runs in the background; week 5, REV-6 to REV-9 and the rewrite; week 6, verification and
a re-review.

## Status (2026-10-03, end of day)

| Item | State | Where |
|---|---|---|
| Critical path | **Done.** One TDE PredCls pass of the released checkpoint on a Colab T4 with every branch's logits dumped (TE = TDE and NIE = 0 in PredCls, so one pass covers all four); offline replay of the official evaluator; per-relation outputs archived in the repository (`data/vg_motifs/wager_sgg/`). Re-scored baseline and TDE reproduce the official R@K, mR@K, ng-mR@K exactly; the proper-score audit regenerated from the rerun matches every archived number to 1e-9. | `experiments/colab_sgg_stage2.py`, `colab_sgg_rank.py`, `tests/test_sgg_rank.py` |
| REV-1 | **Done.** mR@50 (micro, identified relations) +0.0972 = group +0.0841 + case +0.0130 [+0.0093, +0.0168]; body +0.1224, head −0.0255, tail +0.0003 (baseline recalls none of the 15 tail predicates, TDE one). Per-predicate figure. | Sec. 5, Fig. 3, Table 1; App. on the split |
| REV-2 | **Done for PredCls.** (a) Logit adjustment of the baseline (τ = 0.5, 1) as the operating-point control. (b) The released IETrans Neural-Motifs PredCls checkpoint (BGNN's release is SGDet only): mR@50 0.3587 on the standard test relations (0.3576 on IETrans's own, which drops exact duplicates); vs baseline +0.2204 = group +0.2143 + case +0.0060 [−0.0031, +0.0151]; matched case-level −0.0162 (quad) / −0.0544 (log), both excluding zero; AUC −0.0093 [−0.0181, +0.0004]. The split separates the methods: TDE no case-level change, IETrans a case-level loss. Caveat: no plain IETrans baseline released. | Sec. 5 "A second method", Table 1; App. on IETrans |
| REV-3 | **Partly.** Within-cell AUC (temperature- and prior-shift-invariant, tested) for every row: TDE +0.0026 [−0.0028, +0.0086]. Still open: validation-split temperatures and repeated splits. | Sec. 3, 5; `wager/rank.py` |
| REV-5 | **Done.** Exact path split baseline → vis+ctx → ctx → TDE (parts add up, asserted): dropping the prior −0.0009 mR, dropping the visual term +0.0164 (case +0.0016 [−0.0006, +0.0037]), subtracting the averaged context +0.0817. The averaged-context term is 99.96% one vector shared by every relation (corr +0.75 with the log training prior): in PredCls TDE is to first order a learned logit adjustment of the context branch. | Sec. 5 "Why"; App. on TDE's branches; `experiments/run_sgg_tde_path.py` |
| New finding | A ranking-preserving change (logit adjustment, dropping the frequency branch) yields a significant case-level part of a thresholded metric; the paper now reads hit-rate splits against an operating-point control and the AUC. | Sec. 3 "Splitting mean recall" |
| REV-7 | **Partly.** CLIP/geometry/class predictions regenerated on Colab and archived (`data/vg_visual/`); class and geometry accuracies reproduce exactly, CLIP's moves 0.6161 → 0.6156 (fp16 encoding; three previously missing images now present), and every dependent number in the paper was updated (no sign or significance changes). Within-cell AUC answers Sec. 6's open question: CLIP vs geometry +0.0085 [−0.0062, +0.0214], not separated; both beat class-only (+0.0408, +0.0323). Abstract, intro and Sec. 6 now claim more case-level covariance, not better discrimination; IETrans wording aligned (case-level loss, AUC not significant). Seeds / context-only control / zero-shot CLIP still open. | Sec. 6; `experiments/run_vg_visual_rank.py` |
