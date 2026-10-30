# Blockout review sheet: each plate cropped exactly as the game viewport shows
# it ("cover" fit), with the question panel drawn where the real UI puts it.
import json
from PIL import Image, ImageDraw, ImageFont

m = json.load(open("out/blockout.json"))
F = lambda s: ImageFont.truetype("/usr/share/fonts/inter/InterVariable.ttf", s)
# (plate, viewport w, h, panel rect in viewport px or None, label)
VIEWS = [
    ("wide", 1440, 844, (1024, 552, 1424, 828), "Ноутбук 1440×900"),
    ("wide", 844, 334, (516, 78, 836, 326), "Телефон лёжа 844×390"),
    ("tall", 390, 582, None, "Телефон 390×844 (вопрос под картой)"),
    ("tall", 320, 310, None, "Маленький 320×568"),
]
tiles = []
for plate, w, h, panel, label in VIEWS:
    im = Image.open(f"out/blockout-{plate}.png").convert("RGB")
    W, H = im.size
    k = max(w / W, h / H)
    im = im.resize((round(W * k), round(H * k)), Image.LANCZOS)
    x0 = (im.width - w) // 2
    y0 = (im.height - h) // 2
    im = im.crop((x0, y0, x0 + w, y0 + h))
    d = ImageDraw.Draw(im, "RGBA")
    if panel:
        d.rounded_rectangle(panel, 14, fill=(255, 255, 255, 235), outline=(4, 19, 39, 80))
        d.text((panel[0] + 16, panel[1] + 14), "панель вопроса", fill=(4, 19, 39), font=F(15))
    P = m["plates"][plate]
    def px(p):
        return (p[0] * W * k - x0, p[1] * H * k - y0)
    for key, col, txt in (("dock", (255, 85, 0), "погрузка"), ("express", (0, 60, 166), "новая фура")):
        x, y = px(P[key])
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=col)
    tiles.append((im, label))

legend = [((220, 38, 33), "Красная, старая, 36 км/ч: средний круг сверху"),
          ((250, 200, 13), "Жёлтая, старая, 27 км/ч: средний круг справа"),
          ((26, 89, 217), "Синяя, 17 км/ч: малый круг вокруг склада и офиса"),
          ((46, 179, 56), "Зелёная, 2 водителя, 48 км/ч: большой внешний круг"),
          ((255, 85, 0), "Оранжевая точка: ворота склада, сюда появляется новая фура")]
pad = 24
sheet_w = 1440 + 844 + pad * 3
sheet_h = 60 + 844 + pad + 40 + 582 + pad * 2 + 30
sheet = Image.new("RGB", (sheet_w, sheet_h), (237, 243, 248))
d = ImageDraw.Draw(sheet)
d.text((pad, 16), "Сцена 1 · схема v4: один город, два кадра (широкий и вертикальный), маршруты по полосам", fill=(4, 19, 39), font=F(26))
pos = [(pad, 60), (1440 + pad * 2, 60), (1440 + pad * 2, 60 + 334 + 50), (1440 + pad * 2 + 390 + pad, 60 + 334 + 50)]
for (im, label), (x, y) in zip(tiles, pos):
    sheet.paste(im, (x, y + 26))
    d.text((x, y), label, fill=(4, 19, 39), font=F(18))
ly = 60 + 334 + 50 + 26 + 582 + 30
for k, (col, txt) in enumerate(legend):
    yy = 60 + 844 + 26 + pad + k * 34
    d.rectangle((pad, yy + 4, pad + 28, yy + 20), fill=col)
    d.text((pad + 40, yy), txt, fill=(4, 19, 39), font=F(20))
sheet = sheet.crop((0, 0, sheet_w, max(ly, 60 + 844 + 26 + pad + 5 * 34 + pad)))
sheet.save("out/review-blockout.png")
sheet.convert("RGB").resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save("out/review-blockout-small.jpg", quality=88)
print(sheet.size)
