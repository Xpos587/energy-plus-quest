# Keyframe-driven turning experiment

Scope: cheap controlled animation test; truck style redesign and full four-truck loop deferred by user. Production unchanged.

## Inputs
Three stacked reference-derived poses were generated and corrected twice before splitting into key-0.png, key-1.png, key-2.png. Original scene: ../turn-pilot-2026-10-04/start.png. Red truck removed to isolate articulation. Camera background is visually similar but not pixel-locked. This is not an approved replacement map. Intermediate rig visibly bends at hitch; final rig aligns horizontally. Remaining detail/scale/curb issues require scrutiny.

## Seedance test — rejected
Two 4-second480p transitions with explicit start/end frames. CLI job records preserve input roles and seed. Combined turn.mp4 is internal rejected output: first segment overshoots then reverses toward middle pose; second segment makes a spurious loop over the buildings rather than just straightening. Gemini2.5Flash reviewed actual video but incorrectly marked PASS; its report is retained as contradictory output, NOT validation. Remote upload deleted. Visual frame contact sheet establishes failure. Do not show rejected turn.mp4 as a candidate.
Actual video debit:1.2+1.2=2.4Higgsfield credits.

## Alternative engine
One Hailuo02Fast6second transition from mid-turn to straight pose; estimated and actual debit6credits. Awaiting output review. Total Higgsfield video spend this experiment8.4credits. Built-in static image generation and Gemini analysis are separate services; their monetary billing was not returned here, so8.4is NOT a total all-service price.

## Final review of Hailuo — rejected
hailuo.mp4 / hailuo-contact.png: one truck moves right from articulated pose to straight pose, but semitrailer roof/side edges visibly curve into a banana between~0.5–4seconds. Rigid-body requirement fails. Actual-video Gemini review (hailuo-gemini-review.md) independently identifies this deformation and returns FAIL; other assertions about exiting the crop are not adopted without verification. Remote upload cleanup confirmed in receipt.

No candidate passed; no rejected video opened for user review or integrated into game. Three keyframes alone did not establish reliable articulated turning with either tested engine. Next technical direction is geometry-driven motion or much denser fixed-rig poses before interpolation, rather than repeated text-only changes or expansion to four trucks. This is an inference from these trials, not proof all keyframe video models fail.
