# V10 truck grounding

Source is `../fleet-style-v08-2026-10-07/projected/clean/fleet-v09-clean-sill.blend`.

`fleet-v10-real-shadowcatcher.blend` is a dedicated Cycles shadow scene. Fleet is invisible to camera rays but casts shadows. Original city geometry and lights remain in the file, hidden in this pass. Source truck geometry, materials, actions and camera are preserved. A horizontal shadow catcher at z=-0.002 sits 2 mm below tyre contact. A single sun at world direction (-40,+35,+70), 8° angular diameter, plus diffuse blue sky gives a soft screen lower-right cast.

The clean source's EEVEE compositor replaces Combined alpha with vehicle Cryptomatte. That deletes ground shadows. Its added overhead sun also has shadows disabled. This pass separates physical shadow coverage from vehicle alpha instead of deriving a generic ellipse from bounding boxes.

`shadow-raw-NNNN.png`: 16-bit Cycles Combined RGBA, transparent catcher. Black RGB, alpha is shadow opacity (coverage); transparent outside shadows. This is an alpha shadow layer, NOT a transmission map.

`shadows-NNNN.png`: 8-bit PNG straight/unassociated RGBA. Constant sRGB blue-grey RGB=(64,101,129), alpha is raw Cycles coverage multiplied by 0.60. Tint changes color only; the rendered tyre/contact/cast geometry is unchanged. For a raster compositor: `out = shadow_rgb * a + background_rgb * (1-a)` followed by ordinary vehicle alpha-over. For a premultiplied pipeline, premultiply RGB by alpha exactly once on import. Do not multiply this PNG directly as if its RGB were transmission. To obtain neutral transmission, use T=1-alpha (after the 0.60 illustrated strength adjustment).

`vehicles-NNNN.png`: copied clean source EEVEE RGBA, intentionally retaining its appearance. Parent may replace these with newly aged vehicle passes while keeping camera and meshes fixed.

`pilot-composite-NNNN.png`: diagnostic composition only. Background resized with Lanczos to 1920×1334, followed by shadows and vehicles.

`preservation-verification.json` documents exact equality of source/candidate camera, roots, frame interval, all fleet world matrices at 1/385/769, and every fleet mesh vertex, polygon and material assignment. No geometry was changed.

Commands (repository root):

```
blender -b design/scene-01/fleet-style-v08-2026-10-07/projected/clean/fleet-v09-clean-sill.blend -t 6 --python design/scene-01/fleet-grounding-v10-2026-10-07/build_shadow.py
blender -b design/scene-01/fleet-grounding-v10-2026-10-07/fleet-v10-real-shadowcatcher.blend -t 6 --python design/scene-01/fleet-grounding-v10-2026-10-07/render_remaining.py
uv run --with pillow --with numpy python design/scene-01/fleet-grounding-v10-2026-10-07/prepare_pass.py 1 385 769
blender -b -t 2 --python design/scene-01/fleet-grounding-v10-2026-10-07/verify_preservation.py
```
