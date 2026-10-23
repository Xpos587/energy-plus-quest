# Live scene 1 production

Approved direction: retain pass18 illustrated environment with local removal of baked vehicles/shadows; use heading-correct Blender-derived vehicle views and articulated runtime motion. Prior review bytes immutable. Parent authorized local clean plate and atlas production on 2026-09-18. No other scenes modified.

- [x] Read complete handoff; trace App -> CityMap/MapNumbers -> reducer -> Outcome -> ScenesGame; snapshot dirty baseline at /tmp/scene1-live-baseline/status.txt.
- [x] Produce clean environment and inked vehicle atlas from saved pass12 source; preserve identities, two crew, remove outcome wordmark locally.
- [x] Implement responsive animated map, moving accessible targets, pause/reduced motion/visibility cleanup; preserve choices and scores.
- [x] Run full-loop route/clearance tests, app desktop/mobile interactions, lifecycle checks, screenshots and motion evidence; inspect actual artifacts.
- [x] Build/types/unit tests; record changed files, no staging, remaining device limitations.

No new dependencies. Runtime is explicitly 2.5D, not native WebGL. Reproducible source assets live under public/scene1-live; generation scripts in this directory.

Final visual gate: parent rejected the first portrait collage and weak vehicle shading. Removed the collage; final phone camera uses the coherent approved city with explicit locate/overview/pan controls and a separate toolbar. Re-rendered ink/shading and cab detail; calibrated gentler curves with full collision tests. Parent viewed v2 and authorized final handoff as an implementation candidate, explicitly not new user art approval. See README.md for commands, evidence and remaining fidelity/device limits.
