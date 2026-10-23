import { resolve } from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { optimizedImages } from "./scripts/optimized-images";

export default defineConfig({
  base: "./",
  cacheDir: ".tmp-work/scenes-02-05-vite",
  plugins: [optimizedImages(), react()],
  build: {
    outDir: "build/scenes",
    rolldownOptions: { input: { scenes: resolve(import.meta.dirname, "scenes.html") } },
  },
});
