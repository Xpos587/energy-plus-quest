import alvaArtwork from "../../design/scene-01/assets/current/choices/alva.webp";
import arseniyArtwork from "../../design/scene-01/assets/current/choices/arseniy.webp";
import boatArtwork from "../../design/scene-01/assets/current/choices/boat.webp";
import boatTallArtwork from "../../design/scene-01/assets/current/choices/boat-tall.webp";
import cameraArtwork from "../../design/scene-01/assets/current/choices/camera.webp";
import cameraTallArtwork from "../../design/scene-01/assets/current/choices/camera-tall.webp";
import khorArtwork from "../../design/scene-01/assets/current/choices/khor.webp";
import professionalArtwork from "../../design/scene-01/assets/current/choices/professional.webp";
import socksArtwork from "../../design/scene-01/assets/current/choices/socks.webp";
import socksTallArtwork from "../../design/scene-01/assets/current/choices/socks-tall.webp";
import studentArtwork from "../../design/scene-01/assets/current/choices/student.webp";
import studentCard from "../../design/preparation-outpaint-2026-10-11/student.webp";
import professionalCard from "../../design/preparation-outpaint-2026-10-11/professional.webp";
import alvaCard from "../../design/preparation-outpaint-2026-10-11/alva.webp";
import khorCard from "../../design/preparation-outpaint-2026-10-11/khor.webp";
import arseniyCard from "../../design/preparation-outpaint-2026-10-11/arseniy.webp";
import cameraCard from "../../design/preparation-outpaint-2026-10-11/camera.webp";
import socksCard from "../../design/preparation-outpaint-2026-10-11/socks.webp";
import boatCard from "../../design/preparation-outpaint-2026-10-11/boat.webp";
import type { CarrierId } from "./types";
import { imageAsset } from "./imageAssets";

const outcomeCrewDesktop = imageAsset("scene-art/carrier-results-2026-10-02/crew-v3.webp");
const outcomeCrewMobile = outcomeCrewDesktop;
const outcomeExpressDesktop = outcomeCrewDesktop;
const outcomeExpressMobile = outcomeCrewMobile;
const outcomeNearDesktop = imageAsset("scene-art/carrier-results-2026-10-02/near-v6.webp");
const outcomeNearMobile = outcomeNearDesktop;
const outcomeOldDesktop = imageAsset("scene-art/carrier-results-2026-10-02/old-v5.webp");
const outcomeOldMobile = outcomeOldDesktop;
const outcomeOld4Desktop = imageAsset("scene-art/carrier-results-2026-10-02/old4-v5.webp");
const outcomeOld4Mobile = outcomeOld4Desktop;

export const choiceArtwork: Record<string, string> = {
  student: studentArtwork,
  professional: professionalArtwork,
  alva: alvaArtwork,
  khor: khorArtwork,
  arseniy: arseniyArtwork,
  camera: cameraArtwork,
  socks: socksArtwork,
  boat: boatArtwork,
};

export const choiceCardArtwork: Record<string, string> = {
  ...choiceArtwork,
  camera: cameraTallArtwork,
  socks: socksTallArtwork,
  boat: boatTallArtwork,
};

/** Extended backgrounds for setup cards; portraits elsewhere keep their own framing. */
export const preparationCardArtwork: Record<string, string> = {
  student: studentCard, professional: professionalCard,
  alva: alvaCard, khor: khorCard, arseniy: arseniyCard,
  camera: cameraCard, socks: socksCard, boat: boatCard,
};

export const outcomeArtwork: Record<
  CarrierId,
  { desktop: string; mobile: string; portrait?: string; wide?: string }
> = {
  old: { desktop: outcomeOldDesktop, mobile: outcomeOldMobile, portrait: imageAsset("scene-art/carrier-results-2026-10-02/old-portrait-v2.webp"), wide: imageAsset("scene-art/carrier-results-2026-10-02/old-wide-v8.webp") },
  old4: { desktop: outcomeOld4Desktop, mobile: outcomeOld4Mobile, portrait: imageAsset("scene-art/carrier-results-2026-10-02/old4-portrait-v1.webp"), wide: imageAsset("scene-art/carrier-results-2026-10-02/old4-wide-v8.webp") },
  near: { desktop: outcomeNearDesktop, mobile: outcomeNearMobile, portrait: imageAsset("scene-art/carrier-results-2026-10-02/near-portrait-v1.webp"), wide: imageAsset("scene-art/carrier-results-2026-10-02/near-wide-v7.webp") },
  crew: { desktop: outcomeCrewDesktop, mobile: outcomeCrewMobile, wide: imageAsset("scene-art/carrier-results-2026-10-02/crew-wide-v6.webp") },
  express: { desktop: outcomeExpressDesktop, mobile: outcomeExpressMobile, wide: imageAsset("scene-art/carrier-results-2026-10-02/crew-wide-v6.webp") },
};
