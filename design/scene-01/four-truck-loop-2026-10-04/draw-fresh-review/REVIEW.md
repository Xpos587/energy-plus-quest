# Fresh visual review: `v2b-draw-edit.mp4`

## Verdict

**Blocked before a full-loop render/test.** The motion topology is usable as a guide, but the illustrated result does not yet meet the truck-detail contract, and the five-second artifact cannot demonstrate loop closure.

## Coverage

- Full 5.04-second edit sampled every 0.25 seconds: 20 frames from 0.00 through 4.75 seconds.
- Matching 5.00-second controlled-motion source sampled at the same cadence.
- First and final decoded edit frames compared separately; the edit has 121 decoded frames.
- Truck crops inspected at 4x; initial cab crops inspected at 8x only to decide whether occupants were actually legible.
- `frame-01.png` maps to 0.00 seconds, `frame-02.png` to 0.25 seconds, through `frame-20.png` at 4.75 seconds.

## What holds

- Exactly four trucks are visible in every one of the 20 sampled edit frames: blue, green, red, and yellow. No sampled duplicate or extra vehicle appears.
- Each trailer body stays rectilinear through the sampled turns. The tractor and trailer articulate at a joint rather than the trailer body visibly bending.
- The edit follows the controlled source's motion and turn timing closely at the sampled cadence.
- Bright palette, soft cool shadows, and an overall clean illustrated-map treatment are present.

## Blockers and timestamped evidence

1. **The trucks lose the target's articulated-vehicle detail.** At 0.00, 2.25, and 4.75 seconds, the 4x crops show mostly featureless trailer slabs and simplified tractor blocks. The target has distinct wheels and axle groups, articulation hardware, mirrors, grills, lights, windows, and crisp colored edge work. In the edit, most of that is absent or collapses into blur. This is visible for all four colors, most strongly in the green and red trucks while turning at 4.75 seconds.

2. **Cab identity changes through turns.** At 0.00 seconds the cabs read as near-rectangular roof blocks. At 4.75 seconds the red cab becomes a rounded, enlarged blob relative to its trailer, while the green cab changes to a different wedge-like proportion. The controlled source supplies the positions and articulation, but not these illustrated shape changes; this is draw-model instability rather than native route occlusion.

3. **Driver counts cannot be verified.** At 0.00 seconds, the 8x cab crops contain no reliably separable people in any cab. Some views are effectively roof/back views, where occupants would naturally be unverifiable. Even in the later oblique green view at 4.75 seconds, two occupants are not legible. Therefore “green has two drivers; every other truck has one” remains uncertain and is not visually demonstrated by this edit.

4. **The green truck follows a native roof-overlap path from about 3.75 through 4.75 seconds.** The same placement is present in the controlled-motion source: the green tractor/trailer runs across the upper building/roof edge. This is not a new model hallucination. It still violates the final no-roofpaths requirement, so it must be fixed in motion/compositing before the illustrated loop is accepted.

5. **The supplied artifact does not test loop closure.** The first frame and final decoded frame have substantially different vehicle positions. The controlled file is explicitly a five-second motion preview, so this is not evidence that the eventual full loop will jump; it means this edit cannot validate the seam or completed-loop continuity.

## Evidence files

- `actual-contact.png`: all 20 edit samples.
- `source-contact.png`: all 20 controlled-source samples.
- `crops-4x-contact.png`: blue, green, red, and yellow truck crops at 0.00, 2.25, and 4.75 seconds.
- `cabs-8x-contact.png`: initial cab-detail check.
- `target-trucks-contact.png`: four truck crops from `map-v16.png`.
- `actual-3.75-4.75.png` and `source-3.75-4.75.png`: matched late-turn sequence used to classify the green roof overlap as native.
- `actual-first-last.png`: non-closure of this five-second preview.

## Gate for another full-loop attempt

Proceed only after a short draw test preserves one stable, detailed tractor/trailer design per color through a hard turn, makes the required occupants legible in front/oblique views, and moves or masks the green path so it stays off the roof. Then test the actual loop seam with matching start/end vehicle states.
