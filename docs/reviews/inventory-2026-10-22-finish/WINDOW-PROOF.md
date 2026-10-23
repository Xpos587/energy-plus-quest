# Window surface proof — local comparison only

Review `window-v3-v6-paired-proof.png` at native size or `window-v3-v6-paired-proof-3x.png` for detail. Left is the v3 source crop; right uses the new texture on the same visible glass surfaces. The native texture is unmodified.

All five existing glass meshes retain their original 1.8×1.97 m face dimensions, transforms and vertices. An additive UV layer maps the full texture to each existing panel, with alternate horizontal mirrors. The painted shader uses 72% emission at strength 1.05 and 28% rough diffuse. Fake sky/horizon plates and foliage ellipses are hidden only from camera rays. Frame, mullion, sill, lamp and wall geometry remain unchanged.

Candidate scene: `design/warehouse-finish-2026-10-22/warehouse-window-proof-v6.blend`. It retains the earlier keeper billboard proof. Only a small window-region preview was rendered; no full frame was rendered or promoted.

`window-v6-semantic-mask-render.png` is an actual Cycles visibility render of glass in white and the surrounding geometry in black. The protected comparison copies exact v3 source pixels where this semantic mask is zero; antialiased glass pixels use the candidate. The native texture itself is not edited. This yields 24,641 outside-mask pixels with zero changed channels, recorded in `window-v6-context-equality.json`. Raw regional output remains in `window-v6-native-render.png`, including disclosed unrelated Cycles crop/denoising differences.

The requested crop was [660,96,833,322]. Saved float32 render borders produce actual source coverage [660,97,832,323], 172×226 pixels; comparison uses that measured coverage rather than stretching context.

`window-surface-v6.json` records exact pane transforms, dimensions, UV mapping and the zero-change geometry check against v5. `geometry-preservation-window-v6.json` independently compares the candidate with immutable v4 original meshes and cameras.
