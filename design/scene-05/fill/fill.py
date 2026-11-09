# Scene 5 results fill near-square / portrait blocks without bands, blur or stretching (task 08.11).
# The 16:9 flight and pipe-carrier paintings were outpainted upward (sky) and downward (taiga / road)
# with Higgsfield FLUX.2 Pro Outpaint, one run per family:
#   higgsfield generate create flux_2_pro_outpaint --image gen/in-flight.png --expand_top 500 --expand_bottom 759 --wait --json
#   (in-flight.png = revision-5/flight-parcel.webp at 1672x941; in-pipe.png = revision-2/pipe-carrier-khor.webp)
# -> gen/hf-flight.png, gen/hf-pipe.png (1672x2200, original at y 500..1441).
# `python3 fill.py` pastes every recipient/parcel original back over its band so only the bands are new.
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

here = Path(__file__).parent
art = here.parents[2] / "public/scene-art/lastmile-family-v1"
out = art / "revision-13"
JOBS = {
    "flight": ("revision-5", ["flight-parcel", "flight-boat", "flight-parcel-arseniy", "flight-boat-arseniy"]),
    "pipe": ("revision-2", ["pipe-carrier-alva", "pipe-carrier-khor", "pipe-carrier-arseniy"]),
}
W, H, TOP, MID = 1672, 2200, 500, 941

# Original pixels everywhere except a 40px blend at the top and bottom seams.
mask = Image.new("L", (W, MID))
ImageDraw.Draw(mask).rectangle((-99, 40, W + 99, MID - 41), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(14))

out.mkdir(exist_ok=True)
for job, (revision, names) in JOBS.items():
    canvas = Image.open(here / f"gen/hf-{job}.png").convert("RGB")
    assert canvas.size == (W, H), canvas.size
    for name in names:
        img = canvas.copy()
        mid = Image.open(art / revision / f"{name}.webp").convert("RGB").resize((W, MID), Image.LANCZOS)
        img.paste(mid, (0, TOP), mask)
        img.save(out / f"{name}-tall.webp", quality=86, method=6)
        print(out / f"{name}-tall.webp")
