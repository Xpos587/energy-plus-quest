# Extend an overview plate downward with an outpainted band, keeping every original pixel (so all plane
# coordinates stay valid). The outpaint input is the plate pasted at the top of a taller grey canvas.
#   uv run --with opencv-python-headless --with numpy python extend.py PLATE GEN NEW_H OUT
# GEN is aligned onto the canvas (SIFT homography on the original part); only rows below the plate are
# taken from it, cross-faded over the plate's last FEATHER rows.
import sys

import cv2
import numpy as np

plate_p, gen_p, new_h, out_p = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
FEATHER = 48
plate = cv2.imread(plate_p)
h, W = plate.shape[:2]
gen = cv2.imread(gen_p)
g1 = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
# the model may return another aspect: start from a uniform fit of its frame onto the canvas width
gen = cv2.resize(gen, (W, round(gen.shape[0] * W / gen.shape[1])), interpolation=cv2.INTER_LANCZOS4)
g2 = cv2.cvtColor(gen, cv2.COLOR_BGR2GRAY)
sift = cv2.SIFT_create(8000)
k1, d1 = sift.detectAndCompute(g1, None)
k2, d2 = sift.detectAndCompute(g2, None)
good = [a for a, b in cv2.BFMatcher().knnMatch(d2, d1, k=2) if a.distance < 0.75 * b.distance]
src = np.float32([k2[a.queryIdx].pt for a in good])
dst = np.float32([k1[a.trainIdx].pt for a in good])
# full affine: the model squeezes the canvas into its own output size (non-uniform scale)
M, inl = cv2.estimateAffine2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4.0)
print("matches", len(good), "inliers", int(inl.sum()), "M", np.round(M, 4).tolist())
warped = cv2.warpAffine(gen, M, (W, new_h), flags=cv2.INTER_LANCZOS4, borderValue=(0, 0, 0))
valid = cv2.warpAffine(np.full(gen.shape[:2], 255, np.uint8), M, (W, new_h), flags=cv2.INTER_NEAREST)
miss = int((valid[h:] < 128).sum())
print("band px not covered by the outpaint", miss)
if miss:
    sys.exit("outpaint does not cover the band; regenerate rather than smear")
out = warped.astype(np.float32)
a = np.ones((new_h, 1, 1), np.float32)  # weight of the original
a[h - FEATHER:h, 0, 0] = np.linspace(1, 0, FEATHER)
a[h:] = 0
out[:h] = plate * a[:h] + out[:h] * (1 - a[:h])
cv2.imwrite(out_p, out.clip(0, 255).astype(np.uint8))
