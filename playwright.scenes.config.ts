import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/scenes",
  outputDir: ".tmp-work/ui-preview-results",
  fullyParallel: true,
  workers: 2,
  reporter: "line",
  use: { baseURL: "http://127.0.0.1:4202", trace: "retain-on-failure" },
  projects: [
    { name: "phone-320", use: { viewport: { width: 320, height: 568 } } },
    { name: "phone-375", use: { viewport: { width: 375, height: 667 } } },
    { name: "phone-390", use: { viewport: { width: 390, height: 844 } } },
    { name: "landscape", use: { viewport: { width: 844, height: 390 } } },
    { name: "tablet", use: { viewport: { width: 768, height: 1024 } } },
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
  ],
  webServer: {
    command: "node node_modules/vite/bin/vite.js --config vite.ui.config.ts --host 127.0.0.1 --port 4202 --strictPort",
    url: "http://127.0.0.1:4202/scenes.html",
    reuseExistingServer: false,
  },
});
