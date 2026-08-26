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

- `CameraDesktop`: location `(58.0, -72.0, 67.0)`, target `(0.0, 0.0, 1.0)`,
  58 mm, output `1536x864`.
- `CameraMobile`: location `(70.0, -105.0, 100.0)`, target `(2.0, 0.0, 0.8)`,
  50 mm, output `944x1792`.

## Narrative placement

- `OldCarrier`: `(-19.0, 11.5)` on `north-service`, beside an inspection booth.
- `NearCarrier`: `(11.5, 7.0)` on `warehouse-spur`, facing out from the loading
  gate and stopped by a barrier and snow bank.
- `CrewCarrier`: `(-10.5, -3.0)` on `west-diagonal`, with two visible occupants.
- `ExpressCarrier`: `(8.0, -12.0)` on `south-arterial`, with an unobstructed lane
  and restrained snow plume.

The blockout covers a `70m x 56m` ground plane with ten town buildings, a
warehouse district and six named road segments. `validate_layout()` prevents
two carriers from sharing a road id and rejects pairwise distances below `7m`.

The PNGs are structural guides, not production artwork. `*-color.png` carries
layout and semantic color, `*-depth.png` provides coarse depth conditioning and
`*-canny.png` provides edge conditioning.
