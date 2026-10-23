# Fleet cardinal map candidates

Built-in image_gen edits of green cardinal maps using canonical red/yellow truck references. Candidates only; no paid video jobs or production wiring.

| Direction | Red | Yellow |
| --- | --- | --- |
| UP | red-key-0.png | yellow-key-0.png |
| LEFT | red-key-1.png | yellow-key-1.png |
| MID TURN | red-key-1p5-local-repair.png | yellow-key-1p5-local-repair.png |
| DOWN | red-key-2-local-repair.png | yellow-key-2-local-repair.png |
| RIGHT | red-key-3.png | yellow-key-3.png |

Full-map inspection: one truck per image, cardinal pose/center/footprint visually match their green target. Red cab and blue-fastened cream curtain trailer differ from older yellow cab and ribbed cream trailer. Bright colors and map framing retained. Background preservation is visually checked, not claimed pixel-identical to green sources.

DOWN images initially retained two heads. Two full-map repair attempts failed. Successful correction used image_gen on an 8x cab crop, then pasted only its generated windshield interior into the original candidate: rectangle 34x17 at x781, y459. Source patches are *-down-ai-cab-patch.png; native patches *-down-ai-window-native.png; final 8x readbacks *-down-inspection-final.png. Final readbacks show one screen-right driver and empty screen-left passenger seat.

DOWN files without local-repair remain rejected evidence. The misleading *-single-driver-v2.png files still contain two heads and must not be used.

UP windshield occupants are hidden by overhead rear view. LEFT/RIGHT windows have no visible duplicate human clusters at map resolution.

Initial source paths and exact prompts: source-copy-receipt.json. Successful DOWN repair source/prompt and assembly: repair-copy-receipt.json.

MID TURN added from green key-1p5.png with cab/trailer articulation retained. Raw red mid had its sole person on passenger side; yellow raw mid had two heads. Crop-first image_gen repair placed one screen-right driver beside visible side door and emptied screen-left passenger area. Only a native windshield polygon from the generated crop was pasted back at review-crop origin x750,y155. Final crop readbacks are *-mid-inspection-final.png; they pass one-driver gate. AI source patches and native masked patches are retained. MID paths/prompts/polygons: mid-copy-receipt.json.

Selected loop order: key-0 -> key-1 -> key-1p5-local-repair -> key-2-local-repair -> key-3 -> key-0, separately per color.
