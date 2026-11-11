# Scene 2 camera v54 and boat badge — accepted

This is the follow-up to the accepted [socks revision](../compact-socks-v57/README.md).
Michael delegated the pending visual decisions to the coordinator with
«действуй на свою усмотрение в этот раз». The coordinator selected boat B and
requested the camera visibility revision below, then accepted both after
viewing the desktop, phone and native-size phone-crop sheets. Commit permission
covers the six scoped text files only. Push, media publication and deployment
remain outside this authorization. Copy, scoring, choice hit areas and
layout-editor coordinates remain unchanged.

## Camera

The existing v53 secured results used different camera bodies and packages;
the place-4 package was above the floor. The candidate reuses the camera from
`public/compact-art/camera-zone1-fallen-v53.png` in one 124×44-pixel cardboard
insert for places 2–4. Auto uses place 3. No image-generation request was made.

`scripts/compose-camera-v54.py` masks the existing camera, removes surrounding
cardboard/cloth pixels and isolated specks, and levels its fallen pose by 25°.
The common insert rests on the cloth (bottom y=621), the top carton (y=478),
and the cargo-bay floor (y=718). A pale cream packing liner separates the dark
camera from the cardboard rim. The camera is 35 source pixels high, raised to
the top of the insert. The original restraint is removed with a neighboring
wall patch, resized to 22 pixels high and placed at `bottom - 18`, across the
lower rim rather than the body/lens. Straps and complete metal buckles remain
in front of the package. No additional shadow is drawn.

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
# With the local source preview already running on 127.0.0.1:4181:
bun scripts/capture-compact-gifts.mjs .tmp-work/compact-gifts-1011/after camera,boat
bunx vitest run src/scenes
bunx tsc --noEmit -p .
```

The generator asserts the common box size, cargo bounds, foreground restraint
pixels and unchanged pixels outside the affected package/restraint regions.
It also requires at least 85% of the dark camera silhouette pixels to remain
unchanged after adding the restraint: observed values are 95.2%, 97.5% and
90.9% for places 2, 3 and 4. This is an occlusion guard, not a legibility score.
Recompositing the old strap positions over the current insert fails that guard
in all three places. Boat places 1–3 and desktop camera place 1 remain
pixel-identical to baseline screenshots. The phone camera place-1 screenshot
has a small rasterization difference confined to badge 1's edge/shadow;
its artwork and badge DOM bounds are unchanged.
Four new badge cases failed before the UI change; the focused suite then passed
14/14 tests. The latest scene suite passed 278 tests across 38 files; TypeScript passed.
The final capture passed 20 result cases: camera and boat, places 1–4 plus auto,
at 1440×900 and 390×844. It checks decoded artwork, absence of orange region
overlays, disabled result choices, stable choice-target styles, and page errors.
The boat's special place-3 picture correctly has no choice controls.

Local before/after sheets (temporary, subject to repository retention):

- [Camera, desktop](../../.tmp-work/compact-gifts-1011/camera-comparison-1440x900.png)
- [Camera, phone](../../.tmp-work/compact-gifts-1011/camera-comparison-390x844.png)
- [Camera, native phone-size crops](../../.tmp-work/compact-gifts-1011/camera-phone-1x.png)
- [Boat A/B, desktop](../../.tmp-work/compact-gifts-1011/boat-comparison-1440x900.png)
- [Boat A/B, phone](../../.tmp-work/compact-gifts-1011/boat-comparison-390x844.png)

Raw captures and `checks.json` live in the adjacent `before/` and `after/`
folders; `phone-before/` holds the previous dark v54 candidate used as the
camera comparison baseline. Test output is `vitest.log` and `tsc.log`.
Sheets show all four manual outcomes, enlarged source details and labelled
native-size phone crops. Captures use recipient Alva and the default carrier;
they do not establish an exhaustive carrier/recipient/device audit. The camera
remains small in the whole-truck phone view, but its silhouette is separated
from the liner and restraint. Visual acceptance is not inferred from tests.

## Local media inventory

Only these three runtime media files are new; boat assets and camera place 1
are unchanged. SHA-256 values identify the visibility revision reviewed here.

| Path under `public/compact-art/` | SHA-256 |
| --- | --- |
| `camera-zone2-v54.png` | `67287e6064e3757bd91787b9068e2a834778d7bc3472e27137f68dafc7c3627c` |
| `camera-zone3-packed-v54.png` | `2bc62fca68bc849d3ddc11cebf07ab527b21cbf8e66c8842bf5d53eebb7d1eb0` |
| `camera-zone4-v54.png` | `30968253b1afd29c50467a53d1a22933eea2e829238798f225023928769bd32e` |

Binary media stay local/ignored; `media-artifacts.json` is unchanged. Approved
media must later be published through the repository artifact workflow, under
separate authorization, before deploying source that references them.
