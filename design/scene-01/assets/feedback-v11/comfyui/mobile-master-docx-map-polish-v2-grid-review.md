# Mobile master grid review

Source: `mobile-master-docx-map-polish-v2.png`, reviewed at native 768x1424 and 375px preview. Grid: 4 columns x 8 rows, each native cell 192x178.

## Verdict

Reject v2 as-is. The map foundation is much better, but the vehicles are not proportioned to the street grid. At 375px the truck bodies read as oversized foreground objects: Near, Crew, and Express occupy roughly 1.5-2 lane widths/road intervals. Old is too close to the top-left/rail edge and loses countability in the whole frame. The next pass must correct scale and lane placement, not add more decoration.

## Block review

| Cells | Review | Correction |
| --- | --- | --- |
| A1-B1 | Old sits at the edge of the first road and visually merges with water/rail and exhaust. It is operational but too low-contrast to count quickly. | Move it inward on the upper-left road, keep it small, add a clean dark contact shadow and a narrow exhaust; do not enlarge it into a hero object. |
| A2-D2 | Railway is strong and gives the map structure. Surrounding blocks are believable, but the road is too empty relative to the vehicle scale. | Keep railway; balance street-to-vehicle scale rather than adding more objects. |
| A3-C4 | Urban blocks read well after polish: roofs, courtyards, trees, snow banks. | Keep the visual richness and vary only enough to support route clarity. |
| D3-E3 | Warehouse is clear and dominant, but the apron is visually over-large and flat. | Keep one warehouse and three doors; add subtle loading-yard texture only if it does not compete with vehicles. |
| E4 | Near is correctly at the warehouse exit and has a good tight-turn trace, but the body is too wide/long and sits partly across the perpendicular road. | Reduce to about 42-48px wide at 375px, keep fully on the curved exit apron, and preserve the turned wheels/barrier cue. |
| F1-F4 | Lower middle city grid is clean and gives routes room. | No new trucks or signage. |
| G1 | Crew has two readable drivers, but the truck is too large and nearly spans the road/intersection. | Reduce to about 52-58px wide at 375px, center in one lane, preserve the two-driver cabin. |
| H4 | Express has a strong identity and wake, but it occupies too much of the lower-right arterial and crosses the junction visually. | Reduce to about 50-56px wide at 375px, center it on the arterial, keep only one `Express` wordmark and a shorter directional wake. |

## Hard next-pass checks

- Exactly four complete vehicles visible in the whole 375px frame.
- Old, Near, Crew, Express each countable without HTML labels.
- No truck body visually spans two lanes or crosses a junction.
- Warehouse remains at least 2.5x wider than the largest vehicle.
- Crew still has exactly two separate adult drivers.
- Near remains at the loading exit, not parked in the intersection.
- Express remains the fastest-looking vehicle, but its wake stays local to its road.
