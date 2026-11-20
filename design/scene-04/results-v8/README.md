# Scene 4 — crane result candidates

**Verdict: ready for integration review.** The orange-hatted Ivan and white-hatted, bearded Petr are seated at the barge-crane controls behind the window frame. The ladder foot is empty in every branch. Its two uprights, rungs and repeating cage hoops are distinct; the original gift and barge remain in place. Remote shared the deformed ladder, so it is included: the cab stays empty and Ivan operates from the ПРУ in the views that include it. No paid calls, model inference or runtime edits.

| Framing | WebPs in `candidates/` | Dimensions | Before → after |
|---|---|---:|---|
| Main | `outcome-{rush,petr,remote}.webp` | 3884 × 1618 | [Wide sheet](review/wide-framing.jpg) |
| Portrait | `outcome-{rush,petr,remote}-portrait.webp` | 2048 × 3072 | [Portrait sheet](review/tall-framing.jpg) |
| Rail | `outcome-{rush,petr,remote}-rail.webp` | 1956 × 1762 | [Rail sheet](review/mid-framing.jpg) |

I visually inspected the full comparisons, the native crane sheets and the 300% cab and ladder crops in `review/`. Start with [the rail crane at native pixels](review/mid-crane-native.jpg), [its cab at 300%](review/mid-cab-300pct.jpg) and [its ladder at 300%](review/mid-ladder-300pct.jpg). In Petr’s result his original berth is vacated; the waiting cargo and its original label remain. Fine facial details are small in the full quay view, particularly on phones. The rail framing excludes the office. This is raster review, not a deployed game check.

## Rebuild and checks
Run here, **against the original v7 input WebPs** identified in `review/checks.json`:

```sh
~/.local/share/comfyui/venv/bin/python build.py
~/.local/share/comfyui/venv/bin/python review.py
```

`build.py` uses the current remote still as a clean same-camera donor for the old walker and balloons, the approved v5 painted ladder (`public/scene-art/barge-v5/{desk,tall}/ladder.webp`), and the seated pose from `public/scene-art/barge-family-v1/outcome-remote-neutral-v1.webp`. Petr’s head comes from the current v7 `tall/far.webp`. Instead of re-rendering the quay, it masks the painted operator behind the sill, tints the glazing, restores the vacated stations with local patches, and attaches the reaction to the cab. Structural registration is affine only. Reconstructed paving/shadow brushwork is approximate, not a recovered hidden original.

All 9 delivered WebPs decoded at the original dimensions. The shared ladder patches agree across branches. Outside the declared patch regions, mean absolute RGB-channel change after WebP re-encoding was **0.61–0.81 on a 0–255 scale**. [Checks and hashes](review/checks.json) lists the original and candidate SHA-256 digests, exact sizes and crop coordinates. The global cleanup script was confined to this lane’s directory via a bind mount. No files were staged.

## Why recapturing is not the fix
The shipped v7 stills are DPR-2 end-of-animation screenshots: see `scripts/capture-barge-outcomes.mjs` (`craneDuration(id) - 300` and `page.screenshot`). The historical `design/scene-04/blender-v6/quay.py:745–751,1076ff` outcome poses are **not** their direct source. `design/scene-04/stylized-v7/{compose,stylize}.py` registered the paintings and processed the Blender layers; `design/scene-04/blender-v6/export.mjs` packaged those layers. `design/scene-04/blender-v4/painted/receipts/v4-sprites-desk-checks.json` and commit `af1a589` document the earlier painted family. Running the unmodified capture script would overwrite these candidate corrections.
