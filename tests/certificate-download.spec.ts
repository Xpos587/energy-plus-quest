import { expect, test } from "@playwright/test";
import sharp from "sharp";

for (const profile of ["student", "professional"] as const) {
  for (const type of ["future", "energy", "empathy", "efficiency"] as const) {
    if (profile === "professional" && type === "future") continue;
    test(`${profile}/${type} downloads a complete story JPEG`, async ({ page }, info) => {
      await page.goto("/");
      // Isolate the seven reachable results without replaying the same five stages.
      await page.evaluate(async ({ profile, type }) => {
        const load = (url: string) => import(/* @vite-ignore */ url);
        // Reuse the loaded Vite dependency URL, including its current optimizer hash.
        const dependency = (name: string) => performance.getEntriesByType("resource").map(e => e.name).find(url => new URL(url).pathname.endsWith(`/${name}`))!;
        const React = (await load(dependency("react.js"))).default;
        const { createRoot } = (await load(dependency("react-dom_client.js"))).default;
        const { LogistCertificate } = await load("/src/scenes/LogistCertificate.tsx");
        const { logistProfileCopy } = await load("/src/scenes/endingCopy.ts");
        const scores = type === "future"
          ? { energy: -5, empathy: -5, efficiency: -5 }
          : { energy: 0, empathy: 0, efficiency: 0, [type]: 5 };
        const host = document.createElement("div");
        document.body.replaceChildren(host);
        createRoot(host).render(React.createElement(LogistCertificate, {
          profile,
          copy: logistProfileCopy(profile, "arseniy", scores),
          scores,
          onRestart: () => {},
        }));
      }, { profile, type });
      await page.getByRole("button", { name: "Поделиться", exact: true }).click();
      const pending = page.waitForEvent("download");
      await page.getByRole("button", { name: "Скачать картинку для сторис", exact: true }).click();
      const download = await pending;
      expect(await download.failure()).toBeNull();
      expect(download.suggestedFilename()).toBe(`dostavlyaem-radost-${type}.jpg`);
      const path = info.outputPath("certificate.jpg");
      await download.saveAs(path);
      const image = sharp(path);
      expect(await image.metadata()).toMatchObject({ format: "jpeg", width: 1080, height: 1920 });
      // Decode all pixels, not just the header: reject empty, truncated or blank exports.
      const stats = await image.stats();
      expect(stats.channels.some(channel => channel.stdev > 5)).toBe(true);
      await expect(page.getByRole("alert")).toHaveCount(0);
    });
  }
}
