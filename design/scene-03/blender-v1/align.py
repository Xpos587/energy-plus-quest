# Warp a GPT restyle back onto its Blender render so manifest geometry and
# text overlays still line up.  Global homography (SIFT + RANSAC), then a
# dense optical-flow nudge for the residual local drift.
#   uv run --with opencv-python-headless --with numpy python align.py RENDER GEN OUT [OVERLAY_PREVIEW]
import sys

import cv2
import numpy as np

render_p, gen_p, out_p = sys.argv[1:4]
ref = cv2.imread(render_p)
gen = cv2.imread(gen_p)
H, W = ref.shape[:2]
gen = cv2.resize(gen, (W, H), interpolation=cv2.INTER_LANCZOS4)

g1 = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
g2 = cv2.cvtColor(gen, cv2.COLOR_BGR2GRAY)
sift = cv2.SIFT_create(8000)
k1, d1 = sift.detectAndCompute(g1, None)
k2, d2 = sift.detectAndCompute(g2, None)
m = cv2.BFMatcher().knnMatch(d2, d1, k=2)
good = [a for a, b in m if a.distance < 0.75 * b.distance]
src = np.float32([k2[a.queryIdx].pt for a in good])
dst = np.float32([k1[a.trainIdx].pt for a in good])
Hm, inl = cv2.findHomography(src, dst, cv2.RANSAC, 6.0)
print("matches", len(good), "inliers", int(inl.sum()))
warped = cv2.warpPerspective(gen, Hm, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)

# Residual drift: smooth flow from render to warped restyle, applied as remap.
w2 = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
flow = cv2.calcOpticalFlowFarneback(g1, w2, None, 0.5, 5, 61, 5, 7, 1.5, 0)
flow = cv2.GaussianBlur(flow, (0, 0), 25)
mag = np.linalg.norm(flow, axis=2)
print("residual flow px: median %.1f p95 %.1f max %.1f" % (np.median(mag), np.percentile(mag, 95), mag.max()))
gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
final = cv2.remap(warped, gx + flow[..., 0], gy + flow[..., 1], cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
# Pixels the restyle never covered (outside its frame after the warp) would be
# smeared border repeats; repaint them from their surroundings instead.
valid = cv2.warpPerspective(np.full(gen.shape[:2], 255, np.uint8), Hm, (W, H), flags=cv2.INTER_NEAREST)
valid = cv2.remap(valid, gx + flow[..., 0], gy + flow[..., 1], cv2.INTER_NEAREST)
hole = cv2.dilate((valid < 128).astype(np.uint8) * 255, np.ones((5, 5), np.uint8))
print("uncovered px", int((hole > 0).sum()))
if hole.any():
    small = cv2.resize(final, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    fill = cv2.resize(cv2.inpaint(small, cv2.resize(hole, (W // 4, H // 4)), 9, cv2.INPAINT_TELEA), (W, H), interpolation=cv2.INTER_CUBIC)
    m = cv2.GaussianBlur(hole, (0, 0), 3)[..., None] / 255.0
    final = (final * (1 - m) + fill * m).astype(np.uint8)
cv2.imwrite(out_p, final)
if len(sys.argv) > 4:
    cv2.imwrite(sys.argv[4], cv2.resize(cv2.addWeighted(final, 0.5, ref, 0.5, 0), (W * 768 // H, 768)))
