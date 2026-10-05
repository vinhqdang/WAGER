# Panel provenance — 2026-10-05 CVPR review pass

Recorded per the `academic-paper-reviewer` Iron Rule #2. **Role separation is not
independence.** All five Phase 1 seats were served by the same model family and provider as
the orchestrating session, so their errors are correlated by construction. Nothing below
should be read as five independent judgements.

| field | value |
|---|---|
| skill | `academic-paper-reviewer` v1.11.1, mode `full` |
| review target | `cvpr2027/paper.pdf` (8 pp. + references) and `cvpr2027/supp.pdf` (31 pp.) at commit `909e5a3`, built 2026-10-05 |
| target venue | CVPR 2027 main conference; deadline 16 November 2026 |
| Phase 0 | configuration cards carried over unchanged from the 2026-10-03 panel, so that ratings are comparable across the two passes (yardstick continuity); not re-derived |
| Phase 1 seats | 5 (Venue-fit `EIC`, Methodology `R1`, Domain `R2`, Perspective `R3`, Devil's Advocate `DA`) |
| role separation | actual — each seat received a distinct configured identity, its own role-definition file from the skill, and a distinct brief over a shared common brief |
| invocation-context freshness | fresh per seat; each launched as a separate subagent with no conversation history |
| peer-output visibility | none before commitment; all five launched concurrently in one dispatch; each brief forbade opening other seats' reports |
| prior-panel visibility | none; each brief forbade reading earlier panels, the project report, submission notes and the git log (which names the revision items) |
| cross-seat context comparison | not performed by tooling; freshness is asserted from the launch pattern, not verified |
| model family / provider | single family, single provider, shared with the orchestrating session |
| tool access | read access to the repository, including code, results files and cached model outputs; seats could run read-only Python to recompute claims |
| accountable human | Quang-Vinh Dang (British University Vietnam) |
| calibration status | `NOT_CALIBRATED` |
| criteria binding | `criteria_binding_unavailable` — no author-confirmed `ReviewTargetContext`; the CVPR remarks are a configured perspective, **not a venue-alignment determination** |

## Phase 0 configuration card (unchanged from 2026-10-03)

| seat | configured identity |
|---|---|
| Venue-fit (`EIC`) | CVPR area chair, scene understanding and evaluation |
| R1 Methodology | evaluation statistics for vision: calibration, proper scores, U-statistics, uncertainty on benchmark metrics |
| R2 Domain | scene graph generation specialist; unbiased-SGG literature, metrics and codebase; open-vocabulary SGG |
| R3 Perspective | ML evaluation science outside SGG: long-tail, VQA bias, shortcut learning, grouping loss, label shift |
| DA | fixed seat, no configuration card |

## Read-only constraint

Iron Rule #6 was enforced in each brief. Each seat could write only its own report file and
scratch files outside the repository. Any change arising from this panel is made after
synthesis, as a separate act.
