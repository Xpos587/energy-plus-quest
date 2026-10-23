import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ScenesGame } from "./ScenesGame";

const branches = ["alva", "khor", "arseniy"].flatMap((recipient) =>
  ["socks", "boat", "camera"].flatMap((parcel) =>
    ["helicopter", "rover", "robot", "pipe-carrier"].map((answer) => ({
      recipient,
      parcel,
      answer,
    })),
  ),
);
it.each(branches)(
  "opens and restores resolution for $recipient/$parcel after $answer",
  async ({ recipient, parcel, answer }) => {
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    const host = document.createElement("div");
    document.body.append(host);
    const key = "resolution-route-test";
    localStorage.setItem(
      key,
      JSON.stringify({
        progress: {
          sceneIndex: 3,
          phase: "result",
          finished: false,
          answers: {
            compact: "auto",
            inventory: "wms",
            crane: "remote",
            lastmile: answer,
          },
        },
      }),
    );
    const root = createRoot(host);
    const context = { profile: "student", recipient, parcel } as Parameters<
      typeof ScenesGame
    >[0]["context"];
    try {
      await act(async () =>
        root.render(<ScenesGame persistenceKey={key} context={context} />),
      );
      for (
        let page = 0;
        page < 30 && !host.querySelector("[data-journey-ending]");
        page++
      ) {
        const button = [
          ...host.querySelectorAll<HTMLButtonElement>(
            "[data-result-reader] button",
          ),
        ].find((b) =>
          /^(Читать дальше|К вручению подарка)$/.test(
            b.getAttribute("aria-label") ?? "",
          ),
        );
        expect(button).toBeTruthy();
        if (!button) throw new Error("Missing result continuation");
        await act(async () => button.click());
      }
      expect(
        host.querySelector("[data-resolution-art]")?.getAttribute("src"),
      ).toContain(`${recipient}-${parcel}`);
      await act(async () =>
        root.render(
          <ScenesGame key="reload" persistenceKey={key} context={context} />,
        ),
      );
      expect(
        host.querySelector("[data-resolution-art]")?.getAttribute("src"),
      ).toContain(`${recipient}-${parcel}`);
    } finally {
      await act(async () => root.unmount());
      host.remove();
      localStorage.removeItem(key);
      vi.unstubAllGlobals();
    }
  },
);
