---
description: Use when documenting a design system for cross-team use. Covers the documentation structure (Storybook, Notion, dedicated docs site), what to document, who reads it, and the maintenance cost.
metadata:
    github-path: skills/design-system-documentation
    github-ref: refs/tags/v1.0.0
    github-repo: https://github.com/x3fleetsafety/design-skills
    github-tree-sha: 559e2b48bc5fdca738f63c502fd4c766cccd3984
name: design-system-documentation
---
# Design System Documentation

A design system without documentation is a private joke between designers and the original engineers.

## What to document

1. **Foundations** — colors, type, spacing, motion (tokens)
2. **Components** — every primitive + composition with usage examples
3. **Patterns** — common screen patterns (login, dashboard, settings)
4. **Voice** — copy guidelines, terminology
5. **Accessibility** — baseline requirements + per-component notes
6. **Brand assets** — logo, illustrations, photography rules
7. **Migration guides** — old patterns → new patterns

## Where to host

| Tool | Strengths | Cost |
|---|---|---|
| Storybook | Live component examples | Free, self-hosted |
| Zeroheight | Designer-friendly, Figma sync | $$/mo |
| Notion | Easy for non-designers | Free-$$ |
| Custom docs site | Full control | Dev time |
| Inside Figma (with prototypes) | Single source of truth | Free in Figma |

For most SaaS, **Storybook + Notion** is a great combination: Storybook for live components, Notion for narrative.

## Per-component doc template

For each component:
1. What it is (1 sentence)
2. When to use it
3. When NOT to use it
4. Variants + props
5. Live example
6. Code snippet
7. Accessibility notes
8. Related components

## Update cadence

- Major release → docs updated synchronously
- Minor release → docs within 1 sprint
- Component-level changes → docs updated in same PR

Don't merge code without doc updates.

## Common mistakes

- Docs that drift from code (out of date within 6 months)
- Component docs without "when NOT to use"
- Docs that show variants but not patterns
- Storybook with 200 components but no narrative
- Documentation behind an SSO that blocks contractors

## Where this fits in X3 Compass

X3 Compass is single-developer right now — doc-as-code in the repo (BRAND.md, design-skills repo). At team scale, would migrate to Storybook + Notion.
