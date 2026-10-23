# Full-turn budget experiment — 2026-10-04

User requested a cheap complete turn test, explicitly deferred truck redesign and detailed driving engineering. This is an experiment, not a production asset.

Source: ../route-preflight-2026-10-04/map-v16.png, user accepted style basis. start.png is a crop x620,y180,w650,h488 resized to960×720. No redesign or new static image generation.

Provider: Higgsfield, seedance1_5, requested8seconds/480p/4:3/audio false. Prompt in prompt.txt; returned job in result.json. Output turn.mp4: measured8.041667seconds,752×560,24fps. Estimated4.8credits, actual transaction debit2.4credits at2026-10-04T15:04:47.247524Z; account balance before959.7credits. Previous experiments are not included in this cost.

Local inspection: extracted16frames at0.5second intervals; contact.png displays them. Full real-time playback was not verified. Red truck exits right; green travels down, turns toward screen right around3–4.5seconds, then straightens around5seconds. The articulated motion is weak: the rig appears to rotate nearly rigidly, with unstable perspective/length. At about5.5seconds another green tractor appears and a duplicate rig proceeds up the right street while the original remains on the horizontal road. This FAILS identity/count continuity. Do not hide failure by trimming the delivered source clip.

Conclusion: cheap image-to-video can illustrate a complete turn but this start-only trial does not establish a reliable method for a four-truck seamless loop. Next bounded experiment should use explicit end frame after straightening, or a geometric motion guide, before spending on four simultaneous trucks. No production files changed, no further paid trials launched.
