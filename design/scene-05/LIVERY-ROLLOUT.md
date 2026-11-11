# Scene 5 — helicopter livery rollout

## Approval boundary

Michael approved the **rounded white «3» direction** shown in `heli-figure3-review.jpg`. The straight white band (D) remains rejected. Approval covers direction, not automatic publication of every derivative.

The coordinator, using Michael's delegated review authority, **approved R3** after viewing the 1440×900 and 390×844 maps and the wide-livery close-up. The forest, trail, greeter, upper-left chums, empty second pad, rig, deer and curved white «3» are accepted. During rollout, make only the requested local glass correction: the wide-map helicopter's two portholes must be dark and crisp, without the washed-grey dotted halo. Camera and foreground vehicle placement stay unchanged.

Map review must show a narrow flowing creek (not a lake), uncropped upper-left chums, the same white/blue/orange dorm palette in both formats, deer inside the mobile frame, and the approved helicopter marking. Keep the distant lattice drilling rig. **The latest review supersedes the earlier tundra/no-greeter interpretation:** preserve the original dense spruce/larch forest outside local clearings for new elements, the greeter near the dorm, and the muddy trail with its bog interruption from commit `65be6e9`. R2's wide-map livery was rejected as pasted/blocky with orange porthole rings; its replacement must match the tall reference's smooth painted curves, natural portholes and fuselage shading. The earlier no-propagation gate is now satisfied. Local rollout is authorized; commit still requires the coordinator's completed rollout review **and explicit “index free”**. `media-artifacts.json` must remain unchanged.

## Live asset inventory

Paths below are relative to the checkout. Resolver evidence: `src/scenes/lastmile/artworkFamily.ts:16–37`.

| Family | Exact paths / expansion | Selection |
| --- | --- | --- |
| Four flight screens | `public/scene-art/lastmile-family-v1/revision-18/flight-{boat,parcel}{,-arseniy}-tall.webp` | Boat vs parcel; only Arseniy has a separate suffix. Tall masters also cover desktop result blocks. |
| Six choice maps | `public/scene-art/lastmile-family-v1/revision-18/choice-{wide,tall}-{alva,arseniy,khor}.webp` | Aspect ratio and recipient. Wide/Alva also appears in the intro route panel. |
| Route illustration | `public/opening/route-v1/lastmile.webp` | Shared route artwork. |
| Stage icon — excluded from edits | `public/opening/stage-icons-v1/lastmile.webp` | Michael explicitly requires the original toy-style progress icon unchanged: no «3», no rotor repaint. |
| Intro cover | `public/scene-art/lastmile-family-v1/revision-15/intro-wide.webp` | Live cover per `src/scenes/artwork.ts:11–14`; not an image under `public/opening`. |

Michael subsequently included the legacy Khor/Alva helicopter **ground-result** images in the approved rollout scope: `helicopter-ground-khor-{boat,parcel}-v6.webp`, `helicopter-ground-boat-final-v5.webp`, and `helicopter-ground-alva-parcel-v6.webp` in the family root. These four actual images contain a truck and recipients, **not a helicopter**. After viewing the inventory, the coordinator explicitly confirmed **retain all four as-is; no ground-scene replacement**. The review inventory remains **17 live images**, with **12 edited, 4 marked “no helicopter → unchanged”, and the progress icon unchanged by Michael's explicit correction**. Report their runtime use separately without changing the two-leg delivery flow.

## Smallest safe rollout

1. R3 map + one-flight gate accepted. Snapshot all 17 originals and SHA-256 hashes before local media changes.
2. Apply the approved contour to the four flight masters and six choice maps, including the local wide-map glass correction. Preserve recipient-specific cargo, doors, sling, load and object geometry. Do not copy Alva's entire map over other recipients. Retain the four non-helicopter ground results unchanged.
3. Adapt that same marking to the route illustration and helicopter region of the intro cover. **Do not edit the toy-style progress-bar icon.** Review small-size readability and check that no unrelated cover/vehicle pixels change.
4. Recheck real runtime choice, flight and legacy-ground rendering at **1440×900 and 390×844**; deliver all 17 before/after comparisons and SHA-256 inventory. Keep resolver paths unchanged. Validate original dimensions and decoded geometry, then run typecheck and the tests below.
5. Commit only accepted authored source/review paths. Binary media follow `docs/REPOSITORY-HYGIENE.md`; do not stage them. Coordinate any later media-manifest publishing separately. **No push, deploy or release upload is authorized.** Never include other lanes' dirty paths, `scripts/deploy-dokploy.mjs`, or `docs/reviews/grisha-call-*.md`.

Checks: `bun run typecheck`; `bun run test -- src/scenes/lastmile src/scenes/artwork.test.ts src/scenes/SceneOutcomeArt.test.tsx src/components/GameIntro.test.tsx`; unchanged-camera browser review at both requested sizes; `bun run clean:stale`; `bun run check:storage`.

## Current review sources and skills

Current rollout package: `.tmp-work/scene5-1011-rollout/`; approved map inputs remain in `.tmp-work/scene5-1011-r3/`. The original revision-18 maps are the base, with local element patches rather than a regenerated landscape. The approved-direction flight sample is `.tmp-work/scene5-1011/sheets/heli-figure3-review.jpg`.

**Local media applied: 12 edited, 5 unchanged. Coordinator review accepted; explicit “INDEX FREE” granted. The final parcel-glass comparison against untouched neighbours has been visually verified.** [Exact before/after SHA-256 inventory](livery-rollout-inventory.json). The progress icon's original SHA-256 is retained, as are all four ground-result files. `media-artifacts.json` is unchanged; these local edits are not a published media release.

Review sheets in the rollout package: `sheets/all-17-before-after.jpg`, `sheets/runtime-1440x900-before-after.jpg`, `sheets/runtime-390x844-before-after.jpg`, `sheets/wide-dark-glass-detail.png`, `sheets/flight-livery-before-after.jpg`, `sheets/small-livery-before-after.jpg`, and `sheets/map-town-after.jpg`. Native-size captures are in `screens/`.

`scripts/capture-lastmile-rollout.mjs` exercised real interactions at both viewports: all six map paths, four flight paths and four legacy ground paths, producing 32 captures. Before images are isolated browser responses; after images are the actual local `public` files. No UI elements are hidden in this check. Captures wait for the initial map, loading-state clearance, all visible image decodes and compositor frames; `capture-paint-check.json` confirms painted artwork within its actual DOM bounds in all 32 screenshots (the earlier three blank parcel captures are superseded). Zero page errors or horizontal overflow; Alva/boat map camera styles match exactly before/after. Raw evidence: `runtime-check.json` and `validation-summary.json`. Earlier R3 art-only captures used `scripts/capture-lastmile-art-review.mjs`, which hid annotations only in its review context.

All 17 images retain their original dimensions; edited candidates were losslessly encoded and checked for exact decoded-pixel identity outside their local edit masks (`locality-check.json`). Typecheck and the seven relevant test files / 46 tests passed. `clean:stale` and `check:storage` passed after rollout.

### Final porthole review

The coordinator accepted the maps, cover, route and five unchanged files, then requested removal of the orange porthole halo in **all four flights**. The correction is limited to `(1052,773)–(1079,799)`: a thin dark frame and white paint continuing to it. Boat flights retain dark-blue glass. The coordinator corrected the earlier dark-blue instruction for **parcel flights**: those two panes must match their untouched steel-blue neighbours; the finisher samples that neighbour's interior colour. All pixels outside that ROI remain identical to the reviewed candidates. The six maps were checked for the same isolated halo and retained unchanged. The single ten-image comparison is `sheets/portholes-10-before-after.png`; its “before” is the reviewed rollout candidate, not the original pre-rollout image. The coordinator approved this sheet and granted explicit “INDEX FREE”, with the parcel-colour correction to be self-verified rather than submitted for another gate. The final two-parcel comparison with each untouched neighbour is `sheets/parcel-neighbour-final.png`.

### Retained authoring source

`scripts/lastmile-livery/` contains the accepted contour/masks (`geometry.py`), R3 shading (`paint-r3.py`), local map composition (`compose-r3.py`), 17-file candidate propagation (`rollout.py`), and the final flight-glass correction plus ten-image review (`portholes.py`). These scripts write candidates and evidence only, never `public` or the media manifest. The rollout includes the final porthole correction and explicitly copies the progress icon unchanged. No rejected straight-D helper is included.

Inputs are **not all reproducible from source alone**. R3 needs the original maps, accepted R2 local-element donor maps, `livery-generated.png` and `dorm-clean-{wide,tall}.png`. Propagation additionally needs the 17 original files and `inventory.json`, plus the accepted boat-flight sample. These generated inputs currently live in the scratch packages named above; preserving these scripts does not make them available after 72-hour cleanup. Current finished media remain at their normal `public` paths, unpublished. No automatic hydration or generation is part of this workflow.

To reproduce with those inputs present, use `uv run --with pillow --with numpy --with opencv-python-headless python` for the R3 scripts and `uv run --with pillow --with numpy python` for rollout/review:

```text
scripts/lastmile-livery/paint-r3.py R3_WORKSPACE ORIGINAL_MEDIA_ROOT
scripts/lastmile-livery/compose-r3.py R3_WORKSPACE R2_WORKSPACE ORIGINAL_MEDIA_ROOT
scripts/lastmile-livery/rollout.py ROLLOUT_WORKSPACE R3_WORKSPACE APPROVED_BOAT_SAMPLE
scripts/lastmile-livery/portholes.py ROLLOUT_WORKSPACE
```

The workspaces must have their input files and `candidates/` / `sheets/` directories. Original media paths inside `ORIGINAL_MEDIA_ROOT` omit the `public/` prefix. Keep `PYTHONDONTWRITEBYTECODE=1` when running these utilities so disposable bytecode is not created beside source. Each generation step checks its local-edit boundaries; new outputs still need visual approval. The retained R3 paint, composition and rollout were executed with the current inputs; the final 17 candidate SHA-256 hashes exactly matched the reviewed outputs (`source-check/result.json`). The final flight pass changed 473 pixels in each boat image and 484 in each parcel image, all inside the same porthole ROI; the other 13 files and media manifest stayed unchanged during that pass (`porthole-public-check.json`).

### Read-only legacy runtime finding

All four `helicopter-ground-*` files are **live after choosing helicopter**, not dead assets. Both requested viewports showed them at `data-delivery-leg="ground"`, beat 1, after the flight beat. Resolver: `src/scenes/lastmile/artworkFamily.ts:32–37`; switching: `src/scenes/SceneOutcomeArt.tsx:51–55,76–81`; authored text: `src/scenes/implementationText.ts:123`. The displayed text explicitly says the workers transport the gift by all-terrain vehicle for at least 10 km after the landing pad. The coordinator confirmed that the truck illustration is consistent with this two-leg sequence, not a bug. No content or flow fix was made.

`finding-skills` was read and installed skills were searched; no additional installation was needed. For R3, the existing `higgsfield` reference-edit workflow supplied a paint-quality reference. Its changed aircraft geometry was rejected: the R3-reviewed local livery kept the original porthole pixels and used smooth reference curves with broad generated shading, without orange cutout rings. The original maps—not AI-regenerated terrain—are the composition base. Separate tent-removal crops were feature-registered to those originals and applied only at the former tents; the surrounding forest, trail and greeter are not generated replacements. `reference-design-contract` was read earlier but its three-document workflow was not applied: the approved brief and latest review already provide the keep/change boundary, and another design-system contract would duplicate it. The rollout reused those accepted contours and local patches with Pillow/NumPy; the explicitly requested wide-map glass correction replaces only the two panes with clean dark glass. No new generation or skill installation was needed during propagation. The read-only Explore lane verified the asset inventory and runtime selection; it did not approve artwork.
