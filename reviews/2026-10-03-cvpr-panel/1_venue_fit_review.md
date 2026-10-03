# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission (anonymous, Paper ID not yet assigned)
- **Review Date**: 2026-10-03
- **Review Round**: Round 1, pre-submission simulated panel (deadline 16 November 2026)

---

## Reviewer Information

### Reviewer Role
Journal-Fit Reviewer (internal role `EIC`)

### Reviewer Identity
CVPR area chair for scene understanding and evaluation. Has handled scene-graph-generation (SGG) method papers, SGG debiasing papers, and benchmark-analysis and evaluation-metric papers at CVPR, ICCV and ECCV.

### Review Focus
Venue fit for the CVPR main conference, significance and originality relative to the SGG-debiasing and evaluation literature, empirical breadth as CVPR reviewers will judge it, and how the contribution is framed in the 8 pages. Methodological depth (estimator validity, inference, calibration protocol) belongs to another seat; I touch it only where it changes how reviewers will perceive the headline.

---

## Overall Assessment

### Recommendation
- [ ] Accept
- [ ] Minor Revision
- [x] **Major Revision**: on the CVPR scale **Weak Reject** as the paper stands. With the top three remedies below done, Borderline to Weak Accept is realistic.
- [ ] Reject

### Confidence Score
4: the paper sits in my area (SGG evaluation and benchmark analysis). I am less expert on the U-statistic inference, which I do not assess.

Confidence is an uncertainty/scope disclosure only; it never changes consensus counts, severity, decision bearing, or arbitration.

### Calibration Status
`NOT_CALIBRATED`

### Summary Assessment
The paper proposes an exact split of the proper-score difference between two frozen classifiers into a group-level part and a case-level part. The group-level part survives relabelling each test case with another case's label from the same subject–object cell; the case-level part is the within-cell prediction–label covariance. The split is validated with controlled VG predictors and simulations. It is then applied to the released MOTIFS/TDE checkpoints: once calibration is matched, TDE's change is almost entirely group-level. A frozen-CLIP predictor ranked last on aggregate metrics turns out to be the best within-pair discriminator. The idea is clean, cheap and honestly reported, and the teaser question is excellent.

As a CVPR paper, though, it under-delivers on the question its title asks. The headline audit covers one method, one backbone and one setting, and the paper itself says the method is "a group-level intervention by design" (§1, l. 84–85). The answer is never expressed in mean-recall units (§5, l. 368). The headline depends on configuration: two of five rows contradict it, and the two proper scores disagree on the sign. The positive reversal uses toy predictors on a non-canonical split. About 1.4 of the 8 pages are unused while the evidence of generality sits in the supplement.

CVPR reviewers will read this as a neat statistical tool with a narrow, somewhat expected demonstration. That makes it a likely Weak Reject or Borderline-Reject outcome today. The fixes are feasible in six weeks: a multi-method audit across the field, an exact split of mean recall itself (which the paper's own Theorem 1 already permits), and a calibration-invariant companion statistic.

---

## Strengths

### S1: A sharp, memorable question that the SGG community actually argues about
The title question and Fig. 1 are among the best framings I have seen for an evaluation paper in this area. Whether mean-recall gains reflect better visual recognition or a redistribution of predicate priors has been debated informally since MOTIFS. A reviewer grasps the question in ten seconds.
**Evidence Anchor**: `figure: Fig. 1 — (man, surfboard) within-cell relabelling teaser with the ∆T = ∆P + ∆R panel`

### S2: An exact, model-free, cheap decomposition with an operational meaning
The split needs no fitted reference model, held-out fold or tuning parameter. It costs O(NK) on cached predictions. The label-shift example gives the two parts a decision-relevant reading: a group-level gain depends on test-label frequencies matching deployment. That reading is what turns a statistical identity into an evaluation argument.
**Evidence Anchor**: `text: §3, p. 4, l. 216–219 "a group-level gain is contingent on the evaluation set's label frequencies matching deployment, and a case-level gain is not"`

### S3: Unusual candour about scope and configuration dependence
The paper reports all five configurations, including the two that contradict its reading. It has a "What is not claimed" paragraph and states its own uncomfortable sensitivity bound. Reviewers in the evaluation sub-community reward this, and it pre-empts the "cherry-picked configuration" attack.
**Evidence Anchor**: `table: Table 1 — all five rows (raw quad/log, raw subject-only, matched quad/log) reported with the matched quadratic row designated in advance`

### S4: Validation where the answer is known
The algebraic zero for two class-pair-only models, the calibration-only design that exposes a spurious −0.488 on raw outputs, and the coverage simulation under image clustering are the right controls. They answer the first question a sceptical AC asks of a new metric ("does it ever say zero when it should?").
**Evidence Anchor**: `text: §4, p. 5, l. 316–319 "That zero is algebraic, not empirical — both models are functions of the class pair alone, so Theorem 1 forces it"`

### S5: Reproducibility of the audited artefact
The audit uses the released TDE checkpoints with the authors' own code and reproduces their published mR and R numbers (I verified Table 1 and the §5 recall and accuracy figures against `results/sgg_audit_motifs.json`; they match). Code, cached predictions and a number-checking script are promised.
**Evidence Anchor**: `dataset: results/sgg_audit_motifs.json — mR@50 0.1459→0.2476, R@50 0.6612, matched quadratic ∆R −5.77e-5 [−0.00120, 0.00109], all as printed in §5 and Tab. 1`

### S6: Evidence of generality exists, though it sits in the supplement
CIFAR-100-LT across three seeds and three imbalance ratios, with a post-hoc logit-adjustment arm, plus 20-Newsgroups-LT, show the estimator transfers. The calibration-matched CIFAR result (DRW's gain becomes almost entirely case-level) is the kind of "reverses the raw reading" finding reviewers remember.
**Evidence Anchor**: `table: Supp. Table 9 — DRW vs CE calibration-matched ∆R +0.01957 of ∆T +0.02173, against raw split roughly two-thirds transported`

---

## Weaknesses

### W1: The headline rests on one method, one backbone, one setting
**Problem**: The paper's significance claim is about how the field reads mean-recall gains (l. 380–381, l. 470–473). The only real SGG debiasing evidence, however, is a single pair: MOTIFS vs MOTIFS-TDE, PredCls, one checkpoint. No VCTree or VTransE/Transformer backbone appears, and no other debiasing family: re-weighting, re-sampling, post-hoc logit adjustment, BGNN, GCL, IETrans, NICE and so on. A CVPR reviewer will say a single audit cannot support a field-level recommendation ("benchmarks ... report the split beside the headline metric").
**Evidence Anchor**: `text: §5, p. 5, l. 328–332 "Tang et al. [29] release a causal MOTIFS PredCls checkpoint that yields two models from one set of weights"`
**Why it matters**: This is the main reason I would expect Weak Reject scores. Evaluation papers at CVPR are accepted when they change how the field reads a leaderboard, which needs a leaderboard-shaped result. One audited method reads as an illustrative case study.
**Suggestion**: Make the centre of the paper a table that audits the field, with every row confidence-matched and split, and ∆R carrying its interval. Feasible in six weeks on cloud GPUs:
1. Scene-Graph-Benchmark.pytorch (Tang et al.) supports MOTIFS, VCTree and VTransE/Transformer predictors with plain, TDE, re-weighting and re-sampling variants. Use released checkpoints where they exist; otherwise retrain PredCls. That is roughly one GPU-day per model on a single A100 (please verify), so 10–12 models fit in about two weeks of wall-clock time.
2. Add two zero-training rows: post-hoc logit adjustment, and frequency-bias subtraction applied to the plain MOTIFS checkpoint. If a two-line post-hoc prior correction reproduces TDE's mR gain and its split, that is the paper's most quotable result.
3. Add one or two widely cited later methods with public checkpoints (e.g. BGNN via PySGG, IETrans, GCL) where they run in the same evaluation code.
4. Report each method both against its own baseline and against FREQ. The FREQ comparison answers "how much case-level evidence does each architecture buy over the frequency table", a question the field has argued about since Zellers et al. [33].

The title then becomes a question about the field rather than about one method.
**Severity**: Major
**Confidence**: 5 — core expertise: CVPR SGG evaluation norms and reviewer expectations

### W2: The headline finding is expected, by the paper's own account
**Problem**: The paper concedes that TDE is a group-level intervention by construction and that the split "confirms that it acts as designed". A reviewer will ask what was learned that was not predictable from TDE's definition: subtracting a prediction made with the pair's visual features masked. A careful null on an expected outcome rarely carries a CVPR paper.
**Evidence Anchor**: `text: §5, p. 5, l. 378–380 "subtracting a context-only prediction is a group-level intervention by construction, and the split confirms that it acts as designed"`
**Why it matters**: Significance is the criterion CVPR reviewers weigh most for analysis papers. Right now the surprising content is the CLIP reversal (W6), which uses toy models, and the CIFAR reversal, which is in the supplement.
**Suggestion**: Reframe around findings that are not predictable from a method's definition. The audit in W1 is the main vehicle. The most valuable rows are methods that *claim* better visual or contextual reasoning: message passing, visual-context modules, contrastive or relation-aware feature learning. For those, a group-level-only verdict is a genuine finding, and a case-level gain is a vindication. Even one row where the split contradicts what the method's authors claim lifts significance more than any amount of further analysis on TDE. Keep TDE as the motivating example in §1 and §5, but do not make it the paper.
**Severity**: Major
**Confidence**: 4 — core expertise: SGG debiasing literature

### W3: The title question is never answered in its own units
**Problem**: The title asks what ten points of *mean recall* bought, but the paper explicitly declines to connect the proper-score split to mean recall. This is unnecessary. Theorem 1 is stated "for any integrable score contrast H" (l. 180–181). Per-predicate recall with top-K hits is a linear score in per-relation hit indicators, H_i(y) = w(y)·(1[y ∈ top-K of q1(·|x_i)] − 1[y ∈ top-K of q0(·|x_i)]) with w(y) = 1/(K·n_y). Within-cell transport preserves every predicate's test count n_y, so the denominators of mean recall are unchanged. At least for a micro-averaged, per-relation top-K form of mR, the same transport estimator therefore splits the mR gain exactly into group-level and case-level mR points. The graph-constrained variant also fits, because whether pair i's predicate y is ranked inside the image's top-K does not depend on the label.
**Evidence Anchor**: `text: §5, p. 5, l. 367–368 "Those are different units and we supply no bridge between them"`
**Why it matters**: A reader leaves the abstract expecting an answer like "x of the 10.2 points are group-level". Instead they get −0.00006 in quadratic-score units, which no SGG reader can interpret. That mismatch between promise and delivery is the most visible framing defect, and reviewers will name it.
**Suggestion**: Add a "mean recall, split" column to Table 1 and to the W1 table. Check the derivation for the exact mR variant used: Tang et al.'s mR averages per image before averaging over images, which changes the weights. If the official variant does not decompose exactly, use the micro-averaged one and show it tracks the official number. Report how much of TDE's 10.2 points survives within-cell relabelling. This costs hours, not weeks, because the cached predictions exist. It also lets the abstract open with a number in the units the community uses.
**Severity**: Major
**Confidence**: 4 — core expertise in mR evaluation; the decomposability claim follows from Theorem 1's stated generality but the authors should verify it for the exact mR variant

### W4: The headline depends on the chosen configuration, and the two proper scores disagree
**Problem**: Under the matched configuration, the quadratic score gives case-level ∆R ≈ 0 while the log score gives a significant +0.044. The raw log row and the subject-only row contradict "overwhelmingly group-level", as the paper itself says. The defence ("choosing between them is a declaration and not an error to argue away") is principled but will not convince a CVPR reviewer. They will see a result that changes sign with the scoring rule and stays significant whichever way it points.
**Evidence Anchor**: `table: Table 1 — matched quad ∆R −0.00006 [−0.00120, +0.00109] vs matched log ∆R +0.04396 [+0.04079, +0.04714]; raw log ∆R −0.12619 vs ∆P +0.15897`
**Why it matters**: The abstract's main claim survives only as the hedged conjunction "at most a twelfth ... under either proper score". Reviewers who see Table 1 before the prose will suspect a forking-paths choice of configuration. This is the most likely target of a detailed negative review.
**Suggestion**: (a) Report the calibration-invariant, rank-based within-cell companion that Supp. App. K already recommends (a within-cell paired AUC difference with DeLong variance) for every audited pair, as a tie-breaker that does not depend on temperature or scoring rule. If it agrees with "no case-level gain" for TDE, the fragility objection largely disappears. (b) Fix the primary configuration in §3 before any result, as a declared protocol. (c) In the abstract, say "under both proper scores the case-level part is at most 8% of the change" rather than leading with the quadratic null. (d) For every row of the W1 table, show matched quadratic, matched log and rank-based results, so readers see agreement or disagreement field-wide rather than for one pair.
**Severity**: Major
**Confidence**: 4 — reviewer-perception judgement; the statistical merits of the quadratic-vs-log choice are for the methodology seat

### W5: Positioning against the SGG and score-decomposition literature is thin
**Problem**: The bibliography has 39 entries. The SGG debiasing work it engages is TDE, one evaluation critique, one open-vocabulary paper and one survey-style preprint. It does not cite VCTree, BGNN, GCL, IETrans, NICE, FGPL, the energy-based SGG loss, the graph-density-aware losses of Knyazev et al., or F@K-style metrics. On the decomposition side it does not cite the closest modern ML relatives: the grouping-loss line (Perez-Lebel et al., ICLR 2023, "Beyond calibration: estimating the grouping loss of modern neural networks") and Kull & Flach's decompositions of proper scoring rules.
**Evidence Anchor**: `absence: §2 Related work and the reference list — expected engagement with SGG debiasing methods beyond TDE and with grouping-loss / proper-score refinement literature; checked §1, §2, §5, §7, references [1]–[34], ref.bib (39 entries), supplementary Apps. A–N`
**Why it matters**: CVPR assigns reviewers by bidding, and SGG reviewers will be the authors of these methods. A paper that generalises about "debiasing methods" while citing one of them reads as outside the community, and that invites low novelty and significance scores. The grouping-loss work is close enough that an ML-savvy reviewer may call the split a known idea re-applied. The paper should state the difference (two-model contrast, exact finite-sample identity, leave-one-out transport, clustered inference) before a reviewer frames it for them.
**Suggestion**: Rewrite §2 in about 0.3 pages. Keep one paragraph on SGG debiasing families (re-weighting/re-sampling, causal/TDE, message passing/context, label refinement or transfer) and state which the W1 audit covers. Keep one paragraph on decomposition, contrasting with Murphy/Yates, Bröcker and the grouping-loss/refinement literature in one sentence each. Cut the Diebold–Mariano/Giacomini–White and Hájek detail from §2 (it belongs in the supplement) to make room.
**Severity**: Major
**Confidence**: 4 — core expertise for the SGG literature; adjacent for the score-decomposition literature

### W6: The positive reversal uses toy predictors, not SGG models
**Problem**: The "model every metric ranks last" is a frozen CLIP ViT-B/32 on box crops plus a small MLP, trained on a 100k-relation subsample. It is compared with an MLP on box geometry, on the authors' own 70/30 reconstruction of VG150 rather than the canonical split (Supp. N.1). No published SGG model is involved. A CVPR reviewer will find the reversal plausible but artificial: "of course a 1024-d CLIP head under-fits the class-pair prior".
**Evidence Anchor**: `text: §6, p. 6, l. 397–400 "subject and object regions cropped from the image and encoded by a frozen CLIP ViT-B/32 [24], concatenated with the class embeddings MLP-CLASS uses"`
**Why it matters**: The reversal is the paper's only positive "the metric hides real recognition" result, and the second half of contribution 1. It needs to be about models the audience uses.
**Suggestion**: Pick one, or both if time allows. (a) **Zero-shot VLM rows**: score each relation's 50 predicate prompts with CLIP or SigLIP on the union crop, with no training (a few GPU-hours over the canonical test split), and split against MOTIFS and against FREQ. "VLMs lose on mR yet are better within-pair discriminators" is timely given the open-vocabulary SGG trend [17], and is exactly the sort of finding that gets an analysis paper noticed. (b) A published visually stronger SGG model on the canonical split against its frequency-only counterpart. Either way, move the controlled-predictor material in §4 to a compact validation paragraph and give the freed space to real models.
**Severity**: Major
**Confidence**: 4 — core expertise: what SGG reviewers will accept as evidence

### W7: The §6 headline numbers are unmatched, although §1 says every comparison is matched
**Problem**: §1 states that "every comparison here is confidence-matched". The §6 headline (+0.00641, CI [0.00514, 0.00769]), Fig. 2 and the abstract's CLIP claim, however, use raw outputs. The matched figure (+0.00467, CI [0.00314, 0.00621]) appears only as a robustness check (l. 426–427). `results/vg_prior_consequence.json` confirms the CLIP model was given T = 1.175, so the pair does differ in confidence. Fig. 2 labels only the TDE row "matched".
**Evidence Anchor**: `text: §1, p. 2, l. 115–117 "rescaling a model's confidence moves score between the two parts while changing no ranking — which is why every comparison here is confidence-matched"`
**Why it matters**: The conclusion survives, but a reviewer who notices the protocol being applied selectively will discount both headlines. That is avoidable damage.
**Suggestion**: Use the matched numbers as primary everywhere (abstract, §1, §6, Fig. 2). Alternatively, state a rule for when matching applies ("wherever compared models differ visibly in confidence", l. 258) with a threshold, and apply it identically to every pair.
**Severity**: Minor
**Confidence**: 5 — verified against results/vg_prior_consequence.json

### W8: The main paper does not say that the §4 and §6 predictors use a reconstructed, non-canonical VG150 split
**Problem**: §4 says the predictors are trained "on the VG150 PredCls split". Supp. N.1 says they use a VG150-style reconstruction built from raw annotations with a 70/30 image split, giving 229,605 test relations. The canonical split in §5 has 183,639. Readers will see two different test-set sizes for "VG150" with no explanation in the 8 pages.
**Evidence Anchor**: `text: §4, p. 5, l. 305–306 "We train predicate classifiers on the VG150 PredCls split whose inputs we control"`
**Why it matters**: SGG reviewers know the canonical numbers by heart and will flag the inconsistency. Some will suspect a split chosen to make the result work.
**Suggestion**: Add one sentence to §4 saying it is a reconstruction and why. Better, if W6(b) is adopted, rerun the controlled predictors on the canonical split, which costs CPU-hours for FREQ and the MLPs.
**Severity**: Minor
**Confidence**: 5 — verified in the supplementary and LaTeX source

### W9: "The better recogniser" overstates what the split can establish
**Problem**: The paper's own limitation says any within-cell signal is credited, including unrecorded shortcuts. For the geometry pair, a covariate correlated at only 0.061 would explain the whole case-level gain. Yet §1 and §7 call the CLIP model "the better recogniser" and "the best recogniser of the three".
**Evidence Anchor**: `text: §7, p. 7, l. 451–453 "an unrecorded covariate correlated at 0.061 with both parts would account for the entire case-level gain"`
**Why it matters**: A reviewer will quote the limitation back against the claim. The headline language should not be more confident than the paper's own sensitivity analysis allows.
**Suggestion**: Say "discriminates better among relations sharing an object pair" in the abstract, §1 and §7. Report the robustness value ρ† for the CLIP-vs-geometry pair as well; it is cheap.
**Severity**: Minor
**Confidence**: 4 — follows directly from the paper's stated limitation

### W10: The register is a statistics paper's, and 1.4 pages of the budget are unused
**Problem**: The main text ends about halfway down the left column of p. 7, so roughly 1.4 of the 8 permitted pages are unused. Meanwhile, §2–3 spend space on Diebold–Mariano/Giacomini–White, Hájek projections, U-statistic orders and the Cinelli–Hazlett robustness value. The evidence of generality (CIFAR-100-LT multi-seed, text) gets a single paragraph (l. 428–439) and no table or figure.
**Evidence Anchor**: `figure: rendered p. 7 of paper.pdf — the body ends with the Conclusion in the left column; references begin mid-column`
**Why it matters**: CVPR reviewers judge the 8 pages. The unused space is where the W1 audit table, the W3 mR column and a compact generality figure should go. The heavy statistical vocabulary also signals "wrong venue" to vision reviewers.
**Suggestion**: Fill the budget in this priority order: the W1 field audit table (about 0.5 page), the mR-split column and a short "how to report" box (about 0.2 page), the VLM rows (W6), and a one-row-per-setting CIFAR-LT summary (about 0.2 page). Move the inference detail (Hájek, DM corollary, the randomization test) to the supplement and keep one sentence on image-clustered intervals.
**Severity**: Minor
**Confidence**: 5 — direct inspection of the rendered PDF

### W11: The supplement contains traces of earlier drafts that weaken the double-blind first-submission impression
**Problem**: The supplement repeatedly refers to earlier versions: "earlier drafts of this paper asserted" (App. J), "an earlier version of this theorem" (App. J), "Earlier versions of this corollary" (App. K), "earlier versions of this table omitted it" (N.4).
**Evidence Anchor**: `text: Supp. App. J, p. 11, l. 990–991 "The proportion is smaller than earlier drafts of this paper asserted"`
**Why it matters**: The phrases do not break anonymity, but they read as responses to an earlier set of reviews. Reviewers may infer a resubmission and look for what was criticised before. They also cost space and polish.
**Suggestion**: State each result in its final form and remove all revision-history language.
**Severity**: Minor
**Confidence**: 5 — direct reading

### W12: The title claims scene graph generation, but only predicate classification is covered
**Problem**: Every experiment is PredCls, with ground-truth boxes and object labels. SGCls and SGDet, where most methods report their headline results, are absent. The grouping variable becomes model-dependent once object labels are predicted, and the paper does not say so.
**Evidence Anchor**: `absence: §1, §5, §7 — expected a statement of scope limited to PredCls, or an SGCls/SGDet treatment; checked abstract, §1 contributions, §5, §7 limitations, Supp. N.1`
**Why it matters**: This is a predictable reviewer question. Without an answer it reads as an unacknowledged limitation.
**Suggestion**: State the PredCls scope in the abstract and §7. Add two sentences on why the cell must be fixed across the two models (ground-truth pair) and how SGCls could be handled: audit on relations where both models' predicted pair matches ground truth, and report the coverage. Do not try to cover SGDet in six weeks.
**Severity**: Minor
**Confidence**: 4 — core expertise: SGG protocols

---

## Detailed Comments

### Journal Fit (CVPR 2027 main conference)
- **Scope**: In scope. CVPR accepts evaluation and benchmark-analysis papers in scene understanding, and the SGG mR debate is a CVPR-native topic (TDE, BGNN and GCL were all CVPR papers). The paper is not out of scope; it is *pitched* at the wrong layer. It reads as a statistics paper with one vision application, whereas CVPR wants a vision-evaluation paper whose tool happens to be statistical.
- **What CVPR acceptance looks like for this genre**: successful evaluation papers in this area typically (i) audit many methods, (ii) reveal at least one ranking reversal on widely used models, (iii) give a drop-in reporting protocol or toolkit, and (iv) state the answer in the units the community uses. The manuscript has (iii) in embryo (l. 470–474), (ii) only with toy models, and neither (i) nor (iv).
- **Length and format**: within limits, with about 1.4 pages unused (W10). Double-blind hygiene is fine apart from W11.
- **Alternative venues if the deadline slips**: the work as it stands, centred on the statistical tool, would sit comfortably at TMLR or as a NeurIPS Datasets & Benchmarks or evaluation-track submission. The CVPR version needs the field audit.

### Originality
- The identity is the Yates covariance decomposition of a proper-score difference, applied within strata, as the paper acknowledges (l. 144–145, l. 199). The new elements are the two-model contrast, the leave-one-out transport estimator that removes the (n_c−1)/n_c attenuation, image-clustered inference, the confidence-matching protocol, and its use as an *evaluation* instrument for SGG. For CVPR the originality lies in the last of these, the application and what it reveals, not in the theorem. The paper should present it that way and move statistical novelty claims to the supplement.
- Risk: an ML-literate reviewer may relate it to grouping loss or refinement decompositions (W5). Get ahead of this in §2.

### Significance
- If the field audit (W1) showed that most mR gains across debiasing methods are group-level, and that a post-hoc prior correction matches them, the paper would change how SGG results are read. That is high significance for the sub-field, with spill-over to long-tail recognition, where the supplement already has material.
- As written, significance is limited to one expected finding (W2) plus a toy reversal (W6).

### Structural Coherence
- Title, abstract, introduction and conclusion are consistent with each other, but they ask a question in mR units and answer in proper-score units (W3).
- The abstract's main claim is hedged across two scores. The reader has to reach Table 1 to see why (W4).
- §4 and §6 use a different VG split from §5 without saying so in the main text (W8), and §6 departs from the stated matching protocol (W7).

### Title & Abstract
- The title is excellent and should stay, perhaps generalised: "What did a decade of mean-recall gains buy?" if the W1 audit is done.
- The abstract is dense, about 230 words, and contains −0.00006-style results that do not register with vision readers. After W3, lead with "x of TDE's 10.2 mR points survive within-pair relabelling; across N methods, ...". Drop "O(NK)" and "Bregman" from the abstract.

### Introduction
- The motivation is strong and well written. The "What is not claimed" paragraph is good practice; keep it short.
- Contribution 1 bundles a null and a reversal. After the revisions, the contributions should be (1) the tool and protocol, (2) the field audit, (3) the reversal on real or VLM models, (4) the generality evidence.

### Results / Findings
- Table 1 is honest but hard to read: five rows of five-decimal signed quantities. Add the mR-split column and the rank-based companion, and use fewer decimals (three are enough at these CI widths).
- Fig. 2 is effective. Make sure every bar uses the matched protocol (W7).

### Discussion / Limitations
- The limitations are candid and appropriate. The grouping-choice limitation (Supp. App. K: equally fine partitions can disagree completely) is serious and stated honestly. The recommendation that "the benchmark, not the submitting author" declare ϕ is the right answer and worth a sentence in the conclusion's reporting recommendation.

### Conclusion
- It aligns with the evidence presented but generalises ("the field's metrics report the sum") from one audited method. That generalisation becomes warranted after W1.

### References
- See W5. There are also mechanical issues; see Minor Issues.

---

## What would move this from Reject to Accept (ranked, six-week single-author plan)

Ranked by expected change in reviewer scores per unit of effort.

| Rank | Change | Addresses | Effort (single author, cloud GPUs) | Expected effect on reviewers |
|---|---|---|---|---|
| 1 | **Field audit table**: MOTIFS / VCTree / VTransE (or Transformer) × {plain, TDE, re-weight, re-sample, post-hoc LA, frequency subtraction}, plus 1–3 later methods with public checkpoints. Each row split against its own baseline and against FREQ, confidence-matched, with intervals. | W1, W2, W5 | 2.5–3 weeks (mostly unattended retraining; the split itself takes minutes) | Turns a case study into a field result. The largest single score change, likely from Weak Reject to Borderline or Weak Accept on its own. |
| 2 | **Split mean recall itself** via Theorem 1 (linear hit-indicator contrast; within-cell transport preserves predicate counts). Report "group-level mR points" and "case-level mR points" for every row. | W3 | 2–4 days including derivation check and unit test | Answers the title in its own units, makes the abstract legible, removes the most quotable criticism. |
| 3 | **Calibration-invariant companion** (within-cell paired AUC difference, DeLong variance) for every row; declare the primary configuration in §3 before results. | W4 | 3–5 days | Defuses the configuration-dependence and score-choice attack. |
| 4 | **Zero-shot VLM rows** (CLIP/SigLIP prompt scoring on union crops, canonical split) to replace or accompany the toy CLIP-MLP reversal; report matched numbers. | W6, W7, W8 | 4–6 days | Gives a timely positive "the metric hides recognition" finding on models the audience uses. |
| 5 | **Rewrite for CVPR register**: compress §2–3 statistics into the supplement, rewrite §2 against the SGG and grouping-loss literature, use the unused 1.4 pages, add a "how to report" box and a CIFAR-LT summary row. | W5, W10, W12 | 1 week, in parallel with retraining | Removes the wrong-venue signal and improves the clarity scores. |
| 6 | **Hygiene**: matched numbers everywhere, VG150-reconstruction disclosure, soften "better recogniser", strip revision-history language, fix cross-references and bibliography. | W7, W8, W9, W11 | 1–2 days | Prevents avoidable credibility losses. |

Suggested timeline: week 1, ranks 2 and 3 on the existing TDE pair, and launch retraining for rank 1. Weeks 2–4, rank 1 runs plus rank 4. Week 5, rank 5 rewrite. Week 6, rank 6, number checks and a final read.

If only one thing can be done, do rank 1 together with rank 2 applied to it. Without rank 1 I expect Weak Reject or Borderline-Reject scores however polished the rest becomes.

---

## Questions for Authors

1. Does Theorem 1 give an exact split of the *official* mean-recall@K computed by the Scene-Graph-Benchmark code (per-image averaging, graph constraint)? If not, which mR variant does it split exactly, and how closely does that variant track the official number on TDE?
2. How much of TDE's 10.2-point mR gain is reproduced by a post-hoc logit adjustment or frequency-bias subtraction on the plain MOTIFS checkpoint, and what is that correction's split?
3. For TDE, what does a rank-based, calibration-invariant within-cell contrast (e.g. a within-cell paired AUC difference) show? Does it agree with the matched quadratic or the matched log row?
4. Why were the §4/§6 predictors trained on a reconstructed split rather than the canonical VG150 split used in §5, and do the conclusions hold on the canonical split?

---

## Minor Issues

### Language / Grammar
- Abstract, l. 001–025: very dense. Remove "O(NK) time", "Bregman" and "image-clustered confidence intervals" from the abstract; they are not decision-relevant for a CVPR reader.
- §1, l. 99: "and a reversal in which the model ranked last is the best case-level discriminator" is grammatically attached to the TDE bullet. Make it a separate contribution.

### Citation Format
- The main-paper reference list includes entries not cited in the main text ([5], [11], [16], [19], [25], [26], [30]). Their back-reference page numbers (e.g. "[19] ... 4", "[25] ... 5, 12") point to *supplement* pages but read as main-paper pages. Compile the main bibliography from main-text citations only, or turn off back-references.
- [15] and [21] are cited as "a long line of debiasing work" but neither is an SGG debiasing method ([21] is long-tailed recognition, NeurIPS 2025). Cite actual SGG debiasing papers there (W5).

### Figures and Tables
- Table 1: three decimals suffice. Add a column for the identified relations per row; the matched rows use the held-out half (92,027 relations, 3,708 cells, 98.1% coverage per `results/sgg_audit_motifs.json`), whereas §5 prose reports the full-set figures (183,639 relations, 5,044 identified cells, 98.9%).
- Fig. 2(b): the "exactly 0 (forced by Thm. 1)" annotation is useful; label each row with its regime (raw or matched).

### Layout / Consistency
- Naming differs between main paper and supplement: the method is named "WAGER" only in the supplement, and the supplement uses "transported gain" and "within-group covariance gain" rather than ∆P and ∆R. Pick one vocabulary, and name the method in the main paper if it will be named at all.
- Supp. App. L "Terminology" is an empty heading (Table 4 floats above it).
- Supp. N.3, l. 1136–1137: "Two falsification checks, reported in Section H" — the checks are not in Section H.
- Supp. N.6, l. 1251: "the breadth Section 7 claims" — §7 makes no such claim.
- Supp. N.5, l. 1162: "Section 2 argued that long-tailed image classification poses a structurally identical question" — §2 gives this one clause.

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | quality_rubrics.md; CVPR reviewer form ("novelty") | PARTLY_MEETS | text: §2, l. 144–145; Supp. App. B | The identity descends from Yates; the novelty is the two-model, transport-based, inference-equipped evaluation instrument and its SGG application. Grouping-loss literature is not engaged. | Novelty perception depends on reviewer pool | yes — reviewers may score novelty low without W5 |
| Methodological Rigor | quality_rubrics.md | NOT_ASSESSED | — | Methodology seat's remit | — | no (outside my remit) |
| Evidence Sufficiency | quality_rubrics.md; CVPR expectations for evaluation papers | DOES_NOT_MEET | text: §5, l. 328–332; Table 1 | One audited method and backbone for a field-level claim; headline varies by configuration | Repairable in six weeks (W1, W4) | yes — main driver of Weak Reject |
| Argument Coherence | quality_rubrics.md | PARTLY_MEETS | text: §5, l. 367–368; text: §1, l. 115–117 | Question in mR units, answer in score units; matching protocol applied selectively | Repairable cheaply (W3, W7) | yes |
| Writing Quality | quality_rubrics.md; CVPR readership | PARTLY_MEETS | figure: Fig. 1; rendered p. 7 | Excellent framing and teaser; statistics-journal register and unused page budget | none identified | no — affects clarity scores, not acceptance on its own |
| Literature Integration | quality_rubrics.md | DOES_NOT_MEET | absence: §2 / references (W5) | Generalises about SGG debiasing while citing one such method | none identified | yes — affects reviewer assignment and novelty scores |
| Significance & Impact | quality_rubrics.md; CVPR reviewer form ("significance") | PARTLY_MEETS | text: §5, l. 378–380; Supp. Table 9 | Potentially high (would change leaderboard reading) but the demonstrated finding is expected by design; the strongest reversals are toy or in the supplement | Strongly dependent on what the W1 audit finds | yes |

**Recommendation rationale.** The unresolved criteria that bear on the decision are Evidence Sufficiency (single-method audit, configuration-dependent headline), Literature Integration, and Argument Coherence (no answer in mR units). All are repairable within the six-week window by adding experiments and reframing; none needs the method to change. Significance is contingent: its ceiling is high, but the current demonstration does not reach it. Strengths in framing, candour and validation do not offset the evidence-sufficiency gap for a CVPR main-conference paper. Hence Weak Reject on the CVPR scale, mapped to Major Revision.
