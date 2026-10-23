# Green truck layer prototype

Use `composite.mp4` for the empty-map composition; `green-layer-rgba.mov` is a ProRes 4444 transparent layer. Lossless straight-alpha PNGs are in `rgba-frames/`.

`before-after-contact.jpg` compares source, isolated layer on checker, and composition at all six requested times. `detail-*.png` retains native-resolution truck/path crops for edge inspection.

The measured source, camera padding, frame timing, algorithm, validation, corrected failures, and remaining mask limits live in [extraction-report.json](extraction-report.json). This is a bounded prototype, not a production mask acceptance.

Rebuild with:

```sh
mkdir -p tmp
TMPDIR="$PWD/tmp" uv run --no-project --with opencv-python-headless --with numpy python extract_layer.py
ffmpeg -y -framerate 24 -i composite-frames/%04d.png -c:v libx264 -threads 2 -preset fast -crf 18 -pix_fmt yuv420p -movflags +faststart composite.mp4
ffmpeg -y -framerate 24 -i rgba-frames/%04d.png -c:v prores_ks -profile:v 4 -pix_fmt yuva444p10le -threads 2 -alpha_bits 16 green-layer-rgba.mov
```
