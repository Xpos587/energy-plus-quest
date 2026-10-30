# Project work

Follow [repository storage and retention policy](docs/REPOSITORY-HYGIENE.md).
Keep temporary renders, browser checks, scratch scripts and logs inside this
checkout's `.tmp-work/<purpose>/`; do not invent project-specific folders in
`~/.cache`, `~/.local/state`, or beside the checkout. Container/package-manager
stores remain tool-managed, not an alternative home for project outputs.

Before completing work, run `bun run clean:stale` and `bun run check:storage`.
Keep current necessary sources/media/specifications and the latest deliverables,
not historical copies. Put reusable scripts in `scripts/`, not temporary storage.
