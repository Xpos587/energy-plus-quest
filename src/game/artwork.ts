import alvaArtwork from "../../design/scene-01/assets/current/choices/alva.webp";
import arseniyArtwork from "../../design/scene-01/assets/current/choices/arseniy.webp";
import boatArtwork from "../../design/scene-01/assets/current/choices/boat.webp";
import cameraArtwork from "../../design/scene-01/assets/current/choices/camera.webp";
import khorArtwork from "../../design/scene-01/assets/current/choices/khor.webp";
import professionalArtwork from "../../design/scene-01/assets/current/choices/professional.webp";
import socksArtwork from "../../design/scene-01/assets/current/choices/socks.webp";
import studentArtwork from "../../design/scene-01/assets/current/choices/student.webp";
import type { CarrierId } from "./types";

const outcomeCrewDesktop = `${import.meta.env.BASE_URL}scene1-live/crew-desktop.webp`;
const outcomeCrewMobile = `${import.meta.env.BASE_URL}scene1-live/crew-mobile.webp`;
const outcomeExpressDesktop = `${import.meta.env.BASE_URL}scene1-live/express-desktop.webp`;
const outcomeExpressMobile = `${import.meta.env.BASE_URL}scene1-live/express-mobile.webp`;
const outcomeNearDesktop = `${import.meta.env.BASE_URL}scene1-live/near-desktop.webp`;
const outcomeNearMobile = `${import.meta.env.BASE_URL}scene1-live/near-mobile.webp`;
const outcomeOldDesktop = `${import.meta.env.BASE_URL}scene1-live/old-desktop.webp`;
const outcomeOldMobile = `${import.meta.env.BASE_URL}scene1-live/old-mobile.webp`;
const outcomeOld4Desktop = `${import.meta.env.BASE_URL}scene1-live/old4-desktop.webp`;
const outcomeOld4Mobile = `${import.meta.env.BASE_URL}scene1-live/old4-mobile.webp`;

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
