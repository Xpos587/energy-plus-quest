import { expect, it } from 'vitest';
import { sceneOutcomeImage } from '../artwork';

// Michael 17.11/18.11: one approved rover-boat plate (R21) is shared by every recipient.
it('keeps the boat visible on the shared R21 rover plate for every recipient', () => {
  for (const recipient of ['alva', 'arseniy', 'khor'] as const) {
    expect(sceneOutcomeImage('lastmile', 'rover', { profile: 'student', recipient, parcel: 'boat' }))
      .toBe('/scene-art/lastmile-family-v1/revision-22/rover-boat.webp');
  }
});
