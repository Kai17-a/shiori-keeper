# 要件定義書

## はじめに

本ドキュメントは、ブックマーク管理 Web アプリケーション向け REST API の要件を定義する。
API は Python で実装し、データストアには SQLite を使用する。
データモデルは `bookmarks`、`rss_feeds`、`rss_feed_articles`、`folders`、`tags`、`bookmark_tags`、`app_settings` の各テーブルで構成する。

## 用語集

- **API**: ブックマーク管理アプリケーションの REST API サーバー
- **Bookmark**: URL とそのメタデータ（タイトル、説明、お気に入り状態など）を保持するリソース
- **RSS Feed**: RSS または Atom フィードの URL とメタデータを保持するリソース
- **Folder**: ブックマークを整理するためのコンテナリソース
- **Tag**: ブックマークに付与できるラベルリソース（多対多の関係）
- **Webhook**: 外部サービスに通知を送るための URL
- **Client**: API を呼び出すブラウザまたはフロントエンドアプリケーション
- **DB**: SQLite データベース

---

## 要件

### 要件1: ブックマーク管理

**ユーザーストーリー:** 開発者として、ブックマークを登録・閲覧・更新・削除したい。

#### 受け入れ基準

1. WHEN Clientが有効なURL・タイトルを含むPOSTリクエストを `/bookmarks` に送信したとき、THE API SHALL 新しいブックマークをDBに保存し、HTTPステータス201と作成されたブックマークオブジェクト（id, url, title, description, folder_id, is_favorite, tags, created_at, updated_at）を返す。
2. WHEN Clientが `folder_id` を指定してブックマークを作成したとき、THE API SHALL 指定されたフォルダが存在することを確認してから保存する。
3. IF Clientが無効なURL形式を送信したとき、THEN THE API SHALL HTTPステータス422を返す。
4. IF Clientが `title` を省略したとき、THEN THE API SHALL HTTPステータス422を返す。
5. IF Clientが存在しない `folder_id` を指定したとき、THEN THE API SHALL HTTPステータス404を返す。
6. WHEN Clientが `GET /bookmarks` にリクエストを送信したとき、THE API SHALL ブックマーク一覧を返し、`folder_id`、`tag_id`、`q`、`sort`、`page`、`per_page` による絞り込み、ソート、ページングをサポートする。
7. WHEN Clientが `GET /bookmarks` に存在しない `sort` 項目を含めてリクエストを送信したとき、THE API SHALL HTTPステータス422を返す。
8. WHEN Clientが `GET /bookmarks/{id}` にリクエストを送信したとき、THE API SHALL 指定IDのブックマークを返す。
9. WHEN Clientが `PATCH /bookmarks/{id}` にリクエストを送信したとき、THE API SHALL 指定ブックマークを部分更新し、更新後のブックマークを返す。
10. WHEN Clientが `PATCH /bookmarks/by-url?url=...` にリクエストを送信したとき、THE API SHALL 指定URLのブックマークを部分更新し、更新後のブックマークを返す。
11. WHEN Clientが `DELETE /bookmarks/{id}` にリクエストを送信したとき、THE API SHALL 指定ブックマークを削除し、HTTPステータス204を返す。
12. WHEN Clientが `DELETE /bookmarks?url=...` にリクエストを送信したとき、THE API SHALL 指定URLのブックマークを削除し、HTTPステータス204を返す。
13. WHEN Clientが `PATCH /bookmarks/favorite` にリクエストを送信したとき、THE API SHALL 指定ブックマークのお気に入り状態を更新し、更新後のブックマークを返す。

### 要件2: フォルダ管理

**ユーザーストーリー:** 開発者として、ブックマークをフォルダで整理したい。

#### 受け入れ基準

1. WHEN Clientが有効な名前を含むPOSTリクエストを `/folders` に送信したとき、THE API SHALL 新しいフォルダをDBに保存し、HTTPステータス201と作成されたフォルダオブジェクト（id, name, description, created_at）を返す。
2. WHEN ClientがGETリクエストを `/folders` に送信したとき、THE API SHALL フォルダ一覧を返す。
3. WHEN ClientがPATCHリクエストを `/folders/{id}` に送信したとき、THE API SHALL 指定フォルダを更新し、更新後のフォルダを返す。
4. WHEN ClientがDELETEリクエストを `/folders/{id}` に送信したとき、THE API SHALL 指定フォルダを削除し、HTTPステータス204を返す。
5. IF Clientが存在しないIDを指定したとき、THEN THE API SHALL HTTPステータス404を返す。
6. WHEN フォルダが削除されたとき、THE API SHALL そのフォルダに属していたブックマークの `folder_id` を `null` に更新する。
7. WHEN Clientがフォルダを作成または更新するとき、THE API SHALL `description` を任意で保持できる。

### 要件3: タグ管理

**ユーザーストーリー:** 開発者として、ブックマークをタグで分類したい。

#### 受け入れ基準

1. WHEN Clientが有効な名前を含むPOSTリクエストを `/tags` に送信したとき、THE API SHALL 新しいタグをDBに保存し、HTTPステータス201と作成されたタグオブジェクト（id, name, description）を返す。
2. WHEN ClientがGETリクエストを `/tags` に送信したとき、THE API SHALL タグ一覧を返す。
3. WHEN ClientがPATCHリクエストを `/tags/{id}` に送信したとき、THE API SHALL 指定タグを更新し、更新後のタグを返す。
4. WHEN ClientがDELETEリクエストを `/tags/{id}` に送信したとき、THE API SHALL 指定タグを削除し、HTTPステータス204を返す。
5. IF Clientが重複するタグ名を作成または更新しようとしたとき、THEN THE API SHALL HTTPステータス409を返す。
6. IF Clientが存在しないIDを指定したとき、THEN THE API SHALL HTTPステータス404を返す。
7. WHEN タグが削除されたとき、THE API SHALL そのタグに関連する `bookmark_tags` レコードも同時に削除する。
8. WHEN Clientがタグを作成または更新するとき、THE API SHALL `description` を任意で保持できる。

### 要件4: ブックマークへのタグ付与・解除

**ユーザーストーリー:** 開発者として、ブックマークにタグを付与または解除したい。

#### 受け入れ基準

1. WHEN Clientが有効な `tag_id` を含むPOSTリクエストを `/bookmarks/{id}/tags` に送信したとき、THE API SHALL 指定されたブックマークとタグの紐付けを保存し、HTTPステータス200と更新後のブックマークオブジェクトを返す。
2. WHEN Clientが `DELETE /bookmarks/{id}/tags/{tag_id}` にリクエストを送信したとき、THE API SHALL 指定されたブックマークとタグの紐付けを削除し、HTTPステータス204を返す。
3. IF Clientが既に紐付け済みのタグを再度付与しようとしたとき、THEN THE API SHALL HTTPステータス409を返す。
4. IF Clientが存在しないブックマークIDまたはタグIDを指定したとき、THEN THE API SHALL HTTPステータス404を返す。

### 要件5: 永続化とエラー処理

**ユーザーストーリー:** 開発者として、データを永続化し、DB障害時に安全に失敗したい。

#### 受け入れ基準

1. THE API SHALL 全データを SQLite データベースファイルに永続化する。
2. THE API SHALL 起動時に `bookmarks`・`rss_feeds`・`rss_feed_articles`・`folders`・`tags`・`bookmark_tags`・`app_settings` テーブルが存在しない場合、自動作成する。
3. WHILE APIが動作中のとき、THE API SHALL 全ての書き込み操作をトランザクション内で実行し、エラー発生時にはロールバックする。
4. IF データベースへの接続または書き込みに失敗したとき、THEN THE API SHALL HTTPステータス500を返す。

### 要件6: RSS フィード管理

**ユーザーストーリー:** 開発者として、RSS フィード URL を登録・更新・削除したい。

#### 受け入れ基準

1. WHEN Clientが有効なフィード URL・タイトルを含む POST リクエストを `/rss-feeds` に送信したとき、THE API SHALL 新しい RSS フィードを DB に保存し、HTTP ステータス 201 と作成された RSS フィードオブジェクトを返す。
2. WHEN Clientが `GET /rss-feeds` にリクエストを送信したとき、THE API SHALL RSS フィード一覧を返し、`q`、`page`、`per_page` による検索とページングをサポートする。
3. WHEN Clientが `GET /rss-feeds/{id}` にリクエストを送信したとき、THE API SHALL 指定 ID の RSS フィードを返す。
4. WHEN Clientが `GET /rss-feeds/{id}/articles` にリクエストを送信したとき、THE API SHALL 保存済み記事一覧を返し、`page` と `per_page` によるページングをサポートする。
5. WHEN Clientが `PATCH /rss-feeds/{id}` にリクエストを送信したとき、THE API SHALL 指定 RSS フィードを部分更新し、更新後の RSS フィードを返す。
6. WHEN Clientが `DELETE /rss-feeds/{id}` にリクエストを送信したとき、THE API SHALL 指定 RSS フィードを削除し、HTTP ステータス 204 を返す。
7. IF Clientが無効な URL 形式を送信したとき、THEN THE API SHALL HTTP ステータス 422 を返す。
8. IF Clientが RSS または Atom フィードではない URL を送信したとき、THEN THE API SHALL HTTP ステータス 422 を返す。
9. IF Clientが重複する RSS フィード URL を作成または更新しようとしたとき、THEN THE API SHALL HTTP ステータス 409 を返す。

### 要件7: Webhook 設定、RSS 定期実行、集計

**ユーザーストーリー:** 開発者として、アプリ全体の webhook URL を設定し、RSS 実行結果を外部サービスに通知したい。

#### 受け入れ基準

1. WHEN Clientが有効な Discord webhook URL を含む `PUT /settings/webhook` を送信したとき、THE API SHALL その URL をアプリ全体設定として保存し、保存結果を返す。
2. WHEN Clientが `GET /settings/webhook` にリクエストを送信したとき、THE API SHALL 現在設定されている webhook URL を返す。
3. IF webhook URL がまだ設定されていない状態で `GET /settings/webhook` が呼ばれたとき、THEN THE API SHALL HTTP ステータス 404 を返す。
4. IF Clientが Discord webhook URL ではない URL を `PUT /settings/webhook` に送信したとき、THEN THE API SHALL HTTP ステータス 422 を返す。
5. WHEN Clientが `POST /settings/webhook/ping` にリクエストを送信したとき、THE API SHALL webhook の疎通確認を行い、`pong: true` を返す。
6. WHEN Clientが `GET /settings/rss-execution` または `PUT /settings/rss-execution` にリクエストを送信したとき、THE API SHALL RSS 定期実行の有効/無効状態を取得・更新する。
7. WHEN Clientが `GET /metrics/dashboard` にリクエストを送信したとき、THE API SHALL ダッシュボード用の集計値を返す。
8. WHEN Clientが `POST /rss-feeds/{id}/execute` にリクエストを送信したとき、THE API SHALL 指定 RSS フィードを検証し、登録済み webhook URL に通知を送信し、実行結果を返す。
9. IF webhook URL が未設定の状態で `POST /rss-feeds/{id}/execute` が呼ばれたとき、THEN THE API SHALL HTTP ステータス 400 を返す。
10. IF webhook 通知に失敗したとき、THEN THE API SHALL HTTP ステータス 502 を返す。
11. THE API SHALL アルファ版では Discord webhook のみを正式対応とする。
