#!/bin/sh
set -eu
if [ "$#" -eq 0 ] || [ ! -f "$1" ]; then
  echo "Usage: bun run test:e2e:quick tests/<file>.spec.ts [Playwright options]" >&2
  exit 2
fi
case "$1" in
  *.spec.ts) ;;
  *) echo "Choose a .spec.ts file first; use test:e2e for the full matrix." >&2; exit 2 ;;
esac
exec bunx --no-install playwright test --project=desktop-chromium --workers=2 --max-failures=1 --output=.tmp-work/playwright-quick "$@"
