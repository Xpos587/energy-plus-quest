# Warehouse PPE — selected A, local v16 integration

## Current status and boundaries

After Michael delegated this choice («действуй на свою усмотрение в этот раз»), the coordinator selected **A**. It is now integrated locally as `inventory-master-v16{,-tall}.webp`, retaining the reviewed badge positions (3 beside the keeper, 4 left of the computer) and the red-gift `warehouse-results-v3` outcomes. B remains an unused proposal. The earlier “pending choice / runtime remains v15” status is superseded.

The coordinator visually accepted both actual-runtime sheets, all result frames and badge positions (request-scoped reply `f125db29-6e22-4497-a873-b871d0d8c74c`). The coordinator subsequently released the shared index after Scene 2 commit `aa68c14` and authorized this warehouse-only commit. **No push, deployment or media publication is authorized.** `media-artifacts.json` is unchanged (SHA-256 `cea11fb5caa1946c1fce65a627c6f8ffc5e402e66e5ddb026dd6c884324bcd33`). The new media are local, not yet hydratable from a fresh clone. Publish/verify the new media under a separately approved release step before pushing code that depends on them. Scene 4 clothing is outside this change.

The canonical eight-file byte-count/SHA-256 receipt is [`media-inventory.json`](media-inventory.json): two choice plates and six result plates. Binary media remain outside Git.

## Diagnosis and choice

Michael rejected the **v15 clothing**, not the UI form. Observed in those crops: flat orange shoulder blocks, little sewn construction or fabric volume, thigh blocks resembling shorts over blue leggings, and several narrow reflective rings. The actual keeper result has a navy zip placket, shaped orange chest panels, pockets, folds and broader tape. These are plausible reasons for the rejection, **not Michael's confirmed explanation**.

- **Selected A — orange yoke / navy lower jacket:** sewn insulated jacket, navy placket, orange upper chest/back, articulated sleeves, pockets and folds. Orange cargo trousers with navy knee/lower-leg panels and broader calf tape. Closest to the actual result keeper.
- **Unused B — orange torso / navy shoulder saddle:** orange front/back down to the waist, navy shoulders/sleeves, navy placket/hem and pronounced navy-flap chest pockets. A different panel layout, not a hue-only variation.
- Current reference: [`warehouse-results-v3/outcome-keeper.webp`](../../../public/scene-art/warehouse-results-v3/outcome-keeper.webp), selected by [`src/scenes/artwork.ts`](../../../src/scenes/artwork.ts). Written warehouse guidance: [`results-style.md`](../results-style.md) and [`results-v2/p-ppe.txt`](../results-v2/p-ppe.txt). Retain caps; no new helmet, vest, flag or logo.
- **Cross-scene correction:** current crane routing in [`crane/artwork.ts`](../../../src/scenes/crane/artwork.ts) and [`crane/cast.ts`](../../../src/scenes/crane/cast.ts) uses `barge-v5`. Inspected `barge-v5/wide/ivan-run1.webp` and `barge-v5/outcome-rush.webp` show navy/grey clothing, contrary to the older warehouse style document. Cross-scene uniform consistency is not established; `warehouse-restored-2026-10-11` is not a verified current other-scene reference.
- No official company PPE/brand manual was identified in the inspected sources. Colours follow warehouse artwork, not a certified corporate/safety specification.
- Preserve the current dark moustache and cap; do not restore the superseded grey/no-cap keeper description.

## Generation and reproducibility

- `cx/gpt-image-2.5` was checked with successful model metadata/capability queries. Two separate edit requests (A and B) returned image bytes successfully; no retries.
- Prompts: [`a-brief.txt`](a-brief.txt), [`b-brief.txt`](b-brief.txt). Inputs: a registered 5×2 atlas of the ten v15 people (five per format) and the actual result keeper as garment reference only. [`prepare-warehouse-ppe-variants.py`](../../../scripts/prepare-warehouse-ppe-variants.py) recreates those inputs.
- Requested PNG/high quality/2400×1440; **both actual outputs were 1619×971**. They were resampled for registration and reduced to native scene resolution. Do not claim the requested API resolution was returned.
- Local generated sources: `a-atlas.png` (SHA-256 `d1e2b85a553358f443563aa4f0e4cd3cfdf4224f3e6d0fe24b10a64e3b1168bb`), `b-atlas.png` (`727fe3fdae5c5be69619843ff6dff36804310b9431c3d5db32a8b678e4d885c8`). Neither is in the release manifest.
- [`compose-warehouse-ppe-variants.py`](../../../scripts/compose-warehouse-ppe-variants.py) translates/registers garment shapes, then transfers generated pixels through masks onto v15. This is **not another HSV recolour**. Protected head rectangles and hand/tool areas retain the original pixels; generated faces/background are not adopted. Assertions check unchanged pixels outside garment masks and in the protected head rectangles.
- A exports lossless v16 WebP at **1672×1170 / 1200×1750**. Decoded v16 pixels match the selected A PNGs exactly: zero changed pixels. B exports only local comparison images.
- The older R22 `cx/gpt-image-2` request remains completion-unknown after its disconnect. The two distinct R23 requests do not establish whether that older request was billed.

Recreate locally using existing source media, with no image API call:

```sh
uv run scripts/prepare-warehouse-ppe-variants.py
uv run scripts/compose-warehouse-ppe-variants.py a b
```

The retained [`finish-warehouse-v15.py`](../../../scripts/finish-warehouse-v15.py) is a preparation dependency (registered person bounds/masks), not the selected final clothing. [`finish-warehouse-gifts.py`](../../../scripts/finish-warehouse-gifts.py) creates the six red-gift results, including the same wrapped parcel on the keeper's formerly empty trolley. Its pre-encoding outside-mask assertion covers the five recolours, not the added keeper parcel or all pixels after lossy WebP encoding.

## Actual runtime review and checks

[`capture-warehouse-art-review.ts`](../../../scripts/capture-warehouse-art-review.ts) captured **14 actual runtime frames**, with **no request interception, DOM/image replacement or synthetic screenshots**: choice + six result variants at both **1440×900** and **390×844**. It asserts the v16 choice URLs, all six result-v3 URLs, four choice markers, and zero page/HTTP errors. Both choice frames and both full result sheets were visually inspected.

Latest local evidence (72-hour scratch retention applies, not release assets):

- [Desktop: choice and six results](../../../.tmp-work/r24-warehouse-a-runtime/actual-runtime-1440x900.jpg)
- [Phone: choice and six results](../../../.tmp-work/r24-warehouse-a-runtime/actual-runtime-390x844.jpg)
- Native frames: `.tmp-work/r24-warehouse-a-runtime/choice-{1440x900,390x844}.png` and `{entrance-boat,alphabet-boat,alphabet-camera,alphabet-socks,keeper-boat,wms-boat}-{1440x900,390x844}.png`.
- Browser receipt: `.tmp-work/r24-warehouse-a-runtime/browser.json`; exact decoded A check: `selected-a-pixel-check.json` in that directory.
- **82 unit tests / 9 files passed:** `bun run test src/scenes/inventory src/scenes/artwork.test.ts` (`vitest.log`). The new selected-A routing guard was first observed failing against v15, then passed against v16.
- **Project typecheck passed:** `bun run typecheck` runs `tsrs --noEmit` (`typecheck.log`); this is not a claim that unavailable `tsc` was run.
- The 72-case Chromium cohort initially had 70 passes and two stale keeper-clearance failures at 1440×900. The old check required the badge to be above the keeper, contradicting its reviewed position to his right. Browser rectangles and CSS confirmed an 8.077px horizontal gap between the visible disc and keeper bounds at that viewport (`keeper-rects.jsonl`). The test now checks either horizontal clearance or the existing vertical head clearance, without moving the pin or relaxing the original vertical threshold. **Final rerun: 72/72 passed** (`playwright-final.log`): perspective, general composition, alphabet, WMS framing, keeper clearance and intake visibility; desktop/mobile Chromium projects, with 320×568, 390×844, 844×390 and 1440×900 checks (plus intake at 1280×800).

For a local review server on port 4199:

```sh
INVENTORY_TEST_URL=http://127.0.0.1:4199 bun scripts/capture-warehouse-art-review.ts
```

`bun run clean:stale`, `bun run check:storage` and `git diff --check` passed after the final rerun. Storage check observed HEAD 27.9 MiB, local generated output 1580.5 MiB and Git 52.6 MiB.

The check is local Chromium coverage, not a deployed verification or a claim of exhaustive browser/device coverage. Tailoring details remain difficult to judge in the 390px overview; native close-ups are available.

## Earlier proposal review — historical evidence

R23 used Playwright image interception to compare v15/A/B without changing runtime routing. Those **proposal-only** captures must not be confused with the no-interception R24 evidence above. All four marker rectangles matched the baseline. Pixel checks showed zero changes outside garment masks and inside protected head rectangles for both formats/variants; that scoped check is not proof that every visual detail is perfect.

- [Clothing close-ups, v15 / A / B](../../../.tmp-work/r23-warehouse-ppe/ppe-detail-comparison.jpg)
- [Desktop proposal comparison](../../../.tmp-work/r23-warehouse-ppe/browser-comparison-1440x900.jpg)
- [Phone proposal comparison](../../../.tmp-work/r23-warehouse-ppe/browser-comparison-390x844.jpg)
- Checks: `.tmp-work/r23-warehouse-ppe/{a,b}-composite-check.json`, `comparison-check.json`, `browser-current.json`, `browser-a-b.json`.

An independent read-only `delegate` review (parent-model inheritance, run `df6aa37d-3d57-44fa-a835-c2e4db079e57`) preferred A and found no conspicuous compositing defect in the supplied proposal views. It did **not** approve production. A subsequent conservative head-preservation guard was followed by repeated captures and parent inspection.

## Skills applied

- `finding-skills`: assessed installed overlap; `imagegen` already covered controlled editing/provenance, so no external skill/code installation was needed.
- `imagegen`: explicit target/reference roles, capability verification, bounded one-request-per-variant execution, saved prompts/results, actual output inspection, no ambiguous POST retry.
- `reference-design-contract`: keep/change/unknown and evidence distinctions. No claim that a full design-system contract was created or that reading alone proved benefit.
- Focused read-only Explore located source constraints; its incorrect current-other-scene claim was checked against runtime routing and corrected above.
- `systematic-debugging`: confirmed the stale one-axis clearance assumption using rendered DOM bounds and the real pin CSS before changing the assertion.
