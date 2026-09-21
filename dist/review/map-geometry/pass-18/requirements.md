# Pass 18: scenario-first continuity audit

Candidate review only. No live game integration, shared WorldArt changes, other-scene edits or motion changes. One reference-guided image generation is used only for the Express highway result. Passes 14-17 are immutable.

## Primary scenario corpus, before meetings

All nine available DOCX files under `materials` were extracted directly from `word/document.xml`. Current text includes `w:ins` and excludes `w:del`; deleted text is retained separately as `[DELETED]` in the audit extracts, not treated as instruction. Extracts and all embedded images are in the production pass-18 source directory. Available earlier scene-1 primary: 23 July draft; latest: 17 September scenario attached 18 September. No other earlier scenario DOCX was found in the repository. Project passport, Outro, transport 0109, cranes 0209, WMS 1908 and Compact 1908 were also read; later-scene truck references do not prescribe the color of scene-1 manual trucks.

**Latest source:** `materials/meeting/2026-09-18/attachments/Сценарий_игры_Доставляем_радость_правки_1709.docx`, Scene 1, Visualization:

- “На экране общим планом изображен город, по которому передвигаются 4 грузовика, пересекаясь на перекрестках.”
- “№1 и №4 – в разных частях экрана, потрепанные, заметно старые, дымят. Один из них движется быстрее, другой помедленнее.”
- “№2 – фура, которая очень медленно передвигается рядом с офисом.”
- “№3 – «сияющая» фура с двумя водителями, которые движется по «широкому периметру квартала»”
- “После выбора нужная машина «подсвечивается» (опционально) и появляется поп-ап с визуализацией, текстом и результатом ответа (см. справа)”
- “В случае нажатия брендированной кнопки «Автоподбор» карта анимируется и прямо у дверей магическим образом появляется новенькая фура с 2 водителями.”

**Outcome illustration instructions in that source:**

- “№1 или №4”; “Иллюстрация: сотрудник ДПС проверяет документы незадачливого водителя.” Shared semantic outcome, not an instruction to change the selected vehicle's identity.
- №2: “Иллюстрация: Ленивый водитель перекусывает в кафе, забросив ноги на стол.”
- №3: “Иллюстрация: беспилотный автомобиль едет по шоссе в колонне.” The adjacent result says “Благодаря посменной работе водителей”. This is an existing text/illustration inconsistency, not permission to remove the required two drivers. This pass does not reinterpret autonomy or regenerate the scene.
- Automatic: “Вы использовали платформу организации грузоперевозок Express и всего за два часа организовали доставку, выбрав перевозчика с высоким рейтингом, двумя водителями в фуре и по выгодной цене.”
- Automatic illustration: “Автомобиль с логотипом Express мчит по шоссе.”

**Earlier source:** `materials/project/Драфт_первой_сцены_на_просчет_2307.docx`, Screen 2. It says “передвигаются 6 грузовиков”, superseded by four in September, but already separates “№1 или №4”, “№3 – грузовик с 2 водителями”, and “Кнопка «Автоподбор»”. It contains the same post-selection Express-logo illustration instruction. The project passport calls this stage “Поиск фуры-перевозчика из Москвы (цифровое решение Express)”. Neither assigns an orange cab.

**Embedded references inspected:** July has four media entries, two repeated toy-city/Mondrian references. September has 39 media entries (including repeated images); its Scene 1 references are likewise the toy street grid and Mondrian painting, captioned “Условный предметный референс” and “Абстрактное представление для вдохновения”. They are not numbered truck-color specifications. The Compact diagram shows a gray-blue cab and colored cargo blocks; its explicit color clause is “Красным цветом обозначены готовые крепления.” That clause is about cargo restraints, not orange cabs. Other embedded images show warehouses, cranes, helicopter, all-terrain vehicles, lodging and the recipient; orange on a helicopter or snow vehicle does not assign orange to truck №4. `originals-contact.jpg` in the source directory records these references together with current game art.

**Color finding (medium-high confidence within this available corpus): no orange-cab requirement found; no orange-cab prohibition found.** This is an absence finding, not a quotation banning orange and not a claim to have reviewed missing sources. Orange in the historical №4 outcome is existing artwork, not a requirement or Express brand logic. The revised candidate keeps approved pass17 №4 completely unchanged and recolors its outcome cab to muted gray-blue. Both old vehicles now share a neutral low-cab family; no unique orange choice accent is reintroduced.

**Express placement (high confidence, checked against the DOCX table context):** the Visualization column describes the immediate map reaction: a new two-driver truck appears at the doors after autopick. Separately, the Text column contains the automatic-choice “Результат”, its narrative, then “Иллюстрация: Автомобиль с логотипом Express мчит по шоссе.” The highway instruction therefore accompanies the automatic result illustration; it is not explicitly labeled a separate cutscene followed by an approved parked final card. The document does not specify such a two-stage card sequence. Current runtime goes directly to Outcome. The revised candidate replaces the parked illustration with a highway still: the same blue high-cab/light-trailer family, Express lettering and both drivers seated inside. This addresses the result illustration without introducing a cutscene or claiming animation.

**Express finding (high confidence):** exactly four initial manual vehicles; platform autopick is a separate action; a newly selected Express-branded result truck can indeed appear after that action. “Express is not a separate car” must not be expanded into a ban on its explicitly described post-selection truck. No fifth manual truck is added; manual №3 is not silently redirected to Express.

## Meetings and feedback, second

- `materials/feedback/2026-09-03/source.docx` and matching `source.txt`, Map block: “Express - не отдельная машина.” Its Results block says “Иллюстрация ок, только разрешение улучшить.” General block: “Фура (кроме случая, где выбрали плохую) должна быть современной.” The author is not named in the document. Read in context with the latest scenario, the Express clause addresses the initial choice map, not a prohibition on automatic-result branding.
- `materials/meeting/2026-08-24/transcript.txt`, lines 91-95: “вахтовик Арсений написать черными?” / “чтобы вот этого не было оранжевого”. This concerns the Arseniy label, not a cab. Lines 225-229: “выбираем между 4 машинами” and “максимально наглядная картинка”. Earlier conflation of Express with four options in that meeting is superseded by the scenario and written feedback.
- `materials/meeting/2026-09-07/transcript.txt`, 09:40: “Нет, они сами машины потрёпанные”; 10:18: “Сияющая фура с двумя водителями, которая движется по широкому периметру квартала.” No truck-color prescription.
- `materials/meeting/2026-09-16/transcript.txt`, 24:00: “Чтобы было понятно, что старая машина – это старая машина. Что два водителя там едут, что их двое.” At 30:02: “Чтобы видно было, что машина ездит медленно, а не написано текстом «эта машина медленная».” Static candidate art cannot validate speed.
- `materials/meeting/2026-09-18/client-messages.json`, message 239991, 10:39:12 UTC, sender **Teo Durnev**: “старая машина должна выглядеть «потертой ласточкой», а не «грязным постапокалипсисом»”. Message 239990 asks to soften contrast and align the palette with the illustration brandbook, not to assign orange to a specific vehicle. Sender name is not relabeled as Fedya.

Relevant color/vehicle/Express passages were also searched in the available 30 July, 12 August and 2 September transcripts. No additional orange-cab instruction was found. **The 4 September primary meeting transcript is absent from the available meeting materials. Secondary reviews are not presented as newly verified primary quotes. No diarized personal claim is attributed to Fedya.**

## Actual runtime identity, not filenames guessed

Parent semantic search returned no results; scoped code reads then followed the actual flow.

`src/App.tsx` CarrierScreen buttons pass `old`, `near`, `crew`, `old4`, `express`; `src/components/MapNumbers.tsx` indexes `[old, near, crew, old4]`. `src/game/gameReducer.ts` CHOOSE_CARRIER retains that exact id and sets `step: outcome` directly. There is no separate scene-1 cutscene state in this reducer. `src/App.tsx` Outcome reads `outcomeArtwork[carrier.id][format]` for both responsive assets. `src/game/artwork.ts` maps **separate old and old4 files** for desktop/mobile. `src/game/content.ts` shares the old-carrier text/scores with old4, not the illustration mapping. No status or score-based alternate truck artwork is selected. Express is its own id; manual crew does not use it.

`src/components/CityMap.tsx` uses `design/scene-01/assets/current/map/carrier-{desktop,mobile}.webp` posters and corresponding MP4 loops, not pass17. Live video is selected by surface aspect ratio <=1.607143; posters are used outside live mode and on motion failures/blocks. Pass18 therefore fixes the requested **approved-map review candidate**, not production video/poster continuity. Original live map and all ten outcome assets were visually inspected, with full-frame contact sheets and truck closeups retained in the source directory.

## Vehicle passport / candidate mapping

| Manual choice | Approved map 17 -> candidate 18 cab | Trailer / model / condition | Crew, number | Current result -> candidate result | Identity confidence |
|---|---|---|---|---|---|
| 1 / old | Blue -> slate gray-blue | Light neutral box, low angular cabover, worn + exhaust retained | One-driver option; roof 1 retained | Current gray high-roof truck at DPS -> gray recolor of existing old4 low-cab DPS composition | High family/color continuity; not an exact manufacturer/model claim |
| 2 / near | Gray-blue -> blue | Light box, modern rounded high cab | One driver; roof 2 retained | Existing blue truck behind cafe driver, both formats retained | High family/color; cool lighting makes result trailer appear blue-white |
| 3 / crew | Blue unchanged | Cream box, modern high cab, good condition | Two faces under windshield unchanged; roof 3 retained | Existing blue modern truck with two drivers outside retained | High family/color/crew; parked result is not proof of driving |
| 4 / old4 | Muted gray-blue unchanged from pass17 | Light gray box, low angular old cabover, wear + exhaust retained | One driver; roof 4 retained | Historical orange low-cab DPS artwork -> neutral gray-blue cab, identical candidate family to №1 | High family/color; map uses rectangular grille, result has horizontal slots |
| Automatic / express | No initial numbered vehicle | Separate new blue high-cab result truck, cream trailer | Two drivers; no manual number | Reference-guided highway still with blue cab, cream trailer, Express wordmark and both drivers inside; mobile is an exact crop of the same artwork | Action identity high; mark is review typography, not an approved supplied corporate logo |

Numbers are selection locators on the map; this review does not invent registration numbers or paint labels over result drivers. The two old choices share scenario semantics with neutral gray-blue low-cab artwork for both. Existing compositions are reused; no new unrelated vehicle family is generated.

## Scope and remaining limits

Only pass18 files are written in the repository. Map edit changes only cab pigment in explicit masks: roofs, road markings, buildings, crew №3, all trailers and numbers are preserved. Original pass17 girl sprite and both placements are reused without substituting the recipient Alva. Outcome №1 reuses the already-authored №4 DPS composition, so it is intentionally not a pixel-preserving edit of old-desktop. The Express result alone is newly generated using the preceding Express candidate as the visual reference. The entire revised map and manual choices №2/№3 remain byte-identical; №1/№4 subsequently receive a local cab-edge pigment cleanup, without composition changes.

Existing result illustrations are not literal fulfillment of every scenario visualization: crew is parked, not in a highway convoy; old outcome trailer wear remains pronounced. Express now depicts highway travel in a still illustration, not an animated journey. These are disclosed existing composition limits, not asserted fixes. Static images cannot prove speed or an animated arrival. Exact model-sheet identity across perspective is not claimed; this candidate establishes recognizable low/high-cab families, cab color, trailer and crew continuity without whole-city regeneration. Human art acceptance and any later live integration remain separate.

### Additional visual check and reproducibility

The four embedded images in the 3 September feedback DOCX were also inspected: profile, recipient, gift and result screenshots. The result reference shows a dark-blue box truck at a checkpoint; orange occurs on clothing and a gift. Its caption approves the illustration while asking for better resolution, not orange cab paint. This supports a low-cab old-truck family but does not establish a mandatory cab color.

Source root: `/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-18`. `build.py` creates the localized candidate from immutable pass17 and current outcomes. `docx-0.txt` through `docx-8.txt` retain file provenance and tracked deletions. `originals-contact.jpg`, `outcomes-desktop-original.jpg`, `outcomes-mobile-original.jpg`, and `feedback-embedded.jpg` record inspected originals. `candidate/` mirrors the final public review.

Runnable checks from repository root: `python public/review/map-geometry/pass-18/verify.py`; with the existing Vite server at port 4173, `node public/review/map-geometry/pass-18/validate.mjs`. Open the explicit `/review/map-geometry/pass-18/index.html` path: Vite serves the application fallback for the directory-only URL.


### Express highway revision

Checked available `materials/brand` guides, `public/brand` inventory, and Express/Logotech/logo filenames under materials, public and design: no standalone supplied Express logo asset was found. The legible blue Express wordmark is explicitly candidate typography, not represented as an approved corporate logo. The reference-guided still retains the prior blue high cab, light trailer, two blue-shirted crew members (one capped), restrained ink outlines and paper texture. Both crew are seated behind the windshield; there are no people standing outside, warehouse or parking bays. Desktop uses the complete 2752 x 1536 generated frame; mobile is its centered 2057 x 1536 crop, not an independently generated truck.

Source `express-highway/` contains `prompt.txt`, `job.json`, `generated.png` and pre-revision preserved-asset hashes. Model requested through the documented CLI as `nano_banana_2` (returned job type Nano Banana Pro); one completed image job. Only this outcome is generated, never the map or other scenes. `express-highway-validation.json` records 13 byte-identical preserved assets after the separately checked old-cab edge cleanup and the exact mobile crop check.


### Old-cab edge cleanup

Expanded the local paint mask around the roof cap, window pillar, rear cab panel below the extended arm, and wheel-arch triangle in both old/old4 desktop/mobile results. Both old choices remain identical within each format. `cab-edge-closeups.png` shows inspected enlarged edges. Skin, amber indicator lights, windshield scenery and exterior background samples are asserted unchanged against the preceding candidate; Express highway assets, map, near and crew are hash-protected. Source `cab-edge/check.py` is the runnable focused check; `cab-edge-validation.json` records the result. No new generation or live integration in this cleanup.
