# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission (anonymous, Paper ID *****)
- **Review Date**: 2026-10-03
- **Review Round**: Round 1 (pre-submission simulated panel, mode `full`)

---

## Reviewer Information

### Reviewer Role *
Peer Reviewer 1 (Methodology), internal role `R1`

### Reviewer Identity *
A researcher in evaluation statistics for computer vision: calibration, proper scoring rules, uncertainty quantification, and cluster-robust or bootstrap inference on benchmark metrics.

### Review Focus *
Whether the experimental protocol supports the paper's claims. That covers the confidence-matching protocol, the choice among the five reported configurations, the controls and simulations, and the inference behind every interval and every "indistinguishable from zero". I checked the description against the code (`wager/antisymmetric.py`, `experiments/run_sgg_audit_wager.py`, `experiments/antisymmetric_simulation.py`, `experiments/run_vg_visual_wager.py`, `experiments/vg_prior_consequence.py`) and against `results/*.json`. The released MOTIFS/TDE prediction dumps (`data/vg_motifs/*.npz`) are not in the repository, so I could not recompute the audit itself. Every number below is either printed in the paper, read from the committed results JSON, or simple arithmetic on those values, and each is labelled as such.

---

## Overall Assessment *

### Recommendation *
- [ ] **Accept**
- [ ] **Minor Revision**
- [x] **Major Revision**
- [ ] **Reject**

**CVPR scale: Weak Reject** in the current form, which maps to **Major Revision** on the skill's scale. Remedies R1 to R3 in the ranked plan below are feasible in six weeks. If done, they would move my assessment to Weak Accept, because they would make the headline independent of the one protocol choice it currently rests on.

### Confidence Score *
4. The statistics (proper-score decompositions, U-statistics, cluster-robust inference, recalibration) are my core area. The SGG-specific label-semantics point (W6) is adjacent to it.

Confidence is an uncertainty/scope disclosure only; it never changes consensus counts, severity, decision bearing, or arbitration.

### Summary Assessment *
The paper splits any proper-score difference between two frozen models into a part that survives within-group relabelling (group-level, ∆P̂) and a within-group covariance remainder (case-level, ∆R̂). The estimator is a leave-one-out order-two U-statistic with an image-clustered Hájek interval. It is applied to TDE's released MOTIFS checkpoints and to a CLIP-crop predictor. The construction is exact and cheap, and the paper reports its own failure modes unusually candidly: it shows all five TDE configurations, a calibration confound of −0.488, and a sensitivity robustness value of only 0.061.

The headline is weaker than the abstract presents. "No detectable case-level improvement" holds in one cell of a configuration grid, the confidence-matched quadratic row. That row comes from one random split and one NLL-fitted temperature per model. The protocol was validated only for the case where miscalibration really is a temperature change, and TDE's logit subtraction is not one. Under the log score the same matched protocol gives a significant positive case-level gain, which the abstract compresses into "at most a twelfth". The title asks about mean recall, but the analysis never decomposes mean recall or any predicate-balanced quantity, even though Theorem 1 would allow it. The broader lesson is drawn from one checkpoint of one method, and the CLIP reversal from one training run.

None of this undermines the estimator. All of it is repairable with analyses that cost days, not months, so my recommendation is Major Revision (CVPR: Weak Reject).

---

## Strengths *

### S1: An exact, model-free identity with an algebraic negative control
The split ∆T̂ = ∆P̂ + ∆R̂ holds in every sample, with no fitted reference model, fold or smoothing parameter. The MLP-CLASS vs FREQ comparison is a real negative control: both models are functions of the cell, so ∆R̂ = 0 is forced, and the paper says the zero is algebraic rather than presenting it as an empirical success. I confirmed that the additivity in Tables 1, 6 and 7 holds to rounding, and that ∆R̂ is transitive along model chains (0.01023 + 0.00641 = 0.01664 against the reported 0.01665).
**Evidence Anchor**: `equation: Eqs. (4)–(6) and Theorem 3 (Sec. 3, p. 4, l. 221–228; supp. Eq. (17))`

### S2: The configuration-dependence is reported in full
The paper reports all five TDE configurations, including the two at which its own reading is false, and states the grounds for its preferred row. Most audit papers would have shown only the favourable row.
**Evidence Anchor**: `text: Sec. 5, p. 6, l. 392–393 "report the rest so that a reader who rejects those grounds can see what follows instead"`

### S3: Discriminant-validity arms that expose the method's main failure mode
The simulation includes a prior-only arm, an unrecorded-shortcut arm and a calibration-only arm. The last one demonstrates rather than hides that raw ∆R̂ is badly confounded by confidence (−0.488). That is why the matching protocol exists at all.
**Evidence Anchor**: `text: Sec. 4, p. 4, l. 300–302 "is credited a large spurious case-level loss of −0.488 on raw outputs"`

### S4: Inference is clustered and its limits are stated
Relations are aggregated by image before the sandwich, and the naive interval's undercoverage is quantified (88.6%). Appendix J says plainly that Theorem 4's regime (every cell diverging) is not the regime of the application, and that the finite-sample licence is the simulation. An independent code path (Eq. (3)) agrees with the transport estimator to five decimals on CIFAR.
**Evidence Anchor**: `text: supp. App. J, l. 993–994 "is therefore the evidence that the interval remains a good approximation well short of the idealization"`

### S5: A matched-subsample design for the pixel comparison
The CLIP, geometry and class-only heads share one training subsample, one architecture and one optimiser, so the contrast isolates input features from data quantity.
**Evidence Anchor**: `text: Sec. 6, p. 6, l. 402–404 "All three compared models are retrained on one fixed subsample of 100,000 training relations"`

### S6: A self-critical sensitivity analysis
The authors compute a Cinelli–Hazlett-style robustness value on their own estimate and report that it is small (ρ† = 0.061) rather than burying it.
**Evidence Anchor**: `equation: supp. Eq. (25), ρ† = 0.01427 / 0.23284 = 0.06127`

---

## Weaknesses *

### W1: The headline null rests on one instantiation of confidence matching that was validated only under correct specification
**Problem**: The matched quadratic row is the paper's reading, and it rests on several choices that the analysis does not vary:
- One random image split (`run_sgg_audit_wager.py`, `default_rng(20260811)`). The CIFAR study used twenty splits.
- One scalar temperature per model, fitted by NLL on a 240-point grid, but applied to a quadratic-score audit. A Brier-fitted temperature is the coherent choice for that row.
- Only half the test set audited (92,027 relations, coverage 98.1%, per `results/sgg_audit_motifs.json`).
- An interval that conditions on the fitted temperatures, so temperature uncertainty and split randomness are not propagated.

The protocol's validation arm (`calibration_only_arm`) makes the new model an exact power transform of the old one and refits within the same family. Temperature scaling then recovers the truth by construction. TDE's change is different in kind: a subtraction of a context-only counterfactual logit vector, which reshapes the distribution in a class- and case-dependent way. The paper itself says so (`run_sgg_audit_wager.py` comment: "changes the shape of the distribution"). The protocol therefore has not been tested against the kind of miscalibration it is applied to.
**Evidence Anchor**: `table: Table 1, row "matched quad. pair" ∆R̂ = −0.00006 [−0.00120, +0.00109] against row "raw quad. pair" ∆R̂ = −0.01355 [−0.01504, −0.01206]`
**Why it matters**: Going from raw to matched moves ∆R̂ by about 0.0117 on the same audit half: from −0.01172 (audit-half raw, in the results JSON but not in Table 1) to −0.00006. That is about 20 standard errors. The conclusion is therefore determined by the calibrator, and the reader cannot tell whether a different defensible calibrator would leave ∆R̂ near zero or move it by a comparable amount in either direction.
**Suggestion** (all cheap; cached predictions plus NumPy):
1. Fit temperatures on the canonical VG150 **validation** split, which Tang et al.'s codebase can dump, and audit the **full** test set. This removes the split and doubles N.
2. Failing that, 2-fold cross-fitting with the halves swapped and averaged, plus at least 20 repeated splits, reporting the spread as the CIFAR study does.
3. A calibrator-family sensitivity table: NLL-temperature, Brier-temperature, vector/bias scaling, and L2-regularised matrix or Dirichlet calibration. Report ∆R̂ under each.
4. An image-cluster bootstrap of the whole calibrate-then-audit pipeline (B ≈ 1,000, each O(NK)), so the interval includes temperature uncertainty.
5. A simulation arm whose miscalibration is not a temperature (class-dependent logit offsets that interact with case-level logits, as TDE's subtraction does), showing the protocol's residual bias.
6. The recalibration-invariant companion in W3.

**Severity**: Major
**Confidence**: 4 — core expertise: recalibration and proper-score decompositions

### W2: The title question is answered in the wrong units, though the paper's own theorem allows the right ones
**Problem**: Mean recall is a **predicate-balanced, rank-based** metric. The decomposition is applied only to a **frequency-weighted** quadratic or log score. TDE was designed to improve balanced performance, so auditing it on a frequency-weighted proper score invites the reply that it is being judged on a criterion it never targeted. The paper concedes the gap: "different units", "no bridge". Theorem 1, however, holds "for any integrable score contrast H". Write mR@K = Σᵢ w_{yᵢ}·hit(i, yᵢ), with w_y = 1/(|P|·n_y). Within-cell transport preserves every n_y, so ∆mR@K splits exactly into a group-level and a case-level part using H_i(y) = w_y[hit₁(i,y) − hit₀(i,y)]. Under the graph constraint, hit(i,y) = 1{y = argmax_i}·1{pair i in its image's top-K}, which can be evaluated at counterfactual labels from cached outputs. The same reweighting gives a predicate-balanced proper score, where the Bregman interpretation is kept.
**Evidence Anchor**: `text: Sec. 5, p. 5, l. 367–368 "Those are different units and we supply no bridge between them"`
**Why it matters**: As written, the paper answers "what did TDE do to the Brier score", not "what did ten points of mean recall buy". A CVPR reviewer from the SGG community will raise this first. Decomposing ∆mR@50 itself (+10.2 points) answers the title question directly, and because the decomposition is rank-based it is also unaffected by confidence matching (W1).
**Suggestion**: Add a row to Table 1, or a small new table, with the exact transport split of ∆mR@50 (and ∆R@50, ∆zR@50), with image-cluster bootstrap intervals, plus the split of a predicate-balanced quadratic score. Whatever the result, it strengthens the paper. If ∆mR's case-level part is near zero, the title claim is proven in its own units. If it is not, that is the more interesting finding.
**Severity**: Major
**Confidence**: 4 — core expertise: metric decomposition; the identity follows from Theorem 1 as stated

### W3: The log-score result is a significant positive case-level gain, and the abstract's "at most a twelfth" understates it
**Problem**: With confidence matched, the log score gives TDE a case-level gain of +0.04396 [+0.04079, +0.04714], an interval excluding zero. That is evidence that TDE **does** discriminate individual relations better under one of the paper's two declared scores. For scale, the log-score case-level gain of adding box geometry to class embeddings is +0.06536 (Table 8). TDE's matched log gain is about two thirds of it. The populations and model families differ, so this is indicative only.

The "at most a twelfth" framing divides by |∆T̂| = 0.54760. That total has the opposite sign and is dominated by TDE's loss in calibration and dispersion, so the ratio says little about the absolute size of the case-level gain. Even as a ratio, the point estimate 0.0803 passes 1/12 = 0.0833 at the interval's upper end (0.04714 / 0.54760 = 0.0861; my arithmetic, which ignores uncertainty in the denominator). Contribution 1 states "no detectable case-level improvement under the quadratic score". The abstract and Sec. 1 then generalise to "not evidence that the debiased model recognises individual relations better", which is true only under the quadratic score.
**Evidence Anchor**: `table: Table 1, row "matched log pair" ∆T̂ = −0.54760, ∆P̂ = −0.59157, ∆R̂ = +0.04396 [+0.04079, +0.04714]`
**Why it matters**: The two declared scores disagree on the sign and significance of the quantity the title asks about. The paper resolves this by choosing a denominator rather than with evidence. Readers will take the abstract to mean that TDE bought no case-level improvement, and that is not what the evidence says under the log score.
**Suggestion**:
1. Pre-declare one primary score, giving the reason (for example boundedness, which Theorem 4 needs and the floored log score only approximates), and state the log-score result in the abstract in plain words.
2. Add a **recalibration-invariant within-cell rank contrast** as the arbiter: a per-predicate one-vs-rest AUC difference inside cells, averaged with cell weights, with a DeLong-type or image-bootstrap interval. Appendix K already recommends this but never computes it.
3. Report case-level magnitudes against a reference scale measured on the **same canonical split**: for example ∆R̂ of a geometry MLP over FREQ trained on canonical VG150, or the within-cell oracle's ∆R̂. Then "small" has a yardstick.

**Severity**: Major
**Confidence**: 4 — core expertise: proper scoring rules (quadratic vs logarithmic behaviour)

### W4: The general lesson rests on one checkpoint of one method
**Problem**: The paper's broader claims ("What it questions is the habit of reading a mean-recall gain as better recognition"; the recommendation that benchmarks report the split) generalise from one released checkpoint of one debiasing method on one backbone. There is no second method, no second backbone and no training-seed replicate in the SGG audit. The paper's own CIFAR replication shows the across-seed SD of a calibration-matched ∆R̂ to be 0.01188, about 3.6 times the within-run SE of 0.00329.
**Evidence Anchor**: `absence: Sec. 5, Fig. 2 and Sec. 7 — expected an audit of more than one debiasing method or backbone; checked Sec. 1, 5, 6, 7, supplementary N.1–N.6`
**Why it matters**: With n = 1, a reader cannot tell whether "debiasing gains are group-level" describes TDE (which, as the paper notes, is group-level by construction) or the field's practice. The second is the claim that would make this a CVPR contribution and not a case study.
**Suggestion**: Add one "composition table" covering at least 4 debiasing methods × 2 backbones on canonical PredCls. Cheapest first:
- Post-hoc logit adjustment or τ-normalisation on MOTIFS-SUM, which needs no training.
- TDE on VCTree and Transformer, using the same Scene-Graph-Benchmark codebase.
- Loss reweighting and resampling baselines, each trainable in about 1 GPU-day in PredCls.
- One or two recent methods with public checkpoints.

Report ∆T̂/∆P̂/∆R̂ (raw and matched) and the W2 mR split for each. To make room, move the "Beyond scene graphs" paragraph (p. 6, l. 428–439) to the supplementary.
**Severity**: Major
**Confidence**: 4 — core expertise: benchmark-evaluation design

### W5: Transport includes same-image pairs, which contradicts the abstract's operational description and Theorem 3's independence condition
**Problem**: The abstract says each prediction is scored "against the label of a different image". The estimator (`decompose_gain`, Eq. (7)) transports every case to **all** other cases in its cell, including relations from the **same** image. Theorem 3's unbiasedness explicitly needs independent within-cell draws (supp. l. 657–660). Relations from one VG image that share a subject–object class pair are not independent: VG has many repeated and near-duplicate relations (for example several "window on building" in one photo). When i and j are near-duplicates with the same label, A_ij ≈ 0, so such pairs dilute ∆R̂ towards zero, much as the in-sample attenuation of Proposition 4 does.
**Evidence Anchor**: `text: Abstract, p. 1, l. 009–010 "Scoring each prediction against the label of a different image from the same subject–object group"`
**Why it matters**: The direction of the bias favours the TDE headline (a ∆R̂ near zero) and works against the CLIP and geometry findings. The share of within-image pairs is not reported, so the magnitude is unknown. It is probably small for large cells and could matter for small ones.
**Suggestion**: Implement leave-image-out transport, scoring each case only against labels from other images in its cell. It stays O(NK): subtract per-(cell, image) label counts and score sums. The kernel then only pairs independent clusters, which also tidies the variance theory (a generalised U-statistic over images). Report the fraction of within-cell pairs that are within-image, and rerun Tables 1, 6 and 7. If the numbers barely move, say so in one sentence. If they do move, the abstract becomes accurate either way.
**Severity**: Major
**Confidence**: 3 — the estimand mismatch is certain from the code; its numerical size is not

### W6: "Case-level recognition" is measured against single, synonym-laden predicate labels
**Problem**: ∆R̂ credits a model only when its within-cell probability movement points at the **annotated** predicate. VG150's 50 predicates are known to contain near-synonyms and hierarchy (on / sitting on / standing on / parked on; has / with), and each pair carries one label. TDE's stated purpose is to move mass from coarse head predicates to finer, more informative ones, which annotators frequently did not use.
**Evidence Anchor**: `absence: Sec. 5 and Sec. 7 Limitations — expected treatment of predicate synonymy and label ambiguity as a threat to the case-level reading; checked Sec. 1, 5, 7, supplementary K and N.1`
**Why it matters**: A null ∆R̂ against such labels cannot separate "no better recognition" from "finer recognition that coarse labels penalise". That second reading is exactly TDE's authors' argument, so leaving it unaddressed weakens the paper's central interpretation.
**Suggestion**: Rerun the matched audit (and the W2 mR split) with predicate classes merged by a declared synonym/hierarchy map (for example the geometric/possessive/semantic grouping used in the MOTIFS analysis, or a finer synonym merge). Also, if feasible, run it on a denoised-label subset. Report ∆R̂ by head/body/tail predicate group, as the mR literature does. If the null survives coarsening, the claim gets much stronger.
**Severity**: Major
**Confidence**: 3 — adjacent field: SGG label semantics; the measurement-validity logic is core

### W7: The CLIP reversal comes from one training run and is headlined on raw outputs
**Problem**: "The model ranked last is the best case-level discriminator" rests on a single seeded subsample and a single head training run. Its interval reflects test sampling only. The paper's own CIFAR evidence shows training-seed variation several times the within-run SE (W4). The headline +0.00641 is the **raw** value. The matched value, +0.00467 [+0.00314, +0.00621] (one split, `vg_prior_consequence.py`, seed 20260810), is relegated to the end of Sec. 6.
**Evidence Anchor**: `text: Sec. 6, p. 6, l. 413–414 "it discriminates between individual relations significantly better"`
**Why it matters**: This is the abstract's second headline. The test-set z is large (about 9.9 raw and about 6.0 matched, my arithmetic from the reported intervals), so the sign probably survives. The claim is about features, though, so it needs uncertainty over training.
**Suggestion**: The CLIP features are cached, so retraining heads is cheap (minutes each). Run at least 5 seeds × 3 independent 100k subsamples for all three heads. Report the across-run mean and SD of matched ∆R̂ for VISUAL vs SPATIAL, and make the matched value primary in the text and Fig. 2. Draw subsamples at the image level as well as the relation level.
**Severity**: Major
**Confidence**: 4 — core expertise: separating evaluation-set from training-run uncertainty

### W8: The inference validation does not match the regime of the claims
**Problem**: The coverage arm (`coverage_arm`) uses K = 5, about 2,240 relations, a single strongly positive effect (truth ≈ 0.18), cells assigned to relations independently of their image, and 500 replications (Monte Carlo SE ≈ 1 point on the coverage rate). The real audit has K = 50, about 90k relations, an estimate near zero, many same-image/same-cell relations, and a temperature fitted before the audit. The Hájek sandwich also omits the degenerate second-order term, which Appendix F concedes is not negligible at C/√N* ≈ 13.
**Evidence Anchor**: `text: Sec. 4, p. 4, l. 287–288 "the image-clustered interval covers in 94.0% of 500 runs"`
**Why it matters**: Contribution 3 claims nominal coverage under clustering. The evidence supports that claim only for a regime unlike the audited one. Most reported effects sit many SEs from zero, so this mainly matters for the TDE equivalence statement (W12).
**Suggestion**: Run a plasmode check on real data. Repeatedly subsample half the canonical test **images** with the actual model outputs, recompute the interval each time, and check coverage of the full-sample ∆R̂, with a finite-population correction. Compare the sandwich with an image-cluster bootstrap, use at least 2,000 replications, and include a near-null pair (for example a model against its own temperature-perturbed copy).
**Severity**: Minor
**Confidence**: 4 — core expertise: cluster-robust and U-statistic inference

### W9: The matching rule is stated as universal but applied selectively
**Problem**: The introduction and limitations say every comparison is confidence-matched. The method section's actual rule is discretionary ("Wherever compared models differ visibly in confidence", p. 4, l. 257–258). The Sec. 4 controlled predictors and the Sec. 6 headline are reported raw.
**Evidence Anchor**: `text: Sec. 1, p. 2, l. 116–117 "which is why every comparison here is confidence-matched"`
**Why it matters**: Applying a rule discretionarily is a researcher degree of freedom, and "visibly" is not operational.
**Suggestion**: Adopt one rule: always report both regimes and make the matched one primary. Fix the two sentences.
**Severity**: Minor
**Confidence**: 5 — direct textual and code check

### W10: Table 1 compares rows computed on different samples, and its grid is incomplete
**Problem**: The raw rows use the full test set (181,556 identified relations). The matched rows use the audit half (90,310 identified, coverage 98.1%). The main text quotes only the full-set coverage of 98.9%. The audit-half raw ∆R̂ (−0.01172 in `results/sgg_audit_motifs.json`) is not shown, and there is no matched subject-only row.
**Evidence Anchor**: `table: Table 1 caption — "Raw rows use every identified relation; matched rows fit each model's temperature on a held-out half of the images and audit the other half"`
**Why it matters**: A raw-to-matched comparison is only clean on the same sample, and a complete 2 (regime) × 2 (score) × 2 (grouping) grid removes any appearance of selecting among configurations.
**Suggestion**: Report all eight cells on the same audit sample, ideally the full test set with validation-fitted temperatures (W1), each with its N and coverage.
**Severity**: Minor
**Confidence**: 5 — verified against the results JSON

### W11: ∆P̂ is read as "redistribution across predicates" but also contains a dispersion term
**Problem**: Proposition 1 shows that ∆P = (improvement in mean-forecast fit) − (increase in within-cell dispersion). The supplementary itself notes that temperature matching mostly moves dispersion. The main text nonetheless interprets TDE's matched ∆P̂ = −0.18258 as redistribution within pairs.
**Evidence Anchor**: `text: Sec. 1, p. 2, l. 082–083 "a redistribution of probability across predicates within each pair"`
**Why it matters**: The paper's interpretation of what TDE did is untested. Part of the group-level loss may be dispersion that the scalar temperature did not equalise, which links back to W1.
**Suggestion**: Report Proposition 1's two brackets for TDE in both the raw and matched regimes. This is a few lines of code.
**Severity**: Minor
**Confidence**: 4 — follows from the paper's own Proposition 1

### W12: The null is asserted without an equivalence margin or a power statement
**Problem**: "Indistinguishable from zero" is a failure to reject. From the reported SE (0.000585) the 90% interval is about [−0.00102, +0.00091], and the minimum detectable effect at 80% power is about 0.0016 (my arithmetic). Both are small and would support a formal equivalence claim, but the paper never declares a margin or makes that claim.
**Evidence Anchor**: `text: Sec. 5, p. 5, l. 354–355 "p = .555: indistinguishable from zero"`
**Why it matters**: The strongest defensible form of the headline is an equivalence statement, which turns "we failed to detect" into "the case-level change is below X". At present the paper leaves that available strength unused.
**Suggestion**: Pre-declare a margin anchored to a same-split reference (W3 item 3) and report a TOST, after the robustness steps of W1.
**Severity**: Minor
**Confidence**: 5 — standard equivalence-testing practice

### W13: The randomization diagnostic is cited as support for a null it cannot test
**Problem**: The cyclic-shift test is one-sided for a positive gain (`stats >= observed_stat`), works at the relation level (it ignores image clustering), and tests the sharp null of within-cell exchangeability, not ∆R = 0. Its p = .555 is quoted beside the interval as corroboration.
**Evidence Anchor**: `text: Sec. 3, p. 4, l. 247–249 "A randomization test that cyclically shifts labels within every cell is a secondary, relation-level diagnostic"`
**Why it matters**: A one-sided test of a sharp null says nothing about a negative case-level change, and same-image dependence invalidates exchangeability.
**Suggestion**: Either drop it from the TDE paragraph or make it image-blocked (shift whole images' relations together where cell structure allows) and two-sided.
**Severity**: Minor
**Confidence**: 4 — verified in code

### W14: The reproducibility claim is inaccurate for the archive as built
**Problem**: The paper says the cached predictions are supplied. `experiments/build_code_archive.py` explicitly excludes "the large model-output caches under data/", and `data/vg_motifs/` is absent from the repository, so the audit cannot be rerun from what is shipped.
**Evidence Anchor**: `text: Sec. 7, p. 7, l. 474–476 "Code and cached predictions to reproduce every number are in the supplementary material"`
**Why it matters**: For an audit paper, the cached outputs are the data. Reviewers will check this.
**Suggestion**: Ship the two MOTIFS dumps and the CLIP-head outputs, as float16 if needed for size, or point to an anonymised host, and correct the sentence.
**Severity**: Minor
**Confidence**: 5 — direct inspection

### W15: The main text does not say that Sec. 4 uses a reconstructed split, and two numbers disagree
**Problem**: Sec. 4 says "the VG150 PredCls split", but these predictors use a 70/30 reconstruction (229,605 test relations; supp. N.1), not the canonical split TDE is audited on (183,639). Separately, the robustness value uses ∆R̂ = 0.01427 (supp. Eq. (25)) where Tables 3, 6 and 8 report 0.01439.
**Evidence Anchor**: `text: Sec. 4, p. 5, l. 305–307 "We train predicate classifiers on the VG150 PredCls split whose inputs we control"`
**Why it matters**: Readers will compare magnitudes across Sec. 4 and Sec. 5 as if the data were the same.
**Suggestion**: Say "a VG150-style reconstruction" in the main text, and reconcile 0.01427 with 0.01439 (or explain the difference, for example a different run).
**Severity**: Minor
**Confidence**: 5 — direct textual check

---

## Ranked remedy plan (six weeks, one author, cloud GPUs)

Ranked by expected effect on a CVPR methodology reviewer's score per unit of effort.

| Rank | Remedy | Fixes | Effort | Why it matters |
|---|---|---|---|---|
| R1 | Exact transport split of ∆mR@50 (plus ∆R@50 and ∆zR@50) and of a predicate-balanced proper score for TDE vs SUM, with image-bootstrap intervals | W2, partly W1 and W3 | 3–5 days, CPU | Answers the title question in its own units; rank-based, so it does not depend on matching |
| R2 | Matching-robustness package: validation-split temperatures with a full-test audit; cross-fitting and 20 splits; NLL- vs Brier-temperature; vector/Dirichlet calibrators; bootstrap of the whole pipeline; within-cell AUC contrast; TOST against a canonical-split geometry reference | W1, W3, W10, W12 | about 1 week, CPU (one GPU job to dump val predictions) | Turns the headline from "one protocol cell" into a robust statement, or reveals honestly that it is not robust |
| R3 | Composition table for at least 4 debiasing methods × 2 backbones (post-hoc LA/τ-norm first, then TDE-VCTree/Transformer, reweight/resample, one recent method) | W4 | 2–3 weeks GPU, partly parallel | Converts a case study into a finding about the field's practice |
| R4 | Leave-image-out transport, with the within-image pair share reported | W5 | 1–2 days | Makes the abstract accurate and Theorem 3's condition hold |
| R5 | CLIP heads over at least 5 seeds × 3 subsamples, matched value primary | W7 | 2–3 days, 1 GPU | Secures the second headline |
| R6 | Predicate-synonym/hierarchy coarsening and a head/body/tail breakdown | W6 | 2–3 days | Pre-empts the most likely SGG-community objection |
| R7 | Plasmode coverage on real VG images, with a near-null pair and a misspecified-calibration arm | W8, W1 item 5 | 3–4 days, CPU | Makes contribution 3 hold in the audited regime |
| R8 | Text: rewrite the abstract's log-score sentence, apply one matching rule, add Proposition 1 brackets, fix the archive and numbers | W3, W9, W11, W13–W15 | 1–2 days | Removes easy reviewer targets |

On page budget: the main paper currently ends on p. 7 plus references. R1 and R3 need roughly a third of a page together. That space can come from moving the CIFAR/text paragraph (p. 6, l. 428–439) and parts of Sec. 4's simulation prose to the supplementary.

---

## Detailed Comments *

### Title & Abstract
- The title asks a mean-recall question that the body answers only in proper-score units (W2). After R1 the title becomes literally answerable.
- The abstract's "a different image" (W5) and "at most a twelfth … under either proper score" (W3) both need revising.

### Introduction
- The contributions list is precise and appropriately hedged ("under the quadratic score"). The prose above it (l. 080–081) drops that hedge.

### Methodology / Research Design
- **Estimator.** Correct and efficiently implemented. I checked Eq. (7), the per-observation kernel mean (supp. l. 870–872) and the influence function (Eq. (8)) against `decompose_gain`, and they agree. The identity check inside the code (`np.isclose(total, prior + reasoning)`) is good practice.
- **Confidence matching.** This is the decision-bearing design choice (W1). Conceptually, temperature-matched ∆R̂ is a one-parameter stand-in for a refinement-only comparison. The paper should either justify the scalar family for TDE's logit-subtraction distortion or show that the result does not depend on it.
- **Grouping.** The "finest defensible ϕ" argument is sound against coarsening (Proposition 2). Appendix K candidly shows it gives no guidance between equally fine partitions. Reporting within-cell label heterogeneity (entropy of p(y|c), weighted by cell mass) alongside coverage would cost nothing and helps readers judge identifiability.
- **Controls.** The class-only negative control is sound. A positive control on the **canonical** split, such as a geometry MLP over FREQ, is missing and is needed to scale the TDE null (W3, W12).

### Results / Findings
- Additivity and chain-transitivity check out in every table I verified (Tables 1, 6, 7).
- Table 1 mixes samples (W10). Fig. 2 mixes raw and matched comparisons without saying so in the legend; only "TDE vs MOTIFS (released, matched)" is labelled.

### Discussion
- "What that does and does not license" (p. 5, l. 366–381) is the best paragraph in the paper. It should also state the log-score result plainly.
- "Characterises TDE rather than indicting it" is fair. But it implies that the TDE finding is close to an algebraic consequence of a near-cell-constant logit subtraction. Quantify how much of TDE's logit change is cell-constant (the R² of the logit difference on cell dummies). If the share is high, frame the audit as a validation; if it is low, as a finding.

### Conclusion
- "Carrying no detectable case-level improvement under the quadratic score" is accurate. "It finds the best recogniser of the three" needs W7's replication first.

### References
- Out of my remit (Reviewer 2).

---

## Questions for Authors *

1. Under a Brier-fitted temperature, a vector-scaling calibrator, and temperatures fitted on the canonical validation split, does the matched quadratic ∆R̂ for TDE vs SUM stay inside ±0.001? How much does it vary across 20 random splits?
2. What fraction of within-cell pairs in the canonical test split come from the same image? How do Table 1's matched rows change under leave-image-out transport?
3. What is the exact transport split of ∆mR@50 = +0.1017 between the two checkpoints? Is its case-level part distinguishable from zero?
4. Under the log score, the matched case-level gain is +0.044 with an interval excluding zero. On what pre-specified ground is the quadratic score primary, and how should a reader reconcile the two?

---

## Minor Issues

### Language / Grammar
- p. 4, l. 255–256: "(Sec. 4 measures how much)" splits across a column break in a way that reads as a dangling parenthesis. Rephrase.

### Figures and Tables
- Table 1: add N, identified coverage and the temperatures to each row.
- Fig. 2(a): label which rows are raw and which are matched.
- Table 6: the ρ̂ column header is undefined in the caption (it is presumably the share ∆R̂/∆T̂). Define it.

### Layout
- About a third of a page can be recovered by moving the "Beyond scene graphs" paragraph to the supplementary.

---

## Criterion-Bound Judgements *

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | quality_rubrics (methodology lens only) | NOT_ASSESSED | — | Outside R1 remit | Reviewer 2/3 remit | no |
| Methodological Rigor | quality_rubrics; R1 configuration card | PARTLY_MEETS | Table 1; Eqs. (4)–(8); `run_sgg_audit_wager.py` | Estimator and identity are exact and correctly implemented; the headline depends on an unvaried, under-validated matching protocol (W1) and on transport that includes same-image pairs (W5) | Could not rerun the TDE audit (dumps absent) | yes — W1 and W5 are repairable |
| Evidence Sufficiency | quality_rubrics | PARTLY_MEETS | Table 1 matched log row; Sec. 6; absence (W4) | One checkpoint, one CLIP run, no mR decomposition; log score contradicts the headline framing | Magnitude of seed effects in SGG unknown | yes — W2, W3, W4, W7 |
| Argument Coherence | quality_rubrics | PARTLY_MEETS | p. 5 l. 367–368; p. 2 l. 116–117 | Discussion is careful, but the abstract's claims run ahead of the matched-quadratic-only evidence; the matching rule is stated universally and applied selectively | none identified | yes — W3, W9 |
| Writing Quality | quality_rubrics | NOT_ASSESSED | — | Outside R1 remit | — | no |
| Literature Integration | quality_rubrics | NOT_ASSESSED | — | Reviewer 2 remit | — | no |
| Significance & Impact | quality_rubrics | NOT_ASSESSED | — | Reviewer 3 remit | — | no |
| Statistical reporting (Step 4a) | statistical_reporting_standards.md | PARTLY_MEETS | Tables 1, 6–8; supp. App. J | CIs everywhere, effect sizes in natural units, clustering handled. Missing: equivalence/power for the null (W12), propagation of first-stage temperature uncertainty (W1), training-seed uncertainty for method-level claims (W7). No p-hacking signals; all configurations disclosed | Coverage evidence from a regime unlike the audit (W8) | partly |

The unresolved decision-bearing items are W1 to W4: a protocol-robustness gap, a units gap, an understated contrary result, and n = 1 generalisation. All are repairable within the deadline with R1 to R3. None is fatal: the estimator itself is sound.

---

## Arithmetic Receipts

no_recomputable_statistics: The manuscript reports no test statistic with df, no small-N integer-scale means or SDs, and no df from which N could be checked. Its p-values are Monte Carlo randomization p-values (floor .002) and its intervals are normal-approximation Hájek/sandwich intervals, so none of p_from_test_statistic, grim, grimmer or n_from_df applies. Proportions such as 0.6981 at N = 183,639 are GRIM-uninformative at that N. I checked instead the additivity ∆T̂ = ∆P̂ + ∆R̂ in Tables 1, 6 and 7 (consistent to rounding), chain transitivity (0.01023 + 0.00641 = 0.01664 against 0.01665), the "twelfth" ratio (0.0803 point, 0.0861 at the CI upper bound, against 0.0833), and Eq. (25) (0.01427 / 0.23284 = 0.0613; inconsistent with the reported ∆R̂ of 0.01439, see W15).
