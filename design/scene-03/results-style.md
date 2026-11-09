# Scene 3 results: common game style

Scene 3 result art (10-28) diverged from scenes 1, 4 and 5: saturated electric-blue racks and bright orange,
heavy dark ink outlines, glossy comic rendering, cool light, orange+blue hi-vis suits, and a different face in every picture.

Common denominator of scenes 1/4/5 (scene 2 results are flat diagrams; only palette and thin outline carry over):

- soft painterly 2D, thin colour-matched outlines (not black ink), soft modelled volume, moderate detail;
- warm golden daylight, slightly muted palette: navy/cobalt, warm orange accents, cream walls, light blue-grey floor, yellow autumn foliage outside;
- natural proportions, simple friendly faces.

Cast (same people in every scene 3 result, matches the scene 3 overview):

- worker (entrance, alphabet ×3, keeper): man about 35, short dark-brown hair, neat dark-brown moustache, navy cap;
- operator (wms): younger man, short brown beard, navy cap;
- Pavel Mikhailovich (overview only): grey hair, grey moustache, no cap.

Workwear (PPE) is the company suit of the original 10-28 results and scene 4 (Ivan, Pyotr): cobalt-blue jacket with an
orange yoke, light-grey reflective stripes on chest, waist and arms, orange trousers with blue lower legs and reflective
bands, dark boots. Same cut on everyone. Plain navy overalls without orange read as prison wear — do not use them.
Reference: `results-v2/ppe-ref.jpg`.

Emotion must match the result text (`src/scenes/implementationText.ts`):

- entrance, alphabet ×3 — he ran back and forth across the hall: a kind man who is simply a bit tired. Wipes his forehead,
  light exhale, soft eyebrows, gentle eyes, hint of a smile. Not exhausted, not angry, not gloomy, no frown;
- keeper — the place lived only in the keeper's head: thoughtful, scratches the back of his head, small "hmm". No despair;
- wms — the system chose the spot: calm quiet confidence, focused on the scanner, slight satisfied smile. Not stern.

Pipeline: `results-v2/gen.sh` restyles each current result with image-to-image (composition kept),
`blender-v1/align.py` registers it back onto the original so subject boxes stay valid.
`results-v2/ppe.sh` then changes only the people (PPE + emotion) on that restyle; after `align.py`,
`results-v2/paste-people.py` pastes just the changed figures back so the rest of the picture stays pixel-identical.
`results-v2/alphabet.py` builds the three alphabet variants from one base, differing only in the aisle plaque.
