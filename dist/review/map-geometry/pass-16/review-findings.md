# Pass 16: review scope

Only the new pass16 is owned by this task. The user confirmed that another agent owns the remaining scenes/current scene2 warehouse loading. Its concurrent `src/scenes/WorldArt.tsx` modification is authorized unrelated work; no source-scene file was edited or reverted here. The original snapshot is retained, and preservation assertions now scope prior public art, pass12/pass15 production sources and the original character, not the entire repository.

Pixel checks pass: zero changes outside local truck/road masks; previous art hashes preserved; greige roofs, foliage color masks, roof equipment, warehouse doors, seven dock lines, fence silhouettes, retained crossing paint and approved truck3 glass/crew remain unchanged. OCR reads roof numbers 1, 2, 3, 4 in delivered pixels; all four truck regions contain actual edits. PNG and lossless browser WebP are identical. Both girl placements are independently reconstructed from the unchanged original character.

Three local generated vehicle candidates are used. Truck3's candidate was rejected because panel/edge geometry drifted; its original roof is cleaned deterministically instead. Its two people, glass, outline and ground contact stay original. No whole-map generation, transformation, new dependencies or game changes.

Manual visual review covers the full map, all four before/after truck crops and all four road-detail pairs. Older cabs are square and maintained with small exhaust wisps, not wrecks; truck2 has ordinary clean slate-blue modern bodywork, distinct from truck1; truck3 keeps the approved naturally glazed crew without winner effects. Number4 remains orange. No fifth Express vehicle exists. These are artistic observations, not automatic semantic assertions.

Limits: this is static illustration, not speed/animation verification. Small crew details require zoom or closeups on a phone. JPEG comparisons are lossy; invariance applies to PNG/WebP. Real Telegram/iOS and Safari are not covered by Chromium. Parent artistic review and user approval remain separate gates.

Chromium verification passed at 1440x1000, 390x844, 320x568, 820x1180 and 568x320: before/after toggle, both girl placements including actual screenshot pixels, 300% zoom, four numbered review cards, 44px buttons, no page overflow or JavaScript errors, downloaded PNG/JPEG byte equality and all local linked assets matching HTTP bytes. Desktop/mobile full-page screenshots and the other three map viewport screenshots were visually inspected. No blocking defect found in this scoped review; final parent artistic review is still required.

Checks and screenshots: `artifact-check.json`, `validation.json`, plus the working pass16 `screenshots/`. Reproduce with the existing ComfyUI Python environment: run `check_artifacts.py`, then `node browser-check.cjs` with the local server on port4173. No files staged.
