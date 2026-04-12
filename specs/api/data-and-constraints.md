# データと制約

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
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tags (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS bookmark_tags (
    bookmark_id INTEGER NOT NULL REFERENCES bookmarks(id) ON DELETE CASCADE,
    tag_id      INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (bookmark_id, tag_id)
);
```

## スキーマ

- `BookmarkCreate`
- `BookmarkUpdate`
- `RSSFeedCreate`
- `RSSFeedUpdate`
- `RSSFeedExecuteResponse`
- `SettingsWebhookUpdate`
- `SettingsWebhookResponse`
- `SettingsWebhookPingRequest`
- `SettingsWebhookPingResponse`
- `FolderCreate`
- `FolderUpdate`
- `TagCreate`
- `TagUpdate`
- `TagAttach`
- `BookmarkResponse`
- `BookmarkListResponse`
- `RSSFeedResponse`
- `RSSFeedListResponse`
- `FolderResponse`
- `TagResponse`

## レスポンススキーマ

| Schema                 | Fields                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------ |
| `BookmarkResponse`     | `id`, `url`, `title`, `description`, `folder_id`, `tags`, `created_at`, `updated_at` |
| `BookmarkListResponse` | `items`, `total`, `page`, `per_page`, `total_pages`                                  |
| `RSSFeedResponse`      | `id`, `url`, `title`, `description`, `created_at`, `updated_at`                      |
| `RSSFeedListResponse`  | `items`, `total`, `page`, `per_page`, `total_pages`                                  |
| `RSSFeedExecuteResponse` | `feed_id`, `title`, `webhook_url`, `delivered`                                     |
| `SettingsWebhookResponse` | `webhook_url`                                                                      |
| `SettingsWebhookPingResponse` | `pong`                                                                           |
| `FolderResponse`       | `id`, `name`, `created_at`                                                           |
| `TagResponse`          | `id`, `name`                                                                         |
| `ErrorResponse`        | `detail`                                                                             |

## 制約

- `bookmarks.url` は HTTP/HTTPS URL のみ受け付ける
- `rss_feeds.url` は HTTP/HTTPS URL のみ受け付ける
- `bookmarks.title` は必須
- `rss_feeds.title` は必須
- 全体設定の `webhook_url` は 1 つだけ保持する
- `webhook_url` は Discord webhook URL のみ受け付ける
- `folders.name` と `tags.name` は重複を許可しない
- `bookmarks.url` は正規化後に一意扱いする
- `rss_feeds.url` は正規化後に一意扱いする
- フォルダ削除時は関連ブックマークの `folder_id` を `NULL` にする
- ブックマークまたはタグ削除時は `bookmark_tags` を連動削除する
- SQLite の外部キー制約は `PRAGMA foreign_keys = ON` で有効化する
- DB 障害は 500 として返す

## 実装上の補足

- `/bookmarks` の一覧は `folder_id`、`tag_id`、`q`、`page`、`per_page` を受け付ける
- `/bookmarks/{id}` は詳細取得と更新対象を兼ねる
- `/bookmarks/{id}/tags` はタグ付与、`DELETE /bookmarks/{id}/tags/{tag_id}` は解除を担当する
- `/rss-feeds` は RSS リンクの CRUD を担当する
- `POST /settings/webhook/ping` は登録前の webhook 疎通確認を担当する
- `PUT /settings/webhook` はアプリ全体で使う Discord webhook URL を設定する
- `GET /settings/webhook` は現在の Discord webhook URL を返す
- `PUT /settings/webhook` は保存前に `POST /settings/webhook/ping` で疎通確認できた場合のみ実行する
- `POST /rss-feeds/{id}/execute` は RSS を実行し、登録済み Discord webhook に通知する
- `POST /rss-feeds/{id}/execute` はグローバル `webhook_url` 未設定時に 400 を返す
- フォルダとタグは最大件数制限を持ち、上限超過時は 400 を返す
- `BookmarkListResponse.total_pages` はクライアントのページング UI が使えるように返す
