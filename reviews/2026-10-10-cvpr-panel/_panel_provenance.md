# Panel Provenance

- **Panel date**: 2026-10-10
- **Skill**: academic-paper-reviewer v1.11.1 (research-skills bundle 3.23.0), mode `full`, Phase 1 (five seats) and Phase 2 (editorial synthesis)
- **Review target**: anonymous CVPR 2027 submission `cvpr2027/paper.pdf` (+ `supp.pdf`), repository commit `9dad949`. The panel read text dumps `paper_text.txt` and `supp_text.txt` from that version. Later working-tree edits were not reviewed.
- **Venue configuration**: simulated CVPR 2027 perspective only (see `criteria_binding_unavailable` below)
- **Phase 0 cards**: carried over unchanged from 2026-10-05; not regenerated for this panel
- **Accountable human**: Quang-Vinh Dang (British University Vietnam)

## Seat roster and execution record

| Seat | Role ID | Actor type | Execution | Peer outputs visible | Prior-panel material visible | Model family | Provider |
|---|---|---|---|---|---|---|---|
| EIC / Journal-Fit | `1_venue_fit_review` | AI subagent | fresh subagent for this seat, launched concurrently | No | No | same single family as orchestrator | same single provider as orchestrator |
| R1 Methodology | `2_methodology_review` | AI subagent | fresh subagent, concurrent | No | No | same | same |
| R2 Domain | `3_domain_review` | AI subagent | fresh subagent, concurrent | No | No | same | same |
| R3 Perspective | `4_perspective_review` | AI subagent | fresh subagent, concurrent | No | No | same | same |
| Devil's Advocate | `5_devils_advocate_review` | AI subagent | fresh subagent, concurrent | No | No | same | same |
| Editorial synthesizer (Phase 2) | `0_editorial_decision_and_roadmap` | AI subagent | separate Phase 2 subagent; read the five Phase 1 reports and manuscript text only, with no earlier panel, report, submission-notes or git-log material | n/a (reads all five by design) | No | same | same |

The exact model identifier is held by the orchestrator and is not restated in the seat cards. No seat card names a model.

## Provenance axes (orchestrator-attested)

| Axis | Status | Basis |
|---|---|---|
| Role-separated | `true` | Five distinct role definitions and report formats. |
| Within-panel invocation-context separation (`fresh_context`; scope `within_panel_attempt_only`) | `true` | One fresh subagent per seat for this panel attempt. This does not compare against any retry or earlier round. |
| Blind to peer outputs | `true` | No seat saw another seat's output before submitting. The synthesizer reads all five by design. |
| Model-family distinct | `false` | All five seats and the orchestrator share one model family. |
| Provider distinct | `false` | All five seats and the orchestrator share one provider. |
| Human-reviewer distinct | `false` | No human reviewer sat on the panel. |

- **Binary independence claim**: not computed and not made. Role separation proves only `role_separated`.
- **Correlated-error disclosure** (required, because the model-family axis is `false`): the seats share one model family, so errors the family makes systematically (for example the same misreading of a table, or the same literature blind spot) can recur across seats and read as agreement. Agreement among the seats is not independent confirmation. The editorial synthesis therefore rested its key factual checks on read-only recomputation from `results/*.json`, not on seat agreement.
- **Typed provenance artifact**: none was produced and no replay validation or digest verification was run. The axis values above are attested by the orchestrator, not machine-verified. A strict reading of the carrier protocol would render all six axes `unknown` until such an artifact exists. Do not treat this file as a validated `review-panel-provenance/1.0` artifact.

## Calibration and criteria binding

- `calibration_status: NOT_CALIBRATED` for every seat and for the editorial package. No closed profile artifact or replay validator exists, so no seat's confidence scores are empirically calibrated. Confidence values are self-reported scope disclosures and carried no decision weight.
- `criteria_binding_unavailable`: no author-confirmed target context was supplied to any seat. No seat or the synthesizer makes a venue-alignment claim, and CVPR remarks are a configured perspective.

## Constraints observed

- No seat or the synthesizer read earlier panels under `reviews/`, `report/`, `submission_notes/` or the git log.
- The synthesizer modified only `0_editorial_decision_and_roadmap.md` and this file. Phase 1 reports and the text dumps were not changed.
- The synthesizer recomputed eight headline facts read-only from `results/*.json` (V1 to V8 in the decision letter) and left the remainder as seat-reported.
- No cross-model blind decision check was run, and no sprint contract was bound.
- No git commit or push was made.
