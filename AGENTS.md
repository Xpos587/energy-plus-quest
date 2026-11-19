# Project work

Follow [repository storage and retention policy](docs/REPOSITORY-HYGIENE.md).
Use the [development feedback workflow](docs/DEVELOPMENT.md): targeted checks
while editing, full acceptance before release. Prefer `go-task verify:quick` and
`bun run test:e2e:quick tests/<file>.spec.ts` for iteration; neither replaces the
release checks. For long tasks, use native completion or an exact child PID,
never `pgrep -f` on command text or repeated sleeps. Keep production image caches
between edits and inspect existing preview/profiling modes before batch renders.
Keep temporary renders, browser checks, scratch scripts and logs inside this
checkout's `.tmp-work/<purpose>/`; do not invent project-specific folders in
`~/.cache`, `~/.local/state`, or beside the checkout. Container/package-manager
stores remain tool-managed, not an alternative home for project outputs.

Before completing work, run `bun run clean:stale`.
Keep current necessary sources/media/specifications and the latest deliverables,
not historical copies. Put reusable scripts in `scripts/`, not temporary storage.
