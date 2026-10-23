# Runtime art coverage correction

Root cause: both main game and scene showcase use ScenesGame, but new lastmile images were gated to boat + Alva. Other eight contexts deliberately loaded legacy v9/v3 art. Fixed resolver and WorldArt now use the current family for every valid context; scenario-specific drone versus rover transfer is retained.

Choice: approved boat/Alva wide/tall v2 retained. Other contexts use `choice-neutral-wide-v1.webp` and `choice-neutral-tall-v2.webp` under `public/scene-art/lastmile-family-v1/`. Neutral scenes replace visible gift with shipping carton and omit Alva, preserving vehicles/geography/pipe load.

Outcomes: boat robot and boat pipe-carrier shared across recipients; boat/Alva rover and ground helicopter retained. Other variants use `rusak-parcel-result-v1.webp`, `robot-parcel-result-v1.webp`, `helicopter-ground-parcel-result-v1.webp`, `pipecarrier-drone-result-v1.webp`. Arseniy helicopter uses flight only. Remote recipients have flight then ground delivery tied to text pages.

Generated with built-in imagegen. Prompts requested only local cargo replacement, recipient removal where inappropriate, and drone transfer for nonboat pipe-carrier. Existing vehicle/camera/environment/style invariant; robot must remain visibly sunk with taut rescue cable. Tall parcel residual was removed through a 245×195 crop at x0/y620 and composited back; no full rerender for cleanup. Files are versioned; originals retained.

Warehouse PPE corrections documented in `../warehouse-outcomes-2026-09-28/ppe-v10-receipt.md`. Runtime nonboat assets now use entrance/keeper v11; WMS/alphabet camera/socks v10. Boat family retained.

Verification: resolver matrix and file existence checks for all nine parcel/recipient contexts; 26 tests across artwork, boatArtwork, alphabet, crane family passed. Independent reviewer found no severe neutral-art scenario contradictions. Main `/` manually inspected with socks/Khor and confirmed actual new warehouse src. This exposed a desktop-specific contain override in SceneInteraction, missed by element-box measurements; UX agent removed it and added computed-fit assertion. Head-safe framing also required after cover. Full UX coverage lives in `.tmp-work/ux-matrix/coverage-report.json`; geometry checks are not equivalent to artistic approval of every image.

No scenario text/scores changed by this art work. No external deployment.
