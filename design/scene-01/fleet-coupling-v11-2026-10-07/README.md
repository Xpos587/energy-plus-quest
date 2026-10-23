# Fleet coupling candidate v11

`fleet-v11-coupling.blend` is the canonical master. It was saved with the original desktop camera before any isolated QA camera changes. The only source geometry edits are the authorized relocation of old-vehicle exhaust stacks and their existing smoke. Trailer translation is rebaked for the entire existing timeline; heading animation is retained.

Evidence:

- `coupling-before-after.png`: matching side-camera comparison for review/PDF.
- `side-1.png` through `side-4.png`, `front-1.png` through `front-4.png`: isolated views.
- `maxturn-*.png`: each truck at its own maximum articulation.
- `vehicles-0001.png`, `vehicles-0385.png`, `vehicles-0769.png`: original-camera transparent fleet renders.
- `coupling-receipt.json`: hitch change, model-unit gaps, camera and full timeline attachment checks.
- `all-frames-validation.json`: every truck/frame attachment and conservative cab separation measurement.
- `actual-geometry-validation.json`: actual triangle intersection checks and mesh-derived axle contact measurements. The axle estimates are contact-patch midpoints, not named CAD joints.
- `preservation-validation.json`: master readback against source, including image paths, mesh coordinates, hidden flags, materials and camera.
- `shadow-receipt.json`: fresh physical shadow pass configuration. `shadow-raw-*.png` is actual catcher coverage; `shadows-*.png` is the tinted straight-RGBA delivery pass.

Reproduction scripts use Blender background mode. `build.py` loads the preceding age-lookdev source; save its canonical master before rendering isolated QA. Run `build_shadow.py` against that new master, then `uv run --no-project --with pillow --with numpy python prepare_pass.py`. The parent task handles raster-background receiver masking and final city composites outside this directory.

No production/frontend assets are changed. No complete animation render is included.
