// Coordinates in revision-10 choice-map pixels at 1x (runtime WebP is 2x). The v9 map sits at
// `original` inside an outpainted canvas so the camera can cover the stage without bands.
export const lastmileChoiceArtwork = {
  wide: {
    width: 1672,
    height: 1393,
    // Entire barge, vehicles, АБК and the chum camp.
    framing: [{ x: 5 / 1672, y: 248 / 1393 }, { x: 1628 / 1672, y: 1134 / 1393 }],
    original: { x: 0, y: 226, width: 1672, height: 941 },
    hotspots: [
      { id: "helicopter", x: 240 / 1672, y: 494 / 1393 },
      { id: "rover", x: 455 / 1672, y: 688 / 1393 },
      { id: "robot", x: 630 / 1672, y: 738 / 1393 },
      { id: "pipe-carrier", x: 230 / 1672, y: 668 / 1393 },
    ],
  },
  tall: {
    width: 1280,
    height: 1536,
    original: { x: 128, y: 0, width: 1024, height: 1536 },
    framing: [{ x: 183 / 1280, y: 70 / 1536 }, { x: 1133 / 1280, y: 1432 / 1536 }],
    hotspots: [
      { id: "helicopter", x: 398 / 1280, y: 762 / 1536 },
      { id: "rover", x: 738 / 1280, y: 915 / 1536 },
      { id: "robot", x: 951 / 1280, y: 1025 / 1536 },
      { id: "pipe-carrier", x: 483 / 1280, y: 945 / 1536 },
    ],
  },
};
