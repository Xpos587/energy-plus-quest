# Scene 3 results: common game style

Scene 3 result art (10-28) diverged from scenes 1, 4 and 5: saturated electric-blue racks and bright orange,
heavy dark ink outlines, glossy comic rendering, cool light, orange+blue hi-vis suits, and a different face in every picture.

Common denominator of scenes 1/4/5 (scene 2 results are flat diagrams; only palette and thin outline carry over):

- soft painterly 2D, thin colour-matched outlines (not black ink), soft modelled volume, moderate detail;
- warm golden daylight, slightly muted palette: navy/cobalt, one warm orange accent, cream walls, light blue-grey floor, yellow autumn foliage outside;
- natural proportions, simple friendly faces.

Cast (same people in every scene 3 result, matches the scene 3 overview):

- worker (entrance, alphabet ×3, keeper): man about 35, short dark-brown hair, neat dark-brown moustache, navy cap,
  navy work jacket and trousers with light-grey reflective stripes;
- operator (wms): younger man, short brown beard, navy cap, same navy workwear;
- Pavel Mikhailovich (overview only): grey hair, grey moustache, no cap.

Pipeline: `results-v2/gen.sh` restyles each current result with image-to-image (composition kept),
`blender-v1/align.py` registers it back onto the original so subject boxes stay valid.
