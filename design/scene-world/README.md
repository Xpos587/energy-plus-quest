# Reused truck and detailed canonical warehouse

This candidate uses Blender asset reuse, not a procedural ThreeJS reconstruction or generation service. Approved CC0 IndustrialPack FBX props are imported as data, not recreated. img2threejs informed reference decomposition, a detail inventory and source/candidate multiview comparison. The original pass-06 orange truck is recognizable by its formed cab, grille, glass, mirrors, steps, tanks and five-axle arrangement; its independent copied meshes/materials are measured in provenance.

## Reproduce

From the repository root, with Blender 5.2.2 LTS, Python and Pillow:

```sh
blender -b -t 4 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/build.py
blender -b -t 4 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/import_props.py
blender -b -t 4 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/render.py -- compact-desktop compact-mobile inventory-desktop inventory-mobile
blender -b -t 4 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/review.py -- --source
blender -b -t 4 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/review.py
blender -b -t 2 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/audit_master.py
python scripts/scene-world/export.py
python scripts/scene-world/test_world.py
python scripts/scene-world/display_review.py
python scripts/scene-world/handoff.py
```

`build.py` opens the read-only source and saves only `design/scene-world/quest-world.blend`. It calls `reuse_truck.py` and `warehouse_detail.py`. Original source-local geometry, transforms, parenting and material assignments are retained. The deep-copied tractor and trailer are uniformly scaled, with coincident fifth-wheel/kingpin centers. Only the copied trailer enclosure loses its near wall and roof; original rails, rear doors, locking bars, chassis, wheels and under-run bar remain. Rounded rubber shoulders, tread, rim lips, sidewall beads, lugs and attached axles augment rather than replace the source wheels. The two copied rear mudguards are lowered 0.06 local units to clear both tires and the exposed trailer floor; their original mesh data is retained.

The warehouse retains the actual dock facade, shutters, canopy, approach and footprint. Existing racks receive bracing, load beams, pallet slats/runners, protection and selected open picking bins. New service framing, cable trays, luminaires, ventilation, lane markings, bollards, receiving pallet/jack, WMS/scanner fittings and drone landing/optical/propeller-guard details remain subordinate to clear aisles. The opaque warehouse shell is hidden only for inventory cutaway views. Compact actor/cargo are hidden in inventory views to avoid unrelated clipped foreground geometry.

## Evidence

- Read-only source: `public/review/map-geometry/pass-06/city.blend`, SHA256 `15de029833dcaf5beb806e2df2733763d97199c40f8955f240d93118dc6217bd`.
- `provenance.json`: source hash, 176 copied truck mesh hashes before/after adaptation, original material names, camera projections and packed fonts.
- `reuse-review/master-audit.json`: independent source-versus-saved-master comparison, 669 unchanged crane/lastmile object/camera checks, independent datablocks, wheel/mudguard clearance, coupling and 22 cargo-containment checks. The delivered baseline is canonicalized by vertex coordinates and polygon corners (Blender sphere vertex indices can differ between identical rebuilds).
- `validation.json`: 110 categorical rendered mesh/mesh-group visibility checks and anchor-ray gates; `test_world.py` retains framing, dimensions, mesh visibility, packed Cyrillic labels and 44px non-overlap checks at a 320px image plane.
- `reuse-review/comparison-{front,rear,side,wheel}.png`: paired controlled Blender renders against the actual source actor; `display-{desktop,mobile}.png`: final-size plain renders alongside 44px target overlays. These are rendered image-plane reviews, not browser screenshots.
- `reuse-review/baseline-hashes.json`: unchanged crane/lastmile image hashes. Their geometry/cameras are not edited, their manifest entries are retained, and none of their runtime or structural images are rerendered/exported.

The build packs font/assets into the single master. Source/candidate review renders use matching cameras and lighting, and never save the source file. The actual CC0 PalletTruck, CableDrum and ElectricalBox meshes and original UV-mapped base-color/roughness/metallic textures are included. Their FBX files and only the nine used PNG maps are under `assets/industrial-pack`, alongside `LICENSE.md` and the author-page license evidence. All textures are also packed into the master. Normal/height maps are deliberately omitted; no DirectX green-channel ambiguity is introduced. No full archive is shipped.

## Handoff and limits

`handoff-files.json` is the exact changed-file allowlist with hashes; copy only its files and the allowlist itself. Logs, caches and unchanged crane/lastmile files are excluded. Parent must synchronize the two changed scene projection entries into `src/scenes/worldManifest.json` after visual approval; that frontend file is outside this writer's ownership.

These remain simplified industrial reference assets, not photoreal final art. Small lug/vent/pallet details are demonstrated in closeups and do not all resolve on a 320px overview. Overview labels remain backed by accessible interface text. The inventory roof removal is a presentation cutaway, not a new building. No frontend/browser approval, staging, commit or deployment is implied by Blender and structural checks.

## Approved CC0 follow-up

The first handoff missed the queued approved-prop steer. This handoff imports the actual models by 3dmodelscc0 from https://3dmodelscc0.itch.io/free-cc0-industrial-3d-models (CC0 public domain). `import_props.py` updates the existing master directly without rebuilding the truck; run it after `build.py` for a full rebuild. It replaces the procedural pallet jack, moves the receiving pallet into the rear staging bay, and adds the drum and wall-mounted electrical cabinet outside the marked aisle. The cabinet warning face points into the room.

For this follow-up only inventory views were rerendered:

```sh
blender -b -t 4 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/import_props.py
blender -b -t 4 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/render.py -- inventory-desktop inventory-mobile
blender -b -t 4 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/review_props.py
python scripts/scene-world/export.py inventory
```

`reuse-review/imported-assets.json` identifies all ten imported mesh parts, placement bounds, UV counts, source filenames and SHA256 hashes. `imported-pallet-jack.png` and `imported-service-props.png` are actual contextual closeups read during review. The new test checks imported asset hashes and rendered visibility, plus byte-identical compact/crane/lastmile images against the pre-import snapshot.

## Short-landscape compact anchor repair

Parent browser review exposed a 568x320 layout whose mobile image plane is only 229.5x255px. The previous 320px-wide gate did not cover it. `compact_anchors.py` now provides shared semantic cargo-space anchors for full builds and incremental repair. Choices 2 and 4 are lowered 1.2 world units, remaining above the dishes and within the gap beside the pillows. Choices 1 and 3, wall plaques, all meshes, materials, cameras and approved images remain unchanged. Four non-rendered `compact choice place-*` empties persist these points in the master.

```sh
blender -b -t 2 --disable-autoexec --python-exit-code 1 --python scripts/scene-world/update_compact_anchors.py
python scripts/scene-world/test_world.py
python scripts/scene-world/display_review.py
```

The added regression failed before the repair (41.654px), then passed. Adjacent mobile center distances are 46.440, 46.608 and 47.419px at the actual 229.5px width; minimum desktop distance is 55.750px at 320px width. The original 320px rectangular separation gate remains intact. `compact-anchor-validation.json` records all pairs and unchanged hashes for all 40 approved scene PNG/WebP files. Eight independent saved-empty projection checks pass in the master audit. `compact-short-landscape.png` is a fitted image-plane review, not a browser screenshot. Parent must recopy the compact manifest entries and run the final browser gate; no scene rerender was required.
