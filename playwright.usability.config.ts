import { defineConfig } from '@playwright/test';
export default defineConfig({
 testDir:'./tests', testMatch:/scene-usability\.spec\.ts/, outputDir:'.tmp-work/scene-usability', workers:2, reporter:'line',
 use:{baseURL:'http://127.0.0.1:4217', reducedMotion:'reduce'},
 projects:[[320,568],[390,844],[844,390],[768,1024],[1440,900]].map(([width,height])=>({name:`${width}x${height}`,use:{viewport:{width,height}}})),
 webServer:{command:'bun run dev -- --host 127.0.0.1 --port 4217 --strictPort',url:'http://127.0.0.1:4217',reuseExistingServer:true},
});
