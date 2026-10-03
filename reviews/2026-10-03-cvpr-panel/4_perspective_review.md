# Peer Review Report

## Manuscript Information
- **Title**: What Did Ten Points of Mean Recall Buy? Separating Group-Level from Case-Level Gains in Scene Graph Generation
- **Manuscript ID**: CVPR 2027 submission (anonymous, Paper ID withheld)
- **Review Date**: 2026-10-03
- **Review Round**: Round 1 (pre-submission simulated panel, mode `full`)

---

## Reviewer Information

### Reviewer Role
Peer Reviewer 3 (Perspective), internal role `R3`

### Reviewer Identity
An ML evaluation-science researcher from outside scene graph generation, working on long-tailed recognition, VQA bias and dataset shortcuts, and methods for comparing models. I read the paper as someone who would decide whether to use this tool on my own benchmarks. I am not an SGG specialist. Where SGG conventions differ from what I assume, I say so.

### Review Focus
I ask three things. Does the split work on benchmarks other than Visual Genome PredCls? Would people who run leaderboards actually use it? Does the paper rest on assumptions that SGG readers would not think to question? For each weakness I give a remedy that one author with cloud GPUs can finish in the six weeks before the 16 November 2026 deadline. The remedies are ranked by impact in the section "Ranked six-week plan".

### Calibration Status
`NOT_CALIBRATED`

Confidence is an uncertainty/scope disclosure only; it never changes consensus counts, severity, decision bearing, or arbitration.

---

## Overall Assessment

### Recommendation
- [ ] **Accept**
- [ ] **Minor Revision**
- [x] **Major Revision**
- [ ] **Reject**

**CVPR scale: Borderline.** It could rise to Weak Accept if the mean-recall bridge (W4) and one released-checkpoint audit outside SGG with an input-observed grouping (W1/W2) are added. In the skill's terms this maps to **Major Revision**.

### Confidence Score
4. Evaluation methodology, long-tailed recognition and VQA bias are my core areas. I have less hands-on experience with SGG codebases and leaderboard conventions.

### Summary Assessment
The paper splits the proper-score difference between two frozen models into two parts. The first survives relabelling each case with another case's label from the same declared group (the group-level part, ∆P). The second does not (the case-level part, ∆R, a within-group covariance). The split is exact, needs no fitting, runs in O(NK) time and has image-clustered intervals. On TDE's released checkpoints, once calibration is matched, the case-level part is indistinguishable from zero under the quadratic score. A frozen-CLIP crop model that ranks last on accuracy and Brier score is nonetheless the best case-level discriminator.

From an evaluation-science view the core idea is good and the tool is cheap. The question "did the gain come from the prior or from the case?" exists well beyond SGG: in VQA-CP, in long-tailed classification, and in blind-baseline audits of multimodal LLMs. A clean, exact version of that question could be cited widely.

The paper does not yet earn that reach.
- The evidence for generality outside SGG uses groupings derived from the label, which the paper's own setup does not allow.
- The headline asks what mean recall bought, but the analysis decomposes an instance-weighted score and declines to connect the two.
- The practical reason given for wanting the split, that the case-level part is robust to label shift, does not hold in general.
- The "case-level = recognition" reading is not tested against scene-context shortcuts.

All of these can be fixed within six weeks. I recommend Borderline / Major Revision.

---

## Strengths

### S1: An exact, cheap, model-free attribution between two models, a rare object in evaluation science
Most bias diagnostics in VQA and long-tailed recognition describe one model, for example by slicing accuracy by answer rarity. Few attribute the *difference* between two models to a mechanism. The paper names this gap clearly (p. 2, l. 51–55) and fills it with an identity that holds in every sample, needs no reference model or tuning parameter, and runs on cached predictions. That makes it easy to adopt.
**Evidence Anchor**: `text: p. 2, l. 53–55 "None attributes the gain between two models to one route or the other."`

### S2: The ranking reversal is a demonstration that will travel
A model that ranks last on accuracy and Brier score while being the best case-level discriminator is the kind of result that changes how people read a leaderboard. It speaks to a live CVPR question: why do features from foundation models look weak on benchmarks dominated by label priors?
**Evidence Anchor**: `figure: Fig. 2(b), CLIP-crops-vs-geometry row, case-level part positive with interval excluding zero while the total is negative`

### S3: Validation includes a negative control that is zero by algebra
FREQ vs MLP-CLASS gives exactly zero case-level gain because both models depend only on the cell (Theorem 1). This is the right kind of test: it shows the tool does not invent case-level credit. The calibration-only design (−0.488 raw, −0.0003 matched) is equally useful to a practitioner.
**Evidence Anchor**: `text: p. 5, l. 316–319 "That zero is algebraic, not empirical — both models are functions of the class pair alone"`

### S4: Configuration dependence is reported openly
Tab. 1 shows all five configurations, including two that contradict the headline. The paper also states plainly that it supplies no bridge from the proper score to mean recall. That openness makes the paper easy to trust, and easy to improve.
**Evidence Anchor**: `table: Tab. 1, all five rows (raw/matched × quadratic/log × pair/subject)`

### S5: It brings in methods from forecast verification and econometrics
Yates' covariance decomposition, Diebold–Mariano and Giacomini–White tests, Hájek projections and Cinelli–Hazlett-style sensitivity values are all used, and that toolbox is badly under-used in vision evaluation. The paper helps carry it across.
**Evidence Anchor**: `text: p. 3, l. 151–154 "Inference on a paired score difference is the Diebold–Mariano test [8] and its conditional form [10]"`

---

## Weaknesses

### W1: The evidence for generality uses groupings the method's own setup rules out
**Problem**: The setup requires the grouping to be a function of the input that both models observe (p. 3, l. 167–168; supp. Tab. "Terminology": "a discrete function of the input"). The only evidence outside SGG uses groupings that are functions of the *label*: CIFAR-100 superclasses, frequency tiers, and 20-Newsgroups coarse topics (supp. N.5–N.6). Neither model is given these. When the grouping is a coarsening of Y, transport scores a vehicle image against another *vehicle* label. Superclass-level recognition, which is genuinely case-level, is then credited to ∆P. So in those studies "group-level" no longer means "earned from the declared prior". It means "superclass recognition plus within-superclass prior". The main text presents these studies as "the identical estimator" with no caveat.
**Evidence Anchor**: `text: p. 6, l. 430–432 "with superclasses as the grouping, and to long-tailed text classification"`
**Why it matters**: The paper's broadest impact claim is "nothing in Sec. 3 is specific to relations". Here it rests on studies where the two parts mean something different from what they mean in SGG. A long-tail reviewer will spot this immediately. It also marks a real boundary of the method. The split is cleanest where the prior-carrying variable is an *input*: the VQA question, the SGG object pair, the HOI object class, the MLLM question stem. It is murkiest in plain long-tailed classification, where the "prior" is the label marginal itself.
**Suggestion**:
1. In the main text, say that ϕ must be input-measurable and that label-derived groupings change what ∆P means.
2. For long-tailed classification, keep only the global cell (ϕ ≡ const), which is legitimate, or use an input-measurable grouping such as clusters of a frozen-encoder embedding shared by both models.
3. Move the cross-domain showcase to a benchmark where ϕ is naturally an input (see W2).

**Severity**: Major
**Confidence**: 4 (core expertise: long-tailed evaluation; the algebra follows directly from Theorem 1's conditioning)

### W2: No released-checkpoint audit outside SGG, and about 1.5 pages of the page budget are unused
**Problem**: The paper's broader claim ("benchmarks whose labels lean on a feature every model sees", p. 7, l. 470–472) is supported in the main text by one benchmark, VG150 PredCls. Outside SGG, the only evidence is self-trained small models in the supplementary. Meanwhile the main text ends in the first column of p. 7, and references are not counted toward the eight pages. That leaves roughly 1.5 pages free.
**Evidence Anchor**: `absence: main paper Secs. 4–7 and Fig. 2 — expected a decomposition of a published method's released checkpoints on a non-SGG benchmark; checked Secs. 4–7, Fig. 2, supp. N.1–N.6`
**Why it matters**: CVPR readers outside SGG will cite this as an evaluation *tool* only if they see it answer a question in their own field. VQA has exactly the open question the tool is built for. VQA-CP debiasing gains have been argued to come largely from inverting the per-question-type answer prior rather than from better grounding. An exact, model-free answer to that question would be cited by the VQA and multimodal-LLM evaluation communities.
**Suggestion (pick one; both are feasible)**:
- **(a) VQA, higher payoff.** Group by question type, or by exact question string on VQA v2, whose complementary-pair construction guarantees cells with n_c ≥ 2 and differing answers. Compare a baseline (e.g. UpDn) with one or two published debiasing methods that have public code (e.g. RUBi or LMH), plus a "prior-inversion only" control that should land entirely in ∆P. With precomputed region features, each model trains in a few GPU-hours. About 2–3 weeks.
- **(b) ImageNet-LT, cheaper.** Use released decoupling checkpoints (cRT, τ-norm, LWS) with ϕ ≡ const or an input-measurable grouping. τ-norm and LWS change only the classifier, which tests whether classifier-only rebalancing is group-level. About 1 week.

Put the result in the main paper as a half-page section with one table, in the free space.

**Severity**: Major
**Confidence**: 4 (core expertise: VQA bias and long-tail benchmarks)

### W3: One debiasing method stands in for a field-level claim
**Problem**: The title and framing speak to the mean-recall paradigm, but only TDE is audited, on one backbone (MOTIFS). Readers will ask whether the "group-level only" finding describes TDE, which is a group-level intervention by design as the paper itself says (p. 5, l. 378–380), or describes SGG debiasing in general.
**Evidence Anchor**: `text: p. 2, l. 94–95 "An audit of a published debiasing method's released checkpoints"`
**Why it matters**: A one-method result invites the reply "TDE was always going to look like this." A table covering several published methods and backbones, showing which of them buy any case-level gain, would be a field-level finding. That is the result that gets cited.
**Suggestion**: Audit 4–6 further methods whose PredCls checkpoints or training code are public in the shared SGG benchmark codebase. Examples are TDE on VCTree, loss re-weighting, a resampling or data-transfer method, and a bipartite or message-passing debiasing method. Use the same matched protocol and report one row per method with mR@50, ∆T, ∆P and ∆R [CI]. Re-running inference with released weights costs little. Retraining where weights are missing is about 1 GPU-day per model. Budget 2–3 weeks.
**Severity**: Major
**Confidence**: 3 (evaluation-design judgement; I cannot vouch for which SGG checkpoints are currently downloadable)

### W4: The headline question is about mean recall, but the analysis decomposes a head-dominated, instance-weighted score
**Problem**: Mean recall averages over predicates. The decomposed quadratic and log scores are weighted by instance, so ∆R is dominated by head predicates (on, has, wearing). TDE could gain case-level discrimination on tail predicates and lose it on head predicates, netting to −0.00006. That would be a very different story from "no case-level improvement". The paper says it "supply[ies] no bridge" between the units. For CIFAR-100-LT it does give a per-frequency-tier breakdown of ∆R (supp. Tab. "Covariance gain by training-frequency tier"), but not for the flagship TDE audit.
**Evidence Anchor**: `text: p. 5, l. 367–368 "Those are different units and we supply no bridge between them"`
**Why it matters**: To a long-tail researcher, "did the debiased model recognise *rare* relations better?" *is* the question that mean recall stands in for. If it goes unanswered, the title promises more than the analysis delivers.
**Suggestion**: The machinery for a bridge is already in the paper.
1. Theorem 1 holds for "any integrable score contrast H" (p. 3, l. 180–181). So decompose H with label weights w(y) ∝ 1/π(y), a class-balanced quadratic score that is the proper-score analogue of mean recall. Report ∆T, ∆P and ∆R for TDE under that weighting.
2. Because R̂_i = H_i(y_i) − P̂_i is additive over cases, report ∆R by predicate-frequency tier (head/body/tail) as was done for CIFAR.

Both run on cached predictions in about 2–3 days. If tail ∆R is also null, the headline becomes much stronger. If it is positive, the paper gains a more nuanced and more citable finding.
**Severity**: Major
**Confidence**: 4 (core expertise: long-tailed evaluation metrics)

### W5: The stated practical reason for the split, that case-level gains are robust to label shift, does not hold in general
**Problem**: Sec. 3 argues that a group-level gain depends on the evaluation label frequencies while a case-level gain does not, and calls this "the operational reason to want them apart". The example uses two labels and the mirror shift (3/4, 1/4) → (1/4, 3/4), which leaves p₁p₂ unchanged.

In general, write m_{y′}(y) = E[H_X(y) | Y = y′, C = c], i.e. the expected score contrast at label y for cases whose true label is y′. Then ∆R_c = Σ_{y,y′} p(y) p(y′) [m_y(y) − m_{y′}(y)]. This is a p⊗p-weighted average of pairwise discrimination contrasts. The contrasts themselves *are* invariant to label shift (class-conditionals fixed), but their weights are not. I checked this numerically with K = 4 and random m. Moving between random label distributions changed the sign of ∆R in roughly a fifth of draws. With K = 2, ∆R = p₁p₂·const, so the sign is kept but the size changes.
**Evidence Anchor**: `text: p. 4, l. 217–219 "a group-level gain is contingent on the evaluation set's label frequencies matching deployment, and a case-level gain is not"`
**Why it matters**: Practitioners will adopt the split on the strength of this argument. TDE is exactly a label-shift scenario: its premise is that deployment should not reward the head-heavy prior. If the case-level part also moves under shift, a "matched ∆R ≈ 0 under VG test frequencies" result does not settle what TDE buys under balanced deployment.
**Suggestion**:
1. Replace the claim with the pairwise representation above (a short derivation; it follows in two lines from Theorem 1).
2. State precisely what is shift-invariant: the contrasts D(y, y′) = m_y(y) − m_{y′}(y).
3. Report ∆R reweighted to a balanced or deployment label law alongside the observed one.

This turns a weakness into a contribution: a label-shift-invariant core underneath the case-level part. It also connects to W4, because uniform weights give the balanced case-level part, i.e. the bridge to mean recall. About 2–4 days.
**Severity**: Major
**Confidence**: 4 (derivation checked by hand and numerically; outsider to SGG but squarely within evaluation theory)

### W6: "Case-level = better recognition" is not tested against scene-context shortcuts
**Problem**: ∆R credits any signal that varies within a cell (p. 2, l. 111–113; Appendix I gives robustness value 0.061). In SGG the best-known within-pair signal besides the relation itself is *image context*: the other objects present and the scene type, e.g. beach → riding. CLIP crops of the subject and object regions include background, and MOTIFS-style models encode global context. So "it is the better recogniser" could partly mean "it uses scene context better". In VQA, the analogous "grounding" claims did not survive such controls.
**Evidence Anchor**: `text: p. 2, l. 91–92 "its deficit is entirely group-level, and it is the better recogniser"`
**Why it matters**: The tool's value to other fields depends on ∆R reading as recognition rather than as a finer-grained prior. If a model that never looks at the pair's pixels earns a large ∆R, the interpretation has to be weakened. If it does not, the CLIP reversal becomes far more convincing.
**Suggestion**: Add a **context-only control**: an MLP on class-pair embeddings plus a bag-of-object-classes of the *other* annotated objects in the image, with no crop pixels. Report its ∆R against MLP-CLASS beside the geometry and CLIP rows. Optionally also refine ϕ by a coarse scene label and show ∆R(CLIP vs geometry) survives. Both are trained on the same 100k subsample in about 1–2 GPU-days.
**Severity**: Major
**Confidence**: 4 (core expertise: shortcut learning and dataset bias)

### W7: The headline depends on configuration, which makes adoption fragile without a configuration-free companion
**Problem**: Across the five reported configurations the case-level part ranges from −0.217 to +0.044. The headline holds in one of them. The quadratic and log scores disagree on the sign after matching. The matched TDE rows rest on one random half of the images (92,027 relations, per `results/sgg_audit_motifs.json`), whereas CIFAR used twenty splits.
**Evidence Anchor**: `table: Tab. 1, ∆R̂ column, −0.21711 / −0.12619 / −0.01355 / −0.00006 / +0.04396 across the five rows`
**Why it matters**: A benchmark maintainer adopting a diagnostic needs one default whose answer does not turn on a temperature fit and a choice of score. Otherwise each submitter will pick the row that suits them, which is the Goodhart problem the paper is trying to expose.
**Suggestion**:
1. Report the rank-based within-cell companion the authors already propose in Appendix K, a within-cell paired AUC difference with DeLong variance, for every headline comparison. It is invariant to calibration. If it agrees with the matched quadratic row for TDE (null) and for CLIP (positive), most of the configuration objection goes away.
2. Repeat the matched TDE audit over 10–20 random halves and report mean and sd.
3. Publish a one-paragraph "report card" with fixed defaults.

About 3–5 days.
**Severity**: Major
**Confidence**: 4 (core expertise: model-comparison methodology)

### W8: "Every aggregate measure ranks it last" is not checked against mean recall, the field's headline metric
**Problem**: The introduction says every aggregate measure ranks the CLIP model last. The committed results give accuracy, Brier score, MRR and R@5 (`results/vg_visual_results.json`, `results/vg_metric_bridge.json`), but no mR@K for the CLIP model. A model that fits the class-pair prior less well may well have *higher* mean recall.
**Evidence Anchor**: `text: p. 2, l. 88–89 "which every aggregate measure ranks last"`
**Why it matters**: If mR ranks CLIP higher, the reversal changes from "aggregate metrics are blind" to "the field's own debiasing metric agrees with the split while accuracy and Brier do not". That is still interesting, but it is a different and more nuanced claim. As written, a reviewer could falsify the sentence in an afternoon.
**Suggestion**: Compute mR@20/50/100 and zR@K for the three subsample models from cached predictions (hours), and adjust the wording either way.
**Severity**: Minor
**Confidence**: 4 (checked the results files; claim scope is clear)

### W9: The scope is limited to aligned, fully probabilistic predictions
**Problem**: The method needs full probability vectors and the same test cases for both models. In SGG this means PredCls only. SGCls and SGDet, where detected boxes and object labels differ between models, are not discussed. Many leaderboards and API-served multimodal LLMs expose only top-k outputs or text.
**Evidence Anchor**: `text: p. 7, l. 457–459 "it needs probabilities: most benchmarks archive ranked predictions, and that, not compute, is the obstacle to routine use"`
**Why it matters**: Adoption beyond research audits depends on these cases.
**Suggestion**:
1. Add a sensitivity study in which only the top-5 probabilities are kept and the remaining mass is spread uniformly. Report how far ∆R moves for TDE and CLIP (hours).
2. Say in one sentence how SGCls/SGDet could be handled, e.g. by restricting to ground-truth pairs that both models detected.
3. Note that multiple-choice MLLM benchmarks do expose option log-probabilities, which makes them a natural next target.

**Severity**: Minor
**Confidence**: 3 (adjacent: leaderboard practice)

### W10: Choosing the grouping is a governance problem; the needed diagnostic is only in the supplementary
**Problem**: Appendix K shows that two equally fine partitions can disagree completely, and recommends reporting within-cell label heterogeneity. The main text recommends that benchmarks declare ϕ (p. 6, l. 447–448) but does not carry this diagnostic into its reporting recipe (p. 7, l. 472–474).
**Evidence Anchor**: `text: p. 6, l. 445–447 "two equally fine partitions of the same cases can disagree completely about whether a gain is case-level"`
**Why it matters**: Without a heterogeneity diagnostic, a submitter can choose a nearly label-homogeneous ϕ and report a "null" case-level effect.
**Suggestion**: Add mean within-cell label entropy, or effective number of labels, to the recommended report alongside coverage. It is one number and one sentence.
**Severity**: Minor
**Confidence**: 4 (evaluation-protocol design)

### W11: The method has no name in the main paper, and the terms differ between paper and supplementary
**Problem**: The main paper never names the tool and uses "group-level/case-level". The supplementary uses "WAGER" and "transported gain/within-group covariance gain".
**Evidence Anchor**: `text: supp. p. 1, l. 598–599 "this supplementary keeps the long-form names for the two parts of a gain"`
**Why it matters**: People adopt and cite tools by name. Two vocabularies make the paper harder to cite and the code harder to find.
**Suggestion**: Name the method in the main paper and use one set of terms in both documents.
**Severity**: Minor
**Confidence**: 5 (direct observation)

---

## Detailed Comments

### Assumption Audit
- **Explicit assumptions**:
  - The grouping is declared in advance and observed by both models (p. 3, l. 167–168). This holds for SGG PredCls but is broken in the supplementary's cross-domain studies (W1).
  - The comparison must be calibration-matched (p. 4, l. 250–262). The authors defend this, but it makes the result depend on the protocol (W7).
- **Implicit assumptions**:
  1. *Case-level covariance equals recognition.* ∆R is better described as "discrimination finer than ϕ". Whether that is recognition or a finer prior depends on what ϕ leaves out (W6).
  2. *The instance-weighted test distribution is the right yardstick for a debiasing method.* TDE's own premise disputes this, and the paper's label-shift example concedes it, but the decomposition is never re-weighted (W4, W5).
  3. *The case-level part is shift-invariant.* It is not; only its pairwise contrasts are (W5).
  4. *Two frozen models' predictions are aligned case by case.* True only in PredCls-like settings (W9).
- **Paradigmatic assumptions**: SGG treats benchmark frequencies as "bias" to be removed. Forecast verification, where the tool comes from, treats base rates as information the forecaster should use. The paper sits between the two well; its sentence "This characterises TDE rather than indicting it" (p. 5, l. 378) is the right stance. It could go one step further. The quantity a debiasing method needs to buy, if it is to be worth more than a post-hoc logit adjustment, is case-level gain. The paper could state that criterion explicitly as a bar for future debiasing papers.

### Cross-Disciplinary Connections
- **Parallel research**:
  - *VQA prior inversion*: VQA-CP gains have been traced to inverting answer priors per question type; grounding methods have been shown to help through regularisation rather than grounding.
  - *NLP hypothesis-only and partial-input baselines*: these ask the same "prior or evidence?" question about single models.
  - *MLLM blind baselines*: image-free accuracy as a contamination or prior check.

  The split is the two-model, exact version of all three, and saying so would widen the audience.
- **Borrowing opportunities**:
  - From econometrics: the within/between (fixed-effects) decomposition. ∆R is a within-cell estimator, and the paper could use that vocabulary for statisticians.
  - From the label-shift literature (Saerens et al. and Lipton et al., both already cited in the supplementary): the representation in W5 links ∆R directly to label-shift-invariant contrasts.
- **Methodological borrowing**:
  - DeLong-style rank contrasts as a calibration-free companion (W7).
  - Fixed reporting templates as in clinical prediction reporting (TRIPOD-style).

### Practical Impact
- **Real-world application**: A leaderboard maintainer for VG, GQA, VQA-CP, HICO-DET (whose rare/non-rare split is HOI's mean-recall analogue), or an MLLM multiple-choice suite could compute the split from stored probabilities in minutes. The main barriers are not compute but four things: (i) choosing ϕ, (ii) the need for probabilities, (iii) the calibration protocol, (iv) no reference implementation named in the paper. Each has a cheap mitigation (W7, W9–W11).
- **Implementation feasibility**: The O(NK) estimator and released code make adoption easy *once a default protocol exists*. Without one, the five-row table invites people to choose the configuration that suits them.
- **Stakeholders**: Authors of debiasing methods may read the paper as an attack. The careful phrasing on p. 5, l. 378–381 helps. A multi-method table (W3) in which some methods *do* earn case-level gain would make the tool read as a fair referee rather than a critic of TDE.

### Broader Implications
- **Ethical dimensions**: Little direct risk. The one indirect risk is Goodhart pressure on ∆R itself, e.g. tuning confidence to move score between the parts. The rank-based companion (W7) mitigates it.
- **Social impact**: Better separation of prior-following from evidence-using predictions matters wherever deployment label frequencies differ from benchmark frequencies. Visual assistance and robotics relation reasoning are examples; the paper could mention this in one sentence.
- **Future directions**: The most valuable extension is to multiple-choice MLLM evaluation. There ϕ is the question stem and options, both observed inputs, and the open question is how much of a model's gain over its predecessor is answerable without the image. The split answers this exactly when option log-probabilities are available.

### Title, abstract and framing: a larger contribution without overclaiming
- **What the evidence can support today**: "Debiasing gains on prior-heavy benchmarks can be pure group-level redistribution, and aggregate metrics can rank models by the wrong criterion. Here is an exact, cheap way to tell." That is already more general than the title.
- **What it could support after six weeks**, given W1/W2 and W3: "Across N published SGG debiasing methods and a second benchmark (VQA-CP or ImageNet-LT), most headline gains are group-level; we identify which methods buy case-level discrimination." That claim would be cited across communities.
- **Suggested reframing**: Call ∆P a *label-shift bet*. It pays off only if deployment frequencies differ from the test set's in the direction the model moved. That gives practitioners a reason to care about the split that does not depend on the overstated invariance claim (W5).
- **Title**: Keep the strong hook, "What Did Ten Points of Mean Recall Buy?" Drop "in Scene Graph Generation" from the subtitle *only if* a second-domain result reaches the main paper; otherwise keep it, so that generality is not overclaimed.
- **Do not claim**: that debiasing "does not work", or that ∆R measures recognition outright. The paper currently avoids both, and should keep doing so.

### Ranked six-week plan (by impact on acceptance and citations)
| Rank | Remedy | Addresses | Effort (single author, cloud GPU) | Why this rank |
|---|---|---|---|---|
| 1 | Class-balanced (1/π(y)) decomposition and per-predicate-tier ∆R for TDE; mR@K for the CLIP subsample models | W4, W8 | 2–3 days, cached predictions only | Answers the title's own question; cheapest high-value change |
| 2 | Rank-based within-cell AUC companion (DeLong) on every headline row; 10–20 random calibration halves for TDE | W7 | 3–5 days | Removes the main objection to adoption (configuration dependence) |
| 3 | Released-checkpoint audit of 4–6 more SGG debiasing methods (or backbones) under the fixed protocol | W3 | 2–3 weeks | Turns an anecdote into a field-level finding |
| 4 | Second benchmark with an input-measurable ϕ in the main paper: VQA-CP/VQA v2 (preferred) or ImageNet-LT decoupling checkpoints | W1, W2 | 1 week (ImageNet-LT) to 3 weeks (VQA) | Shows the tool's reach in a form readers outside SGG will recognise |
| 5 | Context-only control predictor (class pair + other-object bag, no pixels) | W6 | 1–2 GPU-days | Tests the "better recogniser" reading |
| 6 | Restate the label-shift claim with the pairwise-contrast representation and report a shift-reweighted ∆R | W5 | 2–4 days (mostly writing) | Fixes the practical rationale and supplies part of the mean-recall bridge |
| 7 | Restrict or caveat the CIFAR/text groupings; name the method; unify terms; add a heterogeneity diagnostic and top-k truncation sensitivity | W1, W9–W11 | 3–4 days | Low cost, prevents easy reviewer objections |

The minimum viable package (ranks 1, 2, 5, 6, 7) takes about 2.5 weeks. Add *either* rank 3 *or* rank 4 depending on whether the target audience is SGG (rank 3) or evaluation in general (rank 4). Doing both in six weeks is ambitious but possible if ImageNet-LT is chosen for rank 4.

---

## Cross-Disciplinary Reading Recommendations
These are search leads from memory, not checked in this session. Verify the metadata before citing.
- [UNVERIFIED] Goyal et al., "Making the V in VQA Matter", CVPR 2017. VQA v2's complementary image pairs give natural cells with n_c ≥ 2 and differing answers when ϕ is the question.
- [UNVERIFIED] Teney et al., "On the Value of Out-of-Distribution Testing: An Example of Goodhart's Law", NeurIPS 2020. Argues that VQA-CP gains can come from prior inversion, i.e. the group-level route.
- [UNVERIFIED] Shrestha, Kafle and Kanan, "A Negative Case Analysis of Visual Grounding Methods for VQA", ACL 2020. Shows that apparent grounding gains came from regularisation, a direct parallel to the TDE audit.
- [UNVERIFIED] Cadene et al., "RUBi: Reducing Unimodal Biases for VQA", NeurIPS 2019; Clark, Yatskar and Zettlemoyer, ensemble-based debiasing (LMH), EMNLP 2019. Candidate VQA debiasing methods with public code.
- [UNVERIFIED] Kang et al., "Decoupling Representation and Classifier for Long-Tailed Recognition", ICLR 2020. cRT, τ-norm and LWS checkpoints for an ImageNet-LT audit.
- [UNVERIFIED] Feng, Wallace and Boyd-Graber, "Misleading Failures of Partial-Input Baselines", ACL 2019; Gururangan et al. / Poliak et al. on hypothesis-only NLI baselines (2018). The single-model "prior or evidence" literature in NLP.
- [UNVERIFIED] Chen et al., "Are We on the Right Way for Evaluating Large Vision-Language Models?" (MMStar), 2024. Blind-baseline auditing of multimodal LLMs, a natural next target.
- [UNVERIFIED] Mundlak (1978) on within/between estimators in panel data. Gives ∆R a vocabulary statisticians already know.

---

## Questions for Authors
1. Under class-balanced label weights (1/π(y)), and broken down by predicate-frequency tier, is TDE's case-level part still null, or does it gain on the tail and lose on the head?
2. Does a context-only predictor (class pair plus the other annotated objects in the image, no crop pixels) earn a case-level gain comparable to the CLIP crop model?
3. Given ∆R_c = Σ p(y)p(y′)[m_y(y) − m_{y′}(y)], which statement about label-shift robustness do you intend to make, and does TDE's matched ∆R stay near zero when reweighted to a balanced predicate distribution?
4. For CIFAR-100-LT and 20-Newsgroups-LT, how should ∆P be read when ϕ is a function of the label rather than of the input? Would you keep these studies with ϕ ≡ const only?

---

## Minor Issues

### Figures and Tables
- Tab. 1 caption: give N for the matched rows (the audit half, about 92k relations) next to the full-audit 183,639 quoted on p. 5, l. 340.
- Fig. 2: add mR@50 for each compared model, e.g. as a small annotation, so readers can see the headline metric and the split side by side.

### Layout
- About 1.5 pages of the eight-page budget are unused (main text ends p. 7, col. 1). The best use is a short second-domain section or the multi-method table (W2/W3).

### Language
- p. 2, l. 88: "every aggregate measure" → "accuracy and the proper score" unless mR is checked (W8).

---

## Criterion-Bound Judgements

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | quality_rubrics: Originality; R3 config (evaluation science) | MEETS | text: p. 2, l. 53–55; Fig. 1 | An exact two-model attribution with no fitted reference is new for vision benchmarks; its roots in Yates are acknowledged | I cannot rule out close prior work in forecasting that R2 may find | yes: it supports acceptance |
| Methodological Rigor | quality_rubrics: Rigor | NOT_ASSESSED | — | R1's remit; I comment only where rigor affects adoption (W7) | outside seat | no |
| Evidence Sufficiency | quality_rubrics: Evidence; R3 generality lens | PARTLY_MEETS | Tab. 1; supp. N.5–N.6; absence (W2) | Strong within SGG PredCls; the generality evidence uses label-derived groupings and no released checkpoints outside SGG | depends on remedies 3–4 | yes: main reason for Borderline |
| Argument Coherence | quality_rubrics: Coherence | PARTLY_MEETS | text: p. 4, l. 217–219; p. 5, l. 367–368 | The practical rationale (shift robustness) is overstated, and the title's mean-recall question has no bridge | fixable mostly by writing plus one analysis | yes |
| Writing Quality | quality_rubrics: Writing | MEETS | Sec. 1, Sec. 5 | Clear, direct and candid; minor terminology split between paper and supplementary | — | no |
| Literature Integration | quality_rubrics: Literature | NOT_ASSESSED | — | R2's remit; I give cross-field leads only | outside seat | no |
| Significance & Impact | quality_rubrics: Significance; R3 config | PARTLY_MEETS | Fig. 2; p. 7, l. 470–474 | High potential across VQA, long-tail and MLLM evaluation, not yet demonstrated beyond one SGG method and one benchmark | could become EXCEEDS with W2/W3 remedies | yes |

**Recommendation rationale**: The unresolved criteria that bear on the decision are Evidence Sufficiency (generality) and Argument Coherence (mean-recall bridge, shift-robustness claim). Both can be repaired within the six-week window with the ranked remedies above, and none requires a new theory or a large compute budget. The paper's originality and clarity do not offset these gaps, but they make it very likely that the gaps are worth closing. Current form: **Borderline → Major Revision**.
