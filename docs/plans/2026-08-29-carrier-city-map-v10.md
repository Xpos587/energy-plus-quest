# Carrier City Map V10 Implementation Plan

**Goal:** Replace the current non-city carrier backdrop with a readable logistics-town map whose warehouse, roads, four vehicle choices, and visual carrier properties are understandable before labels are read.

**Architecture:** Blender is the geometric source of truth for desktop, tablet, and mobile cameras plus color/depth/Canny/ID evidence. ComfyUI performs one-region-at-a-time inpaint/edit passes using the existing production vehicle images as references; no cut-and-paste compositing. React keeps the existing state machine and only receives the accepted raster map and interactive regions.

**Tech Stack:** Blender 5.2 background Python, ComfyUI 0.34 local API with guarded remote fal nodes, deterministic Pillow/OpenCV tools, React + TypeScript + Vite, Playwright. Local generative image models are not allowed.

## Global Constraints

- Preserve the existing game state machine, score values, Express-first-class choice, mandatory Express comparison, static deployment, and current interactive carrier IDs.
- Do not overwrite feedback-v9 production assets; write all candidates and accepted v10 outputs under `design/scene-01/assets/feedback-v10/`.
- Validate the warehouse/loading gate before vehicle visibility and reject any candidate with wrong count, duplicate vehicles, broken roads, moved landmarks, or unreadable vehicle identity.
- Desktop and mobile are separate cameras of one world; do not use a mechanical crop as the mobile art direction.
- Use current production vehicle artwork as ComfyUI references; preserve shape, color, and the Express wordmark through regional editing rather than pasted cutouts.
- Keep `FAL_KEY` out of files, logs, prompts, workflow JSON, screenshots, and commits; rotate the exposed credential after the work.
- Inspect every candidate visually at final display sizes before accepting or connecting it.

### Task 1: Build and validate the v10 structural master

**Files:**

- Modify: `scripts/media/carrier_blockout.py`
- Create: `design/scene-01/assets/feedback-v10/blender/`
- Create: `design/scene-01/assets/feedback-v10/blender/layout.json`

- [ ] Add a clearly identifiable blue logistics warehouse, loading apron, gate, and approach road to the Blender scene; retain four carrier collections and distinct road assignments.
- [ ] Improve camera composition for desktop/tablet/mobile so the warehouse is a landmark, four carrier positions are separated, and the town reads as a city rather than isolated houses.
- [ ] Render color, depth, Canny, and ID evidence for all three cameras into the v10 directory.
- [ ] Run manifest checks for connected roads, warehouse/loading-gate visibility, carrier count, safe bounds, and driver/Express wordmark requirements.
- [ ] Inspect the renders and reject the candidate if the warehouse or any carrier is not readable at final sizes.

### Task 2: Run controlled regional ComfyUI vehicle edits

**Files:**

- Create: `design/scene-01/assets/feedback-v10/comfyui/`
- Create: `design/scene-01/assets/feedback-v10/prompts/`

- [ ] Audit ComfyUI `/system_stats`, `/queue`, `/object_info`, installed models, and node schemas before paid or heavy execution.
- [ ] Create aligned masks that include each vehicle, wheels, contact shadow, road, and nearby snow/occluders; archive hard and feathered masks.
- [ ] Run one small proof with the existing current vehicle reference and the Blender structural guide, validating mask polarity and no background drift.
- [ ] Process old, near, crew, and Express one region at a time with conservative depth/Canny conditioning and current production vehicle references.
- [ ] Visually inspect every output and reject duplicates, changed roads, changed warehouse geometry, malformed vehicles, or lost Express lettering.

### Task 3: Assemble and wire only accepted artwork

**Files:**

- Create: `design/scene-01/assets/feedback-v10/production/`
- Modify: `src/components/CityMap.tsx` only if accepted asset filenames or regions require it
- Test: existing `tests/scene.spec.ts` and `tests/layout.spec.ts`

- [ ] Assemble accepted desktop/tablet/mobile outputs without changing gameplay or carrier IDs.
- [ ] Update React imports and region coordinates only after visual review confirms the same four clickable zones.
- [ ] Run Playwright at desktop and mobile, capture v10 map screenshots, and inspect the rendered browser result rather than relying on DOM assertions.
- [ ] Run `go-task verify`, `bun run test:e2e`, and `git diff --check`; do not commit.

## Addendum: human-in-the-loop mask repair workbench

**Goal:** Replace the single opaque clipspace mask with a local, versioned session in which a person can draw several named/commented masks and the controller can compile one guarded ComfyUI job at a time.

**Decision:** Keep the browser-owned mask document separate from ComfyUI's single-mask Painter state. Export logical RGB masks (`white=edit`, `black=preserve`), keep comments in `manifest.json`, compile `LoadImageMask -> MaskToImage -> <edit node>`, and use `/history/{prompt_id}` to reconcile WebSocket progress. Sequential checkpoints are the default; union mode requires one shared comment.

**Files:** `scripts/media/mask_workbench.py`, `scripts/media/mask_workbench.html`, `scripts/media/test_mask_workbench.py`, plus a versioned session directory under `design/scene-01/assets/feedback-v11/comfyui/interactive-repair/` when the human road mask is saved.

**Safety:** The server binds to loopback, never receives `FAL_KEY`, rejects traversal and stale UI-format graphs, records duplicate-job fingerprints, and requires both `--allow-paid` and the literal `SUBMIT_PAID` confirmation before a partner-node submission. No road repair is submitted until the human mask and prompt are reviewed.

**Run:**

```bash
python scripts/media/mask_workbench.py serve \
  --image design/scene-01/assets/feedback-v11/production/carrier-mobile.png \
  --session-dir design/scene-01/assets/feedback-v11/comfyui/interactive-repair/road-01 \
  --template /home/michael/.local/share/comfyui/ComfyUI/user/default/workflows/fal-inpaint-repair.json
```

The default is dry-run only. Restart with `--allow-paid` only after the saved masks, `overlay.png`, `manifest.json`, and compiled graph have been reviewed. A successful paid pass is downloaded to `candidates/`; accepting it records its hash and advances the sequential checkpoint, while rejecting it leaves the prior source active.

### Addendum: contour-only truck protection for the lower arterial

The broad `road-02-lower-arterial` mask now protects only the Crew and Express silhouettes. `facebook/sam2.1-hiera-tiny` (revision `de431c4043854a71d8101e17995dfe596bf101a5`) was loaded through `HF_TOKEN` for segmentation only; no local image generation ran. The refined RGB masks, raw masks, overlays, manifest, and receipts live under `design/scene-01/assets/feedback-v11/comfyui/interactive-repair/road-02-lower-arterial/`. The session is dry-run/schema-validated and still requires human visual approval plus the explicit `SUBMIT_PAID` confirmation before any remote generation.
