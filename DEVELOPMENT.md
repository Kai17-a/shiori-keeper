# 開発ガイド

このドキュメントはローカル開発向けの手順をまとめる。
OSS 利用者向けの案内は [README.md](./README.md) を参照する。

## ローカル起動

### API

```bash
cd api
api-dev
```

`api-dev` は `uvicorn` を使って起動する。

### Frontend

```bash
mise install
cd frontend
bun install
bun run dev
```

`bun` は `mise.toml` で `1.1.38` に固定している。ローカルで `bun run build` を実行する場合も `mise exec bun@1.1.38 -- bun run build` のように同じ版を使う。

### 両方まとめて起動

```bash
./run-local.sh
```

### GitHub Actions をローカル実行

GitHub Actions のワークフローをローカルで再現する場合は `mise exec act -- ...` を使う。

```bash
./scripts/run-github-actions.sh
```

`act` は `mise.toml` で管理しているので、先に `mise install` を実行しておく。
デフォルトでは `.github/workflows/pr-tests.yml` の `pull_request` イベントを実行する。
別のワークフローを試す場合は、ワークフローパスとイベント名を渡す。

```bash
./scripts/run-github-actions.sh .github/workflows/release-on-tag.yml push
```

### Docker を使う場合

```bash
./scripts/docker-compose-up-fresh.sh
```

`docker-compose.yml` はローカル開発向けのサンプルで、`Dockerfile` をビルドして起動する。

```yaml
services:
  bookmark-manager:
    container_name: bookmark-manager
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: /data/bookmark.db
      API_BASE_URL: http://127.0.0.1:8005
    ports:
      - "3001:3000"
      - "8005:8000"
    volumes:
      - ./data:/data
```

Docker 起動時は API を `fastapi run api/main.py` で起動し、1 つのコンテナでフロントエンドと API を利用できる。`API_PORT` を変えない限り、コンテナ内ではフロントが `http://127.0.0.1:8000` の API を使う。
`API_PORT` を変更した場合は、コンテナ内の API 待受ポートとフロントエンドの既定接続先もその値に追従する。

## Push 前チェック

ローカルから `git push` する前に同じ検査を走らせるには、次を設定する。

```bash
./scripts/setup-repo.sh
```

この設定を入れると、この workspace の `.git/config` にだけ `core.hooksPath` が記録される。
`.githooks/pre-push` が実行され、コミットメッセージの Conventional Commits 検査に加えて、API の `ruff check`、API テスト、frontend の unit test が push 前に走る。

### Git 運用

- ブランチの作成単位は `git flow` に基づく
- 作業は `main` から直接ではなく、用途に応じたブランチを切って進める
- 変更が完了したら、そのブランチ上でコミットしてから共有する

push 前に API / frontend / E2E をまとめて手動実行したい場合は次を使う。

```bash
./scripts/run-all-tests.sh
```

この workspace でコードやテストを修正したら、最後に変更を commit する。

## テスト

### API

```bash
cd api
python -m pytest -q
```

### Frontend

```bash
cd frontend
bun run test
bun run e2e
bun run e2e:run
bun run e2e:headed
```

`e2e:run` は結果ログを `.artifacts/playwright-e2e.log` に保存する。
`e2e:headed` はブラウザを開いて実行する。
`e2e:run` は `API_BASE_URL=http://127.0.0.1:8001` で API と frontend を起動し、内部的に同じ値を `NUXT_PUBLIC_API_BASE_URL` として扱う。`http://127.0.0.1:8001` と `http://127.0.0.1:3001` を使って E2E を実行する。

## ローカル URL

- フロントエンド: `http://127.0.0.1:3001`
- API: `http://127.0.0.1:8001`
