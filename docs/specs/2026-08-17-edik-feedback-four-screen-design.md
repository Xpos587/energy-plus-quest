# Four-Screen Client Feedback Revision

## Status

Reopened on 2026-08-20 after Michael rejected the first implementation as visually inconsistent with Edik's feedback. The interaction flow remains approved. Michael approved the V4 media rebuild on 2026-08-20: preserve the illustrated carrier scene instead of returning to a top-down 2D map, make distance from the warehouse functionally legible, remove the depressive tone, and regenerate the complete illustrative media system from mobile-first masters.

## Sources Of Truth

1. `materials/feedback/2026-08-17/source.pdf` — latest consolidated client feedback.
2. `materials/project/Драфт_первой_сцены_на_просчет_2307.docx` — client-authored scene copy and outcome descriptions.
3. `materials/project/Согласованная_версия_паспорта_проекта.docx` — product purpose, audience, mechanics, and platform constraints.
4. `DESIGN.md` — current Energy+ brand contract.

If these sources disagree, the feedback PDF wins for presentation and interaction, while the scene draft remains the source for factual story copy and score values.

## Intent

**Why:** The current prototype reads as a strict B2B decision test. The client needs a warm consumer game in which a simple choice produces an interesting human consequence.

**Human outcome:** A player should understand the mission immediately, make an intuitive choice without decoding a dashboard, and want to see what happened to the recipient and gift.

**Experience invariants:**

- One clear action per screen.
- One illustrated logistics world remains the shared setting, but it never competes with selectable vehicles.
- Choices persist visually so the player does not have to re-read a manifest.
- Every carrier choice leads directly to a human, illustrated consequence.
- Express is explained natively through its own outcome, not through a sales comparison screen.

**Betrayal condition:** A technically polished revision still fails if it feels like a corporate assessment, repeats the player's selections as a report, or explains products before showing a story consequence.

## Delivery Scope

The next client-review package contains four representative screen families, as requested in the feedback:

1. Start and onboarding.
2. Character or gift selection.
3. Carrier map.
4. One illustrated result.

The implementation must keep the prototype playable, but visual review artifacts focus only on these four families. Subscreens that are not necessary for this approval round must not receive speculative polish.

## Revised Flow

The playable flow becomes:

`intro -> profile -> recipient -> parcel -> carrier -> outcome`

The following states are removed:

- `briefing`: it repeats the selected profile, recipient, gift, and route without adding a decision.
- `express`: the comparison/self-check turns the game into a business assessment and repeats information already visible in the carrier choices.
- `complete`: its useful transition content moves into the outcome so the scene ends on the illustrated consequence.

Back navigation is available from every state after the intro. Returning from `outcome` to `carrier` clears the carrier and score result, while retaining profile, recipient, and parcel choices.

## Screen Contracts

### 1. Start And Onboarding

- The screen explicitly says this is the start of the game, not merely the first route segment.
- The map is visible as the game world, but softened behind a readable onboarding panel.
- The title `Доставляем радость` is separate from the company identity block.
- The body is based on the client draft:

  > У логистов есть профессиональное правило: не бывает неважных грузов. Для кого-то это многотонная турбина, а для кого-то — одна маленькая коробка, одна большая радость.

  > Сегодня вам предстоит провести такой груз на Крайний Север — быстро, легко и с любовью к людям.

- Remove `4 решения · 3 показателя · 1 маршрут` and other sales-deck language.
- The primary action is `Начать игру`.
- The GPN-S identity must use an official supplied or official public asset. Do not redraw or synthesize a corporate logo. Until an official file is available, reserve the correct logo area and use a neutral text label rather than a fake mark.

### 2. Selection

- Profile, recipient, and parcel remain sequential decisions because they personalize later copy.
- The shared selection component uses direct client language:
  - `Кто отправится в путь?`
  - `Выберите получателя`
  - `Что будет в посылке?`
- Remove speculative explanations such as `Роль задаст тон финалу`, `сравню решение с цифровыми инструментами`, and invented recipient backstories.
- Cards use only facts present in the client draft. If the source provides only a name or category, the card does not invent a biography to fill empty space; meaning comes primarily from the illustration.
- Profile choices use two complete character posters rather than a small image beside a mostly empty text area. The whole card is the answer control, with the character as the visual focus and the role label integrated into the lower portion.
- The professional is a stern, experienced man around 35-45 years old, visibly older and more capable than the student. He wears the current blue-and-orange PPE shown on page 3 of the feedback PDF, stands confidently, and does not carry an office clipboard or read as a press-service employee.
- Choice artwork uses a shared safe-frame contract: the complete identifying silhouette remains visible on desktop and mobile with breathing room on every edge.
- The reindeer, practical workboat, and knitted socks must be reframed or regenerated if CSS containment alone cannot preserve their complete silhouettes.
- The boat reads as a small practical boat, not a liner.
- A quiet `Назад` action is always present.

### 3. Carrier Map

- The task leads with the decision: `Выберите транспорт для подарка`.
- The task copy is adapted from the client draft: `Прежде всего, нам нужно найти лучший транспорт для перевозки подарка. Выберите машину, которая лучше всего справится с задачей.`
- Vehicles themselves are the only primary answer controls. Locator-pin icons, duplicate bottom cards, card arrows, and any second set of carrier choices are removed.
- The existing technical-plan map and manually modified vehicle cutouts are replaced rather than polished further.
- Do not return to a top-down 2D city map. The carrier board is a welcoming editorial logistics illustration containing the warehouse, four vehicles, and their route relationships in one coherent scene.
- Generate a mobile-first master in which every required vehicle, the warehouse, and the complete choice logic fit inside the central safe area. Produce desktop by model outpainting to the left and right; do not generate an unrelated desktop composition.
- The four visible vehicles stay inside the preserved mobile master area. Desktop expansion adds atmosphere, route continuation, and supporting infrastructure, never a fifth vehicle or a second warehouse.
- Use invisible accessible HTML hotspots over the vehicles. Do not draw drivers, smoke, labels, logos, or vehicle wear manually in ImageMagick, CSS, SVG, or canvas.
- The map contains no decorative traffic. Every visible vehicle is an answer control.
- The scene is bright, energetic, and humane: clear northern daylight, clean snow, saturated Energy+ orange and cobalt, warm practical details, maintained vehicles, and no ruin, grime, danger, or bleak isolation.
- Distance is part of the decision, not decoration. The nearest vehicle sits on a short route beside the warehouse; the older vehicle is visibly farther away on a longer route; the two-driver crew reads as capable of covering a broad route; Express reads as the service that resolves the whole route efficiently. Route continuity must be understandable before reading labels.
- The mission panel is compact and leaves most of the canvas to the playable map. It must not cover a vehicle or become the largest object on the screen.
- Vehicles are distinguishable from the generated artwork without reading text:
  - old trucks visibly worn and smoking;
  - the nearest truck moves slowly near the logistics centre;
  - the two-driver truck reads as newer and more capable;
  - Express is an active branded option without advertising copy.
- Vehicle movement follows the paths described in the draft. Motion must explain the choice and stop under `prefers-reduced-motion`.
- Each vehicle has a restrained route number and one short factual label visually attached to its route, not a separate white card floating under the vehicle. Hover, focus, or tap may reveal one factual sentence, but no persistent legend duplicates all four choices.
- The current profile, recipient, and gift persist as compact illustrated tokens in the header. Geography and score widgets are secondary.
- Express copy is limited to `Автоподбор Express`; its benefit is revealed after selection.
- Mobile uses the untouched central master composition. Desktop uses the same pixels plus model-generated side expansion. CSS may crop the expanded outer atmosphere, but it must never crop a required vehicle, warehouse, or route cue.

### 4. Illustrated Outcome

- The outcome opens immediately after selecting a vehicle. There is no comparison or confirmation step.
- The primary content is a scene illustration showing what happened, not a table of carrier attributes. Every carrier branch receives a distinct narrative backdrop so no result falls back to a vehicle cutout on a generic panel.
- Copy is adapted from the client draft and interpolates the selected recipient and parcel.
- Scores remain exact: Energy, Empathy, and Efficiency values do not change from `src/game/content.ts`.
- The selected carrier's reason and schedule shift are condensed into one consequence line. The four-column condition/crew/cost table is removed.
- The selected recipient and gift appear as illustrated story tokens connected to the scene, while the chosen player character remains visible in the persistent header context.
- The result uses a large art field and a compact editorial story caption. The current white report-card composition is removed completely.
- The caption contains only: a short story kicker, a two-line consequence title, at most two short sentences of human outcome copy, one strong delivery-time stamp, and a compact score-delta row. Nested separators, report-style metric blocks, repeated selection labels, and explanatory filler are removed.
- Recipient and gift tokens may remain as a small visual equation only when they support recognition without crowding the caption.
- Desktop places the caption in the calm area reserved by the illustration. Mobile uses a compact bottom story sheet that preserves the focal action and keeps all actions inside the viewport.
- The result must read first as a story illustration, second as a human consequence, and only third as a score update.
- Actions:
  - `Назад к машинам` returns to `carrier` and clears the carrier result.
  - `Дальше` leads visually toward `Теперь нам нужно погрузить подарок...`; because scene 2 is not implemented, the control is clearly marked `Скоро` rather than pretending the route continues.
  - `Начать заново` resets the scene.
- Do not mention Compact before the transition line and do not explain its mechanics in advance.

## Content Rules

- Use the client's draft as the source for story statements and outcomes.
- Shorten only for screen fit; do not introduce new claims.
- Use `подарок` or the selected parcel name instead of ambiguous slogans such as `Кому доставим радость?`.
- Product benefits appear as consequences of choices, not as promotional claims.
- Keep correct Russian typography: `ё`, em dashes, non-breaking units where relevant, and natural interpolation of recipient/parcel names.

## Visual Direction

- Rebuild the illustrative system with `fal-ai/flux-2-pro`; use `fal-ai/flux-2-pro/outpaint` for desktop expansion. The shared direction is expressive flat editorial game art, dry-brush gouache texture, confident simplified contours, vivid Energy+ orange, cobalt blue, warm white, pale sky blue, clear daylight, and human warmth.
- Use page 3 of the feedback PDF as the authoritative PPE reference for the professional character.
- Increase human detail in people, vehicles, and result scenes rather than adding decorative UI.
- Use generated or edited raster media for characters, vehicles, and outcomes; do not recreate key artwork with CSS or improvised SVG.
- Generate outcome backdrops as complete compositions with consistent lighting, perspective, texture, and palette. Do not assemble the hero art from unrelated cutouts, circles, or infographic connectors.
- Generate the mobile carrier master first, inspect it at original detail, then outpaint it horizontally. The original mobile region must remain unchanged in the desktop file.
- No hand-drawn vehicle modifications are allowed. Mechanical post-processing may only crop, resize, convert formats, and apply masks without changing illustrated content.
- Regenerate all illustrative raster media: two role posters, three recipients, three gifts, the carrier master plus its desktop expansion, and four outcome scenes. Preserve official logos, fonts, and functional UI icons.
- Every generation must be inspected with `view_image` before integration. Reject cropped subjects, extra people or vehicles, fake text/logos, inconsistent perspective, dark grading, accident imagery, and any asset that feels bleak or childish.
- Desktop and mobile must be inspected at `1440x900` and `390x844`.
- Official brand assets are never fabricated. Verdana/available licensed proxy fonts remain the documented fallback until licensed Normalidad files arrive.

## State And Data Changes

- Remove `briefing`, `express`, and `complete` from `GameStep`.
- Remove `OPEN_CARRIER_MAP`, `SHOW_EXPRESS`, and `COMPLETE_SCENE` from `GameAction`.
- Add a back action that maps the current state to its previous valid state.
- Add a result reset action or reuse `RESET` for `Начать заново`.
- Preserve `CarrierChoice.score` values exactly.
- Add outcome illustration metadata to `CarrierChoice` only if the code needs per-carrier assets; do not store presentation-only strings in the reducer.

## Acceptance Criteria

- The full flow reaches an illustrated outcome without visiting briefing, Express comparison, or completion-summary screens.
- A player can go back from profile, recipient, parcel, carrier, and outcome.
- Returning from outcome to carrier removes the previous score and carrier selection but preserves personalization choices.
- The intro contains the client-authored logistics rule and no corporate KPI slogan.
- No visible copy contains the rejected phrases documented in the feedback PDF.
- Vehicles are clickable directly on both desktop and mobile.
- The DOM contains exactly four carrier answer buttons on the carrier screen; there is no carrier dock or duplicate card grid.
- Each vehicle remains legible at a glance and exposes its factual distinction through art plus one short label.
- The carrier illustration contains exactly four vehicles and one warehouse; no vehicle appears to use a different camera, light source, contour treatment, or texture.
- Without opening explanatory cards, a reviewer can identify the short route beside the warehouse and the longer route farther from it.
- The two-driver option contains two naturally integrated adult drivers generated as part of the vehicle artwork; no manually drawn heads or bodies remain.
- Desktop is an outpainted extension of the mobile master, not an independent regeneration; both remain scroll-free.
- Express remains visible as a carrier choice and retains score `{-1, +5, +5}`.
- All four carrier results use distinct full-scene raster artwork, client-authored consequence copy, and no attribute table.
- The outcome contains no report-style white card. The story caption remains subordinate to the illustration and contains no more than one timing treatment and one score-delta treatment.
- The professional is a stern adult man in the feedback-PDF PPE and is visibly distinct in age and occupation from the student.
- No generated scene communicates neglect, poverty, breakdown, danger, or desolation. Negative outcomes remain constructive and human rather than depressive.
- The reindeer, boat, socks, and every other choice subject remain fully visible inside their media frames at both review viewports.
- At `390x844`, the carrier and outcome screens remain scroll-free and all controls stay inside the viewport.
- The four review artifacts are regenerated for desktop and mobile after animations settle.
- `bun run check`, `bun run test`, `bun run build`, and `bun run test:e2e` pass.
- Static packaging still works from a nested URL with no external runtime dependency.

## Known External Dependency

The repository does not currently contain an official GPN-S logo. Implementation may reserve its placement, but final press-service approval requires an official asset from the client or an authoritative public source. This dependency must not be solved by drawing a lookalike.

## V5 Visual-Legibility Amendment — 2026-08-20

Michael approved a focused visual correction after reviewing the complete V4
desktop and mobile flow.

- Energy, Empathy, and Efficiency use new generated pictograms with a single
  recognizable metaphor per metric. The pictogram is visually dominant and the
  Russian label remains visible at every supported viewport.
- Profile cards use edge-to-edge media without an inset cream frame. `Вы —` is
  a real role label, both role names share one type scale, and a reserved action
  column prevents either title from touching the arrow.
- The professional is an approachable, confident adult specialist in the
  approved blue-and-orange PPE. He may look focused, but must not look angry,
  gloomy, exhausted, or hostile.
- Recipient and parcel cards prioritize recognition over preserving empty
  scenery. People, the reindeer, and gifts are cropped substantially closer;
  the identifying subject must remain complete enough to recognize instantly.
- Carrier labels are spatially attached to their vehicles. The Express label
  sits beside the orange truck, while the two-driver badge is attached to the
  blue crew truck rather than floating over the warehouse.
- The large orange-and-cobalt shapes painted on the lower mobile road are
  removed. The road continues with ordinary lane markings and snowbanks.
- `Назад к машинам` and `Начать заново` are visibly interactive secondary
  buttons with a filled or translucent surface, border, hover, focus, and active
  states.
- The old/far-route outcome is replaced or tightly edited until every person is
  anatomically coherent and clearly outside the vehicle body. No person may
  merge with the door, cab, seat, or window.

### V5 Acceptance Criteria

- Score pictograms are at least `28px` on mobile and `30px` on desktop, and all
  three labels remain visible without relying on a tooltip.
- Profile titles do not overlap the arrow at `390x844`, `1024x643`, or
  `1440x900`; media reaches the edge of its assigned half without a contrasting
  inset gutter.
- Each recipient and gift occupies the majority of its media frame rather than
  reading as a small object in distant scenery.
- Every carrier label and the crew badge visually touch or sit immediately
  adjacent to the intended vehicle at both review widths.
- The mobile carrier road contains no large decorative orange-and-blue polygons.
- Both secondary outcome actions have a visible background and border.
- The far-route outcome contains no fused, duplicated, cropped, or malformed
  person.
