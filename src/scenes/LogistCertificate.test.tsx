import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { certificateCopy, jpegPdf } from "./certificateExport";
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

it("wraps the JPEG in a one-page PDF with a valid cross-reference table", async () => {
  const pdf = await jpegPdf(new Uint8Array([0xff, 0xd8, 0xff, 0xd9]), [2, 3], 20, 30).text();
  expect(pdf.startsWith("%PDF-1.4")).toBe(true);
  const offsets = [...pdf.matchAll(/^(\d{10}) 00000 n $/gmu)].map((m) => Number(m[1]));
  expect(offsets).toHaveLength(5);
  offsets.forEach((offset, i) => expect(pdf.slice(offset).startsWith(`${i + 1} 0 obj`)).toBe(true));
  expect(pdf.slice(Number(pdf.match(/startxref\n(\d+)/u)![1])).startsWith("xref")).toBe(true);
});
