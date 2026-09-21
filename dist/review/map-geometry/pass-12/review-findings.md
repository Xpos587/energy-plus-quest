# Pass12 review findings

## Repaired findings

Paths below use source root `/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-12`.

- High, repaired — `repairs.py`, `city-repaired.blend`: two HVAC units intersected skylights. Relocated only those units to the rear roof zone; saved-mesh checks require 0.5m clearance from skylight curbs and parapets. Six skylights remain.
- High, repaired — `repairs.py`: removed four incompatible west-tower loggia assemblies, retaining the six-floor window system. No building mass or footprint change.
- High, repaired — `repairs.py`: both commercial facades reserve the central entry; six contained, separated ground-floor glazing panels replace overlapping panels. Southern upper windows remain separate. Tests inspect each cube in batched facade meshes, not the batched bounding box.
- High, repaired — `repair_layout.py`, `repairs.py`: removed inaccessible warehouse-facing zebras and consolidated the east-road pair. Further landing tests exposed a west-of-yard crossing with the same 0.05m pavement defect; it was removed too. The retained east crossing has two 1.3m landings. Its obstructing lamp moved 1.2m along the pavement. The saved scene contains 48 local dropped-curb ramps.
- High, repaired — `repairs.py`, `check_crew.py`: truck3 originally showed the cab rear. The common static southbound test pose exposes the true front windshield. Two modeled seated people now sit in an actual cabin opening. A second-ray check caught an inward-normal Boolean cutter leaving the opaque shell behind glass; recalculating cutter normals fixes it. Rays now hit windshield, then each head.
- High, rejected before publication — `base-job.json`, `a-job.json`, `b-job.json`, `c-job.json`: whole-frame generation shifted structures and omitted the consolidated crossing. Those whole frames were not accepted as final art. `compose_base.py` and `finish_variants.py` admit only recorded source-guided patches and rigidly registered architectural paint regions; warehouse frontage, doors, bay markings, fences, roads and trucks remain a controlled common base.
- Medium, repaired — `public/review/map-geometry/pass-12/compare.mjs`: a root `data-variant` attribute collided with button selectors after the first switch. Replaced it with `data-active-variant`; all four switches now pass on five viewport sizes.

## Final visual review

Inspected all four supplied brandbook images, both independent reports, the annotated screenshot, immutable professional portrait, pass11 control, repaired guide, all three generated candidates, final paintings/crop boards, final contact sheet and desktop/mobile browser screenshots. Final source-driver closeup shows two actual heads behind the front glass. Final art shows natural skin and clothing under reflected glass, rather than black symbols.

Visible final invariants: six warehouse doors / seven bay boundaries, connected fence and original gate, six clear rooflights / two separated HVAC boxes, six tower floors without pseudo-loggias, separate storefront entries, upper business-center windows above ground-floor glazing, no warehouse-facing dead-end crossing, one retained east zebra, four numbered trucks. Source preservation test proves 74 protected saved objects and the camera are unchanged. Fence route check covers 3,072 original motion frames with a 0.3194m minimum truck/fence clearance. The new static truck3 pose has 0.6188m road-edge clearance and 0.9946m / 0.8900m clearance to adjacent crossings.

## Residual risks and deliberate limits

- Medium, style scope — `map-a.jpg`, `map-b.jpg`, `map-c.jpg`: these are three real architectural drawing/painting treatments, not three unrestrained whole-city redraws. Roads, foliage, vehicles, fence and approved warehouse front deliberately remain common to prevent structural regressions. A emphasizes ink; B emphasizes opaque modeled planes; C emphasizes dry-brush surfaces. This limitation is stated in the page and manifest.
- Low, compositing — `common-base.png`, `base-repair-mask.png`: local road removal is a deterministic retouch. At extreme enlargement its texture may look smoother than surrounding paint. It is not a replacement for a fully authored production background.
- Review required — stylistic compatibility is subjective. A may still feel more architectural than the character; C is intentionally looser. No option is claimed approved.
- Out of scope — static vehicles plus animated exhaust only. The new truck3 test pose is not integrated into the preserved pass07 motion routes. No production-game changes.

## Verification evidence

- `scene-check.json`: saved source passes roof, storefront, floor/loggia, crossing, ramp, furniture-clearance and crew-count checks; old source fails.
- `preservation-check.json`: 74 actual saved objects/camera unchanged.
- `geometry-check.json`: two warehouse-rooted fence chains, 9.3m gate, 3,072 original frames clear.
- `crew-visibility.json`, `truck3-check.json`: true front-glass visibility and static pose clearance.
- `dock-check-a.json`, `dock-check-b.json`, `dock-check-c.json`: seven painted boundaries with six door centers between them.
- `check_artifacts.py`: different architecture, identical crew, original character bytes, RGB-identical cutout, no registration edge holes.
- `smoke.test.mjs`: 769 deterministic samples, correct old-truck anchors, bounded opacity/drift.
- `validation.json`: five viewport sizes, A/B/C/11 switches, stable zoom, reduced motion, animation pause/play, no overflow, local HTTP bytes, unchanged pass07/09/10/11 and character hashes.
