# Constructive green-loop road proposal

The green route remains entirely in the distant eastern district. Vehicle scale is unchanged: 180 px overall, 43 px tractor width, 36 px trailer width. This proposal reconstructs the road to fit the modeled articulated sweep; it is **not a claim that current V16 passes**.

## Chosen path and construction mask

Hitch/reference centerlines: left x765, right x1122, top y140, bottom y730. All four corner radii: 80 px. The green rig starts at hitch (765,340), pointing south. This means shifting its current drawing approximately 20 px east. The tractor front is 70 px ahead of this reference point.

`proposed-road.geojson` contains exact pixel-coordinate polygons for the required road corridor (complete swept envelope buffered outward by 6 px) and additional asphalt beyond the conservative existing-road mask. `proposed-road-edit-mask.png` is its white-on-black raster edit mask. `proposed-road-edit-guide.png` overlays required corridor in green and additional road in orange. Interiors remain holes: no wholesale clearing of the central blocks is intended.

The corridor is constructed from the sweep, so containment is true by construction. The separately checked half-step poses test discretization gaps; they do not provide an independent vehicle-dynamics validation.

## Central plaza opening

Straight section y575–600 requires **x737.5–792.5**, width 55 px, including 6 px margin each side. A practical rounded drawing can use x737–793. The swept corner then expands east; do not draw a constant-width slot all the way to the bottom road.

| y | Left corridor edge | Right corridor edge near central opening |
|---|---:|---:|
|575|737.5|792.5|
|600|737.5|792.5|
|630|737.5|795.8|
|650|737.0|806.6|
|675|737.5|844.4|
|687|737.5|882.1|
|690|737.5|895.8|

These are required surface extents for the chosen candidate, not a globally optimized minimum. The lower turn requires a broad curved cut into the southwest corner of the right-hand low building/plaza, approaching x882 at y687. Thus only opening a narrow plaza slot is insufficient at the current rig size. Preserve the tall center-right block except where the top corner corridor overlaps its raster roof projection.

## Remaining local edits

The entire corridor bounds are x715.99–1171.01, y90.99–779.01. The top corner near the eastern avenue reaches y91, and the lower corner reaches y779. The outer avenue corners extend about 4 px beyond conservative x1167 asphalt. The top connection also needs a wider visible opening and rounded setbacks at both ends. Use the supplied polygon, not its bounding rectangle: the rectangle would unnecessarily erase whole blocks.

A correct final raster must show the road visibly under the swept footprint. Some orange regions are conservative-mask artifacts or roof-overhang projection rather than ground walls; an illustrator must reconcile these with the oblique scene. The model does not establish actual building-footprint demolition requirements.

## Executed check

Three laps, 5274 poses, sampling at 1 px or smaller; maximum articulation 50.1938 degrees. Zero modeled footprints outside the proposed road; zero midpoint violations between adjacent sampled poses. No shortening was applied. Articulation stays below a chosen 55-degree screen-animation guardrail (not a manufacturer limit). The 80 px radius is hitch-path curvature, not a certified axle turning radius: tractor wheelbase and front-wheel steering are not known from this illustration.

Other trucks are not static obstacles in this check. Green crosses the orange middle route and overlaps the yellow bottom route; these require time separation in the animation. The blue route remains distant. Other rigs' individual swept paths were not tested.

Reproduce: `uv run --with pillow --with shapely python design/scene-01/route-validation-2026-10-04/proposed.py`.
