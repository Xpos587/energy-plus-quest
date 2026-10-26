/** Barge scene v2: one neutral quay drawing in two crops, four result stills. */
const base = "scene-art/barge-v2";

export const craneArtwork = {
  wide: {
    image: `${base}/choice-wide.webp`,
    width: 1934,
    height: 813,
    // The strip that must stay in frame: office, gift, crane, barge, far crane.
    focus: { x: 180, y: 90, width: 1740, height: 600 },
    hotspots: {
      remote: { x: 395, y: 400, r: 90, side: "right" },
      rush: { x: 790, y: 380, r: 70, side: "right" },
      wait: { x: 822, y: 150, r: 70, side: "right" },
      petr: { x: 1790, y: 215, r: 70, side: "left" },
    },
    chips: { barge: { x: 1280, y: 560 }, gift: { x: 655, y: 440 } },
  },
  tall: {
    image: `${base}/choice-tall.webp`,
    width: 1120,
    height: 1404,
    focus: { x: 0, y: 130, width: 1120, height: 980 },
    hotspots: {
      remote: { x: 248, y: 640, r: 90, side: "right" },
      rush: { x: 588, y: 580, r: 70, side: "right" },
      wait: { x: 612, y: 196, r: 70, side: "left" },
      petr: { x: 962, y: 445, r: 60, side: "left" },
    },
    chips: { barge: { x: 560, y: 1030 }, gift: { x: 437, y: 700 } },
  },
} as const;
export type CraneFormat = keyof typeof craneArtwork;

/** What each pin points at in the drawing. */
export const craneCaptions = {
  remote: "Иван в офисе",
  rush: "Подъём в кабину",
  wait: "Кран свободен через 3 ч",
  petr: "Пётр на дальнем кране",
} as const;

export const craneOutcomeImage = (id: string) => `${base}/outcome-${id}.webp`;
export const craneChoiceImage = craneArtwork.wide.image;
