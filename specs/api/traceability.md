# 要件対応表

`specs/requirements.md` の要件番号と、この API 仕様書の対応を示す。

## 対応表

| requirements                          | api                                                                      |
| ------------------------------------- | ------------------------------------------------------------------------ |
| 要件1: ブックマーク管理               | `routes-and-flows.md` のブックマーク節、`data-and-constraints.md` の制約 |
| 要件2: フォルダ管理                   | `routes-and-flows.md` のフォルダ節、`data-and-constraints.md` の制約     |
| 要件3: タグ管理                       | `routes-and-flows.md` のタグ節、`data-and-constraints.md` の制約         |
| 要件4: ブックマークへのタグ付与・解除 | `routes-and-flows.md` のタグ付与節                                       |
| 要件5: 設定取得                       | `routes-and-flows.md` の設定節                                           |
| 要件6: 永続化とエラー処理             | `data-and-constraints.md` のデータモデル・制約                           |

## 補足

- `specs/requirements.md` は何を作るかを定義する。
- `specs/api/` はどう返すか、どう失敗するかを定義する。
- 実装変更時は要件変更より先に API 仕様の差分を確認する。
