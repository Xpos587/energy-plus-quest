# Scene 3 warehouse v10 (art v15)

Game-map restyle of the one Blender warehouse (`../blender-v1/warehouse.py`), so every frame shares its geometry.

1. Render plate (wide, tall) and outcomes with `warehouse.py` into `.tmp-work/v17/bl`; `manifest-*.json` here are those renders' manifests.
2. Desk: `media_images.py edit` with the desk notext render, `ref/style-map.jpg`, `ref/style-people.jpg` and `p-desk.txt` → accepted result saved as `ref/master-desk.jpg`.
3. Tall and outcomes: `gen-all.sh` (`gen.sh` uses `ref/master-desk.jpg` as the style reference; prompts `p-tall.txt`, `p-outcome.txt`).
4. `compose.py NAME W H`: align onto the render, put the Blender lettering (zone and rack signs) and the desk monitor screen back.
5. `export.py`: webp into `public/scene-art/warehouse-v15`, hit contours, and it updates `worldManifest.json` hotspots, `alphabet.ts` plaque positions and `outcomeFraming.ts`.

Layout (November 2026, v15): a compact hall (four bays deep) so racks and people read on a phone. Two receiving doors (left) and two dispatch doors (right) with their signs in the back wall, four scene-2 trucks outside behind it; six four-level rack rows run front to back, each with a vertical navy letter banner as wide as the rack on its front end (А–Б … Ю–Я, left to right, letters stacked); the «Автоподбор» desk with a monitor stands at the back wall; the storekeeper Pavel (grey hair and moustache, no cap, tablet) stands at the front right. Staff wear the company workwear of `ref/style-people.jpg` (crop of `docs/scenario-assets/image20.png`): navy jacket and trousers with reflective stripes, blue caps. Around the hall: a fenced lot with a gate and guard booth, lawns with trees, a car park, containers and a road. The choice UI has no badges or captions: the player taps the objects (hit regions = the projected hulls; the invisible keyboard buttons sit on the objects' anchors). No floor markings or overlays: the gift is a red box with a white ribbon. Route metres to dispatch are measured in Blender (`route_m` in the outcome manifest feeds `RouteCompare`).
