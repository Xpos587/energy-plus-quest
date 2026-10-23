# v21 — source-only trailer correction

Next render source: `v21-compact-trailer.blend`.

Derived from delivered v20 64-second loop. No render or game asset replacement performed.

- All four trailer wheel steering pivots moved from Y ±0.805 to ±0.66. Tyres, rims and hubs move together; axle length and upper crossmembers narrowed. Wheel radius and existing compact longitudinal axle spacing retained.
- Fifth-wheel coupling moved from tractor-local X -2.30 to -1.75. Trailer roots moved forward consistently at every keyed frame, including closing frame; fifth wheel and support deck follow. Trailer articulation headings retained.
- Root routes, city, materials, camera and smoke are otherwise retained. This is a geometry patch, not a new physical route solver.
- `geometry-check.json` records lateral hardware bounds, all-frame hitch alignment and loop closure. `verify_saved.py` reopens/checks saved geometry. No visual render was produced, as requested.

Rebuild (source-only):

```sh
blender -b --python design/scene-01/fleet-v21-coupling-geometry-2026-10-09/fix_geometry.py
```

Do not use v20 build_from_routes.py alone for the next render: it restores the older hitch position. Apply this patch after rebuilding v20. Next rendered output requires fresh shadow passes and tracking export because trailer roofs have moved. Existing game video remains v20.
