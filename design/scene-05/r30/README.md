# Last mile · revision 30

Both cameras are projections of the same rebuilt Blender world. Neutral choice art serves all three recipients, as in r29; flight/outcome art is outside this revision. The render separates the main rotor from the plate; the five blades have twelve real angular poses.

## Camera redo — owner gate

The 30–38° camera candidates use a compact, obliquely staged version of the same world. In particular, the quay crane and moored barge are on the left so they do not occupy the central transport row, and neither junction of the river braid carries shelf ice. **No camera has been selected for this redo.** The existing public artwork and the paid receipts below are from the preceding version, not from these previews.

- Full-frame A–D sheets with unselected-stage crops: `.tmp-work/scene5-r30/cameras/contact-tall.jpg` and `.tmp-work/scene5-r30/cameras/contact-wide.jpg`. Blender gates are 1700×2100 / 2400×1800; these cost-free local previews use 45% resolution and five EEVEE samples.
- `.tmp-work/scene5-r30/cameras/options.json` stores each projection and per-object native-pixel bounds. `cover-preflight.json` checks these bounds against the four requested measured stage sizes and, separately, plain viewport cover. All four pairs fit both checks. This checks 3D composition, not any subsequent painted masks or interaction.
- Additional free E study, no new paid request: `.tmp-work/scene5-r30/cameras/contact-tall-E.jpg` and `contact-wide-E.jpg` (B alongside E; measured native projections in `options.json`, crops in `cover-preflight-E.json`). E moves the eye 30% closer to the quay, then reframes with the same 32° pitch so the far destinations remain in the cover area. Compared with B, projected helicopter span grows 350→400 px tall / 308→376 px wide; rover span 194→215 px tall / 196→239 px wide.

## Paid edit ledger (UTC, 22 November 2026)

The owner authorized these edits. Keyrelay `cx/gpt-image-2`, high, one response per entry. No automatic POST retry. Edit brief: [`paint.txt`](paint.txt). Inputs in order: the corresponding rotorless `locked/{view}-neutral.png` reduced to request dimensions; `design/scene-04/barge-v2/style-a.png` (painting style); `.tmp-work/scene5-r7/diag/ref-sheet.png` (transport and terrain material). Private gateway receipts: `.tmp-work/scene5-r30/paint/{view}-1.png.{request,response}.json`.

- 16:27:04 · tall-1 · 1360×1680 · first illustration of the inspected portrait camera and closed river braid.
  - Response saved; inspected: clean blue fork enclosing chums, half-metre parcel still tiny, four right-facing vehicles, hub without blades. Retain for alignment.
- 16:31:13 · wide-1 · 1920×1440 · separate landscape camera; same approved references and painting brief, not a reroll of portrait.
  - Response saved; inspected on the full plate and at 1:1 over the quay. Both banks remain continuous, two chums are on the island, the crane faces the moored barge, and the rover shows four near-side tyres. No repeat submission for either view. Actual cost not reported by the receipts.

Actual returned PNG sizes (not the requested sizes): tall 1128×1394, SHA-256 `cd16ad9d7f33714f03be5f093f136fc6138e1b07dfa5edb2fc7f6ec52364785e`; wide 1448×1086, `0485f3aa5811e54b84d9a9e655f4539541db21bca6135fd08fdb7a072b142e4d`. The portrait request receipt records submission at 16:27:27 UTC; 16:27:04 above is invocation time. The exact vehicle reference sheet is also in `paint/transport-reference.png` under the scratch directory; its source illustrations are revision-19 `robot-parcel.webp`, `rover-parcel.webp`, and revision-21 `pipe-carrier-tall.webp`.

## Reproduction and checks

From checkout root (Blender 5.2.3, existing ComfyUI Python environment, cached local SAM and RealESRGAN weights):

```sh
S=.tmp-work/scene5-r30; D=design/scene-05/r30; P=public/scene-art/lastmile-family-v1/revision-30
blender -b -t 8 --python-exit-code 1 -P $D/build.py -- $S/locked final
blender -b $S/locked/world.blend -t 8 --python-exit-code 1 -P $D/render.py -- preview
blender -b $S/locked/world.blend -t 8 --python-exit-code 1 -P $D/render.py -- final
# Reuse the accepted paid outputs paint/{wide,tall}-1.png. Nothing below submits an image request.
PY=$HOME/.local/share/comfyui/venv/bin/python
HF_HUB_OFFLINE=1 $PY $D/finish.py $S
$PY $D/export.py $S $P
```

- 41° landscape and 49° portrait cameras, no horizon filler. Transport origins use one ground baseline, 22 m pitch and −22° facing. New blue channel forks left and rejoins upstream of the camp. No bridge. The painted clearance and tiny red box are protected separately; the parcel lid is **0.567 × 0.494 m**, projected to 9×9 px wide and 7×8 px tall including wrap. The marker, not an oversized parcel, should carry the affordance.
- The renderer's vehicle ID prompts segment each actual painted vehicle with SAM; no forced mesh warp of the concrete or pasted old silhouettes. Measured vehicle ID/paint IoU **0.604–0.818**; maximum paint-vs-ID bbox-center error 21.5 px in x and 7.5 px in y (not pixel-identical geometry). Hotspots are inside the paint and their own disjoint tap contours. Initial rotor pose and all 11 subsequent poses rotate about each *painted* mast.
- The exporter separately checks the semantic pass and decoded final painting: an 8-connected land flood that excludes open channel water and first ice cannot reach the chums from either quay parcel or АБК. The paint check detects water/ice colours near the river with a 3×3 close for antialiasing. This is map-scale topology, not navigability of actual ice. `.tmp-work/scene5-r30/review/checks.json` records component labels and geometry metrics; `{wide,tall}-id-overlay.jpg` shows painted/3D shape differences.
- Two RGB choice plates + ten transparent layers, all **same intrinsic names and dimensions as r29**. Static layers use the decoded plate; source rectangles and runtime sizes are separate from fixed WebP sprite dimensions. Both 12-frame rotor strips have individual projected blade poses, with a short blended angular exposure. `review/r29-r30-{wide,tall}.jpg` compares frame zero at the same scale. Review files under `.tmp-work` are temporary.

## Parent integration — not live

1. Read `public/scene-art/lastmile-family-v1/revision-30/layout.json`. Assign `expandedArtwork` to `lastmileChoiceArtwork` in `src/scenes/lastmile/expandedArtwork.ts`, and `segmentedContours` to the sibling `segmentedContours.json`. `landmarks` is separate: no new selectable options. The gift pin anchors are **(1147,1488)** wide and **(781,1693)** tall in native full-plate pixels. Pin tip uses those coordinates, not a box centre from r29. Other landmarks include chums, АБК, rig, helipad, windsock and reindeer.
2. Point **only** `lastmileChoiceImage` in `src/scenes/lastmile/artworkFamily.ts` to revision-30. No recipient-specific choice filenames in r29 or r30; leave flights and outcomes alone. Keep `LastmileMotion` and place from new `motion` boxes, not old pixel offsets.
3. **Do not switch just the URL and geometry on current `WorldArt.coverScale`.** Browser-only module substitution (no source edit) in the 15 existing composition-spec viewports: all four vehicles, destinations, parcel and barge fit in 11. A 412×915 phone clips the far rig bounds; the 1024×1366 tablet clips parts of camp/rig/helicopter; 1920×1080 crops the barge and 2560×1080 crops the rig, parcel and barge. In every case the full new artwork contains all of them. `coverScale`'s floor at full-stage cover defeats the new tighter framing at extreme aspect ratios. A browser-only control using the inner `Math.min` fit-to-framing instead shows all checked shapes in **15/15** (`review/runtime.json` vs `review/fit-runtime.json`), but leaves gutters. Parent must handle those gutters (e.g. a non-interactive art surround or constrained map stage), rather than ship plain bands or crop the story. The trial didn't test outcomes, interaction flow, or release packaging.
4. After runtime and owner visual review, update the media manifest and run normal integration/release acceptance. No src, test, manifest or deployed version was changed by this artwork task.
