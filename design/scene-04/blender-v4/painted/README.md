# Scene 4 painted finish — current inputs and verification

The approved geometry is the **barge below the loading crane**. Cameras, world
geometry, anchors and slew poses remain those in [../quay.py](../quay.py) and the
current local `../quay.blend`. Exactly three choices remain: remote, rush, Petr.

## Current media and runtime contract

Runtime media is `public/scene-art/barge-v5/`: **121 WebPs**. The final face and
machinery pass replaces 36 assets (nine per format), then captures nine outcomes.
[receipts/alpha-checks.json](receipts/alpha-checks.json) checks these disjoint groups:

| Files | Contract |
| ---: | --- |
| 36 | Original Blender dimensions and pixel-exact mechanical alpha |
| 44 | Byte-identical original v4 cast |
| 4 | Deterministically reconstructed legacy `ivan.webp`, unchanged and unused |
| 16 | Office composites: original alpha resampled 2× with Pillow LANCZOS |
| 8 | Compact 4×4 operator atlases; 4× logical density, synchronized placement |
| 4 | `far-empty.webp`: exact alpha/dimensions of the base far crane |
| 9 | SHA-bound, opaque, live 2× result captures with hull-safe bounds |

All 121 files also match the accepted hashes in
[receipts/media-files.json](receipts/media-files.json). Binary files stay outside
Git. That 198-file receipt includes necessary sources as well as runtime media;
**this is not a published media release. Do not hydrate over unpublished art.**

- The near crane always draws the painted `top.webp`, plus at most one compact
  operator overlay using the same atlas frame. No whole-crane identity swaps.
- Ivan has the backward cap used in the office; Petr has a forward cap and beard.
  Operators are fully hidden when the strut would split their heads. The retained
  head-alpha threshold is 90%, connected head area 88%. The checker binds the
  accepted atlases to hashes and verifies frame presence against the generator's
  visibility receipt; it does not independently infer faces from pixels.
- Petr moves to the near crane in his branch. The empty far variant uses the
  **same base far box**, not the old larger cab overlay.
- `office.webp` already contains Ivan. The legacy Ivan overlay is not drawn over
  it. Its four unused source files still have their original cap-alpha holes;
  those files were not repaired. The root fix removes the duplicate runtime head.
- Sixteen office heads use focused, smiling/waving and cheering expressions.
  Original body pixels outside the local head mask and resampled alpha are exact.
  The visible neutral-head collar seam was explicitly accepted by the user.
- Near/far machinery housings and counterweights are navy. Near RGB edits are
  bounded by the projected housing/counterweight masks across all 64 frames;
  far RGB edits are bounded by explicit casing/glazing masks. Fine painted edge
  highlights are not a claim of pixel-perfect uniform color.

## Retained sources and density limits

- `manifests/` and the original five painting/alignment briefs preserve the
  reviewed layouts and 48 accepted painting masters in `model-images/`.
- Three additional used masters (`operators-a1.png`, `far-empty-a1.png`,
  `expressions-a1.png`) and their briefs support this pass. No rejected identity
  master or raw request/response transport is part of the retained source set.
- `face-inputs/` retains 24 necessary pre-edit WebPs (six per format), projected
  geometry and two reviewed placement layouts. These are generator inputs, not
  an archive of alternate finished artwork.
- `receipts/geometry-baseline.json` records the **49 structural core exports**;
  original cast evidence comes separately from `public/scene-art/barge-v4/`.
  The current checker does not depend on an expiring scratch Blender directory.
- Reusable scripts live in [../../../../scripts/scene4-painted/](../../../../scripts/scene4-painted/).

Logical canvases are 1942×809, 1536×1024, 1402×1122 and 1024×1536. Their plates
are exactly 2× those dimensions. Original painting RGB was approximately 1.57 MP
per model tile/sheet and was resampled into these locked canvases: **not native
4K model detail**. Office bodies are resampled from 1.5× to 3× logical pixels;
only the new head patches add source detail. Operator overlays are 4× logical
pixels, not new 4× texture detail on the underlying crane.

Plate registration uses sparse SIFT matches, bounded translations and visual
review. Desk has six automatic tiles; mid has four automatic and two reviewed
identity tiles; tall has two identity-review exceptions. Wide left-top has a
reviewed translation of about 4.456 px. The four plate receipts retain the exact
measurements. This is not full per-pixel proof of background geometry.

## Reproduce the face/machinery pass without paid calls

The following commands write candidates and proofs, **not runtime files**.
The recorded rebuild reproduced all 36 accepted edited WebPs byte-for-byte:
[receipts/rebuild-checks.json](receipts/rebuild-checks.json).

```sh
R=/home/michael/Github/energy-plus-quest
W="$R/.tmp-work/scene4-faces-rebuild"
for script in generate-operators generate-office-heads generate-far-cab check-machinery; do
  uv run --with pillow --with numpy --with opencv-python-headless \
    python "$R/scripts/scene4-painted/$script.py" "$W"
done
bun "$R/scripts/scene4-painted/check-painted-assets.mjs" --self-test
bun "$R/scripts/scene4-painted/check-painted-assets.mjs"
```

Review candidates before promotion. Their names are
`$W/candidates/<format>-<asset>.webp`; the nine assets per format are `top`,
`top-ivan`, `top-petr`, `far`, `far-empty`, `office`, `ivan-joy`, `ivan-wave`,
`ivan-cheer`. Copy only approved outputs into their corresponding runtime format
directory, then recapture outcomes. Do not regenerate the accepted receipt's
hashes merely to make a failed check green.

For a deliberate rebuild of the earlier painting layer, first obtain the 49
native structural core exports using [../README.md](../README.md), placing them
in `$R/.tmp-work/scene4-final-render/blender-assets/`. Structural export replaces
runtime media; do not run it merely to check the accepted finish. Retain original
v4 cast separately. From the repository root, the existing `prepare-plates.mjs`,
`prepare-sheets.mjs`, `stitch-plate.py`, `extract-sheets.py` and
`promote-painted.mjs` pipeline reuses the reviewed manifests and 48 masters.
Copy `painted/manifests/*.json` into its scratch `gpt/` directory first. This older
promotion creates the pre-face finish; it does **not** replace the face pass.

## Capture and verify the current runtime

Use an existing source Vite server **without media hydration**. These examples
use a local loopback server, not a phone-reachable preview URL.

```sh
R=/home/michael/Github/energy-plus-quest
W="$R/.tmp-work/scene4-faces/reviews"
BARGE_CAPTURE_RECEIPT="$W/outcome-capture.json" \
  bun "$R/scripts/capture-barge-outcomes.mjs" http://127.0.0.1:4175
bun "$R/scripts/scene4-painted/capture-face-results.mjs" http://127.0.0.1:4175 "$W"
bun "$R/scripts/record-barge-outcomes.mjs" http://127.0.0.1:4175 "$W/motion"
```

The outcome capture writes all nine runtime stills. Rail uses the existing live
**1.11:1 crop and 6.75% hull inset**; dimensions vary slightly with sampled
animation bounds and rounding. Wide/portrait capture their full cameras.
Capture validation requires a visible, decoded plane, native 2× density, opaque
alpha and safe hull bounds. It does not resize images to hide a mismatch.
A previously captured error-screen rail still was superseded by valid captures.
All nine final stills now match the accepted SHA-bound capture receipt.

Real-time result verification waits for both decoded artwork and visible copy;
clock-fast-forward captures that missed copy are not the final evidence. It
checks three choices, no duplicate Ivan layer, correct desktop rail/phone
portrait source, no broken images, no loading state and no horizontal overflow.
Current evidence: [receipts/runtime-checks.json](receipts/runtime-checks.json)
and [receipts/final-verification.json](receipts/final-verification.json).

Latest temporary proof root is `$R/.tmp-work/scene4-faces/reviews/`:
`{remote,rush,petr}-{1440,390}-RESULT.png`, `choice-{1440,390}.png`, nine
`native-outcome-*.png` equal-density comparisons, and six recordings plus contact
sheets in `motion/`. Black rail padding in comparison sheets is outside the
capture, not missing media. Independent visual review inspected all nine native
sheets and six motion sheets without finding a concrete defect. **Contact-sheet
sampling is not a frame-by-frame review of the recordings.**

## Initial loading regression: retained evidence, bounded claims

Before the fix, plate readiness alone allowed transparent layers to pop into the
first scene frames, in normal and reduced-motion cold-load recordings. The old
“capture-only” attribution is retracted; two warm-up frames were not a fix.

`CraneArt.tsx` decodes the complete current image set before revealing the plane,
keeps loading/error/retry treatment, invalidates an in-flight decode when cast
sources change and never blanks an already revealed scene for ordinary frames.
Retry cache-busts every layer. Tests cover delayed last image, pending source
change, failure and retry; failures were observed before the corresponding fixes.
The face pass preserves this gate and adds the single-operator/office regression.

[receipts/loading-checks.json](receipts/loading-checks.json) explicitly separates
the earlier cold-load/packaging evidence from current validation. The earlier
scoped Vite test-mode bundle staged 121 matching barge assets; this was not a full
release build/deployment and its hashes do not describe the later face pass.
Unique before/after cold-load evidence remains in
`$R/.tmp-work/scene4-final-render/{cold-load,cold-load-after}/`.
A brief phone Petr result-transition white frame was observed in an earlier
recording. The initial-scene gate does not claim to fix that separate transition,
and sampled final sheets alone cannot prove it absent from every frame.
