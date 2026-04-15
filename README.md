# Shiori Keeper

ブラウザのブックマークを一覧・整理するためのアプリケーションです。
この `README.md` はインストール方法だけをまとめ、開発手順や設計資料は [DEVELOPMENT.md](DEVELOPMENT.md) と `specs/` に分離しています。

## インストール

公開イメージを使う場合は、GitHub Container Registry から pull して実行します。

```bash
docker pull ghcr.io/kai17-a/browser-bookmark-manager:latest
docker run --rm -p 3000:3000 -p 8000:8000 \
  -e DATABASE_URL=/data/bookmarks.db \
  -v "$(pwd)/data:/data" \
  ghcr.io/kai17-a/browser-bookmark-manager:latest
```

起動後はフロントエンドを `http://127.0.0.1:3000`、API を `http://127.0.0.1:8000` で利用できます。

`docker compose` を使う場合は、次のような構成を使います。

```yaml
services:
  shiori-keeper:
    container_name: shiori-keeper
    image: ghcr.io/kai17-a/browser-bookmark-manager:latest
    environment:
      DATABASE_URL: /data/bookmarks.db
    ports:
      - "3000:3000"
      - "8000:8000"
    volumes:
      - ./data:/data
```
