# Feedback V7 carrier artwork

The V7 carrier scene moves the choice screen from a flat map treatment to the
same volumetric narrative language as the outcome illustrations.

Pipeline:

1. `fal-ai/flux-2-pro/edit` composes a coherent scene from the current carrier
   layout and accepted outcome-style references.
2. Individual problem regions are cropped with context, enlarged and corrected
   through masked `fal-ai/qwen-image-edit/inpaint` passes.
3. Desktop and mobile are treated as separate cameras of the same scene. Mobile
   is not a CSS crop of desktop.
4. Final media is normalized to WebP only after original-resolution visual
   inspection.

The reproducible runner is `scripts/media/carrier_art_pipeline.py`.

Accepted generation record:

- Desktop composition: seed `26082401`.
- Mobile base composition: seed `26082411`.
- Mobile Express insertion: seed `26082421`, chunk `x=420`, `y=105`,
  `width=255`, `height=235`, `padding=96`, `scale=2`.
- Mobile crew-cab correction: seed `26082422`, chunk `x=385`, `y=1060`,
  `width=275`, `height=180`, `padding=96`, `scale=2`.

The chunk workflow keeps the accepted scene intact: crop the target region with
context, enlarge it for the edit model, inpaint only the mask, resize the result
back to the source coordinates and composite it through a feathered mask. This
is preferred to regenerating the full scene when one truck, person or local
detail is wrong.
