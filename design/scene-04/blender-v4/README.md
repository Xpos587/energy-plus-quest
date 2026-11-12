# Scene 4: approved quay geometry and painted finish

`quay.py` is the geometry/camera source; `quay.blend` is the current local native
master. The Blender structural pass preserves object geometry, camera framing,
all 16 slew frames and the three choices. It improves sampling, contour
resolution and contact/soft shadows. It is the geometry input, not the final
painted appearance.

The finishing reference is [the previous painted scene](reference/previous-painted-scene4.png).
Match its restrained warm daylight, pinkish-beige paving and original expressive
characters; do not copy its old barge position. Existing v4 character poses and
operator atlases remain identity references. New painted candidates must pass
registration, silhouette/anchor, runtime and animation checks before promotion.
Keep highlight rings live in the interface, not baked into raster artwork.

The render defaults and provenance are in `quay.py` and its generated
`manifest.json`. `export.mjs` reads the recorded render scale, validates PNG
canvas dimensions before writing media, and retains two format-pixels of alpha
padding. Old 1.5× manifests remain readable. A partial export keeps the other
formats, permitting bounded intermediate storage.

The accepted finishing inputs, exact media inventory, reproduction commands and
verification limits are documented in [painted/README.md](painted/README.md).

## Rebuild locally

```sh
(
set -e
out=.tmp-work/scene4-render
mkdir -p "$out"
for format in wide desk mid tall; do
  blender --background --factory-startup --threads 8 --python-exit-code 1 \
    --python design/scene-04/blender-v4/quay.py -- "$out" layers "$format"
  bun design/scene-04/blender-v4/export.mjs "$out" '' "$format"
  rm -r "$out/$format" "$out/quay.blend"
done
)
```

After all formats succeed, use a source Vite server without media hydration:

```sh
bun scripts/capture-barge-outcomes.mjs http://127.0.0.1:4175
bunx vitest run src/scenes/crane --maxWorkers=2
bun run typecheck
```

The nine runtime result stills come from the live animation at the established
wide, mid-rail and tall-portrait crops, now at 2× with WebP quality 92. The
capture's existing hull/cover-safety assertions remain authoritative. Do not
replace these with the separate Blender `outcomes` mode's different framing.

To rebuild a native master, pass `model` instead of `layers`, omit the format
argument, and choose an output directory. This builds all four cameras without
rendering, sets the crane's rest pose, and hides mutually exclusive result
actors. Collection **Barge - approved geometry** contains the original 12 barge
objects, tagged `quay_group='barge'`; append this collection for scene 5 rather
than editing the shared master. No external textures are required.

## Review and release boundary

The equal-display 128-sample/2× structural proof passed its geometry checks;
that does not approve a painted candidate. Blender/final native artwork,
100% crops, desktop/phone frames and validation logs live under `.tmp-work/scene4-final-render/` and follow the
repository's temporary-evidence retention policy. This is not a published
media release. Binary masters and runtime images remain local/ignored;
`media-artifacts.json`, upload, push and deployment require separate approval.
