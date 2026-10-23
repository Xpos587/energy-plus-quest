# Animated first scene — working state, 2026-10-05

User-selected motion model: Kling. Deadline: 2026-10-06. Main game remains on the previous assets until a complete four-truck candidate passes. No production deployment performed.

## Current candidates

- Green: [22.75-second full loop and measured seam corrections](assembly/candidate-22.75s/README.md), [interactive zoom preview](preview.html). Five source clips, including a split LEFT→DOWN turn. Independent motion review passes; faint extraction fringe and uneven fine detail remain. Green has two visible driver heads at overview enlargement, but high-detail 4× rendering is not certified.
- Blue: [assembly work](../kling-blue-keys-2026-10-05/assembly/). All four actual corner videos pass independent motion review. Driver count remains uncertain at source resolution. Cab opacity and seam corrections are being checked over the whole sequence.
- Red/yellow: [corrected five-pose references](../kling-fleet-keys-2026-10-05/README.md); [corner generation batch](../kling-fleet-corners-2026-10-05/). Whole-video red Omni Edit failed at the provider; its failed result is retained, not promoted. Using bounded start/end corner generation instead.
- Fleet: [phase planning](../fleet-phase-2026-10-05/), based on observed generated motion, not native tracking. No complete four-truck video is accepted yet.

## Fixed contract

Four distinct trucks. Green has two drivers; red, blue and yellow each have one driver and an empty passenger seat. All four start straight, drive cab-first on their lanes, and remain visible without duplication, cab-end swaps or roof overlap. Blue is visibly slower near the warehouse. Bright clean 2D style, soft coloured contours and shadows, without black outlines, stains or sepia. Only the first scene is animated.

Immutable composition background: [empty map](../four-truck-loop-2026-10-04/v2b-empty-map.png). This 1505×1045 source is not true 4K detail. The separate [native 4K fallback](../painted-layer-2026-10-05/) preserves geometry but its flatter visual style is not accepted.

Actual prompts, input frames, failed provider trials and independent review receipts remain beside their source clips. Gemini findings are hypotheses to check against actual frames; documented unsupported claims are not treated as defects. No native 48-second tracking may be substituted for Kling motion. Final video, poster and observed tracking must be installed together and checked in the game at 1×, 2× and 4× on desktop and mobile.
