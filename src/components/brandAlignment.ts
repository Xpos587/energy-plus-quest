/** Optical alignment from the approved intro: 5px at a 180px Energy+ width. */
export const energyOpticalShift = 5 / (180 * 198 / 1352);
export const energyLogoStyle = {
  transform: `translateY(${energyOpticalShift * 100}%)`,
};
