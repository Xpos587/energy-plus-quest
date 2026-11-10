# Scene 3 warehouse: measuring the waviness Grisha reported

Call of 9.11: the hall looks "волнистый" — rack tops, the forklift and the floor undulate. The overview
plate is a GPT restyle of one Blender hall (`blender-v1/warehouse.py`), and the restyle is what bends
straight architecture: the render's posts, beams and floor joints are straight, the paint is not.

`geometry-drift.py` measures that drift: it puts the 1536-wide render plate (`desk-ref.png` from the
v10 pipeline) onto the game plane with the `export.py` mapping, then block-matches plate against render
(normalised cross-correlation, 1/4 grid, blocks that are low-contrast or weakly matched are dropped).

```
python3 design/scene-03/geometry-drift.py public/scene-art/inventory-master-v11.webp .tmp-work/r20/drift
```

Writes `geometry-drift.json` (per-region drift) and `geometry-drift-overlay.png` (render edges in red,
plate→render displacement in blue, vector ×6). Values measured on 10.11 for `inventory-master-v11.webp`:

| region | blocks | mean drift | p95 | max |
| --- | --- | --- | --- | --- |
| hall | 640 | 4.94 px | 20.4 px | 28.3 px |
| rack row left (А–Б, В–К) | 79 | 5.95 px | 21.7 px | 28.3 px |
| rack row middle (Л–М, Н–У) | 109 | 4.71 px | 20.0 px | 23.3 px |
| rack row right (Ф–Э, Ю–Я) | 104 | 4.92 px | 22.9 px | 28.3 px |
| floor in front of the racks | 151 | 7.13 px | 23.3 px | 28.3 px |
| façade and windows | 152 | 6.27 px | 20.4 px | 23.3 px |

Drift is the displacement of painted structure relative to the straight render, so 0 would mean the
paint follows the render exactly. The floor drifts most, which matches "пол волной".

## Why it is not fixed by a warp

Warping the plate by the smoothed negative field was tried and rejected: p95 drift fell from 20.4 px to
about 14–17 px but mean drift stayed at 5 px, and the block field is not reliable enough to warp art with
(it matches cartons by texture, not geometry). A warp that cannot be shown to straighten the paint is not
worth shipping on a plate people look at closely.

The straight geometry has one source — the render — so the honest fix is to redo the restyle step against
it, exactly as in `v10/README.md`, and re-run the checks:

```
cd design/scene-03/v10 && ./gen.sh desk 2048x1360 p-plate.txt && ./gen.sh tall 1600x2000 p-plate.txt
python3 compose.py desk 1536 1024 && python3 compose.py tall 1200 1500 && python3 export.py
```

That needs the gateway's reference-image route, which returned HTTP 502 for every model and size on
10.11 (see the note in the revision log). Re-run `geometry-drift.py` afterwards: the aim is mean drift
under 2 px in the hall, not just a tidier p95.
