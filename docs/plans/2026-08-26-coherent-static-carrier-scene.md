# Coherent Static Carrier Scene Implementation Plan

> **For agentic workers:** After this plan is written, present the execution gate to the user (`/goal-prep` board vs inline executing-plans). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the V8 layered carrier collage with independently composed desktop and mobile town panoramas whose four transport properties are understandable from four separate road districts.

**Architecture:** Build a deterministic Blender blockout of a substantial northern town with several blocks, independent roads, four distinct vehicles, occupants and narrative cue props. Render color, depth and edge guides for two separately art-directed cameras, generate four overlapping regional crops per viewport, composite them with feathered masks and run a low-strength whole-frame harmonization pass. The UI renders one responsive raster with four semantic React hotspots.

**Tech Stack:** Blender 5.2 Python API, Python 3.11 via `uv`, Pillow, fal.ai FLUX Control LoRA/FLUX.2/Qwen, React 19, TypeScript 7, CSS Modules, Vitest, Playwright, Bun.

## Global Constraints

- Follow `docs/specs/2026-08-26-coherent-static-carrier-scene-design.md`.
- Each raster has exactly one primary warehouse, 8-12 substantial buildings and exactly four delivery vehicles.
- Every vehicle occupies a different road branch or district; no queue, convoy, shared apron or head-on lane conflict is allowed.
- Vehicle silhouettes are structurally different: older box truck, compact van, tall crew truck and streamlined Express.
- No final truck is a transparent layer, separate DOM image, CSS drawing or SVG drawing.
- Animation, route traces and labels are not required to understand any option.
- Preserve carrier IDs, scores, reducer behavior, outcomes and Russian copy.
- Author desktop `1536x864` and mobile `944x1792` as separate cameras.
- Validate `1440x900`, `390x844` and iPhone SE `375x667`.
- Inspect every promoted image with `view_image` at original detail.
- Never print `FAL_API_KEY` or `FAL_KEY`.
- Use `uv`, Bun and Podman conventions; do not use `pip`, `npm`, `npx` or Docker.
- Keep review screenshots in `design/scene-01/review/`, never `/tmp`.
- Keep V8 as provenance, but production code must no longer import it.
- Current approval of volumetric art overrides older memory that rejected isometry.
- Confirmed execution lessons: raster art stays in `<img>`, viewports are authored separately, real browser screenshots are authoritative and accessible names stay unique.
- Confirmed generation lesson: use Canny for object count and road geometry, then style only with an object-free reference; a style reference containing trucks duplicates transport.
- Regional crops overlap by 20-30% and include road, buildings, snow, shadows and reflected light; never crop or paste a vehicle alone.
- The final whole-frame pass is low-strength harmonization only. It may unify light, weather and texture but must not relocate roads or vehicles.

### Task 1: Build The Distributed Town Blocking

**Files:**

- Create: `scripts/media/carrier_blockout.py`
- Create: `design/scene-01/assets/feedback-v9/blockout/README.md`
- Create: `design/scene-01/assets/feedback-v9/blockout/carrier-scene.blend`
- Create: `design/scene-01/assets/feedback-v9/blockout/desktop-{color,depth,canny}.png`
- Create: `design/scene-01/assets/feedback-v9/blockout/mobile-{color,depth,canny}.png`

**Interfaces:**

- Produces: `blender --background --python scripts/media/carrier_blockout.py -- --output-dir <dir>`.
- Produces named collections `Warehouse`, `OldCarrier`, `NearCarrier`, `CrewCarrier`, `ExpressCarrier` and `CueProps`.

- [ ] Run the command before implementation and confirm it fails because the script is absent.
- [ ] Replace the compact warehouse-yard geometry with a town measuring at least `48m x 38m`, 8-12 buildings, four intersections or branches and explicit lane dashes. Keep reusable helpers `add_road`, `add_truck`, `add_van`, `add_express_truck` and add a `TownDistrict` coordinate table so each object has one canonical location.
- [ ] Encode four independent spatial stories: old truck on the remote north-west service road beside inspection; near van on the east warehouse spur behind a barrier; crew truck on the south-west urban road with two visible adults; Express on the south-east arterial with an unobstructed forward lane.
- [ ] Assert in the script that each carrier collection has a distinct road id and that pairwise vehicle centres are at least `7.0m` apart. Fail rendering when the invariant is broken.
- [ ] Author fixed `CameraDesktop` and `CameraMobile` transforms separately. Desktop shows a broad town panorama; mobile redistributes districts vertically and is not a crop or camera rotation of desktop.
- [ ] Render material-color, normalized depth and edge passes at exact production dimensions and save the `.blend`.
- [ ] Validate dimensions with Pillow and inspect both color guides using `view_image`; reject any guide where three vehicles share one local road, a vehicle is clipped, opposing vehicles face each other, or the town reads as a warehouse yard.
- [ ] Record camera transforms, focal lengths, object coordinates and the reproduction command in the blockout README.
- [ ] Commit with `git commit -m "feat: block coherent carrier scene"`.

Verification:

```bash
blender --background --python scripts/media/carrier_blockout.py -- \
  --output-dir design/scene-01/assets/feedback-v9/blockout
uv run --with pillow python - <<'PY'
from pathlib import Path
from PIL import Image
root = Path("design/scene-01/assets/feedback-v9/blockout")
for prefix, size in (("desktop", (1536, 864)), ("mobile", (944, 1792))):
    for suffix in ("color", "depth", "canny"):
        assert Image.open(root / f"{prefix}-{suffix}.png").size == size
print("blockout guides valid")
PY
```

Expected: exit `0` and `blockout guides valid`.

### Task 2: Produce Regional Painterly Masters And Harmonize

**Files:**

- Modify: `scripts/media/carrier_art_pipeline.py`
- Create: `scripts/media/test_carrier_art_pipeline.py`
- Create: `design/scene-01/assets/feedback-v9/{prompts,candidates,regions,masks,assembled,production}/`
- Create: `design/scene-01/assets/feedback-v9/README.md`
- Modify: `design/scene-01/assets/feedback-v8/README.md`

**Interfaces:**

- Consumes Task 1 guides and V7 only as a style reference.
- Produces `structured-generate` with image, control, control type, strengths, explicit size, seed, output and metadata.
- Produces `extract-regions` from a JSON manifest and `assemble-regions` with feathered overlap masks.
- Produces only `carrier-desktop.{png,webp}` and `carrier-mobile.{png,webp}` as production art.

- [ ] Extract parser construction so tests can import it without credential setup.
- [ ] Add a failing parser test for `structured-generate` and run it with `uv run --with pytest --with fal-client --with pillow pytest scripts/media/test_carrier_art_pipeline.py -q`.
- [ ] Implement depth mode with `fal-ai/flux-control-lora-depth/image-to-image` and Canny mode with `fal-ai/flux-control-lora-canny`; always request one PNG and save credential-free metadata.
- [ ] Add a failing test for `load_region_manifest()` using `desktop-regions.json`. The manifest contains four named rectangles (`old`, `near`, `crew`, `express`) whose bounds stay inside `1536x864` and whose neighbouring rectangles overlap by at least 20% of the smaller rectangle's width or height.
- [ ] Implement `extract-regions --image --control --manifest --output-dir` so identical coordinates crop the color and Canny/depth guides. Save crop coordinates in each region's metadata.
- [ ] Generate at least three seeds per region. Each prompt describes exactly one primary vehicle story and treats partial neighbouring districts only as context. Prompts define one shared winter light and forbid text, logos, duplicates and isolated/cutout vehicles.
- [ ] Inspect every regional candidate with `view_image`; reject wrong vehicle construction, broken local roads, unreadable crew, unsafe old vehicle, weak Express semantics or lighting that cannot match adjacent regions.
- [ ] Implement `assemble-regions --base --manifest --region name=path --feather 96 --output`. Use Pillow masks with a 96px feather inside overlaps; preserve the base guide outside supplied regions. Add a synthetic test proving no fully transparent pixels and no hard seam at an overlap boundary.
- [ ] Apply an object-free V7 crop only as the style reference. Never supply a reference containing vehicles because it causes duplication.
- [ ] Run one low-strength whole-frame harmonization edit on each assembly. The prompt explicitly preserves exact road geometry, building positions, vehicle count and vehicle locations; it changes only shared light, snowfall, painterly texture and seam continuity.
- [ ] Run the label-free semantic test and record whether both rasters identify farthest, nearest-but-slow, two-driver and Express options, and whether a reviewer perceives four independent routes rather than one convoy.
- [ ] Encode WebP with ImageMagick quality `88`, validate dimensions and append the V8 rejection note without deleting historical seeds.
- [ ] Commit with `git commit -m "feat: render coherent carrier artwork"`.

Parser test core:

```python
def test_structured_generate_arguments():
    args = build_parser().parse_args([
        "structured-generate", "--image", "color.png",
        "--control", "depth.png", "--control-type", "depth",
        "--prompt-file", "prompt.txt", "--width", "1536",
        "--height", "864", "--seed", "26082601",
        "--output", "result.png",
    ])
    assert args.control_type == "depth"
    assert args.width == 1536
```

Region manifest core:

```json
{
  "size": [1536, 864],
  "regions": {
    "old": [0, 0, 720, 430],
    "near": [650, 0, 1536, 500],
    "crew": [0, 330, 850, 864],
    "express": [700, 330, 1536, 864]
  }
}
```

### Task 3: Replace V8 Layers With Semantic Hotspots

**Files:**

- Modify: `src/components/CityMap.tsx`
- Modify: `src/App.module.css`
- Modify: `tests/scene.spec.ts`
- Modify: `tests/layout.spec.ts`

**Interfaces:**

- Consumes the two V9 WebP masters.
- Produces one responsive `<picture>` and exactly four accessible buttons.
- Preserves `CityMapProps`, `CarrierId`, click behavior and outcome navigation.

- [ ] First change E2E expectations to require `feedback-v9`, four buttons, zero `vehicleSprite` nodes and zero `routeNetwork` nodes; run focused Playwright and confirm failure.
- [ ] Import only V9 desktop/mobile art in `CityMap`; remove sprite imports, `artwork`, route SVGs, trails and vehicle `<img>` elements.
- [ ] Keep unique accessible labels and compact optional HTML labels inside semantic hotspots.
- [ ] Remove truck movement, wheel/trail animation, SVG route drawing and sprite filters from CSS. Hover/focus may change label/outline only; truck pixels remain static.
- [ ] Position hit regions over painted trucks and assert each is inside the map, at least `44x44`, outside the mission panel and not materially overlapping another hotspot.
- [ ] Run unit and focused E2E suites and commit with `git commit -m "fix: make carrier choices one coherent scene"`.

E2E contract:

```ts
await expect(page.locator('[data-art-version="feedback-v9"]')).toBeVisible();
await expect(page.locator('[class*="vehicleSprite"]')).toHaveCount(0);
await expect(page.locator('[class*="routeNetwork"]')).toHaveCount(0);
await expect(
  page.locator('section[aria-label="Карта доступных перевозчиков"] button'),
).toHaveCount(4);
```

Verification:

```bash
bun run test
bunx playwright test tests/scene.spec.ts tests/layout.spec.ts
```

### Task 4: Visual QA And Release

**Files:**

- Modify: `design/scene-01/review/README.md`
- Update carrier screenshots in `design/scene-01/review/`.
- Modify V9 art or carrier UI only when a visible defect requires it.

**Interfaces:**

- Produces inspected desktop, standard mobile and iPhone SE evidence, a green build, pushed branch and verified live deployment.

- [ ] Run `bun run check`, `bun run test`, `bun run build`, `bun run test:e2e`, `git diff --check` and `sh scripts/package-static.sh`; all must exit `0`.
- [ ] Capture the carrier screen at `1440x900`, `390x844` and `375x667`, with normal UI and labels hidden for diagnostic review.
- [ ] Inspect every capture with `view_image`: no pasted look or regional seams; four visible/selectable vehicles on independent roads; two readable adults on iPhone SE; safe old truck; constrained near van; fastest-looking Express; no overlap, edge strips, scrolling or unreachable controls.
- [ ] Repair failed image semantics only through the Task 2 whole-frame workflow. Repair hotspot/panel geometry in React/CSS. Never compensate with extra copy or animation.
- [ ] Update the review README with filenames, viewports, label-free findings and final V9 paths; commit tracked review changes with `git commit -m "test: verify coherent carrier scene visually"`.
- [ ] Push `feedback/edik-2026-08-17`, wait for the matching GitHub workflow and inspect `https://energy-plus-quest.hypcat.net/` in desktop and iPhone SE emulation. Confirm `data-art-version="feedback-v9"` and visual parity with local screenshots.
