# Editorial Decision and Revision Roadmap — 2026-09-07 panel

**Manuscript.** *An Exact Decomposition of Paired Score Differences: Separating Prior Fit
from Within-Group Resolution*, at commit `ba220dd` (52 pp.).
**Panel.** Five role-separated seats, all committing blind. Provenance and the limits on
reading them as independent judgements: `_panel_provenance.md`. Calibration status
`NOT_CALIBRATED`; no venue-alignment claim is made (`criteria_binding_unavailable`).

---

## Decision: **Major Revision**

Unanimous among the four seats that issued a recommendation (Journal-Fit, Methodology,
Domain, Perspective all: Major Revision; Devil's Advocate issues no verdict by design).
The Journal-Fit seat's recommendation is conditional and flips to *reject at this venue*
absent an econometric or forecasting application.

**What the panel agrees the paper gets right.** The algebraic core is sound: the
Methodology seat independently reproduced Theorems 1–3, Corollary 1 and Propositions 1
and 3 in exact arithmetic, confirmed the new Section 2 worked example number by number,
and found all 83 quoted literals tracing to committed results. The Devil's Advocate
checked specifically for score-shopping and found none — conclusion and cover letter both
report both scores with both intervals and state their disagreement. The Perspective seat,
the panel's proxy for the referee who could not follow the previous version, restated the
entire contribution correctly in plain language without using any of the paper's coined
vocabulary. **The legibility objection that ended the JSPI submission is answered for the
front matter.**

**What blocks acceptance.** Three things, in order of severity, none of which is an
arithmetic error and none of which the previous revision's added theory addresses.

---

## Adjudication of CRITICAL findings

Iron Rule #4 requires every Devil's Advocate CRITICAL to be adjudicated visibly. Two were
raised; a third CRITICAL came from the Domain seat. All three were re-verified by the
synthesizing session before adjudication.

### CRIT-1 (Domain W1, seconded independently by Methodology W6) — **VALIDATED**
**ΔR is not the classical resolution term.** Classical DeGroot–Fienberg resolution depends
on the forecast only through the partition its level sets generate, so a strictly monotone
recalibration leaves it exactly invariant. The paper's own §6 states that ΔR is *not*
recalibration-invariant. Both cannot be true of one quantity.

Verified directly: under a strictly monotone recalibration, classical resolution holds at
`0.046160` while the within-cell covariance moves `0.257157 → 0.184819`; on a
recalibrated-versus-raw pair the estimator returns `ΔR = −0.072338` where the difference of
classical resolutions is exactly `0.000000`. The Methodology seat's independent
counterexample gives `ΔR̂ = −0.35964444` against a Murphy–DeGroot resolution difference of
exactly `0`.

Theorem 1 is untouched — `ΔR_c = Σ_y Cov(H_X(y), 1{Y=y} | C=c)` is definitional and true.
The defect is the *attribution*. ΔR is a Yates-type forecast–outcome covariance contrast,
which equals twice a resolution difference only under within-cell calibration; Yates (1982)
is the uncited source of the covariance representation the paper credits to Murphy and to
DeGroot & Fienberg.

**Aggravating circumstance specific to this revision.** The overclaim pre-dates commit
`ba220dd`, but that commit made it structural: it promoted "resolution" from an occasional
gloss to the paper's primary term, swept `alignment → resolution` through five files, and
put the word in the title. The rewrite amplified the one claim the panel finds false.

### CRIT-2 (Devil's Advocate C1) — **VALIDATED**
**A committed computation contradicts the paper's central reassurance, and the paper omits
it.** §3.5 asserts an unrecorded confounder "would have to act with an implausibly strong,
simultaneous effect on both channels" to explain away a reported ΔR, and reports only the
crude bound it concedes is 6,739× too loose, describing the sharp form as *needing*
per-instance arrays — implying it was never computed.

It was computed and committed. `results/sensitivity_bound.json` holds `bound_B = 0.232845`
and `robustness_value_rho_dagger = 0.061272` for the Appendix E headline pair
(`ΔR = 0.014267`, `n* = 227,337`). Verified: `ρ† × B = 0.014267 = |ΔR|` exactly, and at the
paper's *own* suggested plausible `ρ̄ = 0.1` the sharp bound `0.023284` **exceeds** the
reported `|ΔR| = 0.014267`. An aggregate correlation of `0.061` suffices to explain the
headline gain away. That is not implausibly strong; it is small.

This file is also the only committed results file the manuscript neither cites nor puts
through `verify_manuscript_numbers.py` — so the verification harness the paper offers as
its integrity guarantee has a hole exactly where the least favourable number sits. No
inference about intent is drawn or needed: the correction is to report the sharp bound and
the robustness value, and to rewrite §3.5's conclusion to match them.

### CRIT-3 (Devil's Advocate C2) — **PARTIALLY VALIDATED**
**The flagship verdict is configuration-dependent and the abstract does not say so.**
Table 4's five configurations of the *same* released pair give
`ΔR = −0.21711, −0.12619, −0.01355, −0.00006, +0.04396` — three mutually exclusive
verdicts across a range of `0.26108`. "Overwhelmingly group-frequency fit" is false for the
raw log row (`|ΔR| = 0.126` against `|ΔP| = 0.159`) and for the subject-only row
(`ΔR = −0.217` dominating `ΔP = +0.102`), and neither abstract nor highlights discloses
that the claim holds at the *calibration-matched, class-pair* configuration specifically.

**Validated** as a disclosure defect in the abstract, highlights and conclusion.
**Rejected** as an accusation of selective reporting: the Devil's Advocate seat itself
verified that the body reports both scores with both intervals and states the
disagreement, and that the magnitude claim holds under both matched scores. The fix is to
name the configuration wherever the headline appears, not to change what is reported.

---

## Consensus, and where the seats disagree

**Consensus (3+ seats).**
1. The terminology reform stopped at the end of §1 (Journal-Fit W7, Perspective W4,
   Methodology minor, Domain minor). Sections 4–6 still carry four names for the grouping
   variable — "grouping variable", "declared discrete prior feature" (§4.1), "prior cell"
   (Fig. 2), "prior feature" (§6.1) — and five for ΔP. The abstract says "group" seven
   times and "cell" never; §4 says "cell" seventy-five times. Three agreement artefacts
   ("an cell" ×2, "an resolution") survive from the mechanical substitution. A referee
   would clear pp. 1–6 with relief and file the same objection about §4–§6.
2. "Prior-fit gain" is a misnomer (Domain W3, Devil's Advocate M3, Perspective minor). ΔP
   rewards reduced sharpness independently of prior fit; the Domain seat's counterexample
   gives `ΔP = +0.375` with both models' mean forecast exactly at the cell base rate, and
   Corollary 4 already concedes ΔP is the reliability channel. The `ΔR ≈ 0` audit
   conclusion survives; the *attribution* of the shift to "group-frequency fit" does not.
3. The recalibration confound is under-disclosed relative to its size (Perspective W1,
   Devil's Advocate M2, Domain W1). §1.3 "Scope, and what is not claimed" omits it
   entirely, and §2 never mentions it, although it flips the sign verdict of the paper's own
   headline audit. Magnitudes: simulated pure recalibration gives `ΔR = −0.488`, 33.9× the
   largest real gain the paper reports.

**Disagreement, adjudicated.**
- *Did moving three studies to Appendix E hurt?* Methodology says the restructure is
  mechanically clean — no dangling refs, and §5.3 an honest précis. Journal-Fit says it cost
  the interest case, because all three verdict-reversing demonstrations now sit behind the
  wall. **Both are right at different levels**, and the second is the one that matters to an
  editor weighing significance: the mechanics are sound, the rhetoric is worse. Recommend
  promoting one verdict-reversal into the main text (Appendix E.4 is the strongest: a model
  that loses every aggregate metric yet resolves individual cases significantly better).
- *Is §5.3 honest about the text study?* Methodology says yes; Devil's Advocate M7 says it
  launders a weak result. **DA prevails on the specifics** — `text_lt_results.json` contains
  no calibration-matched row or temperature at all, so setting it beside the matched CIFAR
  reading as corroboration is not supported, and §5.3 reports only the favourable φ
  (DRW `+0.00155`, null at superclass) while omitting the significant *loss* at the tier
  partition (`−0.00901`).

---

## Findings the panel raised that are new, checkable, and not yet in any prior panel

- **Theorem 4's printed sandwich variance is wrong by a factor 1/G** (Methodology W1).
  Verified algebraically: the `N_*/G` prefactor cancels the `G/(G−1)` numerator. The stated
  consistency claim is false *as printed*; Appendix B and the implementation are correct.
- **"Most eligible VG150 cells sit at the minimum size n_c = 2" is false** (Methodology W4),
  and it appears three times (§4.10, §6.1, App. B) carrying the paper's honesty statement
  about condition (v). The paper's own ablation refutes it: cells of size 2–4 are 2,286 of
  6,346 eligible cells and cover 2.7% of identified relations. **The truth is more
  favourable than the claim** — which is why this must be corrected rather than defended.
- **Corollary 2 discards `Σ_y b_y = 1`** (Methodology W5), so the free bound is `14.00`, not
  the reported `50.00`; the paper's diagnosis of its own looseness is partly an artefact of
  the discarded constraint.
- **Figure 1 is stale.** Its panel title reads "Evaluation of **Reasoning**" — terminology
  abandoned two revisions ago and exactly the jargon the retitle removed — and it is the
  text-only flowchart that `report/REPORT.md` claims was *replaced* in the third revision.
  Confirmed: `experiments/make_fig1_concept.py` does build the two-image crossing figure the
  caption describes; its output was never committed, and the script's own labels still say
  "audit cell" and "instance-alignment gain".
- **§5.1's "averaging over repeated splits … throughout" is false** (Devil's Advocate M1):
  the SGG and VG-visual matched rows each use one fixed-seed split; only CIFAR averages, and
  the omitted split variance (sd `0.001725`) exceeds the reported CI half-width (`0.00115`).
- **The worked example misexplains its own key number** (Devil's Advocate M4). §2 attributes
  model B's `ΔP = −1/8` to worse prior fit "averaged over the cell", but B's cell-mean
  prediction moves `0.5 → 0.625` against a cell frequency of `0.75` — it *improves* by
  `+0.09375`. Verified. The sign comes from within-cell dispersion, not from the cell mean.
  This is text written in commit `ba220dd`, in the section that carries the whole legibility
  fix.
- **Two equally fine partitions give incompatible answers** (Devil's Advocate, adversarial
  example). Four cases, one model pair, `ΔT = +0.480` throughout: pairing 1–3/2–4 gives
  `ΔR = +1.600` (333% share); pairing 1–2/3–4 gives `ΔR = 0.000` (pure prior refit). Same
  granularity, same 100% coverage. "Choose the finest defensible φ" cannot separate them and
  Proposition 2 is silent, because neither partition coarsens the other. This is the formal
  version of Table 4's empirical 16× swing.
- **The unexamined premise** (Devil's Advocate, "so what?"): the paper never exhibits a
  single decision the split would change — no ranking that reverses, no model selection that
  flips, no deployment priced differently. It disclaims "the decomposition says where a gain
  lives, not whether it is worth having" and then shows no case where knowing that mattered.

---

## Revision Roadmap (immutable core, source-ordered, non-ranking)

Ordered by source finding, not by recommended work order. No item is prioritised, selected,
or expanded here; author adjudication belongs in a separate sidecar.

| # | Source | Item | Minimum remedy |
|---|---|---|---|
| R1 | Domain W1 / Meth. W6 / CRIT-1 | ΔR identified with the classical resolution term in title, abstract, §1, §3.1, Cor. 3 and conclusion | State it as a Yates-type within-cell forecast–outcome covariance contrast; note it equals twice a resolution difference only under within-cell calibration; cite Yates (1982); revisit the title and the acronym's R |
| R2 | DA C1 / CRIT-2 | §3.5's robustness reassurance contradicted by `results/sensitivity_bound.json` | Report `B = 0.232845` and `ρ† = 0.061272`; state that `ρ̄ = 0.1` does not certify the headline ΔR; add the file to `verify_manuscript_numbers.py` |
| R3 | DA C2 / CRIT-3 | Headline claim's configuration-dependence undisclosed in abstract and highlights | Name the calibration-matched, class-pair configuration wherever the claim appears |
| R4 | Meth. W1 | Theorem 4's printed σ̂² is 1/G times the correct quantity | Correct the printed formula to match Appendix B and the code |
| R5 | Meth. W4 | "Most eligible cells sit at n_c = 2" false in three places | Replace with the true distribution from the paper's own ablation |
| R6 | Meth. W5 | Corollary 2 discards `Σ_y b_y = 1` | Re-derive at `1 − 1/K`; regenerate `sensitivity_bound_check.json`; update the verifier |
| R7 | Meth. W2, W3 | Theorem 4 conditions (iii) and (v) cannot both bind; Hájek remainder rate asserted at the wrong level | Drop or reconcile (iii); repair via the degenerate second-order rate, needing only `#cells = o(N_*)` |
| R8 | Meth. W7 | Granularity tables target different identified subpopulations with no coverage column | Add coverage to Tables 3 and 4 and to E.7 |
| R9 | Domain W2, W5, W6, W7, W8 | Attribution and gap-claim defects: Yates uncited; multiclass/general extensions credited to a 2026 preprint over Murphy 1973 and Bröcker 2009; the Ferro & Fricker equivalence unproven; the field's silence overstated; a false sentence in §4.10 | Correct each attribution; engage Ferro 2007, DelSole & Tippett 2014, Siegert et al. 2017 on skill-difference inference |
| R10 | Journal-Fit W1, W2, W3 | No econometric or forecasting application; the Diebold–Mariano relation absent from title, abstract and keywords; Cor. 3 invoked at non-trivial groupings where it is stated only for the trivial one | Venue decision; if econometrics, add a forecasting application and re-anchor; correct Cor. 3's invocation scope in §4.10 and E.2 |
| R11 | Journal-Fit W7, Persp. W4, +2 | Terminology reform stops after §1 | One-pass term audit across §4–§6, figures, and captions; fix "an cell" ×2 and "an resolution" |
| R12 | Persp. W1, DA M2 | Recalibration non-invariance absent from §1.3 and §2 | Add it to the scope subsection and to §2 |
| R13 | Persp. W2, W3 | "Four aligned arrays are all it needs" describes the identity, not the procedure; Figure 1 stale and mismatched to its caption | Qualify the claim; regenerate Figure 1 after updating the generator's own terminology |
| R14 | Persp. W5, W6 | Positioned against two literatures; φ-governance one-sided | Engage Kitagawa/direct standardization, Oaxaca–Blinder, DiNardo–Fortin–Lemieux, Mantel–Haenszel and collapsibility, differential item functioning, discrimination-vs-calibration in clinical prediction, partial-input baselines in NLP; qualify the maintainer-declares-φ recommendation |
| R15 | DA M1 | §5.1's "averaging over repeated splits … throughout" false for two of three matched studies | Correct the sentence; report split variance where a single split is used |
| R16 | DA M4 | §2 misexplains model B's `ΔP = −1/8` | Replace the cell-mean explanation with the dispersion one |
| R17 | DA M5, M6 | The audited object is the rescaled, not the released, pair; "ten-point metric gain is almost all prior fit" mixes mean-recall points with proper-score units and attributes a gain to a channel that fell | State what was audited; give the unit bridge or drop the compound claim |
| R18 | DA M7 | §5.3 sets an unmatched text study beside a matched CIFAR reading, and reports only the favourable φ | Report the tier-partition loss; drop the corroboration framing |
| R19 | DA M8, M9 + adversarial example | No weighing of a recalibration-invariant alternative; Prop. 2 silent between equally fine partitions | Discuss a within-cell rank/AUC contrast and a cluster bootstrap over two single-model decompositions; state the equally-fine-partition indeterminacy as a limitation |
| R20 | DA "so what?" | No decision the split would change | Exhibit one: a ranking that reverses, a selection that flips, or a deployment priced differently |

**Not adjudicated here.** Whether to retitle a second time (R1), and the venue decision
(R10), are author calls with consequences this panel is not positioned to weigh. R6 and R2
require regenerating committed results, so they change reported numbers and must not be
folded into a presentation pass.

**Bearing on the previous pass.** Commit `ba220dd` answered the JSPI referee's legibility
objection and did not touch the editors' substance objection — two different complaints, as
the Devil's Advocate seat notes. R20 is the substance objection stated concretely for the
first time across five revisions and three panels.
