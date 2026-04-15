# 概要

この API は、ブックマーク、RSS フィード、フォルダ、タグ、アプリ設定を管理する FastAPI サービスである。

この配下の仕様書は、`specs/requirements.md` の要件を実装視点に分解したものとして扱う。
`specs/requirements.md` はプロダクト要件、`specs/api/` は API の入出力と挙動を中心に記述する。

## 主な特徴

- SQLite による永続化
- ブックマーク、RSS リンク、フォルダ、タグの CRUD
- `settings` によるアプリ全体設定の管理
- RSS 実行 API と Discord webhook 通知
- RSS 実行の実処理は Rust の `batch` が担当し、API は実行要求の入口と結果の参照を担う
- ブックマークへのタグ付与・解除
- `/health` による疎通確認
- webhook 疎通確認用の ping API
- 例外ハンドリングと検証エラーの標準化

## 主要ファイル

- [アプリケーション本体](../../api/main.py)
- [DB 初期化](../../api/database.py)
- [ブックマークルータ](../../api/routers/bookmarks.py)
- [RSS ルータ](../../api/routers/rss_feeds.py)
- [設定ルータ](../../api/routers/settings.py)
- [フォルダルータ](../../api/routers/folders.py)
- [タグルータ](../../api/routers/tags.py)
- [タグ付与ルータ](../../api/routers/bookmark_tags.py)
- [ブックマークサービス](../../api/services/bookmark_service.py)
- [RSS サービス](../../api/services/rss_feed_service.py)
- [設定サービス](../../api/services/settings_service.py)
- [フォルダサービス](../../api/services/folder_service.py)
- [タグサービス](../../api/services/tag_service.py)
- [モデル定義](../../api/model/models.py)

## 仕様の範囲

- 含めるもの
  - HTTP ルート
  - リクエスト/レスポンスの形
  - 代表的な成功・失敗パターン
  - DB 制約に起因する挙動

- 含めないもの
  - UI の見た目
  - フロントエンドの状態管理
  - 実装手順や作業順序
