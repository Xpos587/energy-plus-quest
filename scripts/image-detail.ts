/** Keep native map pixels where desktop display already outruns the source. */
export function preserveDesktopOriginal(original: string): boolean {
  return /^scene-art\/(?:lastmile-family-v1\/choice-final-(?:wide|tall)-v10|lastmile-family-v1\/revision-(?:2|4)\/choice-(?:wide|tall)-(?:alva|khor|arseniy)|barge-family-v1\/choice-neutral-(?:wide|tall)-v7)\.webp$/.test(original);
}

/** Native desktop detail for runtime illustrations from Compact to the ending. */
export function desktopDetailQuality(original: string): number | undefined {
  if (preserveDesktopOriginal(original)) return undefined;
  return /^(?:compact-art\/|scene-art\/(?:inventory-|warehouse-|barge-family-v1\/|lastmile-family-v1\/|resolution-v2\/|certificates-v1\/))/.test(original)
    ? 80 : undefined;
}
