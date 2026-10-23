# Crop corrections · 05.10.2026

Applied to shared runtime and main game. Warehouse accepted V2 masters unchanged; mobile landscape result window + explicit focus retain workers/WMS. Helicopter flight top-left anchor retains rotor and load. Carrier original mobile masters unchanged; wide-v6 variants used above 900px desktop. New boat place-3 V48 is a separate failure illustration: boat stays outside with puzzled workers, original scenario/scores unchanged. Wide/normal sources selected via picture.

Checks: 21 screen captures across393x852,820x1180,1440x900; 12 subject-bound regression tests passed; boat place-3 inspect/revise/read/continue test passed; tsc passed. Reviewer flagged keeper left hand, then withdrew after source comparison: original image itself ends there, mobile crop preserves full original left edge. No source regeneration for warehouse. Review PDF contains current screens only.

Red diagnostic from src/mediaReview.ts was not disabled to conceal gaps. Fixes affect result frames; unrelated choice layout is untouched. New images are review candidates, not Fedya approval. Existing original assets retained for rollback.
