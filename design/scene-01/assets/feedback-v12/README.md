# Feedback V12 production record

Generated for the 3 September 2026 press-office review package, then expanded after review to keep every carrier outcome in the same approved early-autumn metropolitan logistics world. No older outcome raster is imported at runtime.

## Production assets

| Runtime file | Intrinsic size | SHA-256 |
| --- | ---: | --- |
| `production/choices/professional.webp` | `1536x1920` | `9bb526441be4c1a85cf47ec605ef7cdca59afb97f0bc92c3aeef0d32261f2633` |
| `production/map/carrier-desktop.webp` | `2880x1800` | `e907ab308a8e988e49abf9c3f17f09a0f8b369043b85cbc82b6a43f07d55085c` |
| `production/map/carrier-mobile.webp` | `780x1688` | `bc18cdb813e45fc0f6ced04b8398a1fddb7e1aa971aab7037a5cd7d81b07a5c4` |
| `production/outcomes/old-desktop.webp` | `2880x1800` | `8b31507ae94d810970af1fe802c7d9355c250c8aba959868e2956ad8a6ae9f1a` |
| `production/outcomes/old-mobile.webp` | `780x1688` | `3ef94df6069afe4d5d567c0bd53394047c067a0614be6cf26fd74edecf2418c7` |
| `production/outcomes/near-desktop.webp` | `2880x1800` | `a2c244998915d5a6540d7805a390e34ca4f2051d35583c65a25a6f98e1f4c291` |
| `production/outcomes/near-mobile.webp` | `780x1688` | `11fceecf3621ba8447139ec370b214152ed8aef987df75e0f7119b8ac4193eca` |
| `production/outcomes/crew-desktop.webp` | `2880x1800` | `138254e9cf195132fedf0eb8e1e7a4761dbebc23447c4cbdaad9b647ba831f9d` |
| `production/outcomes/crew-mobile.webp` | `780x1688` | `1e27af8c02937e54017783037b8cdd5464503e0d41758d4d87e77b48887dc693` |
| `production/outcomes/express-desktop.webp` | `2880x1800` | `e822306cac7889f028628daf3f32e6ab5ae9516a22be996f62bc04302fd130e6` |
| `production/outcomes/express-mobile.webp` | `780x1688` | `724fda5e1a0f2b1e22c373f078c1886176aa4f084b5c425d64c16df5150a72a7` |

Lossless PNG masters are under `masters/`; runtime files are visually inspected WebP exports at quality 92. Provider-aligned outputs (`2880x1792` and `768x1680`) are normalized to the contracted dimensions before WebP encoding.

## Outcome continuity

- `old`: the same older blue-grey truck receives a responsible technical inspection; the parcel stays safe and the delay remains the consequence.
- `near`: the approved modern teal truck progresses slowly from the warehouse.
- `crew`: the deep-blue truck travels the wide route with exactly two visible adult drivers.
- `express`: a newly assigned teal truck leaves the modern dispatch gate with exactly two drivers, one worker, and the secured parcel.
- Every desktop composition reserves the right 40 percent for HTML copy; every mobile composition reserves the lower 50 percent.
- All outcomes use the same warehouse identity, early-autumn palette, warm daylight, modern city edge, and paper-gouache rendering.

## Prompts and receipts

Every generation call used `fal-ai/gpt-image-2/edit`, opaque background, high quality, high input fidelity, one image, and requested PNG output. Exact prompts, source hashes, provider responses, candidates, masks, and output hashes are retained.

| Outcome pass | Prompt | Candidate | Receipt |
| --- | --- | --- | --- |
| old mobile | `prompts/old-mobile.txt` | `candidates/old-mobile-01.png` | `receipts/old-mobile-01.json` |
| old desktop | `prompts/old-desktop.txt` | `candidates/old-desktop-01.png` | `receipts/old-desktop-01.json` |
| crew mobile | `prompts/crew-mobile.txt` | `candidates/crew-mobile-01.png` | `receipts/crew-mobile-01.json` |
| crew desktop | `prompts/crew-desktop.txt` | `candidates/crew-desktop-01.png` | `receipts/crew-desktop-01.json` |
| express mobile | `prompts/express-mobile.txt` | `candidates/express-mobile-01.png` | `receipts/express-mobile-01.json` |
| express desktop base | `prompts/express-desktop.txt` | `candidates/express-desktop-01.png` | `receipts/express-desktop-01.json` |
| express duplicate cleanup | `prompts/express-desktop-cleanup.txt` | `candidates/express-desktop-02.png` | `receipts/express-desktop-02.json` |
| express parcel cleanup | `prompts/express-desktop-parcel-cleanup.txt` | `candidates/express-desktop-03.png` | `receipts/express-desktop-03.json` |

The selected Express desktop master is candidate 03. Candidate 01 is retained as rejected provenance because it duplicated the worker; candidate 02 removed the duplicate before the bounded parcel repair. Cleanup masks live under `guides/`.

## Input references

- V12 map candidates define the logistics-centre architecture, city, palette, light, and truck families.
- V12 `near` candidates define the approved result composition and paper-gouache treatment.
- Each mobile outcome is generated as its own portrait composition; desktop is an art-directed outpaint rather than a crop.
- Original professional, map, and `near` prompt/receipt records remain unchanged.

## Deterministic gates

- `guides/layout.json` records the map geometry and outcome mapping.
- `guides/production-contact-sheet.png` covers the professional, map, and all four responsive outcomes.
- `python3 -m pytest scripts/media/test_feedback_v12_assets.py -q` checks the exact runtime file set, formats, and minimum dimensions.
- Playwright verifies that every outcome imports V12 desktop and mobile sources.

## Visual QA decision

Accepted for integration: all four outcomes now remain in the same present-day early-autumn logistics centre. There is no snow, village, retro settlement, generated copy, decorative traffic, or duplicate subject in the selected production masters. Narrative subjects stay outside the shared desktop and mobile copy zones.
