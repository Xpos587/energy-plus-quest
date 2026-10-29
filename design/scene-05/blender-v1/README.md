# Scene 5 · last mile · choice artwork revision 7

## Pipeline

1. `lastmile.py` constructs the scene in Blender: four vehicles, barge with pipes/gift, swamp, icy river, dark brown chums, reindeer and a beige two-storey АБК. Seed: `5`; Eevee with Freestyle. Separate wide/tall cameras, not a crop of one render.
2. Render command: `blender --background --factory-startup --python design/scene-05/blender-v1/lastmile.py -- OUTDIR variants`. The script writes the `.blend`, recipient variants and projected-box manifest. These are layout bounds, not an occlusion measurement.
3. `cx/gpt-image-2`, high quality, styles the empty-recipient renders with scenario references (`docs/scenario-assets`, images 12–16). Prompts are in `prompts/`. Requested sizes: 2560×1056 and 1024×1792; working plates normalized to 1942×809 and 948×1659. A second pass gives the river natural edges and visible early ice.
4. Local correction: the generated wide truck had six near-side wheels. A successful reference-guided truck crop supplies the four-wheel silhouette instead. SAM (`facebook/sam-vit-huge`) extracts it and the recipient sprites. Хабт uses the new generated cartoon; Майма and Арсений retain their identities from revision-2 outcome illustrations. Failed crop requests returned HTTP 502 with unknown completion; they were not resubmitted blindly.
5. `compose.py WORKDIR` removes the incorrect truck footprint and places the corrected truck plus one enlarged recipient per variant. Required inputs: `fixed-{wide,tall}.png` and `sprite-{truck,alva,khor,arseniy}.png`. Final recipient heights: 92 wide / 116 tall source pixels. The selected person stands beside their destination, not on the departure quay.
6. RealESRGAN_x4plus tiled inference (256px tiles / 16px context) followed by Lanczos downsampling to 2×. Real WebP, quality 90, method 6: wide 3884×1618, tall 1896×3318.

## Integration and verification

- Six shipped images: `public/scene-art/lastmile-family-v1/revision-7/choice-{wide,tall}-{alva,khor,arseniy}.webp`. Checksums and release URL: root `media-artifacts.json`.
- Coordinates: `src/scenes/lastmile/expandedArtwork.ts`; SAM-derived interactive contours: `segmentedContours.json` in the same folder. The wide helicopter's thin upper rotor blade was restored manually after SAM missed it.
- Wide composition is used at stage aspect ratios ≥1.35; tall otherwise. Tall top crop is bounded so the destination is retained. Outcome illustrations remain unchanged.
- `bun run test --maxWorkers=2`; `bunx tsc --noEmit`.
- `bunx playwright test tests/lastmile-composition.spec.ts tests/visual-teo-framing.spec.ts --workers=2` checks source-pixel vehicle/destination extents and actual selections.
- Reviewed screenshots: 320×568, 390×844, 844×390, 1180×820, 1366×768, 1440×900, 1920×1080, 2560×1080. The 844/1920 crops originally cut off lower vehicles; changing the composition switch from 1.78 to 1.35 fixes both.

This is an illustrated map, not a photorealistic or distance-accurate site plan. The people are deliberately oversized for recognition on small screens. No deploy or branch push is part of this revision.
