# Scene 5 · choice artwork revision 8

Revision 7 is preserved in `../blender-v1`; this version rebuilds geometry rather than recolouring it. No branch push or deployment is part of this revision.

## Source and visual contract

- `lastmile.py`: broad chamfered cargo barge with a hold, wheelhouse, mooring ropes and fenders; short quay separated from gravel staging; inland helipad with a land margin; rounded Mi-8, four near-side balloon tyres on the 8×8 rover, pipe carrier and low tracked robot.
- The compact cream АБК follows `docs/scenario-assets/image12.png`: annex, dark lettering, roof plant, aerial and exposed service pipes. Vehicle references: images 13–16 in that folder. The illustration style follows `design/scene-04/barge-v2/style-{a,b}.png`.
- One recipient at their destination, two brown chums and three reindeer. These are illustrated game-map proportions, not a survey or an engineering safety plan.

## Pipeline

1. `VARIANTS=arseniy blender --background --factory-startup --threads 8 --python design/scene-05/blender-v2/lastmile.py -- WORKDIR/structure-b variants` produces the saved scene, two separate cameras and projected layout bounds. Wide: 1942×809; tall: 948×1659.
2. `blender --background WORKDIR/structure-b/lastmile.blend --threads 8 --python design/scene-05/blender-v2/evidence.py -- WORKDIR/evidence` exports ID/depth passes. `python evidence-check.py WORKDIR/evidence WORKDIR/structure-b` checks actual visible ID pixels for nine groups in both cameras and exports Canny edges. This proves visible pixels and unclipped bounds, **not** a percentage of visible object surface.
3. `cx/gpt-image-2`, high quality, edits the structural images using the prompts in `prompts/`, the scenario references and scene-4 style. Wide output: 1942×809; tall output: 949×1658, normalized to 948×1659. Save these as `base-{wide,tall}.png`. The tall generation also used the successful wide image as a style reference.
4. Recipient changes edit the **whole destination scene crop**, not a cutout sprite: wide `(1100,0,620,600)`, tall `(340,230,608,600)`. First remove Арсений and add Майма; then replace Майма with Хабт. Each final crop uses only its edit target as input. A two-reference tall trial moved the camp and was rejected. Accepted inputs for `compose.py`: `destination-wide-{alva,khor}.png`, `destination-tall-c-{alva,khor}.png`.
5. `python compose.py WORKDIR` registers unchanged background features and feathers crop edges. It asserts that the transport/port below each crop is unchanged. No revision-7 character sprites are reused.
6. RealESRGAN_x4plus tiled inference (256px tiles, 16px context), then Lanczos reduction to 2×. `python export.py WORKDIR public/scene-art/lastmile-family-v1/revision-8` writes genuine WebP, quality 90, method 6: 3884×1618 wide / 1896×3318 tall.
7. SAM (`facebook/sam-vit-huge`) derives fresh vehicle contours from the accepted native images. Contours, source references and dimensions are in `src/scenes/lastmile/segmentedContours.json`; camera extents and markers in `expandedArtwork.ts` beside it. Outcome illustrations remain unchanged.

An interrupted initial tall request was reconciled against the gateway's request log: HTTP 502, `client_cancelled`, 114188 ms; no stored image was recoverable. Billing was not established. Only after reconciliation was a new request submitted. Raw provider receipts contain image payloads and stay private/outside Git.

## Checks and delivery

- Structural ID visibility: all nine groups pass in both cameras.
- Runnable composition assertions; all four accepted crop registrations retain over 1900 inlier matches.
- The camera fits full vehicle silhouettes, the whole barge, АБК aerial and camp—not merely the marker centres. Wide is chosen at stage aspect ratios ≥1.15; the top 64px are reserved for the instruction overlay. A half-pixel tolerance prevents floating-point roundoff from rejecting an exact-fit offset. The expanded framing test failed in six of eight viewports with the previous camera.
- `bun run test --maxWorkers=2`: 372 tests passed (70 files); `bunx tsc --noEmit`: passed.
- `bunx playwright test tests/lastmile-composition.spec.ts tests/visual-teo-framing.spec.ts --project=desktop-chromium --project=mobile-chromium --workers=2`: 26 passed. Bounds also remain below the instruction overlay. Below 360px, unfocused pin captions are hidden to avoid covering neighbouring vehicles; accessible names and 44px targets remain.
- Runtime review sizes: 320×568, 390×844, 844×390, 1180×820, 1366×768, 1440×900, 1920×1080, 2560×1080; all three recipients also checked on phone and desktop.
- Six delivered files: `public/scene-art/lastmile-family-v1/revision-8/choice-{wide,tall}-{alva,khor,arseniy}.webp`. Archive URLs, byte counts and SHA-256 checksums have one canonical home: root `media-artifacts.json`.
