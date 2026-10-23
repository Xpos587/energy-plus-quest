# Green loop assembly work

The full loop is gated by actual motion validity. Decisions and native evidence are recorded once in [segment-review.json](segment-review.json). Rejected originals and replacements remain available for inspection; they are not assembled into a deceptive loop.

Downloaded provider clips are `segment-2.mp4`, `segment-3.mp4`, `segment-4.mp4`, `segment-2-retry.mp4`, and `segment-2-crop.mp4`. Quarter-second source contacts and selected native frames sit beside them.

`segment-3-layer/` and `segment-4-layer/` contain extracted RGBA frames, exact padded empty-map composites, six native detail strips, and their own extraction receipts. Rebuild either with `extract_segment.py 3` or `extract_segment.py 4` using the same lightweight `uv` dependencies as the first extraction prototype.

The original first layer remains in `../../kling-layer-extract-2026-10-05/rgba-frames/`. Future accepted assembly should use the first 120 frames of each segment and omit each provider's extra boundary frame.

`seam-correction/` contains the bounded final-segment translation candidate, native boundary comparison, corrected RGBA frames, corrected segment video, and a side-by-side seam video. The transformation, road-clearance method, motion metrics, visual limitations, and acceptance status live in [correction-report.json](seam-correction/correction-report.json). `correct_final_seam.py` reproduces the correction while preserving every original layer.

No production app or approved preview was modified.
