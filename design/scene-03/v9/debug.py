import json
from PIL import Image, ImageDraw
R = json.load(open("regions.json"))
for name in ("desk", "tall"):
    im = Image.open(f"gen/{name}-final.png").convert("RGB"); d = ImageDraw.Draw(im)
    for k, r in R[name].items():
        d.rectangle(r.get("box") or r["rack"], outline=(255, 0, 0), width=4)
        x, y = r["anchor"]; d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(0, 200, 0))
    im.thumbnail((900, 900)); im.save(f"/home/michael/Github/energy-plus-quest/.tmp-work/v/s3n/dbg-{name}.jpg", quality=80)
