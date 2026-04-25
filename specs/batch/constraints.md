# 制約

## 実行条件

- `batch` は API サーバーとは別プロセスとして実行する
- `DATABASE_URL` は SQLite DB ファイルパスとして扱う
- `DATABASE_URL` 未指定時は `data/data.db` を使う
- DB スキーマは API と dbmate migration が用意したものを前提とする
- `batch` 自身は migration を適用しない

## 設定

- `rss_periodic_execution_enabled` が無効な場合、RSS 巡回は行わない
- `rss_webhook_notification_enabled` が無効な場合、RSS 巡回と webhook 通知は行わない
- `default_webhook_url` が未設定の場合、RSS 巡回と webhook 通知は行わない
- フィード単位の `rss_feeds.notify_webhook_enabled` が無効な RSS フィードは通知対象にしない

## RSS と記事記録

- RSS URL は `reqwest::Url::parse` で解釈できる必要がある
- 取得結果は `rss::Channel::read_from` で RSS channel として解析できる必要がある
- item の `link` がない場合は `"(no link)"` を URL として扱う
- item の `title` がない場合は `"(no title)"` をタイトルとして扱う
- item の `pub_date` がない場合は `"(no published date)"` を published として扱う
- item の summary は `description`、`content` の順で採用し、どちらもない場合は `"(no summary)"` とする
- 送信済み判定は `rss_feed_articles.url` で行う
- 送信済み記事の記録は `INSERT OR IGNORE` を使い、重複 URL を二重登録しない

## 後方互換

- `rss_feeds.notify_webhook_enabled` 列がない DB では、全 RSS フィードを通知対象として扱う
- `rss_feed_articles.published` 列がない DB では、`published` を除外して送信済み記事を記録する

## webhook

- 現在の batch payload は Discord 形式の `username`、`content`、`embeds` を送る
- webhook URL のサービス種別検証は batch 側では行わず、DB に保存済みの `default_webhook_url` をそのまま使う
- webhook 送信は最大 3 回リトライする
- リトライ間隔は 500ms とする
- webhook の 4xx/5xx 応答はフィード単位の失敗として扱う
