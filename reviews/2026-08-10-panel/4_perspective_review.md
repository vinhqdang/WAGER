# Reviewer 3 — Cross-disciplinary Perspective & Practical Impact

> Simulated review panel, 2026-08-10. Persona: ML evaluation / benchmarking / auditing researcher with forecast-verification and fairness-auditing background. Focus: practical impact, the φ problem, cross-disciplinary bridges, interpretation risks.

## What this paper is really about (independent framing)

Stripped of the vision framing, this is a paper from forecast verification: it takes the classical Murphy/DeGroot–Fienberg/Bröcker reliability–resolution decomposition of a proper score, applies it to the *contrast* between two frozen forecasters rather than to one forecaster, and replaces the fitted conditional-climatology baseline with an exact leave-one-out label-transport counterfactual inside declared strata. The deliverables are (a) an exact finite-sample identity ΔT = ΔP + ΔR, (b) a debiasing result (the (n_c−1)/n_c attenuation of the naive plug-in), (c) an aggregation result (coarsening adds a between-cell covariance — essentially a Simpson's-paradox/aggregation-bias statement made exact), and (d) cluster-robust and randomization inference. To my eye it is a *paired resolution-difference estimator with honest inference*, and the authors — to their credit — say almost exactly this themselves in `2related.tex` §2.5 ("ΔR_c is best understood as a resolution difference, not a new quantity"). That candor is rare and welcome. The question this review focuses on is whether the instrument, as packaged and framed, will actually change what anyone does.

## Practical impact assessment (adoption path, usability, missing pieces)

**Who can run it.** The requirements are genuinely light: four aligned arrays (two probability matrices, labels, cell ids), pure NumPy, O(NK), one function (`decompose_gain` in `README.md`). Tests and reproduce scripts exist. This is above-average packaging for a methods paper.

**Who will run it, on what.** Here the picture narrows sharply, and the paper does not confront it:

1. **Full predictive distributions are required** (`5discussion.tex` lines 37–41 admits "it requires released logits or probabilities"). Benchmark leaderboards overwhelmingly collect top-1/top-k predictions, and published papers rarely release probability matrices. Adoption therefore requires either (i) benchmark maintainers changing submission formats, or (ii) authors auditing their *own* model pairs. The paper should say which audience it is designing for and what each concretely does differently on Monday.

2. **Closed-set, discrete-label tasks only.** The introduction motivates with recent audits of multimodal shortcut exploitation (`1intro.tex` lines 17–19), but those benchmarks are largely generative/free-form, where neither a K-way probability vector nor a discrete φ exists. As written, the method's actual habitat is PredCls-style and classification-style benchmarks. That is still a real habitat — but the framing borrows urgency from a class of benchmarks the method cannot currently audit.

3. **No in-the-wild demonstration.** All six VG predictors and all three CIFAR classifiers are purpose-built by the authors (`4experiments.tex` §5.2, §5.6). The instrument is validated, but never pointed at anything anyone else claimed. One audit of two *published* SGG checkpoints would transform the impact claim from "this instrument works" to "here is what it reveals about the literature."

4. **The decision layer is missing.** Suppose a reviewer sees ΔR = +0.006, p = .002. Then what? The paper rightly refuses thresholds (`3method.tex` lines 143–145), but offers no reporting convention, no effect-size anchors, no worked "how to read this table" guidance. A one-page reporting template ("WAGER card": declared φ and rationale, coverage, both channels signed, sensitivity rows) would cost little and do more for adoption than any theorem in the paper.

**The "so what" test.** If every claim is true: authors of long-tail and SGG papers gain a cheap supplementary table; benchmark maintainers gain an argument for collecting probabilities; reviewers gain a question to ask ("what is your alignment channel against the frequency baseline?"). That is a genuine but incremental change to practice, contingent on demonstrations the paper does not yet contain. The two experimental vignettes (CLIP model punished by the prior channel; CB's cancelling ±0.196 channels) are excellent *illustrations*; they are not yet *consequences* — nothing downstream is shown to improve because the decomposition was known.

## The φ problem (choice, multiplicity, guidance adequacy)

The method's meaning is entirely conditional on φ, and the authors know it. What exists is better than most: choose φ before looking at results, justify from the data-generating process, report finer/coarser alternatives (`5discussion.tex` lines 16–19); the coarsening proposition makes the direction of sensitivity exact; the degenerate φ = label case (ΔR ≡ 0 by construction) is explicitly flagged in `4experiments.tex` §"Choosing φ" — the best paragraph in the paper for a practitioner.

Remaining gaps:

- **Multiplicity without a mechanism.** "Choose before looking" is stated but unenforceable. In fairness auditing this exact problem (analyst-chosen subgroups) led to structural answers: maintainer-declared strata, pre-registration, or guarantees quantified over a *class* of groupings (multicalibration/multiaccuracy). WAGER should recommend that the *benchmark*, not the submitting author, declares φ, and should discuss what happens when an author reports the most favorable of several candidate φ's.
- **The "finest defensible" default silently changes the estimand.** Finer φ ⇒ more singleton cells ⇒ different identified subpopulation (VG: 99.0% coverage, benign; but this is not general). Comparisons across granularities in `tab:sensitivity` therefore mix two effects: the between-cell covariance term of Prop. coarsen *and* a population change. Report coarse-φ estimates restricted to the fine audit's identified subsample to isolate the former.
- **Multiple simultaneous nuisances.** Real audits often have two candidate priors (e.g., class pair *and* a geometry bin). Intersecting them destroys coverage; no guidance is given. Even a paragraph acknowledging this and pointing to the open continuous-φ extension (`5discussion.tex` lines 27–29) applied to composite priors would help.
- **"Reasoning."** The disclaimers are diligent (`1intro.tex` lines 46–48; `README.md`; `5discussion.tex` lines 12–17), and the tables consistently say "instance alignment." But the acronym bakes the over-claim into the method's *name*, which is the one part of a paper that travels without its disclaimers. "Model X shows significantly more reasoning (WAGER, p=.002)" is exactly how this will be quoted. Since ΔR provably also credits unrecorded within-cell shortcuts (`3method.tex` lines 61–63), the honest name is the one the tables already use. I would strongly encourage renaming the R of the acronym (e.g., "…of Residual gain") or, minimally, a boxed statement that "reasoning" is a historical label for what is formally an alignment/resolution difference.

## Cross-disciplinary bridges (made, missed, mischaracterized)

**Made, and made well:** the Murphy/DeGroot–Fienberg/Bröcker resolution lineage (`2related.tex` §2.5) is engaged honestly, including recent decomposition work; the U-statistic and permutation-test positioning is careful; the relationship to the abandoned betting formulation is stated without defensiveness.

**Missed — each would widen the audience:**

1. **Comparative forecast evaluation (Diebold–Mariano; Giacomini–White conditional predictive ability).** WAGER is, at its core, inference on a paired score differential — the DM tradition's exact object — plus a decomposition of it. Not citing this literature is a real gap: it is where readers from econometrics and verification will place the method, and conditional predictive ability (evaluating the gain conditional on covariates) is the closest existing relative of "gain conditional on φ."
2. **Label shift / prior shift** (Saerens et al.'s EM prior correction; Lipton et al.'s BBSE). The "prior channel" is precisely the component that label-shift correction can add or remove post hoc. This bridge is not cosmetic — it supplies the missing *decision relevance*: a gain that is prior-transported is exactly the gain that (a) evaporates under prior shift and (b) can be manufactured by recalibrating any model to the test prior. See Weakness 2 for the experiment this implies.
3. **Fairness/disaggregated evaluation.** The tier analysis (`tab:cifar-tier`) *is* subgroup auditing; multicalibration is the formal treatment of "calibration within cells of φ, for many φ simultaneously" and directly informs the multiplicity discussion above. One paragraph connecting these would bring in an entire adjacent community.
4. **The abandoned e-value/betting machinery** is dropped a little too completely. For a *fixed* test set the fixed-sample redesign is clearly right; but the paper's own motivating scenario — leaderboards audited as submissions arrive — is sequential, and anytime-valid inference is the natural tool there. A sentence acknowledging that the sequential-leaderboard variant is a distinct, open problem would preempt the obvious question.

**Mischaracterized:** nothing seriously. The claim that separately decomposing each model and subtracting is biased and inference-free (`2related.tex` lines 96–105) is fair as stated.

## Interpretation risks & broader implications

Two symmetric misuse modes, of which the paper addresses neither head-on:

- **Dismissal misuse:** "two-thirds of your gain is prior-recoverable, hence mostly not real" (the DRW framing, `4experiments.tex` lines 354–362, invites this reading). But fitting the deployment label distribution better is *genuine, decision-relevant* skill whenever the deployment prior matches the benchmark prior — the verification community's climatology lesson. Passages like "the punishment is... for failing to reproduce the annotation prior" (`4experiments.tex` lines 251–257) tilt the rhetoric toward "ΔP = suspect," which the formalism does not support. The paper needs an explicit paragraph: ΔP is not cheating; its worth depends on prior stationarity between benchmark and deployment.
- **Rescue misuse:** the CLIP vignette — worse by every aggregate, "significantly better" alignment — will be cited to defend arbitrary underperforming models as "better at reasoning." As long as ΔR is never connected to any downstream benefit, that narrative is unfalsifiable. The fix is available *within the authors' own experiment* (see Weakness 2).

Also: with N = 227,337 and a 499-shift test whose minimum attainable p is .002, nearly every row reports p = .002 (`tab:wager-results`, `tab:vgvisual`). Statistical vs. practical significance deserves one honest sentence.

## Strengths

1. Rare intellectual honesty about lineage: the method is presented as a transport construction on a *known* resolution concept, not as a new score (`2related.tex` §2.5), and the redesign section says plainly what was removed from the rejected version and why.
2. The exact, assumption-free finite-sample identity with no fitted nuisance, no smoothing, no split, no threshold is a real methodological simplification, and the attenuation proposition converts a design choice into a theorem.
3. Interpretation limits are repeatedly and correctly stated (no causality, shortcut caveat, φ-conditionality) — above the norm for this literature.
4. The two experimental vignettes are pedagogically excellent: CB's ±0.196 cancelling channels behind a +0.001 aggregate, and the CLIP model's deficit sitting entirely in the prior channel, are exactly the failure modes of aggregate scoring made concrete. The independent covariance-identity cross-check on real models is a nice touch.
5. Usable software surface: one-function NumPy API, cached-output workflow, tests, reproduce commands (`README.md`).

## Weaknesses (numbered, each with location + concrete fix)

1. **No audit of any model the authors did not build.** All specimens are purpose-built (`4experiments.tex` §5.2, §5.6, §5.5). *Fix:* audit one pair of published checkpoints with released probabilities (e.g., two SGG systems from the lines cited at `1intro.tex` lines 13–15) and report what the decomposition says about a claimed gain in the literature.
2. **ΔR is never linked to any decision-relevant outcome, leaving both misuse modes open.** The CLIP result (`4experiments.tex` §5.5) begs its own follow-up: recalibrate MLP-VISUAL-S's prior channel post hoc (logit adjustment / multiply in the FREQ prior) and show whether the prior-corrected model then beats MLP-SPATIAL-S on the aggregate; equivalently, evaluate under a shifted label prior and show ΔP evaporates while ΔR survives. Either experiment converts the diagnostic into a prediction and closes the rescue-narrative loophole. *Fix:* add one such experiment; it requires only the already-cached probability matrices.
3. **"Reasoning" in the method's name over-claims relative to what is measured.** Location: title, acronym expansion (`1intro.tex` lines 46–48), `README.md` title, despite tables using "instance alignment." *Fix:* rename the quantity uniformly to instance-alignment/residual gain and either re-expand the acronym or add a prominent boxed disclaimer at first use.
4. **ΔP is rhetorically framed as illegitimate.** Location: `4experiments.tex` lines 251–257 ("punishment... for failing to reproduce the annotation prior"), and the "prior-recoverable" framing at lines 354–362. *Fix:* add a paragraph to `5discussion.tex` stating when prior-channel gain is genuine value (stationary deployment prior) and when it is not (prior shift), with the label-shift citations from Weakness 6.
5. **φ multiplicity has advice but no mechanism.** Location: `5discussion.tex` lines 16–19. *Fix:* recommend maintainer-declared φ; require reporting *all* pre-declared candidate φ's; discuss selection-over-φ explicitly, referencing the multicalibration literature as the formal treatment of many-φ guarantees.
6. **Missing bridges: Diebold–Mariano/Giacomini–White comparative forecast tests; label-shift correction (Saerens et al., BBSE); multicalibration/disaggregated evaluation.** Location: `2related.tex` §§2.3–2.5. *Fix:* one short paragraph each; the DM/GW connection in particular is where statistically literate readers will expect the paper to locate itself.
7. **Cross-granularity comparisons conflate decomposition change with population change.** Coarser φ audits a different identified subsample than finer φ (singleton exclusion). Benign at VG's 99% coverage, not in general. *Fix:* report coarse-φ rows restricted to the fine audit's identified subsample, or add the caveat where Prop. coarsen is invoked empirically.
8. **Scope boundary understated relative to the motivation.** The intro leans on generative/multimodal shortcut audits that the method, requiring K-way probability vectors and discrete φ, cannot currently touch; VQA is promised only as future work. *Fix:* a crisp scope statement (closed-set, probabilistic outputs, discrete declarable prior) early in §1, plus a sentence on how a discrete-answer-space benchmark could be mapped in.
9. **No practitioner decision layer.** Locations: `3method.tex` lines 143–145 (no-threshold stance), `tab:wager-results` (uniform p=.002 from the 499-shift floor, unremarked). *Fix:* add a reporting template (declared φ + rationale, coverage, signed channels, sensitivity rows) and one sentence on randomization-test resolution and practical vs. statistical significance at this N.

## Scores (0–10)

- **Practical impact:** 5 — clean tool, real but narrow habitat; impact currently contingent on demonstrations (Weaknesses 1–2) the paper doesn't yet contain.
- **Clarity of framing:** 8 — unusually honest about what the method is and is not; docked for the acronym and the ΔP rhetoric.
- **Cross-disciplinary grounding:** 7 — the verification bridge is made properly; the DM/GW, label-shift, and fairness-audit bridges are conspicuously absent.
- **Responsible interpretation:** 7 — diligent disclaimers throughout, but both concrete misuse modes (dismissal and rescue) are left structurally open because ΔR is never tied to a consequence.

## Recommendation

**Major revision** — with a genuinely positive disposition. The instrument is sound, simply built, honestly positioned, and better packaged than most; nothing here challenges its validity. What separates this from a paper that changes practice is achievable within one revision cycle and mostly reuses artifacts the authors already have: (i) one audit of published third-party models (W1); (ii) one experiment linking ΔR to a downstream consequence — prior recalibration or prior-shift evaluation of the existing CLIP triple (W2), which I regard as the single highest-value addition; (iii) the ΔP-legitimacy paragraph and the naming fix (W3–W4); and (iv) the short bridge paragraphs (W6). Items (iii)–(iv) are writing; items (i)–(ii) are modest experiments on cached probabilities. Without (i) and (ii), the paper is a well-validated instrument demonstrated only on purpose-built specimens, and its two headline vignettes remain illustrations rather than consequences.
