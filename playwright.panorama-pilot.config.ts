import { defineConfig } from '@playwright/test';
import base from './playwright.choice-buttons.config';
export default defineConfig({...base,testMatch:'warehouse-panorama-pilot.spec.ts',projects:base.projects!.filter(p=>['1440x900','wide-desktop'].includes(p.name!))});
