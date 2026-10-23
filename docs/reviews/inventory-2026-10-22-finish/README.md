# Deterministic warehouse finish candidate

For the requested original-style/current-runtime/candidate comparison and mobile pan limits, use the [human review package](HUMAN-REVIEW.md). Fresh 4344 captures are separate from candidate mockups.

Current review candidate: [fixed-plane illustrated preview](rack-worldplane-v1-full-source.png), with [desktop](rack-worldplane-v1-full-desktop.png), [portrait](rack-worldplane-v1-full-portrait.png) and [right pan](rack-worldplane-v1-full-pan-right.png). This candidate is **not accepted for production**. Its structural comparison, local illustration proofs and geometry receipts are review evidence, not runtime acceptance. Canonical `src`, media routing and production assets have not been changed by this finish work. The [user-facing comparison](warehouse-style-user-comparison-pending.png) explicitly marks the pending style verdict.

The combined candidate uses the approved fixed scene plus local illustrated keeper/forklift cutouts, a painted window texture and the existing painted rack asset mapped onto fixed front/right/top world planes. See [keeper proof](KEEPER-PROOF.md), [window proof](WINDOW-PROOF.md), [forklift mapping](forklift-billboard-v1.json) and [native provenance](local-native-receipts.json). The rack billboard trial failed the strict geometry check and remains rejected history; the current world-plane alternative is a separate review candidate. Its limitations include 2.5D camera-only surfaces, repeated stock texture, flattened top stock and a narrow base seam. It is not Flowers reconstruction. The [22 October reset](../../plans/2026-10-22-throughput-reset.md) supersedes mandatory whole-library Flowers work.

Geometry authority: [approved v4 manifest](../../../design/warehouse-blockout-2026-10-21/manifest-v4.json). Style reference: `public/scene-art/warehouse-revision-4-2026-10-18/overview-r4-v11-local.png`.

The original deterministic v1–v3 base used no image generation; later local painted surfaces are linked above. `design/warehouse-finish-2026-10-22/finish.py` opens the immutable v4 scene, applies materials and additive finishing geometry, validates every original mesh vertex, object transform and camera, then saves to this candidate's separate blend file. The keeper's original scale silhouette is hidden and replaced by a rounded uniformed person in the same position; one seated forklift driver is added. Existing truck skin is revealed within its original frame, leaving its rear open. The architectural roof, south wall and dispatch surface cutaway remains explicit.

Full source is 1440 × 1000. Desktop and portrait are exact deterministic source-plane samples using the canonical v4 crop contract. Objects outside the initial portrait remain in the full source for horizontal pan. Lower camera fit is not used to alter the room.

Run:

```sh
blender --background --python design/warehouse-finish-2026-10-22/finish.py
uv run --no-project --with pillow python design/warehouse-finish-2026-10-22/export_views.py
bun design/warehouse-finish-2026-10-22/overlay.mjs
```

Geometry preservation is recorded in `geometry-preservation-v1.json`. Original-coordinate equivalence proves structural preservation, not finished visual acceptance. Parent must review clean desktop and portrait beside the unchanged geometric guides before promotion.

## Later candidates

V2 restores stronger saturated blue/orange materials, changes the guard's visible roof from solid plate to an open grille within the identical envelope, and passes a fresh immutable-source coordinate audit. V2 includes semantic color and surface-normal check passes with explicit limitations in `structural-legend-v2.json`.

V3 moves only the additive driver's upper body 0.23 m toward the camera inside the guard to clear the grille silhouette, and gives camera rays a bright blue backdrop independent of world illumination. Original keeper, wall, rack, gate, truck and camera coordinates stay unchanged. Latest files use `v3`; earlier files remain review history.
