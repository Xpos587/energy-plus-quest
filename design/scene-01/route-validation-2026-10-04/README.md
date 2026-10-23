# V16 green truck: route feasibility diagnostic

**Verdict: the requested rounded loop does not fit V16.** This is a visible road-network obstruction, before assessing steering. Do not use this candidate as an approved animation path.

The 1506 × 1045 raster shows the green rig approximately x723–766, y212–392: about 180 px long and 43 px at its widest. These are manual image measurements, not a calibrated ground-plane vehicle survey.

## Load-bearing findings

1. At x742, the north street ends at the middle transverse road (roughly y480–575). The requested continuation south to y753 crosses a continuous built block and sidewalk between roughly y575 and y690. In particular, x742/y630 is not road. Rounding corners or shortening the rig cannot fix the absent connection.
2. A horizontal path at y753 sits on the lower edge of the bottom transverse street. With 43 px width, even the reference line needs moving upward to approximately y725–730 before a usable margin can be discussed.
3. A vertical path at x1145 leaves only 22 px to the conservative right asphalt boundary x1167, against a 21.5 px half-width. That is essentially no margin. A trial center closer to x1120–1122 is more credible.
4. The requested top path y103 crosses the foreground edge of the upper city block. A top-road trial needs approximately y140, and the visibly available raster strip is only around 40 px in places. Since this image is an illustrated oblique projection, visible roof/curb edges are not a calibrated ground plane. An actual pass at the top cannot be certified by sliding rigid screen-space rectangles.

## Reproducible candidate

`validate.py` generates a piecewise linear hitch path with exact 40 px circular corners, integrates a passive trailer heading in 1 px or smaller steps, and intersects both body polygons against the union of explicitly recorded manual road rectangles. Tractor: 80 × 43 px (70 px ahead of hitch, 10 px behind); trailer: 110 × 36 px behind the hitch; hitch-to-trailer axle: assumed 85 px. Straight overall length is 180 px. Wheelbase and axle placement are assumptions, not measurements recoverable from V16.

The closed candidate is x742 south, y753 east, x1145 north, y103 west, then south to the starting point. Results: 2037 samples; 1481 have more than 1 px² outside the conservative road mask; peak modeled articulation 66.46°. These counts describe this particular screen-space mask, not collision probabilities or a real truck's dynamics. Gaps and simplified square corners in the conservative mask can flag extra failures. The missing street is independently visible and does not depend on mask precision.

The cyan rectangles in `swept-path-diagnostic.png` show the manual mask, magenta is the hitch line, and red shading shows footprints that leave it. Other trucks, lane direction, moving traffic, steering limits, terrain, roof occlusion and perspective scaling are not modeled. A successful mask test would still not prove a production animation safe.

## Recommendation

If V16 geometry is fixed, change the route: turn west at the middle road, travel down the western avenue, then turn east onto the bottom road. This is a road-network alternative only; its articulated turning clearance has not been validated, and the blue/orange/yellow trucks must be considered. It also still requires resolving the top connector.

If the exact central-down / bottom-right / top-left loop is required, edit the map to create a real central passage through the middle block and widen/reposition the top connector. Then establish an unobstructed road surface in a consistent ground-plane projection and run the articulated swept-path test again. A shorter rig alone cannot repair the current route. Intersection widening and any rig reduction should be chosen after that geometry exists, not guessed from this failure.

Run from repository root:

```sh
uv run --with pillow --with shapely python design/scene-01/route-validation-2026-10-04/validate.py
```
