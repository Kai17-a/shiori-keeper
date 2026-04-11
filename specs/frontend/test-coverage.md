# テスト観点

## 単体テスト

- `frontend/tests/bookmarkApi.test.ts`
  - Trailing slash trimming
  - API base fallback resolution
  - Request header construction
  - Error message normalization

- `frontend/tests/sidebarCatalog.test.ts`
  - Empty sidebar state creation
  - Catalog result application

## E2E テスト

- `frontend/tests/e2e/bookmark-manager.spec.ts`
  - Bookmark create, edit, search, delete
  - Folder create, rename, detail, delete
  - Tag create, rename, detail, delete

## 未カバー範囲

- ページ/コンポーネント単体のテストはない
- 設定画面の挙動を直接検証するテストはない
- ブックマークのフォルダ/タグ割り当てを UI で追う明示的なテストはない
- オフラインやバックエンド停止時の描画を、手動のエラー処理以外で明示的に検証するテストはない
