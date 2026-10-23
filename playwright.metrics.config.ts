import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: /metrics\.spec\.ts|unified\.spec\.ts|scenes\/journey\.spec\.ts/,
  outputDir: ".tmp-work/metrics/browser-results",
  workers: 2,
  reporter: "line",
  use: { baseURL: "http://127.0.0.1:4215", trace: "retain-on-failure" },
  projects: [
    [320, 568],
    [375, 667],
    [768, 1024],
    [1440, 900],
    [844, 390],
  ].map(([width, height]) => ({
    name: `${width}x${height}`,
    use: { viewport: { width, height } },
  })),
  webServer: {
    command: "node node_modules/vite/bin/vite.js --config vite.ui.config.ts --host 127.0.0.1 --port 4215 --strictPort",
    url: "http://127.0.0.1:4215",
    reuseExistingServer: false,
  },
});
