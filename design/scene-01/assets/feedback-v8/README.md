# Feedback V8 living carrier diorama

V8 replaces the static four-truck illustration with a layered interactive
diorama. The client meeting requires the player to understand the choice before
reading the labels: distance, speed, technical age, two drivers and Express must
be visible in the scene itself.

## Production model

1. Start from the accepted V7 three-quarter winter scene.
2. Remove each baked-in vehicle through local, context-rich Qwen inpainting.
3. Generate the two vehicles that were too small or occluded as isolated
   high-resolution reference edits on a cyan key background.
4. Segment or key the vehicle layers and keep them independent from the city.
5. Generate mobile as a separate empty-road camera of the same district.
6. Place the four vehicle layers on perspective-correct road zones in React.
7. Use restrained vehicle motion, road traces and snow/light trails to express
   state; labels only confirm what the image already communicates.

## Accepted generation record

- Remove old truck: Qwen chunk inpaint seed `26082431`.
- Remove near truck: Qwen chunk inpaint seed `26082432`.
- Remove crew truck: Qwen chunk inpaint seed `26082433`.
- Remove Express truck: Qwen chunk inpaint seed `26082434`.
- Isolated old truck: FLUX.2 edit seed `26082441`.
- Isolated near truck: FLUX.2 edit seed `26082442`.
- Empty mobile camera: FLUX.2 edit seed `26082451`.
- Remove accidental mobile background truck: Qwen chunk inpaint seed
  `26082452`.

The reproducible runner is `scripts/media/carrier_art_pipeline.py`. It now
supports box-and-point SAM 3.1 segmentation, EVF-SAM text segmentation,
rectangle-mask creation, largest-component cleanup, object removal, isolated
layer extraction and the existing compose/inpaint/outpaint commands.

## Lessons

- Text-only GroundingDINO segmentation is unreliable for small painterly
  vehicles.
- SAM 3.1 becomes much more reliable when the box coordinates use the original
  image size while positive points use the model's normalized 1024x768 working
  canvas.
- Objects touching buildings or roads produce dirty masks even with SAM. For
  these, generating an isolated reference-matched object is cleaner than trying
  to repair a contaminated cutout.
- General object-removal models may distort illustrated geometry. Local masked
  inpainting with ample context better preserves the art direction.
- A static full-scene image cannot express different speeds convincingly.
  Independent sprites and motion layers are required for this gameplay beat.
