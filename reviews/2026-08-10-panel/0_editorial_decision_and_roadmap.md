# Editorial Decision & Revision Roadmap — WAGER manuscript

> Synthesis of the 5-reviewer simulated panel run 2026-08-10 after the CVIU desk rejection.
> Individual reports: `1_eic_editorial_assessment.md`, `2_methodology_review.md`, `3_domain_review.md`, `4_perspective_review.md`, `5_devils_advocate.md`.
> Every point below traces to a specific reviewer report (tags: EIC, R1 = methodology, R2 = domain, R3 = perspective, DA = devil's advocate).

## Decision: MAJOR REVISION

The Devil's Advocate raised one CRITICAL issue (DA-1), so the decision cannot be Accept. It is not Reject because two independent verifications (R1's line-by-line proof audit; DA's number-by-number results audit) found the theory correct, the code faithful, and **no cherry-picking — every printed number matches the committed results files**. The paper's defects live in the empirical base, the interpretive prose, and the presentation — all fixable in one intensive revision cycle.

### Reviewer positions

| Reviewer | Recommendation | Core verdict |
|---|---|---|
| EIC | (would have desk-rejected) | Statistics paper in a CV costume; no real CV system audited; visible surface defects |
| R1 Methodology | Minor revision | Theory correct and verified; inference needs coverage validation and scoping |
| R2 Domain | Major revision | Real contribution, but CV literature errors and toy-only experiments |
| R3 Perspective | Major revision | Sound instrument; illustrations, not consequences; interpretation risks open |
| DA | 1 CRITICAL, 6 MAJOR, 5 MINOR | Math holds, numbers honest; headline interpretation not identified without a recalibration control |

### Arbitration of the one real disagreement

R1 (minor) vs. everyone else (major/reject): R1 scoped itself to correctness, which survives. The panel's blocking concerns are outside R1's scope — identification of the headline interpretation (DA-1), the absence of any third-party system (EIC-1/R2-W1/R3-W1/DA-3), and venue idiom (EIC-2). Major revision stands.

---

## Consensus issues (raised independently by ≥2 reviewers)

1. **No model the authors didn't build is ever audited** — EIC trigger 1, R2 W1, R3 W1, DA 3. Unanimous top issue.
2. **⚠️ CRITICAL (DA-1, reinforced by R1's discriminant-validity gap and DA-7):** ΔR is not invariant to monotone recalibration; the CB "cancelling channels" headline is an uninterpretable mixture of confidence scaling and lost discrimination until a temperature-scaling control exists. The §5.1 validation tests only oracle signal + null, never a calibration-only or hidden-shortcut alternative. (DA notes the CLIP result plausibly *survives* this attack — softer models are penalized by the covariance term yet CLIP still wins.)
3. **Rejected-precursor leakage** (3 places) + "five contributions"/six items — EIC 3–4, DA 8/12.
4. **p = .002 resolution floor reported as data in every table** — EIC 7, R1 W5, R3 W9, DA 9.
5. **Single training seed per model, method-level conclusions** — R1 W4, R2 W6, DA 4.
6. **CIFAR CB arm suspect** (accuracy ~10 pts below published; underfitting alternative unexcluded) — R2 W6, DA alt-explanations.
7. **Abstract: overloaded with 5-decimal numbers; φ-relative point estimates stated unqualified; "aggregate scores cannot [distinguish]" is factually false as written** — EIC 5, DA 2/6, R3.
8. **Prior-channel semantics flip between domains** (training-frequency shortcut in the intro vs. test-histogram transport in CIFAR, where ΔP *undoes* the training prior) — DA 5, R3 W4 (ΔP framed as illegitimate).
9. **VQA promised by abstract/intro, never tested** — R2 W5, R3 W8.
10. **No bridge from ΔR to metrics CV readers use (R@K/mR@K)** — EIC 2/7, R2 W7.
11. **Missing literature** — CV canon: Xu 2017 (VG150/PredCls, mandatory), Lu 2016, GQA-OOD, Menon 2021, Kang 2020, zR@K discussion, SGG-debias families, VQA-CP debias methods (R2 W2–W4); cross-field: Diebold–Mariano/Giacomini–White, label shift (Saerens/BBSE), multicalibration (R3 W6).
12. **"Reasoning" in the name over-claims; disclaimers don't travel with acronyms** — R3 W3, DA 12, EIC first-impression.

## What the panel confirmed is SOLID (do not re-litigate)

- Theorems 1–2, Props 1–2 correct; O(NK) identity verified against code (R1, DA).
- All manuscript numbers match `results/*.json` exactly; no selective reporting (DA).
- The matched-subsample CLIP design is right, and the CLIP sign-reversal is the paper's genuinely novel result — "invisible to stratified means" (DA "So what" verdict, R2 S3, EIC strength 2).
- Reproducibility, honesty about lineage (§2.5), and limitations discipline are exceptional (all five).

---

## Revision Roadmap (prioritized)

### P0 — Identification & integrity blockers (cheap, do first)
| # | Action | Source | Cost |
|---|---|---|---|
| 0.1 | **Recalibration control**: run `decompose_gain` on temperature-scaled-CE vs CE from cached `data/cifar_lt` arrays; add a calibration-only arm and an unrecorded-shortcut arm to the §5.1 simulation; report a within-cell-recalibrated ΔR variant or reframe the CB narrative as calibration-confounded | DA-1, DA-7, R1-sim | CPU-only, minutes–hours |
| 0.2 | Fix the false abstract claim ("aggregate scores cannot distinguish" → composition claim only) | DA-2 | writing |
| 0.3 | Resolve the prior-channel semantics flip: state ΔP = test-histogram transport once, rewrite intro shortcut framing and CIFAR "prior-recoverable" prose to match; add the ΔP-legitimacy paragraph (prior gain is genuine under stationary deployment prior) | DA-5, R3-W4 | writing |
| 0.4 | Purge all three rejected-precursor mentions; fix "five contributions"/six | EIC-3/4, DA-8/12 | writing |

### P1 — The experiments that make it a CV paper
| # | Action | Source | Cost |
|---|---|---|---|
| 1.1 | **Audit released SGG checkpoints** (Scene-Graph-Benchmark: MOTIFS, VCTree, Transformer, ± TDE; PredCls softmax outputs are exactly the four arrays WAGER needs); make "what the SGG literature's gains consist of" the headline result, ΔR next to R@50/mR@50 | EIC-1, R2-W1, R3-W1, DA-3 | GPU inference (Colab quota constraint) |
| 1.2 | **Downstream-consequence experiment** on cached CLIP triple: post-hoc prior recalibration of MLP-VISUAL-S (or prior-shift evaluation) showing ΔP evaporates / is manufacturable while ΔR survives — converts the diagnostic into a prediction, closes both misuse modes | R3-W2 (R3's single highest-value item) | CPU-only, cached arrays |
| 1.3 | CIFAR strengthening: 3–5 seeds; IR 10/50/100; add logit-adjustment or cRT/τ-norm arm (pure-ΔP falsification case); reproduce or explain CB accuracy vs Cui et al. before keeping the cancellation narrative | R2-W6, R1-W4, DA-4 | GPU training (small: ResNet-32) |
| 1.4 | VQA: either one VQA-CP v2 decomposition (UpDn vs RUBi/LMH, φ = question type) or remove VQA from abstract/intro framing | R2-W5, R3-W8 | GPU or writing |

### P2 — Statistical completeness (R1's list)
2.1 CI coverage simulation with image-cluster dependence + VG-like cell skew (`experiments/antisymmetric_simulation.py`). 2.2 Appendix derivation of the influence function + explicit identified-subpopulation estimand. 2.3 Thm 2: "exchangeable" → i.i.d.-within-cell (or two-distinct-draw estimand). 2.4 B = 9,999 or "p ≤ .002" + one multiplicity sentence; footnote the degenerate [0,0] CI. 2.5 Fix coarsening prose (3method.tex ll.90–96). 2.6 Paper/code doc fixes: FREQ smoothing+backoff, MLP-SPATIAL+ epochs, Appendix D hyperparameters, commit the covariance cross-check script, data-availability statement for the .npz artifacts. 2.7 CLIP-head hyperparameter sensitivity grid + VG/CLIP-pretraining-overlap caveat.

### P3 — Literature & positioning
3.1 R2's citation repairs (Xu 2017, Lu 2016, GQA-OOD, Menon 2021, Kang 2020, Cui/Cao cited where named, SGG-debias families; displace preprints with published canon). 3.2 Reword the strawman: "no exact pairwise decomposition with inference," + paragraph distinguishing WAGER from zR@K / head-body-tail mR@K / GQA-OOD (ideally an empirical zR@K-vs-ΔR comparison on the same pair). 3.3 R3's bridge paragraphs: Diebold–Mariano/Giacomini–White, label shift, multicalibration; sentence on the sequential-leaderboard open problem. 3.4 φ-multiplicity mechanism (maintainer-declared φ; report all pre-declared candidates); scope statement (closed-set, probabilities, discrete φ) early in §1. 3.5 "WAGER card" reporting template. 3.6 Naming: re-expand the R (e.g., "Residual gain") or boxed disclaimer at first use — **user decision**.

### P4 — Presentation for a CV venue
4.1 Rewrite abstract: ≤2 headline findings, plain language, φ-qualification, few decimals. 4.2 Rebuild Fig. 1 around the real (man, surfboard) riding/carrying pair with transport drawn on crops; restyle the matplotlib figures. 4.3 Re-key keywords ("benchmark auditing," "model comparison"). 4.4 Demote Props 1–2 + inference detail toward appendix; lead sections with vision findings. 4.5 Bridge paragraph translating ΔR magnitudes into familiar metric terms. 4.6 Reframe cover letter as "an audit of what current SGG systems' reported gains consist of" (honest only after 1.1).

---

## Open decision for the author (blocks P1 scheduling)

**Venue.** Two coherent paths, per the EIC report:
- **A — CVIU-class CV venue:** requires P1.1 (real SGG checkpoints) + P4; the paper becomes "an audit of the SGG literature with a new exact tool."
- **B — TMLR / JMLR / NeurIPS Datasets & Benchmarks:** the statistical idiom is native and toy-model estimator validation is acceptable; P0 + P2 + P3 would suffice, P1.1 still strongly advisable.

Note: P1.1 and P1.3 need GPU time; the Colab T4 quota was exhausted as of 2026-08-03 and the user previously chose to wait rather than run locally on MPS.
