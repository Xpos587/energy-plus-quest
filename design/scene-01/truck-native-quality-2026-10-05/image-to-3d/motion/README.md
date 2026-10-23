# Actual articulated motion proof

`green-tractor-turn.mp4`: 6.000seconds,144actualBlenderEEVEEframes at24fps,768×640,H.264. `green-tractor-turn.blend` is the reproducible packed scene. `entry.png`,`apex.png`,`exit.png` are actualrenders; `video-contact-sheet.png` is decoded from the finalMP4 at3fps. No generated frames or video-style transfer.

Source rig: controlled-motion-2026-10-04/v2b/controlled-straight-start.blend. Source interval2–99 stretched acrossoutput1–144. Independent baked tractor/trailer world trajectories resampled before deletion of city/othertrucks. Tractor+alloldchildmeshes/crew removed; separately articulated trailer remains unparented, with its own action. Whole textured tractor Mesh_0 appended from ../green-tractor-finished.blend. Original world matrix baked into its mesh vertices before parenting. Rotation mode explicitly XYZ (GLB's QUATERNION mode ignores Euler assignments),rotationZπ,uniformscale2.2,localfrontX1.48,groundZ0. Parent is truck-3-tractor with identityparentinverse; root scale1.122 retained.

Fixed map camera preserves original map orientation and fits all frames with margin. Clean pale blue ground; white separate semitrailer, retained modeled running gear. Final renderer EEVEE (Blender5.2.2 enum BLENDER_EEVEE), no compositor or sequencer overlays. Initial Cycles diagnostic sequence was stopped after crop/orientation errors; final 144-frame sequence completely overwritten with corrected EEVEE renders.

Verification: ffprobe confirms6.000sec,24/1fps,144frames,768×640. Entry/apex/exit and decoded18-frame contact sheet inspected. `validation.json` records all-frame projected bounds and resampled world-transform errors; `motion-receipt.json` includes every outputframe's source time and separate tractor/trailer transforms.

Limitations: complete tractor is one textured mesh; wheels do not independently rotate. Painted occupants, texture defects and generated geometry remain. Original trailer finishes at173.620° while tractor finishes180° (6.380° residual articulation); this matches the original baked interval, not an invented fully aligned exit. This is a maneuver proof, not a finished game asset.

Re-render packed blend: `blender -b green-tractor-turn.blend -o frames/frame- -F PNG -a`.
Encode: `ffmpeg -y -framerate 24 -i frames/frame-%04d.png -frames:v 144 -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart green-tractor-turn.mp4`.
