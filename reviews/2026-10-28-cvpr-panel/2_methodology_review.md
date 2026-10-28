# Peer Review 1 (R1, Methodology / evaluation statistics) - CVPR 2027 simulated panel, round 4

Manuscript: "What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation" (anonymous submission)
Mode: full review, role R1. Target commit requested: ea0efe7. The checked-out HEAD reports as 2300e8e with a clean working tree; I did not inspect history (instructed not to), so whether the two are the same artefact is NOT VERIFIED.
Status flags: `NOT_CALIBRATED`, `criteria_binding_unavailable` (no venue-binding rubric was available; the recommendation below is this reviewer's judgement only, not tied to a score scale).

Anchors: P# = line number of paper_text.txt (e.g. P436); S# = line number of supp_text.txt; "Abs 0xx" = abstract line numbers 001-027.

## 1. Recommendation and confidence

Recommendation: Weak Accept / borderline-accept (leaning accept), conditional on the abstract's cross-release claims being toned down or backed by a multi-seed floor.
Confidence: 4/5 on the arithmetic and estimator (I rebuilt the headline numbers independently); 3/5 on the interpretive claims about PE-Net, IETrans and zero-shot recall, which rest on n=1 releases.

One-paragraph assessment. The exact decomposition and the pairwise U-statistic estimator are correct and simple. Every headline number I rebuilt from the shipped arrays reproduces to the printed precision, including numbers the paper treats as secondary. The paper is unusually candid about protocol dependence. Its weakest part is the inference it draws from comparisons between separately trained checkpoints (PE-Net, IETrans, the "floor") and from non-detections (AUC bounds, "matched by the control"). Those inferences rest on one realised training difference, post-hoc margins and a single operating-point control, and the abstract states them more firmly than the supplement supports.

## 2. Summary of claims as understood

1. Any paired gain in a score, or in a label-weighted hit rate such as mean recall, splits exactly into a group-level part (survives within-cell label transport) and a case-level covariance part. The estimator is a U-statistic with image-clustered Hajek intervals.
2. On released PredCls checkpoints, 87% of TDE's mR@50 gain is group-level with class-pair cells. A ranking-preserving logit-adjustment control recovers +0.094 of +0.097.
3. TDE's within-pair AUC shows no gain. The 90% bound excludes changes above 0.0038 to 0.028 under four weightings.
4. DLFE and IETrans are 94% and 97% group-level. PE-Net is 86% group-level, and its case-level part (+0.024) far exceeds the spread between two separately trained baselines (+0.001), whereas its AUC change does not exceed that spread's AUC (0.006).

## 3. Recomputation log

All scripts are in /tmp/claude-0/-home-user-WAGER/06889eb3-4869-50f6-bd62-a68f44e45a32/scratchpad/r1b/. I wrote my own implementation of Eq. 4-7 and of the within-cell AUC (rank-based, per cell and label pair). I used only the shipped arrays (data/vg_motifs/*/variant_*.npz, meta.npz). Run times were under 1 minute each. The unit tests in tests/ were run: 40 passed.

| # | Quantity | Script | Mine | Paper | Status |
|---|---|---|---|---|---|
| 1 | Audit size: 183,642 relations, 7,127 cells, 5,044 cells with >=2 cases, 98.9% in those | split.py | 183,642 / 7,127 / 5,044 / 98.87% | same (P347-349) | reproduced |
| 2 | mR@50 (graph constraint, micro, eligible), TDE vs base: total / group / case | split.py | .0972 / .0841 / .0130 (share 86.6%) | .0972 / .0841 / .0130, 87% | reproduced |
| 3 | LA control vs base | split.py | .0941 / .0802 / .0139 | same | reproduced |
| 4 | TDE vs LA | split.py | .0031 / .0039 / -.0008 | same | reproduced |
| 5 | DLFE vs dlfe_base; DLFE vs dlfe_soft; dlfe_base vs TDE-release base | split2.py | .1112/.1046/.0065; .1128/.1074/.0054; .0206/.0199/.0007 | same | reproduced |
| 6 | IETrans vs base; PE-Net vs base; PE-Net vs dlfe_base | split2.py | .2204/.2143/.0060; .1703/.1460/.0243; .1497/.1261/.0236 | same (+.0236 at P523) | reproduced |
| 7 | Case-level interval by my own 40-group image delete-a-group jackknife (n_y re-estimated in each replicate) | split2.py | TDE [.0086,.0175]; LA [.0098,.0179]; PE-Net [.0191,.0294]; floor [-.0024,+.0038] | TDE [.0093,.0168] (jackknife [.0088,.0173] at P377); PE-Net [.0197,.0289]; floor [-.0016,+.0030] | point values reproduced; my intervals are 7-25% wider, see W8 |
| 8 | Within-cell AUC change, relation and comparison weighting: TDE; LA; DLFE vs soft; DLFE vs base; dlfe_base vs base; PE-Net vs base | auc.py | -.00179/+.00254; 0/0; 0/0; +.00287/+.00177; -.00603/+.00165; +.00497/+.00546 | -.0018/+.0025; 0; 0; +.0029/+.0018; -.0060/+.0017; +.0050/+.0055 | reproduced. DLFE vs dlfe_soft is exactly 0 under both weightings, as claimed |
| 9 | Pair and predicate weightings: TDE; floor (dlfe_base vs base); PE-Net vs base; PE-Net vs dlfe_base | auc2.py | pair -.0153 / pred -.0038; -.0181 / -.0256; +.0187 / -.0054; +.0368 / +.0202 | -.0153 / -.0038; -.0181 / -.0256; +.0187 / -.0054; +.0368 (S1896-1898) | reproduced |
| 10 | 90% bounds and margin checks (sgg_equivalence.json; S1840-1846) | read of results JSON; arithmetic by hand | 0.0038 / 0.0077 pass 25% of geometry gain (0.0157 / 0.0081 margins); 0.0229 passes 25% for pair (0.0345); predicate 0.0279 fails every margin (25% = 0.0174) | matches P413-421 | consistent. The 0.0077 vs 0.0081 pass is a near-tie, see W4 |
| 11 | Zero-shot split TDE vs LA (results/sgg_zeroshot_split.json, sgg_zeroshot_auc.json) | read only; torch not installed, so the zero-shot triplet list could not be loaded | +.0352 = +.0207 + .0131 [.0093,.0169] + .0014 singleton; AUC on unseen blocks -.0149 [-.0203,-.0056] (relation), -.0127 [-.0343,+.0097] (comparison) | same | stored results consistent with text; NOT recomputed |
| 12 | Share interval (sgg_share_intervals.json) | read only | .866, CI [.826,.906] (G=100 jackknife); IETrans share .973, CI [.902,1.044] | 87%, [83%,91%] | consistent |
| 13 | Multiple predicates "hit" per relation at gc@50 (evaluator-protocol check) | penet_check.py | rows with >=2 predicate hits: base 0.7%, TDE 0.7%, DLFE ~1%, PE-Net 9.7% | not reported | new finding, W2 |
| 14 | Restricting hits to the argmax predicate (crude proxy for a strict one-predicate-per-pair evaluator): PE-Net vs base | penet_check.py | total .1546, group .1296, case .0250 (full: .1703 / .1460 / .0243) | n/a | proxy only, see W2 |
| 15 | Case-level/group-level ratio R/P | split2.py | LA .17; TDE .155; PE-Net .166; DLFE vs soft .05; IETrans .03 | n/a | new, see W1 |

Not recomputed and therefore unverified by me:
- Matched proper-score splits (temperature plus per-class bias; the +0.00445, -0.00006 and -0.0184 values) and cross-fitting. I read the stored JSON only (results/sgg_primary_randomization.json).
- The official-evaluator replay (needs checkpoints, images and Colab). I could not validate the counterfactual hit_i(y) for y different from y_i against any independent implementation. The shipped rank arrays contain them but nothing else audits them.
- The TDE branch decomposition (+0.0817 from the averaged context; 99.96% energy, r=+0.75), the simulations (coverage, size), and the label-shift path.
- The declared-protocol timing statements (P365-372). This needs history, which I was told not to read.
- The 5-seed pixel study, Waterbirds, and CIFAR.

## 4. Strengths

- S1. Theorem 1/Prop. 5 are correct. I checked the algebra: with A_ij as in Eq. 6, Sum_{i<j} A_ij = 1/2[(n-1) Sum H_i(y_i) - Sum_{i!=j} H_i(y_j)], so T - P equals 2/(n(n-1)) Sum A_ij. The all-case plug-in shrinkage by (n-1)/n is real and handled.
- S2. The within-cell AUC is exactly invariant to the control. LA vs base is 0 to 1e-6, and DLFE vs dlfe_soft is exactly 0 in my independent implementation. That makes it the right instrument for a ranking claim.
- S3. Candour about dependence on the grouping, calibration family (sign of TDE's quadratic case-level part flips: -0.00006 / -0.0184 / +0.00445), weighting, label mix and K. Tab. 27 collects every TDE quantity. The 87%/90%/84%/18% share table is honest.
- S4. Reproducibility is better than typical: the per-relation arrays are shipped, and every number I attempted is recoverable in seconds.
- S5. The control design (a ranking-preserving shift) is a good idea. It exposes that a "debiasing" gain can be reproduced with no learning.

## 5. Weaknesses (each with anchor, problem, fix)

### Major

**W1. The PE-Net case-level claim ("far exceeds the +0.001 floor", so "not training noise") tests the wrong null.**
Anchors: Abs 023-027; P519-522; P603-605; S1893-1899.
Problems:
(a) The floor is one realised difference between two MOTIFS baselines from different releases (the paper says "one realised difference, not a variance estimate", S1893-94). A single draw of 0.0007 cannot bound the variability of training differences. The abstract nonetheless presents it as a floor.
(b) PE-Net is compared with a baseline of a different architecture and training pipeline. Its +0.0243 therefore mixes method, backbone, loss and tuning, and calling it a "prototype-based method" effect (P513) is not identified.
(c) The relevant null for a thresholded metric is the operating-point control, which the paper itself builds for TDE (P350-359, P468-471). No such control exists for PE-Net. My recompute of R/P (case-level over group-level) is 0.166 for PE-Net against 0.17 for the LA control (+0.0139 on +0.0802), 0.155 for TDE, 0.05 for DLFE vs its soft network and 0.03 for IETrans. PE-Net's +0.0243 on a +0.146 group-level part is exactly the proportion a pure prior shift produced on the baseline. That does not show PE-Net's case-level part is operating-point, but it means the data do not exclude it.
(d) Evaluation-protocol mismatch. PE-Net is scored with its own relation-NMS evaluator (S1879-1883). At gc@50, 9.7% of ground-truth rows have two or more predicates counted as hits for PE-Net, against 0.7% for MOTIFS/TDE and about 1% for DLFE. A strict one-predicate-per-pair graph constraint is not what PE-Net is being held to. A crude argmax-only proxy lowers PE-Net's ΔmR from .1703 to .1546, a 9% drop in the headline, and leaves its case-level part at .0250. So the conclusion on case-level survives the proxy, but the +0.170 and the 86% share are protocol-dependent, and the manuscript does not say so.
Fix: (i) apply the LA/prior-shift control to PE-Net's own scores (its logits are available in the dumps) and report PE-Net-vs-control as for TDE; (ii) rescore PE-Net under the same strict graph-constraint evaluator as the others, or state that the gain compares two evaluators; (iii) say "release-to-release difference between architectures" rather than "method effect", and move the training-noise language out of the abstract until a floor with several seeds exists.

**W2. The AUC half of the PE-Net sentence is selective.**
Anchors: Abs 026-027; P524-527; S1895-1899.
Problem: the abstract says PE-Net's AUC change, +0.005, "does not exceed their 0.006 spread". That is true for the relation weighting against the TDE-release baseline only. The paper's own numbers show: against the DLFE baseline PE-Net's relation-weighted AUC is +0.0110 (I reproduce it), 1.8 times the 0.0060 spread; under the pair weighting PE-Net is +0.0187 [+0.0037,+0.0337] against the TDE-release baseline and +0.0368 against the other; the spread itself has opposite sign depending on weighting (relation -0.0060, comparison +0.0017, pair -0.0181, predicate -0.0256). The body discloses these (P525-526, S1896-98), but the abstract's comparison of a signed +0.005 with an absolute 0.006 is arbitrary.
Fix: in the abstract say "its AUC change is within the range of the two-baseline difference under some weightings and outside it under others", or drop the sentence and keep "we claim no AUC gain".

**W3. Intervals cover test sampling only, but the paper makes training-difference claims that rely on them, and its own numbers show the intervals are anticonservative for that purpose.**
Anchors: P596-597; S1893-1899; P495-497; P504-509.
Problems:
- DLFE vs its release baseline has AUC +0.0029 [+0.0001,+0.0055]. The paper attributes this to a training difference (P495-496; S1872-73). That is a 95% interval that excludes zero for a difference the authors themselves call training noise.
- The floor itself, -0.0060 [-0.0099,-0.0011], excludes zero.
- The text then reads the IETrans fall (-0.0238) as "four times" this one-draw spread (S1900). Under the weightings closer to mean recall, IETrans is only 1.5 times the floor: pair -0.0274 vs -0.0181; predicate -0.0362 vs -0.0256. (Floor values from S1896-97 and Tab. 32 at S1819-22; both reproduce.) IETrans also has no baseline of its own (P509).
- DLFE's soft network and its baseline have nearly identical mR@50 (0.1647 for both in the shipped summary) but still differ in AUC by +0.0029 and in case-level part by +0.0011, a second implicit floor datum that is not used.
Fix: train three to five seeds of the MOTIFS baseline (Colab GPU is available; one run is the cost of a stage-1 job) and report the spread of case-level part and of each AUC weighting. Otherwise remove "floor" from the abstract and say "one realised cross-release difference". Add the soft-vs-base pair as a second datum.

**W4. The AUC "no gain" bounds are post hoc, scaled by an arbitrary yardstick, and uninformative exactly where mean recall lives.**
Anchors: Abs 019-022; P405-430; S1835-1846; S1816-1820.
Problems:
- The margins are fractions (5/10/25%) of "what box geometry buys over class pair" on a different, reconstructed 70/30 split and a different model family (P316-324). The paper admits "No margin was registered before the audit" and that they "were set after TDE's results were seen" (S1845, P421-423). The yardstick differs by weighting by a factor of four (0.032 to 0.138) with no principled link to mean recall.
- The primary weighting (relation) is also post hoc for TDE (P365-368) and is the one with the tightest bound (0.0038). The comparison weighting, which gives +0.0025, passes only the 25% margin, by a near-tie (bound 0.0077 vs margin 0.0081).
- The weighting that mirrors mean recall (per predicate) gives a bound of 0.0279 and passes no margin; the paper says so (P419-421), but the abstract's "no gain ... tightly only under the two that favour head predicates" can be read as stronger evidence than it is. Absence of a detected gain under the tail-sensitive weightings is mostly lack of power (tail-tail -0.097, [-0.228,+0.024], 0% of weight).
- On head-head comparisons TDE is +0.0067, [-0.00004,+0.0146] (S1821-23), a borderline positive that is relegated to "a pattern".
Fix: state the bound in absolute AUC points next to the baseline AUC (0.61/0.57), not only as a share of a different model's gain. Present the predicate-weighted bound as "not resolved". Report the head-head subgroup interval in the main text. Delete "tightly" or define it. If the margins are kept, label them explicitly exploratory in the abstract.

**W5. "A logit adjustment ... recovers +0.094 of +0.097" is a single control at one operating point; the paper's own data show the operating-point component of the case-level part varies by a factor of three or more.**
Anchors: Abs 015-019; P395-405; P428-430; Tab. 2.
Problems:
- TDE-vs-LA case-level is -0.0008 [-0.0050,+0.0033]. The paper itself says this excludes only changes above 0.0043, a third of TDE's own case-level part (P428-430). The control matches TDE in the sense of not rejecting, not in the sense of equivalence.
- The control is not operating-point matched: R@50 is 0.644 for LA and 0.459 for TDE (P357, P450), and the mass given to no relation is 0.651 vs 0.021 (P463). Across prior-type shifts the case-level/group-level ratio is 0.17 (LA), 0.05 (DLFE vs its own soft network), 0.03 (IETrans), so whether a given shift yields +0.005 or +0.014 depends on the network and the shift. A single tau=1 control cannot calibrate that. The results folder also holds a tau=0.5 control (sgg_recall_split_la0.5_vs_none.json), which suggests a tau family exists, but only tau=1 is reported in the paper.
- The match holds only at K=50 with the graph constraint (Tab. 2); at ng@50/@100 TDE-LA case-level is +0.0072 [-0.0001,+0.0145] / +0.0148 [+0.0064,+0.0232]. All six TDE-vs-LA case-level estimates are non-negative apart from -0.0008 at the headline protocol, which is also the protocol selected as primary after TDE was seen (P365-368).
Fix: report the TDE-vs-control comparison against a tau sweep (or against a control tuned to TDE's R@50 or to its no-relation mass), and state the largest change excluded in the abstract. Put Tab. 2 TDE-vs-LA in the main claim.

**W6. Zero-shot result is a post-hoc subset with a mechanism asserted, not tested.**
Anchors: P483-486; S1902-1917; Tab. 36.
Problems:
- The "unseen-triplet" AUC subset (11% of weight) is defined after seeing the zero-shot recall result. Its interval excludes zero under relation weighting (-0.0149 [-0.0203,-0.0056]) but not under comparison weighting (-0.0127 [-0.0343,+0.0097]). The text quotes only the first in P485-486.
- "TDE's zero-shot advantage is an operating point that happens to favour unseen triplets" (S1915-17) is an interpretation. It is supported by a non-detection of AUC gain plus a fall in one weighting, but no operating-point-matched control for zero-shot recall exists. The LA control lowers zero-shot recall (-0.004), which is a different shift from TDE's.
- The case-level part is +0.0131 (against control) and +0.0186 (against base, 50% of identified change; sgg_zeroshot_split.json). The paper reads these as non-discrimination.
Fix: mark the subset as post hoc; report both weightings together; either run the tau sweep of W5 on zero-shot hits or soften to "consistent with".

### Moderate

**W7. Matching protocol: primary family is chosen so that the control comes out exactly zero, and the TDE result under it is a single post-hoc half.**
Anchors: P244-252; P431-444; S1709-1731; Tab. 28, 35.
Problem: the criterion (a family that removes any global log-prior shift) is principled, but it was declared after TDE and IETrans results were seen (P365-368), and it forces LA's case-level part to 0, so TDE's +0.00445 [p=.001] is the residual against a family designed around the control. The sign of TDE's part flips with family (temperature -0.00006; shared T -0.0184; primary +0.0044; log +0.044/-0.093/+0.025). The headline +0.00445 uses one calibration half (seed 20260811); the 20-half mean is +0.00397 and the cross-fitted value +0.00399, with an upper range +0.00482. The paper does say "ranking is read from the AUC alone", which is the right conclusion.
Fix: report the cross-fitted value and the 20-half range in the main text, not the single half. State in the abstract-level text that proper-score case-level parts are not ranking evidence.

**W8. Interval construction for mean recall: finite-sample and weight-estimation issues.**
Anchors: P253-262 (hit contrast with w(y)=1/(K n_y)); S920-932 (Theorem 4, bounded H); P236 (coverage claims).
Problems:
- Theorem 4 needs |H| <= M. For mean recall H = N/(50 n_y) Δhit, so M scales as 1/n_y for the rarest predicates; tail tiers and the per-predicate intervals in Fig. 3 and Tab. 36 are therefore outside the regime the simulation validated (96.3% coverage is for relation-level quantities, P299-301).
- My own delete-a-group jackknife (40 groups, n_y re-estimated per replicate) is 7-25% wider than the printed Hajek intervals, most visibly for the floor ([-.0024,+.0038] vs [-.0016,+.0030]); the paper's own jackknife for TDE ([+.0088,+.0173], P377) is closer to mine than to Tab. 1's [+.0093,+.0168]. The conclusions are unchanged, but Tab. 1 intervals look slightly narrow because n_y appears to be treated as fixed. The delta matters most for the floor, the one interval used as a threshold.
- The share interval for IETrans is [0.90,1.04] (sgg_share_intervals.json), i.e. above 100%, yet the abstract states "97%" without it.
Fix: use the jackknife (or a ratio-delta method including n_y) for all mean-recall intervals; state coverage for tail tiers separately or flag them descriptive.

**W9. The group-level share is determined by the declared cell, and "finest grouping is the conservative choice" is not established.**
Anchors: P279-286 (Prop. 3, "either sign"); P380-385; Abs 014-016.
Problem: for any model difference that is a function of the pair (the MOTIFS prior is indexed by the pair), the share is 100% by Theorem 1 at the finest cell. TDE's 87% is partly mechanical for that reason. Prop. 3 says merging cells shifts the split by a between-cell term "of either sign", so "finest is conservative" cannot be justified in general. The abstract mentions 18% for subject-only cells, which is honest, but the conclusion that TDE is "group-level" is a statement about the class-pair cell.
Fix: reword "conservative" as "default"; report the share on a few pre-declared refinements (object position, subject size give 90%, P381-382) in the main Tab. 1 with the reason one would stop.

**W10. Label ambiguity is probed with two author-built merges and a ceiling that ignores annotator disagreement.**
Anchors: S1918-1926; S1753-1773.
Problems:
- The synonym (32 classes) and coarse (3 classes) schemes are author-defined, and merging breaks exact invariance of the control (up to 0.0013 AUC, S1925-26). The claim "synonymy does not explain" IETrans's fall rests on those groups only; other near-synonyms (holding/carrying, looking at/watching) stay separate.
- A third of audited relations share image, boxes and cell with another relation of a different predicate (33.1% per sgg_cross_image.json; S1744), i.e. the benchmark already contains multi-label ground truth for a third of inputs. The AUC ceiling of 0.9996 is computed only from ties between those duplicates; the paper itself says annotator style cannot be measured (S1772-73), but the duplicates give a direct estimate of ambiguity.
Fix: add an ambiguity-aware AUC that treats the other recorded label(s) of the same input as non-negatives to be excluded (or counts only comparisons between labels never co-annotated on a same-image duplicate), and report TDE/IETrans/PE-Net under it.

**W11. Multiplicity.**
Anchors: P370-372; Tab. 27; Tab. 32; S2154 onward.
Problem: the paper correctly says one excluded-zero secondary interval is not a finding, but it then reads several secondary results as findings: IETrans's fall (relation weighting; comparison weighting barely excludes zero at -0.0001, S1822), TDE's per-pair fall (called exploratory), the unseen-triplet AUC, the DLFE AUC (+0.0029), and the TDE ng@100 case-level positive. There are on the order of 30 TDE intervals in Tab. 27 and Tab. 32 alone, with no family-wise or false-discovery treatment.
Fix: designate the confirmatory set in advance of the next release (K=50 gc mR split; relation AUC), report everything else with a stated, loose multiplicity convention, and use that convention consistently in the text.

### Minor

- M1. Audit-size inconsistencies: the AUC and cross-release analyses use 183,639 relations (results JSON; three rows dropped, S1759) while the text says "the same 183,642 relations" (S1861, S1883). Zero-shot relation count is 8,845 (text) vs 8,844 (zero-shot AUC JSON).
- M2. Simulation evidence: the null size 0.030 comes from 200 datasets (binomial 95% range about 0.02-0.09) and 94.0% coverage from 500 runs (SE about 1 pt), so they cannot detect size distortions smaller than 3-5 points. The simulation also fails at two cases per cell (81.5%). In VG150 these small cells hold 1% of relations (cells of size 2: 919 cells, 1,838 relations; cells of size <=4: 2.8%; my count), so this matters mostly for per-predicate tails.
- M3. The official statistic is split by a label shuffle (S1732-1743) because Theorem 1 does not apply; the paper itself notes a shortcut in the shuffle flips the sign (-0.0216). The "84% of the official statistic" in the abstract thus relies on a different estimator than the 87%; say so there.
- M4. Counterfactual hit_i(y) for unrecorded labels comes from replaying the first-hit rank under a different label. The observed-label replay matches the official evaluator to 4 decimals (P343-345), but nothing validates the unobserved-label side. A cheap test: for pairs with two recorded predicates, check that hit_i(y_j) from the stored rank matches the evaluator's own result for relation j.
- M5. Reproducibility: replay needs Colab, Google Drive and OneDrive links (colab_dlfe_stage1.py etc.); PE-Net uses a row-blocked NMS verified on 300 images (S1880-81). The timing statements on the declared protocol (P365-368) are not checkable from the artefact; add a signed, dated pre-declaration file to the supplement.
- M6. The LLM usage statement (P609-622) says LLMs "wrote and ran the analysis library" and "the script that checks every number"; that is disclosed. As a reviewer I note that my recomputation was an independent reimplementation and is the real check on the code.

## 6. Abstract claim-by-claim check

| Claim (abstract) | Supported by | Verdict |
|---|---|---|
| Exact split of a gain in a proper score or in mean recall, image-clustered intervals | Thm 1-4, tests, my recompute | supported (Theorem 4's boundedness is strained for per-predicate intervals, W8) |
| 87% (83-91%) group-level; 84% official; 18% subject cells | Tab. 1; share_intervals.json | supported; depends on the cell, W9 |
| LA recovers +0.094 of +0.097; elsewhere differ by 0.02 to 0.15 | Tab. 2 | supported as stated; the equivalence is weak, W5. Differences in Tab. 2 are -.0234, +.0031, +.0300, -.0792, -.1272, -.1549, so "0.02 to 0.15" omits the +.0031 protocol it highlights and rounds .155 down |
| TDE's AUC excludes changes above 0.0038 to 0.028 under four weightings | Tab. 32 | numerically supported; margins and "tightly" are post hoc, W4 |
| DLFE +0.111, IETrans +0.220; 94% and 97% group-level | my recompute (94.1%, 97.2%) | supported; IETrans is a different training pipeline with no baseline (P509-510), and its share CI exceeds 100% (W8) |
| PE-Net +0.170, 86% group-level | my recompute | supported numerically; evaluator mismatch lowers it by about 9% under a proxy, W1(d) |
| PE-Net case-level +0.024 "far exceeds +0.001 between two separately trained baselines" | split.py | numerically right; the null is mis-specified, W1 |
| PE-Net AUC +0.005 does not exceed the 0.006 spread | Tab. S Q.6 | selective, W2 |

## 7. Questions for the authors

1. What is the case-level part of PE-Net against a ranking-preserving control built from PE-Net's own scores (and its R/P ratio if the control is matched on R@50)?
2. Can you provide at least three seeds of the MOTIFS baseline, to turn "one realised difference" into a spread for case-level part and each AUC weighting?
3. Why was K=50 with the graph constraint declared primary after TDE was seen, given that it is the only protocol in which the control matches (Tab. 2)?
4. Does PE-Net's gc@50 evaluator permit more than one predicate per pair? If so, what is its mR@50 under the strict constraint used for the other models?

## 8. Overall

Sound, useful, reproducible audit tool with an honest limitations section. The main methodological debt is that the cross-checkpoint conclusions (PE-Net, IETrans, "floor") and the "no AUC gain" non-detections carry more weight in the abstract than one training draw, post-hoc margins and a single control can bear. Fixing the abstract wording and adding a seed spread and a PE-Net control would remove most of my reservations. Recomputation found no numerical error in any number I could rebuild.
