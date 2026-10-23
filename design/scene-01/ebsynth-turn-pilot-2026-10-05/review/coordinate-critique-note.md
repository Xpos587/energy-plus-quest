# Coordinate-transfer review: FAIL

Local-only verification of `transfer-coordinates-map.mp4` and `transfer-coordinates-turn.mp4`: 72 frames, 12 fps, six seconds. I inspected an 11-frame contact sample at frames 0, 9, 17, 18, 27, 36, 45, 53, 54, 63, and 71, with enlarged adjacent comparisons for 17→18 and 53→54. No Gemini call was made for this version.

The coordinate refinement visibly improves the white trailer roof near the end: frames 54, 63, and 71 are much cleaner than the prior three-key transfer, without the large gray/blue roof patches. This does not clear the gate because the tractor still changes identity at both key boundaries.

- `00:01.417 → 00:01.500` (17→18): the softly painted lime cab abruptly becomes a darker, sharper, more front-facing cab with a large near-black windshield. Roof shape, window treatment, front mask, and trailer wheel/edge rendering change together. Motion and background remain continuous, but the vehicle design does not.
- `00:04.417 → 00:04.500` (53→54): the trailer roof now stays acceptably white, but the cab changes from a lighter green top-down form to a darker detailed front with a strong dark rectangular area appearing immediately below/ahead of it. This remains a conspicuous key seam.
- Across the 11-frame path sample, there is still exactly one green tractor and one white trailer, the hitch remains connected, and the rig completes the intended articulated turn. No duplicate vehicle or roof-riding person is visible.
- Two drivers are not readable at this map scale. Frame 17 contains tiny colored cab detail, but it is insufficient to count or locate two people reliably; later windshields are dark and opaque.

Gate result: **FAIL** for temporal stability, consistent bright-clean 2D vehicle styling, and readable two-driver detail. **PASS** for one tractor/one trailer, connected articulation, the 90-degree route, and no visible duplicates or roof-driving in the inspected coverage. The cleaner trailer roof is a real local improvement, but it does not resolve the cab seams.
