# Scene 1: scenario-led recovery, 7 October 2026

> Исторический рабочий материал: его формулировки и решения не являются актуальным сценарием. Единственный сценарный источник — [редакция 08.10](../../../docs/scenario.md).


## Purpose

The player must infer different carrier tradeoffs from age, smoke, actual movement and crew. Trailer decoration or four different paint colors is not sufficient. v14/v15 are rejected visual directions, not approved references.

## Binding sources

- [Актуальный сценарий](../../../docs/scenario.md), especially lines 15–30: red/#1 and yellow/#4 are old, battered and smoking, in different areas, with different speeds; blue/#2 moves very slowly near the office; green/#3 is new, shining, has two drivers and takes a broad perimeter route. Original 1709 DOCX is linked there.
- [29 September meeting](../../../materials/private/meeting-2026-09-29/summary.md): test with people unfamiliar with the story/mechanics; do not confuse broad style feedback with approval of every frame.
- [29 September style interpretation](../../../materials/private/meeting-2026-09-29/style-feedback.md): align the existing visual family rather than invent another direction. Attribution is not reliable enough to treat every sentence as a direct Fedya quote.
- [2 October meeting](../../../materials/private/meeting-2026-10-02/summary.md): Fedya absent; player feedback showed speed/year/crew rationale unclear. This is player evidence, not a new Fedya approval.
- User decisions in this thread: colors instead of numbers; fully colored trailers; detailed cabins; soft shadows/no black outlines; visible age/smoke/speed rather than decorative roof differentiation. Latest user reminder requires the scenario and all accumulated feedback together.

Available post-25-September archives found: 27 September, 29 September, 2 October. No claim that missing later calls were audited. User-provided call notes in this thread remain additional evidence.

## Chosen approach

Keep deterministic Blender routes, camera, warehouse and clean chassis. Restore detailed source upper cabs rather than using the simplified procedural boxes. Separate three checks: physical age in close and map views, causal visible smoke, and different travel speed in a short video. Keep consistent material/light treatment across the fleet and city.

Existing alternate Volvo FH is modern and does not by itself solve old-carrier readability. Wholesale fleet replacement adds assembly, crew, coupling and style work without proving the choice logic. If restored detailed cabins still read as modern, replace only the old upper cabins with a validated old cab asset; do not rework the entire map.

## External asset research

- [KAMAZ 5410 by Excessmensch](https://sketchfab.com/3d-models/kamaz-5410-2ba587c1a7d04a2aab497d7a053eccf8): author page inspected; 492.2k triangles. Download availability and usable license were not established. Not acquired or integrated.
- [MAZ 500 by own.guest](https://sketchfab.com/3d-models/maz-500-b737cc71f2754f368b80ddd215f39b89): author page inspected; downloadable listing, 41.3k triangles, CC BY 4.0. Candidate for old-cab study, not yet downloaded, topology/style not validated and not claimed compatible with our tractor rig.
- CGTrader KAMAZ-5320 search lead could not be read back as page content; no readiness or licensing conclusion.

## v16 proof boundaries

Measured v15 defect: red and yellow both travelled at 6.892904 scene units/s. v16 eight-second proof retimes paired tractor/trailer roots; see [motion receipt](motion-receipt.md). This changes actual travel, not a fictitious km/h label.

The proof is not a seamless loop and does not establish full-loop collision safety. Static geometry and crew preservation checks are separate from visual acceptance. Physical aging remains subject to visual review; restoring detail and passing geometry tests are not evidence of an old-looking vehicle.

Acceptance requires the age/smoke/speed/crew combination to read at map scale, not just on isolated model renders. No production integration or full-loop approval is implied.
