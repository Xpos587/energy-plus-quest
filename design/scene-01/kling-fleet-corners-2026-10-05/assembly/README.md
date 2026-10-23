# Fleet assembly workspace

Canonical body layers are now the SAM2 source-RGB [red candidate](red-semantic-candidate/README.md) and [yellow candidate](yellow-semantic-candidate/README.md). Both share1280×720 camera,24fps,546frames/22.75s, zero-based RGBA filenames. They are technical layer candidates awaiting actual four-vehicle road/roof placement and phase review. Main app and source videos were not changed.

[Source roof tracking](source-roof-tracking/README.md) follows exact source frame IDs. Each candidate roof-tracking-22.75s.json adds exact rigid translation and explicit source mapping. Anchors are observed upper-cab color estimates in image coordinates, not3D roof geometry. Driver count remains uncertain.

All10 source semantic masks retain sourceRGB exactly inside their binary body mask; each121-frame sequence was projected with exact camera placement and viewed at21 quarter-second isolations/composites. A0.5px feather adds only soft edge coverage and does not erode opaque truck parts. No ground shadow added. Local crop420×460 at(700,100) of1505×1045 maps from provider x311..968 via the matrix recorded in source roof tracking.

Whole-layer seam shifts fade over at most24frames. No rotation, scale, body morph, dissolve, optical flow, or generated source poses. Source detail/sharpness changes at full-frame/local-clip seams remain visibly conditional. Roof-road image distances are diagnostics; they do not certify wheel/world clearance.

All *-layer folders and preliminary red-candidate-22.75s are REJECTED temporal/color/Hough extraction experiments. They leaked cream curb or lost true roof. Partial reruns may coexist with stale contacts; do not consume them as accepted bodies. Canonical semantic output lives only in semantic-layers and the two semantic-candidate directories.

[Blue receipt](../../kling-blue-keys-2026-10-05/assembly/candidate-corrected/README.md) remains separate. Its existing corrected RGBA filenames are ONE-based0001..0480 and retain conditional neutral fringe until a clean semantic replacement is available.
