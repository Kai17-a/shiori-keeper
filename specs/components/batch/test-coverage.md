# テスト観点

## 既存テスト

- `scripts/test-scheduler-config.sh`
  - cron 式未指定時の毎時実行
  - 時間帯を限定した cron 式
  - 空値と複数行設定の拒否

- `batch/tests/run_batch.rs`
  - RSS 定期実行が無効な場合に成功扱いで終了する
  - RSS webhook 通知が無効な場合に成功扱いで終了する
  - RSS 定期実行と webhook 通知の有効設定を、それぞれ対応する設定行から取得する
  - 複数登録された webhook URL を登録順に全件取得する
  - `webhook_endpoints` テーブルがない DB では `app_settings.default_webhook_url` へフォールバックする
  - フィードごとの通知先 webhook 選択を取得する
  - 通知先未選択のフィードは空の選択として扱う

- `batch/tests/webhook.rs`
  - 全体設定が無効な場合に webhook payload から記事サマリーを除外する
  - webhook payload の基本形
  - `record_sent_articles` による送信済み記事の記録
  - `load_sent_article_urls` による送信済み URL の読み込み
  - webhook 送信失敗時の 3 回リトライ
  - webhook の HTTP 429/5xx 応答時の 3 回リトライと途中回復

- `batch/tests/news.rs`
  - 保存済み CSS selector による title、相対/絶対 link、published、summary の抽出
  - custom news site の送信済み URL 記録と重複防止
  - 不正 CSS selector の拒否

- `batch/tests/run_batch.rs`
  - webhook サマリー包含設定は未設定時に有効で、`0` の場合は無効になる
  - custom news site の `scrape_config` と選択済み webhook ID の読込

## 追加で確認したい観点

- `DATABASE_URL` 未指定時に `data/data.db` を選ぶこと
- webhook URL 未登録時に成功扱いで終了すること
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
