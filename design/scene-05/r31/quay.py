import cv2 as cv
import numpy as np
from PIL import Image, ImageFilter


def move_crane(art):
    x0, y0 = 1600, 1230
    tile = np.array(art.crop((x0, y0, x0 + 320, y0 + 300)))
    shape = tile.shape[:2]
    # Trace the painted outline, open trusses and ladder, not the unpainted Blender ID pass.
    # fmt: off
    edges=[[(104,51),(104,44),(112,34),(124,41),(198,60),(202,57),(202,63),(200,69),(205,110),(219,115),(212,135),(201,151),(190,164),(188,171),(197,195),(199,201),(205,249),(208,275),(214,275),(219,283),(215,290),(198,291),(194,288),(176,292),(174,282),(181,275),(189,275),(188,261),(118,261),(109,278),(116,278),(120,285),(115,292),(84,293),(80,288),(77,279),(70,279),(66,278),(66,271),(82,211),(67,211),(60,212),(59,207),(50,205),(53,201),(62,199),(65,202),(75,196),(84,184),(90,179),(87,176),(86,171),(91,131),(122,107),(112,56)],
           [(124,44),(192,62),(184,67),(155,112)],
           [(100,187),(104,182),(115,189),(123,185),(127,192),(99,192)],
           [(98,202),(122,202),(111,232)],
           [(121,250),(137,203),(154,203),(155,210),(175,210),(186,250)],
           [(73,273),(85,224),(90,217),(105,248),(94,276),(84,276),(82,280)],
           [(120,277),(188,277),(186,261),(117,261),(110,277)],
          ]
    # fmt: on
    guide = np.zeros(shape, "uint8")
    cv.fillPoly(guide, [np.int32(edges[0])], 1)
    for hole in edges[1:]:
        cv.fillPoly(guide, [np.int32(hole)], 0)
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (7, 7))
    mark = np.where(cv.dilate(guide, kernel), cv.GC_PR_BGD, cv.GC_BGD).astype("uint8")
    mark[guide > 0] = cv.GC_PR_FGD
    mark[cv.erode(guide, kernel) > 0] = cv.GC_FGD
    cv.setRNGSeed(31)
    cv.grabCut(
        tile,
        mark,
        None,
        np.zeros((1, 65), "float64"),
        np.zeros((1, 65), "float64"),
        4,
        cv.GC_INIT_WITH_MASK,
    )
    alpha = (mark % 2) * 255
    # The port edge continues behind the hoist. Clone adjoining granite courses and same-depth tundra on their respective sides.
    yy, xx = np.indices(shape)
    edge = 131 + (yy - 43) * 0.367
    inside = (xx < edge) & (yy >= 43)
    stoneX = np.rint(1332 + (xx - 48) * 0.56).astype(int)
    # Use an unoccupied bay for the rear apron and two actual bollard pitches for the front apron.
    landX = np.rint(1850 + (xx - 159) * 0.85).astype(int)
    quayX = x0 + xx - 346
    repl = np.array(art)[
        y0 + yy, np.where(yy >= 225, quayX, np.where(inside, stoneX, landX))
    ]
    clear = np.zeros(shape, "uint8")
    cv.fillConvexPoly(clear, cv.convexHull(np.int32(edges[0])), 255)
    cv.fillPoly(
        clear,
        [
            np.int32(
                [(73, 243), (203, 244), (305, 287), (310, 292), (150, 293), (76, 292)]
            )
        ],
        255,
    )
    clear = cv.dilate(clear, np.ones((7, 7), "uint8"))
    clear[294:] = 0
    art.paste(
        Image.fromarray(repl),
        (x0, y0),
        Image.fromarray(clear).filter(ImageFilter.GaussianBlur(1.2)),
    )
    # The mooring line belongs to the barge; keep it attached to the original bollard.
    line = np.zeros(shape, "uint8")
    cv.polylines(
        line,
        [np.int32([(139, 299), (139, 292), (143, 285), (151, 277), (155, 276)])],
        False,
        255,
        4,
        cv.LINE_AA,
    )
    art.paste(Image.fromarray(tile), (x0, y0), Image.fromarray(line))
    mask = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.4))
    bounds = mask.getbbox()
    layer = Image.fromarray(tile).convert("RGBA")
    layer.putalpha(mask)
    layer = layer.crop(bounds)
    # Keep the footing at the pier lip. The smaller footprint clears the existing robot's silhouette.
    w, h = (132, 202)
    x, y = (1309, 1319)
    layer = layer.resize((w, h), Image.Resampling.LANCZOS)
    shadow = cv.warpAffine(
        np.array(layer.getchannel("A")),
        np.float32([[1, -0.30, 0.30 * h], [0, 0.15, 0.85 * h]]),
        (w + 65, h + 3),
    )
    art.paste(
        "#34354a",
        (x, y, x + w + 65, y + h + 3),
        Image.fromarray(shadow)
        .filter(ImageFilter.GaussianBlur(0.7))
        .point(lambda a: a * 0.4),
    )
    art.paste(layer, (x, y), layer)
    return [x, y, w, h]
