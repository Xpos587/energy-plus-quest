# Green truck v03 experiment

Local candidate only. Production game assets and runtime manifests are unchanged.

- Source frozen in previous image-to-3D experiment; motion is the same baked maneuver.
- Two volumetric seated actors and one steering wheel are imported inside the opened cab.
- Main variant maps existing reference face crops onto curved head geometry. There are no rectangular character cards. Faces remain soft because source crops are 54×78 and 56×81 pixels.
- Painted green body uses fixed pigment; remaining texture contrast is compressed continuously. No per-frame AI processing.
- Whole tractor still has generated geometry defects, rough glazing/dashboard and fixed nonrolling wheels. Style and maximum zoom quality are not final.
- A trial smoothing pass made UV/material edges worse and was rejected. The delivered candidate retains original topology.
- A fresh review of the geometric-face variant rejected mannequin faces and generated surface artifacts. Face projection addresses appearance only; it does not remove geometry defects.

Review: `energy-plus-green-truck-v03.pdf`, `preview.html`, `green-turn-v03.mp4`.
Packed scenes: `green-truck-v03.blend`, `green-turn-v03.blend`.
Motion is a six-second open maneuver, not a complete city loop.
