# Seated crew candidate

Import collection `CREW` from `crew.blend`. Coordinates match the unchanged source cab `Mesh_0`: forward = −X, driver = vehicle left = −Y. All actor and wheel objects are prefixed `CREW_`; preview lights and camera are prefixed `PREVIEW_`.

Two illustrated adult male figures are built from real curved head/face/hair meshes, necks, blue work shirts, shoulders, arms, seated hips, bent thighs/knees/calves and shoes. The driver's hands grasp one wheel. Passenger hands rest on his lap. Face likeness is approximate; these are stylized geometric actors, not photoreal source portrait cards.

Positions in cab coordinates:

| Element | X | Y | Z |
|---|---:|---:|---:|
| Driver head reference center | −0.775 | −0.20 | 0.145 |
| Passenger head reference center | −0.775 | 0.20 | 0.145 |
| Driver seated hips | −0.53 | −0.20 | −0.235 |
| Passenger seated hips | −0.53 | 0.20 | −0.235 |
| Wheel center | −0.79 | −0.20 | −0.035 |
| Driver palm centers | −0.774 | −0.262 / −0.138 | 0.015 |

Wheel radius is 0.077, plane normal normalized from `(−1,0,0.32)`. Head vertices remain behind the front windshield plane `X = 0.187338 Z − 0.913884`. Hair, nose and ears are volumetric. The eye and brow details are small adult proportions.

`crew-front.png` and `crew-three-quarter.png` show the fully seated actors. `cab-front.png` and `cab-three-quarter.png` show the actual source cab with its front windshield faces removed **only in the new copied preview**. `crew-cab-preview.blend` is that preview scene. Original cab is never saved or modified.

The source cab contains opaque window geometry; production integration must expose or replace that window surface for crew visibility. At steep aerial camera elevations, the roof can occlude the actors. Existing side glass stays opaque in this preview.

Reproduction: `blender --background --python build_crew.py`; checks: `blender --background --python validate_crew.py`. Cycles, 24 samples, 1000×720 transparent PNG. Read `receipt.json` and `validation.json` for measured checks.
