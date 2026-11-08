# /// script
# dependencies = ["torch", "transformers", "opencv-python-headless", "numpy", "pillow"]
# ///
"""Tighten scene-5 vehicle contours with SAM (box prompt = bbox of the current polygon).

Run from the repo root with any Python that has torch+transformers+opencv (e.g. the ComfyUI venv):
  python scripts/tighten-lastmile-contours.py [boxes.json]
boxes.json optionally overrides a prompt box, e.g. {"wide-robot": [x0, y0, x1, y1]} in contour units.
Writes segmentedContours.json in place and overlay crops to $TMPDIR/lastmile-contours/.
"""
import json, os, re, sys, cv2, numpy as np, torch
from PIL import Image
from transformers import SamModel, SamProcessor
Image.MAX_IMAGE_PIXELS = None
dev = "cuda" if torch.cuda.is_available() else "cpu"
model = SamModel.from_pretrained("facebook/sam-vit-huge").to(dev).eval()
if dev == "cuda": model = model.half()
proc = SamProcessor.from_pretrained("facebook/sam-vit-huge")
path = "src/scenes/lastmile/segmentedContours.json"
d = json.load(open(path))
boxes = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
prev = os.path.join(os.environ.get("TMPDIR", "/tmp"), "lastmile-contours"); os.makedirs(prev, exist_ok=True)
for comp in ["wide", "tall"]:
    full = Image.open(f"public/scene-art/lastmile-family-v1/revision-12/choice-{comp}-alva.webp").convert("RGB")
    W, H = full.size
    for vid, r in d[comp]["regions"].items():
        pts = np.array(list(map(float, re.findall(r"-?\d+(?:\.\d+)?", r["path"])))).reshape(-1, 2) * 2
        bx = boxes.get(f"{comp}-{vid}")
        x0, y0, x1, y1 = (np.array(bx) * 2).tolist() if bx else [*pts.min(0), *pts.max(0)]
        pad = 80
        cx0, cy0, cx1, cy1 = int(max(x0 - pad, 0)), int(max(y0 - pad, 0)), int(min(x1 + pad, W)), int(min(y1 + pad, H))
        crop = full.crop((cx0, cy0, cx1, cy1))
        inp = proc(crop, input_boxes=[[[x0 - cx0, y0 - cy0, x1 - cx0, y1 - cy0]]], return_tensors="pt").to(dev)
        if dev == "cuda": inp["pixel_values"] = inp["pixel_values"].half()
        with torch.no_grad(): out = model(**inp, multimask_output=True)
        masks = proc.image_processor.post_process_masks(out.pred_masks.float().cpu(), inp["original_sizes"].cpu(), inp["reshaped_input_sizes"].cpu())[0][0].numpy()
        scores = out.iou_scores[0, 0].float().cpu().numpy()
        k = int(scores.argmax()); m = masks[k].astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        m = (lab == 1 + int(st[1:, cv2.CC_STAT_AREA].argmax())).astype(np.uint8)
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cs, key=cv2.contourArea)
        c = cv2.approxPolyDP(c, 3.0, True).reshape(-1, 2) + [cx0, cy0]
        r["path"] = "M" + " L".join(f"{x / 2:.1f},{y / 2:.1f}" for x, y in c) + " Z"
        print(comp, vid, "scores", scores.round(3), "pick", k, "pts", len(c))
        img = np.array(crop)[:, :, ::-1].copy()
        cv2.polylines(img, [(c - [cx0, cy0]).astype(np.int32)], True, (255, 0, 255), 3)
        s = 700 / max(img.shape[:2]); img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        cv2.imwrite(f"{prev}/{comp}-{vid}.jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 82])
open(path, "w").write(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
