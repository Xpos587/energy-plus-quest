# Whole-map candidate v07

Review entry: [preview-v07.html](preview-v07.html). Portable review: [energy-plus-map-v07.pdf](energy-plus-map-v07.pdf). Full cycle: [whole-map-v07.mp4](whole-map-v07.mp4).

This is a new render candidate, not stakeholder approval or a production replacement.

## Sources and changes

- Background: the retained city composition, with a local warehouse/apron repair. Warehouse style reference: `../style-audit-2026-09-28/reference.png` from the `design` root; canonical absolute project path is `design/style-audit-2026-09-28/reference.png`.
- Geometry: `fleet/fleet-textured-v07-fast.blend`, derived from `fleet/fleet-textured-v07.blend`. Cabin upper-body proportions increased while rear hitch geometry and wheel contact heights were retained. Exact geometry changes: [receipt](fleet/textured-v07-receipt.json).
- Green uses the two-occupant windshield; the other trucks use the single-occupant windshield. Old red/yellow have lower cab roofs and beige trailers. These are approximations of the approved cards, not exact historical cab reconstructions.

## Verification

- 1152 PNG frames validated with Pillow, all 1920 × 1334. Fleet layer rendered at this resolution; retained background originates at 1505 × 1045.
- ffprobe confirmed encoded output 1920 × 1334, 24/1 fps, 1152 decoded frames, duration 48.000000 seconds.
- All eight animated rig-root matrices, camera and actions remain unchanged across the complete timeline: [verification](fleet/textured-v07-verification.json).
- Conservative ground-footprint SAT found no truck-to-truck overlap candidates in 1152 frames: [receipt](fleet-overlap-v07.json). This does not certify illustrated-building registration.
- Local preview HTTP 200. Browser UI was unavailable in the resumed session; do not claim the preview was opened live.
- Gemini processed the actual 48-second video and its uploaded copy was deleted: [receipt](video-v07-review-receipt.json). Its repeated four-second collision assertions and fixed-trailer assertion are not accepted as evidence. Locally decoded 2/4/8-second frames contradict the stated red/green collision at four seconds; separate rig rotations and rendered turns contradict fixed trailer orientation. Retain the raw review as hypotheses only.

## Remaining visual limits

Cabin/trailer proportions improved without visible deformation in the inspected stills. The high-detail cab/chassis and windshield faces remain more realistic than the illustrated city, especially at close zoom. Articulated turns expose a conspicuous chassis gap. Exact old/new vehicle identities and close-up style still need refinement before final approval. City/vehicle registration is not certified at every building corner. Browser/mobile zoom review remains open.
