## Devil's Advocate Review

**Seat:** Devil's Advocate (`DA`), fixed seat, no configuration card. Skill: `academic-paper-reviewer` v1.11.1, mode `full`, role file `agents/devils_advocate_reviewer_agent.md` (standard-mode output format; no sprint contract was supplied).
**Manuscript:** "What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation", CVPR 2027 submission (repository commit 909e5a3), main paper (8 pp.) plus supplementary (31 pp.), code and `results/*.json`.
**Rating:** none. The DA seat gives findings only, with no CVPR rating and no Accept/Minor/Major/Reject recommendation.

### Calibration Status
`NOT_CALIBRATED`

criteria_binding_unavailable

No author-confirmed target context was supplied. Anything I say about CVPR is a configured perspective, not a judgement that the paper fits the venue. Seat reports always emit `NOT_CALIBRATED`.

### What I recomputed (Iron Rule 6)

All work was read-only. Scratch scripts are in `/tmp/claude-0/-home-user-WAGER/06889eb3-4869-50f6-bd62-a68f44e45a32/scratchpad/panel_DA/`.

1. I ran `python experiments/verify_manuscript_numbers.py --driver cvpr2027/main.tex`. All 298 printed numbers trace to the committed results (164 of them in the main paper). I ran `python -m pytest -q tests`: 30 passed. **None of the numbers I spot-checked was fabricated or mistyped.** My concerns are about how the numbers are interpreted, not whether they are correct.
2. **Within-cell AUC broken down by predicate-tier pair** (`auc_tiers.py`). I used the paper's own `wager.rank._blocks`, the canonical relations of Sec. 5, the tiers of `run_sgg_recall_split.py` (head >10,000 training instances, tail <500), and a 100-replicate image bootstrap.
   - **Weight:** 64.9% of the comparison weight behind the reported AUC falls on head–head predicate pairs (9 head predicates). Pairs among body and tail predicates only carry 1.3%.
   - **TDE − baseline AUC on head–head pairs:** **+0.0068**, bootstrap 95% [+0.0005, +0.0134].
   - **TDE − baseline AUC on all other pairs:** −0.0051 [−0.0134, +0.0026].
   - **With equal weight per (cell, predicate-pair) block:** baseline 0.6955, TDE 0.6847 (−0.0107), LA₁ 0.6975.
   - **Sanity check:** LA₁ leaves every tier's AUC unchanged (head–head 0.5634 → 0.5634).
3. **Image-bootstrap bias in the label-shift intervals** (`boot_check.py`). For the matched geometry-vs-class pair at the benchmark labels, the point estimate is +0.00882. The mean of 60 bootstrap replicates is +0.00833 (SD 0.00033): a downward shift of about 1.5 SD, so the intervals are pulled toward zero.
   - **Why:** 61.1% of audited relations share both their (cell, image) with another relation, and 90.9% of those within-image pairs carry the same label. Their kernel is therefore zero. A multinomial image weight doubles their expected weight (E[w²] = 2 versus 1 for pairs from different images), which dilutes the estimate toward zero.
4. **Cross-file consistency.** In `results/label_shift.json` the matched CLIP-vs-geometry case-level part is +0.00472. In `results/vg_visual_seeds.json` (seed 0) it is +0.00464. The two scripts fit temperatures on different grids: `run_sgg_audit_wager.fit_temperature` uses `geomspace(0.05, 20, 240)`, while `vg_visual_seed_stats.fit_temperature` uses `linspace(0.25, 8, 311)`.
5. **Literature check.** I read the full text of Teng & Wang, Structured Sparse R-CNN (arXiv 2106.10815). It applies post-hoc logit adjustment as an SGG debiasing step (τ = 0.3, Sec. 3 "Logit adjustment (LA)"). From a search-result abstract only, Chiou et al., ACM MM 2021 (arXiv 2107.02112), recover unbiased SGG probabilities post hoc from label frequencies. Neither paper is cited.

### Criterion-Bound Judgements

| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Core thesis (DA Ch. 1) | DA role file, Challenge 1 | PARTLY_MEETS | `table: Tab. 1`; `table: Supp Tab. 27` | "87% group-level" stands. "No discrimination gained" holds only at one weighting. | Rests partly on my 100-replicate tier recomputation | yes: the title question's answer changes |
| Cherry-picking (Ch. 2) | DA role file, Challenge 2 | PARTLY_MEETS | `table: Supp Tab. 16`; `table: Supp Tab. 19` | Every configuration is reported in the supplement, which is commendable. But the headline uses the one configuration (matched quadratic, mR@50) where TDE's case-level part is null. | Authors do argue for that configuration | yes |
| Confirmation bias (Ch. 3) | DA role file, Challenge 3 | PARTLY_MEETS | `text: Supp I l.1175-1176` | Robustness logic is applied asymmetrically to nulls versus positive results | — | no (minor) |
| Logic chain, theorems to claims (Ch. 4) | DA role file, Challenge 4 | PARTLY_MEETS | `equation: Thm. 1 / Eq. (3)` | Theorem 1 is exact but definitional. Reading ΔR as "recognition" needs construct validity that the paper's own evidence contradicts. | — | yes |
| Overgeneralisation (Ch. 5) | DA role file, Challenge 5 | DOES_NOT_MEET | `text: Supp N.5 l.1433-1434` | Two single-seed checkpoints of one backbone family support method-level and benchmark-level recommendations | — | yes |
| Alternative paths (Ch. 6) | DA role file, Challenge 6 | PARTLY_MEETS | `text: Supp K l.1221-1230` | A rank-based within-cell contrast is acknowledged as the cleaner tool. It ends up doing the decisive work. | — | yes |
| "So what?" (Ch. 8) | DA role file, Challenge 8 | PARTLY_MEETS | `table: Supp Tab. 15` | The mR split cannot be interpreted without an existing baseline (LA) and an existing statistic (DeLong-style AUC) | Value as a reporting standard is plausible | yes |
| Field-norm self-calibration (Ch. 9) | DA role file, Challenge 9 | MEETS | — | Only M3 rests partly on a norm. It is grounded in the authors' own stated standard plus one external source. | — | no |

These judgements are not totalled, weighted or mapped to a recommendation.

### Genuine strengths (brief)

- The paper is unusually transparent. It discloses every configuration, including the adverse ones (shared temperature, label shift, log score, subject-only grouping).
- Every number traces to committed results.
- The evaluator replay reproduces the official numbers to four decimals.
- The mechanistic finding is clean and checkable: TDE's averaged-context term is 99.96% one shared vector (Supp Tab. 21).

None of this is in dispute below.

### Strongest Counter-Argument

The paper asks what TDE's ten points bought. Its own appendices answer that the split, by itself, cannot say.

1. **For mean recall, "87% group-level" is not a property of TDE.** A logit adjustment that changes no within-cell ranking gets 85% group-level and a significant case-level part as well (Tab. 1). That pattern is simply what moving a thresholded metric's operating point produces.
2. **To read the split, the paper needs two outside tools.** One is an existing baseline, post-hoc logit adjustment, which is already used as an SGG debiasing step [Teng & Wang]. The other is an existing statistic, a within-cell AUC in the DeLong family. Those two carry the conclusion. The decomposition mostly restates what they show.
3. **The "no discrimination gained" leg is a net of zero at one weighting, not an absence.**
   - The AUC's weight is 65% on nine head predicates.
   - On head–head pairs, TDE's AUC rises significantly (+0.0068, my recomputation). On pairs involving body predicates it falls.
   - Weighted equally per block, TDE's AUC falls by 0.0107.
   - With predicates balanced within each pair, which is the philosophy mean recall itself embodies, TDE's quadratic case-level part is +0.0143 against the baseline and +0.0072 against the control. Both intervals exclude zero.
   - Under the log score it is +0.044 in 20 of 20 calibration halves.
4. **The case-level measure is unstable across equally principled choices.** Its sign varies with the proper score, the temperature protocol, the label mix and the grouping. It also disagrees with rank metrics in both directions: CLIP has more covariance but ranks worse, while TDE has positive ΔR but negative AUC under the label shift.
5. **The evidence is narrow.** The headline rests on two released PredCls checkpoints from one backbone family, each a single training run. The setting is the one in which TDE algebraically collapses toward a prior shift. Meanwhile the paper's own CIFAR study warns that "a method-level claim needs replication rather than a single audit."

What survives is a correct identity and a useful reporting habit. The headline empirical verdict on TDE, and the recommendation that benchmarks adopt the split, are not licensed.

### Issue List

#### CRITICAL
| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|

No singleton rejection-level defect found. The identity (Theorem 1/3) is correct and the numbers trace. M1 comes closest, but the core 87% group-level mR split survives it, and it can be repaired by re-analysis and rewording.

#### MAJOR
| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|
| M1 | Logic chain / data–conclusion mismatch | **Problem.** The conclusion says that behind TDE's gain "no within-group discrimination was gained". The evidence supports only "net zero at the benchmark's comparison weighting".<br>(i) My recomputation: 64.9% of AUC weight is head–head pairs. TDE's head–head AUC change is +0.0068 [+0.0005, +0.0134], against −0.0051 on all other pairs. With equal block weights, TDE is −0.0107.<br>(ii) Predicate-balanced reweighting (Tab. 27): quadratic case-level part +0.01430 [+0.01144, +0.01632] against the baseline and +0.00723 against LA₁.<br>(iii) Log score: +0.04396, positive in 20 of 20 halves (Tab. 25). Against LA₁: +0.01544 (Tab. 19).<br>(iv) Against LA₁ at ng-mR@100: +0.0148 [+0.0064, +0.0232] (Tab. 16).<br>(v) The headline AUC null [−0.0028, +0.0086] cannot exclude a gain of about 12% of MOTIFS's entire within-cell AUC advantage over FREQ (0.0705).<br>Sec. 6 itself concedes that "TDE gains discrimination between some predicate pairs and loses it between others". The abstract, contributions and conclusion state the stronger claim without that qualifier.<br>**Remedy.** Report the within-cell AUC and per-pair D(y,z) by tier pair, and per predicate. Report a predicate-balanced AUC. Restate the claim as a redistribution of discrimination (toward head–head pairs) that nets to zero at the benchmark mix, or drop it. | `text: Conclusion l.614-616 "whose case-level remainder a ranking-preserving logit adjustment matches and behind which no within-group discrimination was gained"` | 4 — recomputed with the authors' code. Bootstrap has 100 replicates and the image-weighting caveat of m1. | | |
| M2 | Construct validity of ΔR (theorems → headline) | **Problem.** Theorem 1 makes ΔR exact by definition (ΔR = ΔT − ΔP). Calling ΔR "recognising which individual images actually show them" is an interpretive claim, and the paper's own results contradict it repeatedly.<br>• CLIP vs geometry: ΔR > 0 with every interval excluding zero, yet prior-matched top-1, MRR and R@5 are all lower, and the AUC does not separate the models (Sec. 6, Supp Tab. 24).<br>• TDE under the label shift: ΔR = +0.0143 while ΔAUC = −0.0183 (Tab. 27).<br>• TDE vs LA₁ matched: the quadratic score gives −0.00398 and the log score +0.01544, both significant (Tab. 19). Both are Bregman scores that Theorem 2 says carry "the same exact covariance meaning".<br>• Shared versus per-model temperature flips TDE from null to −0.019 in 20 of 20 halves (Supp Q.1).<br>• Subject-only grouping flips it to −0.217.<br>A quantity whose sign depends on several equally principled analyst choices, and which disagrees with rank-based discrimination in both directions, does not license "case-level = recognition" language.<br>**Remedy.** Pre-declare one score with a stated reason (e.g. boundedness for Theorem 4). Make the rank-based within-cell contrast the primary estimand for any claim about discrimination. Rename ΔR descriptively, e.g. "within-cell score covariance under S". | `table: Supp Tab. 19 rows "TDE vs LA1, matched, quad./log"` | 4 — all values are the authors' own, verified by their checker | | |
| M3 | Overgeneralisation | **Problem.** The headline audits are two released PredCls checkpoints of one backbone family (MOTIFS), each a single training run, on one test split. The paper then recommends that "benchmarks ... report the split" and speaks of "two released debiasing methods".<br>The authors' own CIFAR study finds roughly fourfold seed variation in the case-level part. They conclude that a method-level claim needs replication rather than a single audit, a standard their SGG audits do not meet.<br>PredCls is also the setting where TDE algebraically reduces to "context minus a near-constant vector" (Sec. 5, Supp Tab. 21). The paper has chosen the case most favourable to "TDE ≈ logit adjustment", and SGCls/SGDet are excluded by construction.<br>**Remedy.** Retrain MOTIFS/MOTIFS-TDE (and ideally VCTree-TDE) over ≥3 seeds and report the spread of every headline number. Audit at least one non-MOTIFS backbone or one further debiasing family. Scope the title, abstract and conclusion to "two released PredCls checkpoints". | `text: Supp N.5 l.1433-1434 "exactly why a method-level claim needs replication rather than a single audit."` | 4 — internal-consistency check | Authors' own stated standard (Supp N.5). External: Bouthillier et al., "Accounting for Variance in Machine Learning Benchmarks", MLSys 2021. | The SGG audits make method-level attributions from one run per model, which is the exact situation N.5 says is insufficient |
| M4 | Logic chain (attribution of IETrans) | **Problem.** The IETrans "gain" and its split compare a released IETrans checkpoint with the separately trained MOTIFS-SUM baseline. The two models differ in visual-term fusion and training run, and IETrans has no learned frequency branch but a test-time log-prior (Supp O.2). The "97% group-level, case-level loss" therefore describes a model-pair contrast, not the effect of IETrans's relabelling. Yet the abstract and contributions attribute it to "IETrans".<br>**Remedy.** Train IETrans and its own plain baseline in the same codebase with matched seeds, or present the row explicitly as a cross-model contrast and drop the method attribution. | `text: Sec. 5 l.504-506 "With no IETrans baseline released, this compares it with a separately trained model of its family."` | 4 | | |
| M5 | "So what?" / alternative paths | **Problem.** For mean recall the split cannot be read on its own. A ranking-preserving LA₁ shows 85% group-level and a significant case-level part (+0.0139). The paper therefore needs (a) the LA₁ control and (b) the within-cell AUC to reach any verdict. The verdict ("TDE ≈ logit adjustment; no AUC change") is delivered by (a) and (b) alone. Supp K concedes that the rank-based contrast "would dissolve the confound this paper spends a protocol on".<br>Post-hoc logit adjustment is already used as an SGG debiasing step (Teng & Wang, arXiv 2106.10815, τ = 0.3). "Nine of the ten points" holds at k = 50 only. At official mR@100, LA₁ recovers 0.0925 of TDE's 0.1286 (72%, Supp Tab. 15).<br>**Remedy.** Show at least one decision for which the mR split gives information that the "LA control + within-cell AUC" pair does not. Otherwise reframe the contribution around the proper-score identity and a reporting protocol. Report the recovered fraction at every k. | `text: Sec. 1 l.088-090 "recovers nine of the ten points with the same split, at under a tenth of TDE's cost in R@50"` | 3 — the "so what" weighting is a judgement call | | |
| M6 | Confirmation bias / method validation | **Problem.** The confidence-matching protocol that produces the headline quadratic null is validated (Sec. 4) only against a perturbation it removes by construction: a temperature-softened copy of the same model. Real checkpoints differ in class- and cell-dependent confidence, which a single scalar temperature cannot equalise. The headline TDE null depends on the protocol: a shared temperature gives −0.019 in 20 of 20 halves.<br>**Remedy.** Validate in simulation against class-wise or cell-wise miscalibration with identical within-cell information. Report the TDE split under vector/class-wise temperature (or Dirichlet) matching. Show that the headline is invariant. | `text: Sec. 4 l.348-350 "a temperature-softened copy of an overconfident one carrying identical case-level information"` | 4 | | |

#### MINOR
| # | Dimension | Issue Description | Evidence Anchor | Confidence |
|---|-----------|-------------------|-----------------|------------|
| m1 | Inference | The image-bootstrap intervals of the label-shift split are pulled toward zero. My check: point +0.00882 versus bootstrap mean +0.00833 (≈1.5 SD), because resampling doubles the weight of same-image, same-label pairs, whose kernel is zero. This shows up as point estimates sitting at the outer edge of most Tab. 27 intervals (e.g. +0.00882 in [+0.00762, +0.00897]). **Remedy:** use the clustered Hájek interval (Sec. 3) here as well, or a pairs-aware bootstrap. | `table: Supp Tab. 27, "Intervals: image bootstrap" (case 95% CI columns)` | 4 — recomputed |
| m2 | Reproducibility | The "same" matched CLIP-vs-geometry split is +0.00464 (Tab. 24) and +0.00472 (Tab. 27), because two scripts fit temperatures on different grids. Tab. 27 says its temperatures "are those of Secs. 5 and 6". **Remedy:** use one shared `fit_temperature`. | `dataset: results/label_shift.json vs results/vg_visual_seeds.json, CLIP vs geometry matched case` | 5 — read from files |
| m3 | Logic | The claim that the flagship null is not exposed to omitted-variable bias is wrong in general. Prop. 2's between-cell term has either sign, so a null at φ can hide a non-zero fully adjusted part. **Remedy:** delete the sentence or bound the null both ways. | `text: Supp I l.1175-1176 "a sensitivity bound on a null result changes nothing about it."` | 4 |
| m4 | Metric fidelity | The split is of micro-averaged mR (+0.0972), not the official per-image mR (+0.1017). The "87%" headline therefore refers to a metric nobody reports. **Remedy:** report the official-metric gap per headline row, or split the official metric with per-image weights. | `text: Sec. 1 l.139-141 "For mean recall the split is of the micro-averaged version, which pools relations across images"` | 4 |
| m5 | Framing | "Exact" is definitional: any ΔP makes ΔT = ΔP + (ΔT − ΔP) exact. The substance is in the meaning of ΔP and ΔR, which M2 questions. **Remedy:** move the word "exact" from the selling point to a property. | `text: Abstract l.008 "We give an exact way to tell them apart."` | 3 |
| m6 | Prior art for the control | Post-hoc frequency correction as SGG debiasing is not cited: Teng & Wang, Structured Sparse R-CNN (LA, τ = 0.3); Chiou et al., DLFE, ACM MM 2021 (from abstract only). **Remedy:** cite these and position TDE ≈ LA relative to them. | `absence: References [1]-[44] — expected prior SGG uses of post-hoc logit/label-frequency adjustment; checked main reference list, Sec. 2, Supp K` | 3 — only one of the two papers was read in full |
| m7 | Overstatement (CLIP) | The conclusion says the split "finds a case-level gain that the aggregates conceal", but Sec. 6 says better recognition "is not established". In addition: under predicate-balanced labels CLIP beats geometry in total (+0.02478, so "ranked last" depends on the label mix), and zero-shot CLIP carries little case-level signal (+0.00046, Supp Q.4). **Remedy:** say "covariance" instead of "gain", and add the label-mix caveat. | `text: Conclusion l.617-619 "applied to a model every aggregate metric ranks last, it finds a case-level gain that the aggregates conceal."` | 4 |

### Ignored Alternative Explanations/Paths

1. **The benchmark leaves little room for case-level gains.** If within-pair predicate choice in VG is mostly annotator style, synonymy or multi-label ambiguity, then any mR gain must be group-level. That would make "87% group-level" a property of VG150 PredCls, not of TDE.
   - MOTIFS's within-cell AUC is only 0.5705.
   - 9.1% of scored relations (183,639 − 166,940) sit on box pairs with a second annotated predicate (Supp Q.2).
   - The synonym merges address this only partly.
   - **What would rule it out:** a ceiling estimate, such as agreement on duplicate or re-annotated relations, or the AUC of an oracle-ish model.
2. **TDE as a redistribution, not a null.** My tier recomputation suggests TDE shifts within-cell discrimination toward head–head contrasts (on / has / wearing) and away from contrasts involving body predicates. This is a more specific, and more damaging, account of TDE than "nothing case-level". The split could deliver it per tier pair, but the paper does not report it.
3. **CLIP's covariance as a dispersion or calibration-shape artefact.** By Prop. 1, ΔP contains a dispersion term. A single temperature cannot equalise within-cell dispersion between a 1,088-dimensional CLIP head and a 76-dimensional geometry head. The CLIP model's covariance advantage, which no ranking metric confirms, may reflect how its probability mass is shaped rather than what it recognises. The AUC null and the lower prior-matched accuracy fit this reading as well as the paper's.
4. **A rank-based primary estimand.** Supp K weighs it and keeps it as a companion. For the paper's actual question ("did the model learn to recognise?"), the rank contrast is the direct estimand, and the proper-score split is the companion.

### Missing Stakeholder Perspectives

- Benchmark and leaderboard maintainers, who are asked to declare φ before a leaderboard opens (Sec. 7).
- Downstream SGG consumers (VQA, captioning, retrieval), for whom a group-level shift toward specific predicates may be the desired behaviour.
- Dataset designers and annotators, whose labelling protocol sets the case-level ceiling.
- Authors of the audited methods, whose released checkpoint and setting (PredCls only) define the scope of the verdict.

### Unexamined Premise

The paper assumes that within an ordered object-class pair, the gold predicate is largely determined by image content, so a case-level channel exists for a better model to exploit. If that is weakly true on VG150 (see Alternative 1), the split's verdict on any debiasing method is mostly a statement about the benchmark. The paper does not measure this premise.

### Observations (Non-Defects)

- **Disclosure.** The supplement lays out every adverse configuration: shared temperature, log score, label shift, subject-only grouping and minimum cell size. Most of the counter-evidence used above comes from the authors' own tables.
- **Mechanism.** The branch decomposition of TDE (Supp O.1, Tabs. 20–21) is a clean, checkable mechanistic contribution that does not depend on the split's interpretation.
- **Arithmetic.** I found no arithmetic or transcription errors. The verifier traces all 298 numbers, and the 30 tests pass.
- **Literature check.** Sources used: [Structured Sparse R-CNN, arXiv 2106.10815](https://arxiv.org/pdf/2106.10815); [Chiou et al., arXiv 2107.02112](https://arxiv.org/pdf/2107.02112).
