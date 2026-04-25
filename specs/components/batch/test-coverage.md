# テスト観点

## 既存テスト

- `batch/tests/run_batch.rs`
  - RSS 定期実行が無効な場合に成功扱いで終了する
  - RSS webhook 通知が無効な場合に成功扱いで終了する

- `batch/tests/webhook.rs`
  - webhook payload の基本形
  - `record_sent_articles` による送信済み記事の記録
  - `load_sent_article_urls` による送信済み URL の読み込み
  - webhook 送信失敗時の 3 回リトライ

## 追加で確認したい観点

- `DATABASE_URL` 未指定時に `data/data.db` を選ぶこと
- `default_webhook_url` 未設定時に成功扱いで終了すること
- `rss_feeds.notify_webhook_enabled = 0` のフィードをスキップすること
- 既送信 URL を含む RSS item を通知対象から除外すること
- 新着記事がないフィードをスキップすること
- RSS URL parse 失敗時に当該フィードだけをスキップすること
- RSS 取得失敗時に当該フィードだけをスキップすること
- RSS parse 失敗時に当該フィードだけをスキップすること
- webhook 4xx/5xx 応答時に当該フィードだけをスキップすること
- webhook 送信成功後にだけ `rss_feed_articles` へ記事を記録すること
- `rss_feed_articles.published` 列がない DB でも送信済み記事を記録できること
- `rss_feeds.notify_webhook_enabled` 列がない DB でもフィード一覧を取得できること
