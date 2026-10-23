# Warehouse illustration revision — 28 September 2026

`generated.png` is the image generation output. It used `public/scene-art/inventory-zones-v4.webp` as the scene layout and `public/scene-art/crane-v2.png` as the style reference. The shipped `public/scene-art/inventory-barge-style-v5.webp` is a centered 1672×933 crop, resized to the scene canvas (2752×1536) and converted to WebP. The prior warehouse images remain available.

The v5 illustration leaves six rack plaques and the two door plaques blank. The current shipped `public/scene-art/inventory-barge-style-v6.webp` includes exact Cyrillic lettering composited onto those existing plaques in perspective. Reproduce from the repository root with `bun design/scene-world/warehouse-regeneration-2026-09-28/lettering.mjs` (ImageMagick and DejaVu Sans Bold required). `WarehouseZones.tsx` supplies only interactive highlighting; there are no duplicate floating labels.

The image is a style proposal, not a claim of artistic approval. The four outcome illustrations were not regenerated in this pass.
