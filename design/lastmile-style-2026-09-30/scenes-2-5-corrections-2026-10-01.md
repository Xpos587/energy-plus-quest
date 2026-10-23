# Scenes 2–5: visual corrections · 2026-10-01

> Исторический рабочий материал: его формулировки и решения не являются актуальным сценарием. Единственный сценарный источник — [редакция 08.10](../../docs/scenario.md).


Scope: all scenes except first; remove letterboxing through meaningful crop, preserve important choices. Portrait extension only where cropping hides choices. UX ownership: task 01a0e848-0314-7590-ac6d-6ed20f22e9fc. Local site only.

## Scenario constraint

Canonical DOCX: `docs/scenario.md`. Explicit visible contents requirement applies to compact socks/camera (`src/scenes/implementationText.ts:65,75`), not all scenes. Warehouse alphabet retains Н/Л/Ф and corresponding location (line 510). Crane wait leaves gift at quay, barge departs with pipes (725). Helicopter has flight plus onward ground delivery for Alva/Khor (915,920), not obligatory onward leg for Arseniy. Existing scenario text is unchanged.

## Art

- `public/scene-art/barge-family-v1/wait-socks-v2.png`: closed neutral carton, physically coherent hand trolley moved clear of quay edge.
- `public/scene-art/outcomes/inventory-alphabet-socks-v9.webp`: closed carton, natural two-handed grip; removes inconsistent visible socks; Н retained.
- `public/scene-art/lastmile-family-v1/lastmile-choice-wide-v2.webp` and `lastmile-choice-tall-v2.webp`: repaired continuous hull; two full longitudinal rows of strapped pipes based on `barge-family-v1/rush-boat-v1.png`; folded gift and motor at bow. Replaces incorrect sparse cargo.
- `public/scene-art/inventory-choice-tall-v1.webp`: vertical architectural extension, retained warehouse options.
- `public/scene-art/barge-family-v1/choice-parcel-tall-v1.webp`: vertical quay extension, generic closed parcel instead of per-gift full scene generation.

Method: built-in imagegen local edits/outpaint; original assets retained. Prompt constraints: edit only carton/cart or vessel; preserve surrounding scene, colors, faces, uniforms and geometry. Vessel reference required two densely loaded longitudinal pipe rows filling hold, gift at bow. Portrait prompts required full original scene in central band, extending environment above/below without new gameplay objects. Generic parcel prompt replaced only gift on trailer with taped neutral carton. Lossless WebP conversion for runtime assets except versioned PNG crane family.

Independent reviewer found no severe hull/cargo continuity or carton/cart contact defects. This is not stakeholder approval. UI/framing integration and live checks reported separately by UX task.
