import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { SceneOutcomeArt } from "./SceneOutcomeArt";

const context = {
  profile: "professional",
  recipient: "alva",
  parcel: "boat",
} as const;

it("uses the flight image for the flight beat without separate episode controls", () => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(
    <SceneOutcomeArt
      scene="lastmile"
      selectedId="helicopter"
      context={context}
      displayedBeat={0}
    />,
  );

  expect(host.querySelector("img")?.getAttribute("src")).toContain(
    "revision-2/flight-boat.webp",
  );
  expect(host.querySelector("nav")).toBeNull();
});

it("uses the ground image only after the narrative reaches the ground beat", () => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(
    <SceneOutcomeArt
      scene="lastmile"
      selectedId="helicopter"
      context={context}
      displayedBeat={1}
    />,
  );

  expect(host.querySelector("img")?.getAttribute("src")).toContain(
    "helicopter-ground-boat-final-v5",
  );
  expect(host.querySelector("nav")).toBeNull();
});
