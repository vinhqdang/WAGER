## Perspective Review Report (Peer Reviewer 3)

### Reviewer Identity
Peer Reviewer 3 (Perspective) — a computer-vision / ML-benchmarking researcher, cross-disciplinary outside voice on a statistics-journal panel. Independent; did not see any other seat's report.

### Overall Recommendation
Minor Revision

### Confidence
4

### Summary Assessment
From an outside-the-field vantage, the three empirical illustrations are unusually careful for a methods paper: the SGG audit reproduces a well-known published checkpoint (Tang et al.'s MOTIFS/MOTIFS-TDE) with numbers in the right ballpark of the original paper's PredCls table, uses the community's own protocol correctly, and is honest about the difference between its reconstructed VG150-style split and the canonical one. The CIFAR-100-LT study uses the standard construction and triple, and usefully reproduces a real, well-documented failure mode of naive class-balanced re-weighting. The 20-Newsgroups-LT addition is a legitimate generality check but reads more like the vision recipe transplanted onto text than a demonstration grounded in how the NLP long-tail community actually works. The Discussion's practical proposal that benchmarks should archive per-example probability vectors is under-argued: it treats the current lack of this practice as oversight rather than engaging storage, leaderboard-integrity, and IP/model-stealing reasons many benchmarks deliberately don't do this. Stakeholder framing is thin.

### Strengths
- Faithful SGG protocol (PredCls, FREQ baseline lineage, auditing the actual released MOTIFS/MOTIFS-TDE checkpoint with original code); reproduced numbers land near the widely cited original TDE paper's table.
- Zero-shot recall and mean-recall-by-frequency-group correctly identified as the community's existing tools for the same worry, positioned accurately (not strawmanned).
- CIFAR-100-LT triple is standard (Cui et al. 2019 profile, ResNet-32, identical optimizer/schedule); the CB degradation reported is consistent with the known motivation for DRW.
- The real-pixel CLIP experiment matches training-set size across the three compared models — exactly the control an ML reviewer would ask for.
- Honest, itemized limitations of the third domain stated in-text rather than left implicit.
- The calibration-matching control is the single most CV-literate methodological move in the paper.

### Weaknesses

1. **[Major]** CIFAR-100-LT's CB baseline accuracy (26.27%) is markedly lower than typical published values for the same protocol at the same imbalance ratio (Cui et al. 2019; Cao et al. 2019 generally report high-30s, not below the CE baseline by ten points), and the manuscript never benchmarks its own numbers against the literature. Fix: add a comparison sentence/table, or explicitly state the reimplementation wasn't tuned to match published numbers because the aim is a controlled triple, not SOTA reproduction. *Queued, not yet addressed.*

2. **[Major]** The practical-feasibility argument for releasing per-example probability vectors underestimates why benchmarks don't already do this: storage scaling, leaderboard-integrity/anti-overfitting practice, and IP/model-stealing concerns are real structural barriers, not mere oversight. Fix: acknowledge these and consider a narrower, more realistic policy ask. *Queued, not yet addressed.*

3. **[Minor–Major]** The 20-Newsgroups-LT study is a vision recipe imported into text rather than grounded in how the long-tailed-text-classification community works; a naturally long-tailed corpus or a modern text encoder would be more convincing to an NLP audience. *Queued.*

4. **[Minor]** The single-seed text result is used rhetorically as strongly as the multi-seed CIFAR result, an asymmetry deserving a sentence in the sections making the strong claim, not only in the buried §4.7 caveat. — *Addressed in this pass* (conclusion reworded to flag this explicitly).

5. **[Minor]** The five hand-built VG predictors aren't benchmarked SOTA SGG systems; a forward pointer to the later real-checkpoint audit would pre-empt a "these aren't real SGG models" reaction. *Queued, low priority.*

6. **[Minor, opportunity]** The paper never cross-validates its alignment channel against zero-shot recall on the same TDE audit, despite both being framed as addressing the same worry. *Queued.*

### Assumption Audit
- A clean, finite, benchmark-recorded nuisance grouping exists and is uncontested — many benchmarks (VQA, open-vocabulary detection) lack an equally clean candidate φ.
- Benchmark maintainers are assumed a neutral party who will declare φ in good faith, without competing incentive to avoid deflating their own leaderboard.
- Full K-way probability vectors from both compared systems are assumed available — silently excludes closed leaderboards/commercial APIs; this is stated as scope but its practical bite isn't quantified.
- A single scalar temperature per model is assumed sufficient to remove confidence-scale confounds; a richer (vector) calibration map is never tested as a robustness check.
- The classical proper-score "resolution" vocabulary is assumed legible to the paper's CV/ML empirical audience, but is largely unfamiliar in those circles — a real adoption friction distinct from correctness.

### Practical Impact Assessment
The estimator is cheap and deployable exactly as advertised — O(NK), pure NumPy, worked directly on someone else's released checkpoint without retraining. The bottleneck is organizational/cultural, not computational: the paper is optimistic to the point of being a little naive about benchmark maintainers adopting probability-vector archiving, and doesn't mention that no standard evaluation harness (torchmetrics/sklearn/HuggingFace evaluate) currently integrates this tool.

### Cross-Disciplinary / Alternative-Domain Suggestions
- Popularity bias in recommender systems: a strong additional domain candidate — inverse-propensity/counterfactual off-policy evaluation literature asks almost exactly WAGER's question, with full score vectors routinely available internally.
- NLI hypothesis-only / annotation-artifact shortcuts (Gururangan et al., Poliak et al., McCoy et al. HANS): arguably a closer text analogue to the VG story than 20-Newsgroups-LT, since it's the NLP field's own well-known shortcut-exploitation battleground.

### Questions for Authors
1. Have you checked the CIFAR-100-LT accuracies against Cui et al. 2019 / Cao et al. 2019's published numbers for the same ratio?
2. Did you cross-check the alignment channel restricted to zero-shot triplets against the reported zR@50 improvement?
3. Have you considered the storage-scaling, leaderboard-integrity, and IP reasons benchmark organizers avoid releasing probability vectors?
4. Would a richer (vector) recalibration change the calibration-matched conclusions, or is a single scalar temperature verified sufficient?
5. Why 20-Newsgroups-LT over a naturally long-tailed text corpus?

### Minor Issues
- `main.tex`'s header comment still framed the paper for CSDA (now fixed as part of the front-matter retargeting).
- Table 3's log-score magnitude (~4.5x the quadratic magnitude) has no one-line intuition in the main text.
- "PredCls" isn't expanded at first use for a non-CV JSPI readership.
