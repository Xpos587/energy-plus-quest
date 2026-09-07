# Outcome trucks: original-scenario alignment

## Scope and source authority

User instruction, 7 September: change outcome trucks; keep the current map and every truck on it untouched. A complete map redesign is deferred to a later task. Trucks 1 and 4 must be visually different.

Read the original 23 July first-scene draft in `materials/project/`, the 4 September meeting transcript, and sections 13.5 and 14 of `docs/specs/2026-09-04-review-feedback-revision.md`.

The original draft's six-truck sentence is inconsistent with its four described numbered choices. Its driverless-column illustration conflicts with the explicit two-driver crew. Preserve the later four-choice interpretation and two adult drivers; do not introduce driverless vehicles or restore the removed intro.

## Art contract

| Choice | Outcome illustration | Preserve |
| --- | --- | --- |
| 1 | Faded-blue old cab, visibly dated shape and moderate wear, light exhaust; traffic-police officer checks the driver's documents at a safe roadside stop | Operable vehicle, one-week delay, 0/-3/-3 |
| 4 | A different old ochre/mustard truck, different cab silhouette and lamps, moderate wear and light exhaust; a distinct view of a document check | Same consequence and score as 1, separate selected identity and media |
| 2 | Modern working blue semi; unhurried driver eats at an outdoor cafe with feet up while the vehicle is safely parked nearby | Delay caused by the driver, not a breakdown or traffic jam; forecast copy and +1/0/-2 |
| 3 | Clean, shiny turquoise modern semi and two adult drivers changing shifts | Correct cabin door, earlier arrival and higher cost, -3/+3/+4 |
| Express | No change in this revision | Modern truck, two drivers, existing copy and -1/+5/+5 |

Keep established illustration style, early autumn, readable people and full-size semitrailers. Wear applies only to old trucks, not to the whole city. No wrecks, drunken caricature, dangerous behavior, fictional logos or new UI.

## Implementation and acceptance

1. Produce mobile masters, then wide expansions from those same masters. Reject hard rectangular source-paste seams and independently redrawn desktop scenes.
2. Retain `old` for choice 1; add `old4` for choice 4 with shared outcome copy and scoring but distinct media. Preserve all Back/reset behavior.
3. Verify image identity and scoring for both old choices, all responsive routes, current full-bleed media and rounded internal panels.
4. Compare checksums of both map assets and `src/components/CityMap.tsx` before and after; they must match.
5. Rebuild the standalone ZIP and committed static runtime, deploy through Dokploy, and verify the public release.

## Meeting added during implementation

The 7 September recording was transcribed without inspecting its video frames. See `materials/meeting/2026-09-07/summary.md` for the timestamped decision analysis and `transcript.txt` for raw ASR text. It confirms old/smoking trucks, the unhurried cafe driver, and the two-driver crew. The meeting changes its animation/show order near the end; the user's later explicit map freeze controls this revision. The warehouse label and white pocket logos are recorded as separate pending work, not silently implemented here.

## Deferred map redesign

Do not implement now: original scenario calls for old trucks 1 and 4 on different routes and at different speeds, very slow truck 2 near the office, and shiny two-driver truck 3 on a wide block perimeter. Use these as the starting contract when the user explicitly starts the full map redesign.
