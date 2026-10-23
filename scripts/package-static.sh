#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
release_dir="$project_root/release"
verification_root=$(mktemp -d)
container_name=""
cleanup() {
  if [ -n "$container_name" ]; then podman rm -f "$container_name" >/dev/null 2>&1 || true; fi
  rm -rf "$verification_root"
}
trap cleanup EXIT INT TERM
for tool in bun zip unzip curl; do command -v "$tool" >/dev/null; done
cd "$project_root"
# The customer reference uses external scripts. Explicitly override old debug
# environment flags; this is minification, not a custom obfuscator.
case "${1:-}" in
  "") build_dir="$verification_root/build" ;;
  --build-to-dist) build_dir="$verification_root/build" ;;
  --stage-only) build_dir="$verification_root/build" ;;
  *) printf '%s\n' 'Usage: package-static.sh [--build-to-dist|--stage-only]' >&2; exit 2 ;;
esac
if [ "$#" -gt 1 ]; then
  printf '%s\n' 'Usage: package-static.sh [--build-to-dist]' >&2
  exit 2
fi
BUILD_MINIFY=true BUILD_SINGLEFILE=false bun run build:app --outDir "$build_dir"
stage="$verification_root/stage"
bun scripts/stage-static.mjs "$build_dir" "$stage" deploy/nginx-joydelivery.conf
(cd "$stage" && zip -q -r "$verification_root/energy-plus-quest-static.zip" .)
webroot="$verification_root/webroot"
mkdir -p "$webroot/specprojects/joydelivery"
unzip -q "$verification_root/energy-plus-quest-static.zip" -d "$webroot/specprojects/joydelivery"
# Test a real subdirectory host, including an intentionally conflicting global
# JS/CSS handler. The scoped game location must take precedence over it.
{
  printf '%s\n' 'server {' '  listen 80;' '  server_name localhost;' '  location ~* \.(js|css)$ { return 418; }'
  sed 's|/path/to/webroot|/usr/share/nginx/html|g' "$stage/nginx-joydelivery.conf"
  printf '%s\n' '  location / { return 404; }' '}'
} > "$verification_root/default.conf"
if [ "${1:-}" != "--stage-only" ]; then
  command -v podman >/dev/null
  container_name="quest-static-check-$$"
  podman run -d --network=pasta --name "$container_name" -p 127.0.0.1::80 \
    -v "$webroot:/usr/share/nginx/html:ro,Z" \
    -v "$verification_root/default.conf:/etc/nginx/conf.d/default.conf:ro,Z" \
    docker.io/library/nginx:1.27-alpine >/dev/null
  podman exec "$container_name" nginx -t
  port=$(podman port "$container_name" 80/tcp | sed 's/.*://')
  url="http://127.0.0.1:$port/specprojects/joydelivery/"
  attempt=0
  until curl -fsS "$url" -o /dev/null; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 30 ]; then podman logs "$container_name"; exit 1; fi
    sleep 0.1
  done
  bun scripts/verify-static-runtime.mjs "$url" "$webroot/specprojects/joydelivery"
fi
if [ "${1:-}" = "--build-to-dist" ] || [ "${1:-}" = "--stage-only" ]; then
  # Deploy exactly the validated archive contents, not Vite's public-directory copy.
  if [ -d "$project_root/dist" ]; then mv "$project_root/dist" "$verification_root/previous-dist"; fi
  if ! cp -R "$stage" "$project_root/dist"; then
    rm -rf "$project_root/dist"
    if [ -d "$verification_root/previous-dist" ]; then mv "$verification_root/previous-dist" "$project_root/dist"; fi
    exit 1
  fi
fi
mkdir -p "$release_dir"
# Keep the previous delivered archive available for rollback.
if [ -f "$release_dir/energy-plus-quest-static.zip" ]; then
  cp "$release_dir/energy-plus-quest-static.zip" "$release_dir/energy-plus-quest-static.previous.zip"
fi
mv "$verification_root/energy-plus-quest-static.zip" "$release_dir/energy-plus-quest-static.zip"
printf '%s\n' 'Verified archive: release/energy-plus-quest-static.zip' 'Before publishing, also run the browser gameplay check described in README-DEPLOY.txt.'
