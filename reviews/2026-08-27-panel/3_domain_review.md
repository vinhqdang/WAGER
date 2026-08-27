# Domain Review Report (Peer Reviewer 2)

## Reviewer Identity
Peer Reviewer 2 (Domain) — proper scoring rules, U-statistics, comparative forecast evaluation, and sensitivity analysis for unmeasured confounding. Independent; did not see any other seat's report.

## Overall Recommendation
Major Revision

## Confidence (1-5)
4 — re-derived the key algebraic claims by hand and independently verified via web search that the recommended comparison literature actually exists and says what is claimed.

## Summary Assessment
WAGER takes the classical Murphy/DeGroot-Fienberg/Bröcker calibration–resolution decomposition, normally applied to one forecaster, and repurposes it as a paired, finite-sample U-statistic with modern inference machinery attached to a model-*pair* gain. That repurposing is real and useful, and the manuscript is honest about scope throughout. The Bregman generalization, asymptotic normality theorem, DM/GW corollary, and Cauchy–Schwarz sensitivity bound are all competently stated and, on inspection, correctly derived.

The one substantive concern: the manuscript's stated argument for why WAGER differs from "decompose each model separately and subtract" (Section 2.5, first distinguishing point) does not survive direct algebraic checking — for the self-prediction/attenuation mechanism the paper itself formalizes, separately debiasing each model's resolution term and subtracting gives *exactly* WAGER's own estimator, term for term, because the whole construction is linear in the score contrast. This does not sink the paper — the second distinguishing point (inference for a specific pairwise estimand) is solid and is where the real contribution lives — but the argument as written needed correction. A closely related published bias-correction for the single-model resolution term (Ferro & Fricker, 2012, QJRMS) was missing from the bibliography and bears directly on this point.

## Strengths
- Section 2.5's second distinguishing point (no inference for a specific pairwise gain exists in the classical literature) is accurate and is the paper's real claim to novelty.
- Theorem 2 (Bregman-score covariance identity) is proved correctly and is a clean generalization: the label-independent part of any Bregman score cancels for the same reason it does for the quadratic score.
- Corollary 2 (DM/GW relation) correctly states what DM and GW test and correctly identifies the total-gain statistic at the trivial partition as that differential's sample mean; appropriately modest framing.
- The sensitivity-bound section is careful about scope — explicitly hedges that WAGER's setting differs from a causal-effect estimand, rather than claiming a reduction to the Rosenbaum/Cinelli-Hazlett machinery. Verified independently that Cinelli & Hazlett (2020) and Freidling & Zhao (2025) both concern sensitivity analysis for a causal effect, confirming the manuscript's hedge is the correct level of claim.
- The self-correction in `report/REPORT.md` (sensitivity-proposition derivation error caught and fixed) is good practice; the corrected proof is now valid.
- Proposition 3 (coarsening) reused for two purposes (empirical robustness finding and confounding bound) is elegant, and the paper is explicit that the coarsening term is not sign-definite.

## Weaknesses

**[Major] Section 2.5's first distinguishing argument does not hold as stated.** The manuscript claimed "the bias does not cancel under subtraction because it scales with each model's own cell counts." Checked directly: the attenuation proof is purely algebraic in a generic per-instance vector H_i(·); it never uses that H is a difference of two models. Applying the identical argument to a single model's own score in place of H: the naive in-sample plug-in resolution for either model is biased by the *same* factor (n_c-1)/n_c, because both models share the same φ-partition and hence the same n_c in every cell. Since covariance is bilinear, subtracting the two separately-debiased single-model resolutions gives bit-for-bit WAGER's own Proposition 4 result. The "does not cancel" claim is incorrect for the mechanism the paper itself formalizes. *Fix requested*: drop/qualify the claim or reframe around what actually differs (inference apparatus). — *Addressed in this pass*: the false argument was removed; the real point (inference for the contrast) was kept and sharpened with the recommended citations.

**[Major] Missing reference: Ferro & Fricker (2012), *A bias-corrected decomposition of the Brier score*, QJRMS 138(668):1954–1960.** Verified via web search (Wiley DOI 10.1002/qj.1924); directly relevant — shows a comparable correction is already known for the single-model resolution term, which recalibrates the "not available for the single-model decomposition" novelty claim in the Introduction. — *Addressed in this pass*: cited, and the introduction's contribution bullet reworded accordingly.

**[Minor]** The "clustered Diebold–Mariano" language blurs serial vs. cross-sectional dependence; one clarifying sentence would help. — *Addressed in this pass*.

**[Minor/Moderate]** The term "confounder" in Section 3.5 imports causal vocabulary into a non-causal, descriptive setting; Related Work already flags this distinction but Section 3.5 itself doesn't repeat it at first use. — *Not yet addressed; queued*.

**[Minor] Missing adjacent literature: DeLong, DeLong & Clarke-Pearson (1988), Biometrics 44:837–845** (paired-correlated-AUC comparison via generalized U-statistic) — structurally close precedent for comparing two correlated models via a paired U-statistic. Verified to exist. — *Addressed in this pass*: cited.

**[Minor] Missing standard reference: Jolliffe & Stephenson, *Forecast Verification: A Practitioner's Guide*** (Wiley, 2003/2012) — the standard synthesizing textbook for the classical decomposition. Verified to exist across two editions. — *Not yet addressed; queued, low priority*.

## Literature Coverage Assessment
Coverage of the core proper-scoring-rule and forecast-comparison canon is accurate and appropriately used. The 2025–2026 supplementary citations read as genuine and appropriately hedged; two spot-checked (Waghmare & Ziegel, Cinelli & Hazlett) match their claimed content exactly. The gap was specifically in the single-model resolution-bias-correction literature (Ferro & Fricker) and the paired-U-statistic-comparison literature (DeLong et al.), both close enough to WAGER's own mechanisms that their absence weakened the novelty argument.

## Theoretical Framework / Positioning Assessment
The framework — U-statistic representation, Hájek projection, Lindeberg–Feller CLT, Cauchy–Schwarz/Popoviciu bounding — is standard, correctly assembled machinery applied to a well-posed new estimand. Positioning relative to DM/GW and to the OVB/sensitivity literature is accurate and appropriately non-overclaiming. Positioning relative to the classical single-model decomposition was where the paper overstated its case (now corrected); the fallback argument (inference apparatus for a specific pairwise estimand) is sound and sufficient once the first argument is fixed.

## Missing Key References
- Ferro & Fricker (2012) — verified, added.
- DeLong, DeLong & Clarke-Pearson (1988) — verified, added.
- Jolliffe & Stephenson (2003; 2nd ed. 2012) — verified to exist; not yet added (low priority, largely redundant with already-cited Murphy/DeGroot-Fienberg/Bröcker).
- [UNVERIFIED search lead] Demšar (2006), JMLR 7 — statistical comparison of classifiers; not independently verified this session.
- [UNVERIFIED search lead] possible Siegert/Bröcker follow-ups in the meteorological verification literature beyond Siegert (2014), which was verified and added.

## Questions for Authors
1. Can you confirm the corrected Section 2.5 argument (now: inference for the contrast, not point-estimate non-cancellation)?
2. Is Ferro & Fricker's (2012) correction known independently of this review, and how does the attenuation proposition relate to it beyond the linear transplant described?
3. Would one sentence distinguishing cross-sectional from serial dependence in Corollary 2 help forestall over-reading the DM equivalence? (Now added.)
4. Would you add one explicit sentence distinguishing the omitted-stratifier setting from a causal-confounder setting at first use of "confounder" in Section 3.5?

## Minor Issues
- Tables 1 (`tab:sensitivity`) and 2 (`tab:sensitivity-numeric`) both instantiate the same coarsening comparison; consider cross-referencing more explicitly.
- The parallel sentence construction using "confounder" for two different estimand types (Section 2.4) could be split for clarity.
