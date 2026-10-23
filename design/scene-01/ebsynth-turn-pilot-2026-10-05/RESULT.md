# Turn trial result

Latest deliverables: [moving before/after v2](review/transfer-coordinates-turn.mp4), [map crop v2](review/transfer-coordinates-map.mp4), [PDF v2](review/energy-plus-map-turn-v2.pdf), [preview v2](review/preview-v2.html).

## Decision

The controlled articulated turn works as a structural basis. This texture-synthesis experiment does **not** pass the art/temporal quality gate and is not applied to the game. Adding stable object-local coordinate guides improves trailer-roof cleanliness, but does not eliminate the cab's identity changes between separately painted keyframes. Driver readability at game zoom remains unproved.

Evidence: [initial actual-video and local-frame review](review/critique-note.md), [coordinate-variant local-frame review](review/coordinate-critique-note.md), [Gemini execution/remote cleanup receipt](review/analysis-receipt.json), [roof-only diagnostic](review/roof-diagnostic.json), [coordinate run commands and measurements](transfer-coordinates/timing.json). The coordinate variant was not analyzed by Gemini; its independent check is explicitly local frame inspection.

The roof diagnostic is not a complete animation-quality score. It measures a fixed source-selected white roof region and should not be presented as a general improvement percentage.

No further video-generation jobs, paid purchases, or production replacement are justified by this trial. Before extending the motion to all four trucks, the cab needs one consistent set of surface artwork and readable drivers on its existing shaped geometry rather than independent paintings that disagree between views. The rejected UV-box model must not be revived.

## Repeat

The source geometry, painted keys, guides and runner scripts are preserved in this experiment directory. `tools/run_coordinate_transfer.py --keys style/key-0000.png style/key-0035.png style/key-0071.png` repeats the bounded coordinate trial. `assemble_trial.py` creates the actual moving comparisons, `measure_roof.py` the narrow diagnostic, and `build_review_v2.py` the external PDF. Use the repository's available Python environment containing Pillow/numpy/reportlab for the review scripts; the compiled CPU EbSynth executable is under `tools/ebsynth/bin/ebsynth`.
