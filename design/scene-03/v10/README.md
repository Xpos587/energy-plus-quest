# Scene 3 warehouse v10

Game-map restyle of the one Blender warehouse (`../blender-v1/warehouse.py`), so every frame shares its geometry.

1. Render plate (wide, tall) and outcomes with `warehouse.py` into `.tmp-work/v13/bl`; `manifest-*.json` here are those renders' manifests.
2. Desk: `media_images.py edit` with the desk notext render, `ref/style-map.jpg`, `ref/style-people.jpg` and `p-desk.txt` → accepted result saved as `ref/master-desk.jpg`.
3. Tall and outcomes: `gen-all.sh` (`gen.sh` uses `ref/master-desk.jpg` as the style reference; prompts `p-tall.txt`, `p-outcome.txt`).
4. `compose.py NAME W H`: align onto the render, put the Blender lettering, painted floor routes and kiosk screen back.
5. `export.py`: webp into `public/scene-art/warehouse-v12`, story layer (gift ring), hit contours.

Layout (November 2026): both docks in the front wall, the scene-2 trucks (blue cab-over tractor, white ribbed trailer) nose-to-camera in the foreground, goods run a U from the receiving door past the alphabet racks to the dispatch door. Outcome routes and their metres are painted on the floor in Blender (`route_m` in the outcome manifest feeds `RouteCompare`).
