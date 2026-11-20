# Crane walk art — local handoff

`manifest.json → formats[format].sprites` is the source of truth for **every** sprite box and frame list. Files in `assets/{wide,desk,mid,tall}` are lossless transparent WebP, cropped from the same 2× grid as `crane-r11/layers/{format}/plate.png`. Paths in `src` are relative to this handoff, not to the app. Do not point a production page at `.tmp-work`.

- **Idle:** use the plate as-is. The people and the ladder are painted into it. Don't draw either walker, patch, or a separate ladder sprite.
- **Departure:** on the same tick as the first moving frame, show **`porch` for Ivan** or **`post` for Petr**, hide that character's former cutout/hover, and keep the patch up until reset. Leave the other person in place. Draw these patches under all moving actors.
- **Walk:** use `walkIvanEast`, `walkIvanInland`, `walkIvanSeaward` or their `walkPetr…` counterparts. Each `frames` is a zero-based sequence of columns in **one horizontal strip**. The box's `w`/`h` describe **one frame**, not the strip. For a canvas draw, source `(i*w*2,0,w*2,h*2)` → destination `(footX-anchorX,footY-anchorY,w,h)`. All destination/anchor/box units are plate CSS pixels. For CSS, use a clipped frame with background-size `cols*w` by `h`; don't scale a whole sheet into one box. Initial walk `x,y` already place the pivot at the first waypoint of the corresponding route (`routes.rush[0]` or `routes.petr[0]`); while moving, use the projected **feet**, not the static tooltip/head anchor. Ivan: `Inland` for the porch exit, `East` for the long land-side lane, `Seaward` on the final segment. Petr: `East`, then `Inland` on the final segment. Eight phases repeat; tie phase to travelled distance (`manifest.walkCycleMetres` = 3.648 world metres per cycle) instead of a vertical CSS bob. Shadows are baked into ground frames only.
- **Depth:** after drawing the walker, draw `walkOccluder` on Ivan's main lane or `walkOccluderPetr` on Petr's lane; switch to `turnOccluderIvan` / `turnOccluderPetr` on the final segment. Composite at the manifest box, no transforms other than the plate's global scale. A `null` mask means no front geometry. Don't use a single full-plate mask or draw all masks together: an object can be in front of one lane but behind the other. The moving crane upper isn't painted on this plate: keep the real upper, hook, and cable in their own layer; draw those over the walk if they overlap. Do not draw the old isolated ladder, even during the climb.
- **Climb:** switch to the shadowless two-frame `climbIvan`/`climbPetr`. Move its foot pivot from the last waypoint to the landing, in front of the ladder (world `x=60.2,y=3.9,z=0…11`). Draw `climbOccluder` if present. Do not center the body on `ladderTop` or add another bob.
- **Cab:** hide the climber and show exactly one **`cabIvan` / `cabPetr`** above the crane's moving upper. These are **4×4 sheets**, laid out like the existing `top` sheet. Draw cell `i` at the sheet's fixed `x,y,w,h`; `sx=(i%4)*w*2`, `sy=floor(i/4)*h*2`. The seats already rotate with the crane: **15 = rest**, **0 = gift**. Do not rotate or reposition them in CSS. `frameBoxes[i]` records the tighter *absolute plate box* for inspection; it is **not** the drawing destination for a whole cell. The departure patch stays up during occupancy; clear it on reset. For quick comparison, `qa/{format}-arrival.png` shows both occupants at rest.

## Box cross-check

Values below are **x, y, frame width, frame height** in plate CSS pixels. The full walk/turn/climb boxes, foot pivots, column counts and all frames are in `manifest.json`; consume the JSON rather than transcribing these values.

| Format | porch | post | walkOccluder (Ivan main) | cabIvan / cabPetr shared cell |
|---|---|---|---|---|
| wide | 452, 589.5, 72, 90 | 829, 575, 65.5, 81.5 | 600, 380.5, 502, 206 | 1348.5, 184, 81, 104.5 |
| desk | 244, 701, 73, 91 | 625.5, 686.5, 66, 82 | 394.5, 490, 507, 208 | 1151, 291, 81.5, 106 |
| mid | 221, 735.5, 67, 83 | 569.5, 722, 60.5, 75 | 358, 542.5, 464, 190.5 | 1050, 361, 74.5, 96.5 |
| tall | 273, 1333.5, 74.5, 134.5 | 524, 1092.5, 47.5, 95 | 234, 1253, 43.5, 91.5 | 495, 371.5, 166, 106 |

**Integration check for the app owner:** `src/scenes/crane/CraneArt.tsx` at inspection time used `walked/1.4` and drew all three holdouts together; this art needs `walked/3.648` for the planted stride and **only the mask for the current segment**. End-climb wins over turn, turn wins over main lane. Test the cadence on device: time-compressing an entire ~80 m walk into a few seconds can make a distance-driven gait strobe. Change playback timing if needed; don't put the CSS bob back. Anchor positions assume the generated r10 camera, r11 painted plate and existing 16-position crane upper, not resized source art.

## Rebuild locally

From this directory, with the supplied r10 and r11 siblings present:

```sh
mkdir -p work qa
blender -b ../crane-r10/render/quay.blend --python-exit-code 1 --python render.py
cc -std=c99 -shared -fPIC -O3 depth.c -lm -o work/depth.so
~/.local/share/comfyui/venv/bin/python export_art.py
~/.local/share/comfyui/venv/bin/python qa.py
```

`render.py` reads r10 model cameras and the source `quay.person()` geometry functions, renders poses in isolation and exports triangles. `depth.c` rasterizes those triangles against upright route planes and seated worker geometry. `patches.py` reconstructs hidden architecture from neighbouring painted surfaces; equivalents in wide/mid use local affine registration. There is no API, diffusion model, new ladder or app edit in this handoff.

## QA verdict (asset-level, before app integration)

67 lossless WebPs (about 2.4 MiB); 20 contact sheets were rendered from the delivered WebPs and visually inspected across wide, desk, mid and tall. Exact masks/boxes, not approximate pasted locations, are used by `qa.py`.

| Asset | Verdict and evidence |
|---|---|
| Walk / climb | Ready. Orange- and white-hat workers are standalone posed figures, not cutouts. Eight distinct planted/recovery phases per heading, two alternating climb poses, no shadow dragged up the ladder. `qa/{format}-walk-cycle.png` and `-arrival.png`. The simplified illustrated meshes are not a pixel-identical copy of the original painting. |
| porch / post | Ready at game size. The full figures and foot shadows are removed. The porch has aligned steps/door frame or paving joints; the crane crossbar, track and quay edge continue behind Petr. `qa/{format}-patches-300pct.png` is a 3× nearest-neighbour enlargement of the **2× source**, before vs after. Hidden surfaces are reconstructions; small differences in brush texture and shadow detail are visible at that enlargement. The old blurry r11 patches and the experimental clone are not included. |
| walkOccluder + branch-specific holdouts | Ready on the supplied routes. `qa/{format}-depth.png` compares the same posed worker at the same point without/with the depth cut. Ivan goes behind the far crane on landscape; on tall Petr is cut by the boom lattice. Petr's waterside lane correctly has almost no landscape occlusion. No standalone ladder or replacement rung art. Masks are route-specific, not general-purpose depths for arbitrary paths. |
| cabIvan / cabPetr | Ready. Both helmets and torsos are visible at the console through the actual cab opening at rest. The roof, posts and boom correctly reduce visibility at some other angles. `qa/{format}-arrival.png` shows both workers; `-cab-slew.png` shows all 16 slew positions with Ivan. |

`qa.py` verifies every manifest texture is present/referenced and decodes at the claimed 2× frame size, all walk/climb phases differ, and each pose has a connected, unclipped opaque silhouette. All 128 packed cab cells were also compared to their reviewed pre-pack overlays: same visible RGB, alpha and plate location. Browser playback, selection/reset state and performance were **not** tested by this art-only lane. Review the integrated rush/Petr branches on desktop and portrait before release.
