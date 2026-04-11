# Bookmark Manager モノレポ

このリポジトリはモノレポ構成です。

## 構成

- `api/` - FastAPI のバックエンド本体とテスト
- `frontend/` - Nuxt 4 の SPA
- `chrome-extension/` - Chrome 拡張のクイック追加ポップアップ
- `specs/` - 要件・設計・タスク・テスト観点の整理
- `specs/api/` - API 仕様
- `specs/frontend/` - フロントエンド仕様
- `docs/commit-policy.md` - コミット規約

## API

バックエンドは `api/` 配下にあります。

フロントエンドは `frontend/` 配下にある Nuxt 4 の SPA です。

リポジトリルートから API を起動するには次を実行します。

```bash
cd api
api-dev
```

`frontend/` 配下からフロントエンドを起動するには次を実行します。

```bash
bun install
bun run dev
```

リポジトリルートから両方まとめて起動する場合は次を実行します。

```bash
./run-local.sh
```

Docker で起動する場合は次を実行します。

```bash
docker compose up --build
```

Docker 起動時は 1 つのコンテナでフロントエンドが `http://127.0.0.1:3000`、API が `http://127.0.0.1:8000` で利用できます。

API テストは次を実行します。

```bash
python -m pytest -q
```

pytest は `api/tests` を対象に収集するよう設定しています。

## テスト仕様

要件・設計・タスク・テスト観点の整理は `specs/` にあります。

- このリポジトリでの作業前提として、`AGENTS.md` と `specs/llm-reading-guide.md` を先に読み、公式 LLM 参照資料も確認してください。
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

## Frontend Tests

`frontend/` 配下ではユニットテストと E2E テストを分けて実行します。

```bash
cd frontend
bun run test
bun run e2e
bun run e2e:run
bun run e2e:headed
```

`e2e:run` は結果ログを `.artifacts/playwright-e2e.log` に保存します。
`e2e:headed` はブラウザを開いて実行します。

## ローカル URL

- フロントエンド: `http://127.0.0.1:3001`
- API: `http://127.0.0.1:8001`

## Chrome 拡張

`chrome-extension/` を Chrome の unpacked extension として読み込みます。
ポップアップでは現在タブのタイトルと URL を自動入力し、API 経由でそのまま DB に登録します。
API Base URL のデフォルトは `http://localhost:8001` です。
