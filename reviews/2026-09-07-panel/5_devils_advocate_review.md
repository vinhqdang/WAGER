# Peer Review Report — Devil's Advocate

## Manuscript Information
- **Title**: An Exact Decomposition of Paired Score Differences: Separating Prior Fit from Within-Group Resolution
- **Manuscript ID**: none (venue-neutral fresh submission; prior round JSPI-D-26-00452R1, rejected)
- **Review Date**: 2026-09-07
- **Review Round**: Round 5 (fifth revision; simulated panel 3 of 3)

---

## Devil's Advocate Review

### Calibration Status
`NOT_CALIBRATED`

### Reviewer Role
Devil's Advocate (fixed fifth seat). Remit: core-argument challenge, cherry-picking,
confirmation bias, logic-chain validation, overgeneralization, alternative paths,
stakeholder blind spots, and the "so what?" test. I do not score journal fit, statistical
design, literature coverage, or practical implications; those are other seats'.

### Review Focus
I attacked (i) whether the contribution survives the "technical note" reading four
editors have now taken, (ii) whether §5.2's flagship verdict is a finding or a choice,
(iii) whether the temperature protocol makes ΔR an estimand or an artefact of a fixed
scale, (iv) whether Proposition 3 reassures without constraining, (v) whether §5.3's
one-page summary outruns Appendix E, and (vi) whether the new worked example is a fair
witness. All numeric checks below were run read-only against the committed artifacts and
the released estimator; every figure I quote is real output, reproduced in the anchors.

---

### Criterion-Bound Judgements

| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Core thesis defensibility (DA Challenge 1) | `references/quality_rubrics.md` § Required judgement form; agent § Challenge 1 | PARTLY_MEETS | `equation: Thm. 2 (finite-sample identity) — ΔT_c = ΔP_c + ΔR_c holds exactly` | The identity and its inference are correct and verifiable; the *named* separation into "prior fit" and "resolution" is where the thesis over-reaches, not the algebra. | I did not audit the appendix proofs line by line; I audited the identity's behaviour numerically via the released estimator. | Yes — the title claim is the labelling, not the identity. |
| Evidence selection (DA Challenge 2) | agent § Challenge 2 | DOES_NOT_MEET | `dataset: results/sensitivity_bound.json — the only committed results file the manuscript neither cites nor verifies` | Of two committed sensitivity computations the paper reports the uninformative one and omits the one whose value is unfavourable. | The omission may be inadvertent; the direction of the omission is not in doubt. | Yes — see C1. |
| Confirmation bias (DA Challenge 3) | agent § Challenge 3 | PARTLY_MEETS | `text: §5.1 "confirming that the protocol removes exactly the confidence-scaling channel"` | Discriminant validity is tested in one direction only (prior does not leak into ΔR) and the converse coupling is neither tested nor stated. | "Exactly" is defensible for the simulated arm; the untested converse is the gap. | Yes — see M3. |
| Logic-chain validity (DA Challenge 4) | agent § Challenge 4 | DOES_NOT_MEET | `table: Table 4 (tab:sggaudit), calibration-matched quadratic row — ΔP = −0.18258, a loss, cited as the content of a gain` | The headline attributes a *gain* to a channel whose measured change is a *loss* (ΔP = −0.18258), across incommensurable units. | The §5.2 body statement is correct; the defect is confined to abstract/highlights/conclusion/cover letter. | Yes — see M6. |
| Overgeneralization (DA Challenge 5) | agent § Challenge 5 | DOES_NOT_MEET | `text: §5.3 "points the same way with the roles of the two schedules exchanged --- which is the point"` | A raw, single-pair text result is set beside a calibration-matched CIFAR result as corroboration, in a paper whose own evidence shows that control moves ΔR by up to 0.175 on real models. | The appendix states the caveat; the main-text summary does not carry it. | Yes — see M7. |
| Alternative paths (DA Challenge 6) | agent § Challenge 6 | DOES_NOT_MEET | `absence: §3.5 and §6 — expected a comparison against a recalibration-invariant (rank/AUC-based) within-cell discrimination contrast; checked §2 related work, §3.5, §4.1, §6, Appendix E` | A recalibration-invariant estimand would dissolve the paper's largest confound; the paper cites the paired-AUC precedent and dismisses it in a subordinate clause without noting the invariance. | Whether the rank version admits as clean an exact identity is genuinely open; that is the paper's to argue, not to skip. | Yes — see M8. |
| Stakeholder blind spots (DA Challenge 7) | agent § Challenge 7 | PARTLY_MEETS | `text: §6 "A benchmark that archived per-example probabilities alongside its leaderboard would make this kind of audit routine"` | The parties asked to bear the adoption cost, and the authors whose checkpoints are audited in rescaled form, are named but not consulted. | Scope-limited: enumerating absent voices only; not their content. | No — presentation-level. |
| "So what?" / incremental contribution (DA Challenge 8) | agent § Challenge 8; `report/REPORT.md` submission history | PARTLY_MEETS | `text: report/REPORT.md "No reported value changed in this revision --- this was a presentation pass"` | The delta over Murphy/Bröcker + Diebold–Mariano is real but narrow (inference for the pairwise contrast, two exact finite-sample facts); the empirical payload does not raise the stakes because its verdict is choice-determined. | This is a significance judgement, which is properly the Journal-Fit seat's; I record it only as it bears on my C2. | Yes — jointly with C2. |
| Field-norm severity calibration (DA Challenge 9 / #215) | agent § Challenge 9 | MEETS | `absence: this report — expected any CRITICAL/MAJOR whose severity rests on an asserted field norm; checked C1, C2, M1–M9` | No finding here rests on "the field should do X"; every one rests on the manuscript's own arithmetic, its own committed artifacts, or its own stated protocol. | None identified. | No — self-check. |

Do not total, weight, average, or mechanically map these judgements to issue severity or an editorial recommendation.

---

### Genuine strengths (stated before the attack, per Review Discipline #5)

Three things the paper does that I could not break. First, every one of the 83 literals
quoted in the manuscript traces to a committed results file: I ran
`experiments/verify_manuscript_numbers.py` and it passed 83/83. Second, the paper does
**not** score-shop on its flagship result — the conclusion and the cover letter both
report the quadratic and log resolution estimates *with both intervals* and state that the
two disagree, which is more disclosure than the field's norm and more than the previous
round offered. Third, Proposition 1's exact $(n_c-1)/n_c$ attenuation is a clean,
checkable, genuinely useful result: it removes a design decision (sample splitting) that
an applied analyst would otherwise have to make and defend.

---

### Strongest Counter-Argument

Here is how I would refute this paper if I held the opposite view.

Your identity is correct and your inference is correct, and neither is the issue. The
issue is that you have built an estimand that is indexed by three analyst choices — the
grouping variable $\phi$, the Bregman generator $\psi$, and the confidence scale — and you
decline to fix any of them, while your abstract states a determinate verdict. Your own
flagship table proves the cost. The same two checkpoints, the same relations, five
configurations you yourself report: $\widehat{\Delta R} \in \{-0.21711, -0.12619,
-0.01355, -0.00006, +0.04396\}$. Three qualitatively different answers — significant
resolution loss, exact null, significant resolution gain — spanning a range of $0.261$,
which is $4{,}528$ times the point estimate your abstract is built on. Your Theorem 3 is
the mechanism: it establishes that each Bregman generator induces its own exact
resolution estimand, so "the within-group resolution gain" has no referent until $\psi$ is
named. You present that theorem as a unification. It is in fact your non-identification
result, and you do not draw the corollary.

Then the confound. You concede $\Delta R$ is not recalibration-invariant, and your answer
is a protocol. But a protocol that fixes the confidence scale is a choice of scale, not an
invariance — and your own numbers show the choice dominates every effect you report. In
simulation, pure recalibration produces $\widehat{\Delta R} = -0.488$. On real models,
recalibrating one CIFAR classifier *against itself* produces $-0.17464$. Your largest
Visual Genome resolution gain is $0.01439$. The nuisance channel is thirty-four times the
signal, and your remedy is to stipulate one point on it. Meanwhile the protocol changes
the very quantity being split: on the same audit half, $\widehat{\Delta T}$ moves from
$-0.11548$ raw to $-0.18264$ matched. You did not decompose the released checkpoints. You
decomposed two models you rescaled.

And your sensitivity bound does not rescue this. Your repository contains the sharp form:
robustness value $0.0613$. A confounder at the strength *you* call plausible explains your
headline away.

---

### Issue List

#### CRITICAL

| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|
| C1 | Cherry-picking / data–conclusion mismatch (Ch. 2, 4) | §3.5 asserts that "an unrecorded confounder would have to act with an implausibly strong, simultaneous effect on both channels to explain away a reported $\widehat{\Delta R}$ of the size seen in" Appendix E, and supports it with the *crude* Popoviciu bound ($KM/2 = 50$, minimum $\bar\rho = 0.00015$) which it then concedes is $6{,}739\times$ too loose to constrain anything. The sharp form of the paper's own Proposition 3 **was computed and committed**: `results/sensitivity_bound.json` gives $B = 0.23284$ and robustness value $\rho^\dagger = 0.06127$ for precisely the Appendix E headline pair (MLP-SPATIAL vs MLP-CLASS, $\widehat{\Delta R} = 0.014267$, $n_* = 227{,}337$). At the sensitivity parameter the manuscript itself offers as plausible — "say $\bar\rho=0.1$" — the sharp bound is $0.02328$, which **exceeds** $\lvert\widehat{\Delta R}\rvert = 0.01427$. So the necessary confounding strength to zero the flagship resolution gain is $6.1\%$, not "implausibly strong", and the paper's own sharp calculation says so. The manuscript never reports $B$, never reports $\rho^\dagger$, is the only committed results file absent from `verify_manuscript_numbers.py`, and §3.5 instead explains the sharper form as costing "needing them rather than only the committed cell-level aggregates" — phrasing that implies it was not computed. Every reported $\widehat{\Delta R}$ inherits this: the VG-visual advantage ($+0.00641$) is smaller still, so its robustness value is lower again. Uncorrected, the paper asserts robustness its own analysis refutes, in the direction that favours it. Repairable by reporting $B$ and $\rho^\dagger$ per audited pair and rewriting §3.5's conclusion — but not by revision of wording alone, since the honest number changes what Appendix E can claim. | `dataset: results/sensitivity_bound.json — robustness_value_rho_dagger = 0.061272 and bound_B = 0.232845 against reasoning_gain = 0.014267` | 5 — core expertise: sensitivity analysis for unmeasured confounding; recomputed $\rho^\dagger = \lvert\Delta R\rvert/B$ and the $\bar\rho=0.1$ bound directly from the committed file | | |
| C2 | Core thesis / stronger counter-narrative (Ch. 1, 4, 8) | The flagship verdict is a choice, not a finding, and the abstract and highlights state it as a finding. Table 4 reports five configurations of the *same* model pair on the *same* relations, and $\widehat{\Delta R}$ takes the values $-0.21711$ ($\phi=$ subject, raw), $-0.12619$ (log, raw), $-0.01355$ (quadratic, raw), $-0.00006$ (quadratic, calibration-matched) and $+0.04396$ (log, calibration-matched): three mutually exclusive qualitative verdicts, range $0.26108$, i.e. $4{,}528\times$ the headline point estimate. The abstract's "overwhelmingly group-frequency fit" is *false* for two of those five rows — at raw log, $\lvert\Delta R\rvert = 0.12619$ against $\lvert\Delta P\rvert = 0.15897$ and the committed `reasoning_share` is $-3.85$ (resolution is $3.85\times$ the total gain); at $\phi=$ subject, $\Delta R = -0.21711$ dominates $\Delta P = +0.10175$ outright. Neither the abstract nor the highlights records that the claim holds only under calibration matching at the class-pair cell. The paper's own Theorem 3 is the mechanism and the paper does not draw its corollary: a distinct exact resolution estimand exists per Bregman generator, so "the within-group resolution gain" is not a single quantity, and §5.2's refusal to adjudicate ("nothing in Section 3.1 privileges one proper score's resolution estimate as the 'true' one") is therefore correct *and* fatal to a determinate headline. Proposition 2 does not repair the $\phi$ half: it relates a partition only to its own coarsenings, and my four-point construction below shows two partitions of *identical* granularity and coverage giving $\widehat{\Delta R} = 0.000$ and $+1.600$ on the same four cases and same model pair. Uncorrected, the paper's sole main-text application cannot state a verdict, and the "so what?" rests on that application. Fixing this needs either a declared principle for choosing $(\phi,\psi)$ or an application whose verdict is stable across them — not a rewrite. | `table: Table 4 (tab:sggaudit) — the five $\widehat{\Delta R}$ cells: $-0.01355$, $-0.12619$, $-0.21711$, $-0.00006$, $+0.04396$ for one model pair` | 5 — core expertise: estimand identification and robustness of reported effects; range and share recomputed from `results/sgg_audit_motifs.json` | | |

#### MAJOR

| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|
| M1 | Logic chain / protocol misstatement (Ch. 4) | §5.1 states that "Averaging over repeated splits gives the calibration-matched rows reported throughout." That is false for the flagship row. `experiments/run_sgg_audit_wager.py` draws **one** calibration half from a single fixed seed (`np.random.default_rng(20260811)`), fits $T^*$ once on it, and audits the complement once; `experiments/vg_prior_consequence.py` does the same with seed `20260810`. Only the CIFAR scripts average (`N_SPLITS = 20`). Two consequences. (i) The word "throughout" is wrong for the two studies the main text leads with. (ii) The reported interval on the flagship row, $[-0.00120,+0.00109]$ (half-width $0.00115$), is the image-cluster sandwich conditional on that one split and excludes split-to-split and temperature-estimation variability — and the paper's own simulation puts the residual sd of the matched estimator at $0.001725$ over 200 runs, i.e. *larger* than the interval half-width it reports. The claim "indistinguishable from zero" is therefore stated at a precision the protocol does not support, and the honest statement is weaker: the quadratic-score remainder cannot be resolved below the protocol's own noise floor. Fix: average the SGG and VG-visual matched rows over splits and widen the interval to include the split component, or state the single-split conditioning explicitly. | `text: §5.1 "Averaging over repeated splits gives the calibration-matched rows reported throughout."` | 5 — core expertise: reading the committed estimation scripts; single-split draw and `N_SPLITS = 20` asymmetry read directly from source | | |
| M2 | Alternative paths / recalibration taken to its conclusion (Ch. 6) | The recalibration protocol is a choice of scale presented as a control, and the paper's own numbers show the choice dominates every effect reported. Simulated pure recalibration: raw $\widehat{\Delta R} = -0.48762$, i.e. $33.9\times$ the largest VG resolution gain the paper reports ($0.014387$). On *real* models: recalibrating one CIFAR classifier against itself ("CE(cal) vs CE (confound size)") gives $\Delta R = -0.17464$ with $\Delta P = +0.37960$ — $12.1\times$ the VG gain and $4.0\times$ the matched log-score SGG remainder. Worse, the protocol is not a single well-defined intervention: on the same CIFAR pair, `cal-old` gives $\Delta R = -0.01962$ and `cal-both` gives $-0.23991$, a factor of $12$ apart, and both are defensible readings of "match confidence". And matching changes the quantity being split, not only the split: on the identical audit half the SGG $\widehat{\Delta T}$ moves from $-0.11548$ raw to $-0.18264$ matched, a shift of $0.06716$ — $1{,}165\times$ the resolution estimate the matched row then reports. So the simulation cited as showing the protocol works ($-0.488 \to -0.0003$) equally shows how large the confound is relative to every real effect in the paper. Fix: report the full protocol sensitivity (raw / cal-old / cal-new / cal-both) for every audited pair as a first-class row set, and state that $\Delta R$ is defined only relative to a declared scale. | `dataset: results/cifar_recalibration.json — row CE(cal) vs CE (confound size) dR = −0.17464; row CB vs CE cal-old dR = −0.01962 against cal-both dR = −0.23991` | 5 — core expertise: calibration and proper scoring; all four magnitudes recomputed from committed JSON | | |
| M3 | Confirmation bias / one-directional discriminant validity (Ch. 3) | §5.1 concludes the channels "separate what they claim to separate" after testing one direction only. The tested direction — a prior-only improvement does not leak into $\widehat{\Delta R}$ ($0.0002$, sd $0.0035$) — is guaranteed by Theorem 1 and holds. The untested direction is the one that matters for interpreting $\Delta P$: a resolution improvement **must** load a deficit into the prior channel. Holding the cell-level prediction *exactly* fixed and increasing only case-level signal, the released estimator returns (cell-mean $q_1(\text{label }1) = 0.7500$ at every step, identical to $q_0$): $e{=}0.02 \Rightarrow \Delta P = -0.02240$, $\Delta R = +0.08000$; $e{=}0.10 \Rightarrow \Delta P = -0.16000$, $\Delta R = +0.40000$; $e{=}0.24 \Rightarrow \Delta P = -0.58560$, $\Delta R = +0.96000$. So a model that has changed nothing about its cell-level prior is reported as having lost up to $0.586$ of "prior-fit gain". $\Delta P$ is the reliability channel — Corollary 4 says so itself, calling $\widehat{\Delta P}$ at the trivial partition "the corresponding calibration term" — and reliability to a cell histogram is degraded by *any* individualization. Calling it "prior-fit gain" and glossing it as fitting "the label frequencies within groups more closely" invites exactly the inference the paper wants readers to draw about TDE and about CIFAR-CB. This bears directly on every reported $\Delta P$: the $-0.00554$ the paper reads as box geometry costing prior fit, and the $+0.11079$ it reads as CB gaining prior fit, are partly the mechanical mirror of their $\Delta R$. Fix: rename the channel to its actual referent, add the converse discriminant arm, and state the coupling wherever a $\Delta P$ is interpreted. | `text: §1 "the new model may fit the label frequencies within groups more closely, or it may match its predictions to the individual cases"` | 4 — core expertise: proper-score decomposition; the sweep is real estimator output but my "prior fit = cell-histogram fit" reading is one of two defensible glosses, which is the point | | |
| M4 | Logic chain — the worked example misexplains its own arithmetic (Ch. 4) | The four-point example is the centrepiece of this revision, and the sentence that explains its most important number is wrong on the quantity it cites. §2 attributes model B's $\Delta P = -1/8$ to prior fit having deteriorated, "averaged over the cell it predicts $0.625$ for label 1 where the truth is $0.75$" — but $q_0$ predicts $0.5$ against that same truth, so B's cell-averaged prediction is *twice as close*. Scoring each model's cell-mean prediction against the cell's own label frequencies gives model B a prior-fit **gain** of $+0.09375$ ($=3/32$) where $\Delta P$ reports a **loss** of $0.125$: opposite signs, from the exact comparison the sentence invokes. (Model A, by contrast, is consistent: $+0.125$ both ways.) A reader who checks the example by hand — which is precisely what the revision invites — finds the stated reason contradicted. The arithmetic of $\Delta T$, $\Delta P$, $\Delta R$ and the $3/4$ attenuation is all correct; only the causal gloss is wrong, and it is wrong in the direction of M3. Fix: replace the explanation with the correct one (case 4's individualized prediction is penalized against three transported label-1 draws) and say plainly that this penalty is the reliability cost of individualization, not a deterioration of frequency fit. | `text: §2 "because its prior fit got worse: averaged over the cell it predicts 0.625 for label 1 where the truth is 0.75"` | 5 — core expertise: the example is fully checkable by hand and I reproduced both quantities with the released estimator | | |
| M5 | Core thesis / audited object (Ch. 1, 4) | The abstract says "on two released scene-graph checkpoints" and the cover letter that "the models are not ours"; the numbers the abstract rests on are from two models the authors rescaled. The headline row applies $T^* = 2.4968$ to MOTIFS and $T^* = 0.9160$ to MOTIFS-TDE, fitted on half the images, and audits the other half ($n = 92{,}027$, 50% of the relations). §5.2 concedes the necessity ("TDE is designed to change the decision rule rather than to emit calibrated probabilities"), which is honest, but the framing then trades on the audit being of the released artifacts. It is not: the released pair gives $\Delta T = -0.11651$, $\Delta P = -0.10296$, $\Delta R = -0.01355$ with a CI excluding zero — a *significant* resolution loss, which is a different published finding from "indistinguishable from zero". A field reader who wants to know what the released TDE checkpoint does gets the raw row; the abstract gives them the rescaled one. Fix: state in the abstract that the verdict is for temperature-matched variants on a held-out half, and say what the released pair gives. | `text: Abstract "On two released scene-graph checkpoints, a ten-point gain in a widely reported metric is overwhelmingly group-frequency fit."` | 5 — core expertise: reading the audit script and results; $T^*$ values and $n$ read from `results/sgg_audit_motifs.json` | | |
| M6 | Overgeneralization / unit slippage in the headline (Ch. 4, 5) | The highlights assert "A released debiasing method's ten-point metric gain is almost all prior fit" and the abstract "a ten-point gain in a widely reported metric is overwhelmingly group-frequency fit". Both are sign-wrong and unit-incommensurable. Sign: the prior channel's measured change is $\Delta P = -0.18258$, a *loss*; a gain cannot consist of a channel that fell. What the decomposition actually shows is that TDE's mean-recall gain is bought by *degrading* prior fit while leaving the resolution channel at most marginally changed — a different and more interesting sentence. Units: the resolution remainders ($-0.00006$ of quadratic score, $+0.04396$ of log score) are compared to "ten points of mean recall" with no bridge, and the paper's own committed bridge file (`results/vg_metric_bridge.json`) covers only its three VG predictors and only accuracy/MRR/R@5 — never mean recall, and never this pair. So "changes within-group resolution by at most a small fraction of that" (cover letter, echoed in §6) divides a proper-score quantity by a rank-metric quantity. Note also that the selected metric is one of three the paper itself reports moving: $mR@50$ $+10.17$pt, $R@50$ $-20.23$pt, top-1 $-14.04$pt. §5.2's own body statement ("is compatible with a within-group resolution change that is either zero or a small fraction of the total") is correct and should simply be promoted. | `text: Highlights "A released debiasing method's ten-point metric gain is almost all prior fit"` | 5 — core expertise: reading the reported channel signs and the committed bridge file's field list | | |
| M7 | Overgeneralization / evidence laundering across the appendix boundary (Ch. 5) | §5.3 summarizes the text study as pointing "the same way with the roles of the two schedules exchanged --- which is the point, since composition is a property of a recipe applied to particular data and not of the recipe's name." Appendix E concedes the study "uses a single trained pair per schedule rather than the multi-seed, calibration-matched protocol" applied to CIFAR — and `results/text_lt_results.json` contains no calibration-matched row and no fitted temperature at all. So the sentence sets a *raw, single-pair* result beside a *calibration-matched, multi-seed* CIFAR result and calls them corroborating, in a paper whose own evidence shows the missing control moves $\Delta R$ by $-0.17464$ on real CIFAR classifiers and by $-0.48762$ in simulation, against a text effect of $+0.04317$. The CIFAR temperatures the paper does report ($T^*$: CE $2.845$, CB $3.515$, DRW $2.612$) show this model family does differ visibly in confidence — the paper's own stated trigger for the control. Separately, the summary reports only the favourable $\phi$: the text DRW verdict flips from $+0.00155$ (null, superclass) to $-0.00319$ (null, global) to $-0.00901$ with a CI excluding zero (tier, a significant resolution *loss*), which Appendix E discloses and §5.3 does not. Moving the evidence to an appendix while keeping an unqualified generalization in the main text is the laundering pattern; the fix is to carry the caveat into §5.3 or drop the corroboration claim. | `dataset: results/text_lt_results.json — no regime, T_old or T_new field and no calibration-matched comparison in any of its six rows` | 5 — core expertise: verified by enumerating every key of every comparison in the committed file | | |
| M8 | Alternative paths (Ch. 6) | The paper's largest limitation has an alternative estimand that removes it, and the paper does not weigh it. Because $\Delta R$ is defined through a proper score on probabilities, it is not invariant to monotone recalibration; a *rank*-based within-cell discrimination contrast is invariant to every monotone transformation by construction, needs no temperature, no half-sample split, and no split-fraction choice. The paper knows the construction: §2.2 cites the paired correlated-AUC U-statistic of DeLong et al. as "a structurally close precedent ... applied to an unconditional ranking statistic rather than a declared-cell gain" — a subordinate clause that notes the difference and omits the property that matters. Nothing in the paper explains why an exact within-cell rank contrast was rejected in favour of inventing a protocol against the confound. A second unweighed alternative: for the flagship pair specifically, the substantive conclusion ("TDE moves the prior") is already legible from the fitted temperatures ($2.50 \to 0.92$), the $R@50$/$mR@50$ trade, and a reliability diagram — no decomposition required — which is a real challenge to the audit's marginal value. Fix: state why the rank route was not taken, or take it as the invariant companion statistic. | `text: §2.2 "the same construction applied to an unconditional ranking statistic rather than a declared-cell gain"` | 4 — core expertise: scoring rules and rank statistics; whether the rank version admits an equally exact identity I did not verify, and that uncertainty is stated | | |
| M9 | Core thesis / the adversarial worked example (Ch. 1, 4) | The paper's worked example is constructed so the decomposition looks decisive; the adversarial counterpart shows it is not determined by anything the paper's protocol declares. Take four cases in which the new model is perfectly right and perfectly confident on all four: $q_0 = (0.5,0.5)$ throughout, $q_1 = (0.9,0.1)$ for cases 1–2 (labels $1,1$) and $(0.1,0.9)$ for cases 3–4 (labels $2,2$); $\Delta T = +0.480$ under all groupings. With $\phi$ pairing case 1 with case 3 and case 2 with case 4 — two cells, size 2 each, coverage 100% — the released estimator returns $\Delta P = -1.120$, $\Delta R = +1.600$, i.e. **333%** of the total gain is "within-group resolution". With $\phi$ pairing case 1 with case 2 and case 3 with case 4 — also two cells, also size 2, also coverage 100% — it returns $\Delta P = +0.480$, $\Delta R = 0.000$: **none** of it is resolution, and this same model is reported as a pure prior refit. One cell gives $+1.067$. Same four points, same two models, same granularity, same coverage; verdicts 0%, 222%, 333%. The paper's only stated protocol is "the finest defensible partition is the conservative default", "declare $\phi$ before looking", and "report pre-declared alternatives" — none of which distinguishes two partitions of *equal* fineness, and Proposition 2 is silent because neither is a coarsening of the other. This is the formal version of what Table 4 shows empirically ($\phi=$class-pair $-0.01355$ vs $\phi=$subject $-0.21711$, a factor of 16). Fix: state the equal-granularity indeterminacy explicitly in §3.4/§6, and require that $\phi$ be justified by the data-generating process rather than by fineness. | `equation: Prop. 2 (coarsening decomposition) — the between-cell covariance term is defined only between a partition and its own coarsening, so it does not relate two partitions of equal granularity` | 5 — core expertise: constructed and executed against the released estimator; all three $\Delta R$ values are real output | | |

#### MINOR

| # | Dimension | Issue Description | Evidence Anchor | Confidence |
|---|-----------|-------------------|-----------------|------------|
| m1 | Evidence consistency | The Appendix E headline resolution gain is committed at two unreconciled values: $0.014387$ (`antisymmetric_results.json`, `sensitivity_bound_check.json`, and the manuscript) and $0.014267$ (`sensitivity_bound.json`, same pair, same $n_*=227{,}337$). Immaterial to any conclusion, but it should be reconciled if the sharp bound is reported per C1. | `dataset: results/sensitivity_bound.json vs results/sensitivity_bound_check.json — reasoning_gain 0.014267 vs delta_r_class_pair_phi 0.014387 for one pair` | 4 — direct file comparison |
| m2 | Abstract framing | The abstract lists "bound the effect of an unrecorded grouping variable" among the paper's results with no indication that the data-free form is, by the paper's own committed `looseness_ratio`, $6{,}739\times$ too loose to constrain the effect it is applied to. §3.5 discloses this; the abstract advertises the bound without it. | `text: Abstract "bound the effect of an unrecorded grouping variable, and show that using a group's own label frequency"` | 4 — abstract and §3.5 compared directly |
| m3 | Reported quantities withheld | The committed results record `reasoning_share` $=-3.85$ (CI $[-6.23,-1.47]$) for the raw log-score row — the one number that displays resolution exceeding the total gain by nearly fourfold — and the manuscript reports the share nowhere for this pair, having declared in §3.6 that it reports $\widehat{\Delta R}$ "not a thresholded ratio". The policy is defensible; its effect here is that the least favourable reading is the one with no summary statistic. | `dataset: results/sgg_audit_motifs.json — raw log row reasoning_share = −3.8502 with share_ci [−6.2288, −1.4717]` | 4 — read from the committed file |
| m4 | Released-artifact framing | The released estimator still names the channel `reasoning_gain` and its module docstring still reads "Within-cell Antisymmetric Gain Evaluation of *Reasoning*", the interpretation the manuscript now explicitly disclaims ("It does not prove causal inference, compositional understanding, or robustness"). A reader arriving from the paper meets the abandoned reading first; the compatibility aliases exist, so the docstring can lead with the current one. | `dataset: wager/antisymmetric.py — module docstring naming the channel Reasoning, and primary result field reasoning_gain` | 5 — read from source |

---

### Ignored Alternative Explanations/Paths

1. **A recalibration-invariant estimand instead of a recalibration protocol.** A within-cell
   rank/concordance contrast between the two models is invariant to every monotone
   transformation of either model's probabilities, so the paper's largest confound — worth
   $-0.488$ in simulation and $-0.175$ on real models, against a largest real effect of
   $0.014$ — simply does not arise. It also needs no half-sample split, no fitted
   temperature, and no split-fraction choice, removing M1's variance omission at the same
   time. The paper cites the paired-AUC precedent and does not consider it. This is the
   most parsimonious alternative to the entire calibration apparatus and it is unweighed.
2. **A cluster bootstrap over the two classical single-model decompositions.** §2.1 argues
   that inference does not transfer because single-model variance estimators "supply no
   covariance between it and a second model's resolution estimated from the same data".
   That is true of the analytic route and irrelevant to the resampling route: resampling
   images, recomputing both single-model decompositions, and differencing gives a valid
   interval for the contrast with no new theory at all. The paper's central claim to
   novelty is that this inference did not previously exist; the cheapest counterexample is
   never mentioned or tested.
3. **The audit's conclusion without the audit.** For the flagship pair, "TDE operates on
   the prior channel" follows from the fitted temperatures ($2.50 \to 0.92$), the
   $R@50 \downarrow 20$pt / $mR@50 \uparrow 10$pt trade, and the audited method's own stated
   construction — all three of which the paper reports. A more parsimonious reading of
   §5.2 is that the decomposition confirmed what TDE's own authors claim, at the cost of
   two analyst choices whose settings determine the sign of the residual.
4. **Reporting the per-cell distribution rather than a magnitude-weighted scalar.** Most
   eligible VG150 cells sit at $n_c = 2$ (the paper says so), where $\widehat{\Delta R}_c$
   is a single antisymmetric pair contrast. An aggregate dominated by such cells invites a
   distributional presentation the paper does not attempt.

---

### Missing Stakeholder Perspectives

- **Benchmark maintainers**, who are asked in §6 to archive per-example probability vectors
  and to declare $\phi$ on submitters' behalf. They bear the entire adoption cost and are
  not consulted, costed, or cited anywhere.
- **The authors of the audited released checkpoints**, whose method is characterized in the
  abstract on the basis of temperature-rescaled variants of their weights (M5), with no
  response channel and no statement of what the released pair gives.
- **Deployers for whom the prior channel is the payload.** The paper states three times
  that a prior-fit gain "is not illegitimate" and never presents a case in which the
  decomposition changes such a deployer's decision.
- **Submitting authors under a maintainer-declared $\phi$**, who would be evaluated on an
  estimand whose value M9 shows is not determined by the maintainer's stated selection rule.

---

### Unexamined Premise

The paper assumes throughout that *within-group resolution is the achievement worth
measuring* and that prior fit is the channel needing exposure. Every rhetorical move
depends on it: the introduction's "what has the new model learned?", the worked example's
verdict that aggregate scores "order two models by the wrong criterion", §5.2's framing of
a mean-recall gain as being of the less interesting kind. The paper disclaims the premise
verbally — "The decomposition says where a gain lives, not whether it is worth having" —
and then never once shows the split changing anyone's action. There is no worked case in
which an evaluator, a maintainer, or a deployer should do something different having seen
$(\Delta P, \Delta R)$ rather than $\Delta T$. That absence is the honest core of what four
editors have called insufficient interest: the paper has built an instrument and validated
it carefully, and has not exhibited a decision it changes. A single such case — a
leaderboard ranking that reverses, a model selection that flips, a deployment under label
shift where the prior channel's fragility is priced — would do more for the "so what?"
than any of the five theorems.

---

### Observations (Non-Defects)

- **The paper is not score-shopping.** I tested this specifically. The conclusion and the
  cover letter both report the quadratic and log resolution estimates *with both
  intervals* and state that the two disagree; §5.2 declines to adjudicate and gives the
  correct reason. The abstract's magnitude claim holds under *both* calibration-matched
  scores. Where the framing does lean is on the calibration-matched regime and the
  class-pair cell without saying so (C2, M5) — not on the choice of score. The prior
  panel's complaint that the log-score interval was missing has been answered.
- **The numbers verify.** `experiments/verify_manuscript_numbers.py` passes 83/83 against
  the committed results. Nothing in my report is a quotation error; every finding above is
  about what the numbers mean or which numbers were left out.
- **Declining to adjudicate between proper scores is the correct move**, given Theorem 3.
  The defect is not the refusal; it is the definite article in the abstract that the
  refusal makes unavailable.
- **Proposition 1 is genuinely useful** and is the result I would keep if the paper had to
  shrink to a note: an exact $(n_c-1)/n_c$ statement that retires a design choice.

---

## The "so what?" test, stated at length

**The editors' case, made as forcefully as it can be.** Strip the apparatus and the
contribution is: compute the classical resolution term for two models instead of one,
apply the standard leave-one-out correction that makes the degree-2 U-statistic unbiased,
and attach a cluster-robust interval. Every piece is characterized by the paper itself as
immediate. §2.1: "$\Delta R$ is a resolution *difference* in exactly this sense, and we
build on the fact rather than obscure it: WAGER is not a new scoring rule". §3.3, on the
Bregman generalization: "Nothing in the proof of Theorem 1 uses properness". Corollary 4:
"immediate from the definitions". §3.5's bound is Cauchy–Schwarz plus Popoviciu and the
paper's own file records it as $6{,}739\times$ too loose to constrain the effect it is
applied to. Proposition 2 is the law of total covariance. Theorem 5 is Lindeberg–Feller
on a Hájek projection. The single-model finite-sample bias this pairs with was already
corrected in the literature the paper cites (Ferro 2012). And the empirical payload — one
audit — confirms what the audited method's own authors say their method does, with a
residual whose sign is set by two choices the paper declines to make. On that reading this
is a well-executed technical note.

**Does it survive scrutiny?** Partly, and the surviving part is narrower than the paper
claims but wider than the editors allow. Two things are genuinely new and genuinely
useful. First, §2.1's gap argument is correct and checkable: variance estimators for the
single-model decomposition target one resolution term and supply no covariance with a
second model's estimate from the same data, so differencing two single-model
decompositions leaves the contrast's sampling variability unaddressed. Forming the paired
gain vector first makes the influence function that of the difference, in one pass. That
is a real hole in the classical toolkit, correctly identified — although the paper weakens
its own case by never testing the obvious resampling alternative (Alternative Path 2).
Second, Proposition 1 is an exact statement that retires a design decision. Both are
small; both are right; both are the kind of thing applied statistics should publish.

**Where the editors are right, and where they mislocate the problem.** They are right that
the current package is a note, not a paper. But "insufficient interest" is the wrong
diagnosis, and it is why the fifth revision missed. The theory would carry a full paper if
the application delivered one stable, surprising verdict. It does not: C2 shows the
flagship verdict spans significant loss, exact null, and significant gain across five
configurations the paper itself reports, and the abstract states one of them. So the paper
does not fail for want of interest; it fails because its only main-text application cannot
state a finding, and the Unexamined Premise above is why nobody notices: the paper never
exhibits a decision the split would change. This revision changed no number
(`report/REPORT.md`: "No reported value changed in this revision — this was a presentation
pass"), which means it did not touch either problem. Rewriting the front matter answers
the referee who complained about legibility; it does not answer the editors who complained
about substance, and those were two different objections.

**What would change my assessment.** One of: (i) an application whose $\Delta R$ verdict
is stable across both scores and at least two defensible $\phi$, with the sharp
sensitivity bound reported alongside it; or (ii) a single worked case where the split
reverses a decision an evaluator would otherwise make. Either would convert a note into a
paper. Neither requires new theory.

---

## Questions for Authors

1. `results/sensitivity_bound.json` reports $B = 0.23284$ and $\rho^\dagger = 0.06127$ for
   the Appendix E headline pair. Why is neither number in the manuscript, and how do you
   reconcile $\rho^\dagger = 0.061$ with §3.5's claim that an unrecorded confounder "would
   have to act with an implausibly strong" effect — given that §3.5 itself offers
   $\bar\rho = 0.1$ as plausible, at which the sharp bound $0.02328$ exceeds
   $\lvert\widehat{\Delta R}\rvert = 0.01427$?
2. §5.1 says the calibration-matched rows are averaged over repeated splits. The SGG and
   VG-visual scripts each use one fixed-seed split. What is the flagship $\widehat{\Delta
   R}$ and interval when averaged over, say, 20 splits with the split component included
   in the variance — and does it still exclude the $\pm 0.0017$ residual sd your own
   simulation reports for the matched estimator?
3. Theorem 3 implies a distinct exact resolution estimand per Bregman generator. Given
   that your flagship pair returns $-0.00006$ (null) under one and $+0.04396$
   (significantly positive) under another on identical calibrated data, on what grounds
   should a reader who must report a single number choose? If there are none, should the
   abstract state a single verdict?
4. My four-point construction (M9) gives $\widehat{\Delta R} = 0.000$ and $+1.600$ for the
   same model pair under two partitions of identical granularity and 100% coverage. Which
   does your stated protocol select, and if neither, what does "the finest defensible
   partition" mean when two partitions are equally fine?
5. Holding a model's cell-mean prediction exactly fixed and increasing only case-level
   signal drives $\Delta P$ from $-0.022$ to $-0.586$. Is the channel you call "prior-fit
   gain" intended as the reliability term (as Corollary 4 implies) rather than as fit to
   the group's label frequencies — and if so, should its name and its gloss in §1 change?

---

## Criterion-Bound Judgements (rubric dimensions)

Calibration status: `NOT_CALIBRATED`

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | `references/quality_rubrics.md` | NOT_ASSESSED | — | Journal-Fit and Domain seats' remit, not the DA's. | Out of scope by role boundary. | No |
| Methodological Rigor | `references/quality_rubrics.md` | NOT_ASSESSED | — | R1/Methodology seat's remit. | Out of scope by role boundary. | No |
| Evidence Sufficiency | `references/quality_rubrics.md` | DOES_NOT_MEET | `dataset: results/sgg_audit_motifs.json — five reported ΔR values for one pair spanning −0.21711 to +0.04396` | The sole main-text application yields three mutually exclusive verdicts across the paper's own reported configurations, and the sharp sensitivity computation that would bound the appendix effects is omitted (C1, C2). | I assess sufficiency only as it bears on the stated conclusions, not study design. | Yes — C1 and C2 are unresolved and decision-bearing. |
| Argument Coherence | `references/quality_rubrics.md` | PARTLY_MEETS | `text: §6 "case-level evidence changes by at most a small fraction of that, possibly none"` | The identity and its scope statements are coherent; the headline surfaces carry a sign error and a unit slippage (M6), and the worked example misexplains its own key number (M4). | Repairable by rewriting; the body text already contains the correct formulations. | Yes — M4 and M6 require revision but the core survives. |
| Writing Quality | `references/quality_rubrics.md` | NOT_ASSESSED | — | Not a DA dimension; the referee's legibility objection is answered elsewhere. | Out of scope by role boundary. | No |
| Literature Integration | `references/quality_rubrics.md` | NOT_ASSESSED | — | R2/Domain seat's remit. | Out of scope by role boundary. | No |
| Significance & Impact | `references/quality_rubrics.md` | PARTLY_MEETS | `absence: §5.2, §6, Appendix E — expected one case in which the decomposition reverses a decision an evaluator would otherwise make; checked §1, §2, §5.2, §5.3, §6, Appendix E` | Two contributions are real and narrow (pairwise contrast inference; the exact attenuation result); the empirical payload does not raise the stakes, and no decision-changing case is exhibited. | Significance is properly the Journal-Fit seat's call; recorded here only as it grounds the "so what?" analysis. | Yes — jointly with C2. |

Explain the recommendation by naming the unresolved decision-bearing criteria and their repairability: the decision-bearing unresolved items are C1 (an assertion of robustness contradicted by the paper's own committed computation, repairable only by reporting the number and revising what Appendix E claims) and C2 (a flagship verdict determined by two analyst choices the paper declines to make, not repairable by wording). Do not total, weight, average, or mechanically map these judgements to an editorial recommendation; the synthesizer decides.
