import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: '.', testMatch: 'preview.spec.ts', reporter: 'line',
  outputDir: '/tmp/energy-shared-ui-v2-test-results',
  use: { baseURL: 'http://127.0.0.1:4184', viewport: { width: 1440, height: 900 } },
});
