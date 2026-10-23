import { expect, it } from 'vitest';
import { craneFamilyImage } from './artworkFamily';

it('uses reviewed result artwork for each parcel', () => {
  for (const parcel of ['boat', 'camera', 'socks'] as const) {
    expect(craneFamilyImage('petr', parcel)).toBe(`scene-art/barge-family-v1/petr-${parcel}-v13.png`);
    expect(craneFamilyImage('rush', parcel)).toBe(`scene-art/barge-family-v1/rush-${parcel}-v3.png`);
    expect(craneFamilyImage('remote', parcel)).toBe(`scene-art/barge-family-v1/remote-${parcel}-v4.png`);
    expect(craneFamilyImage('choice', parcel)).toBe('scene-art/barge-family-v1/choice-neutral-wide-v7.webp');
    expect(craneFamilyImage('wait', parcel)).toBe(`scene-art/barge-family-v1/wait-${parcel}-${parcel === 'socks' ? 'v2' : parcel === 'boat' ? 'v3' : 'v1'}.png`);
  }
  expect(craneFamilyImage('unknown', 'boat')).toBeUndefined();
});
