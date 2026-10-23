# Historical scene 1: painted heading animation

The atlas notes below describe a previous runtime. For the current video map, source and reproduction, see [the separate routes report](../../docs/reviews/2026-09-23-separated-routes.md).

Actual application: http://localhost:4173/ (profile -> recipient -> parcel -> carrier map).
Previous v2 functional acceptance was explicitly rejected visually. V3 motion captures also contain a rejected dirty-region rendering experiment. **Use v5 evidence for current runtime acceptance.** User visual approval is not claimed.

## Root causes and fixes

- Plain source-mesh cuboid tractors were the wrong artwork. Current cabs use reference-shaped reconstructed geometry and four registered GPT Image 2 painted camera projections, rendered into 72 actual headings. Slate low cabs serve 1/4; modern blue cabs serve 2/3. Crew glazing contains two painted seated humans. Truck 2 has the lower modern roof. Trailer panels use the approved18 truck4 painted panel texture. No flat sprite rotation, wordmark, static-truck substitution or fifth manual truck.
- Broad mirrored-pavement replacement polygons erased curbs/markings and left triangular truck shadows. The clean plate now registers a painted repair to original18, then composites only within documented vehicle/shadow support. Outside-mask original pixels remain exact, including protected visible leaves; lossless WebP preserves them. Foreground silhouettes follow actual roof/facade edges, excluding roads and courtyard paths.
- Hard nearest-heading rounding caused five-degree sticking. Premultiplied adjacent-heading blending keeps opaque bodies opaque while changing view continuously.
- Repeated large-image resampling cost frame time. Static layers are cached at display density, with viewport caches for overview. **Every frame clears/redraws the entire canvas.** Dirty-region clipping was removed: fractional clip coverage accumulated translucent stripes/ghost edges; integer clips still produced inconsistent boundary sampling. Correctness takes precedence over that optimization. No dirty-region fallback remains.

Routes, independently articulated trailers, speeds, smoke, all four manual choices, automatic choice, original outcome meaning, keyboard/pointer controls, reduced motion, page visibility and mobile locate/pan controls remain intact. Approved17/18 and the original girl are unchanged. No later-scene content is edited.

## V5 mechanical rendering repair

Parent review found projected duplicate wheels, incorrect tractor/trailer overlap, and a black spike near truck3. These were real blockers, not accepted style differences.

- Mechanical triangles now retain their original mesh UVs instead of receiving camera-painted wheels from adjacent faces. Painted cab/glass appearance is retained.
- Cab and rear chassis render into separate heading passes. Runtime always draws chassis below cargo; only the cab shell participates in cab/trailer depth sorting. Eight atlases replace the five combined passes.
- Hitch offset is calibrated to 2.1 source units instead of 2.3, reducing exposed connection length. Full-loop cab/cargo, fence, building and inter-truck clearance tests pass.
- The black spike was a stationary remnant of the original truck3 roof edge on the crossing, not a moving sprite defect. Expanded local mask support restores the crossing; three former-black stripe-interior samples are now checked as white.
- Trailer camera is tightly framed at 8.4 units around elevation1.7 instead of 12 around ground, preserving sharper detail in the same 256px cells and decoded memory. Runtime uses the matching anchor.

No paid generation or reference artwork changes were made for these fixes. Full-frame redraw and exact-pixel overview/zoom/pan checks remain mandatory. Reconstructed artwork still requires independent visual review; no exact approved18 match is asserted.

## Sources and reproduction

Durable source directory:
`/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-20-live/`

Contains generated reference images, receipts, old/crew GLBs, four guides and registered painted projections, clean plate and rendered heading sources. Existing Blender 5 and ComfyUI Python supply all tools; no new dependency.

```sh
P=/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-20-live
O=/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-21-live/atlas
PY=/home/michael/.local/share/comfyui/venv/bin/python
$PY scripts/scene1-live/build_assets.py
$PY scripts/scene1-live/trailer_paint.py
$PY scripts/scene1-live/register_paint.py old-cab "$P/scene1-old-sheet.png" "$P" "$P"
$PY scripts/scene1-live/register_paint.py crew-cab "$P/crew-cab-sheet.png" "$P" "$P"
for family in old-cab near-cab crew-cab; do
  blender -b -t 4 --python scripts/scene1-live/painted_cab.py -- "$family" "$P" "$O" render
done
blender -b -t 4 --python scripts/scene1-live/render_atlas.py -- "$O" trailers
python scripts/scene1-live/pack_atlas.py
python scripts/scene1-live/test_assets.py
```

## Verification

```sh
npx vitest run --maxWorkers=2 --testTimeout=15000
npx playwright test tests/map-numbers.spec.ts tests/scene1-live.spec.ts --project=desktop-chromium --project=mobile-chromium --workers=1
npm run build -- --outDir /tmp/scene1-v4-build
node scripts/scene1-live/validate.mjs /absolute/evidence-directory
node scripts/scene1-live/measure.mjs /absolute/motion-evidence-directory
node scripts/scene1-live/closeups.mjs /absolute/closeup-directory
```

V5 evidence root:
`/home/michael/.local/state/energy-plus-quest/research/2026-09-18-style-variants/live-scene1-v5/`

The exact-pixel browser regression compares animated frames against a fresh redraw at the same clock, for overview, zoom-follow and keyboard pan, on both desktop/mobile Chromium. No channel difference is allowed. Five-size evidence exercises all manual+auto results and continuing to the next existing scene. Motion evidence records multiple times and a 12-second RAF trace. V5 native browser without video encoder: 719 callbacks/12s, median16.7ms, p95/p99 16.8ms, zero >34ms. Recording adds overhead: 582 callbacks/12s, p95/p99 33.4ms, zero >34ms. Both traces are retained; v4 recording statistics are not claimed for v5.

## Limits

- This is animated 2.5D with real 3D-heading renders, not a native runtime 3D scene.
- Reconstructed geometry/projection detail is not pixel-identical to approved stills; current painted atlas is retained for independent parent visual review, not asserted as new user approval.
- Near/crew share a modern painted family; near has a lower cab. Old1/4 share the approved slate family.
- Physical Safari/iPhone/Telegram WebView remain untested. Performance figures are local Chromium with recording, not a universal device guarantee.
