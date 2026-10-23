# Lastmile choice outpaint v1 · 2026-10-01

Scope: local boat/Alva choice scene. Delivery outcomes unchanged.

Built-in imagegen edited the approved `lastmile-boat-v22-pilot.webp`. Original asset retained. Outputs are generative extensions, not pixel-identical copies.

Assets: `public/scene-art/lastmile-family-v1/lastmile-choice-wide-v1.webp` (1983×793), `lastmile-choice-tall-v1.webp` (948×1659). Geometry and transport anchors: `src/scenes/lastmile/expandedArtwork.ts`.

## Prompts

Wide: Outpaint this approved game image HORIZONTALLY ONLY to a panoramic canvas of 2560x1024 (2.5:1). Preserve original scene centered at full original height, occupying central 71% width. Add about20% original width each left and right. Must show all original objects, their size and relative positions unchanged: helicopter without blades, helipad, barge/gift, pipe carrier, orange eightwheel rover, blue robot, modular ABK, Alva. Extend river/quay/autumn land to left and right; no additional objects or buildings. No change to camera elevation, crop, style or texture. Clean crisp bright 2D same palette. No border. This is horizontal expansion not zooming or rearranging. Output wide panorama.

Tall: Outpaint vertically this exact approved landscape illustration into a PORTRAIT 1024x1792 canvas (4:7 ratio). Keep the COMPLETE original picture across full width in the middle band, at y=608 to y=1184 approximately. Do not crop left or right. Extend terrain ABOVE and BELOW only: winding river, autumn marsh and concrete quay continue naturally. All original vehicles, gift/barge, bluewhite ABK, Alva, helicopter without rotor blades stay identical shape, sizes relative to one another, arrangement and perspective. Do not introduce buildings, people, transport or new gameplay objects. No border, no letterbox, no empty bands. Clean sharp 2D illustration with same exact colors and light. Output must be tall portrait with extensive newly illustrated environment top and bottom, not square. Original scene roughly middle third of height.

## Verification

Live screenshots inspected at 1440×900, 390×844, 320×568, 768×1024: image fills illustration viewport; transport markers and rotor overlays follow the new art. Header and choice controls remain outside the illustration. Independent visual review found no severe scene-logic or identity issues; this is not stakeholder approval. Type checking and app build pass. Existing scenario/artwork tests: 45 passed after updating the expected choice asset.
