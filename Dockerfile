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
RUN bun run generate


# Runtime stage
FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx \
  && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

COPY api /app/api
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Runtime defaults; users can override these with `docker run -e` or compose
ENV DATABASE_URL=/data/bookmark.db
ENV API_PORT=8000

EXPOSE 3000 8000

CMD ["/app/start.sh"]
