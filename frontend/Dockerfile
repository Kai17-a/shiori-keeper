FROM oven/bun:1.1.38-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/nuxt.config.ts frontend/app.vue ./
COPY frontend/pages ./pages
COPY frontend/components ./components
COPY frontend/composables ./composables

RUN bun install
RUN bun run generate

FROM nginx:1.27-alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/.output/public /usr/share/nginx/html

EXPOSE 80
