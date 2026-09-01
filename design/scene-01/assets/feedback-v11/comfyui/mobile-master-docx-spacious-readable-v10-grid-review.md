# Mobile master grid review: v10

Source: `mobile-master-docx-spacious-readable-v10.png`, reviewed at native 768x1424 and 375px preview. Grid: 3 columns x 6 rows, each native cell 256x237.

## Verdict

Reject. The spacious map improves vehicle readability, but the whole-frame output introduces an accidental fifth blue vehicle-like object in A2 while also retaining Old in A1. This fails the exact-four rule. Do not wire this candidate.

## Block review

| Cells | Review | Correction |
| --- | --- | --- |
| A1 | Old is visible against the upper-left road and has a useful exhaust/track cue. | Keep one Old only; preserve contrast and move it away from the railway edge if needed. |
| A2 | An accidental small blue vehicle appears below the upper building. It is not one of the four anchors. | Remove this object in the next whole-frame generation; no extra traffic or vehicle-like fragments. |
| A3 | Sports block and upper urban context read clearly. | Keep. |
| B1-B3 | Upper residential blocks and road grid read as a real city. | Keep the spacious grid; do not let extra cars appear in courtyards or streets. |
| C2 | Warehouse remains unmistakable and dominant. | Keep one broad warehouse, but retain a practical loading apron. |
| D3 | Near is in the correct right-side loading exit with turn traces, but remains visually too large/long for the lane. | Reduce slightly or widen the exit apron; fully ground it without crossing the junction. |
| E1 | Crew is countable and the two drivers are visible, but it still reads large against the road. | Keep medium readability, align with one lane, and preserve exactly two drivers. |
| F3 | Express is countable and its one wordmark/wake work. | Keep medium readability and localize the wake to the arterial. |

## Product implication

Do not solve mobile usability by inflating trucks inside the art. Keep the vehicle bodies medium and add UI-level 44px+ hit areas/labels anchored to the four art positions. The art still needs exactly four countable trucks; the UI carries tap convenience.