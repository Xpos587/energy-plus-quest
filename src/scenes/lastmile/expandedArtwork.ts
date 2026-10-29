// Coordinates in revision-7 choice-map pixels (the shipped WebP is 2x).
export const lastmileChoiceArtwork = {
  wide: {
    width: 1942,
    height: 809,
    anchor: { x: 1000, y: 400 },
    original: { x: 0, y: 0, width: 1942, height: 809 },
    hotspots: [
      { id: "helicopter", x: 620 / 1942, y: 325 / 809 },
      { id: "rover", x: 830 / 1942, y: 598 / 809 },
      { id: "robot", x: 945 / 1942, y: 685 / 809 },
      { id: "pipe-carrier", x: 730 / 1942, y: 492 / 809 },
    ],
  },
  tall: {
    width: 948,
    height: 1659,
    anchor: { x: 474, y: 830 },
    original: { x: 0, y: 0, width: 948, height: 1659 },
    // Keep the destination building and recipient above the vehicle quay in view.
    maxTop: 400,
    hotspots: [
      { id: "helicopter", x: 185 / 948, y: 900 / 1659 },
      { id: "rover", x: 570 / 948, y: 1060 / 1659 },
      { id: "robot", x: 720 / 948, y: 1090 / 1659 },
      { id: "pipe-carrier", x: 405 / 948, y: 1020 / 1659 },
    ],
  },
};
