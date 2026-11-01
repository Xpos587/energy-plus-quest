# v9 art -> runtime WebP (native size, like scene-03/v9) and the vehicle tap contours.
#   python3 compose.py && python3 export.py [contours.json]
# contours.json comes from contours.py (GrabCut) over gen/{wide,tall}-arseniy.png;
# vehicles are identical in all three recipients.
import json
import sys
from pathlib import Path

from PIL import Image

here = Path(__file__).parent
root = here.parents[2]
base = "scene-art/lastmile-family-v1/revision-9"
pub = root / "public" / base
pub.mkdir(parents=True, exist_ok=True)

for fmt in ("wide", "tall"):
    for who in ("alva", "khor", "arseniy"):
        Image.open(here / f"gen/{fmt}-{who}.png").convert("RGB").save(pub / f"choice-{fmt}-{who}.webp", quality=86, method=6)

if len(sys.argv) > 1:
    contours = json.loads(Path(sys.argv[1]).read_text())
    for fmt in contours:
        contours[fmt]["source"] = f"{base}/choice-{fmt}-*.webp"
    (root / "src/scenes/lastmile/segmentedContours.json").write_text(json.dumps(contours, separators=(",", ":")))
