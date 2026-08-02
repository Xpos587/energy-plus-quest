# Energy+ Guides Agent-Native Conversion Implementation Plan

> **For agentic workers:** After this plan is written, present the execution gate to the user (`/goal-prep` board vs inline executing-plans). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert all 163 slides from the four Energy+ brand-guide PDFs into one canonical, precise `DESIGN.md` plus a non-normative slide coverage map.

**Architecture:** `DESIGN.md` is the only source of design rules and is organized for direct reading by humans and coding agents. `docs/brand-guides-slide-map.md` records one row per source slide and links each substantive slide to its canonical section; the existing `docs/brand-constraints.md` becomes a compatibility pointer instead of retaining duplicate rules.

**Tech Stack:** Markdown, Poppler CLI (`pdfinfo`, `pdftotext`, `pdftoppm`), Git.

## Global Constraints

- Preserve all four PDFs in `materials/brand/` byte-for-byte; do not edit, optimize, rename or replace them.
- Inspect every slide individually at readable resolution; extracted text alone is insufficient for visual rules.
- Account for exactly 63 main-guide slides, 48 illustration-guide slides, 30 visual-guide slides and 22 video-guide slides.
- Use `DESIGN.md` as the single canonical location for every brand rule.
- Use `docs/brand-guides-slide-map.md` only for provenance and coverage; do not restate full rules there.
- Do not create `tokens.json`, a project skill, extracted slide images or new brand assets.
- Separate explicit rules, recommendations, examples, medium-specific guidance, project application and missing assets.
- Preserve exact numbers, names and color values from the PDFs; do not infer unsupported precision.
- Generic installed design-system skills may guide document organization but may not override the Energy+ PDFs.
- Keep the repository self-contained and do not rely on uncommitted files outside it.
- No confirmed `[project:energy-plus-quest]` execution-specific workaround was returned by OpenViking on 2026-08-02.

---

### Task 1: Establish the canonical document structure and audit format

**Files:**

- Create: `DESIGN.md`
- Create: `docs/brand-guides-slide-map.md`

**Interfaces:**

- Consumes: four source PDFs in `materials/brand/` and the approved specification in `docs/specs/2026-08-02-energy-plus-guides-agent-native-design.md`.
- Produces: stable `DESIGN.md` section anchors and a slide-map row schema used by Tasks 2–5.

- [ ] **Step 1: Verify source page counts before conversion**

Run:

```bash
pdfinfo 'materials/brand/ENERGIA PLUS GUIDE (основной).pdf' | rg '^Pages:'
pdfinfo 'materials/brand/ENERGIA PLUS GUIDE (иллюстрации).pdf' | rg '^Pages:'
pdfinfo 'materials/brand/ENERGIA PLUS GUIDE (визуал).pdf' | rg '^Pages:'
pdfinfo 'materials/brand/ENERGIA PLUS GUIDE (видео).pdf' | rg '^Pages:'
```

Expected: `63`, `48`, `30`, `22` in that order.

- [ ] **Step 2: Create the `DESIGN.md` skeleton**

Create sections for:

```markdown
# Дизайн-система «Энергии+»
## Как пользоваться документом
## Источники и обозначения
## Основа бренда
## Логотип
## Цвет
## Типографика
## Сетка и композиция
## Фирменный «Переключатель»
## Иллюстрации
### Первый уровень
### Второй уровень
### Третий уровень
## Визуальный контент и фотография
## Видео
## Движение, переходы и звук
## Применение в веб-квесте
## Недостающие исходные материалы
## Проверочный список
```

Each normative subsection ends with a compact `Источник:` line listing the PDF and slide numbers that support it.

- [ ] **Step 3: Create the slide-map schema**

Use four guide sections and one row per slide:

```markdown
| Слайд | Содержание | Роль | Канонический раздел |
| ---: | --- | --- | --- |
| 1 | Обложка | Обложка, без правила | — |
```

Allowed roles: `правило`, `рекомендация`, `пример`, `разделитель`, `оглавление`, `обложка`. A row may contain more than one role when the slide combines them.

- [ ] **Step 4: Verify anchors and empty row counts**

Run:

```bash
rg '^## ' DESIGN.md
rg '^## .*— [0-9]+ слайд' docs/brand-guides-slide-map.md
```

Expected: all planned canonical sections exist; the four map headings state `63`, `48`, `30`, and `22` slides.

- [ ] **Step 5: Commit the document framework**

```bash
git add DESIGN.md docs/brand-guides-slide-map.md
git commit -m "docs: establish Energy+ design guide structure"
```

### Task 2: Convert the 63-slide main guide

**Files:**

- Modify: `DESIGN.md`
- Modify: `docs/brand-guides-slide-map.md`

**Interfaces:**

- Consumes: stable headings and row schema from Task 1.
- Produces: canonical brand foundation, logo, color, typography, grid, composition and switch rules with complete main-guide provenance.

- [ ] **Step 1: Extract page-separated text to a temporary working directory**

```bash
work_dir=$(mktemp -d)
pdftotext -layout 'materials/brand/ENERGIA PLUS GUIDE (основной).pdf' "$work_dir/main.txt"
```

Expected: the text contains form-feed page separators and recognizable guide headings. Do not commit the temporary file.

- [ ] **Step 2: Render and inspect slides 1–16 individually**

Render only the current batch at readable resolution with `pdftoppm -f 1 -l 16 -jpeg -r 144`, then inspect every generated slide. Record each slide in the map and transfer only supported rules into the relevant canonical section.

- [ ] **Step 3: Render and inspect slides 17–32 individually**

Repeat the same process for pages `17–32`, preserving exact logo variants, size limits, clear-space definitions and background conditions.

- [ ] **Step 4: Render and inspect slides 33–48 individually**

Repeat for pages `33–48`, preserving exact typography, color, grid and composition language without treating examples as universal templates.

- [ ] **Step 5: Render and inspect slides 49–63 individually**

Repeat for pages `49–63`, including examples and prohibitions. Mark covers, indexes and section dividers as such rather than inventing a rule.

- [ ] **Step 6: Verify main-guide coverage and exact values**

Run a row-count check scoped to the main-guide table and search `DESIGN.md` for every exact numeric value and color appearing in the guide.

Expected: 63 numbered rows, no gaps or duplicates; each substantive row links to a real `DESIGN.md` heading.

- [ ] **Step 7: Commit the main-guide conversion**

```bash
git add DESIGN.md docs/brand-guides-slide-map.md
git commit -m "docs: convert Energy+ main brand guide"
```

### Task 3: Convert the 48-slide illustration guide

**Files:**

- Modify: `DESIGN.md`
- Modify: `docs/brand-guides-slide-map.md`

**Interfaces:**

- Consumes: `Иллюстрации` hierarchy established in Task 1 and shared brand foundations from Task 2.
- Produces: complete rules for all illustration levels, including geometry, line, color, texture, light, depth, characters, environments, composition and prohibitions.

- [ ] **Step 1: Extract page-separated text and render slides 1–16**

Use `pdftotext -layout` and `pdftoppm -f 1 -l 16 -jpeg -r 144` in a temporary directory. Inspect every slide, classify it in the map and add supported rules to `DESIGN.md`.

- [ ] **Step 2: Render and inspect slides 17–32**

Record visual rules that text extraction cannot preserve: line construction, corner treatment, relative scale, overlap, support surfaces, gradient behavior, noise placement and safe composition areas.

- [ ] **Step 3: Render and inspect slides 33–48**

Complete second- and third-level illustration guidance. Keep portrait/editorial/comic guidance available but clearly separate it from the default illustration system intended for the web quest.

- [ ] **Step 4: Verify illustration coverage and internal consistency**

Expected: 48 numbered rows, no gaps or duplicates. Confirm that all exact stroke values and colors are sourced, one illustration level is not silently generalized to another, and every prohibition has a supporting slide reference.

- [ ] **Step 5: Commit the illustration-guide conversion**

```bash
git add DESIGN.md docs/brand-guides-slide-map.md
git commit -m "docs: convert Energy+ illustration guide"
```

### Task 4: Convert the 30-slide visual-content guide

**Files:**

- Modify: `DESIGN.md`
- Modify: `docs/brand-guides-slide-map.md`

**Interfaces:**

- Consumes: canonical color, typography and composition terminology from Tasks 2–3.
- Produces: complete visual-content and photography guidance, with medium-specific examples kept distinct from universal brand rules.

- [ ] **Step 1: Extract text and render slides 1–15**

Use a temporary directory, `pdftotext -layout`, and `pdftoppm -f 1 -l 15 -jpeg -r 144`. Inspect every slide and record subject matter, framing, color, lighting, composition and treatment rules.

- [ ] **Step 2: Render and inspect slides 16–30**

Complete the guide, distinguishing normative visual direction from campaign examples and finished-layout demonstrations.

- [ ] **Step 3: Verify visual-guide coverage**

Expected: 30 numbered rows, no gaps or duplicates; every substantive slide maps to `Визуальный контент и фотография` or another justified canonical section.

- [ ] **Step 4: Commit the visual-guide conversion**

```bash
git add DESIGN.md docs/brand-guides-slide-map.md
git commit -m "docs: convert Energy+ visual content guide"
```

### Task 5: Convert the 22-slide video guide

**Files:**

- Modify: `DESIGN.md`
- Modify: `docs/brand-guides-slide-map.md`

**Interfaces:**

- Consumes: canonical logo, typography, color and composition terminology from earlier tasks.
- Produces: complete video, motion, transition, title, logo and sound guidance with explicit relevance boundaries for the static web quest.

- [ ] **Step 1: Extract text and render slides 1–11**

Use a temporary directory, `pdftotext -layout`, and `pdftoppm -f 1 -l 11 -jpeg -r 144`. Inspect every slide and transfer supported production and motion rules.

- [ ] **Step 2: Render and inspect slides 12–22**

Complete title, transition, animation, logo and sound sections. State when a rule applies only to produced video rather than web UI.

- [ ] **Step 3: Verify video-guide coverage**

Expected: 22 numbered rows, no gaps or duplicates; all medium-specific rules remain represented and are not presented as mandatory game behavior.

- [ ] **Step 4: Commit the video-guide conversion**

```bash
git add DESIGN.md docs/brand-guides-slide-map.md
git commit -m "docs: convert Energy+ video guide"
```

### Task 6: Consolidate project application and remove duplicate rules

**Files:**

- Modify: `DESIGN.md`
- Modify: `docs/brand-guides-slide-map.md`
- Modify: `docs/brand-constraints.md`
- Modify: `README.md`

**Interfaces:**

- Consumes: all converted guide content and existing project requirements.
- Produces: a single coherent design-system reference discoverable from existing documentation without duplicate rule sets.

- [ ] **Step 1: Write the web-quest application section**

Derive only project-relevant guidance that follows directly from the brand rules: mobile-first composition, safe areas for controls, default use of first-level illustration, responsive cropping and missing-source-asset constraints. Label these as project application rather than source-guide mandates.

- [ ] **Step 2: Add the final checklist**

Cover logo integrity, typography availability, palette, grid, switch usage, illustration consistency, responsive safe zones, motion restraint, medium-specific scope and source-asset verification.

- [ ] **Step 3: Replace `docs/brand-constraints.md` with a compatibility pointer**

The file retains its heading and links to `../DESIGN.md` as the canonical design system and `brand-guides-slide-map.md` as the source audit. It contains no copied color, typography, logo or illustration rules.

- [ ] **Step 4: Update README discovery**

Change the brand-rules link in `README.md` to `DESIGN.md`; keep the slide map discoverable through `DESIGN.md`, not as an equal source of rules.

- [ ] **Step 5: Run completeness and consistency checks**

Run:

```bash
git diff --check
rg -n '#FF5500|#003CA6|#041327|Normalidad|Переключатель' --glob '*.md'
git status --short
```

Expected: no whitespace errors; canonical rule definitions occur in `DESIGN.md`, while other Markdown files contain only contextual references that do not conflict; source PDFs are absent from `git status`.

- [ ] **Step 6: Manually verify the map against all PDFs**

Confirm totals `63 + 48 + 30 + 22 = 163`, inspect every map row with no canonical target, and ensure each is legitimately a cover, divider, index or non-normative example.

- [ ] **Step 7: Review the final diff for unsupported assertions**

For every exact number, color, font rule and prohibition in `DESIGN.md`, confirm at least one cited source slide. Remove inferred requirements that cannot be traced to the PDFs.

- [ ] **Step 8: Commit the consolidated design system**

```bash
git add DESIGN.md docs/brand-guides-slide-map.md docs/brand-constraints.md README.md
git commit -m "docs: finalize Energy+ agent-native design system"
```

- [ ] **Step 9: Push the completed commits**

```bash
git push origin main
```

Expected: the remote accepts all conversion commits and local `main` is synchronized with `origin/main`.
