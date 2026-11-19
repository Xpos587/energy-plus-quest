# Development: short feedback, full acceptance

Run commands from the checkout root. Use `bun run dev` for UI work: it hydrates
verified media and serves original assets without production image encoding.
Do not build a release after every source or CSS edit.

## Choose the check for the change

| Need | Command |
| --- | --- |
| Types | `bun run typecheck` |
| App tests | `bun run test:app` |
| Build/tooling tests | `bun run test:scripts` |
| Compile/bundle without production media encoding or public-directory copies | `bun run build:check` |
| Types, both test suites, compile check | `go-task verify:quick` |
| One E2E file, desktop, two workers, stop after first failure | `bun run test:e2e:quick tests/result-stability.spec.ts` |
| Same file, one named case | `bun run test:e2e:quick tests/result-stability.spec.ts --grep 'compact boat'` |
| One file on mobile | `bun run test:e2e tests/result-stability.spec.ts --project=mobile-chromium` |
| Full E2E project/viewport matrix | `bun run test:e2e` |
| Production media, packaged release and nginx validation | `bun run build` |

`go-task e2e:quick -- tests/result-stability.spec.ts` is the task-runner equivalent.
The quick E2E command requires an existing `.spec.ts` file first; it never falls
back to the whole suite when the target is omitted. Standard Playwright options
follow the file. Use the standard E2E command to choose other projects.

The quick compile output in `.tmp-work/build-check` is **not a deliverable or a
standalone preview**: public media is intentionally not copied. It does not
validate production codecs, packaging or deployment. Keep the full acceptance
commands before handing off a release; quick checks do not replace them.

E2E defaults to two workers; an explicit `--workers=N` can override it. This is a
resource bound, not a measured speed claim. Artifacts go to `.tmp-work/playwright`
or `.tmp-work/playwright-quick`. Run one owner per output directory/server; finish
one run before starting another. Inspect the first real failure before repeating
a broad suite. Retained failure traces remain available for diagnosis.

## Generated files must not reload the game

Both Vite configs exclude this checkout's `.tmp-work`, `build`, `release`,
`test-results` and `playwright-report` trees from watching. Vite already excludes
its configured output and cache directories. The custom patterns are rooted in
the checkout: a checkout inside a parent `.tmp-work` must still watch its source.
This changes file watching, not which assets the server can serve.

## Wait for the job, not for its command text

In Pi, launch long work once and use its native completion notification. Do useful
independent work meanwhile; do not fill the foreground with `sleep` plus log polls.
Do not use `pgrep -f "bun run build:app"` as a completion condition: the observer's
own shell command can match that text and keep the loop alive.

In one shell script, keep the child PID and propagate its real exit status:

```sh
bun run build:check > .tmp-work/build-check.log 2>&1 &
build_pid=$!
# Independent work, if any.
wait "$build_pid"
```

Never stop another session's server or clean its outputs to speed up your job.

## Media and Blender

- The image codec cache already exists at `.tmp-work/image-build-cache/codec-v2`,
  with a 256 MiB bound. Keep it between edits; `clean:generated` intentionally
  removes it. A new worktree has its own cold cache. Do not add another cache or
  duplicate masters to make it warm.
- After a real production build, `.tmp-work/optimized-images.json` records
  `cacheHit` per image. Compare cold/warm elapsed times and receipts in the same
  checkout before changing cache size, codec effort or concurrency. The first
  build's receipts must be inspected before a later build overwrites them.
- Profile Blender scene construction separately from rendering. Validate one
  representative view before a batch. Use an existing generator's preview mode;
  lower render resolution does not fix expensive tree/mesh construction. Preserve
  final geometry, camera, raster quality and acceptance checks.
- Give the model resized previews/contact sheets for comparison, not repeated
  full-resolution masters. Keep masters and detailed acceptance evidence on disk.
  Start independent tasks in new sessions; do not delete active history or expect
  context rollover to shrink the original session file.

Follow the [repository retention policy](REPOSITORY-HYGIENE.md). Preserve current
media and active worktrees. Clean up only after jobs using those files have finished.

## Documentation evidence

Configuration was checked against the installed Vite 8.2 / Playwright 1.62 CLI and
local runtime tests. Official documentation retrieved through Context7 on
2026-11-12 (unversioned/current docs; not a pinned-version guarantee):
[Vite server.watch](https://vite.dev/config/server-options#server-watch),
[Playwright CLI](https://playwright.dev/docs/test-cli).
The `finding-skills` search candidate `jorgeasaurus/agent-skills` /
`playwright-testing/SKILL.md` was read, not installed: its extra Page Objects,
authentication and mandatory link crawler do not fit this workflow change. No new
dependency or downloaded executable was added.
