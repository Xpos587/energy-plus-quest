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
  "renders %s %j as %s with the original result copy and company link",
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
          />,
        ),
      );
      const certificate = host.querySelector("[data-logist-certificate]");
      expect(certificate?.textContent).toContain(copy.title);
      expect(certificate?.textContent).toContain(copy.callToAction);
      /* One target path: the company site, linked inside the closing sentence. */
      const links = host.querySelectorAll("[data-company-cta] a");
      expect(links).toHaveLength(1);
      expect(links[0].getAttribute("href")).toBe("https://supply.gazprom-neft.ru/");
      expect(links[0].textContent).toMatch(/^Узнайте больше о /u);
      expect(host.textContent).not.toMatch(/ваканси/iu);
      expect(host.querySelector("[data-certificate-totals]")).toBeNull();
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

it("speaks in the first person in every shared certificate", () => {
  for (const profile of ["student", "professional"] as const)
    for (const numbers of [[-1, -2, -3], [5, 1, 2], [1, 5, 2], [1, 2, 5]]) {
      const text = certificateCopy(
        logistProfileCopy(profile, "alva", {
          energy: numbers[0],
          empathy: numbers[1],
          efficiency: numbers[2],
        }),
      ).join(" ");
      expect(text).not.toMatch(/(^|[^а-яё])(вы|ваш[а-яё]*|вам|вас|мы)(?![а-яё])/iu);
    }
});

it("shows final totals as the per-stage average shifted to 0…10", async () => {
  const { finalScore } = await import("./endingCopy");
  expect([-25, -5, 0, 5, 12, 25, 40].map(finalScore)).toEqual([0, 4, 5, 6, 7, 10, 10]);
  expect(finalScore(-40)).toBe(0);
});
