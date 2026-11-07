# Scene 3 warehouse v10 (overview v18, v15 outcomes)

Game-map restyle of the one Blender warehouse (`../blender-v1/warehouse.py`), so every frame shares its geometry.

Overview v17 (November 2026), two plates like scene 1 (wide for landscape stages, tall for phones in portrait; `WorldArt` picks the one with the larger contained area):

1. Render both plates into `.tmp-work/wh3d/bl` (from `../blender-v1`): `SS=2 blender --background --factory-startup --python warehouse.py -- ../../../.tmp-work/wh3d/bl plate desk`, and `LAYOUT=tall … plate tall` (narrower, deeper hall). Copy their `manifest-{wide,tall}-plate.json` here.
2. `gen.sh desk 2048x1360 p-plate.txt` and `gen.sh tall 1600x2000 p-plate.txt`: GPT restyle in the scene 1–2 style (`STYLE`, default `public/scene-art/crane-v2.png`) with `ref/style-people.jpg` for the workwear. The gateway currently returns 1536×1024 and 1121×1403 whatever size is asked.
3. `compose.py desk 1536 1024`, `compose.py tall 1200 1500`: align onto the render, put the Blender lettering (zone boards, rack plaques) and the monitor screen back.
4. `export.py`: `public/scene-art/inventory-master-v10.webp` (16:9 crop on the 1672×941 plane) and `inventory-master-v10-tall.webp` (1200×1500), `segmentedContours.json` / `segmentedContours.mobile.json`, `worldManifest.json` (desktop/mobile) and `alphabet.ts`. Marker tips sit on the anchors: plaque top edges and people's heads; on the wide plate the keeper's pin sits above his head and the WMS pin low at the operator so both stay apart on a 320 px phone.

v18 (6.11, decision after the 5.11 call): the zone boards hang flat on the side walls, each one long board over both doors of its zone, so the lettering is larger. 7.11: full restyle (step 2) with `STYLE=../../../public/scene-art/carrier-results-2026-10-02/crew-wide-v6.webp` (scene 1-2 painterly look instead of the flat outline style) → `compose.py` → `export.py` writes `inventory-master-v10{,-tall}.webp`.

v17 changes against v16: closed slatted roll-up doors (no open, warped doorways), the zone boards stand at 55° in front of the doors so ПРИЁМКА/ОТГРУЗКА read, no trucks or spare trailers (they were cut into unexplained white boxes at the frame edge).

Outcomes (v15) were made with `gen-all.sh` (`ref/master-desk.jpg` style, `p-outcome.txt`).

Layout (November 2026, v15): a compact hall (four bays deep) so racks and people read on a phone. Two receiving doors (left) and two dispatch doors (right) with their signs in the back wall, four scene-2 trucks outside behind it; six four-level rack rows run front to back, each with a vertical navy letter banner as wide as the rack on its front end (А–Б … Ю–Я, left to right, letters stacked); the «Автоподбор» desk with a monitor stands at the back wall; the storekeeper Pavel (grey hair and moustache, no cap, tablet) stands at the front right. Staff wear the company workwear of `ref/style-people.jpg` (crop of `docs/scenario-assets/image20.png`): navy jacket and trousers with reflective stripes, blue caps. Around the hall: a fenced lot with a gate and guard booth, lawns with trees, a car park, containers and a road. The choice UI has no badges or captions: the player taps the objects (hit regions = the projected hulls; the invisible keyboard buttons sit on the objects' anchors). No floor markings or overlays: the gift is a red box with a white ribbon. Route metres to dispatch are measured in Blender (`route_m` in the outcome manifest feeds `RouteCompare`).
