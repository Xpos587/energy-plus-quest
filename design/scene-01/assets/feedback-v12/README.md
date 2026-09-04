# Feedback V12 production record

Generated for the 3 September 2026 press-office review package. V12 contains only the approved minimum: professional, carrier map, and representative `near` outcome. No V11 production raster was copied into this directory.

## Production assets

| Runtime file | Intrinsic size | SHA-256 |
| --- | ---: | --- |
| `production/choices/professional.webp` | `1536x1920` | `9bb526441be4c1a85cf47ec605ef7cdca59afb97f0bc92c3aeef0d32261f2633` |
| `production/map/carrier-desktop.webp` | `2880x1800` | `e907ab308a8e988e49abf9c3f17f09a0f8b369043b85cbc82b6a43f07d55085c` |
| `production/map/carrier-mobile.webp` | `780x1688` | `bc18cdb813e45fc0f6ced04b8398a1fddb7e1aa971aab7037a5cd7d81b07a5c4` |
| `production/outcomes/near-desktop.webp` | `2880x1800` | `a2c244998915d5a6540d7805a390e34ca4f2051d35583c65a25a6f98e1f4c291` |
| `production/outcomes/near-mobile.webp` | `780x1688` | `11fceecf3621ba8447139ec370b214152ed8aef987df75e0f7119b8ac4193eca` |

Lossless PNG masters are under `masters/`; runtime files are visually inspected WebP exports at quality 92. fal.ai aligned some requested sizes to model multiples (`2880x1792` and `768x1680`); masters were normalized by at most 16 pixels to the contracted dimensions before WebP encoding.

## Prompts and model parameters

All exact prompts are stored verbatim under `prompts/`. Every call used `fal-ai/gpt-image-2/edit`, opaque background, high quality, high input fidelity, one image, and requested PNG output.

| Prompt | SHA-256 | Requested size | Candidate | Receipt |
| --- | --- | ---: | --- | --- |
| `prompts/map-desktop.txt` | `b8ec58a7f9c1319b109313b988dbe779fa39bc1af8d5e41cce9488533ddee14c` | `2880x1800` | `candidates/map-desktop-01.png` | `receipts/map-desktop-01.json` |
| `prompts/map-mobile.txt` | `4eb30b1925a1d714dfe1b215633cf725fffaf340f56442d381f783e0bed9a2cc` | `780x1688` | `candidates/map-mobile-01.png` | `receipts/map-mobile-01.json` |
| `prompts/near-desktop.txt` | `ee6d2c5d42b64ebb92609432b782877bdac1142972a6f0c6eb2d7ffa7c7e427d` | `2880x1800` | `candidates/near-desktop-01.png` | `receipts/near-desktop-01.json` |
| `prompts/near-mobile.txt` | `6b30033c63b33013cae68bc24ed51f01d9818e557c48493a396484ef17a7e14c` | `780x1688` | `candidates/near-mobile-01.png` | `receipts/near-mobile-01.json` |
| `prompts/professional.txt` | `26fa40db1cbe1c8c42a953fe47a477e03d704b1c3c4ef740d3e23ccf9bc5c2ee` | `1536x1920` | `candidates/professional-01.png` | `receipts/professional-01.json` |

Receipts contain the endpoint, exact parameters, prompt/input hashes, provider result, candidate filename, and candidate SHA-256. Candidate extensions preserve the requested output name; lossless masters normalize the provider response format.

## Input references

| Input | SHA-256 | Role |
| --- | --- | --- |
| `design/scene-01/assets/feedback-v4/production/choices/student.webp` | `2508b846d8253fe8c9a985e40ef61f8ecff5c5a690650835a537aeb8f3cd25a1` | approved face and paper-gouache style |
| `design/scene-01/assets/feedback-v5/production/choices/professional.webp` | `19eb9ef17be69b851f9cd2dbb041a43c98443bdaf0442b32d905a449821a5f4c` | PPE construction reference only |
| `design/scene-01/assets/feedback-v12/guides/desktop-safe-zone.png` | `c1d987ef631e27ad43d1ce8724444d8fb1eaca06dbd905a3befe0dd1e5d50237` | desktop map geometry and HTML safe zone |
| `design/scene-01/assets/feedback-v12/guides/mobile-safe-zone.png` | `8a1cdb684e41406b914a0a511f94a4b2cb6ecd1a0b3ce7395f38fad5fde98166` | mobile map geometry and HTML safe zone |
| `design/scene-01/assets/feedback-v12/candidates/map-mobile-01.png` | `bdcfa0fdf2cc3a87d7b412821b6df42f6c854105678df97d67e08d614a9a2813` | near outcome world and truck identity |
| `design/scene-01/assets/feedback-v12/candidates/professional-01.png` | `1d8cb527abc708a583ae924d72cd46d7aa6ab487d042cb367cbcb8af4163e3ad` | near outcome human/PPE grammar |
| `design/scene-01/assets/feedback-v12/candidates/near-mobile-01.png` | `fc4ccfc8b7648edd8e6baeaa07ffdf014057293634bc2d4b4ea9daecb2b3109e` | protected mobile-first narrative action for desktop outpaint |
| `design/scene-01/assets/feedback-v12/candidates/map-desktop-01.png` | `1da001b8950478da85feda53c288f50028a261db244ef6f3598b341bd057c361` | desktop world, palette, and logistics-centre continuity |

## Deterministic guides and gates

- `guides/layout.json` records early-autumn setting, connected roads, one logistics centre, four trucks, outcome mapping, cameras, and visibility bounds.
- `guides/geometry-contact-sheet.png` proves one warehouse, connected road network, exactly four trucks, no decorative vehicles, and calm number-anchor space.
- `guides/*-color.png`, `*-depth.png`, `*-canny.png`, and `*-truck-masks/` preserve the generation contract and bounded repair inputs.
- `guides/production-contact-sheet.png` is the five-asset visual QA sheet.
- `python3 -m pytest scripts/media/test_feedback_v12_assets.py -q` checks the exact runtime file set, formats, and minimum dimensions.

## Visual QA decision

Accepted for integration: the professional reads as an experienced woman with complete hands, full-body crop, and coherent PPE; both maps show present-day early autumn, a metropolitan distribution centre, exactly four trucks, no Express vehicle, and clear UI safe zones; the `near` outcome keeps one modern teal truck, parcel, and worker outside the copy zones. Generated numbers and labels are intentionally absent because semantic HTML supplies them.
