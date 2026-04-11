# Frontend build stage
FROM oven/bun:1.3.12-alpine AS frontend-build

WORKDIR /app/frontend

RUN apk add --no-cache bash

COPY frontend/package.json frontend/bun.lock ./
RUN bun install

COPY frontend/nuxt.config.ts ./nuxt.config.ts
COPY frontend/tsconfig.json ./tsconfig.json
COPY frontend/app ./app
COPY frontend/public ./public
RUN bun run build


# Runtime stage
FROM oven/bun:1.3.12-alpine

WORKDIR /app

RUN apk add --no-cache python3 py3-pip
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

COPY api /app/api
COPY --from=frontend-build /app/frontend/.output /app/frontend/.output
COPY --from=frontend-build /app/frontend/node_modules /app/frontend/node_modules
COPY --from=frontend-build /app/frontend/package.json /app/frontend/package.json

# Runtime defaults; users can override these with `docker run -e` or compose
ENV DATABASE_URL=/data/bookmark.db

EXPOSE 3000 8000

CMD ["sh", "-c", "fastapi run api/main.py --host 0.0.0.0 --port 8000 & API_PID=$!; cd /app/frontend; bun run start & FRONTEND_PID=$!; trap 'kill $API_PID $FRONTEND_PID 2>/dev/null || true' INT TERM EXIT; wait $API_PID $FRONTEND_PID"]
