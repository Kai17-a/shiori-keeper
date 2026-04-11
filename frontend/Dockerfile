FROM oven/bun:1.3.12-alpine AS build

WORKDIR /app

RUN apk add --no-cache bash

COPY frontend/package.json frontend/bun.lock /app/
COPY frontend/nuxt.config.ts /app/nuxt.config.ts
COPY frontend/tsconfig.json /app/tsconfig.json
COPY frontend/app /app/app
COPY frontend/public /app/public

RUN bun install
RUN bun run build

FROM oven/bun:1.3.12-alpine

WORKDIR /app

COPY --from=build /app/.output /app/.output
COPY --from=build /app/node_modules /app/node_modules
COPY --from=build /app/package.json /app/package.json
COPY --from=build /app/nuxt.config.ts /app/nuxt.config.ts
COPY --from=build /app/app /app/app
COPY --from=build /app/public /app/public
COPY --from=build /app/tsconfig.json /app/tsconfig.json

ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

EXPOSE 3000

CMD ["bun", "run", "start"]
