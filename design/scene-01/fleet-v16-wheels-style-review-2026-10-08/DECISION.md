# Wheel motion, ground contact and trailer paint

User scope: visible wheel steering/rolling, coherent tractor/trailer wheel family, grounded vehicles, consistent green trailer panel joins, and an ImageGen broad painted trailer texture. Preserve v16 map/warehouse/cabs/colors/crew, accepted suspension and smoke. No whole-frame generation.

Base: `../fleet-v16-cab-repair-2026-10-08/fleet-v16-cab-repair.blend`.
Candidate: `../fleet-v16-wheels-style-2026-10-08/`.

Front tractor wheels steer from route curvature; all wheels roll from traveled distance and radius. Ordinary trailer axles remain non-steering; the trailer turns through its articulation. Keep tire contact and cab clearance throughout turns. Inspect actual temporal images because symmetric rim patterns can alias at 24 fps.

Green trailer roof/side overlay seam spacing was inconsistent; correct geometry rather than hiding it with a texture. ImageGen texture provenance is in the candidate's `textures/PROVENANCE.md`; use shared trailer-local mapping and retain the four carrier colors. Broad contact shadows need a separate tight tire contact component to avoid a floating appearance.

Use native-size map and close turn/rolling proofs before any full-loop or production integration. Do not claim game media replaced merely because review exports exist.
