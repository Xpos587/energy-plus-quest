---
description: Use when establishing or migrating to a token-based design system. Covers the multi-layer token architecture (primitive → semantic → component), naming conventions, theming patterns, and how to migrate from hard-coded values without a full rewrite.
metadata:
    github-path: skills/brand-system-tokens
    github-ref: refs/tags/v1.0.0
    github-repo: https://github.com/x3fleetsafety/design-skills
    github-tree-sha: 45931be9d1587102ec130bd001341b752360ceaa
name: brand-system-tokens
---
# Brand System Tokens

A token system is the contract between design and code. Without it, every component is reinventing the wheel.

## Token layers (three deep)

### Primitive tokens (raw values)
```css
--blue-500: #3B82F6;
--gray-50: #F8FAFC;
--space-4: 16px;
--radius-md: 8px;
```

Raw values. Never used directly in UI components.

### Semantic tokens (intent-based)
```css
--color-text-primary: var(--gray-50);
--color-bg: var(--gray-900);
--color-accent: var(--teal-500);
--space-card-padding: var(--space-5);
--radius-card: var(--radius-md);
```

Semantic = "what role this color plays." This layer is what changes between themes.

### Component tokens (per-component)
```css
.button-primary {
  --bg: var(--color-accent);
  --text: var(--color-bg);
  --padding: var(--space-3) var(--space-5);
}
```

Per-component overrides if needed. Most components only use semantic tokens.

## Naming conventions

| Prefix | Example | Use |
|---|---|---|
| `color-` | `--color-bg`, `--color-text-primary` | Colors |
| `space-` | `--space-4`, `--space-card-padding` | Spacing |
| `radius-` | `--radius-md` | Border radius |
| `shadow-` | `--shadow-card` | Box shadows |
| `motion-` | `--motion-fast` | Durations |
| `font-` | `--font-display`, `--font-body` | Type stacks |

Use consistent prefixes. Avoid abbreviations.

## Theming with tokens

Theme = swap semantic tokens to point at different primitives:

```css
:root {
  --color-bg: var(--gray-900);
  --color-text-primary: var(--gray-50);
}
[data-theme="light"] {
  --color-bg: var(--gray-50);
  --color-text-primary: var(--gray-900);
}
```

Components don't change. Just toggle `data-theme` on root.

## Migrating from hard-coded values

Step 1: Audit existing colors / spacing. Count unique values.
Step 2: Build the token ladder based on what's actually used.
Step 3: Replace component-by-component. Use grep + sed to find all `#3B82F6` and replace with `var(--color-accent)`.
Step 4: Test theming works by adding light theme variant.

## Common mistakes

- One layer only (no primitive layer, semantic only) — can't share primitives across themes
- Too many semantic tokens (`--color-button-primary-bg-hover-active-light`) — keep it sparse
- Semantic names that lock to color ("blue") instead of intent ("primary")
- Token tree too deep (4+ levels) — hard to debug

## Where this fits in X3 Compass

X3 Compass uses two-layer (primitive + semantic) in `brand/palette.css`. Components consume semantic tokens. Future light-mode = swap semantic vars on `:root`.
