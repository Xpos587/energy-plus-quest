import type { SceneContext } from '../types';

export const lastmileRevision = 'scene-art/lastmile-family-v1/revision-2';
// revision-5: Mi-8 livery (orange body, black engine housing, five-blade rotor) per the technical reference.
// revision-13: revision-5 flight and revision-2 pipe-carrier outpainted to 1672x2200 (design/scene-05/fill)
// so near-square desktop rails and portrait/landscape phones are covered without bands or cut subjects.
const lastmileTallRevision = 'scene-art/lastmile-family-v1/revision-13';

// revision-16: revision-12 map with a smaller river, big swamp, brighter АБК and the reference Mi-8 livery (design/scene-05/swamp-2026-11-10).
// revision-12: revision-11 map (v9 opening route style, reference vehicles, 2x) colour-graded per call 05.11:
// red/yellow foliage muted outside the vehicles, АБК roof and trim back to blue. Geometry is pixel-identical.
export function lastmileChoiceImage(format: 'wide' | 'tall', recipient: SceneContext['recipient']) {
  return `scene-art/lastmile-family-v1/revision-16/choice-${format}-${recipient}.webp`;
}

export function lastmileFlightImage(context: SceneContext) {
  const gift = context.parcel === 'boat' ? 'boat' : 'parcel';
  const destination = context.recipient === 'arseniy' ? '-arseniy' : '';
  return `${lastmileTallRevision}/flight-${gift}${destination}-tall.webp`;
}

export function lastmileOutcomeImage(option: string, context: SceneContext) {
  const boat = context.parcel === 'boat';
  switch (option) {
    case 'rover':
      return `${lastmileRevision}/rover-${boat ? 'boat' : 'parcel'}-${context.recipient}.webp`;
    case 'pipe-carrier':
      return `${lastmileTallRevision}/pipe-carrier-${context.recipient}-tall.webp`;
    case 'helicopter':
      if (context.recipient === 'arseniy') return lastmileFlightImage(context);
      return `scene-art/lastmile-family-v1/${context.recipient === 'khor'
        ? boat ? 'helicopter-ground-khor-boat-v6.webp' : 'helicopter-ground-khor-parcel-v6.webp'
        : boat ? 'helicopter-ground-boat-final-v5.webp' : 'helicopter-ground-alva-parcel-v6.webp'}`;
    case 'robot':
      return `scene-art/lastmile-family-v1/${boat ? 'robot-boat-result-v3.webp' : 'robot-parcel-result-v1.webp'}`;
    default:
      return undefined;
  }
}
