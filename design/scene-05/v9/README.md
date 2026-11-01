# Scene 5 choice map, v9 (runtime revision-10 = v9.1)

Redrawn on 1 November 2026 with GPT Image 2 (`cx/gpt-image-2`, quality high) in the
style of the opening route thumbnails, like `design/scene-03/v9`. No Blender base.

1. `p-wide.txt`: refs `ref/route-lastmile.png`, `ref/warehouse-v9.png` (style),
   `ref/scenario.png` (layout), `ref/abk.png` (vendor modular АБК), `ref/vehicles.png`,
   `ref/robot.png` -> two drafts; draft 2 = `gen/wide-base.png` (1672×941, Arseniy).
2. `p-tall.txt`: refs route thumbnail + approved wide -> `gen/tall-2.png` (1024×1536).
3. v9.1 vehicles: `p-vehicles.txt` (+ `ref/vehicles.png`, `ref/robot.png`) edits the vehicle crop
   (`gen/crop-*.png` -> `gen/veh-*.png`): pipe truck 1 + 3 axles, flat tracked robot cart with a
   strapped box and orange beacons. `python3 vehicles.py` pastes only those two vehicles
   -> `gen/{wide-base,tall-2}-v91.png`.
4. `p-dest-alva.txt` (+ `ref/mayma.png`) and `p-dest-khor.txt` edit the destination crop
   (wide 630×420+1042+0, tall 600×400+424+20) -> `gen/dest-{wide,tall}-{alva,khor}.png`.
   `python3 compose.py` pastes only the changed people back -> `gen/{wide,tall}-{alva,khor,arseniy}.png`.
5. v9.1 canvas: `p-extend.txt` / `p-extend-tall.txt` outpaint grey-padded bases
   (`gen/pad-*.png` -> `gen/ext-*.png`); `python3 extend.py` places each map inside
   (wide 1672×1393 at +0+226, tall 1280×1536 at +128+0) -> `gen/*-ext.png`, so the camera
   can cover any stage without grey bands.
6. RealESRGAN x4plus (ComfyUI model, tiled), then Lanczos to 2× -> `gen/*-ext-2x.png`.
7. `contours.py` (OpenCV GrabCut in the vehicle boxes) on the Arseniy `-ext` images -> `contours.json`,
   then `python3 export.py contours.json` writes the six runtime WebP files to
   `public/scene-art/lastmile-family-v1/revision-10/` and `src/scenes/lastmile/segmentedContours.json`.

`gen/` is local generation output (ignored). Archive checksums live only in root `media-artifacts.json`.
