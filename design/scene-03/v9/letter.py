# Letter the blank plaques and gate boards: render crisp text and warp it into each measured quad.
#   python3 letter.py   (gen/ovc.png, gen/mob.png -> gen/desk-final.png, gen/tall-final.png)
import json, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/TTF/Roboto-Black.ttf"
RANGES = ["А–Б", "В–К", "Л–М", "Н–У", "Ф–Э", "Ю–Я"]
# Quads measured with quads.py/find.py: top-left, top-right, bottom-right, bottom-left.
LAYOUTS = {
    "desk": {"src": "gen/ovc.png", "plaques": [
        [[410, 155], [503, 160], [499, 206], [410, 198]],
        [[529, 176], [618, 180], [617, 222], [529, 215]],
        [[650, 188], [747, 193], [741, 237], [650, 229]],
        [[775, 201], [874, 207], [869, 253], [775, 244]],
        [[903, 216], [1007, 224], [1001, 270], [902, 261]],
        [[1035, 234], [1148, 241], [1145, 290], [1036, 279]]],
        "receiving": [[32, 152], [292, 95], [288, 154], [27, 222]],
        "dispatch": [[1296, 125], [1520, 174], [1519, 243], [1296, 184]]},
    "tall": {"src": "gen/mob.png", "plaques": [
        [[188, 291], [276, 291], [276, 330], [188, 330]],
        [[299, 291], [382, 291], [381, 330], [298, 330]],
        [[413, 291], [496, 292], [495, 330], [412, 330]],
        [[526, 291], [612, 292], [610, 330], [525, 330]],
        [[638, 291], [736, 292], [724, 330], [638, 330]],
        [[748, 291], [836, 291], [831, 330], [748, 330]]],
        "receiving": [[9, 347], [130, 257], [136, 322], [8, 418]],
        "dispatch": [[890, 257], [1013, 347], [1013, 417], [896, 322]]},
}


def stamp(img, quad, text, color, scale=0.62):
    quad = np.float32(quad)
    w = int(max(np.linalg.norm(quad[1] - quad[0]), np.linalg.norm(quad[2] - quad[3])) * 4)
    h = int(max(np.linalg.norm(quad[3] - quad[0]), np.linalg.norm(quad[2] - quad[1])) * 4)
    tile = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(tile)
    size = int(h * scale)
    font = ImageFont.truetype(FONT, size)
    while d.textlength(text, font=font) > w * 0.86:
        size -= 2
        font = ImageFont.truetype(FONT, size)
    d.text((w / 2, h / 2), text, font=font, fill=255, anchor="mm")
    m = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), quad)
    a = cv2.warpPerspective(np.asarray(tile, np.float32) / 255, m, (img.shape[1], img.shape[0]), flags=cv2.INTER_AREA)
    img[:] = img * (1 - a[..., None]) + np.array(color, np.float32) * a[..., None]


out = {}
for name, L in LAYOUTS.items():
    img = np.asarray(Image.open(L["src"]).convert("RGB"), np.float32)
    for quad, text in zip(L["plaques"], RANGES):
        stamp(img, quad, text, (0x16, 0x32, 0x4F))
    stamp(img, L["receiving"], "ПРИЁМКА", (255, 255, 255), 0.5)
    stamp(img, L["dispatch"], "ОТГРУЗКА", (255, 255, 255), 0.5)
    Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(f"gen/{name}-final.png")
    H, W = img.shape[:2]
    out[name] = {"plaques": [[round(sum(p[0] for p in q) / 4 / W, 4), round(sum(p[1] for p in q) / 4 / H, 4)] for q in L["plaques"]],
                 "signs": [[min(p[0] for p in L[k]), min(p[1] for p in L[k]), max(p[0] for p in L[k]), max(p[1] for p in L[k])] for k in ("receiving", "dispatch")]}
json.dump(out, open("gen/letters.json", "w"), indent=1)
print(json.dumps(out))

# Alphabet outcomes face the racks head-on: plaque boxes (x0, y0, x1, y1) from find.py on gen/o-*.png (1960x840).
OUTCOMES = {
    "alphabet-boat": [(170, 121, 350, 185), (421, 121, 623, 184), (670, 122, 849, 184), (912, 121, 1097, 185), (1162, 124, 1345, 186), (1404, 126, 1574, 187)],
    "alphabet-socks": [(258, 138, 446, 199), (490, 138, 665, 199), (720, 139, 892, 200), (945, 139, 1119, 199), (1176, 139, 1351, 200), (1408, 139, 1583, 200)],
    "alphabet-camera": [(111, 122, 299, 186), (350, 104, 539, 186), (591, 104, 780, 187), (833, 124, 1024, 187), (1075, 125, 1268, 188), (1320, 104, 1509, 188)],
}
for name, boxes in OUTCOMES.items():
    img = np.asarray(Image.open(f"gen/o-{name}.png").convert("RGB"), np.float32)
    for (x0, y0, x1, y1), text in zip(boxes, RANGES):
        stamp(img, [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], text, (0x16, 0x32, 0x4F), 0.66)
    Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(f"gen/o-{name}.png")
