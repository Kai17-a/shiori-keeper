# ルートとフロー

## ルート

| Method | Path                            | Purpose                          |
| ------ | ------------------------------- | -------------------------------- |
| POST   | `/bookmarks`                    | ブックマーク作成                 |
| GET    | `/bookmarks`                    | ブックマーク一覧取得             |
| GET    | `/bookmarks/{id}`               | ブックマーク詳細取得             |
| PATCH  | `/bookmarks/{id}`               | ブックマーク部分更新             |
| PATCH  | `/bookmarks/by-url`             | URL 指定ブックマーク部分更新     |
| DELETE | `/bookmarks/{id}`               | ブックマーク削除                 |
| DELETE | `/bookmarks?url=...`            | URL 指定ブックマーク削除         |
| PATCH  | `/bookmarks/favorite`           | ブックマークのお気に入り状態更新 |
| POST   | `/bookmarks/{id}/tags`          | ブックマークへタグ付与           |
| DELETE | `/bookmarks/{id}/tags/{tag_id}` | ブックマークからタグ解除         |
| GET    | `/metrics/dashboard`            | ダッシュボード用集計取得         |
| POST   | `/folders`                      | フォルダ作成                     |
| GET    | `/folders`                      | フォルダ一覧取得                 |
| PATCH  | `/folders/{id}`                 | フォルダ更新                     |
| DELETE | `/folders/{id}`                 | フォルダ削除                     |
| POST   | `/tags`                         | タグ作成                         |
| GET    | `/tags`                         | タグ一覧取得                     |
| PATCH  | `/tags/{id}`                    | タグ更新                         |
| DELETE | `/tags/{id}`                    | タグ削除                         |
| PUT    | `/settings/webhook`             | Discord webhook 設定             |
| GET    | `/settings/webhook`             | Discord webhook 取得             |
| POST   | `/settings/webhook/ping`        | Discord webhook 疎通確認         |
| GET    | `/settings/rss-execution`       | RSS 定期実行設定取得             |
| PUT    | `/settings/rss-execution`       | RSS 定期実行設定更新             |
| POST   | `/rss-feeds`                    | RSS フィード作成                 |
| GET    | `/rss-feeds`                    | RSS フィード一覧取得             |
| GET    | `/rss-feeds/{id}`               | RSS フィード詳細取得             |
| GET    | `/rss-feeds/{id}/articles`      | RSS フィード記事一覧取得         |
| PATCH  | `/rss-feeds/{id}`               | RSS フィード部分更新             |
| DELETE | `/rss-feeds/{id}`               | RSS フィード削除                 |
| POST   | `/rss-feeds/{id}/execute`       | RSS 実行と webhook 通知          |
| GET    | `/health`                       | ヘルスチェック                   |

## ユーザーフロー

### ブックマーク

- URL とタイトルを入力して作成する
- 一覧で検索・ページング・絞り込みを行う
- 詳細を確認して編集または削除する
- URL 指定で詳細なしに部分更新する
- 必要に応じてタグを追加・削除する
- 必要に応じてお気に入り状態を切り替える

### ダッシュボード

- ブックマーク、フォルダ、タグ、お気に入り、RSS フィードの総数を確認する

### フォルダ

- フォルダを作成する
- 一覧から対象フォルダへ移動する
- フォルダ名と説明を更新し、不要なら削除する

### タグ

- タグを作成する
- 一覧から対象タグへ移動する
- タグ名と説明を更新し、不要なら削除する

### 設定

- Discord webhook URL を保存する
- webhook の疎通確認を行う
- 未設定時の webhook 取得は 404 を返す
- RSS 定期実行の有効/無効を切り替える

### RSS

- RSS フィードを登録する
- 一覧で検索・ページングを行う
- 詳細を確認して編集または削除する
- 保存済みの記事一覧を確認する
- 手動実行して webhook 通知を送る

## 共通レスポンス

- 正常系はリソースモデルを返す
- 一覧はページングレスポンス、または小さなマスタ一覧では配列を返す
- エラーは `{"detail": ...}` 形式で返す
- バリデーションエラーは FastAPI の標準形式を返す

## 受け入れ基準

### ブックマーク

1. `POST /bookmarks` は、有効な URL と title がある場合に 201 を返し、作成済みブックマークを返す。
2. `POST /bookmarks` は、`folder_id` が指定されている場合に存在確認を行う。
3. `POST /bookmarks` は、無効 URL または title 省略時に 422 を返す。
4. `POST /bookmarks` は、存在しない `folder_id` に対して 404 を返す。
5. `GET /bookmarks` は、一覧とページング情報を返す。
6. `GET /bookmarks` は、`folder_id`、`tag_id`、`q`、`sort`、`page`、`per_page` を受け付ける。
7. `GET /bookmarks` の `sort` は複数指定でき、指定順に `ORDER BY` を適用する。
8. `GET /bookmarks` の `sort` に存在しない項目が指定された場合は 422 を返す。
9. `GET /bookmarks/{id}` は、対象ブックマークを返す。
10. `PATCH /bookmarks/{id}` は、部分更新を行い更新後リソースを返す。
11. `PATCH /bookmarks/by-url` は、URL で対象ブックマークを特定して部分更新を行う。
12. `DELETE /bookmarks/{id}` は、204 を返す。
13. `DELETE /bookmarks?url=...` は、指定 URL のブックマークを削除し、204 を返す。
14. `PATCH /bookmarks/favorite` は、お気に入り状態を更新し更新後リソースを返す。

### フォルダ

13. `POST /folders` は、201 と作成済みフォルダを返す。
14. `GET /folders` は、フォルダ一覧を配列で返す。
15. `PATCH /folders/{id}` は、更新後フォルダを返す。
16. `DELETE /folders/{id}` は、204 を返す。
17. フォルダ削除時は、関連ブックマークの `folder_id` を `NULL` にする。
18. フォルダは `name` に加えて `description` を保持する。

### タグ

19. `POST /tags` は、201 と作成済みタグを返す。
20. `GET /tags` は、タグ一覧を配列で返す。
21. `PATCH /tags/{id}` は、更新後タグを返す。
22. `DELETE /tags/{id}` は、204 を返す。
23. タグ削除時は、関連 `bookmark_tags` を削除する。
24. タグは `name` に加えて `description` を保持する。

### タグ付与

25. `POST /bookmarks/{id}/tags` は、タグ紐付けを追加し更新後ブックマークを返す。
26. `DELETE /bookmarks/{id}/tags/{tag_id}` は、204 を返す。
27. 既に紐付け済みのタグを再度付与すると 409 を返す。
28. 存在しない bookmark/tag のいずれかを指定すると 404 を返す。

### ダッシュボードとヘルス

29. `GET /metrics/dashboard` は、ダッシュボードで使う総数を返す。
30. `GET /health` は、`status: ok` を返す。

### 設定

31. `GET /settings/webhook` は、現在設定済みの webhook URL を返す。
32. `PUT /settings/webhook` は、Discord webhook URL を保存する。
33. `POST /settings/webhook/ping` は、Discord webhook の疎通確認を行い `pong: true` を返す。
34. `GET /settings/rss-execution` は、RSS 定期実行の有効/無効状態を返す。
35. `PUT /settings/rss-execution` は、RSS 定期実行の有効/無効状態を更新する。
36. `GET /settings/rss-webhook-notification` は、定期実行時に webhook 通知を送るかどうかの全体設定を返す。
37. `PUT /settings/rss-webhook-notification` は、定期実行時に webhook 通知を送るかどうかの全体設定を更新する。

### RSS

38. `POST /rss-feeds` は、201 と作成済み RSS フィードを返す。
39. `GET /rss-feeds` は、RSS フィード一覧とページング情報を返す。
40. `GET /rss-feeds/{id}` は、対象 RSS フィードを返す。
41. `GET /rss-feeds/{id}/articles` は、保存済み記事一覧とページング情報を返す。
42. `PATCH /rss-feeds/{id}` は、部分更新を行い更新後 RSS フィードを返す。
43. `DELETE /rss-feeds/{id}` は、204 を返す。
44. `POST /rss-feeds/{id}/execute` は、RSS を取得して Discord webhook に通知する。

### `GET /metrics/dashboard`

Response:

```json
{
  "bookmarks_total": 12,
  "folders_total": 3,
  "tags_total": 8,
  "favorites_total": 4,
  "rss_feeds_total": 2
}
```

### `POST /bookmarks`

Request:

```json
{
  "url": "https://example.com",
  "title": "Example",
  "description": "Optional",
  "folder_id": 1,
  "tag_ids": [1, 2]
}
```

Response:

```json
{
  "id": 1,
  "url": "https://example.com/",
  "title": "Example",
  "description": "Optional",
  "folder_id": 1,
  "is_favorite": false,
  "tags": [
    { "id": 1, "name": "tag-a", "description": null },
    { "id": 2, "name": "tag-b", "description": null }
  ],
  "created_at": "2026-04-11T00:00:00",
  "updated_at": "2026-04-11T00:00:00"
}
```

- 成功時の `tags` は空配列または関連タグ配列になる
- `is_favorite` は作成時に指定しなければ `false` になる
- `tag_ids` は重複不可で、重複時は 422 を返す
- 既存 URL は 409 を返す

### `GET /bookmarks`

- `folder_id` でフォルダ絞り込みを行う
- `tag_id` でタグ絞り込みを行う
- `q` でタイトル、URL、説明を検索する
- `page` と `per_page` でページングする

Response:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "per_page": 20,
  "total_pages": 0
}
```

- `total_pages` は総件数と `per_page` から算出する
- 該当件数がない場合は `items` を空配列で返す

### `PATCH /bookmarks/by-url`

- `url` クエリパラメータで対象ブックマークを特定する
- `PATCH /bookmarks/{id}` と同じ更新ルールを使う
- 存在しない URL は 404 を返す

### `DELETE /bookmarks?url=...`

- `url` クエリパラメータで対象ブックマークを特定する
- 存在しない URL は 404 を返す
- 成功時は 204 を返す

### `PATCH /bookmarks/{id}`

- 指定された項目のみ更新する
- `tag_ids` が含まれる場合はタグ集合を置き換える
- 未指定の項目は既存値を保持する
- 存在しない ID は 404 を返す
- URL 変更後に重複があれば 409 を返す

### `PATCH /bookmarks/favorite`

Request:

```json
{
  "bookmark_id": 1,
  "is_favorite": true
}
```

- `bookmark_id` で対象ブックマークを特定する
- `is_favorite` を指定値に更新する
- 存在しない `bookmark_id` は 404 を返す

### `POST /bookmarks/{id}/tags`

Request:

```json
{ "tag_id": 1 }
```

- 既存の紐付けなら 409 を返す
- 成功時は更新後のブックマークを返す
- 存在しない bookmark/tag は 404 を返す

### `DELETE /bookmarks/{id}/tags/{tag_id}`

- 紐付けを削除する
- 成功時は 204 を返す
- 存在しない bookmark/tag は 404 を返す

### `POST /folders`

Request:

```json
{ "name": "Work", "description": "Team notes" }
```

Response:

```json
{
  "id": 1,
  "name": "Work",
  "description": "Team notes",
  "created_at": "2026-04-11T00:00:00"
}
```

### `GET /folders`

- レスポンスは配列で返す
- `name` と `id` の昇順で返す

### `PATCH /folders/{id}`

- 名前を更新する
- `description` も更新できる
- 重複名は 409 を返す
- 存在しない ID は 404 を返す

### `POST /tags`

Request:

```json
{ "name": "python", "description": "Programming language" }
```

Response:

```json
{ "id": 1, "name": "python", "description": "Programming language" }
```

### `GET /tags`

- レスポンスは配列で返す
- `name` と `id` の昇順で返す

### `PATCH /tags/{id}`

- 名前を更新する
- `description` も更新できる
- 重複名は 409 を返す
- 存在しない ID は 404 を返す

### `GET /settings/webhook`

```json
{ "webhook_url": "https://discord.com/api/webhooks/1/token" }
```

### `PUT /settings/webhook`

Request:

```json
{ "webhook_url": "https://discord.com/api/webhooks/1/token" }
```

Response:

```json
{ "webhook_url": "https://discord.com/api/webhooks/1/token" }
```

### `POST /settings/webhook/ping`

Request:

```json
{ "webhook_url": "https://discord.com/api/webhooks/1/token" }
```

Response:

```json
{ "pong": true }
```

### `GET /settings/rss-execution`

```json
{ "enabled": false }
```

### `PUT /settings/rss-execution`

Request:

```json
{ "enabled": true }
```

Response:

```json
{ "enabled": true }
```

### `GET /rss-feeds/{id}`

- 指定 ID の RSS フィードを返す

### `GET /rss-feeds/{id}/articles`

- 保存済み記事の一覧を返す
- `page` と `per_page` を受け付ける

Response:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "per_page": 20,
  "total_pages": 0
}
```

### `POST /rss-feeds/{id}/execute`

- フィード URL を取得して RSS として解析する
- 登録済み webhook URL がない場合は 400 を返す
- 新規記事のみ webhook に送信する
- `notify_webhook_enabled` は batch の定期実行でのみ参照する
- 新規記事がない場合も成功として扱い、メッセージを返す
- 送信済み記事は `rss_feed_articles` に保存済みとして追記する

### `GET /health`

Response:

```json
{ "status": "ok" }
```
