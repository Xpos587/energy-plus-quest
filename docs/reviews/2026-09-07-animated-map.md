# Animated carrier map: r24 release review

## Release status

**Parent-reviewed release candidate.** r23 equal-access inspection resolves the
short-phone crew-detail limit; r24 replaces open-cockpit inspection models with
enclosed cabs, roofs, glazing and doors. Parent review passed this specific
visual gate and authorized publication. This is not external/client approval
of the truck illustration style. Deployment evidence is retained in `r24-live/`.

## Sources and scope

- September 4 meeting, 17:23-18:00: trucks must move; 18:07-20:57: condition,
  distance, pace and crew are visual information for the decision.
- September 4 meeting, 19:27-19:55: high view, comparable routes, no disappearing
  trucks. Modern city/distribution centre, not an isolated racetrack.
- September 7 meeting, 08:10-08:26: label `Склад`; 09:09-10:49: distinct old
  smoking trucks, slow nearby truck, clean two-driver truck on a wide perimeter.
- Original scene scenario and `docs/plans/2026-09-07-outcome-truck-scenario.md`.
- The user preferred the lower image of `r18-art-assisted/art-contact.jpg`.
  r19 preserves that mobile master and outpaints the same location for desktop.
- r21 corrects the r19/r20 camera projection and routes against actual city
  pixels. Its 64-second loop, rather than the provisional 16 seconds, was
  explicitly approved to keep the warehouse truck slow.

Outcome/PPE artwork, carrier identity (`old` versus `old4`), consequences,
scores, profile-first entry and disabled later scenes are unchanged.

## Integrated media

Archive root:
`/home/michael/.local/state/energy-plus-quest/production/2026-09-05-scene-01/`.

Final video render source: `r23-map-inspection/compose.py`; 3D orientation atlases and
immutable city bases are inherited from `r21-fixed-truck-projection/`.

| Format | Size | Duration | Frames | Runtime file |
| --- | --- | --- | --- | --- |
| Mobile | 720 x 1024 | 64 seconds | 1152 at 18 fps | `design/scene-01/assets/current/map/carrier-mobile.mp4` |
| Desktop | 1280 x 724 | 64 seconds | 1152 at 18 fps | `design/scene-01/assets/current/map/carrier-desktop.mp4` |

Each local H.264 video has no audio and has a matching lossless WebP poster.
Vehicles, articulated trailers, shadows and smoke are authored into one frame.
There are no runtime truck sprites. r23 replaces baked numbers with accessible
HTML markers synchronized to the decoded video clock.

- No.1: worn blue truck, distant lower-left block, four laps.
- No.2: modern blue truck around the warehouse, one lap, slowest.
- No.3: clean turquoise truck, two modeled seated figures, wide perimeter,
  two laps, fastest.
- No.4: different ochre long-bonnet truck, distant lower-right block, three laps.

The r22 change enlarges the panoramic cab of No.3 by 28%; the trailer, route,
other vehicles and city remain unchanged. Whole-truck enlargement trials were
rejected for road/turn/collision violations. A 30% cab increase failed the strict
sub-frame desktop road envelope; 28% passed. Rejected trial scripts/fit results
in the archive are not the final render source.

## Runtime layout and accessibility

- Native-aspect fitted map card: the card, not the image inside a mismatched
  plane, fits available space. Exterior space uses the established page surface;
  there is no repeated/blurred background. This exception was approved to avoid
  cropping moving trucks. Full-bleed outcome screens are unaffected.
- Mobile uses one row of four choices; automatic selection remains separate.
  Playback is an accessible icon in the mobile heading, outside the artwork.
- DOM keyboard order remains Back, four numbered choices, automatic selection,
  playback. Playback is portalled into the existing mission panel.
- Paused/reduced-motion/error states show the descriptive fallback. During
  playback it remains available through the map's accessible description, not
  as a text substitute over the vehicles.
- Only the active format loads. Reduced motion does not request video. Existing
  pause/resume, autoplay retry, stale-promise, visibility and media-error handling
  are retained.
- Warehouse anchor is calibrated to the same pixel plane as the video:
  mobile approximately (350,314), desktop (626,185).

## Evidence

In `r22-crew-readability/`:

- `swept-verification.json`: 4608 quarter-frame swept intervals per format;
  zero collisions, road violations or viewport violations. Loop shape error is
  below 1e-9 pixels. These checks include full cab/mirror/trailer polygons.
- `output-verification.json`: actual final file decoding, 1152 frames, 64 seconds,
  expected sizes, no audio, label bounds, loop seam displacement and hashes.
- `runtime-verification/two-cycles.json`: actual browser playback at normal speed
  through two full 64-second loops at 320x568, 390x844, 440x956, 1440x900,
  2560x1440 and 844x390. Frames at 0/16/32/48 seconds and after two loops are
  captured directly from the integrated runtime, not from stale previews.
- Browser tests check the real native dimensions/duration, fitted media geometry,
  whole-cycle moving bounds against controls and viewport, pickup alignment,
  pause/resume/failure behavior, and two complete decoded loop boundaries.
- The ZIP verifier now waits for actual video playback and checks the fitted
  full media plane before continuing the route, with network access blocked.

Final checks: Vitest 16 passed; Playwright 167 passed / 29 intentionally skipped;
`npm run check` passed with existing repository warnings; rebuilt standalone ZIP
passed the extracted-runtime verifier across all 12 profiles. No files staged.

## Historical r22 visual gate (resolved by r23/r24)

At 390x844 the map is approximately 380x541 CSS pixels. At 320x568 it is only
about 171x243 after the required header and controls. The small phone's baked
numerals, worn condition and especially two distinct adult drivers are not
reliably readable. Landscape-phone trucks are also very small. Technical tests
cannot override this finding. A further composition or explicitly approved
inspection/zoom interaction is required before claiming full scenario delivery.

## r23: Approved Equal-Access Vehicle Inspection

The parent explicitly approved inspection to resolve the physical small-phone
limit, without changing outcomes, scores, the city, routes or vehicle identity.
The overview still cannot show facial detail at 320x568; it is not claimed to.

- All four trucks now have identical interactive orange numbers with 18px white
  type and 44px touch targets. At close junctions the targets separate, with
  leader lines retaining the actual vehicle anchors. Positions use the decoded
  video's `currentTime`, 18fps production tracks, loop interpolation and
  `requestVideoFrameCallback` (RAF fallback), not an independent animation clock.
- The 64-second whole-scene videos and posters were re-exported without baked
  numbers. DOM elements are number controls only, not animated truck sprites.
- Each number opens the same native modal dialog with a fresh 900x640 vehicle
  render from the production Blender models. The camera is closer and oblique;
  these are not enlargements of tiny video pixels. All four use the same camera,
  lighting and inspection controls. The two seated faces/shoulders in №3, the
  blue/ochre worn identities and exhaust in №1/№4, and blue №2 are visible.
- Visible captions are only the number. Accessible image descriptions and the
  existing paused/reduced-motion/error fallback describe the visual information.
  Inspection never chooses a carrier or awards points. Escape/Close restores
  focus; native dialog supplies focus containment. The original five choices
  and Back remain unchanged, preceding inspection targets in keyboard order.

Archive: `r23-map-inspection/` under the established production archive contains
`render_details.py`, `compose.py`, the full-size PNGs, bare video/poster outputs,
production track exports and runtime screenshots. No generation service was used.

Validation: 17 unit tests passed, including all 1152 decoded frames in both
formats for separated target bounds at small-phone sizes. Playwright: 173 passed,
29 intentional skips. New tests exercise seek-following, all four image decoding,
keyboard opening/Escape/focus restoration, no accidental selection, reduced
motion and dialog control visibility at 320x568 and 844x390. Static ZIP verification
passed across 12 profiles; check passes with existing repository warnings.

The large views remain stylized production-model illustrations, not photographic
vehicles. Visual approval is still owned by the parent. No commit or deployment
was performed by this worker.

## r24 enclosed-cab release gate

Four inspection WebPs now use enclosed recognizable cabs with roofs, glazing,
doors and visible occupants; No.3 has two seated occupants. Parent reviewed
`r24-enclosed-cabs/contact-sheet.jpg` and passed the specific roof/glass/crew
gate. Whole-city overview remains intentionally small on short phones; all four
vehicles have equal-access inspection, not a privileged hint for No.3.

Final release rerun: 17 unit tests passed; 173 browser tests passed with 29
intentional skips. Outcome/PPE source assets are byte-identical to HEAD r16.
Standalone ZIP is rebuilt and its extracted runtime verified before publication.
