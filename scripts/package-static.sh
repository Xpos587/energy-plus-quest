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
curl -fsS "http://127.0.0.1:4174/specialprojects/energy-plus-quest/$asset_path" -o /dev/null
curl -fsS "http://127.0.0.1:4174/specialprojects/energy-plus-quest/fonts/$(basename "$font_path")" -o /dev/null

echo "Static archive verified: release/energy-plus-quest-static.zip"
