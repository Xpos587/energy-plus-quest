# Scene 4 painted finish — current inputs and verification

The approved geometry is the **barge below the loading crane**, not the older
barge position in the style reference. Cameras, world geometry, anchors and
slew poses remain those in [../quay.py](../quay.py) and the current local
`../quay.blend`. The coordinator visually accepted the painted choice views,
three desktop results and rush motion on 12 November 2026.

## What is retained

- `prompts/`: the five actual painting/alignment briefs.
- `manifests/`: four reviewed tile layouts, four prop layouts, sixteen four-pose
  top layouts, and result pointers to the **48 accepted model images** in
  `model-images/`. No transport dumps, credentials or rejected generations.
- `receipts/`: structural, export, registration, exact-alpha, original-cast,
  live-crop and runtime checks. Some original receipt source paths describe the
  working directory at generation time; current model inputs are resolved by
  `manifests/*.result.json`.
- [../../../../scripts/scene4-painted/](../../../../scripts/scene4-painted/):
  the input preparation, extraction, stitching, promotion and review scripts.
- Runtime media: `public/scene-art/barge-v5/`, 121 WebPs: forty base assets,
  nine result stills, and seventy-two preserved v4 cast files.

Binary files stay outside Git. `receipts/media-files.json` identifies the exact
current media for a later approved release. **This finish is not yet a published
media release. Do not hydrate over unpublished artwork.**

`stage-static.mjs` retains the complete `barge-v5` dynamic family together with
this source switch. Its regression failed before the family change and passes
after it. A current Vite test-mode bundle was staged with all 121 real barge
images; every staged file matched the inventory SHA-256. That scoped packaging
check is not a full release build or deployment; the receipt is in
`receipts/loading-checks.json` under `currentHeadValidation`.

## Native output is not native model detail

The four logical canvases are 1942×809, 1536×1024, 1402×1122 and 1024×1536.
Their runtime plates are exactly 2×: 3884×1618, 3072×2048, 2804×2244 and
2048×3072. The model's tile/sheet RGB output is approximately 1.57 MP; it is
resampled into the locked native canvases. These are **not** claims of native
4K model texture detail. The accepted wide style proof itself is 1935×813.

Mechanical sprite alpha comes from the Blender baseline, unchanged pixel for
pixel. Four Ivan portraits are intentional identity exceptions: original v4
portraits resized to their current native boxes and encoded deterministically.
All other 72 cast files, including both operator atlases in all formats, remain
byte-identical to v4. Four sixteen-frame base atlases plus eight preserved
sixteen-frame operator atlases give 192 crane-top animation frames.

Plate registration uses sparse SIFT correspondences, bounded translations and
explicit visual review. Desk has six automatic tiles. Mid has four automatic
tiles and two explicitly reviewed identity tiles; tall has two identity-review
exceptions. Wide left-top has a reviewed translation of approximately 4.456 px.
The exact measurements and rationales are in the four plate check receipts.
**This is not full per-pixel proof of unchanged background geometry.**

## Reproduce the finish from retained inputs

Run commands from the repository root. First obtain the native structural
exports using [../README.md](../README.md), and place that unpainted 121-file set
in `.tmp-work/scene4-final-render/blender-assets/`. Structural export replaces
runtime files: do not run it merely to check the currently accepted painting.
The native alpha baseline can also be retained during a deliberate rebuild.

```sh
mkdir -p .tmp-work/scene4-final-render/gpt
cp design/scene-04/blender-v4/painted/manifests/*.json .tmp-work/scene4-final-render/gpt/
bun scripts/scene4-painted/prepare-plates.mjs wide desk mid tall
for format in wide desk mid tall; do
  bun scripts/scene4-painted/prepare-sheets.mjs "$format"
  uv run --with numpy --with opencv-python-headless python scripts/scene4-painted/stitch-plate.py "$format"
  uv run --with numpy --with opencv-python-headless python scripts/scene4-painted/extract-sheets.py sprites "$format"
  uv run --with numpy --with opencv-python-headless python scripts/scene4-painted/extract-sheets.py top "$format"
done
bun scripts/scene4-painted/promote-painted.mjs wide desk mid tall
```

These scripts reuse accepted image outputs; they do not submit paid image jobs.
Preparation now recreates inputs from the four retained reviewed manifests;
it does not invent new tile layouts or erase their review exceptions.

For live result stills, use a source Vite server **without media hydration**:

```sh
BARGE_CAPTURE_RECEIPT=.tmp-work/scene4-final-render/outcome-crops.json \
  bun scripts/capture-barge-outcomes.mjs http://127.0.0.1:4175
bun scripts/scene4-painted/check-painted-assets.mjs --self-test
bun scripts/scene4-painted/check-painted-assets.mjs
bun scripts/scene4-painted/capture.mjs final
bun scripts/scene4-painted/compare.mjs
bun scripts/scene4-painted/cold-load.mjs
```

The three rail outcomes use the existing **live 1.11:1 hull-safe crop**, not a
fixed mechanical matte. Their dimensions vary by a few pixels with sampled
animation/bobbing bounds and raster rounding. The original blanket comparison
against baseline dimensions failed on this distinction. The replacement check
requires a SHA-256-bound capture receipt, native 2× dimensions within raster
rounding, mid-camera bounds, the existing 6.75% hull inset and opaque alpha.
It does not resize a result to conceal a difference. Alpha/crop checks do not
prove image content: the final visual montage caught an error-screen rush-rail
still from the earlier concurrent gate-change run. All three rail stills were
regenerated after adding visible-plane/no-loading-status assertions to capture.
The remaining 114 assets pass baseline alpha/dimensions; the four Ivan files pass exact reconstruction.

## Initial loading regression

Before the fix, plate readiness alone allowed independently decoded transparent
layers to pop into the first scene frames. Both normal and reduced-motion
cold-load videos reproduced it. The earlier “capture-only” attribution is
**retracted**. Two animation frames or a warm-up screenshot were not a fix.

`CraneArt.tsx` now decodes the complete current image set before revealing the
plane, retaining the existing loading/error/retry treatment. It invalidates an
in-flight decode when a rail action changes the initial cast source set, but
never blanks an already revealed scene for ordinary animation frames. Retry
cache-busts every layer. The regression covers the last delayed image, a source
change while pending, failure, and retry. The first version and the source-race
version both failed the corresponding new assertion before their fixes.
A fresh read-only reviewer accepted the final gate after that race was fixed.

`origin/main` at `2ad1702e0f133f2cffc63489cb244d1dd371bf72` had the same
plate-only gate (`CraneArt.tsx:111,182,214,220,254,342`). That is source evidence,
not a video reproduction of the older deployment.

Review artifacts are the latest temporary deliverables under
`.tmp-work/scene4-final-render/`: `blender-vs-final/` contains all four native
comparisons, all nine outcomes and true 100% pixel crops; `final/` contains eight
runtime views; `motion/` contains all six desktop/phone recordings;
`cold-load/` and `cold-load-after/` retain before/after real-time videos. Extracted
PNG sequences and raw API transports were removed, not the videos or receipts.
A brief white frame was observed at the phone Petr result transition in the
motion recording, followed by a correct result. The initial-scene gate does not
claim to remove that separate result-image transition gap.
