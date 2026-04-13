# Bookmark Manager

ブラウザのブックマークを一覧・整理するためのアプリケーションです。
OSS 利用者向けの利用方法をこの `README.md` にまとめ、開発手順は [DEVELOPMENT.md](DEVELOPMENT.md) に分離しています。

## 使い方

公開イメージを使う場合は、GitHub Container Registry から pull して実行します。

```bash
docker pull ghcr.io/kai17-a/bookmark-manager:latest
docker run --rm -p 3000:3000 -p 8000:8000 \
  -e DATABASE_URL=/data/bookmark.db \
  -v "$(pwd)/data:/data" \
  ghcr.io/kai17-a/bookmark-manager:latest
```

起動後はフロントエンドを `http://127.0.0.1:3000`、API を `http://127.0.0.1:8000` で利用できます。

`docker compose` を使う場合は、次のような構成を使います。

```yaml
services:
  bookmark-manager:
    container_name: bookmark-manager
    image: ghcr.io/kai17-a/bookmark-manager:latest
    environment:
      DATABASE_URL: /data/bookmark.db
    ports:
      - "3001:3000"
      - "8005:8000"
    volumes:
      - ./data:/data
```

フロントエンドは `/api` を起点に呼び出し、nginx がそれをコンテナ内の FastAPI (`127.0.0.1:8000`) に転送する。
そのため、`docker compose` でホスト側の公開ポートを `3001:3000` と `8005:8000` に変えても、ブラウザからの API 呼び出しは `http://localhost:3001/api/...` のまま動作する。
API 直アクセスは `http://localhost:8005/...` で行える。

GitHub Packages の Docker image 公開機能を使う場合は、別途ワークフローを用意してください。
`GITHUB_TOKEN` に `packages: write` 権限が付くように設定してください。

## リポジトリ構成

- [api/README.md](api/README.md) - FastAPI のバックエンド本体とテスト
- [frontend/README.md](frontend/README.md) - Nuxt 4 の SPA
- `chrome-extension/` - Chrome 拡張のクイック追加ポップアップ
- `specs/` - 要件・設計・タスク・テスト観点の整理
- [docs/commit-policy.md](docs/commit-policy.md) - コミット規約
- [DEVELOPMENT.md](DEVELOPMENT.md) - ローカル開発手順

## ドキュメント

要件・設計・タスク・テスト観点の整理は `specs/` にあります。

- [LLM 読み学習ガイド](specs/llm-reading-guide.md)
- [Nuxt modules LLM](https://nuxt.com/modules/llms)
- [Nuxt LLM full](https://nuxt.com/llms-full.txt)
- [Nuxt UI LLM](https://ui.nuxt.com/llms.txt)
- [Nuxt UI LLM full](https://ui.nuxt.com/llms-full.txt)
- [Vue LLM full](https://vuejs.org/llms-full.txt)
- [API 仕様](specs/api/README.md)
- [総覧](specs/test-observations/README.md)
- [API](specs/test-observations/api/test-observations.md)
- [Frontend](specs/test-observations/frontend/test-observations.md)
- [Frontend E2E](specs/test-observations/frontend-e2e/test-observations.md)
- [コミット規約](docs/commit-policy.md)

`specs/requirements.md` は要件の上位定義、`specs/api/` は API 挙動の詳細、`specs/frontend/` は画面と操作の詳細です。
