# Editorial Decision and Revision Roadmap — 2026-10-05 CVPR panel

**Manuscript.** *What Did Ten Points of Mean Recall Buy? Separating Group-Level from
Case-Level Gains in Scene Graph Generation*, commit `909e5a3` (8 pp. + 31 pp. supplementary).
**Target.** CVPR 2027 main conference, deadline 16 November 2026.
**Panel.** Five role-separated seats committing blind, with the same configuration cards as
the 2026-10-03 panel. Same model family throughout, so errors are likely correlated.
Provenance: `_panel_provenance.md`. `NOT_CALIBRATED`; no venue-alignment claim
(`criteria_binding_unavailable`).

---

## Decision: **Major Revision** — on the CVPR scale, **Borderline as it stands**

| Seat | CVPR scale (10-03 → 10-05) | Skill scale | Confidence |
|---|---|---|---|
| Venue-fit (`EIC`) | Weak Reject → **Borderline** | Major Revision | 4 |
| R1 Methodology | Weak Reject → **Borderline** | Major Revision | 4 |
| R2 Domain | Weak Reject → **Borderline** (leaning Weak Reject) | Major Revision | 4 |
| R3 Perspective | Borderline → **Weak Accept** | Major Revision | 3 |
| Devil's Advocate | 1 CRITICAL, 7 MAJOR, 8 MINOR → **0 CRITICAL, 6 MAJOR, 7 MINOR** | — | 4 |

Every scoring seat moved up one step, and the Devil's Advocate found no rejection-level
defect: "the identity is correct and the numbers trace". The EIC forecasts three typical
CVPR reviewers at **Weak Reject / Borderline / Weak Accept**, i.e. the area-chair discussion
zone, with an SGG-methods reviewer lowest and an evaluation reviewer highest.

**What the panel agrees is right.** All five seats ran the verifier (298/298 numbers trace)
and the tests (30 pass); none found an arithmetic or transcription error. Four recomputed
the headline shares (87% and 97% group-level). R1 gives the 87% an interval, [83.0%, 90.2%].
Seats single out three things: splitting mean recall itself (EIC S2); the exact replay of
TDE's released checkpoint (EIC S4, R2 S1, R1 S3); and the mechanistic account of TDE, which
R2 checked against the code (R2 S2, DA observations). The logit-adjustment control is "the
right control" (R2 S3, R1 S4, R3 S1). The disclosure of adverse configurations is praised
by every seat.

**What blocks acceptance has changed.** On 10-03 it was the units and the single checkpoint.
Now it is two things. First, **the TDE case-level verdict is protocol-dependent**, and the
panel produced new evidence showing it. Second, **the empirical footprint is still narrow
for a field-level claim** at CVPR.

---

## Facts re-verified by the synthesiser before adjudication

| Claim | Seat | Verified how | Result |
|---|---|---|---|
| The audited IETrans checkpoint is IETrans **+Rwt** (internal + external transfer, reweighted loss) | R2 W1 | Authors' `cmds/50/motif/predcls/lt/combine/val.sh` sets `OUTPATH=$EXP/50/motif/predcls/lt/combine/rwt` | **Confirmed** |
| Under temperature + per-class-bias recalibration (also ranking-preserving within cells), TDE's case-level part is significantly positive | R1 W1 | Re-ran R1's script | **Confirmed**: quadratic +0.00445 [+0.00354, +0.00536], log +0.02543 [+0.02287, +0.02800] |
| Under the same recalibration the logit-adjusted control becomes identical to the baseline, and IETrans's case-level loss persists | R1 W1 (full table) | Same re-run | **Confirmed**: LA − base = 0.00000 exactly; IETrans quadratic −0.01679 [−0.01814, −0.01544], log −0.06609. The IETrans case-level loss is robust to the recalibration family, unlike the TDE null |
| The within-cell AUC weights cells by about n_c², the split by n_c; with split-consistent weights the CLIP verdict changes | R1 W2 | Re-ran R1's script | **Confirmed**: CLIP − geometry is −0.0067 [−0.0120, −0.0019] on the full test set (relation-weighted). On the audit half it is 0.0000 relation-weighted and +0.0214 [+0.0001, +0.0435] comparison-weighted |
| The worked example's "+1/2" is the four-case estimate; the population case-level part is 3/8, with group-level 0 | R1 W10 | Computed by hand | **Confirmed**. The text then mixes the estimate with population statements ("stays at +3/8") |
| Matched CLIP − geometry case-level is +0.00464 in Sec. 6 but +0.00472 in Supp. Tab. 27 | DA m2 | grep of both tables | **Confirmed**: two different temperature grids |
| Ref. [22] (BMVC 2022, "Rethinking the evaluation of unbiased SGG") lists the authors of a different paper | R2 W5 | `ref.bib` entry `li2022rethinking` | **Confirmed**: the bib lists Wei Li et al.; the seat identifies the BMVC authors as Xingchen Li, Long Chen et al. (author list to be re-verified at the source when fixed) |
| The case-level part is linear in the contrast, so ΔR̂ = R̂(q₁) − R̂(q₀), with R̂ a per-model within-cell permutation importance | R3 W1 | Algebra (H = S(q₁) − S(q₀), estimator linear in H) plus the seat's numerical check | **Confirmed** |

---

## Consensus

Counting rule: denominator is the four scoring seats; the DA is listed separately; silence
is not agreement.

### CONSENSUS-4

**A. "TDE gained no within-group discrimination" is conditional, and the headline states it
unconditionally.** EIC W2, R1 W1–W3, R2 W3, R3 W4/W10; DA M1, M2, M6. The seats arrive from
different directions:
- **Label mix:** at uniform within-cell labels, +0.01430 against the baseline and +0.00723
  against the control (paper's own Supp. Tab. 27; EIC, R2, DA).
- **Score:** under the log score, +0.044 in 20/20 halves (R2, DA).
- **Recalibration family:** under temperature + per-class bias, +0.00445 quadratic and
  +0.0254 log (R1, verified above).
- **Composition:** 64.9% of the AUC's weight is on head–head predicate pairs. There TDE's AUC
  *rises*, +0.0068 [+0.0005, +0.0134]; on the other pairs it falls, −0.0051 (DA,
  recomputation). With equal block weights TDE falls by 0.0107.
- **Equivalence:** the AUC interval [−0.0028, +0.0086] has no equivalence margin (R1 W3).

What survives every check is narrower and still interesting. The **group-level share** of
the mean-recall gain is 87% [83, 90]. Under both AUC weightings (comparison-weighted +0.0026;
relation-weighted −0.0018 [−0.0038, +0.0014], R1) there is **no detectable net change in
within-cell ranking**. And there is a **redistribution** of discrimination between predicate
pairs (DA, and the paper's own label-shift row). The proper-score case-level verdict on TDE
is protocol-dependent and should not carry the headline.

**B. Case-level part ≠ "better recognition"; the CLIP section exposes the gap.** EIC W4, R2
W8, R3 W6/W10, R1 W2; DA M2, m7. The introduction and Fig. 1 equate the case-level part with
recognising which images show a predicate, but Sec. 6 shows more case-level covariance
without better ranking. Under split-consistent AUC weighting, geometry ranks *better* than
CLIP on the full test set (verified above). R2 and R3 add that in Visual Genome a
group-level shift towards a more specific predicate can itself be correct recognition, under
label ambiguity.

### CONSENSUS-3 (+ DA)

**C. The IETrans attribution is confounded.** EIC W7, R1 W4, R2 W1; DA M4. The baseline is a
separately trained causal MOTIFS-SUM, a different design, and the checkpoint is IETrans+Rwt,
not plain IETrans (verified). "97% group-level, case-level loss" describes a model-pair
contrast, not relabelling.

### CONSENSUS-2 (+ DA)

**D. Breadth.** EIC W1 ("the main reason it sinks; not fixable in rebuttal"), R2 W2; DA M3.
The evidence is two methods, one backbone family, PredCls only, single runs. R2 argues that
SGCls and SGDet are feasible for TDE, because baseline and TDE share the checkpoint and the
object predictions. R1 and R3 do not raise breadth (R3: "repairable without new SGG
experiments").

**E. Prior art on post-hoc frequency correction in SGG is missing.** EIC W3, R2 W4; DA m6.
This literature anticipates "a logit adjustment reproduces TDE":
- DLFE (Chiou et al., ACM MM 2021);
- RTPB (AAAI 2022);
- the logit-adjustment step of Structured Sparse R-CNN (Teng & Wang; the DA read it in full,
  τ = 0.3).

Also absent: PCPL, CogTree, NICE, PE-Net and the F@K metric (R2). Two "the line continues"
citations are not SGG papers (EIC, R2).

**F. What does the split add beyond "logit-adjusted control + within-cell AUC"?** R3 W1/W4,
EIC W9; DA M5.
- The verdicts are delivered by the control and the AUC.
- The decomposition is a difference of per-model within-cell permutation importances, a
  lineage the paper does not cite (Strobl et al. 2008; Fisher, Rudin & Dominici 2019).
- The answer that survives is: exact additive accounting (per predicate, per tier), paired
  cluster-robust inference, and exposure to label shift. R3 adds that the per-model form gives
  a leaderboard-friendly single column.

**G. Zero-shot CLIP is too weak to stand for "the model the audience uses".** R1 W11, R2 W9;
DA m7. It uses a single prompt, ViT-B/32, and reaches 2.5% top-1 (near chance).

**H. Inference details.** R1 W6 and DA m1 (the image bootstrap pulls case-level parts towards
zero, by about 10%, because resampled same-image same-label pairs have zero kernel); DA m2
(two temperature grids). R1 W5 adds that the Hájek variance omits a second-order term that
matters for two-case cells; this affects 1% of VG relations, and the stated conditions differ
between two appendices.

**I. "Nine of the ten points" is specific to mR@50 with graph constraint.** R1 W9; DA M5. At
mR@100 the control recovers 72%.

### Single-seat findings worth keeping

- **R1 W7 / DA M6:** the calibration-only simulation is tautological, because a temperature
  fit undoes a temperature change by construction. Validate against class- or cell-wise
  miscalibration.
- **R1 W8 / R3 W5:** the label-shift analysis follows from the reweighted estimator. Its
  empirical content is the sign heterogeneity of D(y,z). Present it as a sensitivity analysis
  over a range of mixes, with effective sample sizes.
- **R1 W10:** the worked example confuses estimator and estimand (verified).
- **R1 W12:** give the 87% and 97% shares with intervals.
- **R1 (fallacies):** a p = .724 is reported for a statistic that is algebraically zero.
- **R2 W5–W7:**
  - wrong authors on [22];
  - [9] and [21] are mischaracterised;
  - the TDE mechanism holds for SUM fusion only, and "visual term" means the union-region
    term.
- **R2 W10:** the abstract presents the CLIP study, which uses non-SGG classifiers, as an SGG
  finding.
- **R2 W11:** report F@K. By R2's computation the control's F@50 (0.344) beats TDE's (0.322).
- **R3 W2:** the CIFAR and 20NG studies group by label-derived superclasses, so they do not
  test transfer. One input-grounded non-SGG audit (Waterbirds by background, VQA-CP by
  question type) would.
- **R3 W3/W9:** the reporting standard omits the AUC, a label-mix check and within-cell label
  heterogeneity, and it is not scoped to PredCls.
- **EIC W5:** density. The abstract has about 270 words and about 15 numbers; the paper makes
  15 appendix pointers.
- **EIC W6 / DA m4:** the 87% refers to micro-averaged mR, not the official metric. Say so
  where it is headlined.
- **DA m3:** the supplement says a sensitivity bound "changes nothing" about a null. That is
  wrong in general, because the between-cell term has either sign.
- **DA alternative paths:**
  - a benchmark ceiling: if within-pair predicate choice is largely annotator style, any
    gain must be group-level, so measure the ceiling;
  - "TDE as redistribution" as the more specific account;
  - CLIP's covariance as a dispersion artefact.

---

## Adjudication of Devil's Advocate CRITICAL findings

`da_critical_adjudications: []`. The DA raised no CRITICAL issue this round. Its closest
candidate, M1, is subsumed by CONSENSUS-4 A above and is repairable by re-analysis and
rewording. **10-03's DA C1** ("a conclusion about mean recall drawn from a proper-score
covariance") is **resolved**: the paper now splits mean recall itself, and EIC S2 names this
as what makes the paper relevant to CVPR.

---

## Progress against the 2026-10-03 roadmap

| 10-03 item | State now (per this panel) |
|---|---|
| REV-1 split mean recall itself | **Resolved.** Praised (EIC S2, R1 S2); R1 reproduces Table 1 to 4 decimals |
| REV-2 audit the field | **Partly.** A second method and an operating-point control were added; breadth is still the main sink (D). New: IETrans is +Rwt and confounded (C) |
| REV-3 calibration-free companion, protocol | **Done but reopened.** The AUC exists, but its weighting differs from the split's (B); the recalibration family moves the TDE null (A) |
| REV-4 factual errors | **Resolved**; no seat found an error of fact in the claims checked. New citation errors (R2 W5, W6) |
| REV-5 TDE mechanism | **Resolved**; R2 confirms it against the code. Scope to SUM fusion (R2 W7) |
| REV-6 predicate ambiguity | **Accepted** as done. R2 and R3 still argue that ambiguity makes group-level shifts partly recognition (B) |
| REV-7 CLIP reversal | **Partly.** Seeds accepted; the AUC verdict depends on weighting (B); zero-shot too weak (G) |
| REV-8 label-shift payoff | **Accepted** as a result (R3 S2: "a falsifiable prediction the data confirm"); R1 calls it an identity (W8); it **exposed** the TDE conditionality (A) |
| REV-9 related work | **Partly.** SGG post-hoc correction prior art and post-2022 methods are missing (E) |
| REV-10 scope | **Resolved** for PredCls; R3 W2 still finds the label-derived groupings uninformative about transfer |
| REV-11 page budget | **Resolved** on length; EIC W5 still finds the 8 pages dense |

---

## Revision Roadmap (round 2)

| ID | Item | Priority | Source | Done when |
|---|---|---|---|---|
| R2-1 | **Re-state the TDE result around what survives every protocol.** Headline: the gain is 87% [83, 90] group-level, and within-cell ranking shows no net change under both AUC weightings. Then report the redistribution explicitly: AUC by predicate-tier pair, and the label-shift row. Present proper-score case-level parts as protocol-dependent: per-model temperature, shared temperature, temperature + class bias; quadratic and log. Drop "no discrimination gained" in favour of "no net change in within-cell ranking; discrimination moves between predicate pairs". | must_fix | A; DA M1, M2 | Abstract, intro, Sec. 5 and conclusion make no claim that one protocol contradicts |
| R2-2 | **Fix the AUC weighting.** Report the relation-weighted (split-consistent) AUC beside the comparison-weighted one, on the same half as the split, and rewrite the Sec. 6 sentence accordingly (geometry ranks better on the full set under split weights). | must_fix | B; R1 W2 | Both weightings in Tab. 1 and Sec. 6; text matches |
| R2-3 | **Recalibration family.** Add temperature + per-class bias (and a vector/Dirichlet variant) to the robustness section. Validate the matching protocol in simulation against class-wise miscalibration with identical within-cell information. | must_fix | A; R1 W1, W7; DA M6 | A supp table, and a validation arm that is not tautological |
| R2-4 | **IETrans honestly labelled.** Call it IETrans+Rwt. Present the row as a cross-model contrast, or audit a same-codebase plain baseline if one can be trained or found. | must_fix | C | No sentence attributes the split to relabelling alone |
| R2-5 | **Breadth.** Highest yield per R2: TDE in SGCls and SGDet from the same causal-MOTIFS release (shared checkpoint, predicted pairs as the grouping), plus any further released PredCls checkpoints (VCTree-TDE, other debiasers with public weights). Target: a main-paper table of ≥4 method rows across ≥2 backbones or protocols. | must_fix (venue) | D | Field-level wording is backed by the table, or narrowed |
| R2-6 | **Prior art and positioning.** Cite and position against DLFE, RTPB and SSRCNN-LA. State the permutation-importance equivalence ΔR̂ = R̂(q₁) − R̂(q₀) as a proposition, with Strobl 2008 and Fisher et al. 2019. State what the split adds beyond control + AUC: additive accounting, per-predicate and per-tier parts, paired inference, label-shift exposure. Offer the per-model column for leaderboards. | must_fix | E, F | Sec. 2 recognisable to an SGG reviewer; contribution list survives R3 W1 |
| R2-7 | **Case-level ≠ recognition.** Rephrase Fig. 1, the intro and the conclusion as "case-level covariance". Discuss label ambiguity (R2 W8). Scope the CLIP study as non-SGG classifiers in the abstract. | should_fix | B; R2 W10 | No sentence equates ΔR with recognition |
| R2-8 | **Zero-shot CLIP**: a stronger VLM (ViT-L/14 or SigLIP, prompt ensemble), or move it entirely to the supplement with its limits. | should_fix | G | Either a credible baseline or no main-text claim |
| R2-9 | **Inference hygiene.** Use the pairs-aware or Hájek interval for the label-shift table; use one temperature grid everywhere; intervals on the 87% and 97% shares; drop the p for an algebraic zero; make the Hájek conditions consistent; fix the worked example (estimate versus population). | should_fix | H; R1 W5, W10, W12; DA m1–m3 | Verifier re-run; numbers consistent across tables |
| R2-10 | **Scope statements.** "Nine of ten points" at mR@50 (graph constraint) only; micro versus official mR where the 87% is headlined; label shift as a sensitivity analysis over several mixes. | should_fix | I; R1 W8, W9; R3 W5; DA m4 | — |
| R2-11 | **Citations.** Fix [22]'s authors and the descriptions of [9] and [21]; add PCPL, CogTree, NICE, PE-Net; report F@K; scope the mechanism to SUM fusion. | should_fix | R2 W4–W7, W11 | Every changed reference verified at its source |
| R2-12 | **One input-grounded non-SGG audit** (Waterbirds by background, or VQA-CP by question type), or narrow the generality claim. | consider | R3 W2 | — |
| R2-13 | **Benchmark ceiling**: estimate how much within-pair predicate choice is image-determined (e.g. agreement on duplicate annotations). | consider | DA alternative 1 | — |
| R2-14 | **Density**: shorten the abstract and cut numbers; fewer appendix pointers in the main text. | consider | EIC W5 | — |

## Critical path

R2-1, R2-2, R2-3, R2-4, R2-6, R2-7, R2-9 and R2-10 are CPU work and writing on outputs
already cached: days, not weeks. **R2-5 is the only item that needs GPU runs**, and it is the
one the EIC says cannot be fixed in rebuttal. With six weeks to the deadline, start R2-5 now
(Colab, TDE SGCls/SGDet from the same release), and do the text and analysis items while it
runs.

---

### Synthesis audit lines

```
dimension_verdicts: not applicable (no sprint contract supplied; free-form panel as on 2026-10-03)
fired_conditions: []
da_critical_adjudications: []
editorial_decision=major_revision
```

---

## Status (2026-10-05, after the round-2 revision)

| ID | State | Where |
|---|---|---|
| R2-1 | **Done.** Headline restated around what survives every protocol: 87% [83, 91] group-level (image-group jackknife), no detected change in within-cell ranking under either AUC weighting or by tier pair; the proper-score case-level part is protocol- and mix-dependent (−0.00006 per-model T; +0.00445 T + class bias; −0.0184 shared T; +0.044 log; +0.0143 uniform mix). | Abstract, Sec. 1, 5, 7 |
| R2-2 | **Done.** Relation-weighted AUC added to `wager/rank.py` (tested against brute force) and reported beside the comparison-weighted one, on all relations and on the audit half; Sec. 6 now says geometry ranks better under the split's weighting (−0.0067 [−0.0120, −0.0019]). | Tab. 1, Sec. 6, App. on robustness |
| R2-3 | **Done.** Temperature + per-class-bias matching (control ≡ baseline exactly); non-tautological validation arm: a class-wise operating-point shift survives temperature matching (+0.0106) and is removed by T + bias (0.0000). | Sec. 3, 4; `sim_classwise_shift.py` |
| R2-4 | **Done.** Named IETrans+Rwt throughout, with the evaluation-script evidence; framed as a cross-model contrast. Its within-cell loss holds under every measure (relation-weighted AUC −0.0235 [−0.0275, −0.0182]; T + bias −0.0168). | Sec. 5, App. on IETrans |
| R2-5 | **Done for SGCls and SGDet on the full test set.** Inline evaluator replay, equal to the codebase's evaluator on 200 images in both protocols, reproducing the released recalls on the full test set (SGCls R@50 0.3924 vs 0.3925; SGDet 0.3247 vs 0.3245). SGCls: +0.0517 mR@50, 99% group-level; control +0.0518 at R@50 0.384 vs 0.263; TDE's within-cell ranking worse (rel. AUC −0.0128 [−0.0171, −0.0074]). SGDet (26,446 images): +0.0310, 87% group-level, case-level +0.0041 [+0.0013, +0.0070], matched exactly by the control (TDE vs control −0.0000 [−0.0030, +0.0030]); control +0.0418 at R@50 0.3186 vs 0.1657; relation AUC −0.0012 [−0.0051, +0.0030]; matched quadratic case-level −0.00446 [−0.00560, −0.00332]. Other backbones with released weights still open. | Sec. 5 "Beyond PredCls", App. on SGCls/SGDet |
| R2-6 | **Done.** DLFE, RTPB, SSRCNN-LA, PCPL, CogTree, NICE, PE-Net cited (each checked on Crossref); permutation-importance lineage (Strobl 2008; Fisher et al. 2019) with a proposition ΔR̂ = ρ̂(q₁) − ρ̂(q₀), tested; contribution restated. | Sec. 2, Supp. Prop. 2 |
| R2-7 | **Done.** "Case-level covariance" wording in Fig. 1, intro and conclusion; the CLIP study is described as a controlled real-pixel study. | Fig. 1, Sec. 1, 6, 7 |
| R2-8 | **Done (supplement).** Zero-shot CLIP removed from the main text; its limits (single prompt, ViT-B/32, near-chance top-1) stated. A stronger VLM was run: CLIP ViT-L/14 with a five-prompt ensemble, top-1 1.8%, within-cell AUC 0.5252 (ViT-B/32: 0.5164) against MOTIFS's 0.5705, case-level part over FREQ +0.00033; same picture (supplement, "A larger model"). SigLIP and region-level features not run. | App. on zero-shot CLIP |
| R2-9 | **Done.** Label-shift intervals by a delete-a-group jackknife; one temperature grid per study; 87%/97% shares with intervals; algebraic-zero p removed; limit-theorem conditions made consistent, with a small-cell coverage table (81.5% at n_c = 2, nominal from 3 up, 96.3% at VG150's cell sizes); worked example at population values; sensitivity-bound sentence corrected. | Sec. 3, 4, App. on robustness and limit theorem |
| R2-10 | **Done.** Label shift framed as a sensitivity analysis along a path of mixes (TDE's case-level part significant from α = ¼); micro vs official mR stated; "nine of ten points" scoped to mR@50 (graph constraint). | Sec. 6, App. on label shift |
| R2-11 | **Done.** [22] authors fixed (arXiv 2208.01909); [9] described as class-balanced sampling; open-vocabulary citation reworded; F@50 reported (control 0.344 vs TDE 0.322); mechanism scoped to SUM fusion and the union-region term. | Sec. 2, 5 |
| R2-12 | **Not done.** No input-grounded non-SGG audit; the generality paragraph was narrowed instead. | Sec. 6 |
| R2-13 | **Partly.** Identical-input ties cap the within-cell AUC at 0.9996, so MOTIFS's 0.57 is not that kind of ceiling; annotator style is not measurable from the data. | App. on predicate merges |
| R2-14 | **Done.** Abstract shortened (210 words), intro condensed; paper at 8 content pages. | — |
