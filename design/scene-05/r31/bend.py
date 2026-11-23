import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def finish_bend(art, view, sheet):
    # Both strips were edited at the same scale. Limit the composite to water and the immediate banks;
    # all buildings, the camp, and the river above and below the former junction retain their original paint.
    # fmt: off
    if view=='wide':
        x,y,row=170,500,0
        banks=[(266,503),(307,529),(384,540),(495,555),(600,577),(669,592),(703,612),(711,646),(726,682),(759,710),(734,758),(603,749),(568,703),(541,655),(474,631),(373,614),(277,585),(229,556)]
    else:
        x,y,row=0,670,512
        banks=[(-20,650),(58,656),(153,677),(260,703),(350,722),(389,752),(404,799),(428,846),(458,874),(371,925),(293,887),(261,832),(236,795),(177,765),(82,738),(-20,726)]
    # fmt: on
    patch = sheet.crop((0, row, 1536, row + 512)).resize(
        (900, 300), Image.Resampling.LANCZOS
    )
    mask = Image.new("L", patch.size)
    ImageDraw.Draw(mask).polygon([(a - x, b - y) for a, b in banks], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(5))
    a = np.array(mask)
    a[:9] = np.uint8(a[:9] * np.linspace(0, 1, 9)[:, None])
    art.paste(patch, (x, y), Image.fromarray(a))
