# Assembled fallback search, 2026-10-05

## Actually acquired, but rejected visually

CC0 Cab-over sleeper tractor, 3D Assets author's own distribution:
https://3dassets.dev/assets/long-haul-trucking-and-truck-stop-cabover-sleeper-b86f0719
Direct official file: https://cdn.3dassets.dev/assets/13946/v1/model.glb
License: CC0 1.0 Universal, explicitly commercial use and modifications allowed on the source page.
Local file: `cc0-cabover-sleeper-3dassets.glb`.
Source page saved: `cc0-cabover-sleeper-source.html`.
Imported with Blender 5.2.2 using `--disable-autoexec`; only our own `preview_assembled_cc0.py` ran.
Local validation render: `cc0-cabover-preview.png`.
Measured 28 meshes, 37 nodes, 8 materials, 6,756 mesh triangles. It is already assembled and supports wheel-roll/cab-doors-open animations.
However, visual inspection rejected it: a boxy cab with flat windshield, classic American-style rectangular grille and exhaust stacks. It fails the requested modern rounded European truck identity. DO NOT substitute it for the approved truck.
This is a previously published AI-assisted procedural asset; no generation or purchase was triggered.

## Exact access blocker for suitable assembled asset

Primary author PAndras, Scania truck, CC Attribution:
https://sketchfab.com/3d-models/scania-truck-59889032d0ad457c81d7e058c79eedf8
The indexed official model page identifies 249.1k triangles and CC BY. A direct request to the official download endpoint
https://api.sketchfab.com/v3/models/59889032d0ad457c81d7e058c79eedf8/download
returned HTTP 401: {"detail":"Authentication credentials were not provided."}
Saved as `sketchfab-assembled-download-response.json`. No authenticated browser is available in this fallback turn (`cua.listBrowsers()` returned []). We did not bypass access controls, scrape the viewer geometry, create an account or accept terms. The actual suitable geometry was NOT acquired.

## Other rejected leads

OpenGameArt Semi-Trailer Truck (lowpoly), https://opengameart.org/content/semi-trailer-truck-lowpoly, is CC0 and downloadable, but its author preview (`oga-semi-preview.jpg`) is a primitive American bonneted truck with polygon wheels, not the required truck. Did not download its blend.
The prior Paolo Printables source remains the only acquired high-detail commercially permitted modern European truck in this folder, but requires assembly of its STL parts.

Conclusion: the narrow fallback did obtain and validate an assembled CC0 asset, but no asset meeting BOTH the visual contract AND access/license constraints was acquired. The suitable ready-assembled Sketchfab model is blocked by authentication.
