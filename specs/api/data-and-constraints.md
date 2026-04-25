# データと制約

## データモデル

### テーブル

```sql
CREATE TABLE IF NOT EXISTS folders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE,
    description TEXT,
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

CREATE UNIQUE INDEX IF NOT EXISTS idx_bookmarks_url_unique ON bookmarks(url);

CREATE TABLE IF NOT EXISTS rss_feeds (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT    NOT NULL,
    title       TEXT    NOT NULL,
    description TEXT,
    notify_webhook_enabled INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_rss_feeds_url_unique ON rss_feeds(url);

CREATE TABLE IF NOT EXISTS rss_feed_articles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    feed_id     INTEGER NOT NULL REFERENCES rss_feeds(id) ON DELETE CASCADE,
    url         TEXT    NOT NULL,
    title       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    published   DATETIME
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_rss_feed_articles_feed_url_unique
    ON rss_feed_articles(feed_id, url);

CREATE TABLE IF NOT EXISTS app_settings (
    key         TEXT    PRIMARY KEY,
    value       TEXT    NOT NULL,
    rss_periodic_execution_enabled INTEGER NOT NULL DEFAULT 0,
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
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
- `BookmarkFavoriteUpdate`
- `RSSFeedCreate`
- `RSSFeedUpdate`
- `RSSFeedExecuteResponse`
- `SettingsWebhookUpdate`
- `SettingsWebhookResponse`
- `SettingsWebhookPingRequest`
- `SettingsWebhookPingResponse`
- `SettingsRssExecutionUpdate`
- `SettingsRssExecutionResponse`
- `SettingsRssWebhookNotificationUpdate`
- `SettingsRssWebhookNotificationResponse`
- `FolderCreate`
- `FolderUpdate`
- `TagCreate`
- `TagUpdate`
- `TagAttach`
- `BookmarkResponse`
- `BookmarkListResponse`
- `RSSFeedResponse`
- `RSSFeedListResponse`
- `RSSFeedArticleResponse`
- `RSSFeedArticleListResponse`
- `FolderResponse`
- `TagResponse`
- `DashboardMetricsResponse`
- `ErrorResponse`

## レスポンススキーマ

| Schema                      | Fields                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------ |
| `BookmarkResponse`          | `id`, `url`, `title`, `description`, `folder_id`, `is_favorite`, `tags`, `created_at`, `updated_at` |
| `BookmarkListResponse`      | `items`, `total`, `page`, `per_page`, `total_pages`                                  |
| `RSSFeedResponse`           | `id`, `url`, `title`, `description`, `notify_webhook_enabled`, `created_at`, `updated_at` |
| `RSSFeedListResponse`       | `items`, `total`, `page`, `per_page`, `total_pages`                                  |
| `RSSFeedArticleResponse`    | `id`, `feed_id`, `url`, `title`, `published`, `created_at`                           |
| `RSSFeedArticleListResponse`| `items`, `total`, `page`, `per_page`, `total_pages`                                  |
| `RSSFeedExecuteResponse`    | `feed_id`, `title`, `webhook_url`, `delivered`, `message`                             |
| `SettingsWebhookResponse`   | `webhook_url`                                                                        |
| `SettingsWebhookPingResponse` | `pong`                                                                             |
| `SettingsRssExecutionResponse` | `enabled`                                                                          |
| `SettingsRssWebhookNotificationResponse` | `enabled`                                                               |
| `FolderResponse`            | `id`, `name`, `description`, `created_at`                                             |
| `TagResponse`               | `id`, `name`, `description`                                                          |
| `DashboardMetricsResponse`   | `bookmarks_total`, `folders_total`, `tags_total`, `favorites_total`, `rss_feeds_total` |
| `ErrorResponse`             | `detail`                                                                             |

## 制約

- `bookmarks.url` は HTTP/HTTPS URL のみ受け付ける
- `rss_feeds.url` は HTTP/HTTPS URL のみ受け付ける
- `bookmarks.title` は必須
- `rss_feeds.title` は必須
- `rss_webhook_notification_enabled` は RSS 定期実行時の webhook 通知全体可否を表す
- `rss_webhook_notification_enabled` の既定値は `false` である
- `rss_feeds.notify_webhook_enabled` は batch による RSS 定期実行時の webhook 通知可否を表す
- `rss_feeds.notify_webhook_enabled` の既定値は `true` である
- `folders.name` と `tags.name` は重複を許可しない
- `bookmarks.url` は一意である
- `rss_feeds.url` は一意である
- `bookmarks.folder_id` は存在しないフォルダを参照できない
- フォルダ削除時は関連ブックマークの `folder_id` を `NULL` にする
- ブックマークまたはタグ削除時は `bookmark_tags` を連動削除する
- SQLite の外部キー制約は `PRAGMA foreign_keys = ON` で有効化する
- DB 障害は 500 として返す
- `settings/webhook` は Discord または Microsoft Teams webhook URL のみを保存する
- `settings/webhook/ping` は送信前確認用の疎通確認 API である
- `settings/rss-execution` は RSS 定期実行フラグを保存する
- `settings/rss-webhook-notification` は RSS 定期実行時の webhook 通知可否を保存する
- `rss_feed_articles.url` は同一 feed 内で一意である

## 実装上の補足

- `/bookmarks` の一覧は `folder_id`、`tag_id`、`q`、`is_favorite`、`sort`、`page`、`per_page` を受け付ける
- `/bookmarks` の `sort` は `id`、`url`、`title`、`description`、`folder_id`、`is_favorite`、`created_at`、`updated_at` を受け付ける
- `/bookmarks` の `sort` は複数指定でき、左から右へ優先度が高い
- `/bookmarks` の `sort` に存在しない項目が指定された場合は 422 を返す
- `/bookmarks/{id}` は詳細取得と更新対象を兼ねる
- `GET /folders/{id}` は単一フォルダを ID で取得する
- `GET /tags/{id}` は単一タグを ID で取得する
- `DELETE /bookmarks` は `id`、`url`、`title`、`description`、`folder_id`、`is_favorite` の任意組み合わせで対象ブックマークを特定する
- `DELETE /bookmarks` は指定した条件を AND で評価する
- `DELETE /bookmarks` は条件未指定時に 422 を返す
- `PATCH /bookmarks/by-url` は URL で対象ブックマークを特定する
- `PATCH /folders/{id}` と `PATCH /tags/{id}` は partial update として `name` の省略を許可する
- `/bookmarks/{id}/tags` はタグ付与、`DELETE /bookmarks/{id}/tags/{tag_id}` は解除を担当する
- `/metrics/dashboard` はブックマーク、フォルダ、タグ、お気に入り、RSS フィードの総数を返す
- `/rss-feeds` は RSS フィードの CRUD を担当する
- `/rss-feeds/{id}/articles` は保存済み RSS 記事を返す
- `/rss-feeds/{id}/articles` は `q`、`published_from`、`published_to`、`page`、`per_page` を受け付ける
- `GET /settings/webhook` は現在の webhook URL を返す
- `PUT /settings/webhook` は保存済み webhook を更新する
- `POST /settings/webhook/ping` は webhook 到達確認を行う
- `GET /settings/rss-execution` は RSS 定期実行の現在値を返す
- `PUT /settings/rss-execution` は RSS 定期実行の有効/無効を更新する
- `GET /settings/rss-webhook-notification` は RSS 定期実行時の webhook 通知可否の現在値を返す
- `PUT /settings/rss-webhook-notification` は RSS 定期実行時の webhook 通知可否を更新する
- `POST /rss-feeds/{id}/execute` は API プロセスが RSS を実行し、登録済み Discord または Microsoft Teams webhook に通知する
- `POST /rss-feeds/{id}/execute` は webhook URL 未設定時に 400 を返す
- `POST /rss-feeds/{id}/execute` は新規記事がない場合も `delivered: true` を返し、`message` に "No new articles found." を含める
- RSS 手動実行の通知送信と `rss_feed_articles` への送信済み記録は API が担当する
- RSS 手動実行は `rss_feeds.notify_webhook_enabled` の値に関わらず webhook 通知を行う
- `batch` は RSS 定期実行が有効な場合だけ巡回し、`rss_feeds.notify_webhook_enabled` が有効な RSS フィードについて未送信記事の通知と `rss_feed_articles` への送信済み記録を担当する
- `batch` は `rss_feed_articles` の `url` を参照して、既に送信済みの記事を webhook 対象から除外する
- `batch` は webhook 送信成功後に `rss_feed_articles` へ記事を追記する
- `BookmarkListResponse.total_pages` はクライアントのページング UI が使えるように返す
