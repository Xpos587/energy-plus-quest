import type { SceneContext } from '../types';

export const lastmileRevision = 'scene-art/lastmile-family-v1/revision-2';
// revision-5: Mi-8 livery (orange body, black engine housing, five-blade rotor) per the technical reference.
const lastmileHelicopterRevision = 'scene-art/lastmile-family-v1/revision-5';

// revision-12: revision-11 map (v9 opening route style, reference vehicles, 2x) colour-graded per call 05.11:
// red/yellow foliage muted outside the vehicles, АБК roof and trim back to blue. Geometry is pixel-identical.
export function lastmileChoiceImage(format: 'wide' | 'tall', recipient: SceneContext['recipient']) {
  return `scene-art/lastmile-family-v1/revision-12/choice-${format}-${recipient}.webp`;
}

export function lastmileFlightImage(context: SceneContext) {
  const gift = context.parcel === 'boat' ? 'boat' : 'parcel';
  const destination = context.recipient === 'arseniy' ? '-arseniy' : '';
  return `${lastmileHelicopterRevision}/flight-${gift}${destination}.webp`;
}

export function lastmileOutcomeImage(option: string, context: SceneContext) {
  const boat = context.parcel === 'boat';
  switch (option) {
    case 'rover':
      return `${lastmileRevision}/rover-${boat ? 'boat' : 'parcel'}-${context.recipient}.webp`;
    case 'pipe-carrier':
      return `${lastmileRevision}/pipe-carrier-${context.recipient}.webp`;
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
