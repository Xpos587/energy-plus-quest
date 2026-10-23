import { defineConfig } from '@playwright/test';
import base from './playwright.footer-grid.config';
export default defineConfig({...base, testMatch: ['edge-layout.spec.ts','scene-choice-buttons.spec.ts','result-footer-grid.spec.ts'], outputDir: '.tmp-work/edge-layout/results'});
