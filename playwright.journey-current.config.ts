import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: "journey-current.spec.ts",
  fullyParallel: true,
  workers: 3,
  timeout: 120_000,
  expect: { timeout: 10_000 },
  reporter: "line",
  use: {
    baseURL: "http://127.0.0.1:4173",
    reducedMotion: "reduce",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "320x568", use: { viewport: { width: 320, height: 568 } } },
    { name: "390x844", use: { viewport: { width: 390, height: 844 } } },
    { name: "1440x900", use: { viewport: { width: 1440, height: 900 } } },
  ],
  outputDir: ".tmp-work/journey-current/results",
  webServer: {
    command: "bun run dev -- --host 127.0.0.1 --port 4173",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: true,
  },
});
