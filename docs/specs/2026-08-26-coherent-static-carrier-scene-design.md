# Coherent Static Carrier Scene Design

**Status:** Approved by Michael on 2026-08-26.

## Intent

**Why:** The carrier choice must work as visual storytelling. A player who has
not read the scenario brief should be able to make a reasoned choice by looking
at one static illustration.

**Human outcome:** The player understands distance, likely pace, vehicle age,
crew composition and the Express advantage before reading any supporting label.

**Experience invariants:**

- The scene is one coherent winter illustration, not a background with cutout
  vehicles placed on top.
- All four vehicles share one camera, scale system, light source, contact-shadow
  logic, edge treatment and painterly texture.
- The meaning of every option remains legible when labels, routes, hover effects
  and animation are hidden.
- Desktop and mobile use separately art-directed cameras of the same location.
- The scene remains volumetric and consistent with the other three-dimensional
  illustrated screens; it never becomes a flat city map.

**Betrayal condition:** A technically interactive screen that needs animation,
labels or independently composited sprites to explain the vehicles does not meet
the requirement.

## Approved Production Direction

Use a controlled three-dimensional blocking scene to establish geometry, then
generate each final viewport as one complete raster illustration. The blocking
render, depth map and edge map act as structural controls. Reference images may
teach the model vehicle design and the approved painterly language, but they are
never overlaid as final transparent layers.

Local corrections use masked editing on the complete canvas. A correction mask
must include the vehicle and enough adjacent road, snow, reflected light and
shadow for the model to repaint the physical integration. Final vehicle sprites,
CSS route animation and decorative speed animation are removed from the carrier
screen.

## Static Scene Narrative

### Shared Environment

- A blue logistics warehouse is the spatial anchor.
- Roads form an understandable continuous network rather than decorative bands.
- Snow banks, street lighting, buildings and people establish a warm northern
  town without competing with the vehicles.
- The camera is a high three-quarter view: low enough for cab interiors and
  vehicle volume to read, high enough for all four route situations to coexist.
- Warm warehouse and window light contrasts with blue winter ambient light.

### Old Vehicle

- The vehicle is physically farthest from the warehouse on a receding road.
- Relative size, road convergence, partial interposition and lower contrast make
  the distance unambiguous.
- Its older cab and box silhouette, faded paint and restrained wear show age.
- A small inspection checkpoint or service worker communicates additional
  technical attention without implying a breakdown, accident or unsafe vehicle.
- No smoke, detached parts, crash damage or stranded pose is allowed.

### Vehicle At The Gate

- The vehicle is directly connected to the warehouse loading gate and is the
  nearest option.
- Its route is visibly constrained by a gate procedure, a short loading queue or
  a snow-clearing vehicle on the exit lane.
- It is intact and ready, but its immediate environment communicates a slow start.
- The cue cannot depend on a written word such as `медленно`.

### Two-Driver Vehicle

- The cab is large enough in the composition for two adults to be unmistakable.
- One person drives; the second is visibly prepared for the route with a map,
  thermos or route sheet.
- Both figures belong inside the illustrated cab and share its reflections and
  lighting. A detached portrait badge is not used as the primary evidence.
- The truck sits on a viable long road, away from the warehouse but not as deep
  as the old vehicle.

### Express Vehicle

- A modern orange vehicle is positioned on the clearest, most direct road.
- Its orientation, open road ahead, compressed wheel detail and restrained snow
  plume imply confident speed in the static frame.
- Roadside elements and snow texture reinforce the direction of travel without
  comic-book speed lines or UI animation.
- Express is visually the quickest and most capable option even when its label is
  removed.

## Composition And Hierarchy

The illustration uses relative size, interposition, linear perspective,
atmospheric perspective, light and shadow as redundant depth cues. The four
vehicle stories occupy distinct spatial zones with enough negative space to be
selected without covering one another.

Orange is reserved for Express and small warm environmental accents. Blue
vehicles remain separable through value, scale and context rather than competing
accent colors. The warehouse remains recognizable but does not dominate the
foreground.

## Responsive Art Direction

### Desktop

- Target master: `1536x864`, landscape `16:9`.
- All four vehicles and the warehouse are simultaneously visible.
- The mission panel occupies an inactive edge region and never covers a vehicle.
- Vehicle hit areas follow semantic regions of the single raster rather than
  displaying separate vehicle images.

### Mobile

- Target master: `944x1792`, portrait, composed independently from desktop.
- The camera is higher and tighter, but vehicles remain distributed through the
  full available height rather than compressed into the upper third.
- The two-driver cab remains readable at iPhone SE presentation size.
- The mission panel uses a safe lower or upper area that contains no vehicle.
- All four hit areas remain reachable without page scrolling at `375x667` and
  `390x844`.

## UI Integration

- `CityMap` renders one responsive `<picture>` and four transparent semantic
  buttons positioned over the corresponding regions.
- Buttons contain accessible names and optional compact HTML labels, but no
  vehicle `<img>` elements.
- Hover, focus and selection may use a restrained region outline, local contrast
  lift or label response. They do not move the truck or draw an explanatory
  route.
- Reduced-motion and normal-motion presentations communicate identical facts.
- Existing carrier identifiers, scores, reducer behavior and result branches do
  not change.

## Production Workflow

1. Build a low-detail 3D blockout with warehouse, roads, vehicles, people and cue
   props using simple primitives and fixed real-world proportions.
2. Lock desktop and mobile cameras and render color blocking, depth and edge
   guides for each.
3. Generate several whole-frame painterly candidates from the structural guides
   and the approved V7 style reference.
4. Inspect every candidate at original resolution with `view_image`; reject any
   frame with duplicated vehicles, unreadable occupants, inconsistent geometry
   or weak visual semantics.
5. Correct only failed regions through full-canvas masked editing with masks that
   include their environmental integration.
6. Export final lossless masters, then encode production WebP assets.
7. Replace V8 layered rendering with semantic hotspots over the two coherent
   rasters.
8. Capture and inspect desktop, `390x844` and iPhone SE `375x667` screenshots
   before deployment.

## Acceptance Criteria

- Each master contains exactly one warehouse and exactly four trucks.
- No final carrier vehicle is a transparent layer or separately rendered DOM
  image.
- With all HTML labels and animations disabled, a reviewer can identify which
  vehicle is farthest, which is nearest but delayed, which has two drivers and
  which is Express.
- The old vehicle appears aged but operational and safe.
- Two distinct adults are visible in the crew cab at final mobile display size.
- Express reads as fastest through the static environment and vehicle pose.
- Contact shadows, reflected color, snow interaction, perspective and texture are
  continuous across each whole frame.
- Desktop and mobile are separate compositions of the same art direction, not
  mechanical crops.
- The carrier screen remains fully usable at `1440x900`, `390x844` and `375x667`.
- `bun run check`, unit tests, build and Playwright tests pass after integration.

## Rejected Approaches

- Transparent truck sprites placed over an empty background.
- Animation as the primary explanation of distance or speed.
- SVG route traces as the primary explanation of vehicle properties.
- A flat two-dimensional city map.
- Mechanical desktop-to-mobile cropping or horizontal outpainting that preserves
  only one viewport's composition.
- Tight object masks that repaint a truck without adjacent road, shadow and snow.
