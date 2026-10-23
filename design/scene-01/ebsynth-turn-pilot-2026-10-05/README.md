# First-map turn experiment

This is an isolated experiment, not a replacement for the live map or a completed four-truck loop.

## Review artifacts

- [Moving comparison](review/transfer-three-turn.mp4): native Blender guide on the left, three painted keys propagated by EbSynth on the right.
- [Map crop](review/transfer-three-map.mp4), [local preview](review/preview.html), [short external PDF](review/energy-plus-map-turn-v1.pdf).
- [Native geometry receipt](geometry/receipt.json), [per-frame transforms](geometry/transform-receipt.json).
- [CPU measurements and exact commands](transfer-three/timing.json).

## Pipeline and evidence

The existing reconstructed curved cab and detailed chassis supply poses and silhouettes. The rejected box-shaped UV pilot is not used. One fixed camera samples a native tractor turn through 90 degrees. The trailer follows its existing articulated rig. The city and other trucks are hidden for guide rendering; the approved city image is later reused without generative edits.

Three painted keyframes use the guide poses at indices 0, 35 and 71. All edits preserve the guide canvas registration. The approved empty map and green-truck result artwork are the style/identity references. Built-in image generation produced the keys; no paid video-generation job or subscription was started.

EbSynth is the author's [open-source texture-synthesis implementation](https://github.com/jamriska/ebsynth), compiled locally for CPU. RGB and world-normal guides control each synthesized frame. The baseline selects the nearest of three keys independently; it has no optical-flow temporal propagation. Consequently, successful decoding and correct rigid silhouettes do not establish coherent faces or textures.

The one-key test visibly damages details across larger changes of view. The three-key test retains the turn but introduces changing pale patches on the white trailer. Stable mesh-local coordinate guides are tested separately to anchor surface locations. The coordinates' alpha channels match the original guide alpha in every frame; see [coordinate receipt](geometry/coordinateframes/receipt.json).

The prototype is only 512 pixels wide per comparison panel, 12 distinct frames per second, six seconds long. It does not establish 4x zoom quality, a seamless loop, four-vehicle synchronization, collision clearance against the illustrated city, or final driver readability. Two painted heads can be inspected in the guide windshield detail; that does not certify two readable faces throughout the transferred video.

## Preserved production state

No runtime video, poster, tracking manifest, gameplay component or approved scene image is changed by this experiment. Runners and receipts remain here so the experiment is reproducible without mixing it into deployment assets.
