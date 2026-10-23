import { mergeConfig } from "vitest/config";
import base from "./vite.config.ts";

export default mergeConfig(base, { cacheDir: ".tmp-work/ui-vite" });
