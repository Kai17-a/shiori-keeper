# テスト観点

## 単体テスト

- `frontend/tests/bookmarkApi.test.ts`
  - Trailing slash trimming
  - API base fallback resolution
  - Request header construction
  - Error message normalization
  - Frontend API path coverage including bookmarks, folders, tags, RSS feeds, metrics, and settings

- `frontend/tests/sidebarCatalog.test.ts`
  - Empty sidebar state creation
  - Catalog result application
  - RSS フィードを含むサイドバーカタログ反映

## E2E テスト

- `frontend/tests/e2e/bookmark-manager.spec.ts`
  - Bookmark create, edit, search, delete
  - Bookmark の folder/tag 割り当てと絞り込み
  - Favorites page load and favorite toggle
  - Folder create, rename, detail, delete
  - Folder detail 上での関連 bookmark 編集、削除、お気に入り切り替え
  - Tag create, rename, detail, delete
  - Tag detail 上での関連 bookmark 編集、削除、お気に入り切り替え
  - RSS feed create, edit, detail navigation, delete
  - RSS webhook load, ping, save
  - RSS periodic execution toggle
  - RSS detail articles paging
  - Settings page theme toggle

## 未カバー範囲

- ページ/コンポーネント単体のテストはない
- API 初回疎通失敗時のダッシュボードシェル継続描画は明示的に検証していない
- RSS 実行後のサイドバー再同期は明示的に検証していない
- オフラインやバックエンド停止時の描画を、手動のエラー処理以外で明示的に検証するテストはない

## 実装候補

- `frontend/tests/bookmarkApi.test.ts`
  - `/settings/webhook`, `/settings/webhook/ping`, `/settings/rss-execution`, `/metrics/dashboard`, `/bookmarks/by-url`, `/bookmarks/favorite`, `/rss-feeds/{id}/articles` の request path と body を明示確認する

- `frontend/tests/sidebarCatalog.test.ts`
  - folders/tags に加えて RSS feeds を含む結果が状態へ反映されることを確認する
  - refresh 後に既存 state が最新 catalog へ置き換わることを確認する

- `frontend/tests/apiHealth.test.ts`
  - API 到達成功と失敗で health state が切り替わることを確認する
  - 初回失敗時でも UI 側で致命的エラーにしない前提の state を確認する

- `frontend/tests/e2e/bookmark-manager.spec.ts`
  - `/favorites` で favorite のみが表示され、解除で一覧から消えることを確認する
  - bookmark 作成時の folder/tag 割り当てが detail/filter と整合することを確認する
  - `/folders/[id]` と `/tags/[id]` で関連 bookmark の編集、削除、お気に入り切り替えを確認する
  - `/rss` で webhook の load, ping, save と RSS periodic execution toggle を確認する
  - `/rss/[id]` で article list と paging を確認する
  - `/settings` で theme change が reload 後も維持されることを確認する

## 追加ルール

- フロントエンドに共通 `fetcher` や API 基盤のような横断的な実装を追加した場合は、対応する unit テストか e2e テストも同時に追加する
