# Review Panel Provenance (#540/#740)

Panel: simulated CVPR 2027 review panel, skill `academic-paper-reviewer`, mode `full` (skill version not stated by the dispatcher).
Review target: `cvpr2027/paper.pdf` + `cvpr2027/supp.pdf` at repository commit `ea0efe7` (the version after the round-3 must-fix and should-fix passes).
Panel date: 2026-10-28. Review round: 4. The previous panel is `reviews/2026-10-14-cvpr-panel/` (round 3, commit `6b8f1b9`, roadmap IDs `R6-n`); this panel's roadmap IDs are `R7-n`.
Accountable human: Quang-Vinh Dang (British University Vietnam).

## Status of this record

This file is a hand-written provenance statement from the Phase 2 synthesizer, built from what the dispatching instruction said. It is not a replay-valid `review-panel-provenance/1.0` artifact: no typed artifact, artifact SHA-256, normalized-manifest digest or execution-topology digest was supplied to the synthesizer, so none is reported and none is invented. Every axis below is therefore stated as reported by the dispatcher, with the basis shown, and any axis the dispatcher did not state is `unknown`.

- `calibration_status: NOT_CALIBRATED` (package level and for every seat)
- `criteria_binding_unavailable`: no #684 criteria authority or author-confirmed target context was supplied. All five cards disclose this. No venue-alignment claim is made anywhere in the panel output.

## Seats

| Seat | Role ID | Actor type | Execution | Peer outputs visible | Prior-panel outputs visible | Model family | Provider | Human reviewer ID |
|---|---|---|---|---|---|---|---|---|
| Journal-Fit Reviewer (`1_venue_fit_review.md`) | EIC | AI subagent | fresh subagent run on Sonnet, launched concurrently with the other four seats by an Opus orchestrator | no (instructed not to read other seats' or panels' outputs) | no (instructed; compliance not independently confirmed) | single shared family | single shared provider | none |
| Reviewer 1, Methodology (`2_methodology_review.md`) | R1 | AI subagent | same | no (instructed) | no (instructed) | same | same | none |
| Reviewer 2, Domain (`3_domain_review.md`) | R2 | AI subagent | same | no (instructed) | no (instructed) | same | same | none |
| Reviewer 3, Perspective (`4_perspective_review.md`) | R3 | AI subagent | same | no (instructed) | no (instructed) | same | same | none |
| Devil's Advocate (`5_devils_advocate_review.md`) | DA | AI subagent | same | no (instructed) | no (instructed) | same | same | none |

The editorial synthesizer (this Phase 2 run) read all five cards, the round-3 decision package (`reviews/2026-10-14-cvpr-panel/0_editorial_decision_and_roadmap.md`, including its closing "Status after the round-3 revision" table) and provenance file, the manuscript text dumps (`paper_text.txt`, `supp_text.txt`), and parts of `results/*.json`, `data/vg_motifs/wager_penet/summary.json` and the experiment scripts `experiments/colab_sgg_rank.py`, `experiments/expand_penet_to_standard.py`, `experiments/run_sgg_penet_audit.py` and `experiments/colab_penet_stage2.py`. It is not a sixth reviewer and produced no new review comments beyond the verification of seat claims. It is an AI subagent whose runtime identifies it as Sonnet-family, so it shares the seats' model family and provider.

## Axes

| Provenance axis | Status | Basis |
|---|---|---|
| Role-separated | true | five distinct role definitions, one card per role |
| Within-panel invocation-context separation (`fresh_context`, scope `within_panel_attempt_only`) | true | dispatcher: each seat was a fresh subagent run, launched concurrently; says nothing about retries or earlier panels |
| Blind to peer outputs | true (as instructed) | dispatcher: each seat was instructed not to read other seats' outputs; the synthesizer cannot confirm compliance beyond the cards not citing each other |
| Prior-panel isolation | instructed, not verified | dispatcher: each seat was instructed not to read other panels' outputs; the cards do not cite the round-3 panel, but several raise the same themes (cross-release floor, control grid, TDE AUC bounds, grouping dependence), so the instruction cannot be confirmed from the text. R1 states it did not inspect history because it was told not to |
| Model-family distinct | **false** | all five seats ran on one model family (Sonnet) |
| Provider distinct | **false** | single provider |
| Human-reviewer distinct | false | no human reviewer sat on the panel; the accountable human did not author any card |

- **Fresh-context scope**: `within_panel_attempt_only`. It does not compare this panel with the round-3 panel (2026-10-14, commit `6b8f1b9`), the round-2 panel (2026-10-13b, commit `2da86a9`), the round-1 panel (2026-10-13, commit `18a72c9`) or with any retry.
- **Binary independence claim**: not computed. Role separation and blindness do not make five same-family seats independent.
- **Correlated-error disclosure**: all five seats share one model family and one provider, so they can share blind spots, wording habits and the same mistakes. Agreement among the seats is weaker evidence than agreement among independent reviewers. In this panel that matters most for findings repeated from the same manuscript passage (the abstract's cross-release floor sentence, the grouping range, the single K = 50 control), where repetition may reflect a shared reading rather than separate confirmation. The synthesizer's arbitration is by the same family and carries the same limitation. The factual claims that decide the outcome were therefore rechecked against `results/*.json`, the committed arrays, the experiment scripts and the text extracts rather than taken on agreement (see the decision letter, section "Verification"). Claims that could not be rechecked are listed there and marked [UNVERIFIED] in the roadmap where they are used.

## Dispatch facts as stated by the orchestrator

- Orchestrator: Opus. Phase 1 seats: Sonnet, five AI subagents launched concurrently, each instructed not to read other panels' or seats' outputs.
- Cross-model decision check (`ARS_CROSS_MODEL`): not run. No `[CROSS-MODEL-HANDOFF v1]` envelope was emitted and no cross-family comparison exists, so none is claimed.
- No cross-family aggregate and no same-model majority is computed anywhere in the decision package. Seat recommendations are reported in a table and were not counted as votes.
- External lookup: none by the synthesizer in this round. Reference leads in the cards are reported with the seats' own verification labels (VERIFIED or UNVERIFIED as each seat wrote them); the synthesizer did not check them.
- Local computation by the synthesizer: read-only checks of `results/*.json` (the PE-Net no-`rel_nms` replay, the AUC label-weighting and cross-release-floor files, the PE-Net and baseline recall splits, the background-mass table), the keys of `variant_penet.npz`, the experiment scripts named above, the text extracts, and short Python arithmetic on stored values (ratios, differences). No checkpoint was rerun and no prediction array was re-scored in this round. No repository file other than the two deliverables was modified; nothing was committed.

## Seat-reported checkout and tooling

- **R1 checkout**: R1 reported that its checked-out HEAD was `2300e8e`, not the requested `ea0efe7`, with a clean working tree, and that it did not inspect history, so it recorded the identity of the two as NOT VERIFIED. The dispatcher gave no explanation for this and the discrepancy is **unexplained by the dispatch record**. For the record, a read of the repository history by the synthesizer shows that `2300e8e` is a descendant of `ea0efe7` whose diff against it adds only `reviews/2026-10-28-cvpr-panel/paper_text.txt` and `supp_text.txt`, and that no file outside `reviews/` differs between `ea0efe7` and the synthesizer's own HEAD. That is the synthesizer's reading of history, not a statement from the dispatcher, and it does not establish which tree R1 actually viewed; no R1 finding depends on a difference between the two, as far as the card shows.
- **EIC**: executed `experiments/verify_manuscript_numbers.py` ("all 89 manuscript numbers trace to committed results"); viewed pages 1 and 6 of `paper.pdf`; did not inspect the code archive or re-derive proofs. Not rerun by the synthesizer.
- **R1**: wrote its own reimplementation of Eq. 4-7 and the within-cell AUC and ran it on the shipped arrays (scripts under the session scratchpad; not in the repository); ran `tests/` (40 passed); did not rerun the official-evaluator replay, matched proper-score splits, simulations or the Waterbirds and CIFAR studies. Its recomputation table agrees with the synthesizer's spot checks of the stored JSON; its jackknife, argmax-only proxy and multi-hit rate were not repeated.
- **R2**: read stored JSON and scripts, no code run (no torch).
- **R3**: read `paper_text.txt` fully and `supp_text.txt` selectively; no code run; web search for four references.
- **DA**: spot checks against `results/*.json`; searched but did not read `supp_text.txt` in full.

## Known limits of this panel

1. Same-family panel (above). A different-family or human panel could disagree.
2. `NOT_CALIBRATED`: no seat has been measured against known outcomes.
3. No venue binding: statements about CVPR in the cards are a configured perspective, not a venue-alignment determination.
4. Seats and the synthesizer could not re-run released checkpoints. Only quantities recoverable from committed `results/*.json`, `data/` and the manuscript were checked. Several seat claims were not repeated by the synthesizer and are marked [UNVERIFIED] where used: R1's jackknife widening, argmax-only proxy and multi-hit rate, R1's head-head subgroup and zero-shot subset weight, R2's reading of the SGDet matched-pair choice and of the chunked NMS self-test, R2's premise that the TDE-release evaluator has no `rel_nms`, and R3's Waterbirds matched value.
5. The cross-release floor is one realised difference between two trained networks from two releases; it is not an estimate of run-to-run variance and the decision letter says so.
6. Seats reviewed commit `ea0efe7` (R1 reports a checkout at `2300e8e`, above); later edits are not reviewed.
7. The round-3 letter said arXiv:2308.05286 should not be cited (withdrawn per R2); round-4 R2 recommends it as verified. Not reconciled here; marked [UNVERIFIED] in the roadmap.
