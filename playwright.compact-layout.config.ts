import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./tests',testMatch:'compact-header-layout.spec.ts',workers:2,reporter:'line',timeout:30000,
 use:{baseURL:'http://127.0.0.1:4173',reducedMotion:'reduce'},
 projects:[[320,568],[390,844],[624,794],[780,992],[1440,900]].map(([width,height])=>({name:`${width}x${height}`,use:{viewport:{width,height}}})),
 outputDir:'.tmp-work/compact-header/results',
});
