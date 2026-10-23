# Scene 01 fleet style pilot

> Исторический рабочий материал: его формулировки и решения не являются актуальным сценарием. Единственный сценарный источник — [редакция 08.10](../../../docs/scenario.md).


## Intent

Keep the approved whole city, warehouse and four-truck motion. Bring truck surfaces closer to the approved illustrated scene and make vehicle age, trailer construction and crew count support the player's choice.

## Sources

- Scenario distinctions: [Актуальный сценарий](../../../docs/scenario.md).
- Approved style image: [reference](../../style-audit-2026-09-28/reference.png).
- Before: [v07 map](../whole-map-v06-2026-10-06/map-v07-0001.png).
- Native fleet, old roofs, canvas, exhaust and blue refrigeration: `native/`.
- Illustrated adult crew textures: `textures/`. Green has two; the other three use an identical driver and an empty passenger seat.
- Fixed object-space painted cab texture: `projected/`. The painted camera view supplies UVs on real cab polygons. It is not a billboard or a full-frame generated map.

## Review artifact

`energy-plus-map-v09.pdf`: whole map, before/after, style reference, another route frame and four vehicle enlargements. Rebuild with `uv run --with pillow --with reportlab python package_v09.py` from this directory.

## Verification and limits

`projected/projection-receipt.json` records unchanged camera and root transforms across 1152 frames. The source crew material remains independent from the generated body artwork. The opposite-side render checks that a turn does not make the painting slide as an image overlay.

The review PDF uses `projected/clean/`: continuous lower windshield panels and compact mirrors replace the damaged local body faces. `projected/clean/repair-receipt.json` records unchanged root transforms across 1152 frames, unchanged camera and driver polygons, and preserved existing vertex coordinates. Both frontal and opposite views were inspected. Other source body seams and mechanical textures remain imperfect.

This is a static style pilot. No new complete animation or production asset mapping is applied. At the overview scale, driver count and fine age details still need zoom; canvas versus rigid trailers is more visible. The trucks have moved closer to the illustrated map but complete style consistency and immediate distinction at overview scale are not yet established. No Fedya approval is implied.
