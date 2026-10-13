# Review Panel Provenance (#540/#740)

Panel: simulated CVPR 2027 review panel, skill `academic-paper-reviewer` v1.11.1, mode `full`.
Review target: `cvpr2027/paper.pdf` + `cvpr2027/supp.pdf` at repository commit `18a72c9`.
Panel date: 2026-10-13. Review round: 1.
Accountable human: Quang-Vinh Dang (British University Vietnam).

## Status of this record

This file is a hand-written provenance statement from the Phase 2 synthesizer, built from what the dispatching instruction said. It is not a replay-valid `review-panel-provenance/1.0` artifact: no typed artifact, artifact SHA-256, normalized-manifest digest or execution-topology digest was supplied to the synthesizer, so none is reported and none is invented. Every axis below is therefore stated as reported by the dispatcher, with the basis shown, and any axis the dispatcher did not state is `unknown`.

- `calibration_status: NOT_CALIBRATED` (package level and for every seat)
- `criteria_binding_unavailable`: no #684 criteria authority or author-confirmed target context was supplied. All five cards disclose this. No venue-alignment claim is made anywhere in the panel output.

## Seats

| Seat | Role ID | Actor type | Execution | Peer outputs visible | Prior-panel outputs visible | Model family | Provider | Human reviewer ID |
|---|---|---|---|---|---|---|---|---|
| Journal-Fit Reviewer (`1_venue_fit_review.md`) | EIC | AI subagent | fresh subagent run on Sonnet, launched concurrently by an Opus orchestrator | no | no | single shared family | single shared provider | none |
| Reviewer 1, Methodology (`2_methodology_review.md`) | R1 | AI subagent | same | no | no | same | same | none |
| Reviewer 2, Domain (`3_domain_review.md`) | R2 | AI subagent | same | no | no | same | same | none |
| Reviewer 3, Perspective (`4_perspective_review.md`) | R3 | AI subagent | same | no | no | same | same | none |
| Devil's Advocate (`5_devils_advocate_review.md`) | DA | AI subagent | same | no | no | same | same | none |

The editorial synthesizer (this Phase 2 run) read all five cards and the manuscript text dumps. It is not a sixth reviewer and produced no new review comments.

## Axes

| Provenance axis | Status | Basis |
|---|---|---|
| Role-separated | true | five distinct role definitions, one card per role |
| Within-panel invocation-context separation (`fresh_context`, scope `within_panel_attempt_only`) | true | each seat was a fresh subagent run; says nothing about retries or earlier panels |
| Blind to peer outputs | true | dispatcher: no peer visibility during Phase 1 |
| Model-family distinct | **false** | all five seats ran on one model family (Sonnet) |
| Provider distinct | **false** | single provider |
| Human-reviewer distinct | false | no human reviewer sat on the panel; the accountable human did not author any card |

- **Fresh-context scope**: `within_panel_attempt_only`. It does not compare this panel with the 2026-10-05 panel or with any retry.
- **Prior-panel isolation**: seats and the synthesizer were instructed not to read earlier panels under `reviews/`, `report/`, `submission_notes/` or the git log. Phase 0 configuration cards were carried over unchanged from the 2026-10-05 panel. That is configuration (seat definitions), not review content.
- **Binary independence claim**: not computed. Role separation and blindness do not make five same-family seats independent.
- **Correlated-error disclosure**: all five seats share one model family and one provider, so they can share blind spots, wording habits and the same mistakes. Agreement among the seats is weaker evidence than agreement among independent reviewers. In this panel that matters most for findings that several seats repeated from the same manuscript passage (for example the abstract wording and the equivalence margin), where repetition may reflect a shared reading rather than separate confirmation. The synthesizer's own arbitration is by the same family and carries the same limitation. The factual claims that decide the outcome were therefore recomputed from `results/*.json` and `data/` rather than taken on agreement (see the decision letter, section "Verification").

## Dispatch facts as stated by the orchestrator

- Orchestrator: Opus. Phase 1 seats: Sonnet, five fresh subagents, launched concurrently.
- Phase 0 cards: carried over unchanged from the 2026-10-05 panel.
- Cross-model decision check (`ARS_CROSS_MODEL`): not run. No `[CROSS-MODEL-HANDOFF v1]` envelope was emitted and no cross-family comparison exists, so none is claimed.
- No cross-family aggregate and no same-model majority is computed anywhere in the decision package.

## Known limits of this panel

1. Same-family panel (above). A different-family or human panel could disagree.
2. `NOT_CALIBRATED`: no seat has been measured against known outcomes.
3. No venue binding: statements about CVPR in the cards are a configured perspective, not a venue-alignment determination.
4. Seats could not re-run released checkpoints. Only quantities recoverable from committed `results/*.json`, `data/` and the manuscript were recomputed.
