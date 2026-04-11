# LLM 読み学習ガイド

このドキュメントは、このリポジトリで作業する LLM が先に読むことを想定した入口である。
Nuxt、Python、Nuxt UI、TypeScript の実装方針を短く集約し、参照順を明確にする。

## 読む順番

1. [README.md](/home/kaito/workspaces/bookmark-manager/README.md)
1. [要件定義](./requirements.md)
1. [技術設計](./design.md)
1. [フロントエンド概要](./frontend/overview.md)
1. [フロントエンド制約](./frontend/constraints.md)
1. [API概要](./api/overview.md)
1. [APIデータと制約](./api/data-and-constraints.md)
1. 公式 LLM 参照資料
   - https://nuxt.com/modules/llms
   - https://nuxt.com/llms-full.txt
   - https://ui.nuxt.com/llms.txt
   - https://ui.nuxt.com/llms-full.txt
   - https://vuejs.org/llms-full.txt

## 技術別の重点

### Nuxt

- フロントエンドは `frontend/` 配下の Nuxt 4 SPA である
- `ssr: false` のクライアントサイドアプリとして動作する
- 画面は `app/pages/` のファイルベースルーティングで構成する
- 共通シェルは `app/layouts/default.vue` に集約する
- Nuxt の公式 LLM 参照資料も確認する
  - https://nuxt.com/modules/llms
  - https://nuxt.com/llms-full.txt

### Nuxt UI

- UI は `@nuxt/ui` を使って構成する
- ダッシュボード型レイアウト、サイドバー、フォーム、モーダル、トーストを中心に組み立てる
- 既存の Nuxt UI テーマとレスポンシブ制約を壊さない
- Nuxt UI の公式 LLM 参照資料も確認する
  - https://ui.nuxt.com/llms.txt
  - https://ui.nuxt.com/llms-full.txt

### TypeScript

- フロントエンドの実装は TypeScript 前提で統一する
- `frontend/app/composables/` と `frontend/app/utils/` に責務を分ける
- 型定義は `frontend/app/types/` に寄せる
- API との入出力は型を明示し、`any` に逃がさない
- Vue の公式 LLM 参照資料も確認する
  - https://vuejs.org/llms-full.txt

### Python

- バックエンドは `api/` 配下の Python 3.13+ の FastAPI サービスである
- ルータ、サービス、リポジトリ、モデルのレイヤー分離を維持する
- DB は SQLite を使用し、外部キー制約とエラー処理を明示的に扱う
- テストは `pytest` と `hypothesis` を中心に見る

## 参照すべき実装ファイル

### フロントエンド

- [Nuxt 設定](/home/kaito/workspaces/bookmark-manager/frontend/nuxt.config.ts)
- [ルート一覧](/home/kaito/workspaces/bookmark-manager/frontend/app/pages/)
- [レイアウト](/home/kaito/workspaces/bookmark-manager/frontend/app/layouts/default.vue)
- [共通コンポーネント](/home/kaito/workspaces/bookmark-manager/frontend/app/components/)
- [Composable](/home/kaito/workspaces/bookmark-manager/frontend/app/composables/)
- [ユーティリティ](/home/kaito/workspaces/bookmark-manager/frontend/app/utils/)
- [型定義](/home/kaito/workspaces/bookmark-manager/frontend/app/types/)

### API

- [Python プロジェクト設定](/home/kaito/workspaces/bookmark-manager/api/pyproject.toml)
- [アプリケーション本体](/home/kaito/workspaces/bookmark-manager/api/main.py)
- [DB 初期化](/home/kaito/workspaces/bookmark-manager/api/database.py)
- [ルータ群](/home/kaito/workspaces/bookmark-manager/api/routers/)
- [サービス層](/home/kaito/workspaces/bookmark-manager/api/services/)
- [リポジトリ層](/home/kaito/workspaces/bookmark-manager/api/repositories/)
- [モデル定義](/home/kaito/workspaces/bookmark-manager/api/model/)

## 期待する読み方

- 先に仕様を読む
- 次に実装ファイルを読む
- 迷ったら既存の仕様と実装の整合性を優先する
- 新しい実装は、既存の構造と命名を壊さずに追加する
