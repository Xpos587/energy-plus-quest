# Compact semantic correction provenance

Built-in image_gen editing, 20 October 2026. No CLI/API fallback. Canonical code,
copy, scores and four decisions were preserved. Original sources were not overwritten.

## Source and edit boundary

Choice master: `public/compact-art/compact-environment-v26-portrait-v2.png`, crop
(80,410,510,330). The generated master is `place1-master-patch.png`; resized only
to the authored crop plane, then composited at the original coordinates.
Final choice portrait: `public/compact-art/compact-environment-v53-portrait.png`.
Wide v54 is the same portrait plane cropped at (0,308,1368,684).

Master prompt: preserve outer silver frame, floor, warehouse perspective and all
six kettlebells and dishes. Repack weights in two wider lower-left tiers and
preserve dishes lower-right. Leave a genuinely empty shared upper bay, without
cargo or straps crossing it. Retain a red strap above the dishes only. No text,
numbers, people, logos or new cargo. Generated native file:
`exec-f94f6d6a-95be-4891-a96b-250e60af3eb5.png` in the session generated_images directory.

## Place1 variants

- `place1-camera-patch.png`: same cargo geometry and all six weights; an unsecured
  boxed DSLR with orange strap has fallen onto dishes, breaking plates/cup. Keep
  upper bay empty; no text/people/arrows. Native `exec-379fbbf1-fbc8-46b4-9156-466ecb173230.png`.
- `place1-socks-patch.png`: two loose navy/cream/orange knitted socks, one atop
  weights, one draped at dishes edge. No restraint or box, dishes intact, same
  cargo and empty upper bay. Native `exec-dc695953-2db1-461e-80cf-db12f38068ca.png`.
- `place1-boat-patch.png`: same boat identity as v49 (navy inflatable, orange
  oars/trim, white seats, grey motor), entirely within upper bay, all six weights
  and dishes preserved. Native `exec-d2c8219c-d897-4249-b4b5-e87b4548d3d9.png`.
  Composite into v49 retains its broken rear axle outside the cargo patch.

Each place1 patch is composited at (80,410), size510×330, into its original result.
The empty master patch is also applied to camera/socks results3/4 and supported
upright boat, preserving gifts and all other pixels. Final sibling paths are in
`src/scenes/compact/resultArtwork.ts`.

Place2 native prompts, candidates, compositor and explicit small motor-fragment
cleanup are recorded once in [place2/PROVENANCE.md](place2/PROVENANCE.md).

## Three preceding fixes

- v51 wide: authored portrait crop (0,308,1368,684), superseded by v54 after Place1.
- Upright boat support: local built-in generated `boat-support-patch.png`, only
  its bottom160×72 pixels inserted at (900,663) into boat-zone4-v29. 11492 changed
  pixels inside support, zero outside. v52 is preserved; v53 adds common cargo.
- Yellow cabin: color matrix instead of hue-only ochre; existing protected glass
  mask unchanged. This is code-driven paint, not new cabin artwork.

## Verification

Canonical live boat1 text block1A23B1CD says rear-axle overload. The larger bay
therefore does not contradict its outcome. Six weights and broken axle inspected.
38 isolated production runtime cases and all contact sheets inspected, no sampled
document overflow. Eight root-runtime pixel checks pass; 18 targeted unit tests
pass. PDF `docs/reviews/compact-full-audit-2026-10-20/compact-semantic-review.pdf`
was rendered and all four pages inspected. Source freeze and residual boundaries
are canonical in that directory's AUDIT.md and active-upscale-sources.json.
