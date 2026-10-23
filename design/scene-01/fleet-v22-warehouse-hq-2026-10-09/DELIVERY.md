# First scene v22 — local game delivery

The complete animated map is installed in the main local game at http://127.0.0.1:4173/ and rebuilt successfully. The updated map was opened in normal Chrome and left available for review. No remote deployment was performed.

## Delivered artifacts

- [Full master video](package/v22-game-loop-64s-4k.mp4): 64 seconds, 1536 frames, 24 fps, 3840 × 2668.
- [Review PDF](package/v22-scene-review.pdf): full map, actual scenario warehouse photograph beside the new warehouse, equal-display-size clarity comparison.
- Web variants: desktop 3600 × 2500, tablet 2560 × 1778, mobile 1920 × 1334. Encoded directly from composited source pixels, not recompressed from a lossy master.
- Saved Messages: PDF message244747, video message244752. Both messages and media presence verified by readback in [telegram-readback.json](package/telegram-readback.json).

## Canonical production sources

- [Blender source](render/v22-4k-source.blend): v21 compact trailer wheel track and closer coupling, camera/routes retained.
- [City and warehouse layer](city/city-final.png): the active artistic background. Use this in the compositor for future renders; the old architectural donor is only a reference.
- [Compositor/encoder](package/compose.py), [render completion](render/full-complete.json), [installation/backup receipt](package/install-receipt.json).
- Warehouse reference comes from the 08.10.2026 scenario, `docs/scenario-assets/image8.png`. Required three loading bays, СКЛАД label and exact vector Газпром нефть branding are retained. See [city review and provenance](city/REVIEW.md).

## Verification

- All3074 source PNGs decoded;66 render batches,0 failures. The extra frame1537 is only a closure diagnostic, not a duplicated hold in the delivered video.
- All four MP4 outputs fully decoded: [validation.json](package/validation.json).
- Source closure and exported roof tracking verified: [seam-check.json](package/seam-check.json). Decoded beginning/end samples are retained beside it.
- All1536 motion intervals passed the existing road/obstacle clearance contract: [clearance-check.json](package/clearance-check.json).
- Independent still review of frames384/768/1152/1536 passed warehouse integration, visible coupling and contact checks. This is distinct from video review.
- Gemini reviewed the actual64-second desktop video at4 fps; no listed motion/occlusion defect was reported. Uploaded file removed: [review](package/video-review.md), [coverage/cleanup receipt](package/video-review-receipt.json). Sampling cannot establish the absence of every one-frame defect.
- Final app build and TypeScript passed.12 source-selection regression cases passed, including1517px/DPR2.5 with misleading slow-transfer timing.
- Compiled game: desktop and mobile64-second loop-boundary tests passed. Roof tracking/pan passed at320,390,844,768,1440px. The first320px cold-start attempt timed out waiting for video readiness; the isolated rerun passed without changing the test or product.
- Desktop no longer falls to1920 because of an estimated slow load. Only explicit Save Data reduces desktop to2560. Small coarse-pointer screens remain capped at2560. Source stays stable during inspection/zoom.
- Actual visible Chrome at1517 ×877/DPR2.5 decoded3600 ×2500 at2.4× inspection zoom:11 dropped out of2555 frames during the measured interval, including UI/screenshot interaction. [Chrome receipt](package/chrome-quality.json). Headless software-decoding measurements are retained separately and are not representative of this browser result.

## Quality limits

Vehicles were rendered natively at3840 ×2668. The static city was enhanced with a CGI upscale and a separately detailed warehouse patch; this is not a claim of native4K detail in every original background pixel. Extreme4× zoom can still exceed source resolution. The source and high-quality master are retained for future output choices.

No pending work remains for this local render/integration delivery. Broader scene/UX revisions and production deployment are separate tasks.
