# Painted trailer integration

`trailer_style.py` merges the frozen `wheels-base.blend` into `merged.blend`. It changes trailer paint and removes the green box's mismatched overlay dividers and roof slabs. The original continuous green trailer shell remains. Cab geometry, crew, suspension vibration, exhaust, routes, wheels and scene camera are inherited unchanged.

The packed ImageGen texture is `textures/trailer-painted-albedo-imagegen.png`; provenance is stored beside it. The neutral broad painted variation modulates the existing four palette colors around a multiplier of 1.0. It is sampled in shared trailer-root coordinates through three orthogonal projections whose scalar values are averaged independently of face normal. Equal 3D positions therefore receive equal paint values across roof, sides and ends; sampling stays inside the image rather than assuming a seamless tile. The original normal-based shading remains.

The green roof gaps and side dividers previously had different longitudinal positions and different materials. Nine overlay objects are hidden reversibly. Existing blue ribbing and the worn red/yellow canvas geometry remain, with their own original palette colors.

Canonical source checks are in `trailer-style-validation.json`. Wheel geometry and material persistence checks are documented separately in `WHEEL-GEOMETRY.md`. Tight wheel-contact planes are included once in the color render and excluded from the broad projected SUN caster pass.

The review sequence uses source frames 97–192 at 24 fps. Full-map rendering uses the unchanged source camera at 1920×1334. `export_anchors.py` verifies a stationary camera and fixed world landmark, then defines constant world rectangles for red, green and yellow closeups. Optional chassis-follow diagnostics use floating-point affine resampling without per-frame rotation or scale. The fixed-world closeup is the primary camera-stability proof.
