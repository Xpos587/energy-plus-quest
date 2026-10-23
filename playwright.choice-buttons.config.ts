import { defineConfig } from '@playwright/test';
import base from './playwright.scene-zoom.config';
export default defineConfig({
  ...base,
  testMatch: ['scene-choice-buttons.spec.ts', 'warehouse-result-layout.spec.ts'],
  outputDir: '.tmp-work/choice-buttons/test-results',
  projects: [...base.projects!, {name:'landscape',use:{viewport:{width:844,height:390}}}, {name:'wide-desktop',use:{viewport:{width:1920,height:1080}}}],
});
