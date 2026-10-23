import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: /ux-matrix\.spec\.ts/,
  outputDir: ".tmp-work/type-landscape-matrix/results",
  workers: 4,
  fullyParallel: true,
  timeout: 150_000,
  reporter: [
    ["line"],
    ["json", { outputFile: ".tmp-work/type-landscape-matrix/coverage-report.json" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:4173",
    reducedMotion: "reduce",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  projects: [
    [844, 390],
  ].map(([width, height]) => ({
    name: `${width}x${height}`,
    use: { viewport: { width, height } },
  })),
  webServer: {
    command: "bun run dev -- --host 127.0.0.1 --port 4173 --strictPort",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: true,
  },
});
