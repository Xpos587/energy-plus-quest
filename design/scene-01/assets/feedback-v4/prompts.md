# Feedback V4 media provenance

Generated on 2026-08-20 through fal.ai.

## Model family

- Mobile-first generation: `fal-ai/flux-2-pro`
- Horizontal desktop expansion: `fal-ai/flux-2-pro/outpaint`
- Masked cleanup: `fal-ai/flux-kontext-lora/inpaint`

The mobile image is the semantic master. Desktop artwork is derived from that
same image with left/right outpainting only; it is not a separate composition.

## Prompt sources

- Carrier iterations: `carrier-mobile.prompt.txt`,
  `carrier-mobile-v2.prompt.txt`, `carrier-mobile-v3.prompt.txt`
- Choice artwork: `choice-prompts.json`
- Outcome artwork: `outcome-prompts.json`

Shared direction: bright editorial gouache, simplified fictional forms,
dark-cobalt contours, dry-brush paper texture, vivid Energy+ orange and cobalt,
warm white snow, clear daylight, capable people and maintained equipment. The
negative direction excludes darkness, neglect, breakdown drama, rust, smoke,
danger, readable pseudo-text, manufacturer badges and fake corporate logos.

## Accepted carrier artwork

- Mobile master: `production/carrier-mobile.webp`
- Desktop expansion: `production/carrier-desktop.webp`
- Generation seed for the accepted base composition: `24082027`
- Cab cleanup seed: `2369082089`
- Desktop side cleanup seed: `650076334`
- Mobile vertical route continuation seed: `29986987`

The scene contains one warehouse and four choices: the older truck on the long
outer route, the gray truck at the warehouse gate, the blue truck on the broad
foreground route and the orange Express option at the junction. A separate
two-driver badge from `production/choices/crew-badge.webp` communicates the crew
advantage without altering the shared vehicle scene.

The tall mobile production file extends the accepted master downward with a
masked continuation of the existing foreground road. The four vehicles,
warehouse and upper composition stay outside that mask; only the otherwise
empty lower snow field becomes a broad S-shaped route. This keeps tall phone
viewports visually purposeful without generating a separate mobile scene.

## Accepted outcomes

- Mobile masters: `production/outcomes/*-mobile.webp`
- Desktop expansions: `production/outcomes/*-desktop.webp`
- Base generation seeds: old `2026410025`, near `1506637029`, crew `564967491`,
  Express `113373527`
- Outpainting: `expand_left: 500`, `expand_right: 500`, no top/bottom expansion,
  `auto_crop: false`, `mode: high`

The crew and Express grille badges were removed with tight masks after visual
inspection. The old outcome is a routine bright technical checkpoint rather
than a breakdown; the gift remains safe and the consequence is additional
delivery time.

## Production conversion

Accepted PNG results are encoded as WebP at quality 88. Desktop outcomes are
center-cropped from their horizontal outpaints and normalized to `1328x800`.
