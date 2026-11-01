// Coordinates in revision-11 choice-map pixels at 1x (runtime WebP is 2x). The v9 map sits at
// `original` inside an outpainted canvas large enough for the camera to cover any stage.
export const lastmileChoiceArtwork = {
  wide: {
    width: 2056,
    height: 1841,
    // Entire barge, vehicles, АБК and the chum camp.
    framing: [{ x: 197 / 2056, y: 600 / 1841 }, { x: 1820 / 2056, y: 1486 / 1841 }],
    original: { x: 192, y: 578, width: 1672, height: 941 },
    hotspots: [
      { id: "helicopter", x: 432 / 2056, y: 846 / 1841 },
      { id: "rover", x: 647 / 2056, y: 1040 / 1841 },
      { id: "robot", x: 822 / 2056, y: 1090 / 1841 },
      { id: "pipe-carrier", x: 422 / 2056, y: 1020 / 1841 },
    ],
  },
  tall: {
    width: 1664,
    height: 1952,
    original: { x: 320, y: 288, width: 1024, height: 1536 },
    framing: [{ x: 375 / 1664, y: 358 / 1952 }, { x: 1325 / 1664, y: 1720 / 1952 }],
    hotspots: [
      { id: "helicopter", x: 590 / 1664, y: 1050 / 1952 },
      { id: "rover", x: 930 / 1664, y: 1203 / 1952 },
      { id: "robot", x: 1143 / 1664, y: 1313 / 1952 },
      { id: "pipe-carrier", x: 675 / 1664, y: 1233 / 1952 },
    ],
  },
};
