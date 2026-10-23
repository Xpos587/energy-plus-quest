import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  testMatch: /shared-interaction\.spec\.ts/,
  outputDir: ".tmp-work/shared-interaction-results",
  workers: 2,
  reporter: "line",
  use: { baseURL: "http://127.0.0.1:4211", trace: "retain-on-failure" },
  projects: [[320,568], [390,844], [844,390], [768,1024], [1440,900]].map(([width,height]) => ({name:`${width}x${height}`, use:{viewport:{width,height}}})),
  webServer: { command: "bun run dev -- --host 127.0.0.1 --port 4211 --strictPort", url:"http://127.0.0.1:4211", reuseExistingServer:false },
});
