# DA-1 CRITICAL control — executed 2026-08-10

Ran the temperature-scaling control the Devil's Advocate demanded, using the paper's own estimator
(`wager.antisymmetric.decompose_gain`, Brier score, φ = superclass) on the committed
`data/cifar_lt/cifar_lt_results.npz` arrays. Script: scratchpad `review/temperature_control.py`
(worth committing as `experiments/` once adapted).

## Result: the confound is REAL — and the fixed analysis makes the paper STRONGER

```
Reference rows (match the paper):
CB   vs CE            dT=+0.00143  dP=+0.19713  dR=-0.19569
DRW  vs CE            dT=+0.06606  dP=+0.04206  dR=+0.02400

Calibration-only controls (temperature-scaled CE vs CE — identical instance information):
CE(T=1.50) vs CE      dT=+0.10053  dP=+0.13687  dR=-0.03634
CE(T=2.85*) vs CE     dT=+0.20515  dP=+0.37992  dR=-0.17477     (*NLL-optimal T)
CE(T=3.00) vs CE      dT=+0.20571  dP=+0.39645  dR=-0.19074
CE(T=0.67) vs CE      dT=-0.08464  dP=-0.10079  dR=+0.01616     (sharpening)

Against a calibration-matched baseline:
CB  vs CE(T=2.85)     dT=-0.20371  dP=-0.18279  dR=-0.02092
DRW vs CE(T=2.85)     dT=-0.13908  dP=-0.33785  dR=+0.19877
```

Mean max-prob: CE 0.764, CB 0.553, DRW 0.736. CE's NLL-optimal temperature is T*=2.85
(NLL 4.11 → 2.50) — the baseline is indeed badly overconfident, as the paper says.

## UPDATE — proper held-out protocol (supersedes the interpretation below)

`experiments/cifar_recalibration_control.py` (committed): 20 random cal/audit splits of the test
set, T chosen per-model by NLL on the calibration half only, decomposition on the audit half.
T*(CE)=2.85±0.02, T*(CB)=3.51±0.04, T*(DRW)=2.61±0.02 — all three models are overconfident.
Results in `results/cifar_recalibration.json` (mean over splits, sd in parens):

```
CB  vs CE (raw)        dT=+0.00208  dP=+0.19635  dR=-0.19427   (the paper's row)
CB  vs CE (cal-both)   dT=-0.12912  dP=+0.11079  dR=-0.23991
DRW vs CE (raw)        dT=+0.06712  dP=+0.04258  dR=+0.02454   (the paper's row)
DRW vs CE (cal-both)   dT=+0.02173  dP=+0.00216  dR=+0.01957
CE(cal) vs CE          dT=+0.20495  dP=+0.37960  dR=-0.17464   (confound size: pure temperature)
```

**Corrected story for the manuscript** (cal-both is the right primary regime; the cal-old numbers
below are the asymmetric regime and overstate DRW):
1. Pure recalibration moves the channels by ±0.17–0.38 with zero new instance information — the
   raw CB "cancelling channels" narrative is confounded, as DA-1 claimed.
2. Calibration-matched, **CB genuinely loses discrimination** (dR=−0.240): the honest CB story is
   "real alignment loss plus residual prior fit," consistent with its 10-point accuracy drop —
   NOT "traded discrimination for prior fit" and NOT merely softening.
3. Calibration-matched, **DRW's gain is almost entirely instance alignment** (dP≈0.002,
   dR=+0.020): the submitted "two-thirds prior-recoverable" claim about DRW was itself a
   calibration artifact — the genuine improvement is the alignment channel. This *strengthens*
   the paper's headline.
4. Protocol for the revision: report raw + cal-both rows side by side; the calibration-only row
   quantifies the confound; the (n_c−1)/n_c and coarsening theory is untouched.

## VG consequence experiment (R3-W2), executed 2026-08-10

`experiments/vg_prior_consequence.py` → `results/vg_prior_consequence.json`. Within-cell
prior-matching (label-shift style, training-count prior, no labels used) + held-out calibration
control on the cached matched-subsample trio:

```
VISUAL' vs VISUAL  (the correction itself)   dT=+0.02512  dP=+0.02401  dR=+0.00111  <- almost pure dP: falsification test passes
VISUAL  vs SPATIAL (paper row)               dT=-0.04655  dP=-0.05296  dR=+0.00641
VISUAL' vs SPATIAL                           dT=-0.02143  dP=-0.02895  dR=+0.00752
VISUAL' vs SPATIAL' (both corrected)         dT=-0.03326  dP=-0.03988  dR=+0.00663
VISUAL vs SPATIAL cal-both (audit half)      dT=-0.04260  dP=-0.04727  dR=+0.00467  CI=[+0.00314,+0.00621]
```

Takeaways for the manuscript: (a) prior correction is demonstrably ~pure-ΔP (small +0.0011 leak,
note honestly); (b) ΔR is stable under prior correction and survives calibration matching — the
CLIP alignment result is neither a prior nor a calibration artifact (T*(VISUAL)=1.18,
T*(SPATIAL)=1.00 — these heads are nearly calibrated, unlike the CIFAR models); (c) prior matching
halves but does NOT flip the visual model's aggregate deficit — do not claim "corrected pixels win";
claim "deficit is prior/confidence-shaped, advantage is alignment-shaped and robust."

## Logit-adjustment arm (P1.3, seed 0, 2026-08-11) — R2's prediction FALSIFIED, instructively

`experiments/run_cifar_multiseed_wager.py`: LA(CE) = q_CE(y|x)/π_train(y), renormalized.
R2 predicted "post-hoc rebalancing should register as almost pure ΔP." It does NOT:

```
LA vs CE raw   dT=+0.09745  dP=+0.06000  dR=+0.03744    acc: CE .3662 → LA .3959 (beats DRW .3874)
LA vs CE cal   dT=+0.03144  dP=-0.00305  dR=+0.03449    (calibration-matched: gain ≈ all alignment)
```

Mechanism: at φ=superclass, dividing by the GLOBAL prior has a within-cell component
(fine classes inside a superclass differ in frequency), and that correction is
multiplicative in the example's own probabilities — it boosts rare classes most where
the model already had latent evidence, i.e., genuinely instance-coupled; consistent with
logit adjustment being Bayes-optimal for balanced error, not a mere histogram fix.
Contrast: the VG within-cell prior-MATCHING correction (targets the cell histogram
directly) registered ~pure ΔP. Manuscript framing: transport separates cell-level
histogram corrections (→ΔP) from instance-coupled corrections (→ΔR) — the pair of
post-hoc arms demonstrates both directions. Do NOT write the paper claiming LA "should"
be pure prior; write that WAGER reveals it isn't, at this φ, and why.

## Original quick-check interpretation (test-set-oracle T, asymmetric cal-old regime)

1. **DA-1 confirmed.** Pure temperature-softening of CE — zero new instance information —
   reproduces the CB signature almost exactly (dR −0.191 at T=3 vs CB's −0.196). Sharpening
   manufactures positive dR (+0.016). As submitted, the CIFAR "cancelling channels" narrative
   ("what it paid for prior fit was per-instance discrimination") is unidentified.
2. **The repaired story is better, not weaker.**
   - **CB ≈ temperature-softening**: against calibration-matched CE, CB's alignment deficit
     collapses from −0.196 to −0.021. CB's "trade" was almost entirely a calibration move, with
     a small residual deficit (consistent with mild underfitting, per R2/DA).
   - **DRW's alignment gain is real and 8× larger than reported**: against the calibration-matched
     baseline, DRW shows dR = +0.199 (vs +0.024 raw). The raw decomposition *understated* the
     genuine finding because the overconfident baseline polluted both channels.
3. **Suggested protocol for the revision** (addresses DA-1 + DA-7 + R1-sim in one move): report the
   decomposition against a *temperature-recalibrated* old model as the primary row (choosing T on a
   held-out split, not the test set — the T* here is test-set-oracle and must not be copied into the
   paper as-is), keep the raw row as a diagnostic, and add the calibration-only arm to the §5.1
   simulation. Optionally define the recalibration-invariant variant ΔR̃ = ΔR(f1, cal(f0)).
4. **The CLIP result survives** (as DA predicted): softer models are *penalized* on dR, and
   MLP-VISUAL-S wins alignment anyway; if anything a calibration control there would firm it up too
   (worth running on the cached VG arrays as well).
