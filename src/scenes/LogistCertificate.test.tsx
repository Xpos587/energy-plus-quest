import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { certificateCopy } from "./certificateExport";
import { logistProfileCopy } from "./endingCopy";
import { LogistCertificate } from "./LogistCertificate";

it.each([
  ["student", [-1, -2, -3], "future"],
  ["student", [5, 1, 2], "energy"],
  ["student", [1, 5, 2], "empathy"],
  ["student", [1, 2, 5], "efficiency"],
  ["professional", [5, 1, 2], "energy"],
  ["professional", [1, 5, 2], "empathy"],
  ["professional", [1, 2, 5], "efficiency"],
] as const)(
  "renders %s %j as %s with the original result copy and CTA",
  async (profile, numbers, type) => {
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    const host = document.createElement("div");
    const root = createRoot(host);
    const copy = logistProfileCopy(profile, "alva", {
      energy: numbers[0],
      empathy: numbers[1],
      efficiency: numbers[2],
    });
    try {
      await act(async () =>
        root.render(
          <LogistCertificate
            profile={profile}
            copy={copy}
            onRestart={() => {}}
            onHome={() => {}}
          />,
        ),
      );
      const certificate = host.querySelector("[data-logist-certificate]");
      expect(certificate?.textContent).toContain(copy.title);
      expect(certificate?.textContent).not.toContain(copy.callToAction);
      if (profile === "student") {
        expect(
          host.querySelector("[data-practice-cta]")?.textContent,
        ).toContain(copy.callToAction);
      }
      expect(
        host.querySelector("[data-certificate-art]")?.getAttribute("src"),
      ).toContain(`${profile}-${type}`);
      expect(host.textContent).toContain(copy.callToAction);
      expect(
        host.querySelectorAll("button[data-certificate-actions]"),
      ).toHaveLength(1);
      expect(certificateCopy(copy).join(" ")).not.toContain(copy.callToAction);
    } finally {
      await act(async () => root.unmount());
      vi.unstubAllGlobals();
    }
  },
);

it("uses first-person possessive wording in shared certificates and excludes CTA", () => {
  expect(
    certificateCopy({
      title: "Тип",
      paragraphs: ["Поле ваших новых свершений."],
      callToAction: "Узнать больше",
      type: "future",
    }),
  ).toEqual(["Тип", "Поле моих новых свершений."]);
});
