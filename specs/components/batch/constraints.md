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
- `webhook_endpoints` に webhook URL が 1 件も登録されていない場合、RSS 巡回と webhook 通知は行わない
- フィード単位の `rss_feeds.notify_webhook_enabled` が無効な RSS フィードは通知対象にしない

## RSS と記事記録

- RSS URL は `reqwest::Url::parse` で解釈できる必要がある
- RSS 取得は10秒でタイムアウトし、当該フィードだけをスキップする
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
- `webhook_endpoints` テーブルがない DB では、`app_settings.default_webhook_url` を通知先として扱う

## webhook

- batch は webhook URL から Discord、Slack、Microsoft Teams を識別する
- Discord には `username`、`content`、`embeds`、Slack には Block Kit、Microsoft Teams には Adaptive Card 形式を送る
- 記事タイトルは 256 文字、summary は 300 文字に切り詰めてから payload に載せる（Discord の embed 上限と Slack の block text 上限を満たすため）
- embed のチャンクサイズ見積もりには切り詰め後の文字数を使う
- webhook の各送信試行は10秒でタイムアウトする
- webhook の接続エラー、HTTP 429、HTTP 5xx は最大 3 回リトライする
- リトライ間隔は 500ms とする
- リトライ後の HTTP 429/5xx と、それ以外の HTTP 4xx は当該 webhook 単位の失敗として扱う
- 登録済みの全 webhook へ送信し、1 件でも成功すれば当該フィードの記事を送信済みとして記録する
- すべての webhook が失敗したフィードはスキップする
