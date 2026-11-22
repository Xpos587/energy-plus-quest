import { renderToStaticMarkup } from 'react-dom/server';
import { expect, it } from 'vitest';
import { sceneOutcomeImage } from '../artwork';
import { LastmileArt } from './LastmileArt';

for (const recipient of ['alva', 'khor', 'arseniy'] as const) {
  for (const parcel of ['boat', 'camera', 'socks'] as const) {
    const context = { profile: 'student', recipient, parcel } as const;
    it(`${recipient}/${parcel}: selected recipient belongs to the destination art`, () => {
      const markup = renderToStaticMarkup(<LastmileArt context={context} showResult={false} />);
      expect(markup).toContain("scene-art/lastmile-family-v1/revision-30/choice-wide.webp");
      expect(sceneOutcomeImage('lastmile', 'rover', context))
        .toBe(`/scene-art/lastmile-family-v1/${parcel === 'boat' ? 'revision-22/rover-boat' : 'revision-19/rover-parcel'}.webp`);   // one rover plate for every recipient (R19 17.11, R22 boat 18.11)
      expect(sceneOutcomeImage('lastmile', 'pipe-carrier', context))
        .toBe('/scene-art/lastmile-family-v1/revision-21/pipe-carrier-tall.webp');
    });
  }
}
