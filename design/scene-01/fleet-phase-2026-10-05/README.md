# Fleet phase analysis: no accepted four-truck solution

All outputs are local geometry diagnostics. No runtime edits, paid video jobs, manual truck drawing or production changes. Red/yellow contours use actual green RGBA as provisional geometry; their future appearance-edit clips require fresh checks.

## Uniform-scale follow-up

uniform-scale-report.json and uniform-scale-contact-sheet.png test whole-rig uniform scales0.98/0.96/0.94/0.92 around each observed cab-roof anchor, preserving timing, proportions and articulation. No east shift. Common period22.75s,1092 output frames per case. Two requested phase scenarios:96/259/479/blue11 fixed, and comfortable114/296/478 with every eligible straight blue opening phase. None passes zero opaque overlap plus2px clearance. At0.92, fixed scenario still has6 overlapping frame-pair samples (maximum3 opaque pixels); comfortable scenario withblue19 still12 (maximum2pixels). These are minute rendered-edge/fringe intersections, not a physical/world crash claim. Requested stop at0.92 respected. Actual native before/after crops are uniform-scale-crop-*-1.00.png and uniform-scale-crop-*-0.92.png. Source roadmask outside-pixel metrics improve with reduction but retain matte-fringe/segmentation caveats; exact measurements are in the same report. No scale is accepted or applied.

## Evidence and coordinate system

Actual green22.75s tracking/546RGBA frames and blue20s tracking/480RGBA frames at1280x720. Fixed map comes from ../kling-layer-extract-2026-10-05/empty-map-padded.png; extract_layer.py explicitly derives this by aspect-preserving scaling/padding of ../four-truck-loop-2026-10-04/v2b-empty-map.png. Contours, not native routes, govern the checks. Alpha>127 is opaque; alpha>16 is soft. Every extracted alpha pixel is included, including fringes. AABB separation is a conservative sufficient test; zero AABB gaps were refined with exact pixel intersection and closest contour distance. Pixel overlaps are rendered-envelope failures, not physical/world crash claims.

## Useful far-three geometry

Source frame phases green114 / red296 / yellow478, or seconds4.75 /12.333333 /19.916667. All observed opening poses meet straightness criteria. Minimum far-three envelope gap47.4236px; no opaque or soft overlap. Relative green-source offsets permitting at least20px conservative pair clearance are162..384frames; at least30px168..378frames. The comfortable three-truck spacing should be retained.

## 45.5s loop: blue one circuit, far-three two

No phase-only passing four-truck candidate was found. Exhaustive search of all eligible integer opening phases with a20px far-three margin is in exhaustive-phase-report.json and exhaustive-contact-sheet.png. Initial coarse/low-margin results in final-phase-report.json and comfort-phase-report.json are diagnostic alternatives, not acceptance.

With comfortable far-three phases114/296/478, best straight-opening blue phase is8source frames. Central/entry/exit rigid east translation sweep0..10px is fully recorded in blue-rigid-offset-report.json. +6px still leaves75 opaque overlap frame-pairs, maximum136pixels; +10px still62, maximum67pixels. Derived roadmask signed clearance worsens from baseline-2px to-8px at+6px, and to-11px at+10px. The source already has fringe outside the color-derived asphalt mask, so these numbers are conservative image-envelope measurements, not semantic pavement or physical-clearance ground truth. +6px does not pass either collision or color-derived road containment gate.

The central UP straight is observed at blue source192..291. Proposed cubic smoothstep translation uses source170..192 ramp-in,192..294 hold,294..322 ramp-out. This is a rejected diagnostic proposal, preserved in proposed-blue-translation-tracking.json. No rotation/deformation was used. Exact baseline conflict time ranges, cab centers and source-frame pairs are in blue-rigid-offset-report.json. Before/after native crops are blue-offset-*-baseline.png and blue-offset-*-corrected.png; blue-offset-contact-sheet.png pairs them.

## Common22.75s period: two cycles each in45.5s

This reduces phase drift and makes blue slower by its shorter observed route, but still yields no passing candidate under actual source envelopes. With comfortable fixed far-three phases, best blue phase18 retains60 overlap frame-pairs and1134 summed opaque pixels. Unrestricted all eligible integer-phase search with20px far-three minimum is in common-period-phase-report.json. Best phases96/259/479/11 retain30 frame-pair overlaps, maximum34pixels, with22.4722px far-three gap. This compromises the comfortable47px spacing and is not an accepted replacement. Exact common-period conflict snapshots: common-period-overlap-green-blue.png and common-period-overlap-yellow-blue.png; magenta marks actual overlapping pixels. Contact sheet: common-period-contact-sheet.png.

Tiny fringe/edge intersections are distinguished from a world crash. However phase alone has not produced the requested independent cab/trailer envelopes. Alpha cleanup or lane/route geometry changes would require a new explicit check; they were not assumed here.

## Speeds and longer loop

distance-speed-report.json is canonical for measured closed cab-centroid distances and45.5/91s speed comparisons. common-period-speed-report.json records the common-period variant. Tracking distances include roof-centroid noise and source seam steps; no physical km/h calibration is implied. Common-period geometry gives green=red=yellow>blue, so it does not establish the requested four-way ranking.91s with four/three/two/two circuits gives the desired mean image-speed rank, but unequal circuit counts on the same far-three closed lane require overtakes; phases alone cannot avoid their continuous-path position coincidences. Separate lane/route geometry is needed for that91s arrangement.

## Reproduction

inspect_phases.py extracts alpha envelopes and straightness. refine_phases.py builds actual pixel/contour matrices. search_all_openings.py is the search/diagnostic renderer; exhaustive and common-period runs change its source-phase candidate stride to1 and blue source sampling period appropriately. blue_rigid_offset.py reproduces the rigid-offset sweep. All checks sample1092 output frames at24fps; no claim is made for interpolated subframes. Straight openings require trailer principal-axis deviation<=12degrees and cab/trailer articulation<=8degrees, with+-3 source-frame neighbors also qualifying.
