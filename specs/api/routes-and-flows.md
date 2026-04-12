# ルートとフロー

## ルート

| Method | Path                            | Purpose                          |
| ------ | ------------------------------- | -------------------------------- |
| POST   | `/bookmarks`                    | ブックマーク作成                 |
| GET    | `/bookmarks`                    | ブックマーク一覧取得             |
| GET    | `/bookmarks/{id}`               | ブックマーク詳細取得             |
| PATCH  | `/bookmarks/{id}`               | ブックマーク部分更新             |
| DELETE | `/bookmarks/{id}`               | ブックマーク削除                 |
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
| GET    | `/health`                       | ヘルスチェック                   |

## ユーザーフロー

### ブックマーク

- URL とタイトルを入力して作成する
- 一覧で検索・ページング・絞り込みを行う
- 詳細を確認して編集または削除する
- 必要に応じてタグを追加・削除する
- 必要に応じてお気に入り状態を切り替える

### ダッシュボード

- ブックマーク、フォルダ、タグ、お気に入りの総数を確認する

### フォルダ

- フォルダを作成する
- 一覧から対象フォルダへ移動する
- 詳細で配下ブックマークを確認する
- フォルダ名を更新し、不要なら削除する

### タグ

- タグを作成する
- 一覧から対象タグへ移動する
- 詳細で関連ブックマークを確認する
- タグ名を更新し、不要なら削除する

## 共通レスポンス

- 正常系はリソースモデルを返す
- 一覧はページングレスポンスを返す
- エラーは `{"detail": ...}` 形式で返す
- バリデーションエラーは FastAPI の標準形式を返す

## 受け入れ基準

### ブックマーク

1. `POST /bookmarks` は、有効な URL と title がある場合に 201 を返し、作成済みブックマークを返す。
2. `POST /bookmarks` は、`folder_id` が指定されている場合に存在確認を行う。
3. `POST /bookmarks` は、無効 URL または title 省略時に 422 を返す。
4. `POST /bookmarks` は、存在しない `folder_id` に対して 404 を返す。
5. `GET /bookmarks` は、一覧とページング情報を返す。
6. `GET /bookmarks` は、`folder_id`、`tag_id`、`q`、`page`、`per_page` を受け付ける。
7. `GET /bookmarks/{id}` は、対象ブックマークを返す。
8. `PATCH /bookmarks/{id}` は、部分更新を行い更新後リソースを返す。
9. `DELETE /bookmarks/{id}` は、204 を返す。

### フォルダ

10. `POST /folders` は、201 と作成済みフォルダを返す。
11. `GET /folders` は、フォルダ一覧を返す。
12. `PATCH /folders/{id}` は、更新後フォルダを返す。
13. `DELETE /folders/{id}` は、204 を返す。
14. フォルダ削除時は、関連ブックマークの `folder_id` を `NULL` にする。

### タグ

15. `POST /tags` は、201 と作成済みタグを返す。
16. `GET /tags` は、タグ一覧を返す。
17. `PATCH /tags/{id}` は、更新後タグを返す。
18. `DELETE /tags/{id}` は、204 を返す。
19. タグ削除時は、関連 `bookmark_tags` を削除する。

### タグ付与

20. `POST /bookmarks/{id}/tags` は、タグ紐付けを追加し更新後ブックマークを返す。
21. `DELETE /bookmarks/{id}/tags/{tag_id}` は、204 を返す。
22. `GET /metrics/dashboard` は、ダッシュボードで使う総数を返す。
23. `GET /health` は、`status: ok` を返す。

### `GET /metrics/dashboard`

Response:

```json
{
  "bookmarks_total": 12,
  "folders_total": 3,
  "tags_total": 8,
  "favorites_total": 4
}
```

## エンドポイント詳細

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
    { "id": 1, "name": "tag-a" },
    { "id": 2, "name": "tag-b" }
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
  "created_at": "2026-04-11T00:00:00"
}
```

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
{ "id": 1, "name": "python" }
```

### `PATCH /tags/{id}`

- 名前を更新する
- `description` も更新できる
- 重複名は 409 を返す
- 存在しない ID は 404 を返す

### `GET /health`

Response:

```json
{ "status": "ok" }
```
