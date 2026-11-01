# Scene 5 choice map, v9

Redrawn on 1 November 2026 with GPT Image 2 (`cx/gpt-image-2`, quality high) in the
style of the opening route thumbnails, like `design/scene-03/v9`. No Blender base.

1. `p-wide.txt`: refs `ref/route-lastmile.png`, `ref/warehouse-v9.png` (style),
   `ref/scenario.png` (layout), `ref/abk.png` (vendor modular АБК), `ref/vehicles.png`,
   `ref/robot.png` -> two drafts; draft 2 = `gen/wide-base.png` (1672×941, Arseniy).
2. `p-tall.txt`: refs route thumbnail + approved wide -> `gen/tall-2.png` (1024×1536).
3. `p-dest-alva.txt` (+ `ref/mayma.png`) and `p-dest-khor.txt` edit the destination crop
   (wide 630×420+1042+0, tall 600×400+424+20) -> `gen/dest-{wide,tall}-{alva,khor}.png`.
4. `python3 compose.py` pastes only the changed people back -> `gen/{wide,tall}-{alva,khor,arseniy}.png`.
5. `contours.py` (OpenCV GrabCut in the vehicle boxes) on the Arseniy images -> `contours.json`,
   then `python3 export.py contours.json` writes the six runtime WebP files to
   `public/scene-art/lastmile-family-v1/revision-9/` and `src/scenes/lastmile/segmentedContours.json`.

`gen/` is local generation output (ignored). Archive checksums live only in root `media-artifacts.json`.
