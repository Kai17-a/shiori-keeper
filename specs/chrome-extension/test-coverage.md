# テスト観点

- API URL の保存と復元ができること
- 現在タブのタイトルと URL が入力欄に反映されること
- `/health` の結果に応じて接続状態が更新されること
- API 接続成功時に初回自動保存を 1 回だけ試みること
- フォルダ一覧とタグ一覧が読み込まれること
- 新規保存、既存ブックマークの更新、URL ベースの削除が実行できること
- 既存ブックマークが見つかった場合にフォームへ反映されること
- 重複 URL の場合はエラー終了せず既存ブックマーク読込へフォールバックすること
- URL 入力変更時に既存ブックマークの再同期が行われること
- Close ボタンと削除成功時にポップアップが閉じること

## 実装候補

- popup 初期化テスト
  - `chrome.storage.local.get`
  - `chrome.tabs.query`
  - `/health` 成功時の自動保存試行
  - 重複時の `/bookmarks?q=...` fallback

- popup 保存フローテスト
  - 既存 ID ありで `PATCH /bookmarks/{id}`
  - 既存 ID なしで `POST /bookmarks`
  - folder/tag 選択値が payload に含まれる

- popup 削除/補助操作テスト
  - `DELETE /bookmarks?url=...`
  - URL change 時の resync
  - Close button による close
