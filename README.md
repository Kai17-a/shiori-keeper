# Bookmark Manager モノレポ

このリポジトリはモノレポ構成です。

## 構成

- `api/` - FastAPI のバックエンド本体とテスト
- `frontend/` - Nuxt 4 の SPA
- `chrome-extension/` - Chrome 拡張のクイック追加ポップアップ
- `specs/` - 実装メモとタスク管理

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

Docker 起動時はフロントエンドが `http://127.0.0.1:3000`、API が `http://127.0.0.1:8000` で利用できます。

API テストは次を実行します。

```bash
python -m pytest -q
```

pytest は `api/tests` を対象に収集するよう設定しています。

## ローカル URL

- フロントエンド: `http://127.0.0.1:3001`
- API: `http://127.0.0.1:8001`

## Chrome 拡張

`chrome-extension/` を Chrome の unpacked extension として読み込みます。
ポップアップでは現在タブのタイトルと URL を自動入力し、API 経由でそのまま DB に登録します。
API Base URL のデフォルトは `http://localhost:8001` です。
