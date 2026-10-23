# Shared two-pass Flowers contract

Canonical IDs/sources: `docs/reviews/flowers-all-2026-10-20/manifest.json`.
Owner views are in `packages/`; only General updates the canonical manifest.
Every owner writes only its asset outputRoots and its own review directory.
Generation is explicit built-in image_gen, one claim/call at a time per lane; never
replace native calls with resize, codec quality, API fallback, or repeated paid jobs.

Set `FLOWERS_PY` only if convenient; exact invocations:

```sh
uv run --no-project --with pillow --with numpy --with opencv-python python scripts/flowers/pipeline.py prepare F0086 --freeze-receipt docs/reviews/ending-2026-10-20/active-upscale-sources.json
uv run --no-project --with pillow --with numpy --with opencv-python python scripts/flowers/pipeline.py record F0086 p1-00 --candidate OWNER/NATIVE.png --prompt OWNER/prompt.txt --tool-receipt OWNER/receipt.json
uv run --no-project --with pillow --with numpy --with opencv-python python scripts/flowers/pipeline.py protection F0086 --file OWNER/source-space-mask.png --receipt OWNER/protection-receipt.json
uv run --no-project --with pillow --with numpy --with opencv-python python scripts/flowers/pipeline.py assemble F0086 --pass 1
uv run --no-project --with pillow --with numpy --with opencv-python python scripts/flowers/pipeline.py rois F0086 --file OWNER/rois.json
uv run --no-project --with pillow --with numpy --with opencv-python python scripts/flowers/pipeline.py assemble F0086 --pass 2
```

`prepare` freezes the source once, prepares exact 3×3 cores with 20% padding,
reference crop PNGs, prompts and durable `job.json`. Repeating it resumes existing
work, does not reset accepted tiles or refreeze changed source. A different source
revision requires a new job/ID, never overwrite frozen inputs.

Read `source.png` and the crop before image_gen. Reference full source S + tile.
A native candidate saved by an owner may already exist: register it; do not
regenerate it just because it uses an owner-specific filename. `record` retains
each candidate, native dimensions and registration acceptance/rejection. Existing
accepted tiles reject duplicate registration. Rejected attempts remain explicit.
Registration reuses the previous Flowers SIFT/global similarity: >=12 inliers,
fraction>=.45, p95<=1.8 original-source pixels, rotation<=0.6deg. Native output
size is recorded; 8192 is assembled export longest edge, not native whole-scene AI.
The shared registration module additionally rejects nonfinite/degenerate transforms,
scale outside 0.8–1.25 of the ratio implied by image dimensions, and inliers whose
convex hull covers less than 0.5% or spans less than 10% on either image axis.
Assembly revalidates spatial support for old receipts without these guards.
`audit_registration.py --full --output docs/reviews/.../audit.json` reads existing
native files and reports failures without generating images or changing job history.

Protection is mandatory before assembly: grayscale PNG, original source dimensions;
255 retains original pixels, 0 permits reconstructed pixels. The owner must inspect
labels, faces, markers, masks, transparency and geometry and approve its mask. An
explicit empty mask is allowed only when owner-approved; never copy warehouse
boxes/HSV heuristics into unrelated scenes.

Pass1 assembly requires all nine tiles accepted. It applies global similarity,
bounded color offsets, two-band feathering and source-pixel protection. Incomplete
or rejected tiles cannot silently count as processed. Master then needs visual
seam/100%-detail/identity review. Do not call pass1 a completed two-pass asset.

Pass2 ROIs are owner-selected salient details in **original-source pixel units**:

```json
{"rois":[{"id":"p2-face","sourceBox":[100,100,300,350],"purpose":"face and garment seams"}]}
```

These coordinates are scaled into the accepted P1 master; registration errors
are normalized back into original-source pixels. Existing ROI jobs are not reset.
All requested P2 ROIs must be accepted before pass2 assembly. Generation references
original S and the supplied accepted P1 crop, preserving camera and scenario logic.

Final state is `master_ready_for_visual_review`, never automatically integrated.
Owner sends master + receipts + source/mask/focal/seam/100% review to General.
General alone updates shared media routing, rebuilds isolated stage and verifies
actual desktop/mobile currentSrc, decode, native/display dimensions, DPR, crop,
loading and active scenario paths. No deploy or artistic acceptance is implied.

## Explicit retained regions and alpha

After a real rejected attempt, the owner may explicitly retain that region with
`retain ID TILE --reason 'precise rejection/retention reason' --receipt OWNER/receipt.json`.
There are at most three native candidates per tile (initial + two targeted retries).
Pending/unattempted tiles cannot be retained. Assemblies restore retained P1 **cores**
from source pixels (even against overlapping neighbours), or retained P2 ROIs from
accepted P1. Receipts distinguish accepted AI tiles from retained source regions;
P1 retentions are inherited in the final receipt. Such an asset is partial detail
reconstruction, never described as full native reconstruction or all tiles processed.
RGB detail and original alpha/silhouette are handled independently: `prepare`
retains RGBA and `source-alpha.png`, final masters preserve the source alpha channel.

8192 assembly uses a single global non-blocking flock slot at
`.tmp-work/flowers-global-assembly.lock`; a busy slot fails before work starts.
Use one coordinated owner at a time. Blending processes 128-row stripes with a
Gaussian halo, retaining only an immutable uint8 prior tile instead of several
full-size float32 tiles. Record `/usr/bin/time -v` for the first real8192 assembly
and coordinate against measured available RAM; do not kill other owners' jobs.
Tile/ROI feathering applies only at internal boundaries. A box clipped at the
global canvas edge keeps full candidate weight there; validity and source/alpha
protection remain authoritative. New assembly receipts record this boundary policy.

## General-only accepted master activation

`uv run --no-project --with pillow python scripts/flowers/promote.py ID --review docs/reviews/.../runtime-review.json`
requires two assembled passes, original aspect/alpha, longest-edge8192, actual
accepted native tiles and explicit `decision: accepted_for_runtime, passes: 2`.
Partial masters additionally require `acceptsRetainedRegions: true` in that review.
It copies a versioned lossless master into public/flowers-2pass-2026-10-20 and
registers a reversible original→master alias in src/media/flowers-masters.json.
Original files and authored SVG coordinate planes stay unchanged. HOLD prevents
promotion. Registration alone is not proof of runtime integration.

The image plugin reads accepted aliases, preserves alpha/aspect and records
master dimensions independently of derivative dimensions. Existing source paths
stay the keys, including SVG image/crop users. Runtime derivatives come from the
accepted AI master: longest-side5120 for scenes,2560 for endings,1600 for setup;
lossless8192 remains the separate master. Media quality settings are not a proxy
for native reconstruction. Imported design assets and opening art are covered.

`uv run --no-project python scripts/flowers/build.py --build-dir .tmp-work/flowers-build-N --stage-dir .tmp-work/flowers-stage-N --receipt docs/reviews/flowers-all-2026-10-20/build-N.json`
uses the same exclusive resource slot as assembly, one Sharp worker/thread and
records real child peakRSS/walltime. It only builds/stages, never publishes.
General then previews the actual stage, verifies desktop/mobile resources and
coordinates, and publishes assets first/index last while retaining old assets.

`uv run --no-project python scripts/flowers/progress.py --sync` refreshes the
canonical manifest progress from per-asset atomic job receipts. Counts include
registered native attempts only; pending, rejected, retained, P1, P2 and runtime
integration remain separate. Owner-specific native receipts remain linked.

A visual seam rejection may add targeted P2 repair ROIs without regenerating
accepted work: `rois ID --append --file OWNER/new-unique-repair-rois.json`.
All incoming IDs must be new; accepted ROIs/attempts stay unchanged. The job
returns to p2_prepared until new candidates are registered and P2 is reassembled.
Archive the rejected prior assembly as owner evidence before reassembly.
