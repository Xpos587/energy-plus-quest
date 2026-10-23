# Warehouse v23 delivery

User approved `warehouse-final.png`; applied to the main local game, not just the scene gallery. No remote deployment.

- City: `city/city-final.png`, approved warehouse composited at (340,360), 740×780 patch with a feathered architecture/apron mask. Pixels outside the patch unchanged.
- Motion: existing v22 native vehicle/shadow frames and tracking preserved.
- Master: `package/v23-game-loop-64s-4k.mp4`, 3840×2668.
- Runtime: desktop 3600×2500, tablet 2560×1778, mobile 1920×1334; all 64 seconds, 1536 frames, 24 fps, full decode passed (`package/validation.json`).
- Installed into `public/scene1-live/separated-routes/`; cache key v23. Backup and successful app build recorded in `package/install-receipt.json`.
- Source closure verified (`package/seam-check.json`). Compiled game tests at 1440×900 and 390×844 verified v23, resolution, duration, four truck targets and playback wrapping from 63.75 seconds to the start: 2 passed (`package/runtime-tests.log`). Test harness updated to current onboarding; old selectors initially failed before reaching the map.
- Main game also visibly checked in Chrome at port 4173; playing tablet v23, 2560×1778, duration 64 seconds, loop true. Screenshots: `package/game-desktop.png`, `package/game-mobile.png`.
- Independent gpt-5.6-sol medium composite reviewer passed architecture, perspective, road/pavement blending and sampled truck clearance. Unchanged motion was not re-reviewed as new animation.
- PDF: `package/v23-scene-review.pdf`, visually checked. Telegram delivery receipts are in `package/telegram-*.json`.
