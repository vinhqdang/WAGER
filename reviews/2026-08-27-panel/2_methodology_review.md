# Methodology Review Report (Peer Reviewer 1)

### Reviewer Identity
Peer Reviewer 1 (Methodology) — semiparametric/asymptotic statistics, U-statistic theory, influence-function inference, and sensitivity analysis for unmeasured confounding. Independent; did not access `reviews/2026-08-10-panel/` or any other seat's report.

### Overall Recommendation
Major Revision

### Confidence (1-5)
4 — every theorem/proposition/corollary in 3method.tex and Appendix A was re-derived independently from first principles, and the influence-function derivation and Ā_i formula were cross-referenced against `wager/antisymmetric.py`. Lower confidence specifically on Theorem 3's variance-consistency argument, which depended on asymptotic regimes the paper did not fully specify (now fixed — see below).

### Summary Assessment
This is a mathematically careful paper. Theorem 1, its generalization to the Bregman-score family (Theorem 2), the coarsening proposition, the exact attenuation proposition, and the sensitivity bound and its worst-case corollary all check out under direct re-derivation — including confirming the Bregman construction correctly recovers the log score as `log q_y`, a check the manuscript itself didn't show; the coarsening proof's law-of-total-covariance use; the attenuation identity's arithmetic; and the sensitivity proposition's two-step Cauchy-Schwarz argument (the previously-caught "sum of square roots" error is now correctly stated as a "product of two square-root sums"). Code and tests match the stated formulas exactly.

The one substantive gap found: the proof of Theorem 3 (asymptotic normality) invoked a within-cell law of large numbers for variance-estimator consistency that requires per-cell sample sizes to diverge, but the paper's own regularity conditions and its own reported data (VG150 cells "dominated by n_c=2") did not support that. The CLT for the point estimate itself is sound; the variance-estimator consistency proof, as originally written, was not.

### Strengths
- Theorem 1 and its proof: covariance-sum identity and quadratic-score specialization both correct.
- Theorem 2 / Bregman generalization: re-derived S_psi(q,y) for both named psi; log-score specialization correctly collapses to log q_y.
- Proposition (coarsening): correct, textbook law-of-total-covariance application; matches `test_coarsening_proposition_law_of_total_covariance`.
- Proposition (attenuation): algebra verified independently; matches `test_attenuation_proposition_matches_insample_plugin`.
- Sensitivity proposition and corollary: two-step Cauchy-Schwarz argument correctly assembled; Table `tab:sensitivity-numeric` arithmetic confirmed (K=50, M=2, crude bound=50.00).
- The finite-sample identity is enforced at runtime in `decompose_gain` (raises RuntimeError on failure), not merely asserted in prose.
- `report/REPORT.md` documents a real derivation error caught and fixed in the sensitivity proposition; independently re-derived the corrected version and confirmed correct.
- Diebold-Mariano/Giacomini-White corollary: equivalence at the trivial partition is immediate and correctly stated, including the qualification that clustering corrects for image-level rather than serial dependence.

### Weaknesses

**[Major] Theorem 3's variance-consistency proof invoked an asymptotic regime inconsistent with the paper's own reported data.** The appendix proof stated consistency followed from a per-cell WLLN "under condition (iii)" — but (iii) is an aggregate identified-fraction condition, not a per-cell one; a fixed cell's n_c is not bounded by it. The paper's own experiments describe VG150 cells as Zipf-distributed with most eligible cells at n_c=2, which does not diverge. Fix requested: either supply a genuine many-small-cells consistency argument, add an explicit condition requiring n_c→∞ (and reconcile it with the reported n_c=2-dominated regime), or reframe the claim as empirically validated (the 94.0% coverage simulation) rather than proved as stated. — *Addressed in this pass*: added an explicit condition (v) (fixed, finite φ-support with positive limiting mass per cell) and corrected the proof to derive within-cell consistency from (v) rather than (iii), with an honest caveat that (v) is an idealization not attained in-sample by the real VG150 application.

**[Minor]** Condition (iii)'s role in the original proof restated (iv)'s definition rather than deriving it; a formal condition on cluster-size distribution (i.i.d. or uniformly integrable) would be expected by a stats-journal referee.

**[Minor] Floored log score is not exactly the Bregman-generated log score.** The implemented log score floors at ε=1e-6; Corollary cor:bregman's identity is exact only for the unfloored log q_y. *Addressed in this pass*: added a clarifying sentence after the corollary.

**[Minor]** Table `tab:cifar-cal`'s "raw" row (20-split average, disjoint audit half) and Table `tab:cifar`'s full-split number for the nominally same comparison differ (-0.19569 vs -0.19427); disclosed in caption but easy to misread — a footnote at first appearance would help.

**[Minor]** No multiplicity adjustment across the many reported randomization tests and sensitivity rows; the paper's CIs-are-primary defense is reasonable but a sentence on family-wise error would help.

### Detailed Theorem-by-Theorem Notes
- Theorem `thm:population`: statement and proof correct.
- Theorem `thm:bregman`: statement and proof correct; label-independence cancellation verified directly.
- Corollary `cor:bregman`: correct; both named ψ's confirmed.
- Proposition `prop:coarsen`: correct, standard law-of-total-covariance with nested conditioning.
- Proposition `prop:sensitivity`: correct as now stated (product-of-sums form); re-derived independently.
- Corollary `cor:sensitivity-crude`: correct Popoviciu application; table arithmetic checks out.
- Theorem `thm:sample`: deterministic identity correct; unbiasedness-requires-independence-not-exchangeability claim verified as genuinely necessary.
- Proposition `prop:attenuate`: correct, verified algebraically.
- Theorem `thm:clt`: point-estimate CLT sound; variance-estimator consistency proof had the gap described above (now fixed).
- Corollary `cor:dm`: correct and appropriately hedged.

### Statistical Reporting Adequacy
Strong overall: signed effect sizes with 95% CIs throughout, coverage/identified-fraction reported alongside every estimate, randomization p-value floors explicitly flagged, calibration-matching used as an assumption check, unusually thorough reproducibility (fixed seeds, verification script, independent-code-path check to five decimals). Gaps: no multiplicity correction (acknowledged, defensible); CIFAR multi-seed "spread rather than interval" reporting is honest but non-standard.

### Questions for Authors
1. Can you supply a rigorous consistency argument for the variance estimator covering the small-, fixed-n_c regime your own data exhibits, beyond the idealized-condition framing now added?
2. Is the identified-subpopulation estimand implicitly assumed relative to a fixed (non-growing-with-N) set of φ-cells? Does Theorem 3 still apply if the number of distinct cells grows with N?
3. Is Corollary cor:bregman's log-score identity intended to be read as exact only for the unfloored log score? (Now stated explicitly.)

### Minor Issues
- Table cross-referencing footnote for the raw/calibration-split N difference.
- The crude sensitivity bound's looseness (three orders of magnitude at K=50) could be stated more prominently in the main text.
- A one-sentence acknowledgment near Theorem 3 that reported coverage is empirical evidence, not a formal test of the idealized asymptotic regime.
