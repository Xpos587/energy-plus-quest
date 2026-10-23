# Artwork review, 11 October 2026

## Preparation cards

Eight model-outpainted backgrounds are connected through `preparationCardArtwork` in `src/game/artwork.ts`; `GiftPreparation` uses them only in choice cards. Existing portrait sources remain in the selected-person summary. Sources are preserved as PNG, runtime images encoded as WebP quality 95. No separate tablet artwork is needed.

Browser captures in `review/` cover three setup screens at 1440×900, 1920×1080, 390×844, 320×568, 820×1180 and 844×390. All 18 screens were independently inspected. The landscape full-body crop and tablet camera-strap crop found in the first pass were corrected; the second pass found no clipped subjects, blank image bands, overflow or unloaded images.

## Warehouse and quay

Four restored warehouse sources live in `design/warehouse-restored-2026-10-11/`; every parcel routes to `public/scene-art/warehouse-restored-2026-10-11/{entrance,alphabet,keeper,wms}.webp`. Faces and linework were restored by the image model while retaining the original actions, neutral boxes and PPE layout. Tiny raster insignia remain stylized illustration detail, not vector-perfect brand lettering.

Crane rails use neutral wide/tall V6 artwork. Rails terminate with buffer stops; the pedestrian route follows door, landing, stairs, paved apron and near-crane stairs. Both SVG route strokes share one path.

The tall source plane and its segmented contours remain together. Desktop, mobile and tablet choice framing includes both crane booms and office stairs. The outpainted surrounding illustration is registered behind the source plane, with a narrow blended edge. Registration of tall V6 to surroundings: 1790 SIFT matches, 802 RANSAC inliers, median inlier error 1.4288 px. The inverse affine matrix is implemented in `WorldArt.tsx`. Selecting Petr focuses the far crane; its number is positioned beside the cab.

`scene-review/` contains 28 live captures: four warehouse outcomes and three crane states at desktop, wide, mobile and tablet sizes. Desktop/wide surrounding blend, route and contour placement passed independent visual review. Warehouse expressions, anatomy and PPE passed visual review across all 16 captures. The final mobile/tablet choice and route, plus mobile/desktop Petr inspections, were independently rechecked after framing changes: both cranes fit, marker 4 stays beside the cab, contours align and no distracting blend seam remains.

## Checks

`bun run build:app` passes. Five relevant test files pass (45 tests). The full existing suite reports 351 passing and 16 failing tests plus 6 unhandled errors: unrelated restart/header/zoom/media expectations, stale result-reader queries, and missing `Image.decode` in jsdom. The full suite is not green; its logs are `.tmp-work/art-tests-final.log`. Relevant asset-path expectations were updated to the new versions.

`review.pdf` combines actual setup, warehouse and quay browser screenshots.
