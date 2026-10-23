import { defineConfig } from '@playwright/test';
export default defineConfig({
 testDir: './tests', testMatch: 'scene-zoom.spec.ts', outputDir: '.tmp-work/scene-zoom',
 workers: 2, reporter: 'line', timeout: 45000,
 use: {baseURL: 'http://127.0.0.1:4231', reducedMotion: 'reduce'},
 projects: [...[[320,568],[780,992],[1440,900]].map(([width,height])=>({name:`${width}x${height}`,use:{viewport:{width,height}}})),
 {name:'touch-phone',use:{viewport:{width:390,height:844},isMobile:true,hasTouch:true}}],
 webServer:{command:'bun run dev -- --host 127.0.0.1 --port 4231 --strictPort',url:'http://127.0.0.1:4231',reuseExistingServer:true},
});
