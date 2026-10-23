# Fresh visual review — `composite-12s.mp4`

## Verdict

**Not viable for the full 48-second render.** The deterministic motion is readable, but the visible composite does not preserve the accepted truck design or convincing articulation. Extending it would repeat the same defects for four times longer.

## Coverage

Reviewed the complete 12 seconds at 0.5-second intervals, plus the main turn window from 4.00–7.75 seconds at 0.25-second intervals. Compared actual rendered frames with `map-v16.png` and the visible single-truck turn in `kling.mp4`.

## Blocking issues

1. **The articulation looks disconnected rather than mechanically rigid.** Trailer boxes remain straight, but the coupling is visibly wrong. Around 5.50 seconds the green cab sits apart from its trailer; yellow has a long flat tongue; blue reads as a cab block separated by a rectangular bridge. At 7.00 seconds the same gap/tongue construction is still obvious on green, red, and yellow. Kling keeps the rigid cab and trailer close-coupled with wheels and a believable pivot throughout its turn.

2. **The trucks look pasted onto the accepted map.** From 0.00 seconds onward they are narrow, low-detail 3D-like blocks over a richly painted background. They lack the target's dark colored outlines, shaped cabs, mirrors, lights, axle groups, articulation hardware, and grounded soft shadows. Scale and perspective also differ from `map-v16`, so even straight travel reads as a foreign overlay.

3. **Road-edge and roof/foliage layering does not hold visually.** During the 5.50–7.00 second turn window, the green and red vehicles pass over building-edge and tree/sidewalk regions without being occluded or visually grounded. Their always-on-top rendering makes them read as crossing the roof/foreground layer even where the intended coordinates may be a road. Deterministic coordinates do not make the actual composite look correctly aligned.

4. **Drivers are not visible.** No reviewed composite frame resolves occupants in any cab. The green two-driver requirement is especially unverified. By comparison, Kling visibly preserves two people in the green cab during its front/three-quarter turn views.

## What is usable

The background is stable, four truck colors remain distinguishable, and the broad turn paths are understandable. Those are useful motion-layout inputs, but not a visual pass.

## Gate before full 48

Do another short composite only after the truck assets match `map-v16` in scale and painted detail, use a close fifth-wheel pivot with visible axle groups, receive road-aware shadows and foreground occlusion masks, and show the required occupants in front/three-quarter views. Recheck the hardest 5.50–7.00 second turn before expanding duration.
