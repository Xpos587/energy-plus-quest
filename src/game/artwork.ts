import alvaArtwork from "../../design/scene-01/assets/current/choices/alva.webp";
import arseniyArtwork from "../../design/scene-01/assets/current/choices/arseniy.webp";
import boatArtwork from "../../design/scene-01/assets/current/choices/boat.webp";
import cameraArtwork from "../../design/scene-01/assets/current/choices/camera.webp";
import khorArtwork from "../../design/scene-01/assets/current/choices/khor.webp";
import professionalArtwork from "../../design/scene-01/assets/current/choices/professional.webp";
import socksArtwork from "../../design/scene-01/assets/current/choices/socks.webp";
import studentArtwork from "../../design/scene-01/assets/current/choices/student.webp";
import outcomeCrewDesktop from "../../design/scene-01/assets/current/outcomes/crew-desktop.webp";
import outcomeCrewMobile from "../../design/scene-01/assets/current/outcomes/crew-mobile.webp";
import outcomeExpressDesktop from "../../design/scene-01/assets/current/outcomes/express-desktop.webp";
import outcomeExpressMobile from "../../design/scene-01/assets/current/outcomes/express-mobile.webp";
import outcomeNearDesktop from "../../design/scene-01/assets/current/outcomes/near-desktop.webp";
import outcomeNearMobile from "../../design/scene-01/assets/current/outcomes/near-mobile.webp";
import outcomeOldDesktop from "../../design/scene-01/assets/current/outcomes/old-desktop.webp";
import outcomeOldMobile from "../../design/scene-01/assets/current/outcomes/old-mobile.webp";
import outcomeOld4Desktop from "../../design/scene-01/assets/current/outcomes/old4-desktop.webp";
import outcomeOld4Mobile from "../../design/scene-01/assets/current/outcomes/old4-mobile.webp";
import type { CarrierId } from "./types";

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

export const outcomeArtwork: Record<
  CarrierId,
  { desktop: string; mobile: string }
> = {
  old: { desktop: outcomeOldDesktop, mobile: outcomeOldMobile },
  old4: { desktop: outcomeOld4Desktop, mobile: outcomeOld4Mobile },
  near: { desktop: outcomeNearDesktop, mobile: outcomeNearMobile },
  crew: { desktop: outcomeCrewDesktop, mobile: outcomeCrewMobile },
  express: { desktop: outcomeExpressDesktop, mobile: outcomeExpressMobile },
};
