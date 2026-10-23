import process from "node:process";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";
import { defineConfig } from "vitest/config";
import { optimizedImages } from "./scripts/optimized-images";
import { optimizedFonts } from "./scripts/optimized-fonts";
import { gameCache } from "./scripts/game-cache";
import { frozenUiSources } from "./scripts/frozen-ui";

// BUILD_SINGLEFILE=true — вся игра в одном index.html (js/css встроены инлайн).
// Обход для площадки заказчика: их заливка спецпроектов теряет отдельные
// .js-файлы, поэтому отдаём один самодостаточный html.
const singleFile = process.env.BUILD_SINGLEFILE === "true";

export default defineConfig({
  base: "./",
  plugins: singleFile
    ? [
        frozenUiSources({source:process.env.FROZEN_UI_SOURCE_DIR,capture:process.env.FROZEN_UI_CAPTURE_DIR}),
        optimizedImages(),
        optimizedFonts(),
        gameCache(),
        react(),
        viteSingleFile({ useRecommendedBuildConfig: false }),
      ]
    : [frozenUiSources({source:process.env.FROZEN_UI_SOURCE_DIR,capture:process.env.FROZEN_UI_CAPTURE_DIR}), optimizedImages(), optimizedFonts(), gameCache(), react()],
  build: {
    // BUILD_MINIFY=false — читаемый бандл для передачи заказчику (их серверная
    // поддержка пропускает минифицированный js как «подозрительный»).
    minify: process.env.BUILD_MINIFY === "false" ? false : "esbuild",
    // Картинки/шрифты остаются отдельными файлами — они у заказчика заливаются
    // нормально, теряются только скрипты.
    ...(singleFile ? { assetsInlineLimit: 0, cssCodeSplit: false } : {}),
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
  },
});
