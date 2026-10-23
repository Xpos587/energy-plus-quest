# Map v10: truck grounding pilot

## Review output

`energy-plus-map-v10.pdf` contains the whole map, v09/v10 comparison, three route positions and four close views. This is a static review bundle, not a new production animation.

## What changed

The former Cryptomatte vehicle extraction discarded every ground shadow. The new physical shadow pass renders the same animated vehicle geometry and camera onto a road-level Cycles shadow catcher. A common soft sun casts all four shadows in the city's down-right light direction. The exported blue-grey shadow opacity is 0.60 times the physical pass; sun angular diameter is 8 degrees.

Shadow source, exact pass settings and sampled rig preservation are recorded in [grounding source](../fleet-grounding-v10-2026-10-07/README.md) and its receipts. Parent compositing applies a static road receiver mask derived from the unchanged illustrated backdrop. This prevents a ground shadow from being drawn onto a tall building's painted roof. It does not add a depth model to the city.

Red and yellow cab paint has moderate fading and local horizontal lower-body scuffs, excluding driver materials. Existing old-truck exhaust is enlarged and fades toward its upper end, with a neutral grey hue. Modern vehicle materials and all routes remain unchanged. `apply_age.py` saves the master camera before producing isolated QA views; those QA cameras are not saved into the candidate.

## Rebuild

1. `blender --background --threads 4 --python apply_age.py`
2. From the repository root: `uv run --with pillow --with reportlab python design/scene-01/fleet-lookdev-v10-2026-10-07/package_v10.py`

## Verification and limits

Three route positions were rendered: 1, 385, 769. Grounding receipts verify preserved source geometry, camera, root transforms and actions. Age changes leave roots unchanged at the three sampled frames and do not change mesh vertices or driver images; only old exhaust object scale and body shaders are changed. The vehicle pass now uses its native transparent alpha rather than the old Cryptomatte alpha replacement, so exhaust transparency is retained.

Visual inspection and an independent review confirm visibly better grounding and no roof-shadow spill in the supplied frames. Illustrated trailer detail remains simpler than the city; source cab mesh roughness remains imperfect. Fine wear and crew count require zoom. No Fedya approval, all-viewport approval or full-loop validation is claimed. Production files have not been replaced.
