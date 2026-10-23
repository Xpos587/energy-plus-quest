import { defineConfig } from '@playwright/test';
import base from './playwright.choice-buttons.config';
export default defineConfig({...base,testMatch:'warehouse-panorama-live.spec.ts',outputDir:'.tmp-work/panorama-live',projects:base.projects!.filter(p=>['1440x900','wide-desktop','320x568','touch'].includes(p.name!))});
