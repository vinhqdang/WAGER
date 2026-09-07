# Panel provenance — 2026-09-07 review pass

Recorded per the `academic-paper-reviewer` Iron Rule #2. **Role separation is not
independence.** All five Phase 1 seats were served by the same model family and provider,
so their errors are correlated by construction. Nothing below should be read as five
independent judgements.

| field | value |
|---|---|
| skill | `academic-paper-reviewer` v1.11.1, mode `full` |
| review target | `manuscript/main.pdf` at commit `ba220dd` (52 pp., built 2026-09-07) |
| Phase 0 | field analysis and card configuration performed by the orchestrating session, not delegated |
| Phase 1 seats | 5 (Journal-Fit `EIC`, Methodology `R1`, Domain `R2`, Perspective `R3`, Devil's Advocate `DA`) |
| role separation | actual — each seat received a distinct configured identity and a distinct task brief |
| invocation-context freshness | fresh per seat; each seat launched in its own context with no conversation history |
| peer-output visibility | none before commitment; the five seats ran concurrently and no seat's brief contained another seat's output |
| cross-seat context comparison | not performed by tooling; freshness is asserted from the launch pattern, not verified |
| model family / provider | single family, single provider, shared with the orchestrating session |
| accountable human | Quang-Vinh Dang (British University Vietnam) |
| calibration status | `NOT_CALIBRATED` — no measured decision-error profile is applied to these severities |
| criteria binding | `criteria_binding_unavailable` — no author-confirmed `ReviewTargetContext` was supplied, so **no venue-alignment claim is made**; the Journal-Fit seat's remarks about *Econometrics and Statistics* are a configured perspective, not a fit determination |

## Phase 0 configuration card

Determined from the manuscript's own content: primary discipline mathematical
statistics (score decomposition, U-statistic inference); secondary discipline
machine-learning evaluation; paradigm methodological with empirical validation;
maturity fifth revision after four rejections.

| seat | configured identity |
|---|---|
| Journal-Fit (`EIC`) | associate editor, comparative predictive ability / forecast evaluation |
| R1 Methodology | U-statistics, influence-function and cluster-robust inference, randomization tests |
| R2 Domain | proper scoring rules and forecast verification (Murphy / DeGroot–Fienberg / Bröcker / Gneiting lineage) |
| R3 Perspective | ML benchmark methodology; deliberate non-specialist in the paper's apparatus |
| DA | fixed seat, no configuration card |

## Read-only constraint

Iron Rule #6 was enforced in each brief: no seat was permitted to modify anything under
the repository, and each wrote only its own report plus scratch files outside it. Any
manuscript change arising from this panel is made by the author, after synthesis, as a
separate act.
