# 概要

`batch/` は、SQLite に保存された RSS フィードを定期巡回し、新着記事を webhook へ通知する Rust 製バッチである。
API サーバーとは別プロセスとして動作し、HTTP ルートは持たない。

## 主な特徴

- `DATABASE_URL` で指定された SQLite DB を開く
- `DATABASE_URL` 未指定時は `data/data.db` を使う
- `app_settings` から RSS 定期実行と webhook 通知の全体設定を読む
- `rss_feeds.notify_webhook_enabled = 1` の RSS フィードのみを巡回対象にする
- RSS URL を取得し、RSS channel として解析する
- `rss_feed_articles` に保存済みの URL を読み、既送信記事を除外する
- 新着記事を Discord 互換の webhook payload として送信する
- webhook 送信成功後に `rss_feed_articles` へ送信済み記事を記録する
- フィード単位の失敗はログ出力してスキップし、他フィードの処理を継続する

## 主要ファイル

- [エントリポイント](../../../batch/src/main.rs)
- [ライブラリ公開](../../../batch/src/lib.rs)
- [DB アクセス](../../../batch/src/db.rs)
- [実行フロー](../../../batch/src/runner.rs)
- [webhook 送信と記事記録](../../../batch/src/webhook.rs)
- [Cargo 設定](../../../batch/Cargo.toml)

## 技術スタック

- Rust 2024 edition
- `tokio` による async 実行
- `rusqlite` による SQLite アクセス
- `reqwest` による RSS と webhook の HTTP 通信
- `rss` crate による RSS channel 解析
- `serde_json` による webhook payload 構築
