#!/bin/sh

set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
release_dir="$project_root/release"
archive_path="$release_dir/energy-plus-quest-static.zip"
verification_root=$(mktemp -d)
server_pid=""

cleanup() {
  if [ -n "$server_pid" ]; then
    kill "$server_pid" 2>/dev/null || true
  fi
  rm -rf "$verification_root"
}

trap cleanup EXIT INT TERM

cd "$project_root"
bun run build

if rg -n -i 'fetch\(|XMLHttpRequest|WebSocket|EventSource|https?://|//[a-z0-9.-]+/|/api/' \
  src public -g '*.ts' -g '*.tsx' -g '*.js' -g '*.jsx' -g '*.css' -g '*.html'; then
  echo "External runtime dependency found in project source" >&2
  exit 1
fi

if rg -n -P '(?<!\.)/(assets|brand|fonts)/' dist/index.html dist/assets; then
  echo "Root-relative project resource found in production output" >&2
  exit 1
fi

mkdir -p "$release_dir"
rm -f "$archive_path"
(
  cd dist
  zip -q -r "$archive_path" .
)

nested_root="$verification_root/specialprojects/energy-plus-quest"
mkdir -p "$nested_root"
unzip -q "$archive_path" -d "$nested_root"

busybox httpd -f -p 127.0.0.1:4174 -h "$verification_root" &
server_pid=$!

attempt=0
until curl -fsS "http://127.0.0.1:4174/specialprojects/energy-plus-quest/" -o "$verification_root/index.html"; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 20 ]; then
    echo "Static archive did not start from a nested path" >&2
    exit 1
  fi
  sleep 0.1
done

asset_path=$(sed -n 's/.*src="\.\/\([^"]*\.js\)".*/\1/p' "$verification_root/index.html" | head -n 1)
font_path=$(find "$nested_root/fonts" -name '*.woff2' -print | head -n 1)
test -n "$asset_path"
test -n "$font_path"
test -f "$nested_root/README-DEPLOY.txt"
test -f "$nested_root/fonts/README.md"
curl -fsS "http://127.0.0.1:4174/specialprojects/energy-plus-quest/$asset_path" -o /dev/null
curl -fsS "http://127.0.0.1:4174/specialprojects/energy-plus-quest/fonts/$(basename "$font_path")" -o /dev/null

if rg -n -i "(src|href)=[\"'][[:space:]]*https?://|url\\([\"']?[[:space:]]*https?://|localhost|127\\.0\\.0\\.1|hypcat\\.net|dokploy" \
  "$nested_root" -g '*.html' -g '*.css' -g '*.js'; then
  echo "External runtime dependency found in static archive" >&2
  exit 1
fi

bun scripts/verify-static-runtime.mjs \
  "http://127.0.0.1:4174/specialprojects/energy-plus-quest/"

echo "Static archive verified: release/energy-plus-quest-static.zip"
