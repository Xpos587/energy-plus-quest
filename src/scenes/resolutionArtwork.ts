import { imageAsset } from "../game/imageAssets";
import type { ParcelId, RecipientId } from "../game/types";

// Keep complete runtime paths discoverable by the static release packager.
const artwork: Record<RecipientId, Record<ParcelId, string>> = {
  alva: {
    socks: "scene-art/resolution-v2/alva-socks.webp",
    boat: "scene-art/resolution-v2/alva-boat.webp",
    camera: "scene-art/resolution-v2/alva-camera.webp",
  },
  khor: {
    socks: "scene-art/resolution-v2/khor-socks.webp",
    boat: "scene-art/resolution-v2/khor-boat.webp",
    camera: "scene-art/resolution-v2/khor-camera.webp",
  },
  arseniy: {
    socks: "scene-art/resolution-v2/arseniy-socks.webp",
    boat: "scene-art/resolution-v2/arseniy-boat.webp",
    camera: "scene-art/resolution-v2/arseniy-camera.webp",
  },
};

const descriptions: Record<RecipientId, Record<ParcelId, string>> = {
  alva: {
    socks:
      "Майма прижимает подаренные носки к груди. Позади — чумы и её семья.",
    boat: "Майма плывёт на подаренной лодке. На берегу — чумы и её семья.",
    camera: "Фотооткрытка Маймы с семьёй, снятая на доставленный фотоаппарат.",
  },
  khor: {
    socks: "Хабт в подаренных носках на фоне тундры, реки и стада.",
    boat: "Хабт плывёт на подаренной лодке, другие олени стоят на берегу.",
    camera:
      "Фотооткрытка Хабта на фоне тундры и стада, снятая на доставленный фотоаппарат.",
  },
  arseniy: {
    socks: "Арсений держит подаренные носки. Позади — общежитие и коллеги.",
    boat: "Арсений плывёт на подаренной лодке рядом с общежитием.",
    camera:
      "Фотооткрытка Арсения с коллегами у общежития, снятая на доставленный фотоаппарат.",
  },
};

export function resolutionArtwork(recipient: RecipientId, parcel: ParcelId) {
  return {
    src: imageAsset(artwork[recipient][parcel]),
    alt: descriptions[recipient][parcel],
  };
}
