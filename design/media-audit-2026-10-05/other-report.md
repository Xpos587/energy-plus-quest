# Intro, preparation, choices, inspections, endings audit

Live main-game route http://127.0.0.1:4173/. Five viewports: 320×568, 393×852, 820×1180, 1440×900, 844×390. 394 screenshots. Seeded real persistence, then clicked real briefing and inspection controls. No app edits. Existing DEV red-gap diagnostic preserved.

Coverage: intro pages; profile choice; both sender variants on recipient choice; three recipient variants on gift choice; carrier briefing/choice and all five inspections; compact briefing/choice/five inspections; inventory all three gift-letter contexts; crane all three gift contexts; lastmile Alva and Arseniy context branches; every one of nine recipient/gift endings. Reused layouts only where art is context-independent.

## Findings

- Compact at 393×852: image occupies y135.78–466.04 inside y48–553.81 media frame. Red full-width bands y48–134 and467–553, 20.42% entire viewport. Same in every inspection. At 820×1180 bands y48–148 and839–939, 17.12%. Actual SVG image is `/compact-art/compact-environment-v26-portrait-v2.png`, `preserveAspectRatio="xMidYMid meet"`. SVG viewBox expands to 1040×1338.54 /1040×1131.32 but image remains 393×330.26 /820×689.12, so unused space is geometrically explicit.
- Inventory at 393×852: bands y48–136 and465–553, 20.89% viewport. At820×1180 bands y48–126 and861–939, 13.39%. All gift variants/inspections affected. `/scene-art/inventory-master-v4.webp` natural1672×941; at820 image x−243.33,width1304.05,y127.03,height733.91. Vertical blanks coexist with horizontal clipping. In entrance inspection the entrance zone is largely off left; keeper at right is clipped. Selected pins remain near edges rather than bringing the chosen subject clearly into view.
- Crane at320×568: two4px red horizontal strips y48–51 and274–277 (1.41%). Same for all gift variants. At393 a small corner sliver can occur, rather than broad bands. No broad red blanks at1440 or844.
- Carrier crew inspection at320×568: footer back/confirm controls y531.67,h48 => bottom579.67 (11.67px below viewport). Other labeled controls fit within2px tolerance. At820 carrier inspection controls end at1181.19, a1.19px fringe.
- Intro/preparation and all45 ending captures show recipient and gift subjects without destructive crop; layouts remain readable. Carrier inspections keep the selected truck recognisable. Desktop/landscape remaining scene choices retain the main action, though some wide surrounding world is naturally cropped.

## Evidence

- `other-data.json`: all394 captures with currentSrc, natural dimensions, image rectangles/fit/position, button rectangles, horizontal overflow.
- `other-world-geometry.json`: actual SVG/image/world geometry at all five viewports for compact/inventory/crane/lastmile.
- `other-red.json`: exact #ff5252 diagnostic pixel counts, bounding boxes and >80%-width row bands for each affected screenshot.
- `other-shots/`: full screenshots.
- `other-sheet-{width}-{offset}.jpg`: alphabetically grouped labeled contact sheets.
- `other-contact-{width}-{offset}.jpg`: capture-order contact sheets.
- `other-audit.mjs`, `other-geometry.mjs`, `other-red.mjs`, `other-contact.mjs`: reproducible harnesses.

Caveat: document.images also includes hidden header popover images; their large rectangles must not be mistaken for visible media. The world geometry supplement covers SVG media absent from document.images. No screenshot was taken from scenes.html.

## Implemented follow-up: warehouse/crane choice framing

Changes limited to `WorldArt.module.css` (crane image fills one-pixel intrinsic-ratio fringe) and a narrowly scoped appended choice/inspection block in `SceneInteraction.module.css` (portrait warehouse native landscape ratio; short320px crane native landscape ratio). No result rules or TypeScript changed.

Validation: original warehouse geometry assertion failed at320/393/820 before change and passes after.50 fresh screenshots cover inventory/crane choice and all4 inspections at all5 requested viewports. Exact diagnostic red pixels:0 across all50; confirmation/back control overflow:0 across all50. Inventory media now matches image rectangle within1px at all3 portrait sizes, preserving entrance/keeper scene edges. Screenshots `other-after/`, geometry `other-after.json`, labeled sheets `other-after-{width}.jpg`. Original geometry retained as `other-world-geometry-before.json`.

Tradeoff: portrait warehouse uses a short landscape image so all warehouse zones remain visible; remaining portrait height is narrative/control space. No generated fill or artwork changes were introduced.

Compact unselected-choice shell follow-up: portrait stage uses1040/874 native aspect with a300px control reserve for the shortest screen. Five fresh viewport captures have zero diagnostic red pixels and no overflow. Visual review caught320px option/footer overlap with an initial240px reserve;300px reserve resolves it while preserving the full truck. Files `other-compact-choice-after.json` and `other-after/{width}-compact-choice.png`. Compact inspection, briefing, result and art files remain outside this lane.

Carrier inspection follow-up: only portrait carrier camera-inspection reserve changed from190px to212px; button sizes remain48px and no overflow hiding added. Before-check reproduced320crew11.67px footer overflow and820camera inspections1.19px overflow. After-check covers all5 inspections × all5 viewports (25 fresh captures), zero button overflow with0.5px tolerance. At320crew buttons now occupy y510–558, fully visible with10px bottom space. Evidence `other-carrier-before.json`, `other-carrier-after.json`, screenshots `other-carrier-after/`, harness `other-carrier-verify.mjs`. Result rules untouched.

## Final real main-game journeys

`main-flow.mjs` completed fresh browser contexts at1440×900 and393×852 from intro through setup, carrier and allfour remaining scenes to ending. No localStorage injection or persistence seeding. Actual clicked route: professional→Alva→boat→crew→compactplace3→inventoryalphabet→cranePetr→lastmilehelicopter. Desktop35 screenshots; phone36 screenshots, covering every briefing/result page. Both helicopter flight and ground-delivery legs observed in both runs. Every checked visible control fits; images decoded; no horizontal overflow, page errors or failed network requests. No flow blockers found. No app edits or test edits for this verification.

Evidence: `main-flow-report.json` with per-phase image/control state and delivery leg; screenshots `main-flow/`; completed ending files `1440-34-ending.png` and`393-35-ending.png`.
