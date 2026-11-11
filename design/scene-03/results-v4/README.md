# R25 warehouse correction

## Scope

Keep the accepted A uniforms and choice artwork. Fix the six result illustrations' bent straight lines, seat the keeper's gift on the cart, remove red from the WMS neighbour carton, and point choice markers 3/4 at the keeper/computer. No dialogue, scores, marker CSS, release manifest, upload or deployment changes.

## Source and composition

`uv run scripts/finish-warehouse-results-v4.py` produces the six lossless WebPs in `public/scene-art/warehouse-results-v4/` and runs the image assertions. Its current inputs are:

- Four original pre-registration masters: `hf-alphabet-camera.png`, `hf-entrance.png`, `hf-keeper.png`, `hf-wms.png` in this directory. These are necessary media sources, not disposable generation intermediates.
- Fixed SIFT/RANSAC transforms in [registration.json](registration.json). Only resize and projective homography are used. A homography preserves straight lines; the former `design/scene-03/blender-v1/align.py` also applied nonlinear Farneback optical flow.
- Each corresponding accepted `warehouse-results-v3` result supplies its own person pixels, including the entrance worker's already-removed flag. Reviewed silhouette envelopes, not rectangular background patches, protect the people. The saved lossless output is decoded and compared against these protected pixels.
- The existing gift finisher supplies recolouring/ribbon/bow helpers. The WMS foreground carton explicitly occludes the gift side. The keeper gift is reprojected onto a footprint inside the platform with a local contact shadow, rather than pasted above an unrelated shadow.

Four masters cover six results: the alphabet camera composition supplies all three alphabet backgrounds; each variant retains its existing printed plaque and own accepted person pixels. The v3 trio audit in [receipt.json](receipt.json) bounds the isolated WebP differences outside the plaque. An additional observed check of the original lossless `gen3/fin-alphabet-{boat,camera,socks}.png` intermediates found **zero** differing pixels outside `(1025,205)–(1138,285)`. There is no authored difference in cargo, gift contents/label or cart load. The original intermediate paths were under `.tmp-work/s3style/gen3/`; they are provenance evidence, not rebuild inputs.

Visual comparison of all four raw/current compositions shows straight shelves, window frames and platforms before nonlinear registration and bent counterparts in v3. This supports the registration step as the cause; an earlier hypothesis blaming the restyle alone was based on choice-art geometry notes and is superseded for these result images.

## Choice markers

Coordinates are native-image anchors; the existing CSS triangle ends at the anchor (within one screen pixel). Actual 390×844 and 1440×900 close-ups were checked.

| Target | Wide 1672×1170 | Tall 1200×1750 |
|---|---:|---:|
| 3 — keeper cap | 1345,582 | 930,909 |
| 4 — monitor frame | 1290,692 | 868,1055 |

`src/scenes/inventory/callouts.test.tsx` failed on the former floor anchors before the coordinate change and passes with target-bound assertions. The separate ring/CSS lane is not part of this change.

## Review evidence

Current local evidence: `.tmp-work/r25-warehouse-lines/`.

- `before/` and `after/`: actual-runtime screenshots plus `browser.json`; 7 frames per viewport (choice and all six results), no request interception, no DOM/image replacement, no page/HTTP errors.
- `runtime/`: side-by-side before/after frames, both viewports.
- `geometry-{result}.jpg`: all six composition/cart comparisons.
- `uniform-{result}.jpg`: all six accepted-person comparisons.
- `keeper-contact.jpg`, `wms-neighbour.jpg`: W2/W3 close-ups.
- `wms-corner-fixed.png`, `wms-box-fixed.png`, `wms-corner-runtime-{390x844,1440x900}.jpg`: final WMS correction against the reviewed v4 candidate. The old foreground-carton mask exposed the gift's own kraft side below its red top, creating a false overhang. The corrected mask follows the actual carton edge; the light vertical strip remains the side ribbon. Three visible-side colour probes fail on the old candidate and pass on the corrected output. The other five approved output SHA-256s are unchanged.
- `pins-detail-{390x844,1440x900}.png`: actual-runtime marker details.

These are review renders, not shipped sources. Input/output hashes, protected-pixel counts, variant differences and invariant checks are recorded in [receipt.json](receipt.json).

## Validation and boundaries

- Generator: all six decoded outputs have zero changes inside their protected-person envelopes; WMS neighbour pixels equal the straight source, and the visible gift side stays red up to the carton edge; all keeper footprint corners lie inside the deck.
- Vitest: full suite passed — 393 tests in 73 files (including the 82 inventory/artwork tests).
- Typecheck: passed.
- Playwright: 12 cases passed, covering 320×568, 390×844, 844×390 and 1440×900; all choices/parcels, keeper clearance, WMS framing and result paging.
- Choice v16 wide/tall and `media-artifacts.json` SHA-256 checks: unchanged.
- Before/after screenshots may also show the independently edited global choice-ring CSS; this lane changes coordinates only.

Skills: read `finding-skills`, `imagegen` and its gateway/prompting guidance; searched installed candidates (Blender/ComfyUI/Higgsfield). Existing source reconstruction solved this 2D registration defect, so no new skill installation, model generation or paid API request was needed. Reading skills is not claimed as measured improvement.

This is local source/media work. New v4 media are not in the release manifest; publishing/deploying is explicitly deferred to the coordinator's separate authorized release flow.
