export const portraitChoiceArtwork = {
  inventory: {
    image: "scene-art/inventory-choice-tall-v1.webp",
    width: 948,
    height: 1659,
    anchor: { x: 474, y: 837 },
    original: { x: 0, y: 572, width: 948, height: 529 },
    hotspots: [
      { id: "entrance", x: 161 / 948, y: 916 / 1659 },
      { id: "alphabet", x: 512 / 948, y: 799 / 1659 },
      { id: "keeper", x: 777 / 948, y: 900 / 1659 },
      { id: "wms", x: 683 / 948, y: 1006 / 1659 },
    ],
  },
  crane: {
    image: "scene-art/barge-family-v1/choice-parcel-tall-v1.webp",
    width: 948,
    height: 1659,
    anchor: { x: 474, y: 725 },
    hotspots: [
      { id: "rush", x: 351 / 948, y: 774 / 1659 },
      { id: "wait", x: 552 / 948, y: 728 / 1659 },
      { id: "petr", x: 781 / 948, y: 548 / 1659 },
      { id: "remote", x: 123 / 948, y: 770 / 1659 },
    ],
  },
} as const;
