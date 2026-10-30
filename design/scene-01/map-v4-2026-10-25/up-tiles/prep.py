"""3x3 cores with 20% padding on a reflect-padded source, so image edges
sit inside the AI tiles. usage: prep.py SOURCE NAME PADFRAC"""
import json, sys, cv2
src, name, pf = sys.argv[1], sys.argv[2], float(sys.argv[3])
S = cv2.imread(src); H, W = S.shape[:2]
px, py = round(W * pf), round(H * pf)
P = cv2.copyMakeBorder(S, py, py, px, px, cv2.BORDER_REFLECT_101)
cv2.imwrite(f"{name}-pad.png", P)
PH, PW = P.shape[:2]
xs = [round(W * i / 3) + px for i in range(4)]; ys = [round(H * i / 3) + py for i in range(4)]
xs[0], ys[0], xs[3], ys[3] = 0, 0, PW, PH
tiles = []
for j in range(3):
    for i in range(3):
        cw, ch = xs[i+1] - xs[i], ys[j+1] - ys[j]
        ex, ey = round(cw * .2), round(ch * .2)
        b = [max(0, xs[i]-ex), max(0, ys[j]-ey), min(PW, xs[i+1]+ex), min(PH, ys[j+1]+ey)]
        n = f"{name}{j}{i}"
        cv2.imwrite(f"{n}.png", P[b[1]:b[3], b[0]:b[2]])
        tiles.append({"name": n, "box": b})
        print(n, b, b[2]-b[0], b[3]-b[1])
json.dump({"pad": [px, py], "size": [W, H], "tiles": tiles}, open(f"boxes-{name}.json", "w"), indent=1)
