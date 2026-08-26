# Carrier V9 blockout

Reproduce from the repository root:

```bash
blender --background --python scripts/media/carrier_blockout.py -- \
  --output-dir design/scene-01/assets/feedback-v9/blockout
```

The Blender startup warning about the optional `cattrs` package comes from the
distribution's remote asset-library add-on and does not affect background
rendering.

## Cameras

- `CameraDesktop`: location `(22.5, -29.0, 27.0)`, target `(0.2, 2.1, 0.7)`,
  55 mm, output `1536x864`.
- `CameraMobile`: location `(17.0, -34.0, 34.0)`, target `(-0.8, 2.5, 0.5)`,
  60 mm, output `944x1792`.

## Narrative placement

- `OldCarrier`: `(-10.5, 7.0)`, small muted-brown truck on the far road beside
  an inspection booth.
- `NearCarrier`: `(3.2, 0.2)`, neutral truck at the loading gate behind a
  barrier and snow bank.
- `CrewCarrier`: `(-3.2, -5.2)`, large blue foreground cab with two occupants.
- `ExpressCarrier`: `(4.6, -3.4)`, modern orange truck on the open foreground
  road with a restrained snow plume.

The PNGs are structural guides, not production artwork. `*-color.png` carries
layout and semantic color, `*-depth.png` provides coarse depth conditioning and
`*-canny.png` provides edge conditioning.
