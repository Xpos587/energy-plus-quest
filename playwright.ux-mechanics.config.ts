import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: /ux-mechanics\.spec\.ts/,
  outputDir: ".tmp-work/ux-mechanics",
  workers: 2,
  reporter: "line",
  timeout: 120000,
  use: { baseURL: "http://127.0.0.1:4231", reducedMotion: "reduce", trace: "retain-on-failure" },
  projects: [[320,568], [375,667], [780,992], [844,390], [1440,900]].map(([width,height]) => ({
    name: `${width}x${height}`, use: { viewport: {width,height} },
  })),
  webServer: {
    command: "bun run dev -- --host 127.0.0.1 --port 4231 --strictPort",
    url: "http://127.0.0.1:4231", reuseExistingServer: true,
  },
});
