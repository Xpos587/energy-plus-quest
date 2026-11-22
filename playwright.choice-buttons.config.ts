import { defineConfig } from '@playwright/test';
const dev = {
 testDir: './tests', workers: 2, reporter: 'line', timeout: 45000,
 use: {baseURL: 'http://127.0.0.1:4231', reducedMotion: 'reduce'},
 webServer:{command:'bun run dev -- --host 127.0.0.1 --port 4231 --strictPort',url:'http://127.0.0.1:4231',reuseExistingServer:true},
} as const;
export default defineConfig({
  ...dev,
  testMatch: ['scene-choice-buttons.spec.ts', 'warehouse-result-layout.spec.ts'],
  outputDir: '.tmp-work/choice-buttons/test-results',
  projects: [...[[320,568],[780,992],[1440,900]].map(([width,height])=>({name:`${width}x${height}`,use:{viewport:{width,height}}})),
    {name:'touch-phone',use:{viewport:{width:390,height:844},isMobile:true,hasTouch:true}},
    {name:'landscape',use:{viewport:{width:844,height:390}}}, {name:'wide-desktop',use:{viewport:{width:1920,height:1080}}}],
});
