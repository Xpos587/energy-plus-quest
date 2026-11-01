# Locate blank plaques (near-white) and gate sign boards (blue/orange) on a generated overview.
import sys, cv2, numpy as np
img = cv2.imread(sys.argv[1]); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, s, v = [hsv[..., i].astype(int) for i in range(3)]
def comps(mask, name, minarea):
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
    for i in range(1, n):
        x, y, w, hh, a = st[i]
        if a >= minarea and w > hh * 1.2 and a > 0.55 * w * hh:
            print(name, x, y, x + w, y + hh, a)
comps((s < 30) & (v > 205), "white", 1200)
comps((h > 100) & (h < 125) & (s > 150) & (v > 120), "blue", 4000)
comps((h > 5) & (h < 20) & (s > 170) & (v > 200), "orange", 4000)
