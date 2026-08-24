import arseniyArtwork from "../../design/scene-01/assets/feedback-v4/production/choices/arseniy.webp";
import boatArtwork from "../../design/scene-01/assets/feedback-v4/production/choices/boat.webp";
import cameraArtwork from "../../design/scene-01/assets/feedback-v4/production/choices/camera.webp";
import khorArtwork from "../../design/scene-01/assets/feedback-v4/production/choices/khor.webp";
import socksArtwork from "../../design/scene-01/assets/feedback-v4/production/choices/socks.webp";
import studentArtwork from "../../design/scene-01/assets/feedback-v4/production/choices/student.webp";
import outcomeCrewDesktop from "../../design/scene-01/assets/feedback-v4/production/outcomes/crew-desktop.webp";
import outcomeCrewMobile from "../../design/scene-01/assets/feedback-v4/production/outcomes/crew-mobile.webp";
import outcomeExpressMobile from "../../design/scene-01/assets/feedback-v4/production/outcomes/express-mobile.webp";
import professionalArtwork from "../../design/scene-01/assets/feedback-v5/production/choices/professional.webp";
import outcomeExpressDesktop from "../../design/scene-01/assets/feedback-v5/production/outcomes/express-desktop.webp";
import outcomeNearDesktop from "../../design/scene-01/assets/feedback-v5/production/outcomes/near-desktop.webp";
import outcomeNearMobile from "../../design/scene-01/assets/feedback-v5/production/outcomes/near-mobile.webp";
import outcomeOldDesktop from "../../design/scene-01/assets/feedback-v5/production/outcomes/old-desktop.webp";
import outcomeOldMobile from "../../design/scene-01/assets/feedback-v5/production/outcomes/old-mobile.webp";
import alvaArtwork from "../../design/scene-01/assets/feedback-v6/production/choices/alva.webp";
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
  near: { desktop: outcomeNearDesktop, mobile: outcomeNearMobile },
  crew: { desktop: outcomeCrewDesktop, mobile: outcomeCrewMobile },
  express: { desktop: outcomeExpressDesktop, mobile: outcomeExpressMobile },
};
