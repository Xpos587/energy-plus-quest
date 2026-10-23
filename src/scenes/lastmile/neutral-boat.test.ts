import { expect, it } from 'vitest';
import { sceneOutcomeImage } from '../artwork';

it('keeps the boat visible without showing Mayma for other recipients', () => {
  for (const recipient of ['arseniy', 'khor'] as const) {
    expect(sceneOutcomeImage('lastmile', 'rover', { profile: 'student', recipient, parcel: 'boat' }))
      .toBe(`/scene-art/lastmile-family-v1/revision-2/rover-boat-${recipient}.webp`);
  }
});
