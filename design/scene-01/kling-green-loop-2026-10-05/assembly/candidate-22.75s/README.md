# Green loop review candidate

[Full loop](composite.mp4), [all five seams at 4×](seams-4x-h264.mp4), [native seam pairs](seams-native.png), [decoded video boundary samples](decoded-boundaries.png).

546 frames at 24 fps, 1280 × 720, 22.75 seconds. Sequence: original green clip first120; 2a source54–119; 2b first120; 3 first120; translation-corrected4 first120. Exact empty city map, aspect preserved, white provider padding retained. No retiming, rotation, deformation or dissolve.

[Canonical tracking](green-tracking.json) follows the largest observed opaque green cab cluster centroid. Normalized upper-left coordinates. It is an image estimate of cab roof, not a native 3D anchor. [Measured seams, corrections and limitations](seam-report.json).

This remains a review candidate: the intended route and truck identity survive the split turn; faint cream/crosswalk fringe persists behind the 2a trailer at some frames. Drawing/driver details and speed differ across provider clips. Do not treat this as a clean-alpha or production-seamless acceptance. Original video inputs and old rejected trials are preserved. Candidate-25s is superseded by this trimmed candidate.
