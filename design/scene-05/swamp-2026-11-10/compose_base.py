# Step 1: paste Higgsfield swamp edits (gen/hf-swamp-*.png) back into the revision-12 arseniy canvas.
#   uv run --with pillow --with numpy python compose_base.py  -> gen/base-{wide,tall}.png
from pathlib import Path
import numpy as np
from PIL import Image
here = Path(__file__).parent
R = here.parents[2] / "public/scene-art/lastmile-family-v1/revision-12"
JOBS = {"wide": ((0, 196, 4112, 3290), "y"), "tall": ((103, 0, 3122, 3904), "x")}
F = 90
SW = {"wide": "swamp4-wide", "tall": "swamp4-tall"}
for k, ((x, y, w, h), axis) in JOBS.items():
    base = Image.open(R / f"choice-{k}-arseniy.webp").convert("RGB")
    new = Image.open(here / f"gen/hf-{SW[k]}.png").convert("RGB").resize((w, h), Image.LANCZOS)
    m = np.ones((h, w), np.float32)
    ramp = np.linspace(0, 1, F, dtype=np.float32)
    if axis == "y":
        m[:F] *= ramp[:, None]; m[-F:] *= ramp[::-1][:, None]
    else:
        m[:, :F] *= ramp[None]; m[:, -F:] *= ramp[::-1][None]
    ba = np.asarray(base).astype(np.float32)
    # Outside the crop the old wide river would show at the map edge: reflect the new art into those strips instead.
    pad = ((y, ba.shape[0] - y - h), (x, ba.shape[1] - x - w), (0, 0))
    full = np.pad(np.asarray(new).astype(np.float32), pad, mode="reflect")
    if axis == "y":  # wide: original forest strips top/bottom, feathered seam (no mirrored artefacts)
        ba[y:y+h, x:x+w] = ba[y:y+h, x:x+w] * (1 - m[..., None]) + full[y:y+h, x:x+w] * m[..., None]
    else:
        ba = full
    Image.fromarray(ba.astype(np.uint8)).save(here / f"gen/base-{k}.png"); print(k, base.size)
