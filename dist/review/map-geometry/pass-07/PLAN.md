# Responsive map scale - pass 07

Goal: a working, full-viewport responsive review of the current material city, with larger readable trucks on 320px/375px iPhone SE, tablet, desktop and landscape. Keep the game and approved pass-06 review archived and unchanged during exploration.

## Evidence and decision

- GPNS group 5546232558: Ed, September 8 and 16, point 4: machines are small and unclear; Teo, September 16 15:17: hard to tap the machine, larger scale helps.
- September 16 meeting 24:00, 25:05-28:35: increase scale, cut peripheral blocks, mobile first; vehicle differences must be visual. September 7 10:30: trucks too small. July 30: mobile priority. August 12: office browser zoom 125-140% is a real use case.
- UI-skills MCP: pbakaus/adapt and jakubkrehel/better-layout. Adapt the composition to the available container, not device names; separate controls from content, >=44px touch targets, safe areas, support short/landscape screens. Real-device verification is distinct from emulation.
- UCGIS, Mobile Maps and Responsive Design (2018), https://doi.org/10.22224/gistbok/2018.2.5: mobile map generalization and change of scale/layout, not simply shrinking all map symbols.
- Mapbox padding example, https://docs.mapbox.com/mapbox-gl-js/example/offset-vanishing-point-with-padding/: fit the meaningful map viewport after allocating panel space. Reuse the principle, not the dependency or the sample's zoom prohibition.
- web.dev viewport units and W3C enhanced target size fetched into research/. Native CSS + existing MP4 is sufficient; no Mapbox, WebGL runtime, new dependency or pan/zoom requirement.

Baseline measured from pass-06 meshes over all 768 frames: a 320x350 map, fitted to all trucks and warehouse, has a minimum truck long edge of 38.80 CSS px. check_scale.py fails against a proposed 48px floor. This floor is an engineering hypothesis, not Fedor's approval or proof of recognizing two drivers.

## Work

- [x] Search Telegram, local meeting transcripts, UI-skills MCP and web; inspect existing player/layout and actual scene geometry.
- [x] Export baseline projected truck meshes and warehouse bounds; reproduce the scale failure.
- [x] Calibrate larger trucks in the isolated candidate. Retain their shape/materials and city buildings; validate all routes, articulated envelopes and visibility before rendering. Do not enlarge sprites on top of unchanged roads.
- [x] Fit full-loop active bounds, including touch margins, inside the actual map container; panel below on narrow layouts and beside on wide layouts. Peripheral context may crop, never a truck/dock. Keep browser zoom enabled. On genuinely short screens allow page scrolling instead of shrinking indefinitely.
- [x] Build the isolated review with existing brand fonts, native choice controls, synchronized map targets, poster/media-failure fallback and reduced-motion handling. No game score changes or production integration.
- [x] Verify responsive geometry throughout the loop, control interactions, resizing/orientation, playback and source switching in browser; inspect screenshots at CSS pixel size. Record unsupported real iPhone/Telegram testing honestly.

Deliver current review URL, measured before/after scale and verification report. Approval of two-driver storytelling is not implied by a size test; current truck geometry has opaque windows and no driver figures.

## Completed verification

Published isolated pass-07 review at /review/map-geometry/index.html. Pass-06 page archived with verified original SHA-256. All 14 Chromium viewport scenarios pass, with full-loop geometry checks, synchronized seeks, keyboard/touch selection, captured moving targets, cancelled drag, source-switch phase, loop, reduced motion, media failure and retry. Native browser zoom, physical iPhone/Safari and Telegram WebView remain explicit device-verification gaps. Portrait tablets now put controls below the map; short landscape layouts compact their controls and allow vertical scrolling.
