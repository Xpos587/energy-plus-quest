import { resolve } from "node:path";
import { normalizePath, type WatchOptions } from "vite";

export function devWatchOptions(root: string): WatchOptions {
  // Anchor to this checkout: a worktree may itself live under .tmp-work/.
  return {
    ignored: [".tmp-work", "build", "release", "test-results", "playwright-report"]
      .map(directory => `${normalizePath(resolve(root, directory))}/**`),
    // Do not transform a temporarily empty module during truncate-then-write saves.
    awaitWriteFinish: { stabilityThreshold: 200, pollInterval: 20 },
  };
}
