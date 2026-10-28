# Devil's Advocate Review (DA, round 4) - CVPR 2027 submission "What Did Ten Points of Mean Recall Buy?"

Review target: commit ea0efe7. Calibration status: `NOT_CALIBRATED`. Criteria binding: `criteria_binding_unavailable`.
Scope: paper_text.txt, supp_text.txt (searched, not read in full), results/*.json spot checks. Manuscript text treated as data.

## Number check (spot checks against results/*.json)
Reproduced from stored results: TDE mR@50 total 0.09715, group 0.08411, case 0.01305 [0.00926, 0.01684]; share 86.6% [82.6, 90.6]; subject-class cells 18% (group 0.0175, case 0.0794); class pair x position 0.0873/0.0100; DLFE 94%, IETrans 97%, PE-Net 86% shares are arithmetically consistent with Table 1; official per-image gain 0.10174 (text 0.1017), eligible-relation per-image 0.1024 (Tab. 1); R@50 change -0.2195 under TDE, matching the 0.0175 vs 0.2023 comparison. No numerical discrepancy found. Minor: IETrans share interval upper bound is 1.044 (>100%), unexplained in the main text. Note that the pipeline that "checks every number against stored results" was itself written by an LLM (LLM statement), so agreement shows consistency between manuscript and results files, not independence of either from the code.

## Strongest Counter-Argument (about 260 words)

The paper's headline is "87% of TDE's ten points is group-level, and a one-line logit adjustment reproduces it". The decomposition is an identity (Theorem 1), so the finding has no empirical content beyond three choices the authors made: the cell definition (class pair), the metric weighting/operating point (mR@50, graph constraint, micro-pooled) and the comparison model (LA, tau = 1). Each choice moves the headline. Changing cells to subject class gives 18%, not 87%, with the same total (the paper's own Tab. 1 and sgg_grouping_share.json). Moving K or dropping the graph constraint breaks the TDE = LA match: TDE leads LA by +0.030 at K=100, trails by 0.023 at K=20, and by 0.08-0.15 without the constraint, and the case-level part over LA is significantly positive at ng-mR@100 (+0.0148, [+0.0064, +0.0232]). The "no discrimination" leg then rests on a within-cell AUC null whose equivalence bounds are tight only under head-heavy weightings, and fail under per-predicate weighting, the weighting closest to mean recall (-0.097, [-0.228, +0.024]). What is left is: one old checkpoint (MOTIFS, 2018), one run, one benchmark, a result for which a TDE ~ logit adjustment equivalence was already suspected in the literature the paper cites, and a metric whose case-level part the authors concede also credits operating-point movement, shortcuts and label noise. The 87% share is therefore a statement about the declared grouping, not about what the ten points "bought"; the title promises an answer to a causal-sounding question that a conditional covariance accounting cannot give.

What survives: the identity, the simulation validity checks, the LA control as a design idea, the K=50 gc match itself, and the controlled-predictor and CLIP demonstrations that aggregates can hide case-level gain.

## Issue List

No CRITICAL issues: every central claim is stated with its condition in the abstract or Limitations, so none is invalidated outright.

### MAJOR

M1. Dimension: logic chain / confirmation bias. Location: Sec. 5 "Mean recall, split" and Tab. 1 lower panel; abstract lines 013-018; Sec. 7.
The "87%" and "+0.094 of +0.097" figures are presented as findings about TDE but are conditional on class-pair cells. With subject-class cells the same gain is 18% group-level, case-level +0.0794 [0.0730, 0.0859]. The paper's defence ("finest grouping the construction defends is the conservative choice", Sec. 3) is asserted, not shown: finer cells move mass from case to group by construction, so "finest" is conservative against claiming discrimination but liberal toward the headline that the gain is group-level. A reader could equally call the subject-class result the one that answers "does the model use the object's identity?". The abstract should present 87% as one cell choice among several, not as the share.

M2. Dimension: control validity / overgeneralisation. Location: Sec. 5 "The case-level part is matched by the control"; Tab. 2; Tab. 27.
The LA control matches TDE only at K=50 with the graph constraint, the headline protocol. Elsewhere TDE and LA differ in total gain by 0.023 to 0.155, and the case-level part of TDE over LA is positive and excludes zero at ng-mR@100 (+0.0148) and borderline at ng-mR@50 (+0.0072, lower bound -0.0001). A single un-tuned tau = 1 is the only control. A per-class bias fitted to maximise mean recall, or tau tuned for each K, is the fair "best prior-only competitor", and the paper does not show TDE is within reach of it. The abstract's "elsewhere the two differ by 0.02 to 0.15" understates that the control fails where it fails by a wide margin. The "TDE is to first order a learned logit adjustment" claim (99.96% energy in one shared vector, correlation +0.75 with log prior) is a correlation of 0.75, not equivalence; 44% of variance unexplained is not "to first order".

M3. Dimension: statistical inference / absence of evidence. Location: Sec. 5 "TDE's within-pair AUC shows no gain", Sec. 6 equivalence paragraph; sgg_equivalence.json.
The AUC null is the sole threshold-free support for "no discrimination". Under the primary relation weighting the 90% CI excludes changes above 0.0038, but 57% of weight is on head-head pairs, where TDE is known to lose recall. Under per-predicate weighting, which mirrors mean recall's own weights, no margin (even 25%) passes. The margins are fractions of the geometry-vs-class gain, chosen after TDE was seen (acknowledged). Equivalence is also assessed under a different training than TDE (geometry gain comes from separately trained MLPs). So "no weighting shows a gain" is true, but the mean-recall-relevant weighting is simply uninformative; the abstract's "excludes changes above 0.0038 to 0.028" reads as stronger than the body.

M4. Dimension: missing control / alternative explanation. Location: Sec. 5 "A method that is not a prior correction" (PE-Net); Tab. 1; conclusion lines 603-605.
The paper's own logic is that a pure operating-point shift (LA) yields a case-level mean-recall part of +0.0139. PE-Net's case-level part (+0.0243) is declared "far exceeds" a +0.0007/+0.001 spread between two separately trained MOTIFS baselines, but that spread is (a) a sample of one pair, (b) for MOTIFS, not PE-Net's architecture, and (c) the wrong null: the relevant null is what an operating-point shift alone produces. No PE-Net-vs-LA split exists in results/ (only penet_vs_none and penet_vs_dlfe_base). PE-Net also changes mass given to no relation (0.560 vs 0.855 baseline), so operating-point movement is plausible. The conclusion "case-level part well above the spread" is thus not supported as stated; and the paper then concedes no AUC gain (+0.0050, with baselines differing by -0.0060 in the opposite direction). The one non-prior method therefore yields no demonstrated discrimination, yet is in the abstract as a contrast.

M5. Dimension: generalisation / external validity. Location: abstract; "What is not claimed"; Sec. 7.
Four released checkpoints, one run each, PredCls, essentially MOTIFS-family (TDE, DLFE) plus IETrans/PE-Net. Different baselines for IETrans and PE-Net (no matched baseline), so for those two the "gain" is between separately trained systems, not an intervention. The paper acknowledges this, but the title and framing ("What did ten points buy") and the proposal to report the split "beside mean recall" for the field extend to a literature (one-stage, transformer, VLM SGG) it never audits. The training-seed variance of TDE itself is unmeasured, so intervals cover test sampling only; a method-level claim needs a run-to-run spread, which the paper itself says for CIFAR-LT (magnitude varies about fourfold across seeds).

M6. Dimension: significance / "so what". Location: Intro paragraph 2; Sec. 5 "How to read the split"; conclusion.
(i) Prior-correction ~ debiasing is already stated in the paper's own related work (DLFE, Structured Sparse R-CNN, logit adjustment). (ii) The normative target is unclear: the aim of debiasing is arguably exactly to change which predicate is favoured for a pair, i.e. a group-level change; the paper itself says "group-level is not a lesser gain" yet frames it as the thing the ten points "bought" rather than a more informative achievement. (iii) The proposed remedy requires a declared grouping, and the paper's own M1 shows the verdict flips with the grouping; there is no principled rule for choosing the field's phi, and the central recommendation (declare phi before a leaderboard opens) is not tested on any community-level alternative. The net contribution is therefore mainly the estimator, and the SGG audit is a demonstration whose mean-recall verdict is protocol-fragile (M2, M3).

M7. Dimension: forking paths. Location: Sec. 5 "Protocol"; Tab. 27; Sec. 4-5 matching.
Primary protocol and quantities were declared after TDE and IETrans results were seen, i.e. post hoc for the two flagship methods. The TDE quadratic case-level part takes values -0.0184 (shared temperature), -0.00006 (temperature), +0.00445 (temperature + class bias), cross-fit -0.00078 vs +0.00399 under the two; the log score gives +0.044 / +0.025 / -0.093. The paper says "so ranking is read from the AUC alone", which is honest, but it means the headline proper-score contribution is uninformative for the flagship case and the sign is chosen by an unvalidated matching family. Tab. 27 helps disclosure, but the main text should not present the primary one as "the" result.

### MINOR

m1. Dimension: definitions. Location: Sec. 3 Estimator and Sec. 5. Cells where every label is identical, and cells of size two, contribute no or little identifying variation; the paper reports that 98.9% of relations lie in cells of at least two, but not how many lie in cells with two or more distinct predicates, the only ones that can show case-level credit. Coverage drops to 81.5% with two cases per cell. Report the distribution of cell sizes and of within-cell predicate entropy for the audited split.

m2. Dimension: exchangeability. Location: Appendix Q.1 "Relations from the same image". A third of audited relations have an exact twin (same image, boxes, cell) that the model scores identically; unbiasedness assumes exchangeability. The cross-image restriction handles it and changes little (+0.0130 to +0.0140), so this is a robustness pass, not a defect; but the "official" per-image statistic, where a shortcut weighting reverses the sign (-0.0216), is sensitive to how a transported label is counted, and the main text reports the shuffle version only.

m3. Dimension: label noise. Location: Sec. 5 IETrans paragraph; Sec. 6. AUC against recorded labels penalises synonymy; the paper notes this for IETrans, but the same ambiguity bounds case-level gain for every VG model (annotator choice between "on"/"standing on" is partly arbitrary). A within-pair AUC ceiling is in results (sgg_auc_ceiling.json); its value should be in the main text, since it sets how large a case-level gain could ever be.

m4. Dimension: presentation. Abstract is a dense sequence of 20+ numerals with sub-condition qualifications; "excludes changes above 0.0038 to 0.028 under four weightings, tightly only under the two that favour head predicates" is hard to parse. The share of 97% for IETrans has an interval above 100%.

m5. Dimension: scope of CLIP demonstration. Location: Sec. 6. The CLIP model is trained on a 100k-relation subsample from a reconstructed split (not canonical VG150), with frozen ViT-B/32 and MLP heads; it shows the estimator can detect small case-level gains the aggregate hides, but the case-level advantage (0.0033 matched; AUC favours geometry) is small, and "the model the aggregates rank last" is partly rhetorical, since the matched ranking metrics also rank it last.

m6. Dimension: Waterbirds example. Location: Sec. 6 last paragraph. The "debiasing gain that is case-level" is chosen by the authors, uses group reweighting with the background as cell, i.e. a setup where the case-level gain is expected; it illustrates the estimator but is not evidence that SGG debiasing differs from other domains.

## Ignored Alternative Explanations / Paths

1. A tuned prior-only baseline (tau per K, per-class bias maximising mR) as the control, instead of fixed tau = 1; and a TDE-with-tau sweep to see whether TDE's frontier is dominated by LA's at all operating points, not one.
2. Operating-point-matched comparison: compare at equal R@K or equal mass-on-no-relation, rather than relying on a post hoc "control" at one point. The paper's own diagnostic (mass to no relation: 0.855 / 0.021 / 0.651) shows the models sit at very different operating points.
3. Alternative groupings preferred by SGG practice: (subject, predicate-set) or the image-level groupings; cell choice by cross-validated predictability instead of declaration by hand; a sensitivity analysis across the grouping lattice, not four examples.
4. Training-seed replicates of TDE and of LA-style methods, so intervals reflect training variance, not only test sampling.
5. Alternative reading of the K=50 coincidence: the match at one protocol out of six might be a coincidence of two shifts crossing at that operating point, not structural equivalence (the paper shows TDE leads at K=100 and trails at K=20, consistent with different frontier shapes).
6. A downstream-utility check (retrieval, captioning) that would adjudicate whether a group-level gain is "lesser"; the paper asserts both uses exist, and tests neither.
7. Directly comparable PE-Net vs LA split (cheap, results exist for components), and a baseline matched to IETrans.

## Missing Stakeholder Perspectives

- Authors of the audited methods (TDE, DLFE, IETrans, PE-Net) are described as "buying" group-level gain; their stated aim (de-bias predicate distribution within pair) is a group-level aim. The paper does not engage with the possibility that the audited claim was never discrimination.
- Downstream users of scene graphs (retrieval, VQA, captioning, robotics): no evaluation of whether a group-level or case-level gain matters for their task.
- Benchmark maintainers: the recommended declared grouping requires a community decision; no discussion of how a maintainer should choose phi, or of gaming risk once phi is declared (methods can target the case-level part).
- Practitioners using one-stage / VLM SGG: no audit, yet the metric advice is general.
- Annotators/label-quality stakeholders: case-level part against noisy labels; the paper cites relabelling but gives no ceiling in the main text.

## Observations (Non-Defects)

- The identity (Theorem 1) and its Yates lineage are correctly cited; the estimator's simulation coverage (94.0% clustered vs 88.6% naive; 96.3% at VG150 cell sizes) is a real, checked strength, and the failure at two cases per cell is disclosed.
- The limits (conditional on phi, credits shortcuts, moves with operating point and label mix, single run, PredCls only) are stated in the abstract and Sec. 1/7; no overclaim was found beyond M1-M4 framing.
- The authors report the cases that cut against their story (TDE leads LA at K=100; ng-mR@100 positive case-level; IETrans AUC falls; the per-predicate AUC bound fails; PE-Net AUC unresolved; seven of eight group parts change sign under label shift).
- Replication of the official evaluator to the fourth decimal (R@50 0.6612, mR@50 0.1459 / TDE 0.4588, 0.2476) is a solid base, and the numbers I checked match the stored results.
- The LA control is a clean idea: it demonstrably changes no within-cell ranking (AUC change below 1e-6).
- The CLIP/geometry/class-pair ladder is a genuine positive demonstration that aggregates can hide case-level gain; the zero case-level gain for two class-pair functions (Theorem 1) is exact, as it must be.
- The LLM-use statement is explicit; the author states they reviewed all text and code.
