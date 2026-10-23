/** One neutral parcel; operator positions and walking distance define the choices. */
export const craneChoiceArtwork = {
  wide: {
    image: "scene-art/barge-family-v1/choice-neutral-wide-v7.webp",
    width: 1983,
    height: 793,
    anchor: { x: 1050, y: 397 },
    hotspots: [
      { id: "rush", x: 950 / 1983, y: 415 / 793 },
      { id: "wait", x: 950 / 1983, y: 415 / 793 },
      { id: "petr", x: 1420 / 1983, y: 265 / 793 },
      { id: "remote", x: 215 / 1983, y: 335 / 793 },
    ],
  },
  tall: {
    image: "scene-art/barge-family-v1/choice-neutral-tall-v7.webp",
    width: 1122,
    height: 1402,
    anchor: { x: 561, y: 650 },
    hotspots: [
      { id: "rush", x: 650 / 1122, y: 555 / 1402 },
      { id: "wait", x: 650 / 1122, y: 555 / 1402 },
      { id: "petr", x: 1000 / 1122, y: 250 / 1402 },
      { id: "remote", x: 300 / 1122, y: 735 / 1402 },
    ],
  },
};
