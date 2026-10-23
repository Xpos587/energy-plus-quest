import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  testMatch: /(?:final-branches|shared-interaction|scenario-outcomes)\.spec\.ts/,
  outputDir: ".tmp-work/global-polish",
  workers: 2,
  reporter: "line",
  timeout: 60000,
  use: {baseURL:"http://127.0.0.1:4215", trace:"retain-on-failure"},
  projects: [
    {name:"phone",use:{viewport:{width:390,height:844}}},
    {name:"desktop",use:{viewport:{width:1440,height:900}}},
  ],
  webServer:{command:"bun run dev -- --host 127.0.0.1 --port 4215 --strictPort",url:"http://127.0.0.1:4215",reuseExistingServer:false},
});
