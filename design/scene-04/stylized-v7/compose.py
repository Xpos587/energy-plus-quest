"""Run from .tmp-work/crane-r10 (inputs: ../crane-r8/gen, gen/, paintin/). r10: paint only what changed (people + Petr's pontoon) into the r8 paintings.
patch (gpt-image edit of a 1.5x crop) -> ECC to the new Blender crop -> blend over the old painting
inside the Blender diff mask (old vs new paintin), dilated and feathered."""
import cv2, json, numpy as np
pm = json.load(open('../crane-r8/gen/input/manifest-paintin.json'))
crops = json.load(open('gen/input/crops.json'))
def edges(b):
    g = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    return cv2.GaussianBlur(cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1)), (0, 0), 2)
for f, (x0, y0, x1, y1) in crops.items():
    W, H = pm[f]['width'], pm[f]['height']
    old = cv2.resize(cv2.imread(f'../crane-r8/gen/{f}-1.png'), (W, H), interpolation=cv2.INTER_CUBIC)
    newb = cv2.imread(f'paintin/paintin-{f}.png'); oldb = cv2.imread(f'../crane-r8/gen/input/{f}-1x.png')
    cw, ch = x1 - x0, y1 - y0
    patch = cv2.resize(cv2.imread(f'gen/{f}-patch.png'), (cw, ch), interpolation=cv2.INTER_AREA)
    warp = np.eye(2, 3, dtype=np.float32)
    _, warp = cv2.findTransformECC(edges(newb[y0:y1, x0:x1]), edges(patch), warp, cv2.MOTION_AFFINE,
                                   (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), None, 5)
    print(f, 'ecc', np.round(warp, 4).tolist())
    patch = cv2.warpAffine(patch, warp, (cw, ch), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    d = (np.abs(newb.astype(int) - oldb.astype(int)).sum(2) > 40).astype(np.uint8)[y0:y1, x0:x1]
    d = cv2.morphologyEx(d, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    m = cv2.dilate(d, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 4)[..., None]
    # keep the seam soft at the crop border too
    edge = np.ones((ch, cw), np.float32); edge[[0, -1], :] = 0; edge[:, [0, -1]] = 0
    m = m * cv2.GaussianBlur(cv2.erode(edge, np.ones((15, 15))), (0, 0), 4)[..., None]
    out = old.astype(np.float32)
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - m) + patch * m
    cv2.imwrite(f'gen2/{f}-1.png', out.round().astype(np.uint8))
    cv2.imwrite(f'qa/composed-{f}-crop.png', out[y0:y1, x0:x1].round().astype(np.uint8))
