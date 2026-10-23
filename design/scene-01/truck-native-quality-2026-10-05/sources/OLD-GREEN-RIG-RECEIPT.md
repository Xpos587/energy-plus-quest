# Existing green truck replacement contract

Read-only measured with Blender 5.2.2 background, `--disable-autoexec`, from `design/scene-01/controlled-motion-2026-10-04/v2b/controlled-straight-start.blend`. No save or runtime change. Evidence: `old-motion-inspection.json`, `old-green-contract.json`; inspectors alongside them.

## Roots, motion and axes

Green is truck **3**, confirmed material `FIX cab 3`: Principled Base Color RGBA `(0.16, 0.43, 0.30, 1)`.

- Tractor root/pivot: **`truck-3-tractor`**, unparented EMPTY, uniform scale **1.122**. Frame 1 world location `(29.8, 20.124311, 0)`, rotation Z `1.570796` rad.
- Trailer root/pivot: **`truck-3-trailer`**, separate unparented EMPTY, same scale. Frame 1 location `(29.8, 17.543711, 0)`, rotation Z `39.268574` rad. Rotation is unwrapped; preserve its exact action rather than normalize Euler angles.
- Their actions `truck-3-tractorAction` and `truck-3-trailerAction` each have six curves (XYZ location, XYZ Euler), **1153 LINEAR keys per curve**, frames 1–1153. Scene range 1–1152 at 24 fps. Neither root has constraints or drivers. Motion/articulation is baked independently into both roots; trailer is not parented to tractor.
- Root-local axes: **+X forward, Y across truck, +Z up**. Front grille/bumper around X=1.5, rear axle X=-2.1. Fifth wheel local location `(-2.3, 0, 0.95)`. Trailer root origin matches the fifth-wheel XY attachment behind tractor by 2.3 local units (2.5806 world units).

## Geometry envelope (root-local, before root scale)

| Component | Name | Bounds min → max |
|---|---|---|
| Cab shell | `3 formed enclosed cab` | `(-0.85,-0.90,0.65)` → `(1.48,0.90,3.08)` |
| Chassis | `3 ladder frame` | `(-2.70,-0.60,0.53)` → `(1.40,0.60,0.77)` |
| Trailer body | `3 long semitrailer` | `(-6.80,-0.91,1.01)` → `(0.70,0.91,3.27)` |

Cab shell size local `(2.33,1.80,2.43)`; after root scale `(2.61426,2.01960,2.72646)`. At frame 1 cab world AABB is `(28.7902,19.17061,0.7293)` → `(30.8098,21.78487,3.45576)`. Cab object has identity local transform and identity parent inverse; its geometry contains its offset from root.

Wheels: `3 seated tire` through `.003` are direct tractor children. Front pair centers `(0.77,±0.73,0.44)`, rear pair `(-2.10,±0.73,0.44)`. Tire diameter 0.86 local, width 0.28, bottom Z=0.01; world diameter 0.96492. Tire object rotation X=π/2, scale 1. Wheels have no actions/drivers. Corresponding hubs: `3 recessed hub`, `3 hub center` and suffixes; rim recess meshes directly parent tractor.

Trailer wheels `3 seated tire.004`–`.009` are trailer children; axle X positions -4.48, -5.35, -6.22, same Y/Z and dimensions.

Other cab-specific children to hide when substituting a complete cab: `3 bumper`, `3 radiator inset`, `3 grille louvre` (+.001–.003), `3 windshield`, `3 side window` (+.001), `3 door handle`, `3 door seam`, `3 mirror arm`, `3 close-set mirror` (each +.001), `3 recessed step` (+.001–.003), `3 lamp housing` (+.001), `3 roof aerodynamic deflector`. Preserve frame, fuel tanks, mudguards, fifth wheel and wheels unless new geometry intentionally replaces them.

Two existing crew meshes per person are also direct tractor children: `FIX crew driver torso` local `(0.28,-0.48,1.72)` and `FIX crew driver head` `(0.40,-0.48,2.14)`; `.001` versions use Y=+0.48. Their materials and world bounds are in full inspection JSON.

## Camera and safe integration

Active `desktop`: ORTHO scale **111.8**, location `(1.774149,-84.676872,131.331421)`, Euler `(0.574134,≈0,0.079830)` radians; no animation/constraints. Do not change for rig preservation.

Import GLB into a new cab-only container, orient it +X forward/Z up, fit to the shell envelope above with wheels/chassis kept, and place in tractor-root coordinates. Parent its container to **`truck-3-tractor` with identity parent inverse** after establishing local transform. Preserve both root transforms/actions unchanged; do not reparent the trailer, overwrite animation, apply root scale, or use imported world bounds as local dimensions. If GLB includes wheels/chassis, remove/hide those duplicates rather than covering retained rig wheels. Verify crew remains visible through real windshield openings/transparency: a closed image-to-3D shell may conceal them.

Sample root transforms at frames 1,120,240,576,1152 are in `old-green-contract.json` for replacement readback.
