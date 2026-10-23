# Lean repository and current media

The Git repository contains source code, text documentation, review receipts and `media-artifacts.json`. Binary media and generated releases do not belong in Git history. Old history was intentionally replaced; old commit IDs are obsolete.

## Current files, not historical archives

Measured on 23 October 2026: tracked source/text content is **27.2 MiB**, the packed Git directory is **5.7 MiB** (also verified by a fresh remote clone). The current media set is **1,340.3 MiB across 26 external release assets**; it is intentionally reported separately, not hidden in the Git-size figure. All published archive sizes and GitHub SHA-256 digests matched the manifest. A real published archive was downloaded, extracted and file-verified successfully. Temporary upload archives were deleted after that verification.

Current image/video/font masters, scenario illustrations, latest report images/PDF and the pending warehouse geometry are stored as checksummed assets in the GitHub Release named by `media-artifacts.json`. These are the exact current files, not backups of old experiments. Each archive and each file has a byte count and SHA-256. No quality settings or decoded media pixels were changed by moving their storage.

Run `bun run media:hydrate` after cloning. Existing matching files are reused without downloading. Run `bun run media:verify` to check every recorded file. Downloads stream into temporary storage, are verified before extraction, and are deleted after hydration. Archive entries are limited to the manifest's regular files; traversal, links and unexpected entries are rejected.

The local game and latest PDF remain available at their existing paths. A Git checkout alone intentionally does not contain binary assets; `bun run dev` and build commands hydrate them automatically. Media publishing must finish before pushing code that references a new release. Keep the current release while any current code depends on it; never overwrite an archive at an existing digest URL.

To update media: prepare regular-file-only tar.gz archives of changed/current root-relative paths, publish them under a new current release name, and update each file/archive size and SHA-256 in the manifest. Run `bun run media:verify`, build/stage, and verify the runtime before publishing the source change. Once no current manifest references an old media release, remove that obsolete release rather than accumulating historical copies. Raster quality changes require visual review; relocating media does not authorize recompression.

## Enforced Git limits

`repository-budget.json` is authoritative:

- Tracked content: at most **40 MiB**.
- Git directory: at most **64 MiB**.
- Individual tracked file: at most **1 MiB**.
- Binary image/video/PDF/font/native masters and `dist` are forbidden in the index.
- Generated local output across `.tmp-work`, `build`, `release`: at most **2 GiB**.
- Image codec cache: at most **256 MiB**, encoded results only; no duplicated source buffers.

The pre-commit hook checks staged objects, not unstaged files. Enable it after cloning with `bun run setup:hooks`. CI checks the committed tree. New exceptions require a concrete reason and must still satisfy the total repository limit.

## Build and deployment

`Containerfile` builds from the lean source checkout: frozen Bun install, verified media hydration, TypeScript/Vite build, runtime-only staging, then nginx. Generated `dist` is ignored and never committed. The build context excludes local masters and reports; media is downloaded inside the builder from the public current release. No token is put into the image.

Local preview: `bun run preview:current` serves the current `dist` on `http://127.0.0.1:4344/`. Build a fresh static directory before using preview in a new clone. The deploy workflow builds/pushes the container and triggers the existing Dokploy application on pushes to `main`.

Current task status and unaccepted candidates: [handoff](plans/handoffs/2026-10-23-transfer.md). Moving media does not approve the warehouse or helicopter artwork. Copy remains frozen.
