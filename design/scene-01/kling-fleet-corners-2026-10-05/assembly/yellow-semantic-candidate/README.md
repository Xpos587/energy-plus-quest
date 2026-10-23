# Yellow semantic layer candidate

Technical candidate only. Native semantic body masks and sourceRGB were preserved, exactly projected, and translated as a rigid layer. Final road/roof placement and actual four-vehicle phase remain pending. Driver count uncertain.

Canonical common output: rgba-frames/0000.png..0545.png; roof-tracking-22.75s.json; composite-22.75s.mp4. Actual full decode:546frames,24fps,1280×720,22.75s. Raw tracking/frames preserved independently.

Yellow1-mid keeps all120 moving source poses. All5×120 gives600raw25s; common546 selects ROUND(i*599/545), preserving both route endpoints and distributing54 dropped poses. No interpolation.

All5 source layers:121frames each, all roof anchor pixels opaque, all21quarter samples per layer viewed with intact cream roof/wheels and no observed attached curb/tree. All546 assembled anchor pixels remain opaque. Native endpoint pairs and8motion samples per seam viewed. Source appearance/sharpness changes at0-1→1-mid and mid-2→2-3 remain, particularly red cab detail; positional alignment cannot repair those without changing source appearance.

Seam report and translation maxima: gate-report.json. Moves are whole-layer translation only, ramps24frames, no scale/rotation/deformation/crossfade/opticalflow. No ground shadow added. Raw source RGB is exact before camera projection/resampling. Road image metrics refer to upper-cab image point, not world or wheel clearance.

Evidence: seams-native.png; seams-motion-contact.jpg; seams-4x-review.mp4 (240decodedframes,24fps,880×720,10s); decoded-validation.json. Source motion reviews live in parent fleet folder. These samples establish mask/body observations, not independent motion or driver-count proof.
