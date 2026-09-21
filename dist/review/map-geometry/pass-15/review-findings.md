# Pass 15 checked review

- Only twelve existing blue roof planes and selected leaf colors changed. Native 3504x2336 geometry, grain, ink and lighting remain; no generation, warp or new dependencies.
- Inspected the complete map, both girls, native paired roof/fixture crops, foliage edges, every edge-cropped roof, warehouse side roof and loading canopy. Greige roofs no longer compete with blue trucks. No blue roof-edge strips or fixture-box halos remain.
- Foliage keeps distinct green crowns and muted yellow/ochre variation, not an orange wash. 51.9% of tested leaf pixels remain green (HSV hue >=65 degrees); foliage HSV value is unchanged.
- Roof-plane cast-shadow chroma follows the new material, as explicitly approved; luminance differs by at most 0.454/255 from source due to RGB rounding. All off-roof shadows are unchanged.
- Artifact check verifies 345 prior/source hashes, zero edited pixels outside the two masks, 21,505 unchanged fixture pixels, protected trucks/crew/facades, original character RGB, lossless browser/master identity and independent two-girl PNG compositing.
- Chromium passes 1440x1000, 390x844, 320x568, 820x1180 and 568x320: before/after, girl toggle, 300% zoom, no page overflow/errors, visible foreground/natural girl pixels, downloaded PNG/JPEG byte equality and local asset HTTP byte equality. Desktop and mobile screenshots personally inspected.
- JPEG sharing derivatives are lossy; pixel invariance applies to map.png and map.webp, not JPEG files. Natural-scale girl intentionally needs zoom on small screens, just as in pass 14.
- No blockers found. User approval is not claimed. Game files, previous passes and the immutable professional girl are untouched; nothing staged.

Reproduce with the existing environment:

```sh
P=/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-15
/home/michael/.local/share/comfyui/venv/bin/python "$P/finish.py"
/home/michael/.local/share/comfyui/venv/bin/python "$P/check_artifacts.py"
node "$P/browser-check.cjs"
```

Browser check expects the existing local server on port 4173. Native paired boundary evidence and browser screenshots are in the production pass-15 directory.
