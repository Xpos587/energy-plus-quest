# Full game loop delivery — 2026-10-09 Moscow

## Delivered

- Master: `v20-game-loop-64s.mp4`, 1920 × 1334, 24 fps, 1536 frames, 64 seconds.
- PDF: `v20-game-loop-review.pdf`.
- Saved Messages 6352363131: PDF 244491, video 244492; readback confirmed both media messages.
- Local runtime installed in `public/scene1-live/separated-routes` with matching first-frame poster and `src/game/carrierTracking.json` (1536 rows). Desktop preserves the master; tablet 864×600, mobile 720×500. All variants passed full decode.
- `dist` rebuilt successfully with the new media and optimized poster. No remote deployment or Git commit.

## Verification

- Source and render receipts: RENDER.md, loop-contract.json, validation.json, routes/fresh-hull-proof.json.
- Independent source/decoded-frame review approved the loop. All 1536 RGBA frames stay inside the camera, minimum pixel margin 131. Rendered boundary 1537 matches frame 1; last-to-first motion matches ordinary adjacent-frame motion.
- `bun run test src/components/CarrierTracking.test.tsx`: 3 passed.
- `bun run build:app`: passed.
- `bunx playwright test tests/carrier-tracking.spec.ts --project=desktop-chromium --workers=1`: 5 passed, five viewport sizes.
- `bunx playwright test --config .tmp-work/v20-loop-preview.config.ts`: 2 passed against compiled app, actual carrier-choice screen. Verified duration 64 seconds, automatic end-to-start playback, desktop/mobile source selection. Screenshots inspected in test-results/v20-loop-preview.
- Initial delivery-test entry assumed pre-onboarding flow; corrected test to follow current intro and open the carrier-choice screen. No product change needed for that failure.

## Recovery and scope

Atomic install receipt and recoverable old runtime files are outside deployed public assets: `/home/michael/.local/state/energy-plus-quest/runtime-integration-2026-10-08/install-receipt.json`.

Routes changed from the nonperiodic eight-second proof to safe periodic full routes. Green has the highest loop-average speed; blue slows near the warehouse and accelerates away. Red/yellow have opposite-phase pacing but equal full-loop averages. Displayed vehicle facts express scenario maximum speeds, not measured map-world average speeds. Do not claim a strict red-over-yellow average ranking. Existing responsive map cropping/panning behavior is unchanged.
