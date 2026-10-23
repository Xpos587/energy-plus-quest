import { defineConfig } from "@playwright/test";
import base from "./playwright.scene-zoom.config";
export default defineConfig({ ...base, testMatch: "result-stability.spec.ts", projects: [{ name: "result-stability" }], outputDir: ".tmp-work/result-stability" });
