# First-scene controlled 3D experiment

Current review: [PDF v02](review/energy-plus-map-3d-v02.pdf), [preview](review/preview.html), [actual 6-second render](image-to-3d/motion/green-tractor-turn-detailed.mp4).

This is an isolated motion and appearance prototype. It is not the finished four-truck map, a closed loop, or a production replacement. No game component, production scene asset, or runtime manifest was changed.

## Evidence and frozen sources

- Print-kit assembly: [native receipt](native/FINAL-RECEIPT.md). Rejected for visual quality.
- Ready-made models: [source search receipt](sources/ASSEMBLED-FALLBACK-RECEIPT.md). Downloaded CC0 cab-over rejected for wrong identity. The suitable Sketchfab candidate required authenticated download and was not acquired.
- Higgsfield image-to-3D: [completed job](image-to-3d/result.json), [frozen GLB](image-to-3d/green-tractor.glb), [geometry receipt](image-to-3d/geometry-receipt.json). One generation, seed 42, textured, 60k target triangles. Account balance immediately before/after this isolated submission: 707.83 / 677.83 credits, difference 30 credits. No other 3D or video generation submitted by this experiment.
- Illustration finish uses fixed Blender materials, not generative processing of animation frames. Raw reconstruction texture and cab surfaces still need work before production use.
- Two-driver clarity restored via permanent UV projection onto existing windshield faces: [projection receipt](image-to-3d/driver-projection-receipt.json), [packed source blend](image-to-3d/green-tractor-detailed.blend). This is textured 2D interior artwork, not volumetric people. Close-up count/readability does not prove face readability in the whole-maneuver video.
- Motion: [original rig contract](sources/OLD-GREEN-RIG-RECEIPT.md), [all-frame bounds/root verification](image-to-3d/motion/validation.json), [detailed render receipt](image-to-3d/motion/DETAILED-RECEIPT.md). 144 real Blender frames, 6 seconds, 24 fps, 768×640. Tractor translates through a 90-degree turn; trailer follows with separate baked articulation. Single fixed camera, no generative frame interpolation. Integrated GLB wheels do not yet rotate independently; trailer retains 6.38° lag at exit. Not a closed loop.
- Gemini actual-video inspection attempted but blocked at Files API upload by regional HTTP 400. No remote file was created, no Gemini review occurred. [Attempt receipt](review/motion-analysis-receipt.json). Decoded contact sheets and structural verification are the completed checks; do not claim Gemini approval.

## Decision

Controlled motion is demonstrable and repeatable. The generated model is a useful prototype, not accepted final art. Before four-truck rollout: clean cab panels, chassis and wheel materials; separate wheels and preserve steering/rolling transforms; verify actual map camera and 1×/2×/4× display; then test all four identities and road paths together. Keep the frozen illustrated map and approved vehicle references as the art contract. Do not solve surface quality by generating each video frame independently.
