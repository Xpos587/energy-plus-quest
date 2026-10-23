# Build from the lean source checkout; public media comes from checksummed releases.
FROM ghcr.io/astral-sh/uv:0.11.9 AS uv

FROM docker.io/oven/bun:1.4.3 AS builder
COPY --from=uv /uv /usr/local/bin/uv
# The font plugin runs the PEP 723 subsetter through uv.
ENV UV_PYTHON=3.12.11 UV_PYTHON_DOWNLOADS=automatic
RUN uv python install 3.12.11
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
# Keep the large verified media layer reusable when only application code changes.
COPY media-artifacts.json ./
COPY scripts/media-artifacts.ts ./scripts/media-artifacts.ts
RUN bun scripts/media-artifacts.ts

COPY index.html tsconfig.json vite.config.ts repository-budget.json ./
COPY public/ ./public/
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY deploy/ ./deploy/
COPY docs/ ./docs/
RUN bun run build:app --outDir build
RUN bun scripts/stage-static.mjs build dist deploy/nginx-joydelivery.conf

FROM docker.io/library/nginx:1.27-alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist/ /usr/share/nginx/html/
RUN printf '%s\n' \
  'server {' \
  '  listen 80;' \
  '  root /usr/share/nginx/html;' \
  '  index index.html;' \
  '' \
  '  gzip on;' \
  '  gzip_vary on;' \
  '  gzip_proxied any;' \
  '  gzip_comp_level 5;' \
  '  gzip_min_length 1024;' \
  '  gzip_types text/css application/javascript application/json image/svg+xml;' \
  '' \
  '  # Revalidate documents so a release immediately points to its new assets.' \
  '  location = /quest-cache.js {' \
  '    add_header Cache-Control "no-cache";' \
  '    try_files $uri =404;' \
  '  }' \
  '  location ~* \.html$ {' \
  '    add_header Cache-Control "no-cache";' \
  '    try_files $uri =404;' \
  '  }' \
  '' \
  '  # Generated variants and Vite bundles change their URL with their content.' \
  '  location ~* "^/assets/[^/]+-[a-z0-9_-]{8,}\.(?:css|js|mjs|jpg|jpeg|png|gif|svg|ico|webp|avif|woff2?|ttf|otf|mp4|webm|mp3|ogg|wav)$" {' \
  '    add_header Cache-Control "public, max-age=31536000, immutable";' \
  '    try_files $uri =404;' \
  '  }' \
  '' \
  '  # Original artwork remains replaceable at the same path.' \
  '  location ~* \.(?:css|js|mjs|json|map|wasm|txt|xml|pdf|webmanifest|jpg|jpeg|png|gif|svg|ico|webp|avif|woff2?|ttf|otf|mp4|webm|mp3|ogg|wav)$ {' \
  '    add_header Cache-Control "public, max-age=86400";' \
  '    try_files $uri =404;' \
  '  }' \
  '' \
  '  location /assets/ {' \
  '    add_header Cache-Control "public, max-age=86400";' \
  '    try_files $uri =404;' \
  '  }' \
  '' \
  '  location / {' \
  '    add_header Cache-Control "no-cache";' \
  '    try_files $uri $uri/ /index.html;' \
  '  }' \
  '}' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
