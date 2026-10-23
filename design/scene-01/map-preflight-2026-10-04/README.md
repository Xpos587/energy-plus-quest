# Static map preflight — 2026-10-04

Current candidate: map-v10.png; review: map-v10-review.pdf. Not deployed, not animation-ready.

User gate: review actual map at overview and maximum zoom before animation. All trucks must start straight on straight road sections. Existing animated production map remains intact.

Based on style-static-2026-10-02/map-v9.png and actual-truck-refs.png. Generated master returned 1505×1045 despite higher-resolution request; do not represent it as a high-detail 4K master. Corrected blue windshield to one driver, green retains two. PDF crops are direct original-pixel extracts, not separately regenerated details.

Code MAX_MAP_ZOOM=4. Existing production video sources: desktop1008×700, tablet864×600, mobile720×500, 48s24fps. These source resolutions are not adequate evidence of close-up cabin readability.

Review blockers: red/yellow cabin orientation appears inconsistent with trailer axes; drivers cannot be confirmed through small side windows. Building shadows remain harder than desired. Need native detail reconstruction with exact geometry before animation. Do not interpolate/upscale and claim newly resolved details. No paid animation generated.

Next: use exact aligned truck geometry to constrain localized truck reconstruction, then inspect integrated final crops and live viewport zoom. Preserve geography, modern warehouse, road directions and four truck identities. Only after user composition review and detail gate proceed to single animation sample.
