# Paste the v9.1 vehicle fix (pipe truck 1+3 axles, flat tracked robot) into the bases.
#   python3 vehicles.py -> gen/{wide-base,tall-2}-v91.png (then compose.py)
# gen/veh-*.png = p-vehicles.txt edit of gen/crop-*.png (+ ref/vehicles.png, ref/robot.png).
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

here = Path(__file__).parent / "gen"
# crop box in the base, then truck/robot rectangles in base pixels
JOBS = {
    "wide-base": ((40, 120, 740, 587), [(80, 340, 385, 530), (555, 440, 705, 545)]),
    "tall-2": ((150, 700, 950, 1233), [(190, 820, 525, 1052), (740, 935, 910, 1060)]),
}
for name, ((x0, y0, x1, y1), boxes) in JOBS.items():
    base = Image.open(here / f"{name}.png").convert("RGB")
    edit = Image.open(here / f"veh-{name}.png").convert("RGB").resize((x1 - x0, y1 - y0), Image.LANCZOS)
    mask = Image.new("L", (x1 - x0, y1 - y0))
    for bx0, by0, bx1, by1 in boxes:
        ImageDraw.Draw(mask).rounded_rectangle((bx0 - x0, by0 - y0, bx1 - x0, by1 - y0), 24, fill=255)
    base.paste(edit, (x0, y0), mask.filter(ImageFilter.GaussianBlur(8)))
    base.save(here / f"{name}-v91.png")
