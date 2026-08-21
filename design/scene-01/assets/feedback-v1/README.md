# Feedback v1 media

Built for the 2026-08-17 Edik feedback revision with `scripts/build-feedback-assets.sh`.

## Source roles

- `map-v2-desktop/edited.webp`, `map-mobile/edited.webp`: edit targets; road and hotspot geometry preserved, contrast reduced.
- `choices-v2/professional.webp`: edit target; restrained maturity cues added while preserving identity and pose.
- `choices-v2/khor.webp`, `choices-v2/boat.webp`: accepted v2 edits versioned into the feedback set because they already satisfy the full-frame reindeer and practical workboat notes.
- `carriers-cutout/*.png`: edit targets; normalized and differentiated as worn, ordinary, two-driver, and clean Express vehicles.
- `choices-v2/alva.webp`, `choices-v2/camera.webp`: compositing inputs for the representative Express consequence.

## Prompt-equivalent art direction

Use case: precise-object-edit and compositing. Asset type: game choice art, map controls, and illustrated outcome. Preserve the Energy+ orange/blue palette, paper texture, existing road geometry, character identity, and card-facing composition. Make the map quiet and the vehicles primary. Show the old carrier as worn with a small smoke cue, the ordinary carrier as visually modest, the crew carrier with two visible people, and Express as a clean orange vehicle with neutral text only. The Express outcome should feel warm and human: the vehicle reaches Alva with the selected camera safely in transit. Avoid invented corporate logos, unrelated text, new product claims, photorealism, and copied game-reference art.

## Method

Local ImageMagick raster editing/compositing. The built-in image generator was unavailable in this environment; no API fallback or fabricated branding was used.
