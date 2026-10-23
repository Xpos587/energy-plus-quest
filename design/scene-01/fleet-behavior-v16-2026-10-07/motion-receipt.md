# v16 bounded motion proof

The candidate `fleet-v16-motion.blend` renders frames 1–192 at 24 fps (8 seconds). `fleet-v16.blend` keeps the original full route animation. The proof resamples both tractor and trailer from the same original time, without changing their path or relative articulation.

| Truck | Role | Measured scene units/second | Travel over 8 seconds |
|---|---|---:|---:|
| 1 red | faster old truck | 6.892905 | 55.143243 |
| 2 blue | creep near warehouse | 0.910341 | 7.282729 |
| 3 green | steady wide route | 6.892859 | 55.142875 |
| 4 yellow | slower old truck | 4.135700 | 33.085601 |

These are scene units, not km/h. Red moves 1.6667 times as fast as yellow. Blue uses only source frames 1–87.4 over this proof, retaining its warehouse-side initial segment.

`motion-analysis.json` contains actual per-frame conservative footprint checks: visible mesh bounds form separate oriented tractor/trailer rectangles; every rendered frame checks all vehicle pairs and 47 major building envelopes, including architecture hidden for background compositing. Zero envelope overlaps; minimum separating-axis gaps are 6.481568 scene units between vehicles and 2.628611 to major architecture. Positive envelope separation rules out intersection within those bounds. Street furniture, subframe swept volumes, and full-loop interactions are not qualified by this bounded check.

`motion-readback.json` verifies the saved file after reopening. All 193 samples (including the exact eight-second endpoint) agree with the paired source poses to maximum matrix error 0.000000537; relative tractor–trailer matrix error is 0.000006199.

The excerpt is not a seamless eight-second loop. Independent source-route periods under these rates are 48 seconds (red/green), 80 seconds (yellow), and 106⅔ seconds (blue). Original long animations remain in the geometry source; no claim of a collision-free combined long loop is made.

Commands:

```sh
blender -b design/scene-01/fleet-behavior-v16-2026-10-07/fleet-v16.blend --python design/scene-01/fleet-behavior-v16-2026-10-07/retime_v16.py -- --apply
blender -b --python design/scene-01/fleet-behavior-v16-2026-10-07/verify_motion_v16.py
```

Rendering and visual review are separate evidence owned by the parent task. No production/UX files changed.
