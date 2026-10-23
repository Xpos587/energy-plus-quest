import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it } from 'vitest';
import { sceneOutcomeImage } from '../artwork';
import { LastmileArt } from './LastmileArt';

for (const recipient of ['alva', 'khor', 'arseniy'] as const) {
  for (const parcel of ['boat', 'camera', 'socks'] as const) {
    const context = { profile: 'student', recipient, parcel } as const;
    it(`${recipient}/${parcel}: selected recipient belongs to the destination art`, () => {
      const markup = renderToStaticMarkup(<LastmileArt context={context} showResult={false} />);
      expect(markup).toContain(`revision-4/choice-tall-${recipient}.webp`);
      expect(sceneOutcomeImage('lastmile', 'rover', context))
        .toBe(`/scene-art/lastmile-family-v1/revision-2/rover-${parcel === 'boat' ? 'boat' : 'parcel'}-${recipient}.webp`);
      expect(sceneOutcomeImage('lastmile', 'pipe-carrier', context))
        .toBe(`/scene-art/lastmile-family-v1/revision-2/pipe-carrier-${recipient}.webp`);
    });
  }
}
