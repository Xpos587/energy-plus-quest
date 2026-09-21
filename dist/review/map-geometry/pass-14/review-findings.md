# Pass14: remove registration, restore the girl to the map

## Actual change

The pass13 raw generation already contains straight architectural edges, straight truck bodies, six dock doors/seven bay lines, the repaired roof arrangement and separate storefront entries. Its finishing script introduced the rejected rubber distortion through thin-plate displacement, projective region blending and a mesh resample. Pass14 does not run that script or replace it with another registration system.

The final lossless map is the native 3504x2336 raw13 painting, pixel-identical everywhere outside a 4,618-pixel front-glass repair mask. No global stretch, crop, perspective transform, TPS, mesh, background bleed or texture filter is applied. The existing detailed crew painting is uniformly reduced and translated into the front glass; its people are not projectively fitted. No new paid generation was necessary.

The original girl is back INSIDE the map by default, in both the browser and exported comparison. The large foreground copy is deliberately enlarged to judge drawing style; the small copy stands on the business-center sidewalk. The old character file and its existing alpha cutout are untouched; the new display asset is an RGB-identical crop. The checkbox hides both copies only in the interactive view; downloads are explicitly labeled as including the girl.

## Final-image visual inspection

Viewed the raw13 painting and sample, original girl, pass12 geometry-reference image, final map with girl, final detail board, actual before/after geometry crops, and final desktop/mobile browser screenshots. These are checks of the delivered raster, not claims inferred from the unchanged Blender scene.

- Roof edges remain straight across their full spans, including peripheral buildings. Warehouse skylights form two rows of three; two larger HVAC units sit behind them with clear separation. The small central object remains a vent, not a third HVAC.
- The warehouse front contains six distinct roll-up doors. Seven straight painted boundaries align with the jambs; five raster scanlines independently find all seven. The canopy and warehouse sign remain readable.
- Truck bodies retain straight box edges and consistent cab proportions. Exactly four trucks remain, numbered 1 through 4; older trucks1/4 are maintained rather than wrecked. Native aspect ratio avoids pass13's initial nonuniform squeeze as well as its later local warps.
- Both warehouse-rooted fence chains stay continuous, with one open vehicle entrance. Truck4 remains on the road outside the entrance. There is no added crossing into the fence. The east crossing is singular at the southern business-center junction, with sidewalk landings.
- The six-floor tower grid is coherent; its lowest row is partly screened by the foreground shop. Retail and business-center central doors are separated from three panes on each side; the business-center upper windows do not intersect the ground-floor glazing.
- Truck3 contains two naturally seated adults, visible skin/clothing, a steering wheel and diagonal glass reflections inside the actual front windshield. The cabin shell and windshield boundary are the unwarped whole-map drawing.
- The full-city drawing-language change from12 remains: inked foliage clusters, graphic curb/building contours, solid colored cab planes and opaque painted shadow groups throughout the frame. It is not a return to12 or a texture-only filter. Lighting is sunny daylight.

## Framing and review

The map14 frame is 3:2, matching the raw image; every edge is present. Versions12/13 are uniformly contained with narrow side margins rather than stretched to3:2. All three states keep the same review canvas, foreground character placement and zoom. The small diagnostic moves to the corresponding sidewalk. Detail cards are explicitly labeled as fixed14 crops. All art is static: smoke is omitted rather than reusing invalid anchors.

`geometry-evidence.jpg` shows real before13/after14 roof, truck and peripheral-pavement crops. `details.jpg` shows roof/dock/fence/crew/facades/crossing. `comparison-after.jpg` and `comparison.jpg` include both copies of the original girl within each map.

## Residual limits

The generated city remains modestly displaced relative to the12 source camera; correcting that displacement through rubber registration was exactly the rejected operation, so it is not reapplied. The9.3m gate dimension belongs to the source scene and is not claimed as a calibrated measurement in this illustration. The foreground figure deliberately overlays peripheral buildings but not the dock, trucks, crew, central shops or gate. Small diagnostic and crew details need zoom on phones. Style compatibility still requires user judgement; this is not a claim of user approval. Main game, animation routes, old versions and original character bytes remain untouched.

## Executed checks

- `pass-14/check_artifacts.py`: final native map equals raw13 outside the front-glass mask; character RGB and 661 protected file hashes preserved; both exported figures verified against an independent composite; all seven dock lines detected at five depths; no staged files.
- `pass-14/browser-check.cjs`: 1440x1000, 390x844, 320x568, 820x1180 and 568x320; three states, 300% zoom, no horizontal page overflow or script errors, all local links and HTTP bytes, downloaded comparison bytes. Difference screenshots independently establish actual visible girl pixels at both placements, not just an SVG element bounding box. The full foreground figure fits the initial desktop viewport.
- Baseline `git status --porcelain=v1` is unchanged; all new work is under the two pass14 directories.
