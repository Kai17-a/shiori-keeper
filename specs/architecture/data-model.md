# DB 定義

このドキュメントは、現在の SQLite スキーマを Mermaid ER 図で表したものである。
詳細な API レスポンススキーマや制約は [API データと制約](../components/api/data-and-constraints.md) を参照する。

## ER 図

```mermaid
erDiagram
    FOLDERS ||--o{ BOOKMARKS : "folder_id"
    BOOKMARKS ||--o{ BOOKMARK_TAGS : "bookmark_id"
    TAGS ||--o{ BOOKMARK_TAGS : "tag_id"
    RSS_FEEDS ||--o{ RSS_FEED_ARTICLES : "feed_id"

    FOLDERS {
        INTEGER id PK
        TEXT name UK
        TEXT description
        TEXT created_at
    }

    BOOKMARKS {
        INTEGER id PK
        TEXT url UK
        TEXT title
        TEXT description
        INTEGER folder_id FK
        INTEGER is_favorite
        TEXT created_at
        TEXT updated_at
    }

    TAGS {
        INTEGER id PK
        TEXT name UK
        TEXT description
    }

    BOOKMARK_TAGS {
        INTEGER bookmark_id PK, FK
        INTEGER tag_id PK, FK
    }

    RSS_FEEDS {
        INTEGER id PK
        TEXT url UK
        TEXT title
        TEXT description
        INTEGER notify_webhook_enabled
        TEXT created_at
        TEXT updated_at
    }

    RSS_FEED_ARTICLES {
        INTEGER id PK
        INTEGER feed_id FK
        TEXT url
        TEXT title
        TEXT created_at
        DATETIME published
    }

    APP_SETTINGS {
        TEXT key PK
        TEXT value
        INTEGER rss_periodic_execution_enabled
        TEXT updated_at
    }

    SCHEMA_MIGRATIONS {
        varchar version PK
    }
```

## リレーション

| From | To | Cardinality | Delete behavior |
| --- | --- | --- | --- |
| `bookmarks.folder_id` | `folders.id` | many-to-one | `ON DELETE SET NULL` |
| `bookmark_tags.bookmark_id` | `bookmarks.id` | many-to-one | `ON DELETE CASCADE` |
| `bookmark_tags.tag_id` | `tags.id` | many-to-one | `ON DELETE CASCADE` |
| `rss_feed_articles.feed_id` | `rss_feeds.id` | many-to-one | `ON DELETE CASCADE` |

## 一意制約と index

| Name | Target | Purpose |
| --- | --- | --- |
| `idx_bookmarks_url_unique` | `bookmarks(url)` | ブックマーク URL の重複防止 |
| `idx_rss_feeds_url_unique` | `rss_feeds(url)` | RSS フィード URL の重複防止 |
| `idx_rss_feed_articles_feed_url_unique` | `rss_feed_articles(feed_id, url)` | 同一 feed 内の記事 URL 重複防止 |
| `idx_bookmarks_created_id` | `bookmarks(created_at DESC, id DESC)` | ブックマーク一覧の新着順 |
| `idx_bookmarks_folder_created_id` | `bookmarks(folder_id, created_at DESC, id DESC)` | フォルダ絞り込み一覧 |
| `idx_bookmarks_favorite_created_id` | `bookmarks(is_favorite, created_at DESC, id DESC)` | お気に入り一覧 |
| `idx_bookmark_tags_tag_bookmark` | `bookmark_tags(tag_id, bookmark_id)` | タグ絞り込み一覧 |
| `idx_rss_feeds_title_id` | `rss_feeds(title ASC, id ASC)` | RSS フィード一覧 |
| `idx_rss_feed_articles_feed_published_id` | `rss_feed_articles(feed_id, published DESC, id DESC)` | RSS 記事の published 順 |
| `idx_rss_feed_articles_feed_published_null_id` | `rss_feed_articles(feed_id, published IS NULL, published DESC, id DESC)` | published 未設定記事を含む RSS 記事一覧 |

## 設定値

`app_settings` はアプリ全体設定を保持する key-value テーブルである。

| Key | Meaning |
| --- | --- |
| `default_webhook_url` | RSS 手動実行や batch 通知で使う webhook URL |
| `rss_periodic_execution_enabled` | batch による RSS 定期実行の有効/無効 |
| `rss_webhook_notification_enabled` | batch 実行時の webhook 通知の有効/無効 |
