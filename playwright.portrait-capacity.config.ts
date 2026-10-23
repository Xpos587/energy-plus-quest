import {defineConfig} from "@playwright/test";
import base from "./playwright.scene-zoom.config";
export default defineConfig({...base,testMatch:"portrait-result-capacity.spec.ts",projects:[{name:"portrait",use:{viewport:{width:624,height:794}}}],outputDir:".tmp-work/portrait-capacity/test-results"});
