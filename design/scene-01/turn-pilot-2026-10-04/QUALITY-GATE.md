# Video acceptance gate

Current turn.mp4 is REJECTED. A completed generation is not a reviewed candidate. User should not be the first defect detector.

Before showing another animation candidate:
1. Analyze the actual complete video with analyzing-videos/Gemini; request timestamped evidence covering turns and the ending. User authorized Gemini processing in conversation. Delete remote upload after analysis.
2. Independently inspect sampled frames, increasing sampling around suspected defects. A model PASS cannot override visible failure. Record contradictory model output as unreliable, not evidence of success.
3. Tractor leads; trailer pivots at hitch with distinct headings during turn and follows a narrower path. No rigid whole-truck rotation, lateral skating, rubber trailer or hitch separation.
4. Track each original cab and trailer across the entire clip: no duplicates, splitting, disappearance or replacement.
5. For final full-map footage, all four trucks remain on their defined routes and within map boundaries. A cropped pilot cannot establish full-map route containment; exiting a crop is not proof of leaving the map.
6. Fixed background/camera, wheels on asphalt, no curb/building penetration. Final loop additionally needs matching start/end state and velocity.
7. Fail any hard condition => keep internal, provide concise failure/cost status rather than presenting as progress ready for acceptance.

This pilot fails steps3/4, and never tested all four routes or loop. First Gemini2.5Flash pass incorrectly reported stable count and correct articulation; contradicted by visible duplication at~5.5seconds. Never accept that report as ground truth.
