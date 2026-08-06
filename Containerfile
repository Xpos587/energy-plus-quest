# Energy+ Quest — static Vite SPA
# Multi-stage: bun build → nginx alpine serve

# syntax=docker/dockerfile:1
FROM docker.io/oven/bun:1 AS builder

WORKDIR /app

# Copy lockfile and package manifest for layer caching
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Copy source and build
COPY . .
RUN bun run build

# ── runtime stage ────────────────────────────────────────────
FROM docker.io/library/nginx:1.27-alpine

# Copy built static assets
COPY --from=builder /app/dist /usr/share/nginx/html

# SPA fallback config
RUN printf 'server {\n\
  listen 3000;\n\
  root /usr/share/nginx/html;\n\
  index index.html;\n\
  location / {\n\
    try_files $uri $uri/ /index.html;\n\
  }\n\
}\n' > /etc/nginx/conf.d/default.conf

# Run as non-root
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && chown nginx:nginx /var/run/nginx.pid
USER nginx

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
