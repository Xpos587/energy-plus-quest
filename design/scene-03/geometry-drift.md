# Scene 3 warehouse: measuring the waviness Grisha reported

Call of 9.11: the hall looks "волнистый" — rack tops, the forklift and the floor undulate. The overview
plate is a GPT restyle of one Blender hall (`blender-v1/warehouse.py`), and the restyle is what bends
straight architecture: the render's posts, beams and floor joints are straight, the paint is not.

`geometry-drift.py` measures that drift. It puts the 1536-wide render plate (`desk-ref.png` from the v10
pipeline) onto the game plane with the `export.py` mapping, then block-matches plate against render on
gradient-magnitude maps (normalised cross-correlation, 1/4 grid, low-contrast and weakly matched blocks
dropped) so paint texture does not decide a match.

```
python3 design/scene-03/geometry-drift.py public/scene-art/inventory-master-v11.webp .tmp-work/r20/drift
```

Writes `geometry-drift.json` (per-region drift) and `geometry-drift-overlay.png` (render edges in red,
plate→render displacement in blue, vector ×6). Values measured on 10.11 for `inventory-master-v11.webp`;
the global median displacement is 0/0 px, so the mapping itself contributes no bias:

| region | blocks | mean drift | p95 | max |
| --- | --- | --- | --- | --- |
| hall | 621 | 4.01 px | 14.4 px | 28.3 px |
| rack row left (А–Б, В–К) | 83 | 4.30 px | 20.1 px | 28.3 px |
| rack row middle (Л–М, Н–У) | 98 | 2.66 px | 6.6 px | 23.3 px |
| rack row right (Ф–Э, Ю–Я) | 100 | 3.44 px | 9.1 px | 17.0 px |
| floor in front of the racks | 137 | 5.83 px | 20.4 px | 28.3 px |
| façade and windows | 163 | 3.62 px | 11.0 px | 23.3 px |

Drift is the displacement of painted structure relative to the straight render, so 0 would mean the paint
follows the render exactly. The left rack row and the floor drift most, which matches "стеллажи и пол
волной".

## Why a warp is not the fix

Warping the plate by the smoothed negative drift field was tried with the sign verified both ways
(mean drift in the hall 4.01 → 3.17 px over four passes, middle rack row 2.66 → 1.63 px). The 100% crop
then shows local hiccups in the rack posts and a slightly swirled floor, and the hand-drawn bulges in the
cartons and the uneven post spacing — the parts that read as "волнисто" — survive untouched. A warp that
trades a measured 0.8 px for visible artifacts is not worth shipping on a plate people look at closely.

Outcome (10.11): the Keyrelay reference route stayed down (HTTP 502 for every model), so the plates were redrawn
through the Higgsfield CLI instead, with the v11 plate as Image 1 and the straight Blender render as Image 2.
Wide (`inventory-master-v12.webp`): `nano_banana_pro` 3:2, prompt "all edges straight, boxes as crisp rectangles,
floor with straight slab joints, keep composition, people, lettering" (cleanest straight edges, flatter floor).
Tall (`inventory-master-v12-tall.webp`): `nano_banana_2` 4:5 on the top 1500 rows, prompt asking for smooth floor
and painterly shading (`nano_banana_pro` flattened the tall plate to a vector look); the bottom 250 rows of v11
are kept with a 60-row blend. Object positions match v11, so hotspots/contours/alphabet.ts are unchanged
(only the `source` field and the test regexes moved to v12). The drift metric above was not re-run: the
decision was a visual review of 100% crops.
