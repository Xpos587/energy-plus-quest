# Actual v11 animation delivery

`fleet-v11-video.blend` is the video master. It derives from the fully verified v11 coupling master and hides the four unsupported floating rear underrun bars identified during PDF review. See `rear-bar-fix.json` for the exact scope. The corrected side/front stills in this directory were rendered from geometry.

Run or resume from the repository root:

```sh
sh design/scene-01/fleet-video-v11-2026-10-07/run_render.sh
```

The pipeline renders every animation frame independently, first the geometric shadow pass and then full-resolution vehicle color. Existing frame files support resuming interrupted work. Encoding starts only after both complete passes.

The shadow is the animated visible vehicle mesh projected along the approved SUN onto the ground. Translucent smoke does not cast this pass. A soft coverage edge approximates the angular light source. It is not a Cycles light-transport render; `benchmark-warm.json` records the measured OPTIX alternative. The still/PDF shadow pass remains the separately rendered Cycles result. The video compositor uses the same approved neutral tint and opacity and masks the shadow off painted roofs.

Evidence and delivery:

- `fleet-v11-48s.mp4`: resulting actual animation.
- `video-validation.json`: encoded stream readback, frame count, duration, dimensions and source references.
- `color-receipt.json`, `projected-shadow-receipt.json`: source render configuration and measurements.
- `shadow-full.log`, `color-full.log`, `encode.log`: complete job logs.
- `video-frame-*.png`: selected actual composed timeline frames.
- `pilot-composite-0385.png`: early representative turning preview; the final video uses the later corrected source without floating rear bars.

No production code or frontend assets are modified. The parent task owns final PDF packaging, independent visual review and Telegram delivery.
