# Actual Blender geometry QA

**PASS for modern European tractor exterior in overview views. NOT a full production/crew pass.**

Imported actual `free3d-volvo-fh-green.glb` into factory-empty Blender 5.2.2 with autoexecution disabled. New isolated `preview.blend`; original downloaded GLB and production scene untouched. Rendered Cycles, 24 samples with denoising, 900×900, soft world daylight plus two area lights, orthographic camera. Commands: `blender -b --disable-autoexec --python design/scene-01/whole-map-v06-2026-10-06/source-research/qa_volvo.py` completed exit 0. Both images opened and visually inspected:

- `volvo-front3q.png`: continuous rounded cab shell, coherent windshield/grille/headlamp arrangement, recognizable modern Volvo FH outline; wheels, mirrors, chassis and side fairings modeled sufficiently for overview use.
- `volvo-desktop-high.png`: stable cab roof and outline at high angle, chassis clearly legible. Some rough roof accessory edges and texture/geometry imperfections remain. No gross lumpy or inflated cab silhouette apparent in these views.

Opaque dark windshield; no visible two-person crew or inspectable interior from exterior. One material and one mesh: cab-color changes will require texture editing or spatial material masking. Lamp/grille detail partly comes from texture; not a fully separated clean CAD-style vehicle.

Model triangle count 18,471. Imported Blender coordinates: front **-Y**, +Z up. Bounds and exact camera transforms in `volvo-qa-manifest.json`.

A separate read-only attempt to append current Higgs `Mesh_0` for a camera comparison did not yield a reliable front view; `higgs-front3q-comparison.png` is **not approved evidence**. Direct matched-view superiority over current Higgs is therefore unverified. This does not invalidate the two actual Volvo renders. No production adoption performed.
