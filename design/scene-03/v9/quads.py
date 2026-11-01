# Print 4-corner quads of plaque/sign candidates and save a debug overlay.
import sys, cv2, numpy as np
img = cv2.imread(sys.argv[1]); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, s, v = [hsv[..., i].astype(int) for i in range(3)]
masks = {"white": (s < 30) & (v > 205), "blue": (h > 100) & (h < 125) & (s > 110) & (v > 90), "orange": (h > 5) & (h < 22) & (s > 150) & (v > 190)}
dbg = img.copy()
for name, m in masks.items():
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cs:
        a = cv2.contourArea(c)
        if a < (1200 if name == "white" else 4000): continue
        hull = cv2.convexHull(c)
        q = cv2.approxPolyDP(hull, 0.04 * cv2.arcLength(hull, True), True)
        if len(q) != 4 or a < 0.8 * cv2.contourArea(hull): continue
        print(name, q.reshape(-1, 2).tolist())
        cv2.polylines(dbg, [q], True, (0, 0, 255), 3)
cv2.imwrite(sys.argv[2], dbg)
