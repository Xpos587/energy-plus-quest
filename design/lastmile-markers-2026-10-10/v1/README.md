# Lastmile marker revision V1 — 10 October 2026

Applied in the main game. Canonical artwork remains choice-final-wide-v9.webp and choice-final-tall-v9.webp; no image regeneration.

Small square 20 px markers (24 px on desktop) share the warehouse/barge visual treatment and keep 44 px touch targets. Hotspots are adjacent to vehicle edges; robot's old vertical offset is reset. Numbers and option IDs remain helicopter 1, rover 2, robot 3, pipe-carrier 4.

MobileSAM vit_t masks use full-image coordinates in LastmileZones, outside WorldArt's original-image remapping container. Hover/focus or selection highlights the transport; idle state has no contours. Selected masks use 10% warm fill with restrained 1.6 px stroke and white understroke. The helicopter uses its body/tail silhouette, excluding the landing pad; fine rotor blades are not included. The full robot silhouette includes tracks.

Actual main-game review: five viewports (320×568,393×650,393×852,820×1180,1440×900), four selected options each, no page errors or horizontal overflow. Twenty direct-object click checks passed. Touch target and selected visibility checks passed. TypeScript passed; 29 focused scene/scenario tests passed. Independent read-only reviewer inspected final mobile and desktop screenshots and found no blockers in scope.

Review PDF: energy-plus-lastmile-markers-v1.pdf. Source prompts and masks: segment.py, segmentation-receipt.json, masks/. Screenshot receipt: check.json; runtime script: capture.mjs.
