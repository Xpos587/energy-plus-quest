# v22 native 4K vehicle render

Source `v22-4k-source.blend` preserves v21 compact trailer geometry, camera, animation, materials, and existing holdout. Only render settings changed. Texture references were resolved against v21 before saving; packed textures remain embedded.

Approved pipeline:

- Vehicles: 3840×2668, EEVEE, TAA 8, volume 32, volume tile 4, RGBA PNG.
- Launch via `prime-run`: verified NVIDIA GeForce RTX 3050 Ti Laptop GPU, OpenGL. Default launch selected integrated AMD Radeon.
- Ground shadow: 1920×1334, actual animated visible mesh projection, TAA 8.
- Deliverable frames 1–1536, 24 fps, exactly 64 s. Frame 1537 is a separate boundary diagnostic.
- City plate and final compositing are owned outside this directory.

Measured pilots on frames 1, 384, 768:

| Renderer | Seconds per frame |
| --- | --- |
| AMD full 4K tile 2 | 43.960, 30.718, 28.548 |
| AMD 4K without smoke | 6.498, 4.663, 4.495 |
| RTX full 4K tile 2 | 13.717, 10.081, 7.869 |
| Approved RTX full 4K tile 4 | 4.830, 3.971, 4.121 |

Tile 4 retains native 4K hard surfaces and the original in-scene smoke occlusion. Its volume grid matches 1920/tile2. Parent approved it after the native comparison `smoke-tile2-vs4-native-crops.png`. RGB mean absolute differences on the visible union are recorded in `gpu-quality-comparison.json`.

Resume approved full render:

```sh
uv run --with pillow python design/scene-01/fleet-v22-warehouse-hq-2026-10-09/render/render_all.py --full-approved
```

Use `--first N --last N` for a bounded approved subset; default full range is 1–1537. `--pilot` requests only 1, 384, 768. Without a mode the launcher refuses to run.

The launcher decodes every existing PNG before skipping it, decodes each complete batch, and decodes all requested images once more at completion. Each render writes a temporary PNG before atomic rename. It verifies requested files even if Blender reports success after a Python exception. Passes run sequentially to avoid GPU and RAM contention.

`full-process.json` records the detached process, `full-render.log` logs batch results, `full-progress.json` records completed counts, and `full-complete.json` is written only after final decode checks. Actual per-frame times are in `render-receipt-*.json` and `shadow-receipt-*.json`.

Initial AMD tile2 vehicle pilots are archived in `pilot-amd-tile2/`. Only approved RTX tile4 pilots were seeded into `turn-vehicles/`. Existing shadow pilots used identical geometry and settings and remain valid.
