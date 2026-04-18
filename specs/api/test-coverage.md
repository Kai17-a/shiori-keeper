# テスト観点

## 単体テスト

- `api/tests/test_database.py`
  - 全テーブルの自動作成
  - 初期化の冪等性
  - DB 障害時の 500 応答

- `api/tests/test_bookmarks.py`
  - 作成、一覧、詳細、更新、削除
  - 検索、絞り込み、ページング
  - フォルダ関連付け
  - URL 指定削除
  - URL 指定更新とお気に入り切り替え
  - タグ付与・解除
  - バリデーションと重複エラー
  - タグ集合の置き換え

- `api/tests/test_folders.py`
  - 作成、一覧、更新、削除
  - 参照先更新と 404 応答
  - フォルダ上限

- `api/tests/test_tags.py`
  - 作成、一覧、更新、削除
  - 重複エラーと 404 応答
  - タグ上限

- `api/tests/test_rss_feeds.py`
  - 作成、一覧、詳細、更新、削除
  - 記事一覧、実行、webhook 設定
  - RSS/Atom 以外の URL 拒否
  - webhook 疎通確認
  - RSS 定期実行設定
  - 新規記事なしメッセージ
  - 既送信記事のスキップ
  - article paging

- `api/tests/test_metrics.py`
  - ダッシュボード集計

- `api/tests/test_settings.py`
  - webhook 未設定時の 404
  - webhook 保存と再取得
  - Discord webhook URL 形式検証
  - ping の 422 と 502
  - RSS 定期実行設定の取得と更新

## ルート単位の確認観点

- `POST /bookmarks`
  - 正常作成
  - `folder_id` の存在確認
  - `tag_ids` の重複拒否
  - 既存 URL の 409

- `GET /bookmarks`
  - デフォルトページング
  - `page` と `per_page`
  - `folder_id`、`tag_id`、`q` の絞り込み

- `PATCH /bookmarks/{id}`
  - 部分更新
  - URL 指定更新
  - お気に入り切り替え
  - タグ集合の置き換え
  - 404 と 409

- `PATCH /bookmarks/by-url`
  - 対象 URL の部分更新
  - 存在しない URL の 404
  - URL 重複時の 409

- `DELETE /bookmarks?url=...`
  - URL 指定削除
  - 存在しない URL の 404

- `POST /folders` / `POST /tags`
  - 正常作成
  - 空文字拒否
  - 上限超過
  - `description` の保存

- `PATCH /folders/{id}` / `PATCH /tags/{id}`
  - 名前更新
  - 重複名 409
  - 存在しない ID の 404

- `POST /bookmarks/{id}/tags`
  - 紐付け追加
  - 重複紐付け 409
  - 存在しない bookmark/tag の 404

- `DELETE /bookmarks/{id}/tags/{tag_id}`
  - 紐付け解除
  - 存在しない bookmark/tag の 404

- `GET /settings/webhook` / `PUT /settings/webhook`
  - 取得と更新
  - Discord webhook URL の形式検証

- `POST /settings/webhook/ping`
  - 疎通確認
  - 422 と 502

- `GET /settings/rss-execution` / `PUT /settings/rss-execution`
  - 現在値取得
  - 有効/無効更新

- `GET /metrics/dashboard`
  - 総数取得

- `GET /rss-feeds/{id}/articles`
  - 記事一覧取得
  - `page` と `per_page`
  - 存在しない feed の 404

- `POST /rss-feeds/{id}/execute`
  - webhook 未設定時の 400
  - 新規記事通知
  - 既送信記事スキップ
  - 新規記事なしメッセージ
  - webhook 失敗時の 502

## プロパティテスト

- `api/tests/test_properties.py`
  - 作成のラウンドトリップ
  - 無効 URL の拒否
  - 存在しないリソースの 404
  - フォルダ/タグフィルタの正確性
  - キーワード検索の正確性
  - 部分更新の不変性
  - 削除とカスケード
  - タグ付与・解除のラウンドトリップ
  - URL 指定更新とお気に入り切り替え

## 未カバー範囲

- OpenAPI ドキュメントのスナップショット
- 同時実行時の競合テスト
- 低レベルの SQLite パフォーマンス検証

## 実装候補

- `api/tests/test_database.py`
  - `rss_feed_articles` を含む全テーブル初期化を確認する

- `api/tests/test_bookmarks.py`
  - `PATCH /bookmarks/by-url` の 404/409 を追加する
  - `DELETE /bookmarks?url=...` の 404 を追加する
  - folder/tag `description` を伴う bookmark 関連付けの整合を確認する

- `api/tests/test_folders.py`
  - `description` の create/update round-trip を追加する

- `api/tests/test_tags.py`
  - `description` の create/update round-trip を追加する

- `api/tests/test_settings.py`
  - 未設定 webhook の 404
  - Discord webhook URL host/path 検証
  - ping の upstream failure を 502 へ写像するケース
  - RSS periodic execution の true/false 両遷移

- `api/tests/test_rss_feeds.py`
  - `/rss-feeds/{id}/articles` の paging と 404
  - `/rss-feeds/{id}/execute` の 400, 502, no-new-articles message
  - 送信済み article の二重記録防止

- `api/tests/test_metrics.py`
  - `favorites_total` と `rss_feeds_total` の状態遷移反映を追加する

- `api/tests/test_properties.py`
  - URL 指定削除
  - folder/tag `description` を含む部分更新の不変性
