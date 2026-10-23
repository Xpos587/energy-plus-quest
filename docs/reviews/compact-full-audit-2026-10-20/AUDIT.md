# Compact — full non-copy workboard audit, 20 October 2026

Authority: full Scene 2 section of
[workboard](../../plans/2026-10-16-scene-workboard.md), plus
[16 October meeting](../../../materials/meeting/2026-10-16-grisha/transcript.md).
Frozen runtime examined: `http://127.0.0.1:4344/`, root
`.tmp-work/grisha-demo-2026-10-19-stage`. Checkout is audited separately.
Initial evidence: `runtime-4344.json` and the matched `4344-*.png` captures,
1440×900 and 390×844 at DPR 2. No user browser storage was touched.

## Every non-copy requirement

| Workboard requirement | Initial status | Evidence / boundary |
| --- | --- | --- |
| Clicking illustration during description | Deferred by meeting | 35:34–36:14 explicitly ends with leaving it unchanged for now. Intro has no active hotspots; not an authorized regression fix. |
| Remove redundant intermediate descriptions; make zones the primary choice | Implemented in current flow | `ScenesGame` sends choice directly to result. `selectedId` is only passed to Compact art for the result; no intervening description/confirmation screen. |
| Auto confirmation must not zoom to an arbitrary place | Implemented by removing that intermediate step | No confirmation camera is invoked in the live choice flow. Auto result follows the actual canonical boat/camera/socks placement. |
| Places 2/3 must not zoom to place 4 | Implemented for current direct flow | Current flow bypasses inspection. Local inspection camera is calculated from the corresponding region; `compact-camera.test.tsx` covers all four and automatic/manual parity. |
| Cabin color must match selected carrier | Partial | Red/blue/green identities present; old4 is ochre/mustard in `4344-1440-yellow-choice.png`, while separate boat-3 art is bright yellow. Same hue-only cabin shape for every carrier. |
| Warehouse environment rather than empty space | Partial | Portrait and result sources show warehouse. Wide choice `loading-clean-belts-v26.png` still shows mostly sky and floor, unlike the portrait source. |
| Enlarge place 1 so the boat can plausibly fit | Partial / unresolved in choice | Result `boat-zone1-axle-v49.png` has an enlarged horizontal boat and repacked heavy crates. Choice layout stays 150×52 wide / 151×51 portrait, inconsistent with the result footprint. Needs coordinated choice art + zone + result, not a larger invisible hitbox. |
| Make cargo in third column above weights understandable | Not demonstrated | Three closed cardboard boxes remain. Their contents are not established by the scenario visual source, so adding invented contents would be a new content decision. |
| Check that upright boat is not supported by its motor | Not done in initial runtime | `boat-zone4-v29.png`, used for manual 4 and auto, visibly has the motor underneath against the floor. Source and live mobile capture confirm it. |
| Mobile empty area below text | Meeting decision still open / layout owner | 29:24–31:28 asks to resend options for discussion, not to add decoration. Current choice has no large empty reading gap in the 390 capture; shared viewport layout remains General's responsibility. |
| Compact lower numbered buttons should be concise | Approved implementation applied | Approved Figma badge/label family is present. Later external spacing changes belong to General; no local changes here. |
| Zones should look active and support direct selection | Implemented, artistic acceptance unclaimed | Current stroke is opaque dark blue 2.5px with animated dashed outline and an independent 44px minimum hotspot; direct zone buttons exist. Live captures show all four zones and numbers. |
| Mobile actions must remain in the viewport | Passed sampled runtime | Initial 390×844 choice and result captures fit. Additional narrow/short bounds are delegated to shared-layout owner; no real-device/browser-toolbar claim. |
| Entire cutaway and numbers should fit desktop at scale | Passed overview sample, not universal claim | 1440×900 overview shows whole truck and all four outlines. Result detail cameras intentionally crop to the selected outcome; workboard concern was the overview. Browser zoom matrix belongs in final integration. |
| Desktop image quality | Not closed by semantic audit | Current source families are mostly ~1368px portrait and 1774px wide. Upscaling before semantic corrections would preserve incorrect art; General's active-source manifest waits for semantic freeze. |

## Additional continuity issue

Four actual source/runtime crop pairs are in [cab-comparison](cab-comparison/README.md).
Compact changes color on one common tall cab. Carrier-specific shape identity is
therefore unresolved. The moving map's small overhead cab pixels do not prove an
exact bonnet profile; historical SVG icons are not sufficient replacement sources.
Color families match, with visible saturation differences. This continuity issue
is not closed by the color or glass fix.

The boat/place-3 failure illustration still shows the boat outside on a dolly.
It does not visualize an eventual alternative loading solution. The workboard
lists that request among verbal changes; changing the canonical outcome story
is outside this non-copy pass and must not be silently invented.

## Verified semantic revision, resumed 21 October

The table above records the frozen initial runtime, not a claim that fixes are
already on 4344. Owner preview is the production build at 4352, captured as
`4352-*.png` and `runtime-4352.json`: 38 cases, 1440×900 and 390×844, DPR2,
four carrier choices and all five results for each of three gifts. No document
overflow in these samples. All contact sheets were visually inspected.

- Yellow old4 now uses a yellow-preserving color matrix. Existing protected
  glazing/mirror mask retained; 8 pixel checks pass against this production build.
- Wide choice uses the same quiet warehouse as portrait, with matching cargo.
- Upright boat now rests on transport support rather than its motor; manual4
  and automatic share the corrected source.
- Place1 is genuinely empty above six kettlebells and the dishes crate:
  372×94 normalized units, formerly 150×52 wide. Zone2 now follows the smaller
  strapped bay above dishes. Zones3/4 and four selectable decisions are unchanged.
- All six place1/2 outcomes were updated for camera/socks/boat. Common cargo in
  camera/socks results3/4 and upright boat is also coherent with the choice.
  Separate boat3 worker/dolly failure composition is retained as authored.
- Canonical boat1 text is block `1A23B1CD` in `docs/scenario.md`: rear-axle
  overload, not failure to fit. New art preserves its broken rear axle, six
  weights, and intact dishes. Copy, scores and decision logic are unchanged.

Current sources are frozen in [active-upscale-sources.json](active-upscale-sources.json).
Quality processing and General's actual 4344 integration remain separate steps;
no two-pass or publication completion is claimed here. 18 targeted Compact unit
tests passed. The earlier root pixel harness incorrectly selected the expanded
mobile background; the corrected harness selects the cargo image and all8 pass.

Remaining: carrier-specific cab shape, third-column closed-box contents, and the
boat3 eventual alternative-loading visual are not resolved by this revision.
Shared reading-space/layout and browser zoom validation stay with General.

## General integration readback — 21 October

The same frozen semantic sources are now present on normal root
`http://127.0.0.1:4344/`. Targeted isolated readback: choice, boat1 and camera2
at1440×900 and390×844. All6 had zero page errors and no document overflow.
`runtime-4344-final.json` records exact loaded AVIF URLs and zone bounds;
`4344-final-*.png` are the matching captures. Choice loads v54wide / v53portrait;
boat1 and camera2 load their new v53 results. Zone1 is372×94, zone2 is166×36.
These are semantic-source runtime results; Flowers native masters remain a
separate in-progress quality pipeline and are not claimed active on4344 yet.

## Selective quality handoff after the 22 October reset

[The approved throughput reset](../../plans/2026-10-22-throughput-reset.md)
supersedes mandatory Flowers for every asset and the artificial four-ROI gate.
No new native calls are required for the remaining Compact images. Existing
attempts, rejected outputs and source-protected regions remain explicit history.

Ten finished selective masters have owner acceptance and were released individually
to General: F0144, F0025–F0029, F0136–F0137 and F0145–F0146. Canonical acceptance
receipts are in `../compact-flowers-2026-10-21/lane-choice/`, `lane-boat3c/`,
`lane-results-a/` and `lane-results-b/`. Their `processingMode` is
`selective_flowers`; protected original areas and partial native coverage are
disclosed. This is not a claim of native whole-scene8192 generation or universal
AI processing of all22 sources.

General confirmed F0144 active on4344; the changed wide runtime derivative is
5120×2560. The eight actual4344 glazing/paint tests passed again after activation
(6.1s). General also confirmed the preceding six-master batch passed16 actual
runtime states, HTTP200 and zero JavaScript errors. General has now integrated
the last three owner releases (F0136, F0137, F0029) and verified four actual4344
cases for each. All ten selective Compact releases are integrated; canonical
receipts are linked from [final runtime quality](../general-ux-2026-10-22/final-runtime-quality.json).
Original semantic sources and cabin-shape limits
are unchanged. Remaining active rasters follow General's conventional quality
path; unfinished/rejected AI candidates are not accepted replacements.
