# Edik Feedback Four-Screen Revision Implementation Plan

> **For agentic workers:** After this plan is written, present the execution gate to the user (`/goal-prep` board vs inline executing-plans). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the corporate assessment flow with a warm six-state game flow and produce four client-review screen families: onboarding, selection, carrier map, and illustrated outcome.

**Architecture:** Keep the existing React context/reducer architecture and static Vite build. Simplify the state machine, centralize artwork mappings, make carrier vehicles the actual map controls, and collapse consequence/comparison/completion into one illustrated outcome screen. Preserve score values and static deployment behavior.

**Tech Stack:** React 19, TypeScript 7, CSS Modules, Vite 8, Vitest 4, Playwright 1.62, Bun.

## Global Constraints

- Latest client feedback in `materials/feedback/2026-08-17/source.pdf` overrides earlier presentation contracts.
- Client-authored story copy comes from `materials/project/Драфт_первой_сцены_на_просчет_2307.docx`; do not invent product claims.
- Preserve carrier scores exactly, including Express `{ energy: -1, empathy: 5, efficiency: 5 }`.
- Express remains a visible carrier option, but the separate comparison/self-check screen is removed.
- Do not fabricate the GPN-S logo, Normalidad, Express marks, or other corporate assets.
- Use raster media for character, vehicle, and outcome artwork; do not replace key artwork with CSS drawings.
- Desktop and mobile review targets are `1440x900` and `390x844`; both must remain scroll-free.
- `go-task` is not installed in the current environment, so verification uses `bun run check`, `bun run test`, `bun run build`, and `bun run test:e2e` directly.
- Preserve all existing dirty-worktree changes. Do not revert existing review images, `dist/index.html`, `index.html`, meeting materials, or feedback materials.
- Do not commit implementation or regenerated screenshots until Michael visually approves the finished revision.
- Wait for screen animation and `document.fonts.ready` before capturing review screenshots.
- Static packaging must remain self-contained and work from `/specialprojects/energy-plus-quest/` with external requests blocked.
- The 2026-08-20 correction removes the carrier dock entirely and replaces every outcome fallback with a complete carrier-specific narrative backdrop.
- The user explicitly requested inline execution in the current session; no additional execution handoff question is required.
- V4 uses `fal-ai/flux-2-pro` for mobile-first masters and `fal-ai/flux-2-pro/outpaint` for horizontal desktop expansion. Official pricing observed on 2026-08-20 is `$0.03` for the first output megapixel and `$0.015` per additional input/output megapixel.
- Do not generate independent desktop and mobile illustrations. Required content lives in the mobile-safe center; desktop only adds model-generated side context.
- Skip unrequested multi-lens review. Inspect every generated asset and final screenshot directly with `view_image`.

---

### Task 1: Simplify The State Machine And Lock Client Copy

**Files:**

- Modify: `src/game/types.ts`
- Modify: `src/game/gameReducer.ts`
- Modify: `src/game/gameReducer.test.ts`
- Modify: `src/game/content.ts`

**Interfaces:**

- Produces: `GameStep = "intro" | "profile" | "recipient" | "parcel" | "carrier" | "outcome"`.
- Produces: `GameAction` with `BACK` and without `OPEN_CARRIER_MAP`, `SHOW_EXPRESS`, or `COMPLETE_SCENE`.
- Preserves: `CarrierChoice.score`, `findProfile`, `findRecipient`, `findParcel`, and `findCarrier`.
- Produces: optional `ChoiceItem.description` so the UI does not invent filler copy where the draft provides only a name.

- [x] **Step 1: Replace reducer tests with the revised flow and back behavior**

```ts
it("moves directly from parcel selection to the carrier map", () => {
  const state = gameReducer(
    {
      ...initialGameState,
      step: "parcel",
      profile: "student",
      recipient: "alva",
    },
    { type: "CHOOSE_PARCEL", value: "camera" },
  );

  expect(state).toMatchObject({
    step: "carrier",
    profile: "student",
    recipient: "alva",
    parcel: "camera",
  });
});

it("returns from an outcome to the carrier map and clears its score", () => {
  const outcome = gameReducer(
    {
      ...initialGameState,
      step: "carrier",
      profile: "professional",
      recipient: "arseniy",
      parcel: "boat",
    },
    { type: "CHOOSE_CARRIER", value: "crew" },
  );

  expect(gameReducer(outcome, { type: "BACK" })).toEqual({
    step: "carrier",
    profile: "professional",
    recipient: "arseniy",
    parcel: "boat",
    scores: { energy: 0, empathy: 0, efficiency: 0 },
  });
});

it("walks backward through the personalization choices", () => {
  expect(
    gameReducer(
      { ...initialGameState, step: "recipient", profile: "student" },
      { type: "BACK" },
    ).step,
  ).toBe("profile");
  expect(
    gameReducer(
      {
        ...initialGameState,
        step: "parcel",
        profile: "student",
        recipient: "alva",
      },
      { type: "BACK" },
    ).step,
  ).toBe("recipient");
});
```

- [x] **Step 2: Run unit tests and verify the new expectations fail**

Run: `bun run test -- src/game/gameReducer.test.ts`

Expected: FAIL because `CHOOSE_PARCEL` still returns `briefing` and `BACK` is not a valid action.

- [x] **Step 3: Reduce the public state/action types**

```ts
export type GameStep =
  | "intro"
  | "profile"
  | "recipient"
  | "parcel"
  | "carrier"
  | "outcome";

export type GameAction =
  | { type: "START" }
  | { type: "CHOOSE_PROFILE"; value: ProfileId }
  | { type: "CHOOSE_RECIPIENT"; value: RecipientId }
  | { type: "CHOOSE_PARCEL"; value: ParcelId }
  | { type: "CHOOSE_CARRIER"; value: CarrierId }
  | { type: "BACK" }
  | { type: "RESET" };

export type ChoiceItem<T extends string> = {
  id: T;
  title: string;
  eyebrow: string;
  description?: string;
  symbol: string;
};
```

- [x] **Step 4: Implement direct progression and deterministic back navigation**

```ts
const emptyScores = { energy: 0, empathy: 0, efficiency: 0 };

export const initialGameState: GameState = {
  step: "intro",
  scores: emptyScores,
};

function goBack(state: GameState): GameState {
  switch (state.step) {
    case "profile":
      return { ...state, step: "intro" };
    case "recipient":
      return { ...state, step: "profile", recipient: undefined };
    case "parcel":
      return { ...state, step: "recipient", parcel: undefined };
    case "carrier":
      return { ...state, step: "parcel", carrier: undefined, scores: emptyScores };
    case "outcome":
      return { ...state, step: "carrier", carrier: undefined, scores: emptyScores };
    case "intro":
      return state;
  }
}
```

Update `CHOOSE_PARCEL` to return `step: "carrier"`; remove the three obsolete reducer cases; route `BACK` through `goBack`.

- [x] **Step 5: Replace generated-sounding choice and result copy with draft-backed wording**

Use these exact choice labels:

```ts
profiles: [
  { id: "student", title: "Студент", eyebrow: "Вы —" },
  { id: "professional", title: "Профессионал", eyebrow: "Вы —" },
]

recipients: [
  { id: "alva", title: "Девочка Альва", eyebrow: "Получатель" },
  { id: "khor", title: "Северный олень Хор", eyebrow: "Получатель", description: "«Хор» с языка хантов — самец оленя." },
  { id: "arseniy", title: "Арсений", eyebrow: "Вахтовый работник" },
]

parcels: [
  { id: "camera", title: "Фотоаппарат", eyebrow: "Подарок" },
  { id: "socks", title: "Вязаные носки", eyebrow: "Подарок" },
  { id: "boat", title: "Лодка", eyebrow: "Подарок" },
]
```

Adapt the four `resultBody` values from the DOCX without changing their factual consequence or scores. Remove advertising language from carrier descriptions; Express becomes `Автоподбор Express` with `Подберёт перевозчика по состоянию техники, экипажу и стоимости.`

- [x] **Step 6: Run unit tests**

Run: `bun run test -- src/game/gameReducer.test.ts`

Expected: all reducer tests PASS, including the unchanged Express score assertion.

---

### Task 2: Build The Six-State Interface And Persistent Choice Context

**Files:**

- Create: `src/game/artwork.ts`
- Modify: `src/App.tsx`
- Modify: `src/App.module.css`
- Modify: `src/components/ScoreBoard.tsx`

**Interfaces:**

- Consumes: simplified `GameStep` and `BACK` action from Task 1.
- Produces: `choiceArtwork` and `carrierArtwork` record mappings used by App and CityMap.
- Produces: shared `BackButton` and `SelectionSummary` UI.

- [x] **Step 1: Centralize asset imports so App and CityMap share one mapping**

```ts
import type { CarrierId } from "./types";

export const choiceArtwork: Record<string, string> = {
  student: studentArtwork,
  professional: professionalArtwork,
  alva: alvaArtwork,
  khor: khorArtwork,
  arseniy: arseniyArtwork,
  camera: cameraArtwork,
  socks: socksArtwork,
  boat: boatArtwork,
};

export const carrierArtwork: Record<CarrierId, string> = {
  old: carrierOldArtwork,
  near: carrierNearArtwork,
  crew: carrierCrewArtwork,
  express: carrierExpressArtwork,
};

```

- [x] **Step 2: Replace the screen switch with the approved six-state flow**

Remove `Briefing`, `ExpressReveal`, `ComparisonRow`, `comparisonPosition`, and `Complete`. Use:

```tsx
{state.step === "intro" && <Intro onStart={() => dispatch({ type: "START" })} />}
{state.step === "profile" && (
  <ChoiceScreen
    description="Выберите, кто отправится в путь."
    eyebrow="Начало игры · роль"
    items={profiles}
    onBack={() => dispatch({ type: "BACK" })}
    onSelect={(value) => dispatch({ type: "CHOOSE_PROFILE", value })}
    title="Кто отправится в путь?"
  />
)}
{state.step === "recipient" && (
  <ChoiceScreen
    description="Выберите того, кому мы повезём подарок."
    eyebrow="Получатель"
    items={recipients}
    onBack={() => dispatch({ type: "BACK" })}
    onSelect={(value) => dispatch({ type: "CHOOSE_RECIPIENT", value })}
    title="Выберите получателя"
  />
)}
{state.step === "parcel" && (
  <ChoiceScreen
    description="Решите, что окажется внутри посылки."
    eyebrow="Подарок"
    items={parcels}
    onBack={() => dispatch({ type: "BACK" })}
    onSelect={(value) => dispatch({ type: "CHOOSE_PARCEL", value })}
    title="Что будет в посылке?"
  />
)}
{state.step === "carrier" && (
  <CarrierScreen
    onBack={() => dispatch({ type: "BACK" })}
    onSelect={(value) => dispatch({ type: "CHOOSE_CARRIER", value })}
  />
)}
{state.step === "outcome" && (
  <Outcome
    onBack={() => dispatch({ type: "BACK" })}
    onReset={() => dispatch({ type: "RESET" })}
  />
)}
```

In `ChoiceScreen`, render description copy only when the client source contains it:

```tsx
{item.description && <p>{item.description}</p>}
```

- [x] **Step 3: Replace intro copy and identity hierarchy**

```tsx
<p className={styles.gameStart}>Начало игры</p>
<h1>Доставляем <span>радость</span></h1>
<p>
  У логистов есть профессиональное правило: не бывает неважных грузов.
  Для кого-то это многотонная турбина, а для кого-то — одна маленькая
  коробка, одна большая радость.
</p>
<p>
  Сегодня вам предстоит провести такой груз на Крайний Север — быстро,
  легко и с любовью к людям.
</p>
<button type="button" onClick={onStart}>Начать игру</button>
```

In the header, separate `Доставляем радость` from a neutral `Газпромнефть-Снабжение` text identity slot. Do not reuse the Energy+ app icon as the company logo.

- [x] **Step 4: Add unobtrusive back navigation and persistent visual choices**

```tsx
function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <button className={styles.backButton} onClick={onClick} type="button">
      <span aria-hidden="true">←</span>
      Назад
    </button>
  );
}

function SelectionSummary() {
  const { state } = useGame();
  const selected = [state.profile, state.recipient, state.parcel].filter(Boolean);
  if (selected.length === 0) return null;

  return (
    <div className={styles.selectionSummary} aria-label="Ваш выбор">
      {selected.map((id) => (
        <img alt="" aria-hidden="true" key={id} src={choiceArtwork[id ?? ""]} />
      ))}
    </div>
  );
}
```

Render `SelectionSummary` in the header before the secondary score widgets.

- [x] **Step 5: Make scores secondary until the result**

Keep `ScoreBoard` accessible, but reduce its desktop width and hide long labels on the map. The result retains `ScoreDelta` with exact values. Do not remove score semantics or icons.

- [x] **Step 6: Add layout styles for the revised hierarchy**

Add these CSS contracts and tune values after screenshot inspection:

```css
.backButton {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 40px;
  border: 0;
  background: transparent;
  color: var(--ink-blue);
}

.selectionSummary {
  display: flex;
  align-items: center;
  gap: 6px;
}

.selectionSummary img {
  width: 36px;
  height: 36px;
  border: 2px solid #fff;
  border-radius: 50%;
  object-fit: cover;
  background: #fff;
}

.openingPanel {
  max-width: 620px;
}

.openingPanel > p {
  max-width: 54ch;
}
```

Mobile must keep the primary action and back control inside `390x844` with no page scroll.

- [x] **Step 7: Run type, unit, and build verification**

Run:

```sh
bun run check
bun run test
bun run build
```

Expected: all commands exit `0`; no obsolete step name remains in `src/`.

---

### Task 3: Make Vehicles The Map Controls And Outcomes The Story

**Files:**

- Modify: `src/components/CityMap.tsx`
- Modify: `src/App.tsx`
- Modify: `src/App.module.css`
- Modify: `tests/scene.spec.ts`
- Modify: `tests/layout.spec.ts`

**Interfaces:**

- Consumes: `carrierArtwork` from Task 2.
- Produces: direct vehicle buttons with stable `aria-label` values.
- Produces: final `Outcome` screen with back/reset/next-soon actions.

- [x] **Step 1: Rewrite Playwright expectations for the six-state flow**

The primary journey must assert:

```ts
await page.getByRole("button", { name: /Начать игру/ }).click();
await page.getByRole("button", { name: /Студент/ }).click();
await page.getByRole("button", { name: /Альва/ }).click();
await page.getByRole("button", { name: /Фотоаппарат/ }).click();
await expect(
  page.getByRole("heading", { name: "Выберите транспорт для подарка" }),
).toBeVisible();
await page.getByRole("button", { name: /^Машина 2:/ }).click();
await expect(
  page.getByRole("heading", { name: "Близко — не значит быстро" }),
).toBeVisible();
await expect(page.getByRole("button", { name: /Назад к машинам/ })).toBeVisible();
await expect(page.getByText(/Теперь нам нужно погрузить подарок/)).toBeVisible();
```

Add a back-navigation test that returns from outcome to carrier, selects Express, and confirms the Express outcome appears without a comparison screen.

- [x] **Step 2: Run E2E tests and verify they fail against the old UI**

Run: `bun run test:e2e -- tests/scene.spec.ts`

Expected: FAIL on `Начать игру`, direct parcel-to-map navigation, and result actions.

- [x] **Step 3: Replace locator pins with vehicle buttons**

Each `mapHotspot` renders the actual vehicle:

```tsx
<button
  aria-label={`${marker.label}: ${carrier?.title ?? "перевозчик"}`}
  className={styles.mapVehicle}
  data-carrier={marker.carrier}
  key={marker.carrier}
  onClick={() => onSelect(marker.carrier)}
  type="button"
>
  <img alt="" aria-hidden="true" src={carrierArtwork[marker.carrier]} />
  <span>{marker.carrier === "express" ? "Express" : marker.label}</span>
</button>
```

Remove `locatorBlue`, `locatorOrange`, `locatorBadge`, and pin-number decoration. Preserve the existing hotspot coordinates so the map remains structurally stable.

- [x] **Step 4: Add meaningful vehicle motion**

```css
.mapVehicle img {
  width: clamp(76px, 8vw, 132px);
  filter: drop-shadow(0 8px 10px rgb(4 19 39 / 18%));
}

.mapVehicle[data-carrier="old"] img {
  animation: old-truck-route 8s ease-in-out infinite alternate;
}

.mapVehicle[data-carrier="near"] img {
  animation: near-truck-route 11s linear infinite alternate;
}

.mapVehicle[data-carrier="crew"] img {
  animation: crew-truck-route 7s ease-in-out infinite alternate;
}

.mapVehicle[data-carrier="express"] img {
  animation: express-truck-route 6s ease-in-out infinite alternate;
}

@media (prefers-reduced-motion: reduce) {
  .mapVehicle img {
    animation: none !important;
  }
}
```

Keyframes use only `transform: translate3d(...)`; do not animate layout properties.

- [x] **Step 5: Replace the mission and carrier dock copy**

Use:

```tsx
<p className={styles.eyebrow}>Первый участок пути</p>
<h2>Выберите транспорт для подарка</h2>
<p>
  Прежде всего, нам нужно найти лучший транспорт для перевозки подарка.
  Нажмите на машину, которая лучше всего справится с задачей.
</p>
```

The bottom dock may retain short factual labels for accessibility and mobile clarity, but vehicle imagery remains the dominant target and Express has no sales paragraph.

- [x] **Step 6: Turn `Outcome` into the illustrated scene ending**

```tsx
<div className={styles.outcomeArtwork}>
  <img alt="" aria-hidden="true" src={carrierArtwork[carrier.id]} />
</div>
<div className={styles.outcomeCopy}>
  <p className={styles.eyebrow}>Вот что произошло</p>
  <h2>{carrier.resultTitle}</h2>
  <p className={styles.panelLead}>
    {interpolateOutcome(carrier.resultBody, recipient?.title, parcel?.title)}
  </p>
  <ScoreDelta scores={carrier.score} />
  <p className={styles.nextBeat}>Теперь нам нужно погрузить подарок...</p>
  <div className={styles.resultActions}>
    <button className={styles.textButton} onClick={onBack} type="button">
      Назад к машинам
    </button>
    <button className={styles.primaryButton} disabled type="button">
      Дальше · скоро
    </button>
    <button className={styles.textButton} onClick={onReset} type="button">
      Начать заново
    </button>
  </div>
</div>
```

Keep the schedule shift and carrier facts as one compact supporting row. Remove Express comparison controls and completion-summary statistics. Task 4 replaces the temporary carrier visual with the accepted outcome artwork before the client-review package is captured.

- [x] **Step 7: Update layout tests for every revised state**

Remove obsolete briefing/express/complete clicks. Keep `expectNoPageScroll`, `expectControlsInsideViewport`, score-icon checks, and result overlap checks. Run the full flow through the outcome on both Playwright projects.

- [x] **Step 8: Run focused E2E tests**

Run:

```sh
bun run test:e2e -- tests/scene.spec.ts tests/layout.spec.ts
```

Expected: all desktop and mobile tests PASS.

---

### Task 4: Produce Feedback-Specific Media And The Four-Screen Review Package

**Files:**

- Create: `design/scene-01/assets/feedback-v1/professional.webp`
- Create: `design/scene-01/assets/feedback-v1/khor.webp`
- Create: `design/scene-01/assets/feedback-v1/boat.webp`
- Create: `design/scene-01/assets/feedback-v1/outcome-express.webp`
- Create: `design/scene-01/assets/feedback-v1/map-desktop.webp`
- Create: `design/scene-01/assets/feedback-v1/map-mobile.webp`
- Create: `design/scene-01/assets/feedback-v1/carrier-old.png`
- Create: `design/scene-01/assets/feedback-v1/carrier-near.png`
- Create: `design/scene-01/assets/feedback-v1/carrier-crew.png`
- Create: `design/scene-01/assets/feedback-v1/carrier-express.png`
- Create: prompt/provenance Markdown beside each accepted media set.
- Modify: `src/game/artwork.ts`
- Modify: `tests/scene.spec.ts`
- Modify: `scripts/verify-static-runtime.mjs`
- Regenerate: selected files under `design/scene-01/review/`

**Interfaces:**

- Consumes: current `choices-v2` images, carrier cutouts, and page 3 of the feedback PDF as edit references.
- Produces: replaceable raster assets with stable aspect ratios and transparent/clean safe areas.
- Produces: eight review screenshots: four states x desktop/mobile.

- [x] **Step 1: Use image editing rather than from-scratch replacement for existing characters**

Read and follow the `imagegen` skill before generating media. Edit the existing professional, reindeer, and boat assets:

- professional: mature face, current orange/blue PPE from feedback page 3, same illustration family and card-facing pose;
- reindeer: entire body, antlers, and legs inside the frame with safe margins;
- boat: small practical northern workboat, not a passenger liner.

Save the exact prompts and accepted outputs under `design/scene-01/assets/feedback-v1/`.

- [x] **Step 2: Edit the map and vehicle system without changing hotspot geometry**

Edit the existing desktop/mobile maps rather than regenerating them. Remove or fade baked-in vehicles, locator circles, and dominant decorative fills; preserve road, building, and hotspot geometry. Edit the four existing carrier cutouts so their differences are visually readable:

- old: worn bodywork and a small smoke cue;
- near: ordinary single-driver truck, visually slower and less prominent;
- crew: newer truck with a visible two-person crew cue in the cab;
- Express: clean orange vehicle, branded only with assets already available or neutral `Express` text.

- [x] **Step 3: Generate the one representative Express outcome requested for approval**

The image shows the orange Express vehicle travelling confidently with a two-driver crew and the selected gift safely in transit. It shares the existing Energy+ palette and illustration language, adds warmth and human detail, and copies no reference-game art. Other carrier outcomes continue to use the edited carrier visual during this approval round.

- [x] **Step 4: Wire accepted media into `src/game/artwork.ts` and build**

Use the edited maps/carriers globally and add a partial outcome mapping so only the approved Express branch uses the new result scene:

```ts
export const outcomeArtwork: Partial<Record<CarrierId, string>> = {
  express: outcomeExpressArtwork,
};
```

In `Outcome`, use `outcomeArtwork[carrier.id] ?? carrierArtwork[carrier.id]`.

Run: `bun run build`

Expected: TypeScript and Vite build PASS; all outcome assets appear in `dist/assets/`.

- [x] **Step 5: Rewrite screenshot capture to emit only the client-review set**

Capture:

- `intro-desktop.png` / `intro-mobile.png`;
- `profile-desktop.png` / `profile-mobile.png` using the professional choice frame;
- `carrier-desktop.png` / `carrier-mobile.png`;
- `outcome-desktop.png` / `outcome-mobile.png` using one representative outcome.

Wait for `document.fonts.ready`, all images to be complete, and at least `700ms` after each transition before capture.

- [x] **Step 6: Update static-runtime verification for the new path**

Replace obsolete actions in `scripts/verify-static-runtime.mjs` with:

```js
await page.getByRole("button", { name: /Начать игру/ }).click();
await page.getByRole("button", { name: /Студент/ }).click();
await page.getByRole("button", { name: /Альва/ }).click();
await page.getByRole("button", { name: /Фотоаппарат/ }).click();
await page.getByRole("button", { name: /Автоподбор Express/ }).click();
await page
  .getByRole("heading", { name: "Перевозчик найден за два часа" })
  .waitFor();
```

Keep all six viewport profiles, external-request blocking, image-load checks, and no-scroll assertions.

- [x] **Step 7: Run the full verification suite**

Run:

```sh
bun run check
bun run test
bun run build
bun run test:e2e
git diff --check
sh scripts/package-static.sh
```

Expected:

- Biome, Vitest, build, and Playwright exit `0`.
- Desktop/mobile review images are regenerated after settled animations.
- `git diff --check` prints nothing.
- `release/energy-plus-quest-static.zip` is verified at the nested path with no external runtime dependency or page scroll across all six static-runtime profiles.

- [x] **Step 8: Inspect every review artifact at original detail**

Open all eight regenerated review images individually. Reject and fix any:

- clipping, scroll, overlapping text, or hidden controls;
- fake/misleading logo treatment;
- vehicle that is less visible than the map background;
- professional who still reads as the student's age;
- cropped reindeer or liner-like boat;
- outcome that reads as a data card rather than a human consequence;
- stale briefing, Express comparison, or completion copy.

Do not commit. Hand the dirty worktree and the eight images to Michael for visual approval.

---

### Task 5: Correct The Rejected Carrier And Outcome Compositions

**Files:**

- Modify: `tests/scene.spec.ts`
- Modify: `tests/layout.spec.ts`
- Modify: `src/components/CityMap.tsx`
- Modify: `src/App.tsx`
- Modify: `src/App.module.css`
- Modify: `src/game/artwork.ts`
- Create: `design/scene-01/assets/feedback-v2/outcome-old.webp`
- Create: `design/scene-01/assets/feedback-v2/outcome-near.webp`
- Create: `design/scene-01/assets/feedback-v2/outcome-crew.webp`
- Create: `design/scene-01/assets/feedback-v2/outcome-express.webp`
- Create: `design/scene-01/assets/feedback-v2/prompts.md`

**Interfaces:**

- Preserves: the approved reducer flow and exact score values.
- Produces: exactly four `button.mapVehicle` controls on the carrier screen.
- Produces: `outcomeArtwork: Record<CarrierId, string>` with no fallback branch.
- Produces: a result layout with one consequence line, score delta, back/reset actions, and no carrier-facts table.

- [ ] **Step 1: Write failing browser assertions for the corrected visual contract**

Assert that the carrier screen has exactly four buttons inside the map, no carrier dock, and no duplicate carrier titles outside the map. Assert that every result contains a carrier-specific scene image and no `График`, `Техника`, `Экипаж`, or `Цена` fact labels.

- [ ] **Step 2: Run the focused Playwright tests and confirm RED**

Run: `bun run test:e2e -- tests/scene.spec.ts --project=desktop-chromium`

Expected: FAIL because `.carrierDock` still duplicates the four choices and `.carrierFacts` is still rendered.

- [ ] **Step 3: Generate four complete narrative outcome backdrops**

Use one consistent flat editorial game-illustration direction, a restrained Energy+ blue/orange/warm-white palette, no logos, no text, no watermark, and negative space for the story panel. Save the exact prompt variants and provider/model provenance in `feedback-v2/prompts.md`.

- [ ] **Step 4: Make map vehicles the sole carrier controls**

Delete the `carrierDock` render path and its styling. Enlarge the four map vehicles, attach one concise label and one factual hint, strengthen hover/focus/tap affordance, and retain transform-only route motion plus reduced-motion support.

- [ ] **Step 5: Replace the report card with an illustrated story outcome**

Use the complete carrier-specific artwork as the dominant field. Remove the four-column carrier-facts table. Render the interpolated story, one schedule/consequence chip, compact `ScoreDelta`, `Теперь нам нужно погрузить подарок...`, and the existing navigation actions.

- [ ] **Step 6: Tune desktop and mobile as separate compositions**

At `1440x900`, keep the mission card small and the vehicles dominant. At `390x844`, keep the map and result within one viewport, enlarge touch targets, and avoid any vertical carrier-card grid.

- [ ] **Step 7: Run complete verification and inspect screenshots at original detail**

Run `bun run check`, `bun run test`, `bun run build`, `bun run test:e2e`, `git diff --check`, and `sh scripts/package-static.sh`. Inspect regenerated carrier/outcome screenshots for desktop and mobile before handing them to Michael. Do not commit until visual approval.

---

### Task 6: Rebuild The Illustrative System From Mobile-First FLUX.2 Masters

**Files:**

- Create: `design/scene-01/assets/feedback-v4/prompts.md`
- Create: `design/scene-01/assets/feedback-v4/carrier-mobile.png`
- Create: `design/scene-01/assets/feedback-v4/carrier-desktop.png`
- Create: `design/scene-01/assets/feedback-v4/{student,professional,alva,khor,arseniy,camera,socks,boat}.png`
- Create: `design/scene-01/assets/feedback-v4/outcome-{old,near,crew,express}.png`
- Modify: `src/game/artwork.ts`
- Modify: `src/components/CityMap.tsx`
- Modify: `src/game/content.ts`
- Modify: `src/App.module.css`
- Modify: `tests/scene.spec.ts`
- Modify: `tests/layout.spec.ts`

**Interfaces:**

- Produces: one mobile carrier master with exactly four vehicles and one warehouse.
- Produces: a desktop carrier image created only by horizontal outpainting of that master.
- Preserves: existing `choiceArtwork` and `outcomeArtwork` record interfaces.
- Preserves: reducer behavior and all score values.

- [ ] **Step 1: Add failing browser assertions for the V4 contract**

Assert the carrier scene exposes four answer buttons with factual accessible names containing the near/far route distinctions. Assert the page loads only `feedback-v4` choice, carrier, and outcome artwork and contains no obsolete result title `Возраст берёт своё`.

- [ ] **Step 2: Run the focused tests and confirm RED**

Run: `bun run test:e2e -- tests/scene.spec.ts tests/layout.spec.ts --project=desktop-chromium`

Expected: FAIL because current imports target `feedback-v1/v2/v3`, route labels do not fully encode distance, and the old result title remains.

- [ ] **Step 3: Run one 1-MP carrier smoke test**

Call `fal-ai/flux-2-pro` once with a portrait mobile-first prompt. Save the seed and exact prompt. Inspect the output with `view_image`. Continue only if it contains exactly four maintained vehicles, one obvious warehouse, a short near route, a long far route, bright daylight, no text/logos, and no bleak or damaged imagery.

- [ ] **Step 4: Expand the accepted carrier master horizontally**

Call `fal-ai/flux-2-pro/outpaint` on the accepted master with left/right expansion only. Keep the original center unchanged. Inspect the output with `view_image` and reject seams, duplicated vehicles, added warehouses, route discontinuity, or darker grading.

- [ ] **Step 5: Generate the remaining mobile-safe illustrative masters**

Generate roles, recipients, gifts, and four outcomes using the same style block and palette. Keep every subject fully inside a central 4:5 safe frame so the same file can be used at all viewports. Inspect every image individually before integration; generate a replacement only for a rejected asset.

- [ ] **Step 6: Integrate V4 media and constructive copy**

Switch `artwork.ts` and `CityMap.tsx` to `feedback-v4`. Rewrite negative result headings and sentences without changing the factual delivery shifts or scores. Position hotspots over the four vehicles in the shared mobile master region and retain the same normalized coordinates on the desktop expansion.

- [ ] **Step 7: Capture and visually inspect the complete review set**

Run the existing screenshot flow at `390x844` first, then `1440x900`. Open every review image with `view_image`. Fix any crop, overlap, hidden control, route ambiguity, dark/depressive treatment, or mixed illustration language.

- [ ] **Step 8: Run complete verification and rebuild the archive**

Run `bun run check`, `bun run test`, `bun run build`, `bun run test:e2e`, `git diff --check`, and `sh scripts/package-static.sh`. Do not commit until Michael visually approves the V4 result.

---

### Task 7: Restore Visual Legibility Across Metrics, Choices, Map, And Outcome

**Files:**

- Modify: `tests/scene.spec.ts`
- Modify: `tests/layout.spec.ts`
- Modify: `src/components/ScoreBoard.tsx`
- Modify: `src/components/CityMap.tsx`
- Modify: `src/App.module.css`
- Modify: `src/game/artwork.ts`
- Modify: `design/scene-01/assets/feedback-v4/prompts.md`
- Create: `design/scene-01/assets/feedback-v5/metrics/*.webp`
- Create: `design/scene-01/assets/feedback-v5/choices/professional.webp`
- Create: `design/scene-01/assets/feedback-v5/carrier-mobile.webp`
- Create: `design/scene-01/assets/feedback-v5/outcomes/old-mobile.webp`
- Create: `design/scene-01/assets/feedback-v5/outcomes/old-desktop.webp`

**Interfaces:**

- Preserves: game state, carrier scores, copy, and all choice identifiers.
- Produces: `scoreItems` backed by three generated metric pictograms.
- Produces: the existing `choiceArtwork` and `outcomeArtwork` records with only
  the approved professional and old-outcome sources replaced.
- Produces: four map buttons whose visible labels and optional crew badge are
  spatially attached to the matching vehicles.

- [ ] **Step 1: Add failing browser assertions for V5 semantics**

Assert that score labels remain visible on mobile, metric images expose the V5
asset marker, profile buttons contain a dedicated role label/title/action
structure, map labels expose their carrier id, and both result secondary actions
use the secondary-button class.

- [ ] **Step 2: Run focused Playwright and confirm RED**

Run:

```sh
bun run test:e2e -- tests/scene.spec.ts tests/layout.spec.ts --project=mobile-chromium
```

Expected: FAIL because the existing SVG metrics have no V5 marker, mobile hides
`.scoreLong`, map labels have no carrier marker, and role cards still use the V4
split layout.

- [ ] **Step 3: Generate and visually accept the replacement media**

Generate three large square metric pictograms and one approachable professional
portrait with `fal-ai/flux-2-pro`. Correct the lower carrier road and far-route
people with masked `fal-ai/flux-kontext-lora/inpaint`. Inspect every accepted
candidate at original detail before production conversion.

- [ ] **Step 4: Integrate metrics and choice-card hierarchy**

Replace metric imports, keep labels visible, increase score and delta icons,
make profile media edge-to-edge, equalize role title scale, reserve the arrow
column, and crop recipient/gift artwork closer without losing recognition.

- [ ] **Step 5: Attach map annotations and repair outcome controls**

Attach visible labels and the crew badge to their vehicles at desktop and mobile
coordinates. Remove the lower-road polygons. Give both secondary result actions
an opaque/translucent surface, border, and complete interaction states.

- [ ] **Step 6: Capture and inspect all affected review screens**

Capture profile, recipient, parcel, carrier, and outcome at `390x844` and
`1440x900`. Reject small subjects, inset media gutters, label drift, icon
ambiguity, weak buttons, or malformed people.

- [ ] **Step 7: Run complete verification and package**

Run:

```sh
bun run check
bun run test
bun run build
bun run test:e2e
git diff --check
sh scripts/package-static.sh
```

Do not commit until Michael visually approves the V5 result.
