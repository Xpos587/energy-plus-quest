# Scene 01 current frontend review

The table below is a historical baseline, not the current frontend or an approval.

## Current: r08 mobile hierarchy

- Larger independent intro logos and white start-button text; existing header retained.
- Mobile map before controls; no result eyebrow; compact labeled metrics and one available return action instead of a competing disabled CTA.
- Current evidence: external `mobile-r08/`. 88 browser tests, 14 unit tests and eleven extracted-ZIP profiles pass; 16 intentional skips.
- Report: `docs/reviews/2026-09-06-responsive-repair.md`. No generation or publication.

## Historical: r07 header and media corners

- Restores numbered four-step progress from `52de707`, with visible labels on mobile and current-step tracking through Back.
- Stable responsive header; rounded image corners, selection thumbnails and scene contours.
- Current external evidence: `header-r07/`, with 21 production captures, historical source and verified ZIP. 14 unit tests, 77 browser tests and eleven ZIP profiles pass.
- Report: `docs/reviews/2026-09-06-responsive-repair.md`. No new generation or deployment.

## Historical: r06 prod composition

- Report: `docs/reviews/2026-09-06-responsive-repair.md`.
- Current evidence: external scene archive `composition-r06/`; 63 production captures, three desktop composition masters, exports, receipts and verified ZIP.
- Compact horizontal choices and centered panels replace the poster layout. Outcome panels overlay reserved quiet space on desktop; narrow results blend into a continuous navy surface.
- 14 unit tests, 66 browser tests and eleven extracted-ZIP checks pass. Carrier Back, current copy and native short-screen scrolling are retained.
- Current archive manifest and cover select r06. No external approval or deployment.

## Historical: r04 responsive repair

- Current report: `docs/reviews/2026-09-06-responsive-repair.md`.
- Current media, 63 full-page production captures and verification records: external scene archive `responsive-r04/`.
- Carrier Back is restored. Natural vertical scrolling replaces viewport locking; all choice/result images are contained without CSS cropping. Old/crew/express now have new desktop/mobile artwork.
- 14 unit tests, 50 browser tests and eleven extracted-ZIP checks pass. Prior no-vertical-scroll gates do not apply.
- The current ZIP and checksum retain their standard paths in `release/`.

## Historical: r03 meeting cleanup

- All eight audited gaps are corrected; report: `docs/reviews/2026-09-06-meeting-runtime-gap-audit.md`.
- Current browser evidence lives outside Git: archive `frontend-integration/captures-r03/` (27 captures) and `submission/ready-r03/` (18 selected captures). `submission/cover.md` and `manifest.json` select the current package.
- Current text uses `Хор`. No internal badges, intro eyebrow or choice-card arrow discs remain; the five delivery stages are shown throughout onboarding and the route.
- Both logo pairs share adaptive sizing. Body text is at least 21.333px, controls 16px and support text 14px; the primary CTA passes 4.5:1 contrast. Short-phone stage labels wrap without clipping.
- 14 unit tests and 45 browser tests pass; six duplicate exhaustive runs are intentionally skipped. Seven extracted-ZIP smoke checks also verify meeting cleanup.
- Current archive: `release/energy-plus-quest-static.zip`; checksum: `release/energy-plus-quest-static.zip.sha256`. The archived copy is `frontend-integration/energy-plus-quest-static-r03.zip`.
- No new media generation, external approval or deployment occurred in this correction.

## Historical Baseline

- Runtime asset root: `design/scene-01/assets/current/`
- Desktop viewport: `1440x900`
- Mobile viewport: `390x844`
- Capture mode: viewport only (`fullPage: false`)
- Latest implementation contract: [`docs/specs/2026-09-04-review-feedback-revision.md`](../../../docs/specs/2026-09-04-review-feedback-revision.md)
- Feedback coverage audit: [`docs/reviews/2026-09-04-feedback-coverage-audit.md`](../../../docs/reviews/2026-09-04-feedback-coverage-audit.md)
- Baseline visual audit: [`docs/reviews/2026-09-04-visual-style-review.md`](../../../docs/reviews/2026-09-04-visual-style-review.md)

| State | Desktop | Mobile |
| --- | --- | --- |
| Professional profile | [profile-desktop.png](profile-desktop.png) | [profile-mobile.png](profile-mobile.png) |
| Carrier map | [carrier-desktop.png](carrier-desktop.png) | [carrier-mobile.png](carrier-mobile.png) |
| `old` result | [outcome-old-desktop.png](outcome-old-desktop.png) | [outcome-old-mobile.png](outcome-old-mobile.png) |
| `near` result | [outcome-near-desktop.png](outcome-near-desktop.png) | [outcome-near-mobile.png](outcome-near-mobile.png) |
| `crew` result | [outcome-crew-desktop.png](outcome-crew-desktop.png) | [outcome-crew-mobile.png](outcome-crew-mobile.png) |
| `express` result | [outcome-express-desktop.png](outcome-express-desktop.png) | [outcome-express-mobile.png](outcome-express-mobile.png) |

These baseline images are retained unchanged. Use the current external archive listed above for review.

## 6 September: historical art-direction preparation

- Local archive: [/home/michael/.local/state/energy-plus-quest/production/2026-09-05-scene-01/](/home/michael/.local/state/energy-plus-quest/production/2026-09-05-scene-01/).
- Ready scope: **text-only**, `READY_FOR_ART_DIRECTION_REVIEW`; `copy/scene-01.md`, nine combinations in `copy/interpolations.md`, and `submission/cover.md`. Not submitted or approved.
- Working materials only: desktop/mobile map and near geometry blockouts, short-mobile crops, truck 02 reference, draft PPE preservation masks, source hashes and `manifest.json`. These are not finished artwork or browser captures.
- Full visual package remains blocked on further generation authorization; no corrected character masters, final map/near art, or motion are claimed. Runtime assets and baseline captures remain unchanged by this preparation.
- Subsequently authorized PPE test 01: one Nano Banana 2 reference-edit, 2 credits spent, **REJECT** for incorrect sleeve/trouser zoning and construction. Comparison: `characters/ppe-test-01/comparison.png` in the archive; receipt/verdict: `requests/ppe-test-01/`; test manifest: `manifest-ppe-test-01.json`. The local source-pixel preservation proof is not a corrected master. At that checkpoint the text-only package was unchanged and further generation was not authorized. This restriction was subsequently superseded by explicit user authorization.

## 6 September: actual static visual-r01 package

- Archive: `/home/michael/.local/state/energy-plus-quest/production/2026-09-05-scene-01/`; start with `submission/cover.md`, file hashes and provenance in `manifest.json`.
- `READY_FOR_ART_DIRECTION_REVIEW`, scope **visual direction**: six primary context/map/near PNGs, independent Russian copy, supplementary mobile/short-phone mockups and PPE details in `submission/visual-r01/`.
- Whole-person character corrections, separate desktop/mobile map and near masters are now present. Missing official markings, short-near production typography, equal action geometry and mobile crew readability remain explicitly open in the cover; motion and gameplay are not verified.
- Verified 28 indexed files, PNG dimensions/hashes and nine runtime text interpolations. Actual observed account difference: 97 credits including the initial test; no client submission or approval.
- Only this archive note changed the repository for that production pass. Runtime integration was subsequently authorized separately; see the next section.

## 6 September: integrated frontend preview

- Following the explicit request to fix the preview, the new character/map/near media are integrated into the existing React application, preserving its brand fonts, card treatments, panels and full first-scene route. This is no longer the separately drawn PNG interface.
- Run `bun run dev -- --host 127.0.0.1 --port 4173`. The build is also verified at `/specprojects/joydelivery/`; no public deployment or commit is performed.
- Carrier: five neutral, equal-size panel actions, noninteractive numbers, pickup label and logistics progress. Near: forecast copy, simple SVG metrics, no score tracks or repeated context, disabled continuation with an explanation. Returning from a result preserves personalization; the carrier map cannot return to gift selection.
- Six runtime WebPs are replaced from archived masters. Other outcomes retain their existing artwork; only mobile framing changes to keep the complete story above the panel. Source backups and export hashes: archive `frontend-integration/before/` and `frontend-integration/exports.json`.
- Validation: 14 unit tests, 30 browser tests across seven viewport configurations, production build and nested-path offline-resource smoke checks pass. `bun run check` exits successfully with existing CSS/symlink warnings.
- Actual browser captures (desktop/mobile/375x667, all first-scene screens and outcomes) are in archive `frontend-integration/captures/`. The older images linked in the baseline table above are not these new captures.
- Scope remains a working static first-scene preview, not a completed game or approved artwork. Official PPE markings and subsequent gameplay remain pending.

## Entire-plan completion, r02

- Execution report: `docs/reviews/2026-09-06-scene-01-plan-execution.md`; completed and conditional steps are tracked in the original art-direction plan.
- Current package: archive `submission/ready-r02/` and `submission/cover.md`. These are actual production browser captures, not the rejected Pillow UI. `manifest.json` selects 16 current files and distinguishes older/supporting artifacts.
- `release/energy-plus-quest-static.zip` is built and verified after unpacking at `/specprojects/joydelivery/`. Map sources now meet the full-resolution contract; UI crops their quiet margins. Global paper-noise is removed.
- Validation now includes 38 passing browser tests, 14 unit tests and seven production archive smoke checks. Six duplicate exhaustive-test instances are intentionally skipped; all nine personalization combinations × four outcomes run on 375×667.
- Task 7: one 22.5-credit motion prototype, **FAIL** for the loop discontinuity and truck 3 reaching the curb in frames 117–121. Source, numbered/H.264 samples, all 121 frames, tracks and `motion/verdict.md` are archived. No rejected video is loaded by the app; final video generation stops at this gate.
- Total observed media spend: 119.5 credits, remaining balance 880.5. No client submission, public deployment, commit or new push.
