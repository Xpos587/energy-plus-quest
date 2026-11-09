# Paste only the changed people of a PPE/emotion pass (NEW, already aligned) onto the approved restyle (BASE),
# so the scene outside the people stays pixel-identical.  python paste-people.py BASE NEW OUT
import sys
import cv2
import numpy as np

base, new = (cv2.imread(p) for p in sys.argv[1:3])
d = cv2.absdiff(base, new).max(axis=2)
m = (cv2.GaussianBlur(d, (0, 0), 6) > 18).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 4000])  # people, not speckle
m = cv2.dilate(keep.astype(np.uint8) * 255, np.ones((41, 41), np.uint8))
a = cv2.GaussianBlur(m, (0, 0), 8)[..., None] / 255.0
cv2.imwrite(sys.argv[3], (new * a + base * (1 - a)).astype(np.uint8))
print("pasted area %.3f" % (m > 0).mean())
