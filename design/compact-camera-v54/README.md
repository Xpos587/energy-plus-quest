# Scene 2 camera v54 restraints and accepted boat badge

The original camera/badge revision was accepted in `aa68c14`, following the
accepted [socks revision](../compact-socks-v57/README.md). Michael subsequently
reported that the camera fastenings had changed too much, while socks were OK.
The follow-up restores camera restraints and raises the camera above them.
The coordinator approved upward box extensions and a small same-sprite
reduction at place 3 to stay below the roof. Cargo support positions, copy,
scoring, hit areas and badges are unchanged.
The coordinator accepted the current comparison: camera body/lens readable,
native restraints retained. Source-commit permission covers the compositor and
this README only; push, upload and deployment are not authorized. The earlier
boat acceptance is unchanged.

## Camera

The existing v53 secured results used different camera bodies and packages;
the place-4 package was above the floor. The candidate reuses the camera from
`public/compact-art/camera-zone1-fallen-v53.png` in cardboard inserts of the
same 124-pixel width for places 2–4. Auto uses place 3. No image-generation
request was made.

`scripts/compose-camera-v54.py` masks the existing camera, removes surrounding
cardboard/cloth pixels and isolated specks, and levels its fallen pose by 25°.
The inserts still rest on the cloth (bottom y=621), top carton (y=478), and
cargo-bay floor (y=718). They extend upward to heights 68, 48 and 59 pixels.
The camera rises by 24 / 5 / 15 pixels versus the original v54 placement;
places 2/4 retain its 35-pixel height. Place 3 uses a uniform 31-pixel version
of the same sprite, with its top at y=431, safely below the roof. This narrow
exception was explicitly approved after the unchanged 35-pixel camera could
not clear the band within the niche's headroom. The cream liner stays behind
the camera. Restraints retain their original dimensions,
curvature, metal buckles and wall mounts, matching socks pixel-for-pixel.
Places 2–3 retain the original anchor positions; place 4 uses the same 66-pixel
floor-level translation as socks. Straps remain in front of the package.
The previous 22-pixel vertical scaling and `bottom - 18` relocation from
`aa68c14` are removed. No additional shadow is drawn.

Place 1 is **unchanged**, including the fallen box, camera and broken plates.
This preserves the failure described in [the scenario](../../docs/scenario.md).
Its damaged, rotated package is not pixel-identical to the secured insert.
The place-3 result number moves left, including auto, so it does not cover the
camera on a phone. The same approved socks badge displacement is reused.

## Boat: B selected under delegated review

- **A — leave everything as before.** Baseline screenshots retain the number
  over the bow in place 4.
- **B — keep every illustration; move only result number 4 left.** The
  coordinator selected this option under Michael's explicit delegation.
  Auto receives the same adjustment. Places 1–3 do not change.

The boat's different poses communicate different outcomes: rear axle damage,
crushed dishes, failure to load, and a secured vertical boat. Making every pose
look secured would contradict those outcomes. The carrier-specific place-3
failure pictures and all boat asset mappings remain untouched.

## Reproduce and verify

Use the existing local media, including the socks compositor's source assets;
this script imports its environment, restraint extraction and resize helper.
Do not publish or force-add binaries to make this review candidate portable.

```sh
uv run --with pillow --with numpy --with scipy python scripts/compose-camera-v54.py
# With the local source preview already running on 127.0.0.1:4175:
bun scripts/capture-compact-gifts.mjs .tmp-work/barge-camera-fastenings/after camera,socks http://127.0.0.1:4175
bunx vitest run src/scenes/compact
bun run typecheck
```

The generator asserts box width, cargo/roof bounds, at least 70% unobscured
camera silhouette, original hardware pixels at the socks anchor coordinates,
and unchanged pixels outside the affected package/restraint regions.
The hardware regression failed on the previous scaled/moved restraint; the
70% visibility regression then failed on the first full-size-restraint draft.
Both pass for all three current outputs. Generation was first run into a
candidate directory via `main(output)` before integration. Pixel comparison
with the saved pre-fix v54 images found **zero changed pixels outside the
approved box/restraint regions**. All 3,410 / 2,085 / 1,968 opaque hardware
pixels match socks at places 2 / 3 / 4, respectively.

The first correction's 47.7% / 44.2% / 35.9% visibility was rejected as
unreadable. The current measured fractions are **72.7%, 72.1% and 72.2%**;
the body and lens now sit above the band, which crosses the lower camera.
The earlier 85% guard is superseded by the coordinator's 70% target, not
silently relaxed. Fractions measure occlusion, not recognition; full-size
phone screenshots remain necessary because the whole-truck view is small.

Fresh checks: 52 compact tests across 5 files and TypeScript passed. Both before
and after capture passed 20 result cases: camera and socks, places 1–4 plus
auto, at 1440×900 and 390×844. They check decoded artwork, no orange region
overlays, disabled result choices, stable choice-target styles and page errors.
Before/after `checks.json` files are identical. All ten socks result screenshots
and desktop camera place 1 are pixel-identical. Phone camera place 1 differs
only within badge 1's unchanged bounds plus shadow; its artwork hash is
unchanged. Choice screenshots have animated hint differences and are not
claimed pixel-identical.

Current local evidence (temporary, subject to repository retention):

- [Original camera / before / socks / after detail sheet](../../.tmp-work/barge-camera-fastenings/restraints-comparison.png)
- [Full 1440×900 frames, places 2–4 before/after](../../.tmp-work/barge-camera-fastenings/full-frames-1440-comparison.png)
- [Full 390×844 frames, places 2–4 before/after](../../.tmp-work/barge-camera-fastenings/full-frames-390-comparison.png)

Raw captures and `checks.json` are in that folder's `before/` and `after/`;
`place-{2,3,4}-{before,after}-detail.png` are enlarged individual crops.
`pixel-checks.json`, `ui-checks.json`, `regression-{red,green}.log`,
`visibility-{red,green}.log`, `vitest.log` and `typecheck.log` contain validation
evidence. The v53 comparison files are
local media named by `aa68c14^:src/scenes/compact/resultArtwork.ts`, not binaries
recovered from Git. Captures use Alva/default carrier only; no exhaustive
carrier/recipient/device or human-recognition test is claimed.

## Local media inventory

Only these three runtime media files changed; socks, boat assets and camera
place 1 are unchanged. SHA-256 values identify the current local correction.

| Path under `public/compact-art/` | SHA-256 |
| --- | --- |
| `camera-zone2-v54.png` | `2ef8cfce7e1054dd91b226e9d86a0af5d7a347a2f78c86cdc2376df5faf40343` |
| `camera-zone3-packed-v54.png` | `cdaccf85cde3ee2234814b44d40ef5d1617bd027b7092477722c0974d1547d29` |
| `camera-zone4-v54.png` | `5ba52b56d08d149bb1cde0ef88ba39a1b92668f869fb88a25acf1e08b3c3f2c2` |

Binary media stay local/ignored; `media-artifacts.json` is unchanged. Approved
media must later be published through the repository artifact workflow, under
separate authorization, before deploying source that references them.
