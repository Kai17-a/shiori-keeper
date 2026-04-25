# Frontend build stage
FROM oven/bun:1.3.13-alpine AS frontend-build

WORKDIR /app/frontend

RUN apk add --no-cache bash

COPY frontend/package.json frontend/bun.lock ./
RUN --mount=type=cache,target=/root/.bun \
    bun install

COPY frontend/nuxt.config.ts ./nuxt.config.ts
COPY frontend/tsconfig.json ./tsconfig.json
COPY frontend/app ./app
COPY frontend/public ./public
RUN bun run generate

# Batch build stage
FROM rust:1-slim AS batch-build

ARG TARGETPLATFORM

WORKDIR /app/batch

COPY batch/Cargo.toml batch/Cargo.lock ./
RUN mkdir src && echo "fn main(){}" > src/main.rs

RUN --mount=type=cache,id=cargo-registry-${TARGETPLATFORM},target=/usr/local/cargo/registry,sharing=locked \
    --mount=type=cache,id=cargo-target-${TARGETPLATFORM},target=/app/batch/target,sharing=locked \
    cargo build --release

COPY batch/src ./src

RUN --mount=type=cache,id=cargo-registry-${TARGETPLATFORM},target=/usr/local/cargo/registry,sharing=locked \
    --mount=type=cache,id=cargo-target-${TARGETPLATFORM},target=/app/batch/target,sharing=locked \
    cargo build --release \
    && cp target/release/shiori-keeper-batch /bin/

# Runtime stage
FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx curl \
  && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o ./dbmate https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64
RUN chmod +x dbmate

ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.44/supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=6eb0a8e1e6673675dc67668c1a9b6409f79c37bc \
    SUPERCRONIC=supercronic-linux-amd64

RUN curl -fsSLO "$SUPERCRONIC_URL" \
  && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
  && chmod +x "$SUPERCRONIC" \
  && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
  && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

COPY api /app/api
COPY db /app/db
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html
COPY --from=batch-build /bin/shiori-keeper-batch /usr/local/bin/shiori-keeper-batch

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Runtime defaults; users can override these with `docker run -e` or compose
ENV DATABASE_URL=/data/bookmark.db
ENV API_PORT=8000

EXPOSE 3000 8000

CMD ["/app/start.sh"]
