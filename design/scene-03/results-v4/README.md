# Native warehouse result illustrations

## Current scope

All six warehouse **results** now use clean native illustrations. The user specifically approved `native-keeper.png` (SHA-256 `90433cc609d5dcd689418f3641c330c3254ae71cc2b6c0a11d8471af6c355210`) and requested the same quality for the other results, excluding the main choice illustration. That exact keeper PNG is retained, with identical decoded pixels in the shipped lossless WebP.

The choice illustrations `inventory-master-v16.webp` and `inventory-master-v16-tall.webp` are unchanged. This revision changes no dialogue, scores, routing or marker coordinates. After reviewing the new art, the user additionally requested a framing correction: the alphabet-camera worker was cut off on phones. Responsive result framing is therefore in scope; the illustration pixels remain unchanged. The existing choice-marker anchors remain defined in `src/scenes/inventory/segmentedContours{,.mobile}.json`.

## Rebuild

```sh
uv run scripts/finish-warehouse-results-v4.py
```

This Pillow-only exporter reads four native PNG masters in this directory and writes six lossless WebPs into `public/scene-art/warehouse-results-v4/`. It checks the reviewed source hashes, exact dimensions and decoded output pixel equality. There is no full-image resizing, registration, optical flow, perspective warp, person patching or gift compositing.

| Native master | Actual dimensions | Results |
|---|---:|---|
| `native-alphabet-camera.png` | 1999×786 | alphabet-camera, alphabet-boat, alphabet-socks |
| `native-entrance.png` | 2004×785 | entrance |
| `native-keeper.png` | 1672×941 | keeper |
| `native-wms.png` | 1671×941 | wms |

The boat and socks variants differ from the clean camera master only inside the plaque text rectangle `(1054,232)–(1115,262)`, right/bottom exclusive. Their labels are respectively `Л-М` and `Н-У`; camera retains the generated `Ф-Э`. The exporter uses the existing `public/fonts/normalidad-proxy-bold.woff2`, interpolates the blank plaque background from its adjacent rows, and antialiases only the new glyphs. An assertion proves **zero changed pixels outside that 61×30 rectangle**. Cargo, character and background are otherwise identical across the alphabet trio.

[receipt.json](receipt.json) records source/output hashes, dimensions, lossless pixel checks and variant bounds. These checks preserve approved pixels; they are not automated proof of artistic quality or perspective correctness.

## Generation provenance

Four edits used `cx/gpt-image-2.5`, high quality, PNG output. The previous result served as a composition reference. Entrance, keeper and WMS additionally used the clean alphabet-camera image as a style reference. The four `*.prompt.txt` files preserve the exact instructions; [generation.json](generation.json) records model, submission time, reference hashes, requested parameters and actual output dimensions. Raw API transport dumps are not canonical sources.

The provider returned the original target dimensions, **not** the requested 2000×784 / 1664×944 sizes. Its four outputs were retained byte-for-byte as native masters. Generation preserves the visual identity, poses and blue/orange workwear, not pixel-identical people from the previous illustrations.

## Correction to the earlier R25 assessment

The earlier claim that all six results had straight geometry was incorrect and is withdrawn. A projective homography preserves mathematical lines; it does not prove that lines drawn in its input are straight. Visual review found defects in source geometry as well as jagged/ghosted bow and ribbon edges from deterministic gift compositing. Neither the original restyle nor the later transform is established as the sole cause.

The former homography/person-overlay/gift-overlay exporter has been replaced, rather than applied to the new masters. Its four superseded `hf-*.png` masters and `registration.json` were moved to system Trash after checking for current references and receiving coordinator approval. Old protected-person/footprint checks did not establish the visual quality the user wanted and do not describe these regenerated results.

## Responsive result framing

The native illustrations are not cropped or resampled on disk. `src/scenes/outcomeFraming.ts` now uses one horizontal focus for the three identical alphabet compositions and revised entrance/keeper focus. The obsolete entrance-only phone override was removed from `src/scenes/SceneOutcomeArt.module.css`.

The inventory-only portrait rule in `src/components/SceneInteraction.module.css` bounds the art row by viewport width and reserves at least 320px for paged copy/actions. WMS keeps its existing layout. The bounded result sheet uses `max-height: none`, letting the existing paginator measure its actual row instead of an older estimated maximum. This matters at 320×568: the estimate was 395.04px for a 320px sheet and placed buttons below the viewport. No shared paginator or result-copy code was changed by this lane.

`tests/inventory-result-framing.spec.ts` checks all six branches at six viewport sizes: native-image subject bounds, visible navigation, complete paging and no document overflow. The original 390×844 camera case failed with its visible left edge at native x=709.22, excluding the worker whose required bound starts at x=605 (`framing-red.log`). The keeper assertion covers the worker and gift, not the whole cart at every viewport. `tests/inventory-fixture.ts` now waits for real briefing/choice controls instead of a fixed 1.2-second startup window.

## Local review and verification

Latest evidence: `.tmp-work/warehouse-warp-fix/` (temporary review material, not rebuild inputs).

- `before/{result}-full.webp`: previous six results, with cart/shelf/gift 100% crops.
- `after/{result}-full.webp`: six current decoded exports. `after/{result}-{cart,shelves,gift}-100.png` and `after/{result}-crops-100.png` preserve 1:1 detail for inspection, without enlarging the artwork.
- `runtime/`: pre-framing browser comparison. `framed-runtime/`: final 14 captures at 390×844 and 1440×900 (two choices plus all six results at both sizes), with `browser.json` confirming image URLs, choice-anchor checks and zero page/HTTP errors. Additional alphabet-camera captures cover 320×568, 430×932, 820×1180 and 844×390. All 16 result screenshots were visually inspected. No request interception or image/DOM replacement.
- `baseline.sha256`: original hashes; both main choice illustrations and `media-artifacts.json` were checked unchanged after export.
- Targeted Vitest: all 111 tests in 11 files have passing results (inventory, artwork, outcome-art and compact-scene checks). The final combined run passed 110; one compact-scene case hit its 5-second timeout while browser work was running. The compact file then passed all 27 tests when run alone (`unit-final.log`, `compact-final.log`). Typecheck passed (`typecheck-final.log`). This is targeted coverage, not a claim that the full repository suite passed.
- Playwright: all 27 cases have passing results. The final serial run passed 26; Chromium crashed in the 1440px framing case without a failed framing assertion (`playwright-final.log`). That case passed in isolation (`playwright-1440-final.log`). Coverage includes 12 existing warehouse perspective/keeper-clearance/WMS-paging cases, 9 inventory subject-framing cases and 6 new viewport tests exercising all six results (36 result routes with paging). Sizes span 320×568 through 1440×900, including portrait tablet and landscape phone. The earlier six-case framing-only run also passed in full (`framing-green.log`). Unrelated last-mile cases were excluded.

The local validation server uses its own Vite dependency cache and disables file watching for the check. Earlier runs were interrupted by reloads on Playwright trace HTML under `.tmp-work` as well as concurrent source edits. These interruptions are distinct from the reproduced 320px pagination defect, which required the scoped CSS fix above.

Visual approval of keeper came directly from the user. Other compositions were inspected at full frame and 100% detail; machine pixel assertions are not a substitute for that review. Runtime captures and framing tests verify the current local build, not a production deployment.

## Publication boundary

The current v4 assets are not yet listed in `media-artifacts.json`. No media upload, manifest update, push or deployment is performed by this lane. Publishing remains a separate coordinator-authorized operation under [repository policy](../../../docs/REPOSITORY-HYGIENE.md).
