# Peer Reviewer 2 (Domain, R2): SGG protocol and debiasing claims

Panel: CVPR 2027 simulated review, round 4, full mode. Target commit ea0efe7.
Status: `NOT_CALIBRATED`; `criteria_binding_unavailable`.
Scope: read paper_text.txt and supp_text.txt, plus results/*.json, experiments/penet_rel_nms_chunked.py and the audit scripts. No code was re-run (no torch). Numbers below are read from stored JSON.

## 1. Summary of the submission
The paper gives an exact decomposition of the gain between two frozen models into a group-level part (the gain that survives shuffling labels within a subject-object class-pair cell) and a case-level covariance part. Applied to mean recall (mR) it finds that most of the mR gain of TDE, DLFE, IETrans and PE-Net on VG150 PredCls is group-level. For TDE it adds a training-log-prior logit-adjustment control (LA), a within-cell AUC and an SGCls/SGDet replication. The statistics are careful and unusually honest about their limits. The SGG-specific claims are narrower than the abstract suggests, and several comparisons are less clean than the text states.

## 2. Findings (anchor / problem / fix)

### Major

**M1. PE-Net's headline gain mixes in a post-processing difference (rel_nms) that the baseline does not receive.**
- Anchor: Supp Q.6 (lines 1879-1883); Abstract "PE-Net ... +0.170 ... +0.024 case-level"; results/penet_official_recall.json (`replayed_without_rel_nms`); experiments/run_sgg_penet_audit.py:151.
- Problem: PE-Net's PredCls evaluator applies relation-level NMS (rel_nms). The TDE-release MOTIFS baseline is scored by the Scene-Graph-Benchmark evaluator, which to my knowledge has no rel_nms. The authors' own stored replay without rel_nms gives PE-Net mR@50 = 0.2961, R@50 = 0.6302, against 0.3142 and 0.6523 with it. About 0.018 of the 0.1703 mR gain, and 0.022 of R@50, therefore comes from the evaluator, not the model.
- Why it matters for the case-level part: rel_nms picks a pair's predicate using other overlapping pairs in the image. It can create case-level covariance that the within-pair AUC and the proper score cannot see, because both use raw probabilities. This is the same order as the reported case-level +0.0243 and the "far exceeds the floor" argument.
- The paper does not mention that the no-NMS replay exists. It says only that the chunked version "computes the same quantities".
- Fix: report the PE-Net split with and without rel_nms. Apply the same NMS to the baseline, or drop NMS for PE-Net. Re-state the abstract claim for the matching protocol.

**M2. The chunked rel_nms self-test is weak, though the end-to-end check is good.**
- Anchor: experiments/penet_rel_nms_chunked.py selftest; Supp line 1881.
- Problem: the 300 test images use random normal logits, 2-40 objects, classes 1-5 and uniform random boxes. Since each probability row sums to 1, the l21 > 0.7 branch is always true, so the threshold is never exercised. The test also never uses realistic near-duplicate-box scenes.
- Strength: reproducing the printed R@50 = 0.6523 and mR@50 = 0.3142 on the full test set is far stronger evidence than the unit test. I do not doubt the chunked implementation.
- Fix: state that the end-to-end match is the validation, and add a test on real PE-Net outputs for some hundred images.

**M3. "Prior corrections" mislabels IETrans, and the IETrans comparison cannot support a method-level conclusion.**
- Anchor: Abstract lines 021-022 ("DLFE and IETrans, also prior corrections ... 94% and 97% group-level"); Sec. 7 Conclusion ("three released prior-correcting PredCls checkpoints"); Supp O.2, Q.8.
- Problem: the released checkpoint is IETrans+Rwt. It combines training-label relabelling with a reweighted loss, plus a test-time log-prior. There is no IETrans baseline, and the MOTIFS-SUM baseline "differs in its fusion".
- Consequences: the 97% share and the AUC fall (-0.0238) compare two differently trained models. The paper concedes this in Sec. 5 and Supp O.2, but the abstract and conclusion generalise. The IETrans relabelled training data also change which triplets are "seen", so the standard zero-shot list does not describe what the model saw.
- Fix: drop "prior correction" for IETrans in the abstract and conclusion. Report it as "a released relabel+reweight system vs a different baseline" or remove it from the headline. Say explicitly that only DLFE (own baseline) and TDE (same weights) are controlled comparisons.

**M4. The "cross-release floor" is not a training-noise floor, and the abstract leans on it.**
- Anchor: Abstract lines 024-027; Tab. 1 baseD; Supp Q.6 "Training spread"; results/sgg_cross_release_floor.json.
- Problem: it is a single realised difference between two MOTIFS checkpoints from different code forks. It is not a variance estimate (the authors say so). The two baselines also differ a lot in behaviour: background mass 0.855 vs 0.682, and zero-shot R@50 0.1102 vs 0.0334 (results/dlfe_official_recall.json, sgg_audit_motifs.json). Group-level mR differs by +0.0199.
- Consequences: such differences are a fork/config gap, not seed noise. The floor therefore also mixes in implementation differences, and it says nothing about cross-architecture spread (PE-Net vs MOTIFS). The AUC floor is sign-unstable, as the paper notes, so "AUC +0.005 does not exceed 0.006" is a statement about one pair of runs. The case-level "+0.0007" floor has the same limitation.
- Fix: soften "far exceeds" in the abstract to "exceeds the one observed cross-release difference". Train 3+ seeds of one baseline, or state that no variance-based claim is made about PE-Net.

**M5. The central "TDE equals a prior shift" result is protocol-specific, and it is protocol-selected.**
- Anchor: Abstract lines 015-019; Sec. 5 "What that licenses", Tab. 2; Supp Tab. 17.
- Problem: LA with tau = 1 matches TDE at gc-K=50 only. At gc-K=100 TDE leads by +0.0300. At gc-K=20 it trails by 0.0234. Without the graph constraint the two differ by 0.08-0.15, and TDE's case-level part over LA is significant at ng-K=100 (+0.0148 [+0.0064, +0.0232]). Tau was not tuned (the LA0.5 row exists in Tab. 17 and the stored results).
- Consequences: the abstract does say "elsewhere the two differ by 0.02 to 0.15". But its framing, and Sec. 5's "reproduces the gain, its split and its tier profile", invite a stronger reading than the data give. The rank-based AUC claim is protocol-independent and is the sturdier one. It is stated only under four weightings, two of which give wide bounds and one of which has TDE falling (per-pair -0.0153). The abstract's "shows no gain" is a null result with wide per-predicate bounds (up to 0.028), as the paper itself says.
- Fix: lead with the AUC and its bounds. Present the LA match as a K=50 coincidence of the operating point. Report LA at tau in {0.5, 1, 1.5} with the same split, and per protocol.

**M6. The conclusion about "debiasing methods" rests on one checkpoint each, in PredCls only, with TDE as the sole method taken beyond PredCls.**
- Anchor: Sec. 1 "What is not claimed"; Abstract; title ("Ten Points of Mean Recall"); Supp Q.9.
- Problem: DLFE, IETrans and PE-Net were not run in SGCls or SGDet. No other debiasing family was tried (loss reweighting or resampling such as CogTree/PCPL/FGPL/SHA-GCL, relabelling such as NICE, or edge-selective transformers).
- The paper's scope statement is honest, but the title and abstract speak of "debiasing methods" and "gains in SGG". TDE's own SGCls/SGDet result is itself less clean: only 58% and 65% of relations are matched, and the AUC/proper-score results describe that subset.
- Fix: retitle or rescope ("for four released PredCls checkpoints"). Add one resampling or loss-based method (for example, a trainable one on the same baseline) as the case where case-level gain is expected; this would also test the decomposition against a known non-prior method.

### Moderate

**m1. SGDet matched-pair choice.**
- Anchor: Supp Q.9, lines 1934-1936.
- Problem: the predicate distribution is taken from the single matched pair with the largest summed IoU. The evaluator can score a hit from any of several matched pairs, and in SGDet the pair ordering uses the triple score (rel x subject x object). Detector-score effects and duplicate-pair ranking are therefore credited to the case-level part of mR. The within-cell AUC audits a different pair than the one that produced the hit.
- Fix: report how often the hit pair differs from the largest-IoU pair, and the case-level part restricted to images where they coincide.

**m2. Zero-shot list and the zero-shot evidence.**
- Anchor: Supp Q.7, Tab. 36; results/penet_official_recall.json lines 60-61.
- Problem: Tab. 36 omits PE-Net. Its official zR@50 is 0.1713 against the TDE-release baseline's 0.1102 (+0.061), the largest zero-shot gain of any model. That is the natural place for a non-prior method to show case-level discrimination, and the paper does not report the zero-shot split or AUC for it.
- A second issue: IETrans's training set drops 5,000 images and relabels, while the standard list is built from the original train. The DLFE baseline's zR@50 of 0.0334 is also 3x lower than the TDE-release baseline's, which again shows the two baselines are not interchangeable.
- Fix: add PE-Net (and DLFE) rows to the zero-shot split and AUC. State which training split defines "unseen" for each checkpoint.

**m3. Dedup in the IETrans test set.**
- Anchor: Supp O.2, Tab. 24.
- Problem: the loader removes duplicates (152,226 vs 183,642). The mapping argument is sound and the effect is small (mR@50 0.3576 to 0.3587). It is valid, but the PE-Net, DLFE and TDE audits all score the full 183,642 with SGB's duplicate-matching rules, so state that no other model's official numbers change.
- Fix: one sentence in the main text.

**m4. mR definition mismatch.**
- Anchor: Sec. 3 "Splitting mean recall"; Sec. 5 (0.0972 vs 0.1017); Q.1.
- Problem: the official mR is a mean over images of per-image per-predicate recall. The headline split is a micro-pooled w(y) = 1/(K n_y) version. Share 87% vs 84% is disclosed, but the abstract's lead number (87%) is for the non-official statistic. DLFE, IETrans and PE-Net shares are reported only for the micro version.
- Fix: report the official-statistic split for all four methods in one table.

**m5. Cell choice and pair-level shortcut.**
- Anchor: Sec. 3 "Choosing the grouping"; Sec. 5 (subject-only cells give 18%).
- Problem: the 87% depends on cells being (subject class, object class). The 18% under subject-class-only cells shows how fragile the headline is. This is argued as a limitation, but in SGG the biased signal is also image-dependent and spatial, for example the geometry or union box. MOTIFS's frequency bias is indexed by exactly this pair, so the grouping matches the baseline's bias by construction. For a method that uses spatial or context bias the "group" notion is less natural.
- Fix: state this in the abstract in one clause; add the 90% (position-refined) row to the main table.

**m6. Statistical intervals.**
- Anchor: Sec. 5 and Tab. 1.
- Problem: all intervals cover test sampling for one training run. Tab. 1 shows several secondary intervals excluding zero (DLFE AUC +0.0029 [+0.0001, +0.0055]) which the paper rightly declines to interpret. Pre-declaration is stated for DLFE and PE-Net only after TDE and IETrans were seen.
- Fix: acceptable as written; keep "post hoc for TDE and IETrans" in the abstract.

### Minor
- m7. The PE-Net mean-recall share of 86% is against a different architecture. State it beside the number in the abstract, as for IETrans.
- m8. "Ten points" in the title is TDE's mR@50 under the graph constraint. Say so in the title or first line.
- m9. Tab. 1 mixes baselines per row (MOTIFS, LA, DLFE's own, separately trained). Add a "baseline" column.
- m10. The LLM usage statement is long and says the code and the number-checking script were written by the LLM. Independent verification of the evaluator replay (Tab. 17) is therefore valuable. The numbers do match printed evaluator values (R@50 0.6612 / mR 0.1459; TDE 0.4588 / 0.2476; PE-Net 0.6523 / 0.3142; DLFE 0.5165 / 0.2686).

## 3. What I checked and found sound
- Replayed evaluator: stored `evaluator_printed` vs `replayed` agree to four decimals for TDE, DLFE, PE-Net and IETrans; `max_abs_difference_replayed_vs_stored` is 0.0.
- Group share arithmetic in the abstract (87%, 84%, 18%, 94%, 97%, 86%) matches Tab. 1.
- SGCls/SGDet: treating unmatched relations as misses for all models is the right way to keep mR well defined, and the grouping by GT class pair is sound (matched pair labels equal the GT labels).
- Zero-shot status as a label weight is valid under Theorem 1. The replay matches official zR (0.1102, 0.1432).
- The chunked rel_nms agrees with the original in the end-to-end test (see M2).
- Scope limits (single run, PredCls, no one-stage or VLM models) are stated candidly.

## 4. Literature coverage
The related-work coverage of unbiased SGG is good for a paper whose focus is evaluation. Gaps (checked by web search unless marked):
- Evaluation or metric work not cited: Knyazev et al., "Graph Density-Aware Losses for Novel Compositions in Scene Graph Generation", BMVC 2020, arXiv:2005.08230 [verified]. It treats zero-shot and few-shot evaluation and a weighted metric.
- Gao et al., "Informative Scene Graph Generation via Debiasing", arXiv:2308.05286 [verified]. It argues that mR@K misses informative predicates and proposes mRIC@K.
- Biswas et al., "Probabilistic Debiasing of Scene Graphs", arXiv:2211.06444 [verified, title and ID found; the author attribution was not confirmed].
- F@K (harmonic mean of R@K and mR@K) as an alternative headline metric: used in "Head-Tail Cooperative Learning Network for Unbiased SGG", arXiv:2308.12048 [verified]. The original source of F@K was not pinned down [UNVERIFIED]. Since the paper's argument concerns trading R@K against mR@K, an operating-point reader will expect F@K or the R/mR trade-off discussion, which exists at least from TDE.
- Possibly relevant but not verified: surveys of scene graph generation (TPAMI-level) [UNVERIFIED]; work on non-trainable post-hoc rebalancing in SGG beyond DLFE [UNVERIFIED].
- Statistical side: the decomposition is closely tied to Yates, and the paper cites it. The CVPR audience may ask for a connection to Shapley-type attribution or the Oaxaca-Blinder decomposition from economics [UNVERIFIED as a citation recommendation]; the paper does not discuss these.

## 5. Significance for the SGG community
- Value: a diagnostic that separates "predicates are named more often for the pair" from "relations are told apart" is useful. The finding that TDE's within-pair ranking does not improve is a clear message for people who report mR. The audit tooling and released replays are a contribution in themselves.
- Limits: the practical lesson (mean recall rewards operating-point shifts and prior correction) is already widely suspected, and the paper cites work saying so ([6], [26], [31], [46]). What is new is the exact accounting. The weakest part is the generalisation from four checkpoints to "debiasing methods", and M1/M3/M4 mean that two of the four comparisons are not controlled. A resampling-type method and multi-seed baselines would make the claim much stronger.
- Fit: the paper is dense with statistics (supp ~40 pages) and the main-text SGG story sits in two pages. A reader from SGG will want a single table: method, controlled baseline (yes/no), mR@50 gain, official-statistic share, AUC bounds.

## 6. Abstract claim audit
| Claim | Supported? |
|---|---|
| 87% (83-91%) of TDE mR@50 gain group-level, class-pair cells | Yes for micro mR, K=50, gc. |
| LA recovers +0.094 of +0.097 | Yes, K=50 gc only (M5). |
| TDE AUC excludes changes above 0.0038-0.028 | Yes, but only the two head-heavy weightings are tight. |
| DLFE and IETrans "also prior corrections", 94%/97% | DLFE yes; IETrans no (M3). |
| PE-Net case-level +0.024 "far exceeds" +0.001 between separately trained baselines | Not secure (M1, M4). |
| PE-Net AUC +0.005 "does not exceed" 0.006 | Honest, but based on one realised pair of runs. |

## 7. Recommendation (not calibrated)
Major revision. Accept in principle if M1 (rel_nms confound) and M3 (IETrans wording) are fixed and M4/M5/M6 are rescoped. `NOT_CALIBRATED`; `criteria_binding_unavailable` (no venue score thresholds were bound to this review).
