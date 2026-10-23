# Barge choice V4 — 10 October 2026

Applied in the main local game. Runtime art remains v5; UI revision V4.

Canonical option order: remote, rush, wait, petr. Displayed numbering matches left-to-right scene positions (1, 2, 3, 4). Action ids, scenario paragraphs, scores and outcomes remain authoritative in crane/index.ts.

Removed ambiguous action icons in barge cards; retained simple numbered badges. Removed the shared pale marker backing. Removed the isolated Petr label: all on-image markers now use numbers alone; names and actions remain in the choice cards. Selected physical silhouette uses warm 10% fill, 1.6 px stroke, and a light 4 px understroke. Rush shows the office-to-crane route. Petr inspection aligns the existing image right to keep the whole far crane inside the viewport.

Verification: 23 focused tests passed; TypeScript passed; five runtime viewport captures with no horizontal overflow or page errors; 25 interaction checks passed after the final crop/style adjustment. Final captures verify selected emphasis on five viewports. Independent reviewer rechecked the final mobile/desktop captures and found no critical issue in scope.

Review PDF: energy-plus-barge-choice-v4.pdf.
