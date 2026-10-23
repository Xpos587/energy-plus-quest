# v16 partial technical proof

- Video: `fleet-v16-behavior-proof-8s.mp4`, 192 separately evaluated frames, 24 fps, 8 seconds, 1920×1334. Exact render snapshot: `fleet-v16-motion-render-source.blend`.
- Final static source: `fleet-v16.blend`; separately retimed final source: `fleet-v16-motion.blend`.
- Five-page review: `energy-plus-fleet-v16-technical-proof.pdf`.
- Recovered detailed red/yellow upper cabs, original approved UVs and crew image, clean lower chassis. Shader framing only changes bright fringe below windshield faces; image assets untouched.
- Smoke is lower-opacity volume with procedural density variation and height fade. Its shape is static relative to the pipe.
- The video snapshot retains a wider lower windshield gasket; final static source restores the narrow gasket. Small white corner fragments remain unresolved. The PDF discloses both differences.
- This proves detail recovery and the short paired-root speed experiment. It does not prove that old/new age distinction is artistically resolved or approved.
- Video verification: ffprobe192 frames/24fps/8.000s/1920×1334; full ffmpeg decode exited0. Frames96/192 inspected. PDF page5 rendered and inspected.
- No production assets replaced, no full48-second animation generated.
