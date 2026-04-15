# 技術設計書: ブックマーク管理API

## 概要

本ドキュメントは、ブックマーク管理システムの技術設計を定義する。
PythonでAPIサーバーを実装し、SQLiteをデータストアとして使用する。
加えて、Rust の `batch` で RSS 実行と Discord webhook 通知を担当する。
ブックマーク・RSS フィード・フォルダ・タグ・設定の CRUD と、ブックマークへのタグ付与・解除、RSS 実行による Discord webhook 通知を提供する。

### 技術スタック

- 言語: Python 3.11+
- Webフレームワーク: FastAPI
- バリデーション: Pydantic v2
- DB: SQLite（標準ライブラリ `sqlite3` を使用）
- テスト: pytest + hypothesis

---

## アーキテクチャ

### レイヤー構成

```
Client (HTTP)
    │
    ▼
┌─────────────────────────────┐
│  Router Layer (FastAPI)     │
│  api/routers/               │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Service Layer              │
│  api/services/              │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Repository Layer           │
│  api/repositories/          │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  SQLite Database            │
└─────────────────────────────┘
```

### バッチ処理

```
SQLite Database
    │
    ▼
┌─────────────────────────────┐
│  Batch Job (Rust)           │
│  batch/                     │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Discord Webhook            │
└─────────────────────────────┘
```

- `batch` は RSS フィードを読み込み、未送信の記事だけを webhook に通知する
- `batch` は送信済み記事を `rss_feed_articles` に記録し、重複通知を避ける
- `batch` は webhook 送信失敗時にリトライし、最終失敗時は処理を中断する
- `batch` は API サーバーとは別プロセスとして動作し、HTTP ルートは持たない

### ディレクトリ構成

```
shiori-keeper/
├── api/
│   ├── main.py
│   ├── database.py
│   ├── model/
│   ├── routers/
│   ├── services/
│   └── repositories/
├── frontend/
├── chrome-extension/
└── specs/
    ├── requirements.md
    ├── design.md
    ├── tasks.md
    └── test-observations/
├── batch/
│   ├── Cargo.toml
│   └── src/
│       ├── db.rs
│       ├── lib.rs
│       ├── main.rs
│       └── webhook.rs
```

---

## API

### エンドポイント

| Method | Path                            | 説明                     |
| ------ | ------------------------------- | ------------------------ |
| POST   | `/bookmarks`                    | ブックマーク作成         |
| GET    | `/bookmarks`                    | ブックマーク一覧取得     |
| GET    | `/bookmarks/{id}`               | ブックマーク詳細取得     |
| PATCH  | `/bookmarks/{id}`               | ブックマーク部分更新     |
| DELETE | `/bookmarks/{id}`               | ブックマーク削除         |
| POST   | `/bookmarks/{id}/tags`          | ブックマークへタグ付与   |
| DELETE | `/bookmarks/{id}/tags/{tag_id}` | ブックマークからタグ解除 |
| POST   | `/folders`                      | フォルダ作成             |
| GET    | `/folders`                      | フォルダ一覧取得         |
| PATCH  | `/folders/{id}`                 | フォルダ更新             |
| DELETE | `/folders/{id}`                 | フォルダ削除             |
| POST   | `/tags`                         | タグ作成                 |
| GET    | `/tags`                         | タグ一覧取得             |
| PATCH  | `/tags/{id}`                    | タグ更新                 |
| DELETE | `/tags/{id}`                    | タグ削除                 |
| PUT    | `/settings/webhook`             | Discord webhook 設定     |
| GET    | `/settings/webhook`             | Discord webhook 取得     |
| POST   | `/rss-feeds/{id}/execute`       | RSS 実行と webhook 通知  |
| GET    | `/health`                       | ヘルスチェック           |

### レスポンス方針

- 正常系は各リソースの Pydantic モデルで返す
- 一覧取得は `items` / `total` / `page` / `per_page` を含むページングレスポンスを返す
- エラーは `{"detail": ...}` 形式を返す
- バリデーションエラーは FastAPI の標準形式を使う

---

## データモデル

### テーブル

```sql
CREATE TABLE IF NOT EXISTS folders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bookmarks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT    NOT NULL,
    title       TEXT    NOT NULL,
    description TEXT,
    folder_id   INTEGER REFERENCES folders(id) ON DELETE SET NULL,
    is_favorite INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS rss_feeds (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT    NOT NULL,
    title       TEXT    NOT NULL,
    description TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS app_settings (
    key         TEXT    PRIMARY KEY,
    value       TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tags (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS bookmark_tags (
    bookmark_id INTEGER NOT NULL REFERENCES bookmarks(id) ON DELETE CASCADE,
    tag_id      INTEGER NOT NULL REFERENCES tags(id)      ON DELETE CASCADE,
    PRIMARY KEY (bookmark_id, tag_id)
);
```

### 設計上の決定

- `folders.id` は削除時に `bookmarks.folder_id` を `NULL` にする
- `bookmark_tags` はブックマーク・タグ削除時に連動削除する
- SQLite の外部キー制約は接続時に `PRAGMA foreign_keys = ON` で有効化する
- `bookmarks.url`、`rss_feeds.url`、`folders.name` はアプリ側で重複を除去し、DB一意性を保つ
- `app_settings` はアプリ全体設定のキーバリューストアとして扱う
- `default_webhook_url` は Discord webhook URL だけを許可する
- RSS 実行 API は `default_webhook_url` 未設定時に 400 を返す
- RSS 実行の送信本体は `batch` が担当し、API サーバーは RSS 実行の要求受付と永続化結果の参照を担当する
- `batch` は `rss_feed_articles` を参照して既送信記事を除外し、送信成功後に同テーブルへ記録する

### Pydanticスキーマ

```python
class BookmarkCreate(BaseModel):
    url: AnyHttpUrl
    title: str
    description: str | None = None
    folder_id: int | None = None
    tag_ids: list[int] | None = None

class BookmarkUpdate(BaseModel):
    url: AnyHttpUrl | None = None
    title: str | None = None
    description: str | None = None
    folder_id: int | None = None
    tag_ids: list[int] | None = None

class FolderCreate(BaseModel):
    name: str
    description: str | None = None

class FolderUpdate(BaseModel):
    name: str
    description: str | None = None

class TagCreate(BaseModel):
    name: str
    description: str | None = None

class TagUpdate(BaseModel):
    name: str
    description: str | None = None

class TagAttach(BaseModel):
    tag_id: int

class RSSFeedCreate(BaseModel):
    url: AnyHttpUrl
    title: str
    description: str | None = None

class RSSFeedUpdate(BaseModel):
    url: AnyHttpUrl | None = None
    title: str | None = None
    description: str | None = None

class SettingsWebhookUpdate(BaseModel):
    webhook_url: AnyHttpUrl

class TagResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

class FolderResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime

class BookmarkResponse(BaseModel):
    id: int
    url: str
    title: str
    description: str | None
    folder_id: int | None
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime

class BookmarkListResponse(BaseModel):
    items: list[BookmarkResponse]
    total: int
    page: int
    per_page: int

class RSSFeedResponse(BaseModel):
    id: int
    url: str
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime

class RSSFeedListResponse(BaseModel):
    items: list[RSSFeedResponse]
    total: int
    page: int
    per_page: int

class RSSFeedExecuteResponse(BaseModel):
    feed_id: int
    title: str
    webhook_url: str
    delivered: bool

class SettingsWebhookResponse(BaseModel):
    webhook_url: str
```

---

## 運用上の補足

- 未知の SQLite エラーは 500 に変換する
- アプリ起動時に初期化処理を実行する
- RSS 実行は実際の RSS/Atom フィード URL のみ許可する
- Webhook は現時点では Discord のみを正式対応とする
