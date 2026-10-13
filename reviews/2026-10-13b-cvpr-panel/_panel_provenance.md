# Review Panel Provenance (#540/#740)

Panel: simulated CVPR 2027 review panel, skill `academic-paper-reviewer`, mode `full` (skill version not stated by the dispatcher).
Review target: `cvpr2027/paper.pdf` + `cvpr2027/supp.pdf` at repository commit `2da86a9`. A Table 2 rendering defect flagged by the EIC was fixed afterwards in commit `5d69361`; the seats read the pre-fix PDF.
Panel date: 2026-10-13. Review round: 2 (the seat cards label themselves "Round 1"; the round number here is the dispatcher's).
Accountable human: Quang-Vinh Dang (British University Vietnam).

## Status of this record

This file is a hand-written provenance statement from the Phase 2 synthesizer, built from what the dispatching instruction said. It is not a replay-valid `review-panel-provenance/1.0` artifact: no typed artifact, artifact SHA-256, normalized-manifest digest or execution-topology digest was supplied to the synthesizer, so none is reported and none is invented. Every axis below is therefore stated as reported by the dispatcher, with the basis shown, and any axis the dispatcher did not state is `unknown`.

- `calibration_status: NOT_CALIBRATED` (package level and for every seat)
- `criteria_binding_unavailable`: no #684 criteria authority or author-confirmed target context was supplied. All five cards disclose this. No venue-alignment claim is made anywhere in the panel output.

## Seats

| Seat | Role ID | Actor type | Execution | Peer outputs visible | Prior-panel outputs visible | Model family | Provider | Human reviewer ID |
|---|---|---|---|---|---|---|---|---|
| Journal-Fit Reviewer (`1_venue_fit_review.md`) | EIC | AI subagent | fresh subagent run on Sonnet, launched by an Opus orchestrator | no | unknown (not stated by the dispatcher) | single shared family | single shared provider | none |
| Reviewer 1, Methodology (`2_methodology_review.md`) | R1 | AI subagent | same | no | unknown | same | same | none |
| Reviewer 2, Domain (`3_domain_review.md`) | R2 | AI subagent | same | no | unknown | same | same | none |
| Reviewer 3, Perspective (`4_perspective_review.md`) | R3 | AI subagent | same | no | unknown | same | same | none |
| Devil's Advocate (`5_devils_advocate_review.md`) | DA | AI subagent | same | no | unknown | same | same | none |

The editorial synthesizer (this Phase 2 run) read all five cards, the manuscript text dumps (`paper_text.txt`, `supp_text.txt`), the round-1 decision package and provenance file, and parts of `results/*.json`. It is not a sixth reviewer and produced no new review comments. It is an AI subagent whose runtime identifies it as Sonnet-family, so it shares the seats' model family and provider.

## Axes

| Provenance axis | Status | Basis |
|---|---|---|
| Role-separated | true | five distinct role definitions, one card per role |
| Within-panel invocation-context separation (`fresh_context`, scope `within_panel_attempt_only`) | true | dispatcher: each seat was a fresh subagent run; says nothing about retries or earlier panels |
| Blind to peer outputs | true | dispatcher: no peer visibility during Phase 1 |
| Prior-panel isolation | unknown | the dispatcher did not say whether seats could read the round-1 panel; the cards do not cite it |
| Model-family distinct | **false** | all five seats ran on one model family (Sonnet) |
| Provider distinct | **false** | single provider |
| Human-reviewer distinct | false | no human reviewer sat on the panel; the accountable human did not author any card |

- **Fresh-context scope**: `within_panel_attempt_only`. It does not compare this panel with the round-1 panel (2026-10-13, commit `18a72c9`) or with any retry.
- **Binary independence claim**: not computed. Role separation and blindness do not make five same-family seats independent.
- **Correlated-error disclosure**: all five seats share one model family and one provider, so they can share blind spots, wording habits and the same mistakes. Agreement among the seats is weaker evidence than agreement among independent reviewers. In this panel that matters most for findings repeated from the same manuscript passage (for example the abstract's control sentence, the grouping range and the IETrans wording), where repetition may reflect a shared reading rather than separate confirmation. The synthesizer's arbitration is by the same family and carries the same limitation. The factual claims that decide the outcome were therefore rechecked against `results/*.json` and the text extracts rather than taken on agreement (see the decision letter, section "Verification"). Claims that could not be rechecked are listed there as not verified.

## Dispatch facts as stated by the orchestrator

- Orchestrator: Opus. Phase 1 seats: Sonnet, five AI subagents, no peer outputs visible to any seat.
- Cross-model decision check (`ARS_CROSS_MODEL`): not run. No `[CROSS-MODEL-HANDOFF v1]` envelope was emitted and no cross-family comparison exists, so none is claimed.
- No cross-family aggregate and no same-model majority is computed anywhere in the decision package.
- External lookup: one external source (arXiv 2503.17862) was fetched by the synthesizer to check a claim R2 marked [UNVERIFIED]; the result is reported in the decision letter, check (g), as partially verified. Other [UNVERIFIED] leads from R2 were not checked.

## Known limits of this panel

1. Same-family panel (above). A different-family or human panel could disagree.
2. `NOT_CALIBRATED`: no seat has been measured against known outcomes.
3. No venue binding: statements about CVPR in the cards are a configured perspective, not a venue-alignment determination.
4. Seats and the synthesizer could not re-run released checkpoints. Only quantities recoverable from committed `results/*.json`, `data/` and the manuscript were checked, and several seat recomputations (R1's alternative AUC weightings and jackknife SE, R3's CIFAR figures) were not repeated by the synthesizer.
5. Seats reviewed commit `2da86a9`; the Table 2 fix in `5d69361` was not re-reviewed.
