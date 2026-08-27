# Editorial Decision & Revision Roadmap — WAGER manuscript (JSPI revision)

> Simulation of a 5-seat review panel run 2026-08-27, in the absence of real referee
> reports from JSPI (Ms. Ref. No. JSPI-D-26-00452, major revision). Independent, blind
> seats: Journal-Fit Reviewer, Methodology (Peer Reviewer 1), Domain (Peer Reviewer 2),
> Perspective (Peer Reviewer 3), Devil's Advocate. Individual reports:
> `1_journal_fit_review.md`, `2_methodology_review.md`, `3_domain_review.md`,
> `4_perspective_review.md`, `5_devils_advocate_review.md`.
> This is a **different, independent panel** from `reviews/2026-08-10-panel/` (that one
> reviewed the pre-redesign CVIU submission); seats were told not to read it.

## Decision: MAJOR REVISION (in progress — this document tracks what has already been fixed)

Two CRITICAL-tier issues were found and both are now fixed as of this pass. Three
further MAJOR issues were found and checked against the manuscript/code directly before
acting; two were fixed in this pass, the rest are queued below. No issue found the core
constructions (the transport identity, the finite-sample U-statistic, the estimator
implementation) to be wrong — every theorem re-derived by the Methodology seat checked
out except one proof-technique gap in the newest theorem, which is now fixed.

### Reviewer positions (as submitted, before this pass's fixes)

| Reviewer | Recommendation | Core verdict |
|---|---|---|
| Journal-Fit | Major Revision | Statistical core fits JSPI; front matter still addressed to CSDA; paper is CV-proportioned for this readership |
| Methodology | Major Revision | Every theorem re-derived and correct except the CLT's variance-consistency proof, which invoked a condition not met by the paper's own data |
| Domain | Major Revision | Literature accurate and well-hedged, but one of two stated distinguishing arguments against the classical single-model decomposition is algebraically false |
| Perspective | Minor Revision | Empirical setups are unusually faithful to their communities; CIFAR's own CB accuracy is never checked against the literature it reimplements |
| Devil's Advocate | N/A (findings only) | 1 CRITICAL (flagship claim overstated relative to a robustness check the paper itself ran), 6 MAJOR, several MINOR |

## Fixed in this pass

### CRITICAL-1 (Journal-Fit): front matter still addressed a superseded journal
`manuscript/main.tex`'s `\journal{}` macro, `manuscript/cover_letter.tex`, and
`manuscript/title_page.tex` all still addressed *Computational Statistics and Data
Analysis*, the paper's previous (now desk-rejecting) venue, despite `README.md` and
`report/REPORT.md` both stating the current target is JSPI. **Fixed**: retargeted all
three files, including the cover letter's scope argument (JSPI's inference/model-
comparison remit, not CSDA's Section I/II taxonomy) and its description of the paper's
own new theoretical content, which the CSDA-era cover letter had never been updated to
mention either.

### CRITICAL-2 (Devil's Advocate): flagship claim's significance is score-dependent, and the paper only showed the score that supported "unchanged"
Table `tab:sggaudit`'s calibration-matched log-score row (`ΔR=+0.04396`) was missing its
95% CI in the manuscript, even though the driver script had already computed one
(`results/sgg_audit_motifs.json`: `[+0.04079,+0.04714]`). Verified directly against the
committed JSON before acting. Adding it shows the log-score estimate is **significantly
positive**, not null — it does not reproduce the quadratic score's `[-0.00120,+0.00109]`.
The abstract, introduction, conclusion, and cover letter's "instance alignment is
statistically unchanged" language stated only the quadratic-score reading as the
headline finding. **Fixed**: added the missing CIs to the table and
`experiments/verify_manuscript_numbers.py`; rewrote the abstract, the relevant
introduction contribution bullet, the `4experiments.tex` result paragraph, the
conclusion, the cover letter, and one `highlights.txt` bullet (85-character Elsevier
limit) to state precisely what both scores agree on (prior-transported dominance, at
least an order of magnitude larger than either alignment estimate) versus what they
disagree on (whether any alignment remainder is exactly zero).

### MAJOR (Domain): one of the two stated distinguishing arguments against the classical decomposition is false
`2related.tex` §"Relation to classical proper-score decompositions" claimed subtracting
two separately-estimated single-model resolutions doesn't recover WAGER's own estimate
because the self-prediction bias "scales with each model's own cell counts." Re-derived
by hand: both models share the same `φ`-partition and hence the same per-cell `n_c`, so
the identical `(n_c-1)/n_c` attenuation factor (already proved, Proposition 4) applies to
each model's own naive resolution estimate, and subtracting the two recovers WAGER's own
attenuated estimate of the contrast exactly, term for term (by bilinearity of the
covariance identity). The claim as written does not survive this check. **Fixed**:
removed the false argument; kept and sharpened the paper's real distinguishing point
(inference for the *contrast* — no covariance between two single-model estimates from
the same data is available from the classical literature, even with its own bias
correction). Added three verified citations directly relevant to this point: Ferro &
Fricker (2012, QJRMS, bias-corrected single-model Brier decomposition), Siegert (2014,
QJRMS, single-model variance estimator for that decomposition), and DeLong, DeLong &
Clarke-Pearson (1988, Biometrics, paired-correlated-AUC U-statistic covariance — a close
structural precedent). Softened the introduction's contribution bullet accordingly (the
attenuation result is now framed as a transplant of a known single-model fix to the
paired case, not as something with no single-model analogue at all).

### MAJOR (Methodology): Theorem `thm:clt`'s variance-consistency proof used a condition its own data doesn't satisfy
The appendix proof claimed `Δ̂R_c →_p ΔR_c` for each cell "by the weak law of large
numbers... under condition (iii)" — but condition (iii) bounds only the *aggregate*
identified fraction, not any individual cell's size `n_c`, and the paper's own reported
regime has most eligible VG150 cells at the minimum size `n_c=2` (never growing).
Verified: a per-cell WLLN genuinely requires `n_c→∞` for that specific cell, which (iii)
does not provide. **Fixed**: added an explicit new condition (v) — `φ` has a fixed,
finite support with strictly positive limiting mass per cell, so `n_c→∞ a.s.` for every
cell in the idealized `N→∞` limit — and corrected the proof to derive within-cell
consistency from (v), not (iii). Added an explicit, honest caveat in the theorem
statement, the surrounding prose, and the discussion section: condition (v) is an
asymptotic idealization the actual VG150 application has not attained in-sample (Zipf
cell sizes dominated by `n_c=2`), and the reported 94.0%-vs-95% coverage simulation, not
the theorem directly, is the operative finite-sample evidence.

### MAJOR (Devil's Advocate): text-domain "role swap" stated as earned when it's single-seed and uncalibrated
The conclusion called the 20-Newsgroups-LT result the estimator's "sharpest
demonstration" of cross-domain generality without the single-seed,
non-calibration-matched caveat that the paper's *own* CIFAR-100-LT study showed is
load-bearing (a calibration-only control there moved the channels by a magnitude
comparable to the entire text-domain finding). **Fixed**: reworded the conclusion to
state the finding as suggestive pending the fuller (multi-seed, calibration-matched)
protocol, not as already earned.

### MAJOR (Devil's Advocate): "genuine"/"genuinely" register undercuts the paper's own Reasoning→Resolution rename
The paper renamed its acronym's R specifically to stop implying causal/compositional
understanding, but reused "genuine" a dozen times across the sections readers see first.
**Fixed** (proportionate fix, not a global rewrite): added one clarifying sentence to
the Discussion's existing disclaimer, stating "genuine" means real-effect-vs-artifact,
not a reasoning/causal claim.

### MINOR (Methodology): floored log score is not exactly the Bregman-generated log score
`gain_matrix`'s log score floors probabilities at `ε=1e-6`; Corollary `cor:bregman`'s
identity is exact only for the unfloored `log q_y`. **Fixed**: added a clarifying
sentence immediately after the corollary.

## Queued (not yet acted on — prioritized for the next pass)

### P0 — worth doing before resubmission
| # | Action | Source | Cost |
|---|---|---|---|
| 0.1 | Benchmark this paper's own CIFAR-100-LT CE/CB/DRW accuracies (36.62/26.27/38.74) against Cui et al. 2019 / Cao et al. 2019's published numbers for the same ratio; the CB collapse here is unusually severe and never checked against the literature it reimplements | Perspective W1 | cheap — literature lookup + one sentence or table |
| 0.2 | Cross-check the alignment channel against zero-shot recall on the MOTIFS-TDE audit (both diagnose the same frequency-exploitation worry; data is likely already cached) | Perspective W6 | cheap if `results/sgg_audit_motifs.json` has the needed arrays |
| 0.3 | Address the "benchmarks should archive per-example probabilities" recommendation's real adoption barriers (storage scaling, leaderboard-integrity/anti-overfitting practice, IP/model-stealing) rather than framing the gap as pure oversight | Perspective W2 | writing |
| 0.4 | Add a runtime warning (or at least a prominent docstring note) in `wager/antisymmetric.py::decompose_gain` that calibration-matching may be required before the interval is meaningful, since the CIFAR/SGG studies show this is load-bearing but the shipped API has no signal of it | Devil's Advocate M4 | small code change |

### P1 — presentation, for JSPI specifically
| # | Action | Source | Cost |
|---|---|---|---|
| 1.1 | The paper is CV/ML-proportioned (half of Section 4 plus most of the implementation appendix is benchmark engineering detail — VG150 reconstruction, CLIP QuickGELU pitfall, crop-dedup counts, GPU wall-clock). Move implementation minutiae to a supplement; lead with the statistical apparatus | Journal-Fit W2 | writing, moderate |
| 1.2 | 48 pages, nine enumerated contributions is unusual for JSPI (typically 20-30 pages, 2-4 headline results stated discursively). Consider consolidating the contribution list to 3-4 items and whether the third domain belongs at full weight in this submission or as a shorter confirmatory note | Journal-Fit W3 | writing, moderate-large |
| 1.3 | Abstract (~330 words, one paragraph naming every result) reads as a table of contents; trim to the central claim + one headline finding | Journal-Fit W5 | writing |
| 1.4 | Keyword list includes "Pattern recognition" (CV-flavored); swap for JSPI-native terms ("sensitivity analysis," "comparative forecast evaluation") | Journal-Fit minor | trivial |
| 1.5 | Distinguish "same DM/GW statistic form, different (cross-sectional vs. serial) dependence corrected for" from "identical inferential target" in Corollary `cor:dm`'s prose, to avoid over-reading the equivalence | Domain minor | one sentence |
| 1.6 | State once, at first use of "confounder" in the sensitivity section (3.5), that this is an omitted-stratifier setting with no exposure/potential-outcomes structure, distinct from the causal-effect setting of the cited sensitivity-analysis literature — already stated in Related Work but not repeated at point of use | Domain minor | one sentence |

### P2 — deeper, lower urgency
| # | Action | Source | Cost |
|---|---|---|---|
| 2.1 | Add a genuine "many small clusters" consistency argument for `Theorem thm:clt`'s variance estimator (the DeLong-style construction the paper now cites is the right template) as a follow-up to the idealization caveat added in this pass, if a fully general proof is wanted rather than the current honest idealization + simulation-backed defense | Methodology M1 (residual) | real technical work |
| 2.2 | Stress-test the CB "genuine alignment loss" finding against an untuned-hyperparameter alternative explanation (a re-tuned or lower-LR CB run) | Devil's Advocate obs. 9 | GPU retraining |
| 2.3 | The sensitivity-bound worked example (Table `tab:sensitivity-numeric`) uses `Z`=object class, which is not actually unrecorded (it's half of the default `φ`); find or construct a demonstration against a genuinely unrecorded confounder | Devil's Advocate M7 | new experiment |
| 2.4 | Add a sentence on family-wise error across the paper's many reported randomization tests and sensitivity rows, even though CIs are defended as primary | Methodology minor | one sentence |
| 2.5 | Consider a formal random-effects interval across CIFAR seeds rather than a bare min-max spread | Methodology minor | writing/small analysis |

## What the panel confirmed is solid (do not re-litigate)

- Theorem 1 (transport/covariance identity), Theorem 2 (Bregman generalization, including
  the log-score reduction to `log q_y`), Proposition (coarsening), Proposition
  (attenuation), Proposition (sensitivity bound, corrected form) and its worst-case
  Corollary, and Corollary (DM/GW) are all independently re-derived and correct
  (Methodology).
- The runtime-enforced identity check in `decompose_gain` (raises on failure) and the
  83-check `verify_manuscript_numbers.py` cross-check are unusually strong reproducibility
  practices (Methodology, Devil's Advocate).
- The Visual Genome PredCls protocol, the MOTIFS/MOTIFS-TDE checkpoint audit, and the
  CIFAR-100-LT CE/CB/DRW construction are all faithful to how those communities actually
  work (Perspective).
- The matched-training-size CLIP-vs-geometry design and the calibration-matching protocol
  itself are genuinely good methodological moves, unusually careful for either a CV or a
  stats paper (Perspective, Devil's Advocate).
- The paper's multi-cycle self-correction discipline (removing the betting/e-value
  framework, the Reasoning→Resolution rename, catching its own Cauchy–Schwarz error) is
  real and documented, not merely claimed (Devil's Advocate).
