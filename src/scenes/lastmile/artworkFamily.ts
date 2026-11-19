import type { SceneContext } from '../types';

// revision-18: flight screens with the Mi-8 repainted to the client reference livery (black upper half, orange lower,
// small white nose patch); cargo door, sling and load unchanged (design/scene-05/swamp-2026-11-10/finish_flight.py).
const lastmileFlightRevision = 'scene-art/lastmile-family-v1/revision-18';
// revision-21: tundra flight (parcel/boat), one pipe-carrier plate and a calmer rover-boat, approved 18.11.
// ponytail: Arseniy keeps revision-18 flights (worker on the ground) until tundra variants exist.
const lastmileTundraRevision = 'scene-art/lastmile-family-v1/revision-21';
// revision-22: revision-21 flights with the white «3» on the Mi-8 nose and a regenerated rover-boat (.tmp-work/s5-r22).
const lastmileRevision22 = 'scene-art/lastmile-family-v1/revision-22';

// Revision 25 repaints the same v29 layout, with revised vehicles and flooded ruts.
export function lastmileChoiceImage(format: 'wide' | 'tall', _recipient?: SceneContext['recipient']) {
  return `scene-art/lastmile-family-v1/revision-25/choice-${format}.webp`;
}

export function lastmileFlightImage(context: SceneContext) {
  const gift = context.parcel === 'boat' ? 'boat' : 'parcel';
  if (context.recipient === 'arseniy') return `${lastmileFlightRevision}/flight-${gift}-arseniy-tall.webp`;
  return `${lastmileRevision22}/flight-${gift}-tall.webp`;
}

// revision-19: sunny closeups approved 16.11 (rover, ground helicopter, robot) on the R5 bog/tundra; one rover plate for all recipients.
const lastmileOutcomeRevision = 'scene-art/lastmile-family-v1/revision-19';

export function lastmileOutcomeImage(option: string, context: SceneContext) {
  const boat = context.parcel === 'boat';
  switch (option) {
    case 'rover':
      return boat ? `${lastmileRevision22}/rover-boat.webp` : `${lastmileOutcomeRevision}/rover-parcel.webp`;
    case 'pipe-carrier':
      return `${lastmileTundraRevision}/pipe-carrier-tall.webp`;
    case 'helicopter':
      if (context.recipient === 'arseniy') return lastmileFlightImage(context);
      return `${lastmileOutcomeRevision}/ground-${context.recipient === 'khor' ? 'khor-' : boat ? '' : 'alva-'}${boat ? 'boat' : 'parcel'}.webp`;
    case 'robot':
      return `${lastmileOutcomeRevision}/robot-${boat ? 'boat' : 'parcel'}.webp`;
    default:
      return undefined;
  }
}
