# Last mile · revision 31

## Paid edit ledger · 23 November 2026, UTC

Keyrelay `cx/gpt-image-2`, high quality. The initial four details used one POST; the follow-up bend used one POST. No automatic retries. [Exact edit brief](paint.txt). Inputs prepared by [prepare.py](prepare.py): r30 isolated map objects + scene 4 gift silhouette (edit target), actual in-game illustrated detail references, scenario photographs. The fourth photographic cell identifies the unchanged robot and is not an edit target. Local request and response: `.tmp-work/scene5-r31/paint/details-1.png.{request,response}.json`.
- **06:21:41 · details-1** · requested/returned 1536×1024. The transparent PNG (SHA-256 `7f694faa703182f5ffe6a93657ac25e73177907df219c956523faac24edb236f`) has clear black/orange Mi-8 livery with the white nose marking and a bladeless mast; four large visible tyres and a boxy body on the Rusak; blue striped cab, white projecting bonnet and slotted grille on the pipe truck; a red box with a wide cream ribbon and bow. Provider returned alpha rather than the requested magenta background. Inspected `.tmp-work/scene5-r31/review/details-1.jpg`; no reroll. The receipt did not report cost.

- **07:50:56 · bend-1** · `cx/gpt-image-2`, high quality, 1536×1024 requested/returned. [Exact bend brief](bend.txt). One edit of two 900×300 crops of the pre-follow-up r31 plates (wide origin 170,500; tall 0,670), resized to 1536×512 and stacked. Local donor/warp trials left a double shoreline or stretched the ice across the channel; the one paid edit was limited to those strips. Inspected the returned PNG (SHA-256 `bca5e502a50cf65c9aa37877f671d3e82c628c49b08566f780dff6cb32bc7639`) and both registered river close-ups: one channel, broken white rims on both banks, scattered smaller floes approaching the bend, no ice barrier. No reroll. Request/response and inputs are in `.tmp-work/scene5-r31/paint/bend-{target,1}.png` and `bend-1.png.{request,response}.json`. Receipt did not report cost. The crane used no paid edits.

## Paint and geography

Only local regions of the decoded r30 illustrations were edited. Both original camera projections and native dimensions are unchanged; the runtime still selects **only wide**, irrespective of recipient or screen. No new Blender world/camera or full-frame paid repaint. `export.py` feathers a dry, same-depth r30 tundra patch into the screenshot's inner diagonal arm beside the reindeer, preserving the outer sweep behind the chums. It moves/scales the original painted industrial complex to the far bank, clears the old site, and registers the four painted details. Robot, barge, harbour floes and 12 original rotor poses are retained; the strip is registered to the new painted mast. New silhouettes and deep interior hotspot centres come from the returned alpha, not the obsolete r30 Blender vehicle IDs. Lossy choice encoding uses r30 quality 94; static vehicle layers use decoded choice colour. All twelve WebPs match the r30 filenames and individual dimensions.

The scenario says the route between the quay and destinations crosses bog and a river with first ice (`docs/scenario.md`, blocks `39CE9BB5`, `06D090A1-text`). The overland ride from the helipad to the camp is explicit in `056B051D`. The bank by the muddy quay tracks and the visible ice across those tracks remain. An 8-connected dry-land flood must give **one nonzero component to chums, reindeer, АБК, destination helipad and rig** and a **different nonzero component to the quay gift**. Both wide and tall pass on the revised semantic river/ice mask and independently on decoded final paint (water/ice colours with a 3×3 close in the *old* river corridor, including the deleted arm). See `.tmp-work/scene5-r31/review/checks.json`. This is map-scale topology, not a claim about safe travel over ice.

Transport refs: `docs/scenario-assets/image13.png` = real Mi-8 with nose emblem; `image14.jpg` = snow-swamp rover; `image15.jpeg` = tracked platform (unchanged); `image16.jpeg` = white bonnet/blue striped truck cab. Compared the v9 illustrated sheet (`design/scene-05/v9/ref/vehicles.png`) and the r30 transport sheet with the current flight/ground art. The historical r30 sheet depicts tan cargo; the **actual decoded runtime** robot/rover/ground parcel outcomes and r22 tundra flight show visible red-and-cream wrapping, carried on roof/platform, in hand or at the helicopter's open door. The unchanged Arseniy r18 flight reverses those colours (tan box, red ribbon); the box is clear in the door, so the request not to redo legible outcome art takes precedence. Pipes under the helicopter are not the parcel. No flight or outcome URL/pixels changed; boat variants still depict a boat.

## Reproduce locally

```sh
PY=$HOME/.local/share/comfyui/venv/bin/python
$PY design/scene-05/r31/prepare.py
# Reuse the inspected details-1.png and bend-1.png. Do not resubmit the paid edits.
$PY design/scene-05/r31/export.py
```

Inputs include the r30 ID passes and SAM masks under `.tmp-work/scene5-r30`. The complete r31 runtime outputs are independent of scratch, including `revision-31/layout.json` (native landmarks, per-view contours and motion). No files in r30 were overwritten. Source `expandedArtwork.ts` and `segmentedContours.json` take the `wide` entries. Parcel landmark **(1119,1452), 55×58** native, not a pointer target. Distant rig **(1363,250), 171×162**, down from 211×200.

The checked-out manifest had no revision-30 archive record. Following the existing checksummed archive convention, all thirteen r31 files are in the manifest; the matching regular-file-only tarball is `.tmp-work/scene5-r31/scene5-lastmile-r31.tar.gz`. Its GitHub release URL is a **planned release target, not published**; source was not committed, pushed or deployed. Upload that exact archive before releasing source or expecting a clean checkout to hydrate it from the network.

## Initial review (before the crane/bend follow-up)

Choice screenshots and image review are under `.tmp-work/scene5-r31/review/`:

| Choice screenshot | Measured map stage, CSS px | Native visible x interval | Rig right margin, CSS px | Gift, CSS px |
|---|---|---|---:|---:|
| `choice-390x844.png` | 390 × 525.84 | 329–1664 | 38 | 16 × 17 |
| `choice-412x915.png` | 412 × 596.84 | 375–1618 | 28 | 18 × 19 |
| `choice-1440x900.png` | 1040 × 836 | 0–2239 | 328 | 26 × 27 |
| `choice-1920x1080.png` | 1520 × 1016 | 0–2400 | 548 | 35 × 37 |
| `choice-1024x1366.png` | 704 × 1302 | 619–1592 | 42 | 40 × 42 |

All five use r31 wide, zero gift pins, with neither rig nor parcel behind the hint. `browser.json` includes exact bounds. As in r30, the tall tablet's sidebar makes its map narrower than the foreground row: the helicopter tail and chums are outside that crop, but the helicopter tap point, rig, АБК, reindeer and gift remain visible. No alternate portrait camera was introduced.

- `reference-vs-r31.jpg` pairs each final crop with the illustrated vehicle or parcel reference; `closeup-{helicopter,rover,pipe-carrier,gift}.png` are enlarged crops of the final composite. `outcome-gifts.jpg` shows the actual parcels in existing flight/ground outcomes. `viewport-sheet.jpg` gives a five-screen overview; inspect individual screenshots for phone legibility.
- `go-task verify:quick`: typecheck, 427 Vitest cases in 76 files, 72 tooling tests and Vite compile check passed. Build emitted the existing large-chunk advisory. This was not a release build.
- `bun run test:e2e:quick`: 93/93 passed in 11 lastmile, highlight, feedback and network-recovery files, desktop Chromium with the tests' explicit viewports; existing 4173 server and `.tmp-work/final-2011/pw4173.config.ts`, output override into r31 scratch. Logs: `.tmp-work/scene5-r31/{verify,e2e}.log`.
- The initial thirteen files passed their size/SHA-256 check (superseded by the current manifest below). An additional checkout-wide `bun run media:verify` stops at pre-existing checksums for twelve `public/scene-art/lastmile-r5/*.webp` files. These are unrelated legacy assets; they were not replaced to make the check pass.

## Follow-up: phone crane and former river junction

The original crane ended near x=1819. From the left camp (438) this requires 1381 native px before adding any margin, but the 412×915 choice stage covers only 1243. The owner's camera-parcel second briefing page shows only 1148. [Quay compositing](quay.py) moves the original blue/orange crane above the pipe hold of the moored barge. It keeps a full boom, cable, ladder and gantry in **(1309,1319), 132×202** without covering the truck or robot. The old site uses adjacent quay/tundra, an existing bollard pitch, and the original mooring line. The camp, vehicles, camera, contours, tap points and all ten motion files are unchanged. Only the two choice plates and `landmarks.wide.crane` in `layout.json` differ from the initial r31 runtime files. The native plates are still WebP quality 94; minor quantization differences outside edited regions are possible in these lossy plates. No r30 file changed.

[Bend compositing](bend.py) feathers only the edited channel and its immediate banks into each plate. Both semantic and final decoded-paint topology asserts pass: the camp, reindeer, АБК, destination helipad and rig share the same nonzero dry-land component; the gift remains on the other bank. See `.tmp-work/scene5-r31/review2/export.log`.

Current evidence is in `.tmp-work/scene5-r31/review2/`. `choice-{360x780,390x844,412x915,1440x900,1920x1080,1024x1366}.png` are the six inspected browser screenshots. `river-bend-{wide,tall}.png` are native-scale close-ups; `quay-final.png` shows the crane between the truck and the robot. `browser.json` records contour/rotor/landmark bounds relative to the real stage and hint; `owner.json` checks the camera-parcel briefing pages as well as choice.

| Phone | Choice stage (CSS px) | Camp left clearance | Crane right clearance |
|---|---|---:|---:|
| 360×780 | 360 × 436.84 | 44.5 px | 72.1 px |
| 390×844 | 390 × 525.84 | 31.8 px | 65.1 px |
| 412×915 | 412 × 596.84 | 20.8 px | 58.6 px |

All requested objects clear all three choice frames and the hint. The original narrow tablet sidebar still trims the camp and helicopter tail; the crane now fits there too. Typecheck and 433 Vitest tests in 76 files passed. The 11 requested Playwright specs passed 93/93 in desktop Chromium, including their explicit phone sizes, against the existing 4173 server. The full configured project matrix passed **226/226** across the same 11 files. Logs are `review2/{typecheck,vitest,e2e,e2e-matrix}.log`. A first concurrent run timed out in unrelated Compact Vitest and carrier-highlight Playwright cases; both full reruns passed without changes to those tests.

Current regular-file-only archive `.tmp-work/scene5-r31/scene5-lastmile-r31.tar.gz`: **3,769,268 bytes**, SHA-256 `1084b7b991ab2b901bdea8e365314698f9595e82ecb1acaead0625e528616eb7`. All 13 archive members and runtime files match the current manifest (`review2/audit.py`, `review2/audit.log`). This is still an unpublished planned media release; no commit, push or deployment.
