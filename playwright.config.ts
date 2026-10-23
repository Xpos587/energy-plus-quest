import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  reporter: "line",
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "retain-on-failure",
  },
  projects: [
    ...[
      { name: "small-phone", width: 320, height: 568 },
      { name: "iphone-14-pro-max", width: 430, height: 932 },
      { name: "phone-landscape", width: 844, height: 390 },
      { name: "tablet-landscape", width: 1180, height: 820 },
      { name: "wide-monitor", width: 2560, height: 1440 },
    ].map(({ name, width, height }) => ({
      name: `${name}-chromium`,
      testMatch: /(?:layout|viewport)\.spec\.ts/,
      use: { ...devices["Desktop Chrome"], viewport: { width, height } },
    })),
    {
      name: "desktop-chromium",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1440, height: 900 },
      },
    },
    {
      name: "mobile-chromium",
      use: {
        ...devices["Pixel 5"],
        viewport: { width: 390, height: 844 },
      },
    },
    {
      name: "mobile-toolbar-chromium",
      testMatch: /(?:layout|viewport)\.spec\.ts/,
      use: {
        ...devices["Pixel 5"],
        viewport: { width: 390, height: 700 },
      },
    },
    {
      name: "iphone-se-chromium",
      testMatch: /(?:layout|viewport)\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 375, height: 667 },
      },
    },
    {
      name: "windows-125-chromium",
      testMatch: /(?:layout|viewport)\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1152, height: 720 },
      },
    },
    {
      name: "windows-140-chromium",
      testMatch: /(?:layout|viewport)\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1024, height: 643 },
      },
    },
    {
      name: "tablet-chromium",
      testMatch: /(?:layout|viewport)\.spec\.ts/,
      use: {
        ...devices["Galaxy Tab S4"],
        viewport: { width: 820, height: 1180 },
      },
    },
  ],
  webServer: {
    command: "bun run dev -- --host 127.0.0.1 --port 4173",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: true,
  },
});
