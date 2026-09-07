# Mobile-master media and responsive polish

## Current decision

- Existing mobile map and four outcome images remain the canonical visual sources and are unchanged in the runtime.
- Desktop artwork is now generated expansion of those mobile scenes, not separately composed illustrations.
- The map extension contains industrial buildings, roads and loading areas. The first coastal extension was rejected; the final extension has no sea or beach.
- Rectangular source-paste composites were rejected because they introduced visible seams. Runtime uses the seamless raw outpaint outputs, visually reviewed against the mobile originals.

## Rendering

The image box, rather than device width, selects the mobile or expanded image through a CSS container aspect-ratio query. A single visible image covers each outcome surface. The old cover-background plus contain-foreground stack and mobile blurred duplicate are removed.

The map and its labels share a cover-sized coordinate plane inside a clipped, rounded surface. Decorative outer streets can be cropped; truck labels remain inside the visible surface. Desktop and mobile coordinates follow their respective mobile-derived artwork. The tall-phone fourth label is above its truck rather than outside the right edge.

Progress circles are 28px on every breakpoint, with 18px regular numerals, a unit line height and shared optical alignment. The first numeral compensates for the font's asymmetric sidebearing. White numerals on brand orange remain unchanged. Efficiency now uses an ascending line-chart icon with axes and an arrowhead.

## Evidence

- `tests/viewport.spec.ts` checks shared numeral geometry, all map-label bounds, media coverage, a single visible outcome layer, and no duplicate image background.
- Full browser suite: 130 passed, 18 intentional skips across 12 viewport profiles.
- Build, unit tests and configured code checks pass.
- Standalone ZIP verified after extraction at 12 viewport profiles, including 430x932; all resources local, no horizontal or vertical page overflow.
- Additional captures cover desktop, phone, short phone, ultrawide and 150%-equivalent viewport/device scaling.
- Sol reviewed the mobile-derived art; Terra reviewed runtime integration. No unresolved findings after rejecting the source-paste composites and replacing the coastal map.

Production archive: `~/.local/state/energy-plus-quest/production/2026-09-05-scene-01/mobile-master-r12/`.

The archive's `runtime-integration.json` records mobile originals, raw generated masters, runtime hashes and the standalone ZIP hash. Separate sea-removal receipts are in `mobile-master-r12-map-repair/`.
