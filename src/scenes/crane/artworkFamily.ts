import type { SceneContext } from '../types';

/** Only reviewed families are switched on; other outcomes keep their existing art. */
const versions: Record<string, string> = { choice: 'v1', rush: 'v3', wait: 'v1', petr: 'v13', remote: 'v4' };
const parcelVersions: Record<string, string> = {
  'wait-socks': 'v2',
  'wait-boat': 'v3',
};

export function craneFamilyImage(variant: string, parcel: SceneContext['parcel']): string | undefined {
  if (variant === 'choice') return 'scene-art/barge-family-v1/choice-neutral-wide-v7.webp';
  const version = parcelVersions[`${variant}-${parcel}`] ?? versions[variant];
  return version ? `scene-art/barge-family-v1/${variant}-${parcel}-${version}.png` : undefined;
}
