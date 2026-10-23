# Current cab continuity evidence — 2026-10-20

Four actual crop pairs: `old-pair.png`, `near-pair.png`, `crew-pair.png`, `old4-pair.png`. No source assets or application code changed.

## Sources

- Scene 1: frame at 0 seconds decoded directly from `public/scene1-live/separated-routes/city-motion-desktop.mp4`. This is the current source selected by `src/components/IllustratedCityMap.tsx:12–19`, with cache version 23. Full decoded frame: `scene1-current-video-t0.png`. Do not substitute CarrierTruckIcon or historical close-up pictures for this moving map.
- Compact: existing current runtime screenshots `../4351-1440-red-choice.png`, `../4351-1440-blue-choice.png`, `../4351-1440-green-choice.png`, `../4351-1440-yellow-choice.png`. Their selected source is recorded in `../runtime-4351.json`: `desktop-detail-compact-environment-v51-wide-*.avif`. `CargoBay.tsx` selects `compact-art/compact-environment-v51-wide.png` through `imageAsset`/`detailImageAsset` and recolors its common cab.
- Individual unmodified crops retained as `CARRIER-scene1-cab.png` / `CARRIER-compact-cab.png`. Comparison panels enlarge the small map source pixels using nearest-neighbor; they do not invent detail.

## Crop bounds

Scene 1 bounds are expressed in the 1888×1312 poster coordinate plane, then scaled to the decoded video dimensions: old `(1090,1005,1173,1098)`; near `(570,970,645,1050)`; crew `(1365,197,1448,290)`; old4 `(1475,824,1548,919)`. Compact bounds `(1570,125,1995,795)` in the 1996-pixel-wide screenshot plane, scaled to source dimensions.

## Confirmed findings and limits

- Color families carry through: old red, near blue, crew green, old4 yellow. Compact is visibly brighter/more saturated: notably red becomes pink-red and green becomes deeper green than the map's lighter yellow-green. These are visual comparisons, not calibrated color measurements; lighting and rendering styles differ.
- Every Compact carrier uses exactly the same tall, curved, high-roof cab geometry with a separate upper fairing, window outline, doors and steps; only hue/saturation changes. Thus carrier-specific shape identity is not implemented in Compact.
- The current video contains distinct cab presentations, but the overhead view and small native cab resolution limit precise silhouette matching. These crops do not prove a particular bonnet geometry or authorize copying the historical icon's bonnet. Near/crew share the general modern tractor family; red/yellow appear older and squarer. Treat an exact replacement design as requiring a source/model reference, rather than inferring it from old SVG icons.

