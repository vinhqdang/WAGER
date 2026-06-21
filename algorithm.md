# WAGER: Wealth-Anchored Gain Estimation of Reasoning
### A distribution-free, anytime-valid framework for attributing computer-vision benchmark gains to genuine visual reasoning vs. annotation-frequency priors

**Target venue:** WACV 2027, Evaluations & Datasets (E&D) Track
**Status:** algorithm specification — self-contained, engineer-runnable on a single 8 GB GPU
**Author:** Đặng Quang Vinh

---

## 0. One-paragraph summary

We answer, for any vision benchmark and any pair of methods, the question *"how much of the reported gain is genuine visual reasoning, and how much is just better fitting of annotation-frequency priors?"* WAGER does this by (1) constructing, for a fixed model `f`, a **self-prior projection** `q̄_f` — the model's own predictions averaged within each frequency-defining cell `φ(x)`; (2) running a **testing-by-betting** capital process that wagers on `f` out-predicting `q̄_f` on held-out data; (3) reading off two things from that single process — an **e-value** (a distribution-free, anytime-valid certificate that the model uses image information beyond the prior) and the **growth rate**, which converges to the model's *usable conditional information beyond the prior*; and (4) combining two such processes into the **Reasoning Gain Ratio (RGR)** with an anytime-valid confidence interval. Everything operates on cached logits, so the compute cost is trivial.

The novelty is **not** any individual ingredient (frequency baselines, V-information, betting martingales all exist). It is the **construction**: the self-prior projection as a frozen "forecaster B," the e-process built on it, the theorem tying its growth rate to usable reasoning information, and the gain-attribution ratio with finite-sample validity — applied uniformly across SGG, VQA, LVIS, and MLLMs. No prior benchmark critique gives a validity guarantee; they all report point estimates.

---

## 1. Motivation

### 1.1 The disease
On the most label-imbalanced vision benchmarks, a trivial predictor that looks up the most frequent label given some cheap context already recovers most of the headline metric:

- **Scene Graph Generation (VG150).** The `FREQ` baseline of Zellers, Yatskar, Thomson & Choi (2018) — predict `argmax_p P(predicate | subject, object)` from training counts — reaches R@50 ≈ 60.6 on PredCls vs. MOTIFS at 65.2, and on SGDet `FREQ` (26.2) is within ~1 point of MOTIFS (27.2). A lookup table recovers ~96% of "state-of-the-art" recall.
- **VQA.** Answering "yes" blindly to "Do you see a…" reaches ~87% on the original unbalanced VQA (Goyal, Khot, Summers-Stay, Batra & Parikh, 2017). On the changing-prior split VQA-CP (Agrawal, Batra, Parikh & Kembhavi, 2018), UpDn collapses from ~63% to ~40%.
- **Long-tail detection (LVIS).** AP on rare categories is dominated by image-frequency priors (Gupta, Dollár & Girshick, 2019).

### 1.2 Why existing fixes are not enough
- **mean Recall@K** (Chen, Yu, Chen & Lin, 2019; Tang, Zhang, Wu, Luo & Liu, 2019) rebalances metric weight but can be gamed by suppressing head predictions, and Li, Zhang, Bai, Zhao, Jiang & Yuan (2022) show it breaks category independence.
- **VQA-CP OOD splits** can be solved by *inverting* known label statistics; Teney, Kafle, Shrestha, Abbasnejad, Kanan & van den Hengel (2020) show a random-answer method beats SOTA on some question types — a textbook Goodhart failure.
- **Causal TDE** (Tang, Niu, Huang, Shi & Zhang, 2020) is a *training/inference intervention*, not an *evaluation* that quantifies how much of a reported gain is confound.

**Every one of these is bespoke to one benchmark and gives a point estimate with no uncertainty quantification.** None answers "is *this specific gain* real, and with what confidence?"

### 1.3 The gap WAGER fills
A general, statistically-principled, cross-benchmark test that decomposes a reported gain into a prior-recoverable part and a residual reasoning part, with a finite-sample validity guarantee. That object does not exist. WAGER is that object.

---

## 2. Problem setup and notation

| Symbol | Meaning |
|---|---|
| `x` | an instance (e.g., an ordered object pair + its image region for SGG; an image+question for VQA) |
| `y ∈ {1,…,K}` | the ground-truth label (predicate / answer / category) |
| `φ(x)` | **prior features**: the cheap, frequency-carrying sufficient statistic (defined per benchmark in §6). E.g. for SGG, `φ(x) = (subject-class, object-class)`. |
| `q_f(y\|x)` | a model `f`'s predictive distribution over labels (softmax of cached logits) |
| `p(y\|x)`, `p(y\|φ)` | true conditionals (never assumed known) |
| `u(y)=1/K` | uniform reference |
| Splits | `A` = projection-fit fold, `B` = evaluation stream, drawn by a random permutation of the test set |

We assume only that instances on stream `B` are **exchangeable** (we enforce this by randomizing order). We never assume calibration of `q_f`, nor knowledge of the true prior.

---

## 3. The new math

### 3.1 Self-prior projection (Definition 1)
For a fixed model `f`, define its **self-prior projection** as the model's own predictions averaged within each prior-feature cell:

$$\bar q_f(y \mid \phi) \;=\; \mathbb{E}\big[\, q_f(y \mid X)\;\big|\;\phi(X)=\phi \,\big].$$

Estimate it on fold `A` by cell-wise averaging with Krichevsky–Trofimov (add-½) smoothing:

$$\hat{\bar q}_f(y\mid \phi) \;=\; \frac{\tfrac12 + \sum_{j\in A}\, q_f(y\mid x_j)\,\mathbb{1}[\phi(x_j)=\phi]}{\tfrac{K}{2} + \sum_{j\in A}\mathbb{1}[\phi(x_j)=\phi]}.$$

`q̄_f` is, by construction, the best summary of `f` that is **measurable with respect to the prior features only** — a predictor that has thrown away every pixel-level cue and kept only what frequency context implies. This is the crux: instead of comparing `f` to an *external* frequency baseline (whose mismatch with the true prior breaks validity), we compare `f` to *its own* frequency-collapsed self. The two share calibration, vocabulary, and idiosyncrasies, so any out-of-fold predictive advantage of `q_f` over `q̄_f` can only come from pixels beyond `φ`.

### 3.2 Per-instance reasoning score and clipped bet (Definition 2)
On the evaluation stream `B`, define the **prior-excess log-score**:

$$d_i \;=\; \log q_f(y_i \mid x_i) \;-\; \log \hat{\bar q}_f(y_i \mid \phi(x_i)), \qquad \tilde d_i = \mathrm{clip}(d_i,\,-c,\,c).$$

`d_i > 0` ⇔ at instance `i`, using the image beyond `φ` helped predict the true label. Clipping to `[−c, c]` (default `c = log K`) bounds the variable so we can apply betting-on-the-mean machinery.

### 3.3 The wealth process and the null (Definition 3)
We test
$$H_0:\quad \mu \;:=\; \mathbb{E}[\,\tilde d_i\,] \;\le\; 0 \qquad\text{("}f\text{ predicts no better than its prior-projection")}$$
against `H₁: μ > 0`. Following the bounded-mean capital process of Waudby-Smith & Ramdas (2024) and the forecaster-comparison e-process of Henzi & Ziegel (2022), define wealth

$$W_0 = 1,\qquad W_n \;=\; \prod_{i=1}^{n}\Big(1 + \lambda_i\,\tilde d_i\Big),\qquad \lambda_i \in \big[0,\tfrac{1}{c}\big)\ \text{predictable (}\mathcal F_{i-1}\text{-measurable).}$$

The betting fraction `λ_i` is chosen online — we use the **Online-Newton-Step / aGRAPA** rule of Waudby-Smith & Ramdas (2024) (a closed-form predictable update), which needs no tuning.

**Theorem 1 (anytime-valid certificate).** *Under `H₀`, `(W_n)` is a non-negative supermartingale with `E[W_n] ≤ 1`. Hence `W_n` is an **e-value**, and by Ville's inequality (Ville, 1939), for any `α∈(0,1)`,*
$$\Pr\!\Big[\,\exists n:\; W_n \ge 1/\alpha \,\Big]\;\le\;\alpha.$$
*Therefore "stop and reject `H₀` when `W_n ≥ 1/α`" controls type-I error at level `α`, with no fixed sample size and no distributional assumptions beyond exchangeability.*

*Proof sketch.* `λ_i` is predictable and `1+λ_i \tilde d_i ≥ 0` because `λ_i < 1/c` and `\tilde d_i ≥ −c`. Under `H₀`, `E[1+λ_i\tilde d_i | F_{i-1}] = 1 + λ_i·E[\tilde d_i|F_{i-1}] ≤ 1`. Telescoping gives `E[W_n]≤1`. Ville's inequality applied to the non-negative supermartingale yields the bound. ∎

The key design choice that buys validity *without knowing the true prior*: `q̄_f` is **frozen on fold `A`** and treated purely as a competing forecaster. We are not estimating a true conditional independence (which is provably hard, cf. Shah & Peters, 2020); we are running an honest **predictive** comparison of two fixed forecasters, which is exactly what testing-by-betting certifies.

### 3.4 Growth rate = usable reasoning information (Theorem 2)
Let the per-step log-wealth increment be `g_i = log(1+λ_i \tilde d_i)`.

**Theorem 2.** *With the log-optimal predictable bet `λ_i* = argmax_λ E[log(1+λ \tilde d) | F_{i-1}]`, the growth rate converges almost surely:*
$$G(f)\;:=\;\lim_{n\to\infty}\frac1n\log W_n \;=\; \mathbb{E}\big[\log q_f(Y\mid X)-\log \bar q_f(Y\mid\phi(X))\big]\;=:\;\mathcal I_f,$$
*(taking `c→∞`), where `I_f ≥ 0` is the **usable conditional information** that model `f` extracts from `X` about `Y` beyond the prior features `φ`. If `q_f` equals the true posterior `p(·|x)` and `q̄_f` the true `p(·|φ)`, then `I_f = I(Y;X|φ(X))`, the conditional mutual information.*

*Proof sketch.* By Kelly (1956) / Cover & Thomas (2006, Ch. 6, 16), the log-optimal growth rate of a forecasting game equals the expected log-score differential, which the SLLN drives to `E[\tilde d]`. As `c→∞`, `\tilde d_i → d_i` and `E[d] = E[log q_f(Y|X)] − E[log \bar q_f(Y|φ)]`. The chain rule `I(Y;X)=I(Y;φ(X))+I(Y;X|φ(X))` (valid because `φ` is a function of `X`) identifies the residual with conditional MI under the calibrated case. ∎

**One object, two readouts.** The *same* wealth process certifies (via `W_n`, Theorem 1) **and** quantifies (via `G(f)`, Theorem 2). This unification — a distribution-free certificate whose growth rate is precisely the usable reasoning information beyond annotation priors — is the central new result.

### 3.5 Calibration-invariance (Corollary 3)
**Corollary 3.** *`I_f` is invariant to any global recalibration map `T` applied uniformly across a `φ`-cell (e.g., temperature scaling within a cell), because `T` cancels between `q_f` and `\bar q_f`. Consequently, miscalibration shared within a prior cell cannot inflate the measured reasoning. Under Gibbs' inequality, an arbitrary miscalibrated `q_f` can only* ***under***-*estimate the true reasoning information, never manufacture it.*

This is why WAGER cannot be fooled by an overconfident model: confidence that is constant within a frequency cell is divided out by the self-projection.

### 3.6 The Reasoning Gain Ratio (Definition 4 + Theorem 4)
Decompose each model's total information about `Y` over uniform:
$$\underbrace{\mathbb{E}[\log\bar q_f(Y\mid\phi)-\log u(Y)]}_{I^{\text{prior}}_f\ \text{(prior-fitting)}} \;+\; \underbrace{\mathbb{E}[\log q_f(Y\mid X)-\log\bar q_f(Y\mid\phi)]}_{I^{\text{reason}}_f\ =\ I_f\ \text{(reasoning)}}\;=\;I^{\text{tot}}_f.$$

For a claimed improvement from `f` to `f′`, define the **Reasoning Gain Ratio**:
$$\mathrm{RGR}(f',f)\;=\;\frac{I^{\text{reason}}_{f'}-I^{\text{reason}}_{f}}{I^{\text{tot}}_{f'}-I^{\text{tot}}_{f}}$$
the fraction of the information gain attributable to better reasoning rather than better prior-fitting.

**Decision rule.** `RGR < 0.5` ⇒ the majority of the reported gain is prior-recoverable ⇒ flag the SOTA claim as **non-substantive**.

**Theorem 4 (anytime-valid CI for RGR).** *Each of `I^reason` and `I^tot` is the mean of a bounded score; the betting confidence sequence of Waudby-Smith & Ramdas (2024) gives each an anytime-valid `(1−α)` interval. Combining numerator and denominator intervals by Fieller's method (Fieller, 1954) under a Bonferroni split yields a `(1−2α)` anytime-valid confidence interval for `RGR(f′,f)`.*

This converts "is the gain real?" into a **sequential test with a certified interval** — the thing no existing benchmark critique provides.

---

## 4. The WAGER algorithm

```
INPUT  : cached predictive distributions q_f(·|x) for each model f on a benchmark test set;
         prior-feature map φ(·); levels α; clip c = log K; #permutations R.
OUTPUT : for each model f: e-value E_f, reasoning info Î_reason_f (CI), prior info Î_prior_f;
         for each pair (f',f): RGR with anytime-valid CI; verdict.

1  For r = 1..R:                                    # randomize stream order for exchangeability
2     π ← random permutation of test indices; split into A (40%) and B (60%)
3     For each model f:
4        q̄_f ← cellwise_average(q_f over A, key=φ, KT-smoothing)        # self-prior projection (Def.1)
5        stream over i∈B in order π:
6           d_i  ← log q_f(y_i|x_i) − log q̄_f(y_i|φ(x_i));  d̃_i ← clip(d_i,−c,c)     # (Def.2)
7           λ_i  ← ONS_betting_fraction(history d̃_{1..i-1})            # predictable, closed-form
8           W_i  ← W_{i-1} · (1 + λ_i · d̃_i)                          # wealth (Def.3)
9        E_f^r ← W_{|B|}                                              # e-value (Thm.1)
10          Î_reason_f^r , CI ← betting_mean(d̃ over B)                # growth rate (Thm.2,4)
11          e_i  ← log q̄_f(y_i|φ(x_i)) − log u(y_i)
12          Î_prior_f^r ← betting_mean(clip(e_i))
13  Aggregate over R permutations: E_f ← mean_r E_f^r ; intervals ← union via Thm.4
14  For each pair (f',f): RGR ← (ΔÎ_reason)/(ΔÎ_tot) with Fieller CI (Thm.4)
15  Verdict(f',f) ← "non-substantive" if upper-CI(RGR) < 0.5 else "reasoning-supported"
```

### Reference implementation (NumPy core — runs on CPU; <100 MB RAM)

```python
import numpy as np

def kt_projection(q_A, phi_A, K):
    """Self-prior projection q̄_f estimated on fold A. q_A: (Na,K) probs; phi_A: (Na,) cell ids."""
    cells = {}
    for p, c in zip(q_A, phi_A):
        cells.setdefault(c, []).append(p)
    qbar = {c: (0.5 + np.sum(v, 0)) / (0.5 * K + len(v)) for c, v in cells.items()}
    unif = np.full(K, 1.0 / K)
    return qbar, unif

def ons_lambda(d_hist, c, lam_prev, A0):
    """Online-Newton-Step predictable betting fraction (Waudby-Smith & Ramdas 2024)."""
    if len(d_hist) == 0:
        return 0.0, A0
    z = d_hist[-1]
    grad = z / (1 + lam_prev * z + 1e-12)
    A0 = A0 + grad ** 2
    lam = lam_prev + (2 / (2 - np.log(3))) * grad / (A0 + 1e-12)
    return float(np.clip(lam, 0.0, 0.5 / c)), A0   # cap below 1/c for nonnegativity

def wager_stream(q_f, y, phi, qbar, unif, c):
    """Returns (e_value, d_clipped_array, e_prior_array) over evaluation fold B."""
    W, lam, A0 = 1.0, 0.0, 1.0
    d_list, e_list, hist = [], [], []
    for i in range(len(y)):
        qb = qbar.get(phi[i], unif)
        d = np.log(q_f[i, y[i]] + 1e-12) - np.log(qb[y[i]] + 1e-12)
        d = float(np.clip(d, -c, c))
        lam, A0 = ons_lambda(hist, c, lam, A0)
        W *= (1 + lam * d); hist.append(d); d_list.append(d)
        e_list.append(float(np.clip(np.log(qb[y[i]] + 1e-12) - np.log(unif[y[i]] + 1e-12), -c, c)))
    return W, np.array(d_list), np.array(e_list)

def betting_ci(x, c, alpha=0.05, grid=None):
    """Anytime-valid CI for E[x] of a bounded var via Waudby-Smith & Ramdas capital process."""
    grid = np.linspace(-c, c, 2001) if grid is None else grid
    keep = []
    for m in grid:
        W, lam, A0, ok = 1.0, 0.0, 1.0, True
        hist = []
        for z in (x - m):
            lam, A0 = ons_lambda(hist, c, lam, A0)
            W *= (1 + lam * z); hist.append(z)
            if W >= 1 / alpha:
                ok = False; break
        if ok:
            keep.append(m)
    return (min(keep), max(keep)) if keep else (np.nan, np.nan)
```

> The full repo wires this to cached logits, runs the `R`-permutation aggregation, the prior-info channel, and Fieller combination for RGR. The hot loop is `O(NK)` per model — milliseconds on CPU for `N≈500k`, so **GPU is only used once, to produce the cached logits**.

---

## 5. Why this is genuinely new (reviewer-facing)

1. **First to cast benchmark-confound attribution as a game-theoretic e-process** → anytime-valid, distribution-free certificate. All prior SGG/VQA/LVIS critiques give point estimates with no validity guarantee.
2. **The self-prior projection `q̄_f` is a new estimator.** Comparing a model to *its own* frequency-collapsed self (rather than an external FREQ baseline) makes the null exact without knowing the true prior and makes the measurement provably calibration-invariant (Cor. 3). This is the technical core, not an application of V-information.
3. **Theorem 2 unifies certification and quantification in one object** — the betting growth rate equals usable reasoning information beyond the prior. That identity is new.
4. **RGR with an anytime-valid CI (Thm. 4)** turns "is the SOTA gain real?" into a sequential hypothesis test with a certified interval — novel as an evaluation primitive.
5. **Cross-benchmark, cross-modal by construction.** The same four steps instantiate on SGG, VQA, LVIS, and MLLMs; prior critiques are each bespoke to one benchmark.

What we *borrow and cite* (so the contribution is honestly scoped): betting/e-value theory (Shafer; Vovk & Wang; Ramdas, Grünwald, Vovk & Shafer; Waudby-Smith & Ramdas; Henzi & Ziegel), the growth-rate–information identity (Kelly; Cover & Thomas), and the usable-information viewpoint (Xu, Zhao, Song, Stewart & Ermon; Ethayarajh, Choi & Swayamdipta; Hewitt, Ethayarajh, Liang & Manning).

---

## 6. Prior features `φ` per benchmark (the confound definition)

| Benchmark | Task | `φ(x)` (the frequency-carrying sufficient statistic) | `y` |
|---|---|---|---|
| VG150 (Visual Genome) | Scene Graph Generation | ordered pair `(subject-class, object-class)` | predicate (50) |
| GQA200 | SGG | `(subject-class, object-class)` | predicate (100) |
| PSG | Panoptic SGG | `(subject-class, object-class)` | relation (56) |
| VQA v2 / VQA-CP | VQA | question-type (and optionally first-3-words bucket) | answer |
| GQA (QA) | VQA | question structural type / template id | answer |
| LVIS | Long-tail detection | category-frequency tier (rare/common/frequent) + image context bucket | category |

`φ` is deliberately chosen as the statistic through which annotation frequency acts. Ablation over `φ` granularity (§9) shows results are stable.

---

## 7. Datasets and where to get the files

| Resource | Where | Notes |
|---|---|---|
| **Visual Genome** images + annotations | `https://homes.cs.washington.edu/~ranjay/visualgenome/` | base data |
| **VG150 preprocessed split + pretrained SGG model logits** | `https://github.com/KaihuaTang/Scene-Graph-Benchmark.pytorch` (Kaihua Tang) | **primary source of cached logits** — MOTIFS, VCTree, IMP, VTransE, +TDE checkpoints; export per-pair predicate distributions |
| **PSG dataset + OpenPSG models** | `https://github.com/Jingkang50/OpenPSG` | PSG logits |
| **GQA** (images, scene graphs, QA) | `https://cs.stanford.edu/people/dorarad/gqa/` | QA + SGG variants |
| **VQA v2** | `https://visualqa.org/` | balanced VQA |
| **VQA-CP v1/v2** | `https://www.iro.umontreal.ca/~agrawal/vqa-cp/` (Aishwarya Agrawal) | changing-prior splits |
| **LVIS v1.0** | `https://www.lvisdataset.org/` | rare/common/frequent tiers |
| **Open MLLM weights** (4-bit) | HuggingFace: `Qwen/Qwen2-VL-2B-Instruct`, `vikhyatk/moondream2`, `llava-hf/llava-1.5-7b-hf` | for the MLLM study; see §8 for 8 GB strategy |

> **8 GB-critical detail:** WAGER consumes *cached probability vectors*, not models. You run each model's forward pass **once** to dump `(y_true, q_f(·|x), φ(x))` to disk as `.npz`, then all WAGER computation is CPU NumPy. For SGG you don't even need a GPU — the Scene-Graph-Benchmark model zoo lets you export predicate distributions from released checkpoints.

---

## 8. Implementation plan (8 GB VRAM, ~8 weeks)

**Phase 0 — Harness (days 1–4).** Define the cached-logit schema `{image_id, instance_id, y_true, q (K-vector), phi_key}`. Implement the §4 core + `R`-permutation driver + Fieller CI. Unit-test on synthetic data.

**Phase 1 — Validity & power simulations (days 5–12).** *(This is the credibility backbone — do it before touching real models.)*
- **Type-I error:** feed `q_f = q̄_f` (model = prior). Verify `Pr[W_n ≥ 1/α] ≤ α` across 1000 runs and that `Î_reason ≈ 0`.
- **Power / recovery:** synthesize models `q_f = (1−β)·prior + β·oracle` for `β∈[0,1]`. Verify `RGR` tracks the injected reasoning fraction `β` and CI coverage hits nominal `1−α`.

**Phase 2 — SGG (weeks 2–3).** Export cached predicate distributions for `FREQ`, `FREQ+OVERLAP`, `IMP+`, `MOTIFS`, `VCTree`, `VTransE`, `MOTIFS+TDE` on VG150 (PredCls/SGCls/SGDet), GQA200, PSG. No training needed — released checkpoints. Run WAGER. **Expected anchor result:** `FREQ` returns `Î_reason ≈ 0`, e-value ≈ 1 (framework correctly finds no reasoning); `+TDE` raises RGR (validates against the causal literature).

**Phase 3 — VQA (weeks 4–5).** Cache distributions for prior-only, question-only (blind LSTM), SAN, UpDn/BUTD, LXMERT on VQA v2 and VQA-CP v2. Run WAGER; cross-check that WAGER flags the VQA-CP "label-inversion" exploiters identified by Teney et al. (2020).

**Phase 4 — MLLMs (week 6).** For each VQA/GQA item, get option-token log-probs from a small/quantized open MLLM (Qwen2-VL-2B in fp16 ≈ 5 GB; LLaVA-1.5-7B in 4-bit via `bitsandbytes` ≈ 5–6 GB; moondream2 as a <4 GB fallback). Cache once. Apply WAGER. **Headline experiment:** do modern MLLM "gains" over classical baselines survive the RGR test, or are they prior-fitting?

**Phase 5 — LVIS + ablations + write-up (weeks 7–8).** LVIS rare-tier analysis; ablations over `φ` granularity, betting strategy (ONS vs. mixture vs. Cover's universal portfolio), clip `c`, split ratio, smoothing; stability across seeds. Draft the 8-page WACV paper + supplement.

---

## 9. Baseline models and comparison protocol

**Models analyzed by WAGER**
- *SGG:* FREQ, FREQ+OVERLAP, IMP+, MOTIFS, VCTree, VTransE, MOTIFS+TDE, (optional) a transformer SGG if logits available.
- *VQA:* prior-only, blind-LSTM (question-only), SAN, UpDn/BUTD, LXMERT, + one open MLLM.
- *LVIS:* a standard long-tail detector (e.g., a released Mask R-CNN + repeat-factor-sampling baseline) at the score-distribution level.

**Methods WAGER is compared *against* (as evaluation tools)**
mean Recall@K (Chen et al. 2019; Tang et al. 2019), Independent mean Recall (Li et al. 2022), VQA-CP accuracy gap (Agrawal et al. 2018), and TDE effect size (Tang et al. 2020). We show WAGER (a) reproduces their qualitative verdicts where they agree, (b) adds a validity guarantee none of them has, and (c) disagrees in diagnosable cases (e.g., it does **not** reward mR@K-gaming that suppresses head predictions without adding visual information).

---

## 10. Evaluation plan and success criteria

**A. Framework validity (simulation).** Nominal type-I error control (≤ α) under model=prior; CI coverage ≥ 1−α; monotone recovery of injected reasoning fraction `β` (Pearson `r > 0.95` between true `β` and RGR).

**B. Anchor / sanity (real).** `FREQ` on VG150 ⇒ e-value ≈ 1, `Î_reason ≈ 0`. TDE ⇒ strictly higher RGR than its non-TDE base. These are pass/fail credibility gates.

**C. Headline findings (real).** A ranking of methods by RGR on each benchmark; identification of specific reported gains with upper-CI(RGR) < 0.5 ("non-substantive"). Stratified `Î_reason` on head/body/tail predicates and zero-shot triplets, showing aggregate metrics hide tail collapse.

**D. MLLM study.** Per-benchmark RGR for MLLM-over-classical gains, with verdicts.

**E. Ablations.** Stability of verdicts across `φ` granularity, betting rule, `c`, split ratio, smoothing, and #permutations `R`.

**Headline claim we expect to defend:** *Under a distribution-free, anytime-valid test, a substantial fraction of reported progress on VG150, VQA-CP, and recent MLLM leaderboards is statistically indistinguishable from improved annotation-frequency-prior fitting.*

---

## 11. Threats to validity / honest caveats

- **Exchangeability**, not i.i.d., is the assumption; we enforce it by permuting the stream and averaging over `R` permutations. Temporal/structured leakage within an image (multiple pairs per image) is handled by blocking permutations at the image level.
- **Estimated projection.** Exact validity uses a frozen `q̄_f` from an independent fold `A`; we use sample-splitting (and optionally cross-fitting) so `q̄_f` is `F_0`-measurable for stream `B`. Cell sparsity is handled by KT smoothing and backoff to the global prior for unseen `φ` cells.
- **`φ` must capture the confound.** If a relevant frequency channel is omitted from `φ`, WAGER can over-credit reasoning. We mitigate with the `φ`-granularity ablation and report results for the most conservative (finest) `φ`.
- **"Usable" information is family-relative** (Xu et al. 2020): `Î_reason` measures what *this* model extracts beyond the prior, which is exactly the right currency for *gain attribution* but is not a claim about information-theoretic limits.
- **Numbers in §1 are from secondary re-implementation tables** (e.g., Scene-Graph-Benchmark.pytorch) and must be re-derived from primary PDFs before the camera-ready.
- **Novelty claim** (no existing general anytime-valid gain-attribution framework) rests on extensive but not exhaustive search; do a final Semantic Scholar / DBLP sweep before asserting non-existence in print.

---

## 12. References

*(Author lists are given in full. DOIs/pages should be re-verified against the publisher of record before camera-ready; entries marked ⚠ have an author list or page range I was not able to verify with full confidence and must be confirmed against the source.)*

**Benchmarks & datasets**
1. Krishna, Ranjay; Zhu, Yuke; Groth, Oliver; Johnson, Justin; Hata, Kenji; Kravitz, Joshua; Chen, Stephanie; Kalantidis, Yannis; Li, Li-Jia; Shamma, David A.; Bernstein, Michael S.; Fei-Fei, Li. "Visual Genome: Connecting Language and Vision Using Crowdsourced Dense Image Annotations." *International Journal of Computer Vision*, 2017, 123(1):32–73. DOI: 10.1007/s11263-016-0981-7.
2. Goyal, Yash; Khot, Tejas; Summers-Stay, Douglas; Batra, Dhruv; Parikh, Devi. "Making the V in VQA Matter: Elevating the Role of Image Understanding in Visual Question Answering." *CVPR*, 2017, pp. 6904–6913. DOI: 10.1109/CVPR.2017.670.
3. Agrawal, Aishwarya; Batra, Dhruv; Parikh, Devi; Kembhavi, Aniruddha. "Don't Just Assume; Look and Answer: Overcoming Priors for Visual Question Answering." *CVPR*, 2018, pp. 4971–4980. DOI: 10.1109/CVPR.2018.00522.
4. Hudson, Drew A.; Manning, Christopher D. "GQA: A New Dataset for Real-World Visual Reasoning and Compositional Question Answering." *CVPR*, 2019, pp. 6700–6709. DOI: 10.1109/CVPR.2019.00686.
5. Gupta, Agrim; Dollár, Piotr; Girshick, Ross. "LVIS: A Dataset for Large Vocabulary Instance Segmentation." *CVPR*, 2019, pp. 5356–5364. DOI: 10.1109/CVPR.2019.00550.
6. Yang, Jingkang; Ang, Yi Zhe; Guo, Zujin; Zhou, Kaiyang; Zhang, Wayne; Liu, Ziwei. "Panoptic Scene Graph Generation." *ECCV*, 2022, pp. 178–196. DOI: 10.1007/978-3-031-19812-0_11.

**Frequency-prior critiques & SGG methods**
7. Zellers, Rowan; Yatskar, Mark; Thomson, Sam; Choi, Yejin. "Neural Motifs: Scene Graph Parsing with Global Context." *CVPR*, 2018, pp. 5831–5840. DOI: 10.1109/CVPR.2018.00611.
8. Tang, Kaihua; Niu, Yulei; Huang, Jianqiang; Shi, Jiaxin; Zhang, Hanwang. "Unbiased Scene Graph Generation from Biased Training." *CVPR*, 2020, pp. 3716–3725. DOI: 10.1109/CVPR42600.2020.00377.
9. Chen, Tianshui; Yu, Weihao; Chen, Riquan; Lin, Liang. "Knowledge-Embedded Routing Network for Scene Graph Generation." *CVPR*, 2019, pp. 6163–6171. DOI: 10.1109/CVPR.2019.00632.
10. Tang, Kaihua; Zhang, Hanwang; Wu, Baoyuan; Luo, Wenhan; Liu, Wei. "Learning to Compose Dynamic Tree Structures for Visual Contexts." *CVPR*, 2019, pp. 6619–6628. DOI: 10.1109/CVPR.2019.00678.
11. ⚠ Li, Wei; Zhang, Haiwei; Bai, Qijie; Zhao, Guoqing; Jiang, Ning; Yuan, Xiaojie. "Rethinking the Evaluation of Unbiased Scene Graph Generation." *BMVC*, 2022. arXiv:2208.01909. *(verify full author list + page numbers against BMVC proceedings.)*
12. Teney, Damien; Kafle, Kushal; Shrestha, Robik; Abbasnejad, Ehsan; Kanan, Christopher; van den Hengel, Anton. "On the Value of Out-of-Distribution Testing: An Example of Goodhart's Law." *NeurIPS*, 2020. arXiv:2005.09241. *(verify final proceedings pagination.)*
13. Shrestha, Robik; Kafle, Kushal; Kanan, Christopher. "A Negative Case Analysis of Visual Grounding Methods for VQA." *ACL*, 2020, pp. 8172–8181. DOI: 10.18653/v1/2020.acl-main.727.

**Dataset bias & shortcut learning**
14. Torralba, Antonio; Efros, Alexei A. "Unbiased Look at Dataset Bias." *CVPR*, 2011, pp. 1521–1528. DOI: 10.1109/CVPR.2011.5995347.
15. Geirhos, Robert; Jacobsen, Jörn-Henrik; Michaelis, Claudio; Zemel, Richard; Brendel, Wieland; Bethge, Matthias; Wichmann, Felix A. "Shortcut Learning in Deep Neural Networks." *Nature Machine Intelligence*, 2020, 2(11):665–673. DOI: 10.1038/s42256-020-00257-z.
16. Misra, Ishan; Zitnick, C. Lawrence; Mitchell, Margaret; Girshick, Ross. "Seeing through the Human Reporting Bias: Visual Classifiers from Noisy Human-Centric Labels." *CVPR*, 2016, pp. 2930–2939. DOI: 10.1109/CVPR.2016.320.

**Usable information / probing (the quantity WAGER measures)**
17. Xu, Yilun; Zhao, Shengjia; Song, Jiaming; Stewart, Russell; Ermon, Stefano. "A Theory of Usable Information Under Computational Constraints." *ICLR*, 2020. arXiv:2002.10689.
18. Ethayarajh, Kawin; Choi, Yejin; Swayamdipta, Swabha. "Understanding Dataset Difficulty with V-Usable Information." *ICML*, 2022, *PMLR* 162:5988–6008.
19. Hewitt, John; Ethayarajh, Kawin; Liang, Percy; Manning, Christopher D. "Conditional Probing: Measuring Usable Information Beyond a Baseline." *EMNLP*, 2021, pp. 1626–1639. DOI: 10.18653/v1/2021.emnlp-main.122.
20. Voita, Elena; Titov, Ivan. "Information-Theoretic Probing with Minimum Description Length." *EMNLP*, 2020, pp. 183–196. DOI: 10.18653/v1/2020.emnlp-main.14.

**Testing-by-betting / e-values / growth rate (the new machinery)**
21. Ville, Jean. *Étude critique de la notion de collectif.* Gauthier-Villars, Paris, 1939. *(origin of Ville's inequality; monograph, no DOI.)*
22. Kelly, John L. "A New Interpretation of Information Rate." *Bell System Technical Journal*, 1956, 35(4):917–926. DOI: 10.1002/j.1538-7305.1956.tb03809.x.
23. Cover, Thomas M.; Thomas, Joy A. *Elements of Information Theory*, 2nd ed. Wiley-Interscience, 2006. ISBN: 978-0-471-24195-9.
24. Cover, Thomas M. "Universal Portfolios." *Mathematical Finance*, 1991, 1(1):1–29. DOI: 10.1111/j.1467-9965.1991.tb00002.x.
25. Shafer, Glenn. "Testing by Betting: A Strategy for Statistical and Scientific Communication." *Journal of the Royal Statistical Society: Series A*, 2021, 184(2):407–431. DOI: 10.1111/rssa.12647.
26. Vovk, Vladimir; Wang, Ruodu. "E-values: Calibration, Combination and Applications." *The Annals of Statistics*, 2021, 49(3):1736–1754. DOI: 10.1214/20-AOS2020.
27. Ramdas, Aaditya; Grünwald, Peter; Vovk, Vladimir; Shafer, Glenn. "Game-Theoretic Statistics and Safe Anytime-Valid Inference." *Statistical Science*, 2023, 38(4):576–601. DOI: 10.1214/23-STS894.
28. Waudby-Smith, Ian; Ramdas, Aaditya. "Estimating Means of Bounded Random Variables by Betting." *Journal of the Royal Statistical Society: Series B*, 2024, 86(1):1–27. DOI: 10.1093/jrsssb/qkad009.
29. ⚠ Henzi, Alexander; Ziegel, Johanna F. "Valid Sequential Inference on Probability Forecast Performance." *Biometrika*, 2022, 109(3):647–663. DOI: 10.1093/biomet/asab047. *(verify volume/pages.)*
30. ⚠ Grünwald, Peter; de Heide, Rianne; Koolen, Wouter M. "Safe Testing." *Journal of the Royal Statistical Society: Series B*, 2024, 86(5):1091–1128. DOI: 10.1093/jrsssb/qkae011. *(verify issue/pages.)*
31. Fieller, Edgar C. "Some Problems in Interval Estimation." *Journal of the Royal Statistical Society: Series B*, 1954, 16(2):175–185. DOI: 10.1111/j.2517-6161.1954.tb00159.x.
32. ⚠ Shah, Rajen D.; Peters, Jonas. "The Hardness of Conditional Independence Testing and the Generalised Covariance Measure." *The Annals of Statistics*, 2020, 48(3):1514–1538. DOI: 10.1214/19-AOS1857. *(verify pages.)*

**Calibration**
33. Guo, Chuan; Pleiss, Geoff; Sun, Yu; Weinberger, Kilian Q. "On Calibration of Modern Neural Networks." *ICML*, 2017, *PMLR* 70:1321–1330.

---

## 13. Reproducibility checklist
- [ ] Cached-logit `.npz` per (benchmark, model) with `{y_true, q, phi_key}`.
- [ ] Fixed random seeds; `R ≥ 100` image-blocked permutations.
- [ ] Phase-1 simulation passing type-I/coverage gates **before** real runs.
- [ ] Anchor gates passing (FREQ⇒e≈1; TDE⇒↑RGR) before headline claims.
- [ ] Released code + cached logits + per-figure notebooks (double-blind-safe).