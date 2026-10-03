# Panel provenance — 2026-10-03 CVPR review pass

Recorded per the `academic-paper-reviewer` Iron Rule #2. **Role separation is not
independence.** All five Phase 1 seats were served by the same model family and provider as
the orchestrating session, so their errors are correlated by construction. Nothing below
should be read as five independent judgements.

| field | value |
|---|---|
| skill | `academic-paper-reviewer` v1.11.1, mode `full` |
| review target | `cvpr2027/paper.pdf` (8 pp.) and `cvpr2027/supp.pdf` (23 pp.) at commit `d227e40`, built 2026-10-03 |
| target venue | CVPR 2027 main conference; deadline 16 November 2026 |
| Phase 0 | field analysis and card configuration performed by the orchestrating session, not delegated |
| Phase 1 seats | 5 (Venue-fit `EIC`, Methodology `R1`, Domain `R2`, Perspective `R3`, Devil's Advocate `DA`) |
| role separation | actual — each seat received a distinct configured identity, its own role-definition file from the skill, and a distinct brief |
| invocation-context freshness | fresh per seat; each launched as a separate subagent with no conversation history |
| peer-output visibility | none before commitment; all five launched concurrently in one dispatch, each brief forbade opening other seats' reports. The Domain seat reported seeing another report's filename in the directory listing and not opening it |
| prior-panel visibility | none; each brief forbade reading earlier panels and the project report |
| cross-seat context comparison | not performed by tooling; freshness is asserted from the launch pattern, not verified |
| model family / provider | single family, single provider, shared with the orchestrating session |
| accountable human | Quang-Vinh Dang (British University Vietnam) |
| calibration status | `NOT_CALIBRATED` |
| criteria binding | `criteria_binding_unavailable` — no author-confirmed `ReviewTargetContext`; the CVPR remarks are a configured perspective, **not a venue-alignment determination** |

## Phase 0 configuration card

Primary discipline: computer vision, evaluation methodology for scene graph generation.
Secondary: statistical evaluation (proper scores, U-statistics). Paradigm: evaluation
methodology with empirical audit. Maturity: complete draft; sixth venue attempt and first in
conference format.

| seat | configured identity |
|---|---|
| Venue-fit (`EIC`) | CVPR area chair, scene understanding and evaluation |
| R1 Methodology | evaluation statistics for vision: calibration, proper scores, uncertainty on benchmark metrics |
| R2 Domain | scene graph generation specialist; unbiased-SGG literature and metrics |
| R3 Perspective | ML evaluation science outside SGG: long-tail, VQA bias, shortcut learning |
| DA | fixed seat, no configuration card |

## Read-only constraint

Iron Rule #6 was enforced in each brief. No seat modified the manuscript; each wrote only its
own report. Any change arising from this panel is made after synthesis, as a separate act.

## Synthesiser verification

Before adjudicating, the synthesiser re-verified six factual claims against primary sources
rather than accepting them from the reports: the released TDE predictor code (upstream
`roi_relation_predictors.py`), the committed results file, and the estimator itself.
Details are in `0_editorial_decision_and_roadmap.md`.
