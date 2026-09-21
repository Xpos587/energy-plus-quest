# Pass13 drawing-language review

## Delivered change

One whole-city ink-and-opaque-paint redraw, not another roof-only variant. Generated from the repaired pass12 layout, the original professional girl as a separate style reference, and the first environment fragment. Three purposeful image jobs: fragment, whole map, natural crew refinement. The girl is never generated into the map. Its original file and the pre-existing RGB-identical cutout remain untouched.

The drawing visibly changes at normal size: foliage is built from outlined irregular leaf clusters and grouped dark shapes, trucks have articulated blue cab planes and tire silhouettes, warehouse and storefront edges are drawn rather than softly rendered, road and pavement acquire graphic curbs and solid color. The original girl's ink and opaque clothing shadows now have counterparts throughout the environment. This is a reviewed candidate, not a claim of user approval.

## Findings repaired during finishing

- Whole-frame generation retained the right objects but shifted central blocks by roughly 20-35 display pixels. Registration uses projective building/vehicle regions with a continuous background mapping. Both fence chains and gate endpoints are included. No pass12 environment pixels are pasted back.
- A first unconstrained background registration curved building edges and exposed frame holes. Projective architectural regions and generated-texture frame bleed replace that candidate. The final mapping has no folds; raster checks reject long black edge holes. Small pavement/peripheral distortions remain a stated limit.
- The whole-map crew was recognizable but lacked the successful glass treatment. A dedicated detailed two-person cab edit supplies only the front-glass polygon; the restyled cab and map are retained. Faces, bodies, steering wheel and reflections now share the drawing language.

## Final visual inspection

Inspected the original girl, pass12 contact sheet and repaired map, four supplied brandbook pages, fragment beside the girl, whole-map generation, crew closeup, final full-size map, exported comparison, detail board and thumbnail. Browser screenshots are recorded separately in the source pass13 screenshots directory.

- Warehouse: six separate doors, seven painted bay boundaries, small СКЛАД sign. The raster regression independently detects all seven boundaries across four scanlines and checks that the six visually located door centers fall between them.
- Roof: six skylights in two rows of three; two HVAC boxes at the rear clear of skylights; the small center vent remains, and is not a third HVAC unit.
- Tower: coherent six-floor window grid with the lowest floor partly screened by the existing shop; no added pseudo-loggia levels.
- Both storefronts: central door is separate; three ground-floor panes each side. Business-center upper windows sit above rather than across the ground-floor glazing.
- Fence: two connected warehouse-rooted chains, one open vehicle entrance, no crossing terminating in the fence. One east-road zebra remains. The 9.3m dimension belongs to the unchanged saved source; the illustration is not a CAD measuring surface.
- Vehicles: exactly four, numbered 1-4 in their original districts. Truck3 has two naturally seated adults under the true front glass. Trucks1/4 are maintained older vehicles, not wrecks. All trucks remain stationary; only the reused exhaust animates.

## Residual limits

The short drawn shadows are more defined than pass12, especially under trees and behind the warehouse. The image remains daylight rather than dramatic night lighting. Registration introduces small local departures in pavement and cropped peripheral art; important composition, count and connectivity are maintained semantically, not pixel-for-pixel CAD projection. The girl remains more polished than some of the fine environmental hatching at high enlargement. Style compatibility still needs the user's decision. No production or full-route-animation integration is claimed.

## Evidence

- `scene-check.json`: newly rerun Blender checks on the unchanged saved source; roof clearance, storefront separation, six doors/seven boundaries, retained crossing landings and crew all pass.
- `artifact-check.json`: original/cutout preservation, hashes of prior reviews and saved source, actual painted bay detection, broad image-change coverage and frame-hole checks.
- `registration.json`: all recorded anchors, projective regions, positive mapping Jacobian, zero old environment pixels inserted.
- `validation.json`: browser checks, downloads and local HTTP byte equality, five viewport sizes, two-state switching, stable zoom, original reference visibility, reduced-motion/pause behavior, no overflow and no page errors.
- Unmodified pass12 `smoke.test.mjs`: 769 deterministic frames, truck1/4 only, correct original cab-side anchors and bounded opacity/drift.
