# Scene 01 concept PNG package — 9 September 2026

Local presentation exports prepared from the current browser UI for the GPN-S concept review.

## Main desktop set

`desktop/` contains five 3840x2160 PNG captures at a 1920x1080 viewport and DPR 2, following one real journey:

1. `01-profile.png` — profile choice, unhovered
2. `02-recipient.png` — recipient choice (`Альва`)
3. `03-parcel.png` — parcel choice (`Фотоаппарат`)
4. `04-map-no-lines.png` — carrier map, stable paused frame with four passive labels and no leader lines
5. `05-outcome-crew-two-drivers.png` — crew result with two drivers

`mobile/` contains the same five screens at 1170x2532 (390x844 viewport, DPR 3) as an optional phone set. `contact-sheet.jpg` is a compact desktop preview.

The package intentionally does not include later warehouse/barge/last-mile screens: those stages are not implemented in scene 01. The PNGs were captured locally through the real UI; no mock screens or generated lettering were added. Current local professional and Arseniy artwork is used as-is.

## Checks

- Official SVG logos are optically aligned by visible height and center rather than forced to the same CSS width.
- Capture script checks image decoding, four map labels, absence of interactive map hotspots, crew outcome visibility, console/page errors, image dimensions, and SHA-256 checksums. The reproducible script and diagnostics are archived in the external r38 archive.
- No Telegram message, upload, deployment, commit, stage, `dist/`, or `release/` artifact is part of this package.

## Map identity and edge repair (r38)

Supersedes the rejected r37 edge patch. Badges now sit directly on their own trailer roofs and follow the presented video frame, without route-interior avoidance or delayed smoothing. Both videos are rebuilt with the unchanged r27 truck geometry/paths and corrected static bottom continuations. Desktop continuation comes from one new authorized outpaint; mobile continuation uses the recovered original r25 source. No mirrored, tiled, stretched, or repeated edge strips are used. The authored plane retains its intrinsic aspect ratio.

Evidence and updated capture manifest: external archive `r38-map-identity-and-edges/`. Includes natural-speed loop recordings, six viewport captures, exact frame-anchor regression tests, and full-body quarter-frame swept checks. The compact badges overlay trailer roofs; tiny-screen two-driver detail remains limited by the existing artwork scale.

## Motion update (r39)

Presentation PNGs refreshed from the final 60fps motion build. The r38 approved city bases and extension assets remain byte-identical; only vehicle pose sampling/rasterization and matching trailer-label tracks changed. Both 64-second videos contain 3840 genuinely rendered frames. The offline renderer uses subpixel sprite translation, route-tangent heading, and a periodic road-constrained correction field checked at quarter-frame intervals. Evidence: external `r39-truck-motion-smooth/`.
