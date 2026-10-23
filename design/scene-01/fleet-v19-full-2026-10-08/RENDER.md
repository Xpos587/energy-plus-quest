# Full current V19 render

Source: [city-occlusion.blend](../fleet-v19-city-occlusion-2026-10-08/occlusion/city-occlusion.blend).

The saved current source contains frames **1–192 at 24 fps**. This export renders that entire range, yielding **8 seconds at 1920 × 1334**. It is not a repetition of the previous two-second excerpt, and it does not restore the obsolete 48-second route animation. No route, camera, geometry, material, wheel, smoke, or cab-shake animation was rewritten for this export.

All 192 vehicle/holdout frames and all 192 matching current compact-axle shadow frames were rendered fresh. Four serial 48-frame chunks per pass avoid GPU accumulation. Ground silhouettes come from the current visible vehicle meshes and are clipped by the existing road receiver mask. The branded V19 city is composed with those shadows and transparent vehicle frames.

Reproduce:

```sh
uv run --no-project python design/scene-01/fleet-v19-full-2026-10-08/render_all.py
uv run --no-project --with pillow --with numpy python design/scene-01/fleet-v19-full-2026-10-08/compose_all.py
```

Validation: `render-receipts.json` records all eight Blender process exits; `validation.json` records decoded frame count, dimensions, frame rate, duration, and full FFmpeg decode status. `contact-sheet.png` samples the beginning, middle, and end. This export is not installed in the game and is not declared a seamless loop.
