import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "../index.css";
import { ScenesGame } from "./ScenesGame";
import type { SceneContext, SceneId } from "./types";

const params = new URLSearchParams(window.location.search);
const parcel = params.get("parcel");
const recipient = params.get("recipient");
const stage = params.get("scene");
const context: SceneContext = {
  parcel: parcel === "boat" || parcel === "socks" ? parcel : "camera",
  recipient:
    recipient === "khor" || recipient === "arseniy" ? recipient : "alva",
  profile:
    params.get("profile") === "professional" ? "professional" : "student",
};
const startAt: SceneId =
  stage === "inventory" || stage === "crane" || stage === "lastmile"
    ? stage
    : "compact";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");
createRoot(root).render(
  <StrictMode>
    <ScenesGame context={context} startAt={startAt} />
  </StrictMode>,
);
