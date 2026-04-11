# Bookmark Manager モノレポ

このリポジトリはモノレポ構成です。

## 構成

- [api/README.md](api/README.md) - FastAPI のバックエンド本体とテスト
- [frontend/README.md](frontend/README.md) - Nuxt 4 の SPA
- `chrome-extension/` - Chrome 拡張のクイック追加ポップアップ
- `specs/` - 要件・設計・タスク・テスト観点の整理
- `specs/api/` - API 仕様
- `specs/frontend/` - フロントエンド仕様
- `docs/commit-policy.md` - コミット規約

## 利用方法

### 開発者向け

ローカル開発は [DEVELOPMENT.md](/home/kaito/workspaces/bookmark-manager/DEVELOPMENT.md) を参照する。

### OSS 利用者向け

公開イメージを使う場合は、GitHub Container Registry から pull して実行する。

```bash
docker pull ghcr.io/<github-owner>/bookmark-manager:latest
docker run --rm -p 3000:3000 -p 8000:8000 \
  -e DATABASE_URL=/data/bookmark.db \
  -e API_BASE_URL=http://127.0.0.1:8000 \
  -e NUXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 \
  -v "$(pwd)/data:/data" \
  ghcr.io/<github-owner>/bookmark-manager:latest
```

実際に使うときの `docker-compose.yml` は次の形です。

```yaml
services:
    bookmark-manager:
        container_name: bookmark-manager
        image: ghcr.io/<github-owner>/bookmark-manager:latest
        environment:
            DATABASE_URL: /data/bookmark.db
            API_BASE_URL: http://127.0.0.1:8000
            NUXT_PUBLIC_API_BASE_URL: http://127.0.0.1:8000
        ports:
            - "3000:3000"
            - "8000:8000"
        volumes:
            - ./data:/data
```

GitHub の Docker image 公開機能を使う場合は、別途ワークフローを用意してください。
`GITHUB_TOKEN` に `packages: write` 権限が付くように設定してください。

## テスト仕様

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
