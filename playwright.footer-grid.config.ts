import {defineConfig} from '@playwright/test';
import base from './playwright.choice-buttons.config';
export default defineConfig({...base,testMatch:'result-footer-grid.spec.ts',projects:[...base.projects!,{name:'624x794',use:{viewport:{width:624,height:794}}}]});
