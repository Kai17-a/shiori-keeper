# API

このディレクトリは FastAPI バックエンド本体とテストを含む。

## 起動

```bash
api-dev
```

`api-dev` は `uvicorn` を使って起動する。

## テスト

```bash
python -m pytest -q
uv run ruff check .
```

## 主要ファイル

- [アプリケーション本体](./main.py)
- [DB 初期化](./database.py)
- [モデル定義](./model/models.py)
- [ルータ群](./routers/)
- [サービス層](./services/)
- [リポジトリ層](./repositories/)
- [テスト](./tests/)

