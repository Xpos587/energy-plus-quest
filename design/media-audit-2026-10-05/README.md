# Media framing audit · 2026-10-05

Current review PDF: [energy-plus-media-crop-v2.pdf](energy-plus-media-crop-v2.pdf).

## Coverage

Five baseline viewports: 320×568, 393×852, 820×1180, 1440×900, 844×390.
Additional Petr results: 1024×768, 1920×1080, 2560×1080.

- Initial results: 205 cases / 271 screenshots. Carrier4, compact12, warehouse4, crane12, lastmile9 route cases including the distinct Arseniy helicopter attributes; first/last reader pages and image transitions captured.
- Final results: 214 cases / 280 screenshots, no capture failures, unloaded raster images, horizontal document overflow or offscreen reader controls. Evidence [final-results/results-summary.json](final-results/results-summary.json), [full records](final-results/results.json).
- Other media: 394 captures of intro, setup profile/recipient/gift combinations, choice and inspection screens, and nine ending combinations at five sizes. Evidence [other-report.md](other-report.md), [other-data.json](other-data.json).
- Actual main game, without seeded progress: fresh intro through ending at 1440×900 and 393×852, including flight→ground delivery. 71 captures; no loading, navigation or control failures. [main-flow-report.json](main-flow-report.json).

Identical media routes are grouped: Compact auto equals camera/place3, socks/place3, boat/place4; Express uses crew; warehouse result art is independent of gift; lastmile camera/socks neutral parcel artwork aliases are shared. This is coverage of distinct media/routing, not a claim of every possible Cartesian product.

## Applied

1. Compact: restored outcome close-ups and selected-zone inspection framing that a later CSS rule had overridden. Dedicated boat/place3 illustration retained. Unselected portrait stage follows the truck artwork ratio.
2. Warehouse overview: portrait media row follows native landscape ratio; all warehouse areas remain visible, without unused image bands. Existing accepted result illustrations preserved.
3. Crane overview at small-phone size: source ratio respected; thin unused strips removed.
4. Petr results: wide desktop reader alongside image, preserving workers and gift together; remaining desktop reader height adjusted. No image regeneration.
5. Helicopter to Arseniy: flight framing attribute now applied consistently, preserving rotor and pipe load.
6. Carrier inspection: portrait panel reserve 190→212px; 48px controls retained. All25 carrier/viewport combinations fit after repair.

At tall portrait sizes, surplus height goes to the reading panel. We do not fill it by enlarging/cropping away the scene's action or by inventing background imagery.

## Verification limits

TypeScript passes; all12 existing subject-framing tests pass. Three old journey tests fail before entering setup because their intro navigation no longer matches the current intro. They were not repaired as part of media work; the fresh actual-playthrough harness above verifies the current flow instead.

Illustration ambiguity, not a crop defect: Arseniy helicopter frame visibly depicts pipes but not the selected gift. A gift may be inside the cabin, and the ending shows the selected gift; no requirement for exposed gifts outside Compact has been established. Do not add an unapproved delivery episode or new artwork based only on this ambiguity.

Original screenshots are preserved in results/ and other-shots/. Final result evidence is in final-results/; final choice/inspection fixes in other-after/ and other-carrier-after/. Do not treat initial screenshots as the deployed result.

Final independent visual review: all five baseline result-sheet sets, extra Petr desktop sizes, and choice/preparation/ending sheets checked. No remaining blocking crop or scenario-meaning failures found. Incidental source-edge cuts were distinguished from responsive crop. Arseniy's selected gift is confirmed in the ending; the pipe-only flight frame is an optional clarity enhancement, not a contradictory result.
