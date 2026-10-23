# First-scene animated loop — current receipt, 2026-10-05

Target: one usable animated first scene, four distinct articulated trucks, seamless loop, readable at zoom, styled like the accepted scenes. User selected Kling after the single-truck comparison. That approval applies to ../turn-model-comparison-2026-10-04/kling.mp4, not a full-map animation.

Main game runtime has NOT been replaced by the experiments in this pass.

## Sources and current status

- Accepted style: ../route-preflight-2026-10-04/map-v16.png. Bright detailed clean illustration with soft colored outlines and shadows. This is not a route certificate.
- Correct deterministic movement: ../controlled-motion-2026-10-04/v2b/source-loop-48s.mp4, 48s /24fps /1152frames. Frozen rig starts all four trucks within3degrees of straight. Source collision/asphalt and loop-boundary receipts live there. This low-detail native source is a technical motion reference only.
- Production-compatible roof centers: ../controlled-motion-2026-10-04/v2b/roof-tracking/carrier-roof-tracking.json. Exactly1152rows, four normalized roof centers perrow, red/blue/green/yellow.
- Illustrated aligned city: v2b-aligned-style.png. Vehicle-free derivative: v2b-empty-map.png. Image editing may alter nonvehicle pixels, so neither is a pixel-exact physical geometry certificate.
- Separate rendered truck-layer pilot: ../painted-layer-2026-10-05/composite-12s.mp4. Four trucks, native motion preserved,12s,24fps. Rejected visually: simplified pasted appearance, insufficient driver detail, disconnected-looking tractor/trailer articulation. Full render stopped. Geometry diagnosis and bounded repaired stills live in that directory; repaired stills are not an accepted animation.
- Current Kling bounded trial: ../kling-bounded-2026-10-05/. Source image, end keyframe, exact prompt and provider result retained there. It is a short segment, not a loop. Do not reuse native roof tracking for generated motion without extracting and checking actual positions.

## Video trials and measured Higgsfield debits

| File | Finding | Credits |
|---|---|---:|
|edit-pilot.mp4|Extra parked blue truck; toy3D|7.5|
|edit-pilot-v2.mp4|Schematic; not accepted illustrated detail|7.5|
|full-map.mp4|Free paths leave map/cross buildings; no valid loop|18.75|
|controlled-edit-failed.json|Failed job; debit refunded|0|
|controlled-edit-retry.mp4|V1clearance/occlusion and toy style fail|7.5|
|controlled-edit-pro.mp4|More expensive mode still toy3D|10|
|v2b-draw-edit.mp4|Cleaner background but cab detail/morphing and roof overlap fail|18.5|

Verified prior video debit for this work:69.75credits, excluding earlier comparison pilots, static-image costs and Gemini. New bounded Kling trial recorded separately; do not add an estimate to actual debit.

Kling3 motion-control schema is exposed but cost/create reject Unknown workflow. No successful job or debit. Draw To Video specialized CLI accepts video/sketch/timestamp/prompt; duration/resolution flags are rejected even though generic workflow schema lists them. Actual Draw result was5.041667s,121frames,24fps,752x560, default480p. Gemini analysis attempt returned503; uploaded video deleted, receipt retained.

## Delivery gate

All four identities, rigid articulated turns, no duplicate/disappearance/reversing/offroad routes, readable cab/driver counts, static detailed background, loop seam, and1x/2x/4x desktop/mobile selection must be checked before replacement. Original game uses48s/24fps; video, poster and roof tracking must change together. A short fragment cannot be promoted by simply looping it or by applying mismatched native tracking.

A reviewer finding is a hypothesis until checked against actual frames. Gemini previously reported inaccurate PASS/direction observations; local evidence controls acceptance. The rendered-layer reviewer identified a real cab/chassis shrink defect, measured and fixed in bounded stills; stylistic and driver detail limitations remain.
