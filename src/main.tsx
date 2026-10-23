import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { registerGameCache } from "./game/offlineCache";
import "./index.css";
import "./nativeInteractions";
import "./mediaReview";
import "./ux-brand.css";

const uxVariant = new URLSearchParams(window.location.search).get("ux");
if (uxVariant === "brand") {
  document.documentElement.dataset.ux = uxVariant;
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("Root element not found");
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
registerGameCache();
