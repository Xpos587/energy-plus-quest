import type { SceneContext } from '../types';

export const lastmileRevision = 'scene-art/lastmile-family-v1/revision-2';
const lastmileChoiceRevision = 'scene-art/lastmile-family-v1/revision-4';

export function lastmileChoiceImage(format: 'wide' | 'tall', recipient: SceneContext['recipient']) {
  return `${lastmileChoiceRevision}/choice-${format}-${recipient}.webp`;
}

export function lastmileFlightImage(context: SceneContext) {
  const gift = context.parcel === 'boat' ? 'boat' : 'parcel';
  const destination = context.recipient === 'arseniy' ? '-arseniy' : '';
  return `${lastmileRevision}/flight-${gift}${destination}.webp`;
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
