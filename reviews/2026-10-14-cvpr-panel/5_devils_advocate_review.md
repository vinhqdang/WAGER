# Devil's Advocate Review (DA), CVPR 2027 simulated panel, round 3

Manuscript: "What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation". Review target: commit 6b8f1b9.
Status: NOT_CALIBRATED; criteria_binding_unavailable (no venue rubric bound; judgments are from the DA role only).
Scope: paper_text.txt, supp_text.txt, and spot checks of results/*.json (sgg_grouping_share.json, sgg_share_intervals.json, sgg_recall_split_TDE_vs_la1.json header, Table 27 in the supplement). The spot-checked headline numbers match: 0.0972 total, 0.0841 group, 0.0130 case, 86.6% share with CI [82.6, 90.6], subject-class cells 0.0175 group / 0.0794 case, 5,044 cells, 98.9% coverage.

## 1. Strongest Counter-Argument (about 270 words)

The headline "87% of TDE's ten points is group-level" is close to a restatement of how the baseline is built, and the decomposition adds less than it appears to. In MOTIFS-SUM the frequency prior is indexed by the object pair, and TDE subtracts the context-averaged sum. The paper's own mechanistic result is that TDE's change is, to 99.96% of its energy, one vector shared by every relation and correlated +0.75 with the log training prior (Sec. 5, "Why"). That finding comes from reading the logits. It does not need the transport construction. Once it is known that the change is a global logit shift, "it changes no within-pair ranking and is therefore mostly group-level" follows from the design, and the decomposition re-derives it.

The remaining quantity, the share, is not a stable property of the method. It is 87% with class-pair cells, 18% with subject-class cells, 77% to 86% across K, and undefined or negative without the graph constraint. The control (logit adjustment) matches TDE only at K=50 with the constraint, and the authors concede this. The abstract's "0.02 to 0.15" gaps elsewhere are exactly where a reader would test generality.

The claim that TDE buys no discrimination rests on null results with margins set after the data were seen. The AUC bounds are 0.0038 to 0.028, and tail-tail comparisons are undecidable (−0.097, [−0.228, +0.024]). Mean-recall-versus-control excludes only changes above 0.0043, "a third of TDE's own", which the paper says is "too wide to call it zero". The interpretive sentence that the covariance is "bought with discrimination the baseline had" is a mechanism assertion with no direct test.

Finally, the paper concedes group-level gain is not a lesser gain, since retrieval wants it. The normative payoff, that the ten points are the wrong ten points, is then asserted for captioning and VQA with no downstream experiment.

## 2. Issue List

Nothing below invalidates a central claim as stated, because the paper scopes its claims carefully. I therefore list no CRITICAL issues. The MAJOR items are where the headline framing outruns the evidence.

### MAJOR

**M1. The share is grouping-dependent, and the "finest defensible grouping" argument is not a criterion.** Dimension: construct validity / logic chain. Location: Sec. 3 "Choosing the grouping"; Sec. 5 paragraph on cells; Tab. 1 lower panel (subject cells give 18%); Limitations ("equally fine partitions can disagree", Appendix K).
- The decomposition is only as meaningful as the declared cells, and the paper's own result moves from 87% to 18% under a coarser choice.
- The justification is that the benchmark's own object vocabulary fixes the pair. That defends class pair over subject class. It gives no principle for stopping at class pair rather than at a class pair crossed with visual attributes, which would move group-level mass into case-level.
- Refinements tried (position, subject size) leave the share at about 90%. That is reassuring but covers only two refinements, both of which keep the same pair prior.
- The "declared before the audit" claim is weakened by the paper's own protocol note: the primary protocol was fixed after TDE and IETrans results were seen (Sec. 5 "Protocol").

**M2. The ranking-null claim for TDE is an absence-of-evidence argument with post hoc margins, and it is weakest where mean recall is most sensitive (tail predicates).** Dimension: statistical inference / confirmation bias. Location: Sec. 5, "The case-level part is matched by the control", lines 396 to 427; Abstract lines 019 to 022.
- The abstract says "No weighting ... shows TDE gaining discrimination". Under the primary weighting the AUC change is −0.0018, [−0.0043, +0.0016]. Per-pair weighting, the one that gives tail predicates weight, shows a fall (−0.0153, [−0.0249, −0.0004]).
- The tail-tail comparison is "too few to decide". The primary and comparison weightings put 57% and 65% of weight on head-head pairs, which is not the region where TDE's mean-recall gains occur (the body gains +0.1224).
- The equivalence margins "were set after TDE's results were seen" (line 423 to 424).
- Against the control, the mean-recall case-level interval [−0.0050, +0.0033] excludes only changes above 0.0043. That is a third of the case-level part the paper itself reports for TDE against the baseline, and the text calls it "too wide to call it zero".
- The abstract's mean-recall-level claim is bounded by these hedges, but the Conclusion ("no weighting of TDE's within-pair AUC shows a gain") reads as stronger than the evidence.

**M3. The control matches TDE only at K=50 with the graph constraint, which is the cell where the headline was chosen.** Dimension: cherry-picking / generalization. Location: Sec. 5 "What that licenses" (lines 457 to 462); Tab. 2; Tab. 27.
- Table 2 gives TDE minus control of −.0234 (K=20), +.0031 (K=50), +.0300 (K=100) and −.0792, −.1272, −.1549 without the constraint.
- Without the constraint, TDE's case-level part over the control is +.0072 [−.0001, +.0145] at K=50 and +.0148 [+.0064, +.0232] at K=100, the latter excluding zero.
- Disclosure is honest. But the statement that "the ten points are a change in which predicates the model favours" is a K=50, constrained-protocol statement carried into the title question. The paper's SGCls and SGDet replications (Sec. 5 "Beyond PredCls") give a control that gains more than TDE, which supports it, but only 58% and 65% of relations have a matched pair there.

**M4. For two of the three "other method" audits, the comparison baseline is a separately trained model, so the group/case split mixes the method effect with training noise and the training recipe.** Dimension: causal attribution / confounding. Location: Sec. 5 "Two more methods" (IETrans, PE-Net); Tab. 1 caption.
- IETrans+Rwt differs from the baseline in data relabelling, reweighted loss and a test-time prior. PE-Net is a different architecture. There is no seed-level variance: "intervals cover test sampling, not training".
- The abstract's contrast that PE-Net "changes features rather than the prior, gains discrimination" therefore compares a single run to a single run. The paper flags this for IETrans ("does not isolate the effect of relabelling") but states the PE-Net result without equal hedging in the abstract and conclusion.
- The IETrans AUC fall (−0.0238, CI [−0.0272, −0.0187]) is explained away as possible synonymy. That explanation is untested, and it would equally weaken the AUC as the arbiter of the "ranking claim" for relabelling methods.

**M5. The case-level part is not a discrimination measure, yet it is the quantity the "so what" depends on; discrimination claims rest on the AUC alone.** Dimension: construct validity. Location: Sec. 3 (Confidence matching, operating-point paragraph); Sec. 4 (unrecorded shortcut credited +0.041); Sec. 5 (frequency-prior removal gives +0.00817 case-level with AUC change −0.00001).
- The paper shows three ways the case-level part is nonzero without any new ranking: a moved operating point (+0.0139 for the control), pair-varying prior shifts (+0.00817), and unrecorded within-cell shortcuts. A temperature-only protocol flips the sign (−0.00006 against +0.00445 under temperature plus class bias, and −0.0184 under a shared temperature).
- This is stated openly, but it means the headline pair (group-level vs case-level) is protocol-defined rather than a natural decomposition. The conclusion's recommendation to report "both parts with intervals" would put a protocol-sensitive number on leaderboards.
- Note also that the logit-adjustment control's +0.0139 case-level part means that part of the 13% "case-level" remainder is itself prior correction. In that sense 87% group-level understates the prior-correction share, and the paper's framing under-reports its own strongest finding.

**M6. Normative "so what" is under-supported.** Dimension: significance. Location: Sec. 5 "How to read the split"; Conclusion.
- The paper concedes that group-level gain is legitimate for retrieval-by-predicate and is what mean recall rewards by design. The claim that captioning or VQA would want case-level gain is an assertion, with no downstream evaluation.
- The one case where case-level and group-level disagree about model ranking (CLIP vs geometry, Sec. 6) uses a controlled MLP on a reconstructed split, not a published SGG method, so it does not show that any SGG leaderboard ordering would change.
- The related critiques that mean recall rewards prior fitting and that logit adjustment rivals debiasing methods are cited in the paper ([26], [28], [31], [46]). The incremental empirical conclusion for TDE is thus a quantification of something partly known; the incremental methodological contribution (the paired-gain form of Yates's decomposition, with clustered inference) is the real contribution and is a statistics contribution more than a vision one.

### MINOR

**m1. Generalization from four checkpoints on one architecture family.** Dimension: external validity. Location: Abstract; "What is not claimed" (lines 098 to 111). All checkpoints are Neural-Motifs PredCls, one run each. The title and the framing ("Debiasing methods ... are judged by mean recall") invite a field-level reading that the scope statement withholds. The scope statement is honest; the title and abstract opening are broader than the evidence.

**m2. Forking paths in protocol selection.** Dimension: statistical hygiene. Location: Sec. 5 "Protocol" and Tab. 27. The paper discloses that primary quantities were declared after TDE and IETrans were seen, and Tab. 27 lists about 30 TDE quantities with only two marked primary. The disclosure and the "one secondary interval is not read as a finding" rule are good practice. The 87% interval [83, 91] is a single-protocol interval and does not carry the protocol uncertainty (the quadratic case-level sign flips across matching families).

**m3. Within-image dependence handled in two ways that disagree in the tails.** Dimension: estimator validity. Location: Supp. Q.1 (per-image statistic). The official per-image statistic is not covered by Theorem 1 and is split by shuffles. A different treatment of labels in images where a predicate is absent reverses the case-level part (−0.0216). The paper chose the shuffle; this shows that the per-image split depends on an implementation convention, though the paper reports it.

**m4. A third of relations share an image with another relation in the same cell**, violating exchangeability for the estimator. The cross-image check moves TDE's case-level part from +0.0130 to +0.0140. The effect is small. It is not mentioned in the main text beyond the clustering.

**m5. Small-cell coverage.** Dimension: estimator validity. Location: Sec. 4 "Simulation"; Supp. Tab. 5, Tab. 10. Coverage falls to 81.5% with two cases per cell. VG150's own cell-size mix gives 96.3% in simulation, but the real data's heavy tail of near-minimum cells is the regime where the share's CI could be too narrow. The minimum-cell-size sensitivity in Tab. 10 is shown for the spatial-vs-class model, not for the TDE share.

**m6. Presentation density.** The main text packs many numbers, protocol variants and appendix pointers per paragraph (Sec. 5 in particular), so a reader cannot easily see which claim is primary. This is a reading-cost issue, not a validity issue.

## 3. Ignored Alternative Explanations / Paths

1. **Direct logit-level analysis without the decomposition.** The paper's own "Why" paragraph (a single shared vector correlated with the log prior) is a simpler account of TDE. A reader should be shown what the decomposition tells them that the vector analysis plus the control does not. The cleanest answer is the PE-Net and DLFE cases, but those are single-run comparisons.
2. **A fitted per-cell prior as the group-level ceiling.** The control uses one global log-prior. A cell-specific (per object-pair) Bayes-optimal prior correction would define the maximum group-level-only gain for every method, and would turn the share into a share of an attainable ceiling. The paper has an oracle headroom file in results/ (sgg_oracle_headroom.json) and an oracle contrast in Sec. 5, but not a per-cell-prior ceiling in the main text.
3. **Label ambiguity and annotation noise as an explanation for small case-level parts.** Visual Genome predicates are noisy and partly synonymous. If within-pair labels carry little recoverable signal, a null case-level part could reflect label noise and not the method's inability to discriminate. The supplement has AUC-ceiling and label-ambiguity files, but the main text does not use them to calibrate the nulls (for example, how large an AUC gain any model could achieve on these labels).
4. **Training-time effect versus test-time effect.** TDE is an inference-time intervention on a fixed network, which makes the group-level conclusion natural. For methods that alter training (IETrans, PE-Net, DLFE's baseline), the training run is a confound (see M4). Multiple training seeds per method would separate the two.
5. **Alternative groupings tied to the image.** Cells defined by scene or image type (as in the Waterbirds example) would test whether "group-level" in VG is mainly a property of the object-pair prior or of a wider context variable.
6. **Per-predicate rather than pooled reading.** The tier profile (body gains, head loses, tail unchanged) suggests TDE's effect is a redistribution among head and body predicates, with the tail essentially unaffected. That is arguably a more informative negative result about debiasing than the group/case split.

## 4. Missing Stakeholder Perspectives

- **Method authors (TDE, IETrans, DLFE, PE-Net).** The paper evaluates released checkpoints under a protocol they did not choose. IETrans's intended contribution is label correction, which by design changes what counts as the right label, and the AUC against recorded labels penalizes it. The perspective that "agreement with recorded labels" is the wrong yardstick for relabelling methods gets one sentence.
- **Downstream users (captioning, VQA, retrieval, robotics).** The "case-level matters for downstream" argument has no downstream evidence. Their real need, the right predicate on the right relation for an image, is asserted rather than measured.
- **Benchmark and leaderboard maintainers.** The proposed reporting standard (declared grouping, both parts with intervals, AUC, operating-point control) is heavy, and the paper shows the parts are protocol-sensitive. A maintainer needs a recommendation on which protocol to fix and who declares the grouping.
- **Annotators and dataset curators.** VG's within-pair label noise sets the ceiling on any case-level measurement; a curator view of how much within-pair signal is recoverable is missing from the main text.
- **Reviewers and reproducibility checkers.** Offline replay of the official evaluator is a strength (matches to four decimals). Reproducing the split needs saved logits for every branch, which many released checkpoints lack, limiting adoption.

## 5. Observations (Non-Defects)

These points hold up under adversarial reading.

- **The identity is exact and the validation is genuine.** Theorem 1 is the paired-gain form of an established covariance decomposition, and the simulation checks the right things: null at 0.030 rejection, coverage 94.0% image-clustered against 88.6% treating relations as independent, the oracle contrast (+0.5068 all case-level), and calibration-only change flagged as −0.488 on raw outputs and −0.0003 after confidence matching.
- **The scope limits are stated, not buried.** "What is not claimed", the Limitations section, and the K=20/K=100 and unconstrained divergences are all disclosed, including the sign flips and the quadratic-score protocol dependence.
- **Headline numbers reproduce.** The spot-checked results files agree with the manuscript (share 0.8657, CI [0.826, 0.906]; subject-cell result 0.0175 group / 0.0794 case; 5,044 cells; 98.9% coverage). The replay of the official evaluator reproduces published mR@50 for the baseline (0.1459) and TDE (0.2476).
- **Self-critical negative results are included.** The CLIP model's case-level gain alongside a lower top-1 accuracy, the opposite-sign label-shift behaviour, and PE-Net's AUC rise are all reported, which counters the suspicion that the paper only reports confirming cases. The PE-Net result shows the split can detect gained discrimination when it exists, which is what makes the TDE null informative.
- **The Waterbirds example shows the method is not one-directional.** A debiasing method whose gain is case-level appears, so the instrument is not hard-wired to say "group-level".
- **Pre-declaration is partially real.** DLFE and PE-Net were analysed after the protocol was fixed, so those two results are out-of-sample for the protocol choice.

## Summary counts

CRITICAL: 0. MAJOR: 6 (M1 to M6). MINOR: 6 (m1 to m6).

NOT_CALIBRATED; criteria_binding_unavailable.
