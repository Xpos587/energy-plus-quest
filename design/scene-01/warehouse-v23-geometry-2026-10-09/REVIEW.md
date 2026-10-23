# Warehouse v23 — geometry correction for review

Status: approved by Michael and installed in the local main game on 2026-10-09. Full 64-second video recomposed from existing vehicle/shadow passes; no new Blender animation render was needed. Delivery evidence: [DELIVERY.md](DELIVERY.md).

User rejected the v22 warehouse geometry: incoherent layered roof, stretched canopy, warped glazing and poorly arranged loading-area posts. The prior small-scale visual approval was insufficient; inspect the architecture at close range.

References:
- Actual digital warehouse: `docs/scenario-assets/image8.png`, linked by the 08.10 scenario.
- Old coherent volumetric study: `/home/michael/.local/state/energy-plus-quest/research/2026-09-20-warehouse-blender/warehouse-closeup.png`.
- Rejected current crop: `../fleet-v22-warehouse-hq-2026-10-09/city/warehouse-final-crop.png`.

Final artwork: [warehouse-final.png](warehouse-final.png).

Corrections:
- One flat roof plane within a connected low parapet; removed stacked slabs.
- Continuous three-level curtain-wall grid on planar facets.
- Compact wall-mounted blue canopy with lower wall brackets. No vertical canopy posts in the loading approach; no floating upper mounting tabs.
- Three free loading doors and aligned approach rectangles.
- Four short yellow/black bollards at the outside and shared pier axes.
- Existing Газпром нефть / СКЛАД signage retained and visually checked for spelling.

Generation: built-in ImageGen local edit with the three references; a second surgical edit removed only the upper canopy tabs. Originals retained in the generated_images session folder; project copies are authoritative review artifacts.

Independent reviewer: gpt-5.6-sol, medium. Re-review explicitly rejected v22 at close range, then passed the corrected geometry. The final follow-up removed its remaining optional concern about duplicate upper canopy hardware. A still review does not establish final map/composite registration or video quality; those checks follow acceptance of this building layout.

Integration reused the existing native v22 vehicle/shadow frames and replaced only the warehouse region in the static city layer. City pixels outside that rectangle were verified unchanged. Independent composite review passed at close-up and full-map scale.
