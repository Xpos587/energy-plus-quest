# MAZ 500 inspection result

The imported source is visually viable for a detailed old-cab extraction study. Inspect `maz500-q2.png` for front three-quarter and `maz500-top.png` for top view; q1 is rear three-quarter. These are actual imported geometry renders, not the author's preview.

Visible old-cab cues: lower rounded cab shell, split front windscreen, round headlamps, simple horizontal grille, thin roof, small mirrors and prominent wheel arches. Door handles, wipers, roof seams/marker lights, glazing, seats and wheel tread are modeled. This has substantially more physical detail than the rejected primitive cab direction. There is no driver in this source.

Blender import measured 20 mesh objects, 41,106 triangles and 10 materials. Materials have no texture-image nodes. Whole source world bounds are recorded in `asset-inspection.json`; per-object world bounds and connected components in `component-inspection.json`.

Cab faces negative world X. Painted cab pieces `Object_3` and `Object_4` use `standard1`; their combined bounds are approximately X -5.264 to -2.792, Y -1.552 to 1.552, Z 1.072 to 3.377. They are separate from the chassis, so core shell extraction is straightforward. Glass and lamps also have separate material objects. Dark rubber/trim/chassis geometry is grouped by material and spans the vehicle: do not copy all dark objects into the cab. An extraction must filter spatial regions or components, preserving seals, wipers and interior while excluding tyres, spare wheel, fuel tanks and chassis. Numerous disconnected components reflect split mesh vertices; naive largest-component selection would destroy detail.

Integration remains unperformed. Next authorised study would extract cab pieces, remove manufacturer badge, recolor red/yellow, fit to the preserved v16 chassis, and reposition each existing single driver behind appropriate glass. Cab-to-wheel-arch alignment and real map-scale age readability require renders before acceptance. Workbench material display does not validate final glass transparency or lighting.

`maz500-isolated-study.blend` is the isolated imported source with study camera. `inspect_asset.py` reproduces import, report and five 1200 × 1000 stills; `inspect_components.py` writes the extraction diagnostics. Production and v16 source files were not changed.
