// Coordinates in revision-8 choice-map pixels (the shipped WebP is 2x).
export const lastmileChoiceArtwork = {
  wide: {
    width: 1942,
    height: 809,
    // Entire barge, vehicle silhouettes, aerial and destination clearing.
    framing: [{ x: 405 / 1942, y: 27 / 809 }, { x: 1670 / 1942, y: 798 / 809 }],
    original: { x: 0, y: 0, width: 1942, height: 809 },
    hotspots: [
      { id: "helicopter", x: 650 / 1942, y: 270 / 809 },
      { id: "rover", x: 910 / 1942, y: 550 / 809 },
      { id: "robot", x: 1010 / 1942, y: 663 / 809 },
      { id: "pipe-carrier", x: 780 / 1942, y: 433 / 809 },
    ],
  },
  tall: {
    width: 948,
    height: 1659,
    original: { x: 0, y: 0, width: 948, height: 1659 },
    framing: [{ x: 17 / 948, y: 300 / 1659 }, { x: 920 / 948, y: 1390 / 1659 }],
    hotspots: [
      { id: "helicopter", x: 145 / 948, y: 866 / 1659 },
      { id: "rover", x: 565 / 948, y: 1000 / 1659 },
      { id: "robot", x: 723 / 948, y: 1064 / 1659 },
      { id: "pipe-carrier", x: 395 / 948, y: 950 / 1659 },
    ],
  },
};
