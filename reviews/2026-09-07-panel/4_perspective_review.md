# Peer Review Report

## Manuscript Information
- **Title**: An Exact Decomposition of Paired Score Differences: Separating Prior Fit from Within-Group Resolution
- **Manuscript ID**: not assigned (post-JSPI rewrite, local copy `manuscript/main.pdf`, 51 pp.)
- **Review Date**: 2026-09-07
- **Review Round**: Round 1 for this panel (Round 2 for the manuscript, following a JSPI rejection on presentation grounds)

---

## Reviewer Information

### Reviewer Role *
Peer Reviewer 3 (Perspective)

### Reviewer Identity *
Machine-learning evaluation and benchmark methodology. I work on how benchmarks are built, scored, maintained and gamed; I am a deliberate outsider to the U-statistic and proper-scoring-rule apparatus this paper is built on. I read as the panel's proxy for the reader the JSPI referee was: someone who cares about the claim and cannot check the algebra unaided. I do not assess the correctness of Theorems 1–4 or the variance derivation (Reviewer 1's remit), nor conduct a systematic literature-coverage audit (Reviewer 2's remit).

### Review Focus *
Whether the legibility rewrite actually works on a non-specialist, and specifically whether the abstract, Section 1 and Section 2 are sufficient to state the contribution without the paper's own coined vocabulary. Whether the paper's adoption story — archived per-example probabilities, maintainer-declared grouping variables, "four aligned arrays" — is realistic given how benchmarks actually operate. Which adjacent fields already do this construction under another name.

---

## Overall Assessment *

### Recommendation *
- [ ] **Accept**
- [ ] **Minor Revision**
- [x] **Major Revision** — Substantial revisions needed, re-review required after revision
- [ ] **Reject**

### Confidence Score *
4 — high confidence on the legibility, adoption-realism and cross-field-positioning questions I was seated to judge; deliberately abstaining on the statistical machinery, where my confidence would be 2.

### Summary Assessment *

The paper decomposes the score gap between two already-run probabilistic classifiers into the part attributable to fitting each subgroup's label frequencies and the part attributable to telling individual items within a subgroup apart, by re-scoring each model's stored probability vector against other items' labels inside the same subgroup. It proves the split is an exact sample identity for any Bregman score, supplies cluster-robust inference for the difference, and audits two publicly released scene-graph checkpoints, finding a headline ten-point mean-recall gain to be overwhelmingly base-rate fit.

The rewrite largely worked. I can restate the contribution in my own words from the abstract, Section 1 and Section 2 alone, without using the paper's vocabulary — which is the strongest evidence available that the JSPI complaint has been answered. The four-point example in Section 2 is genuinely good pedagogy: it arrives on page 5, it is arithmetically checkable, and its model-A/model-B contrast makes the motivating failure visible rather than asserted. The decision to audit someone else's released checkpoints rather than the authors' own models is the right and uncommon move, and Section 1.3 states the paper's limits more plainly than most methods papers manage.

What remains unfixed is that the reform stopped at the prose. Table 1 announces a vocabulary substitution the body never performs (the abstract says "group" seven times and "cell" zero; Sections 2–5 say "cell" roughly 150 times), Figure 1 does not depict what its caption describes and still carries the abandoned expansion of the acronym, and the released software exposes the paper's central quantity under two other names. Separately, the adoption argument is understated in cost and the paper's positioning omits several adjacent fields that have decomposed a between-group difference into composition and rate for decades. None of this touches the mathematics; all of it is repairable, and none of it is repairable by a copyedit. Hence Major Revision.

---

## The five questions I was seated to answer

### 1. Can I state the contribution without the paper's coined vocabulary?

Yes — and I record it verbatim, because that is the answer to the JSPI referee. The only technical word I keep is *resolution*, which the paper correctly identifies as pre-existing standard vocabulary, not its own coinage.

> Two classifiers have already been run over the same test set, so for every test item you have each model's full probability vector over all the labels, the true label, and a tag saying which subgroup the item belongs to. The paper's move is to notice that keeping the whole probability vector lets you re-score either model against a label it never saw — namely, some other item's label. So score the head-to-head difference twice: once against each item's own label, and once averaged over the labels of all the *other* items in the same subgroup. The first is the ordinary reported score gap. The second is the gap that would survive if you shuffled the labels among items inside each subgroup, which is the portion the newer model earned purely by getting each subgroup's overall label mix right — the same thing a lookup table of subgroup frequencies would earn. Subtract, and what is left is the portion earned by telling items inside a subgroup apart. Because the subtraction is bookkeeping on numbers you already have, it is exact on the sample rather than an estimate: no reference model to fit, no held-out fold, no knob to set, one pass over the data. The leftover term coincides with a quantity forecast verification has long called *resolution*, but computed for the difference between two forecasters instead of for each one separately, and that is what lets the authors attach a standard error and a confidence interval to the split. Applied to two publicly released scene-graph checkpoints, the verdict is that a headline ten-point metric gain is almost all the first kind of improvement and close to none of the second.

Where I got the material: the paragraph "What this paper does" (§1, p. 2) carried almost all of it, and Section 2 confirmed I had understood it correctly. Two places slowed me down and did not stop me:

- The abstract's penultimate sentence — *"The remainder is a U-statistic of order two equal to the within-group covariance between the two models' predicted-probability difference and the label indicator"* — stacks five technical noun phrases in 48 words and is the one place in the front matter where a non-specialist will stall. It is recoverable because the preceding four sentences already delivered the idea in plain terms, so the stall is survivable rather than fatal. I would still move it to the last position or split it in two.
- Section 2's closing paragraph asserts that the covariance form evaluates to 3/8 without showing that arithmetic, in the one section whose stated promise is that *"all the arithmetic is in eighths"*. I checked it by hand and it is right, but the reader who cannot is left with one unverifiable number in the section built for verification.

### 2. Is the four-point worked example pedagogically effective?

Mostly yes, with one consequential omission. It arrives early enough (p. 5, immediately after the introduction), it is short (two pages), and the design is well chosen: model A and model B are the same distance from the old model, so the reader sees that the aggregate score prefers B by 3× while the decomposition shows the two improved on disjoint grounds. The sentence *"aggregate scores are not merely imprecise about composition, they can order two models by the wrong criterion"* is earned by the arithmetic rather than asserted, which is exactly what the example is for.

But a reader who stops after the abstract, Section 1 and Section 2 will understand the identity and misuse the method. Section 2 has a single subgroup, so it cannot and does not show: where the confidence interval comes from, why the identified fraction matters, that merging subgroups changes the answer, or — most seriously — that rescaling a model's confidence moves score between the two components while adding no information about any item. That last fact reverses the paper's own headline audit: raw, the resolution channel reads −0.01355 with an interval excluding zero; calibration-matched, it reads −0.00006 with an interval containing zero. A practitioner who read the front matter, pointed the software at two uncalibrated checkpoints and reported the raw number would publish a significant finding the paper itself disowns. See W1.

### 3. Does Table 1 help, or does it signal a problem?

Both, and the diagnosis matters more than the verdict. A glossary is a reasonable answer to a legibility complaint. But this glossary is load-bearing for a self-inflicted reason: it promises a substitution the paper then declines to make. Its preamble says readers *"can read 'group' for cell"* — and the paper itself never does. Row by row:

| Row | Verdict |
|---|---|
| grouping variable φ ↔ stratifying / conditioning variable | **Load-bearing.** A symbol needs a name. But the paper should then adopt the standard word, not keep a third one: §4.1 introduces φ as a *"declared discrete prior feature"*, a fourth synonym that appears nowhere in this table. |
| cell ↔ level of φ; stratum | **Should be dropped, and the term with it.** "Stratum" or "group" is standard and free. Keeping "cell" while the abstract and conclusion say "group" is what forces the reader to consult the table at every section boundary. |
| label transport ↔ within-stratum relabelling | **Should be dropped.** "Transport" collides with optimal transport, a large and different literature — and the collision is *inside this paper*, which cites transport-map reductions in §3.3. "Relabelling", the paper's own gloss, is shorter and unambiguous. |
| total gain ΔT ↔ paired score differential | **Load-bearing and good.** This row does real work for a statistics reader. |
| prior-fit gain ΔP ↔ (blank) | **Load-bearing but under-filled.** The counterpart cell is a dash, yet §4.10 says outright that at a trivial partition ΔP is *"the corresponding calibration term"* of the classical decomposition. The paper knows the standard counterpart and withheld it from the table. Standardization and decomposition literatures would also call it the composition component. |
| within-group resolution gain ΔR ↔ resolution difference | **The best row in the table.** This is the one place the substitution is actually carried out in the body, and it is why I could restate the contribution. |
| coverage ↔ identified fraction | **Should be dropped.** The paper uses "coverage" in the standard interval sense in the same breath — the abstract's "interval coverage", §5.1's "Coverage of the primary interval", "94.0% empirical coverage" — and in the coined sense at "99.0% coverage" in §6.1. A glossary that redefines a word the paper simultaneously uses in its textbook sense makes things worse, not better. Use "identified fraction" throughout. |
| calibration-matched ↔ temperature-scaled on held-out data | **Load-bearing and good** — and it is the row that quietly discloses that the procedure uses held-out data, which the abstract denies. See W2. |

Net: two rows earn their place (ΔT, ΔR), two are defensible if the term is kept (φ, calibration-matched), and four mark terms that should simply have been dropped in favour of the standard word.

### 4. Adoption realism

The paper's diagnosis is right and its cost estimate is optimistic.

**Right:** the obstacle really is disclosure, not compute or difficulty. Leaderboards in vision and NLP overwhelmingly ingest ranked or argmax predictions, which is why nobody can run this audit today. And the precedent for the fix already exists, which the paper does not mention: HELM (Liang et al., 2022) publishes per-instance model outputs, and EleutherAI's `lm-evaluation-harness` computes per-option log-likelihoods for multiple-choice tasks as a matter of course. Kaggle has required probability submissions for log-loss and AUC metrics for over a decade. The paper's recommendation is therefore less radical than it presents itself, and it would be strengthened by saying so — an adoption argument that names three existing archives is far more persuasive than one that asks maintainers to change on principle.

**Optimistic:** "four aligned arrays are all it needs" is honest about the *identity* and misleading about the *procedure the paper actually recommends*. To reproduce the paper's own headline row you additionally need a fifth array (image/cluster identifiers, without which the primary uncertainty statement is unavailable), a random split of those clusters into halves, one fitted temperature per model, and an average over repeated splits. That is a sample split and a tuning parameter — the two things the abstract says are not needed. See W2.

**Not addressed at all:** three constraints a maintainer would hit immediately. (i) The two models must have been run on the identical test items in the identical order over the identical label vocabulary; leaderboards whose test sets or label spaces evolve between submissions cannot supply that, and the paper's own audit only gets it because both variants come from one checkpoint. (ii) Storage of two N×K float arrays is trivial at VG150's K = 50 and is not at K = 1000 or K = 10^5; the paper reports O(NK) as a virtue and never states the regime where it stops being one. (iii) Many benchmarks' scored unit is not a closed K-way choice at all — the paper's own scene-graph setting had to be run in PredCls mode to obtain a fixed 50-way predicate distribution, which is a real narrowing of applicability that §1.3's scope paragraph does not mention.

**Maintainer-declared φ:** as governance, the recommendation is one-sided. It does remove the submitting author's incentive to shop for the most flattering grouping. It also concentrates that power in whoever maintains the benchmark — frequently a small team who also publish competing methods on it, and frequently nobody at all after two or three years. And it sits in tension with the paper's own Proposition 3, which proves the answer is not invariant to how coarse φ is: "declare one φ" and "report all pre-declared candidates" are different policies, and the paper recommends both a paragraph apart without resolving which binds. See W6.

### 5. Cross-disciplinary connections the paper misses

The construction — hold a nuisance distribution fixed, attribute the difference to composition versus within-stratum performance — is not new outside forecast verification and comparative forecast evaluation, the two literatures the paper positions against. I am confident about the following, and each is a positioning obligation rather than a priority dispute:

- **Demography and epidemiology: direct standardization and the Kitagawa decomposition.** Kitagawa (1955) split a difference between two crude rates into a composition component and a rate component. That is structurally ΔP and ΔR. Direct standardization is the same operation as label transport with the counterfactual distribution taken from a reference population instead of from within the stratum.
- **Econometrics: Oaxaca (1973) / Blinder (1973), and DiNardo, Fortin & Lemieux (1996).** The endowments-versus-coefficients split is the same two-component logic; DFL reweighting is the counterfactual-distribution version. Anyone from labour economics will recognise ΔT = ΔP + ΔR on sight, and will ask how the paper's identity differs from a decomposition whose known hazards (path dependence, choice of reference) are well catalogued.
- **Biostatistics: Mantel–Haenszel stratified estimation, and collapsibility.** Proposition 3 is a proper-score instance of non-collapsibility; Greenland, Robins & Pearl (1999) is the standard reference for why a coarser stratification is not neutral. Citing it would let the authors say the coarsening result is an instance of a known phenomenon rather than a surprise.
- **Clinical prediction modelling: discrimination versus calibration.** This is the closest thing to a ready-made plain-language gloss for the paper's two components, and the paper's own appendices already use the word — "within-class discrimination", "per-instance discrimination" — without ever connecting to the framework. Harrell and Steyerberg's treatments of calibration-in-the-large versus discrimination are the standard vocabulary a biostatistics reader will reach for, and Table 1 should have a row for it.
- **Psychometrics: differential item functioning.** DIF asks whether two groups respond differently to an item *conditional on a matching stratum*, and the Mantel–Haenszel DIF statistic is the classical estimator. The conditioning-on-a-declared-stratum logic and the "is this a real difference or a base-rate difference" question are the same.
- **Algorithmic fairness: base-rate fit versus within-group discrimination.** Kleinberg, Mullainathan & Raghavan (2017) and Chouldechova (2017) establish that a classifier can match group base rates while having identical within-group ranking behaviour, and that these are in tension. That is the paper's ΔP/ΔR distinction as an impossibility result. The paper cites multicalibration, which is the narrowest possible entry point into this literature.
- **NLP evaluation: partial-input and hypothesis-only baselines.** Gururangan et al. (2018) and Poliak et al. (2018) established the field's standard way of stripping prior-only signal — train a model on the input fragment that carries the prior. This is precisely the "prior-only reference" the paper criticises in §1 as indirect and noisy, and Feng, Wallace & Boyd-Graber (2019), "Misleading Failures of Partial-input Baselines", is a direct argument for why that approach misleads. That paper is the strongest available support for the paper's own motivation, and it is absent.
- **NLP significance testing practice.** Dror et al. (2018) is where an ML audience places paired permutation tests on evaluation sets. Corollary 2's Diebold–Mariano bridge speaks to econometricians; this is the bridge to the readers who own the benchmarks the paper wants to change.

Two connections I flag as leads rather than claims: recommender-systems popularity-bias evaluation, where within-user or within-popularity-stratum evaluation is the standard correction for exactly this confound; and information-theoretic benchmark-difficulty measures beyond the V-information line the paper already cites.

---

## Strengths *

### S1: The legibility fix demonstrably worked on its target reader
The paragraph "What this paper does" delivers the whole construction in plain sentences before any symbol appears, and it was sufficient for me — a non-specialist in U-statistics — to restate the contribution in my own words (recorded verbatim above). Given that the prior referee "could barely make sense of what is going on" in the introduction, this is the outcome that matters most, and the paper achieved it.
**Evidence Anchor**: text: §1 "What this paper does", p. 2 "score each case's predictions against the other case's label"

### S2: The worked example's design, not just its presence
Model A and model B are constructed to be equidistant from the old model, differing only in whether the change depends on the individual case. That single design choice is what lets two pages of arithmetic demonstrate the paper's motivating failure — an aggregate score ranking B three times above A when the two improved on disjoint grounds — instead of asserting it. Most methods papers' toy examples illustrate the machinery; this one produces the counterintuitive result.
**Evidence Anchor**: table: Table 2, p. 5 — model A and model B columns are equidistant from q0, only B varying by case

### S3: Auditing released checkpoints rather than the authors' own models
The primary application is two publicly released checkpoints of a widely cited debiasing method, evaluated with the original authors' code. From a benchmark-methodology standpoint this is the right test and an uncommon one: it removes the degree of freedom that makes most evaluation-methodology papers unfalsifiable, and it makes the paper credible to the community whose reporting practices it wants to change.
**Evidence Anchor**: text: §5.2, p. 20 "the primary application is to a published pair rather than to predictors of our own"

### S4: The limits are stated where they cost the authors something
Section 1.3 declares what is not claimed before any result; §5.1 quantifies rather than hedges the confound (an unrecorded within-subgroup shortcut is credited to the resolution channel at +0.041); §5.2 reports that two proper scores disagree about the headline number and declines to adjudicate; §4.5 states that its own sensitivity bound is three orders of magnitude loose. An evaluation-methodology paper that reports the results that weaken it is unusual and should be credited.
**Evidence Anchor**: text: §1.3, p. 5 "Three limits on interpretation are worth stating before any result"

### S5: Reproducibility infrastructure at a level benchmark methodology rarely reaches
Every printed number traces to a committed cached results file, the propositions have direct numerical checks against explicit discrete populations independent of the estimator's own code path, and the four-point example of Section 2 is itself a unit test. For a paper asking benchmark maintainers to change their archiving practices, practising that standard is part of the argument.
**Evidence Anchor**: dataset: results/*.json and tests/ as described in Appendix D — every printed value traced to committed cached outputs

---

## Weaknesses *

### W1: A reader who stops after Section 2 will misuse the method, because the caveat that reverses the paper's own headline result is not in the front matter
**Problem**: Non-invariance to monotone recalibration is the single fact most likely to cause an incorrect published finding, because it changes the sign and the significance of the paper's own audit: raw, the quadratic-score resolution channel is −0.01355 with an interval excluding zero; calibration-matched, it is −0.00006 with an interval containing zero. Yet §1.3, the section explicitly headed "Scope, and what is not claimed" and offering "three limits on interpretation... worth stating before any result", does not list it. It appears once in the front matter, in a subordinate clause at the end of contribution 4, and not at all in the worked example. The reader I am proxying — who reads the abstract, the introduction and the example, then opens the software — has been told the identity is exact and has not been told that the number it produces depends on a confidence scale they have not fixed.
**Evidence Anchor**: absence: §1.3 "Scope, and what is not claimed" — expected recalibration non-invariance among its enumerated interpretation limits; checked §1.3, §2, Table 1, and contribution 4 of §1.1
**Why it matters**: The paper's contribution is an audit instrument for other people's model pairs. An instrument whose most consequential precondition is discoverable only on page 19 is not yet usable by the audience the paper is written for, and the failure mode is a false positive that looks statistically significant.
**Suggestion**: Promote it to a fourth numbered limit in §1.3, in one sentence with the two numbers from Table 4 as the demonstration. Then add a short paragraph to Section 2 showing what happens to the four-point example when model B's predictions are sharpened — the arithmetic is small enough to show, and it is the most convincing possible form of the warning. Consider making the calibration-matched row the default reported quantity rather than a control invoked "wherever the compared models differ visibly in confidence", which is itself an analyst judgement call.
**Severity**: Major
**Confidence**: 5 — core competence: this is the standard failure mode of benchmark tooling adopted from a paper's front matter

### W2: "Four aligned arrays / no sample splitting / no tuning parameter" understates what the recommended procedure costs
**Problem**: The abstract states the identity "needs no fitted baseline model, no sample splitting and no tuning parameter"; §1.3 says "exactly four aligned arrays"; §6.2 repeats "four aligned arrays are all the algorithm requires". All three are true of the bare identity. None is true of the procedure that produces the paper's headline number, which additionally requires a fifth array (cluster identifiers, without which the paper's primary uncertainty statement — the image-clustered interval — cannot be formed at all), a random split of clusters into halves, a temperature fitted per model on the first half, and an average over repeated splits. A temperature fitted on held-out data is a tuning parameter estimated on a sample split. Table 1's own last row concedes this in its definition, "temperature-scaled on held-out data", which is where I first noticed the conflict.
**Evidence Anchor**: text: Abstract, p. 1 "needs no fitted baseline model, no sample splitting and no tuning parameter"
**Why it matters**: This is the paper's adoption argument, and adoption arguments are read by people deciding whether to spend engineering budget. The honest version is still a good argument — the identity is genuinely cheap, and the extra cost is one data split rather than a fitted nuisance model — but a reader who discovers the gap after committing will discount the rest of the paper's practical claims.
**Suggestion**: Restrict the "no splitting, no tuning" claim explicitly to the identity and its interval, and state the recommended protocol's cost in the same breath: five arrays, one random split of clusters, one temperature per model, repeated splits averaged. In §1.3 and §6.2, say "four aligned arrays for the identity; a fifth for clustered inference; a cluster split for the calibration control". The claim survives the correction; the credibility gain is worth more than the lost crispness.
**Severity**: Major
**Confidence**: 5 — core competence: I reconstructed the required inputs from §5.1, §4.8 and the public `decompose_gain` signature

### W3: Figure 1 does not show what its caption describes, and both concept figures carry the vocabulary the rewrite abandoned
**Problem**: Figure 1's caption reads "The construction, on two real test cases... Two VG150 test relations share the group φ = (man, surfboard) but carry different labels. Exchanging their labels (arrows)...", and §1 points the reader to it for exactly that. The figure contains no test cases, no images, no labels and no exchange arrows: it is a four-box abstract flowchart, and its panel title reads "WAGER: Within-cell Antisymmetric Gain Evaluation of **Reasoning**" — the pre-rewrite expansion, contradicting §1's own "within-group antisymmetric gain evaluation of resolution". Figure 2, on page 14, is the figure the caption describes: it has the crossing arrows and the label exchange. Figure 2's own title uses a third word, "alignment", and labels its two units "image i" and "image j" although the paper's units are relations, several per image, which is why it clusters by image.
**Evidence Anchor**: figure: Figure 1, p. 3 — panel title reads "Evaluation of Reasoning" and shows a four-box flowchart, not the two captioned VG150 cases with label-exchange arrows
**Why it matters**: The non-specialist reads the figures first. In a manuscript resubmitting after a rejection for obscurity, the first visual the reader meets contradicts its own caption, uses a term the paper's glossary says was replaced, and expands the acronym differently than the text does. It reads as a rewrite that did not reach the figure scripts, which invites the reviewer to wonder what else it did not reach.
**Suggestion**: Move the current Figure 2 to the position of Figure 1 — it is the picture the introduction needs — and either drop the flowchart or move it to Section 4 as a pipeline summary. Regenerate both titles in the paper's current vocabulary, and relabel Figure 2's units as relations within a shared subgroup rather than "image i"/"image j". If any acronym is kept, fix its expansion once and use it everywhere including the figure scripts and the software docstring.
**Severity**: Major
**Confidence**: 5 — core competence: direct inspection of `figures/fig1_new_concept.png` against its caption

### W4: The terminology reform stops at the prose, which is why Table 1 has to exist
**Problem**: Table 1's preamble tells the reader they "can read 'group' for cell... and lose nothing". The paper does not take its own advice. The abstract uses "group" seven times and "cell" zero; Section 1 uses "group" twenty-three times; Section 2 then switches entirely to "cell" (eleven uses, zero of "group"), and Section 4 uses "cell" seventy-five times. A fourth name, "declared discrete prior feature", is introduced in §4.1 and appears in no glossary row. The reader carried along by the plain-language introduction hits the worked example and must begin translating — and the glossary is load-bearing precisely because the substitution it promises was never executed.
**Evidence Anchor**: text: §1.2, p. 4 "Readers who prefer the standard vocabulary can read ``group'' for cell"
**Why it matters**: This is the JSPI complaint in a milder form. A glossary that a reader must hold open is not a fix for unexplained terminology; it is a bookmark for it. And the specific failure — one word in the front matter, a different word in the body — means the two parts of the paper read as written by different hands, which is the impression the rewrite was meant to remove.
**Suggestion**: Perform the substitution globally. Pick one word — "group" reads best in the abstract and is what the title uses — and use it from the abstract to the appendices, retiring "cell", "prior feature" and "prior cell". Then Table 1 shrinks to the four rows that carry real information (ΔT, ΔP, ΔR, φ), which is a far better advertisement for the paper's legibility than an eight-row glossary.
**Severity**: Major
**Confidence**: 5 — core competence: counted across all ten manuscript source files

### W5: The paper positions against two literatures and omits several that have decomposed exactly this contrast for decades
**Problem**: Section 3 situates the work against proper-score decomposition and comparative forecast evaluation, both accurately. It does not mention the composition-versus-rate decomposition literatures: Kitagawa's rate decomposition and direct standardization in demography and epidemiology, Oaxaca–Blinder and DiNardo–Fortin–Lemieux in econometrics, Mantel–Haenszel stratified estimation and collapsibility in biostatistics, differential item functioning in psychometrics, the discrimination-versus-calibration framework in clinical prediction modelling, base-rate versus within-group fairness impossibility results, or the partial-input-baseline literature in NLP that is the closest existing practice to the alternative the paper criticises. The paper's word for "resolution" in its own appendices is "discrimination", used informally and never connected.
**Evidence Anchor**: absence: §3 Related work — expected the composition-versus-rate decomposition and standardization literatures (Kitagawa, Oaxaca–Blinder, Mantel–Haenszel, DIF, discrimination-versus-calibration, partial-input baselines); checked §3.1–§3.4, ref.bib, Table 1
**Why it matters**: Two costs. First, credibility: a labour economist or an epidemiologist reading ΔT = ΔP + ΔR will recognise it immediately, and a paper that does not acknowledge the resemblance looks either unaware or evasive about how much of its novelty is the finite-sample identity plus inference rather than the decomposition itself. Second, the omitted literatures have already catalogued this construction's hazards — path dependence and reference-choice sensitivity in Oaxaca–Blinder, non-collapsibility in the stratification literature — and Proposition 3 is a rediscovery of one of them. Citing them would let the authors present the coarsening result as an instance of a known phenomenon in a new estimand, which is a stronger claim than presenting it as a surprise.
**Suggestion**: Add a short subsection, "Decomposing a difference into composition and within-stratum performance", naming these lines and stating plainly what is and is not new: the pairwise finite-sample identity, the U-statistic remainder, and the inference for the difference. Add a Table 1 row mapping ΔP/ΔR to calibration/discrimination, which is the single highest-value bridge to clinical-prediction and fairness readers. This will shorten the novelty claim and strengthen it.
**Severity**: Major
**Confidence**: 4 — adjacent-field competence: confident these literatures exist and are structurally parallel; I have not audited priority, which is Reviewer 2's remit

### W6: The maintainer-declared-φ recommendation is one-sided as governance and in tension with the paper's own coarsening result
**Problem**: The Discussion recommends that "the benchmark, not the submitting author, declare the grouping variable", on the grounds that this "removes the incentive to report only the most favorable of several candidates". The analysis stops there. It does not consider that benchmark maintainers are frequently also authors of methods evaluated on their benchmark; that most benchmarks have no active maintainer after a few years; or that the paper's own Proposition 3 proves the estimate is not invariant to how coarse φ is, so whoever declares φ chooses which improvements are creditable. The paper then recommends, one paragraph later, that "all pre-declared candidates should be reported", which is a different and partly incompatible policy, and offers multicalibration as the principled answer while explicitly leaving it to future work.
**Evidence Anchor**: text: §6.1, p. 23 "Our recommendation is that the benchmark, not the submitting author, declare the grouping variable"
**Why it matters**: This recommendation is a substantial part of the paper's claim to impact — it is repeated in the Conclusion — and as written it would be hard for a benchmark to act on. The paper has, in Proposition 3, the technical result that makes the governance question sharp, and does not use it there.
**Suggestion**: Replace the single recommendation with a short, honest governance paragraph: pre-registration of φ by whoever declares it, with the rationale published alongside; a required minimum set of candidate groupings rather than one; disclosure when the declaring party has a submission on the leaderboard; and an explicit statement, citing Proposition 3, that the declared granularity is a substantive choice rather than a formality. Naming the failure modes will make the recommendation more likely to be adopted, not less.
**Severity**: Major
**Confidence**: 4 — core competence in benchmark governance; I have not surveyed maintainer practice systematically

### W7: The two proper scores disagree about the headline resolution number and the paper declines to adjudicate, which leaves the channel short of a reportable quantity
**Problem**: In the calibration-matched audit, the quadratic score gives ΔR = −0.00006 with a 95% interval of [−0.00120, +0.00109] and a randomization p of .555, while the log score on the same comparison gives ΔR = +0.04396 with a 95% interval of [+0.04079, +0.04714]. One reads exactly null; the other is significantly positive with the opposite sign. The paper reports this honestly, narrows its claim to what both scores agree on, and says "nothing in Section 4.1 privileges one proper score's resolution estimate as the 'true' one".
**Evidence Anchor**: table: Table 4, p. 22 — calibration-matched quadratic ΔR = −0.00006 [−0.00120,+0.00109] against log ΔR = +0.04396 [+0.04079,+0.04714]
**Why it matters**: The paper asks benchmarks to adopt this as a reporting standard, which requires the reported quantity to have a determinate value. If the sign and significance of the resolution channel depend on a scoring rule the paper declares rather than derives, a maintainer cannot report "the" resolution gain, and a submitting author gains a new degree of freedom — choose the score whose channel favours their method. This is the same gaming problem the paper solves for φ and leaves open for S. Note that the narrowed claim the paper does make ("far smaller than the prior-side shift") is well supported; the problem is what a reporting standard would have to say.
**Suggestion**: Either give a principled default with an argument (the paper's stated reasons for the quadratic score — bounded, no clipping, uses the whole vector — are already most of one, and boundedness is a condition of Theorem 4, so the log score is arguably outside the inference framework the paper proves), or state a reporting rule: report both, and treat the resolution channel's sign as established only where the two agree. Either is defensible; the current position leaves the practitioner without an instruction. It would also help to say why the two scores diverge here — whether it is the ε-floor, or the log score's sensitivity to small probabilities on rare predicates — since that diagnosis is what tells a maintainer which score matches their benchmark.
**Severity**: Major
**Confidence**: 4 — benchmark-reporting competence; the underlying question of which proper score is appropriate is Reviewer 1's

### W8: Section 2 claims to exhibit properties it structurally cannot
**Problem**: Section 2 opens by saying four data points "exhibit in arithmetic every property that Section 4 proves in general". Having one subgroup, it cannot exhibit the coarsening proposition (which needs at least two finer subgroups), the identified fraction and singleton exclusion, the cluster-robust interval, or asymptotic normality — that is, contributions 2 and half of 3.
**Evidence Anchor**: text: §2, p. 5 "exhibit in arithmetic every property that Section~\ref{sec:method} proves in general"
**Why it matters**: A reader who trusts the sentence will believe they have seen the whole method and will not read Section 4. Given the paper's stated aim of being followable in its first two sections, over-promising there is costly.
**Suggestion**: Say what it does exhibit: the identity, the exactly-zero resolution gain for a subgroup-constant change, the attenuation factor, and the ordering failure. Then say in one sentence which properties need more than one subgroup and where they are.
**Severity**: Minor
**Confidence**: 5 — core competence: direct reading

### W9: The one number in the worked example the reader cannot check by hand
**Problem**: Section 2's closing paragraph states that the covariance form evaluates to 3/8 for model B, in a section that promises "all the arithmetic is in eighths". The step is not shown; the reader must set up two within-subgroup covariances themselves. I verified it and it is correct.
**Evidence Anchor**: text: §2, p. 6 "gives $2\sum_y\operatorname{Cov}(\Delta q_y,\ind\{Y=y\})=3/8$ --- not the $1/2$ the transport calculation returned"
**Why it matters**: This paragraph carries the attenuation result, which is one of the paper's four contributions, and it is the one place in the section built for hand-verification where hand-verification stops.
**Suggestion**: Add one displayed line with the two probability-change vectors and the two indicator vectors, or a two-row table. It costs three lines and completes the section's promise.
**Severity**: Minor
**Confidence**: 5 — core competence: I checked the arithmetic

### W10: Table 1 withholds a standard counterpart the paper names elsewhere
**Problem**: The "prior-fit gain ΔP" row's standard-counterpart cell is a dash, implying no standard term exists. Section 4.10 states that at the trivial partition ΔP is "the corresponding calibration term" of the classical single-model decomposition.
**Evidence Anchor**: table: Table 1, p. 4 — the "prior-fit gain ΔP" row's standard-counterpart cell is "---"
**Why it matters**: The dash tells the reader that this component is the paper's own invention when the paper knows otherwise, and it withholds the mapping (calibration / reliability, or composition) that would let a clinical-prediction, epidemiology or economics reader place the whole construction in one glance.
**Suggestion**: Fill the cell with "calibration (reliability) term; composition component", cross-referencing §4.10.
**Severity**: Minor
**Confidence**: 5 — core competence: direct comparison of Table 1 with §4.10

### W11: "Coverage" is used in two incompatible senses, one of them created by the glossary
**Problem**: Table 1 defines "coverage" as the identified fraction. The paper simultaneously uses the word in its standard interval sense throughout — the abstract's "Simulations establish interval coverage", §5.1's heading "Coverage of the primary interval", "94.0% empirical coverage against a nominal 95%" — and in the coined sense at "VG150's 99.0% coverage" in §6.1. Section 6.2 then uses it in a third, colloquial sense: "claim a coverage we have not earned".
**Evidence Anchor**: text: §5.1 heading, p. 19 "Coverage of the primary interval" against Table 1's "coverage & identified fraction"
**Why it matters**: These are the two quantities a reader most needs to keep apart when judging the audit — how much of the test set was usable, and whether the interval is trustworthy. A shared word between them is a comprehension hazard that the paper introduced on purpose.
**Suggestion**: Drop the glossary row, use "identified fraction" everywhere for the first sense, and reserve "coverage" for intervals. The software's `coverage` field should be renamed or documented accordingly.
**Severity**: Minor
**Confidence**: 5 — core competence: counted all occurrences across the manuscript sources

### W12: The public software exposes the paper's central quantity under two names, neither of which is the paper's
**Problem**: The manuscript names `wager/antisymmetric.py` and `decompose_gain` as the implementation of record. That module's docstring expands WAGER as "Within-cell Antisymmetric Gain Evaluation of **Reasoning**", its result object's field is `reasoning_gain` with an `alignment_gain` alias, and its interval is `reasoning_ci`/`alignment_ci`. The word "resolution" does not name any public field. A reader who has just been taught "within-group resolution gain" cannot find it in the code by name.
**Evidence Anchor**: dataset: wager/antisymmetric.py (named in Appendix D) — public result fields are reasoning_gain and alignment_gain, with no resolution-named field or property
**Why it matters**: The software is the adoption path, and the paper's principal legibility claim is that coined vocabulary was replaced with standard terms. An artifact carrying two superseded names undercuts that claim and makes the paper harder to follow into the code — the specific complaint the rewrite exists to answer. The backward-compatibility note in the code is a reasonable engineering decision; the absence of the current name is not.
**Suggestion**: Add `resolution_gain` / `resolution_ci` as the primary names with the existing two as documented aliases, fix the module docstring's expansion, and state the alias mapping once in Appendix D so a reader moving from paper to code is not left guessing.
**Severity**: Minor
**Confidence**: 5 — core competence: read the module and the manuscript's reference to it

### W13: The scope section omits the adoption constraints a benchmark maintainer would hit first
**Problem**: Section 1.3 states the requirement as four aligned arrays and rules out generative evaluation. It does not state that the two models must have been evaluated on identical items in identical order over an identical label vocabulary; that storage is two N×K float arrays, which is a real constraint at large K; or that the scored unit must be a closed K-way choice, which is why the paper's own scene-graph audit runs in PredCls mode.
**Evidence Anchor**: absence: §1.3 "Scope, and what is not claimed" — expected the item-alignment, shared-vocabulary, storage and closed-choice-mode constraints on applicability; checked §1.3, §5.2, §6.2, Appendix D
**Why it matters**: These are the questions a maintainer asks in the first five minutes. Answering them in the scope section costs three sentences and is the difference between a proposal that can be evaluated and one that has to be reverse-engineered.
**Suggestion**: Add them to §1.3 as stated preconditions, and note in §5.2 that PredCls mode is what supplies the fixed 50-way distribution — currently the reader must infer this.
**Severity**: Minor
**Confidence**: 4 — core competence in benchmark engineering; the storage figure is my estimate, not the paper's

---

## Detailed Comments *

### Title & Abstract
The title is a genuine improvement: it names the operation ("decomposition of paired score differences") and the two components, and it does so without coined vocabulary. It is honest about scope and would be findable by someone searching for a score decomposition.

The abstract's first five sentences are the best writing in the paper. It opens on a concrete situation, names the ambiguity, gives the construction in one sentence, and states what it costs. The last third is where it turns: the U-statistic/covariance/resolution sentence is the front matter's densest, and the very last sentence ("a ten-point gain in a widely reported metric is overwhelmingly group-frequency fit") introduces "group-frequency fit", a phrase used nowhere else — the body says "prior-fit gain". Fixing that one phrase and reordering the last two sentences would leave the abstract in good shape.

### Introduction
Effective. The Visual Genome man-on-a-surfboard example is the right kind of opening — a reader with no statistics can see the ambiguity. The critique of the fitted-reference alternative is fair and gives a reason for the new construction rather than asserting a gap. The four contributions are readable, and reducing nine to four was clearly the right call.

Two structural problems, both covered above: the figure the introduction points to does not show what the caption promises (W3), and the vocabulary changes at the section boundary (W4). One smaller thing: contribution 4 carries the recalibration caveat in a subordinate clause where §1.3's enumerated limits are the natural home (W1).

### Literature Review / Theoretical Framework
Within the two literatures it addresses, the positioning is careful and specific — the argument that inference does not transfer from single-model decompositions (§3.1) is the strongest paragraph in the section, and the DeLong precedent is exactly the right kind of citation. My concern is the perimeter, not the interior: the composition-versus-rate decomposition literatures are absent (W5). Systematic coverage is Reviewer 2's call, not mine.

### Methodology / Research Design
I abstain on the correctness of the theorems, the influence-function derivation and the variance estimator; that is Reviewer 1's remit and outside my competence. Two things I can judge. First, the section's own reading guide — "a reader who wants only what is needed to use the estimator can read Sections 4.1, 4.2, 4.6 and 4.8" — is a genuine kindness and more papers should do it. Second, the ordering works: the identity precedes the generalisation, the design-choice results, and the inference, which is the order a practitioner needs.

### Results / Findings
The audit is well constructed and honestly reported. Reproducing the published behaviour before decomposing it (R@50, mR@50, zR@50 all matching) is the right discipline, and the reproduction numbers let a reader check that the audited pair is the pair the field knows. The raw-versus-calibration-matched contrast is the paper's most valuable empirical content precisely because it changes the answer. Table 4 is legible.

The unresolved item is the scoring-rule disagreement (W7). The paper's handling is honest; it is not yet an instruction.

Moving three of four studies to Appendix E behind a one-page summary was the right decision for the reader who wants the argument, but note that it relocates rather than reduces: a reader who wants to check the breadth claim faces twenty appendix pages, and the most interesting single result in the paper — the frozen-CLIP model that loses on every aggregate measure while resolving individual cases significantly better — is now on page 44. That result is the cleanest demonstration the paper has that the decomposition can overturn an aggregate verdict. I would consider promoting it to the main body, in two paragraphs, in place of some of §4's exposition.

### Discussion
Substantive and largely candid; §6.1's list of interpretation limits is more forthcoming than most. The adoption paragraph correctly identifies disclosure as the obstacle and would be considerably stronger for naming the archives that already do it (see question 4 above). The governance recommendation needs work (W6). Section 6.2's admission about the fine class label not serving as a grouping variable — "it would leave every cell label-homogeneous and drive ΔR to zero by construction, producing an artifact that reads exactly like a null result" — is exactly the right kind of warning and belongs in the front matter, not on page 24.

### Conclusion
Does not over-infer. The characterisation of the audited method — "since the method's own construction subtracts a context-only prediction, this characterizes what it does rather than indicting it" — is fair to the authors of the audited work, which matters for a paper whose contribution is auditing other people's releases. The closing recommendation repeats the governance proposal and inherits W6.

### References
Not my remit. I note only that the bibliography is heavily weighted to computer vision and forecast verification, consistent with W5.

---

#### Assumption Audit

- **Explicit assumptions**: The declared assumptions are stated where they belong and, for the ones I can judge, held to. Two are worth restating as choices rather than givens. First, that the grouping variable is discrete and low-cardinality — the paper says so, and notes that approximate matching for continuous variables would trade exactness for modelling assumptions. Second, that both models are frozen and produce full probability vectors over a shared label set; this is what makes the whole construction free, and it is also what excludes most of what benchmarks now evaluate (generative outputs, ranked candidate sets, variable label spaces). The paper acknowledges the first exclusion and not the second two (W13).
- **Implicit assumptions**: Three that I would ask about. (i) That a "case-specific" improvement is the more valuable kind. The paper is careful to disclaim this in §1.3 and §6.1 — "a prior-fit gain is not illegitimate" — but the rhetoric elsewhere pulls the other way: "a lookup table of training frequencies also achieves" it, "evaporates if the relation frequencies shift", "answers a question nobody asked". A reader will come away believing ΔR is the good channel, whatever §1.3 says. (ii) That a single declared grouping variable can carry the analyst's notion of "the prior". The paper's own Proposition 3 shows the answer moves with granularity, so the estimand is jointly a property of the models and of an analyst's choice — which the paper states, but which the framing "an exact decomposition" understates. (iii) That the score gap is the quantity in dispute. In the audited case it is not: mean recall is, and the paper's own bridge appendix exists because the field's metric and the paper's score are different objects. §5.2's honest note that "TDE is designed to change the decision rule rather than to emit calibrated probabilities" is the seam here, and it deserves more than one sentence, because it is the general case rather than a quirk of this audit — most benchmarks are scored by decision-rule metrics, and a proper-score decomposition speaks to them only indirectly.
- **Paradigmatic assumptions**: The paper is a statistics paper about an ML practice, and its paradigm — declare the nuisance structure, hold it fixed, attribute the remainder, attach an interval — is the right one and is applied consistently. Its blind spot is the one that paradigm usually has: it treats φ as exogenous. In benchmark practice φ is an artifact of annotation policy, and the object-class pair in Visual Genome is itself a product of a vocabulary chosen by frequency. Conditioning on it does not make it neutral; it makes it authoritative. The paper is closer to acknowledging this than most (§6.1's "the annotation prior is a property of the dataset") and could say it outright.

#### Cross-Disciplinary Connections
Covered in full under question 5 above. In brief: parallel research exists in demography (Kitagawa; direct standardization), econometrics (Oaxaca–Blinder; DiNardo–Fortin–Lemieux), biostatistics (Mantel–Haenszel; collapsibility), psychometrics (differential item functioning), clinical prediction modelling (discrimination versus calibration), algorithmic fairness (base-rate versus within-group impossibility results), and NLP evaluation (partial-input and hypothesis-only baselines; paired significance-testing practice). The most valuable borrowings would be the calibration/discrimination vocabulary as a Table 1 row, the collapsibility framing for Proposition 3, and the partial-input-baseline literature as support for the paper's own motivation. Methodologically, the decomposition literatures also carry warnings the paper should inherit — reference-choice sensitivity and path dependence in Oaxaca–Blinder-type splits are the analogue of the paper's φ-granularity problem, already studied.

#### Practical Impact
- **Real-world application**: Real, and narrower than claimed. Where a benchmark already archives per-example probabilities over a fixed label set and has a defensible grouping variable, this is a genuinely cheap and genuinely informative audit, and I would run it. The audited example is convincing evidence of that. The set of benchmarks meeting those conditions today is small, and the paper's estimate of how easily it could grow is optimistic (W2, W13).
- **Implementation feasibility**: The computation is not the barrier and the paper is right about that. The barriers are archiving policy, item-alignment across submissions, and — the one the paper does not treat — that the decision-rule metrics benchmarks actually report are not the proper scores this decomposes. A maintainer persuaded by this paper still has to decide what to do when the decomposition and the leaderboard metric disagree, which is precisely the situation the audit produces.
- **Stakeholders**: Two voices are missing. The *submitting author*, who will experience a maintainer-declared grouping variable as a rule that decides whether their improvement counts, and who has no recourse if they think the declared φ absorbs the signal their method targets — the paper's own Proposition 3 says this is possible. And the *benchmark maintainer*, treated in the Discussion as an agent who will adopt a new archiving and declaration policy, with no discussion of who pays for the storage, who arbitrates disputes about φ, or what happens when the maintainer is also a competitor. A short paragraph from each perspective would strengthen the adoption case considerably.

#### Broader Implications
- **Ethical dimensions**: Low direct risk; two indirect ones worth a sentence. First, an audit instrument that declares part of an improvement to be "merely" base-rate fit will be used rhetorically, and the paper's careful disclaimer that prior-fit gain is legitimate will not travel with the number. Long-tailed and rare-class work is where this matters most, since that literature's whole point is often to change how base rates are handled — a paper could have its central contribution described as prior-fit by an auditor using this tool. The paper's §1.3 and §6.1 disclaimers are good; I would add one sentence naming this specific misreading. Second, if adopted as a reporting requirement, the declared grouping variable becomes a normative statement about which distinctions a benchmark considers worth making, and in fairness-adjacent settings that is a value judgement rather than a technical one.
- **Social impact**: Indirect, via evaluation practice. If the paper's recommendation were adopted, the plausible effect is good: it would make shortcut-driven improvements visible earlier and cheaply. The risk is a monoculture in which the declared φ becomes the definition of "real" improvement, which the paper anticipates ("its value lies not in any single φ settling what counts as understanding").
- **Future directions**: The most valuable next step from where I sit is not a theoretical extension but a demonstration on a benchmark that already archives per-instance outputs — a HELM-style scenario or a multiple-choice suite where log-likelihoods are already computed — which would let the paper claim adoption is available now rather than contingent on archiving reform. Second, the multicalibration connection is currently a promissory note; a version of the decomposition with a guarantee uniform over a declared class of groupings would answer W6 and W7 at once. Third, translating the components into the decision-rule metrics benchmarks actually report is the bridge that would make this usable by the audience the paper addresses; the metric-bridge appendix is a start.

---

## Questions for Authors *

1. The calibration-matched protocol requires a random split of clusters, a temperature fitted per model, and averaging over repeated splits, and the primary interval requires cluster identifiers. How do you reconcile that with the abstract's "no sample splitting and no tuning parameter" and with "four aligned arrays are all the algorithm requires"? I am not disputing that the identity itself is free — I want the recommended procedure's cost stated where a practitioner will read it.

2. Table 4's two proper scores disagree on the sign and the significance of the calibration-matched resolution channel. If a benchmark adopted your reporting block, what would it report? Is the quadratic score the default because it is bounded (and therefore inside Theorem 4's conditions, which the floored log score is not), or is the intended standard "report both and claim only what they agree on"? And do you have a diagnosis of why they diverge here?

3. How does the identity ΔT = ΔP + ΔR relate to Kitagawa's rate decomposition and to Oaxaca–Blinder-type composition/structure splits, and how does Proposition 3 relate to non-collapsibility as understood in the stratification literature? I ask because readers from those fields will see the resemblance immediately, and because those literatures have already catalogued reference-choice sensitivity — a favourable comparison stated by you is worth more than an unfavourable one inferred by a reader.

4. Your audited method is reported through mean recall, and you note that it "is designed to change the decision rule rather than to emit calibrated probabilities". How should a maintainer act when your decomposition of a proper score and their decision-rule metric disagree? This seems to me the general case rather than a quirk of this audit, and the answer determines whether the reporting block you propose is usable.

5. Who declares the grouping variable when the benchmark maintainer is also a competitor on the leaderboard, or when there is no active maintainer? And given Proposition 3, what recourse does a submitting author have if they believe the declared grouping absorbs precisely the signal their method targets?

---

## Minor Issues

### Language / Terminology
- Abstract, last sentence: "group-frequency fit" appears nowhere else; the body says "prior-fit gain". Use one phrase.
- §4.1, p. 9: "a declared discrete prior feature" is a fourth name for φ, absent from Table 1.
- §6.2, p. 24: "the fine class label cannot serve as an cell" — article error, and an instance of "cell" used as a bare noun where "grouping level" would read better.
- §4.6 and passim: "WAGER computes", "WAGER already requires a bounded score", "WAGER will count" — the acronym as grammatical subject appears roughly thirty times in Section 4 and is the register the prior referee objected to. "The estimator" or "the decomposition" reads better and costs nothing.
- The acronym's expansion differs across artifacts: "resolution" in §1, "Reasoning" in Figure 1's panel title and in the software docstring. Fix once or drop the acronym.

### Figures and Tables
- Figure 1 (p. 3): caption describes a figure that is not there; see W3.
- Figure 2 (p. 14): title uses "alignment", a term in neither the paper nor Table 1; units labelled "image i"/"image j" although the paper's units are relations, several per image.
- Figure 2 belongs near Figure 1's current position, where the introduction needs it.
- Table 1: consider reducing to the four informative rows once the vocabulary is unified (W4, W10, W11).

### Layout
- Section 2's promise "every property that Section 4 proves in general" (W8) sits in the section's first sentence, where it does the most damage.
- The most striking empirical result in the paper (the frozen-CLIP model that loses on every aggregate measure while resolving individual cases better) is on page 44. Consider promoting two paragraphs of it into the main body.

---

## Criterion-Bound Judgements *

Calibration status: `NOT_CALIBRATED`

Applying `references/quality_rubrics.md` within this seat's remit. Judgements are criterion-bound categories, not scores; they are not totalled, weighted, or mapped to the recommendation.

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | quality_rubrics.md Dimension 1 (defensible gap; distinguished from prior work; novelty not overstated) | PARTLY_MEETS | absence: §3 Related work — expected the composition-versus-rate decomposition and standardization literatures (Kitagawa, Oaxaca–Blinder, Mantel–Haenszel, DIF, discrimination-versus-calibration, partial-input baselines); checked §3.1–§3.4, ref.bib, Table 1 | The specific contribution — a pairwise finite-sample identity with inference for the difference — is plausibly novel and the paper is careful not to claim the resolution term itself. But novelty is argued against two literatures only, and several adjacent fields have decomposed a between-group difference into composition and within-stratum performance for decades. The claim needs positioning against them, which will narrow and strengthen it. | Priority assessment is Reviewer 2's remit; I assert structural parallelism, not precedence | Yes — W5 requires new positioning text before the novelty claim can be assessed as stated |
| Methodological Rigor | quality_rubrics.md Dimension 2 | NOT_ASSESSED | — | Correctness of Theorems 1–4, the influence function and the variance estimator is Reviewer 1's remit and outside my competence | Full abstention | No |
| Evidence Sufficiency | quality_rubrics.md Dimension 3 (right type, quality and coverage of evidence for each material claim) | PARTLY_MEETS | table: Table 4, p. 22 — calibration-matched quadratic ΔR = −0.00006 [−0.00120,+0.00109] against log ΔR = +0.04396 [+0.04079,+0.04714] | Simulation, controlled predictors, two data modalities and a third-party checkpoint audit are more than adequate coverage for the identity and its behaviour. The gap is claim-specific: the claim that this is adoptable as a benchmark reporting standard is not yet evidenced, since the headline resolution channel's sign depends on an undeclared scoring-rule choice and no demonstration exists on a benchmark that already archives probabilities | I do not assess whether the simulation designs are the right ones (Reviewer 1) | Yes — W7 bears on what the reporting proposal can claim |
| Argument Coherence | quality_rubrics.md Dimension 4 (traceable problem-to-implication chain; conclusions within evidence) | PARTLY_MEETS | text: Abstract, p. 1 "needs no fitted baseline model, no sample splitting and no tuning parameter" | The problem-method-result chain is traceable and the conclusions do not over-reach on the mathematics. Two links do not hold: the cost claim in the abstract is contradicted by the procedure used for the headline number, and the governance recommendation is stated twice in incompatible forms one paragraph apart | Internal-consistency verification generally is the Devil's Advocate's remit; I report only what bears on the adoption argument | Yes — W2 and W6 are both repairable by rewriting, but must be rewritten |
| Writing Quality | quality_rubrics.md Dimension 5 (communicates its reasoning precisely enough to be reviewed and used) | PARTLY_MEETS | text: §1.2, p. 4 "Readers who prefer the standard vocabulary can read ``group'' for cell" | Substantially improved and now reviewable — I could restate the contribution in plain language from the front matter, which is the criterion the prior rejection set. It is not yet usable without friction: the promised vocabulary substitution is not carried out, "coverage" carries two senses, Figure 1 contradicts its caption, and the software exposes the central quantity under two superseded names | Judged as the paper's target non-specialist reader, which is this seat's assignment; a specialist reader would rate this higher | Yes — W3 and W4 are the unresolved remainder of the issue that caused the prior rejection |
| Literature Integration | quality_rubrics.md Dimension 6 | PARTLY_MEETS | text: §3.1, p. 7 "Variance estimators for the single-model decomposition target one resolution term in isolation" | Within forecast verification and comparative forecast evaluation the integration is critical and specific rather than decorative, and the argument about why inference does not transfer is genuinely good. Scoped to my remit — cross-disciplinary reach — the conceptual lineage outside those two literatures is not identified | Systematic coverage audit is Reviewer 2's remit; I assess only whether adjacent-field lineage is named | Yes, jointly with Originality, via W5 |
| Significance & Impact | quality_rubrics.md Dimension 7 (claimed implications follow from evidence; demonstrated separated from speculative) | PARTLY_MEETS | text: §6.1, p. 23 "Our recommendation is that the benchmark, not the submitting author, declare the grouping variable" | The demonstrated significance is real: a published, widely cited improvement is shown to be almost entirely base-rate fit, using the original authors' own code. The claimed practical impact — routine adoption on archived probabilities with maintainer-declared groupings — is presented with more confidence than the analysis supports, understates its own procedural cost, and does not survive the governance and applicability questions a maintainer would ask first | Benchmark-practice judgement, from experience rather than a survey of maintainer policy | Yes — W1, W2, W6 and W13 all bear here, and W1 additionally carries a misuse risk |

The recommendation follows from four unresolved decision-bearing criteria, all repairable without new mathematics and none by copyediting: Writing Quality (the vocabulary substitution and the figures — the unfinished remainder of the issue that caused the prior rejection), Significance & Impact (the understated adoption cost, the absent misuse warning in the front matter, and the one-sided governance recommendation), Originality and Literature Integration jointly (positioning against the composition-versus-rate decomposition literatures), and Evidence Sufficiency (what a reporting standard can claim when two proper scores disagree on the headline channel). The identity, the audit and the reproducibility infrastructure are, from where I sit, sound and worth publishing. Major Revision, not Reject: every finding I raise is a rewriting or repositioning task on a manuscript whose substance survives it, and the central legibility test — can a non-specialist state the contribution — the paper now passes.
