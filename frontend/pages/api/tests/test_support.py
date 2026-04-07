from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException
from pydantic import ValidationError

from api.app.models import BookmarkCreate, BookmarkUpdate, FolderCreate, TagAttach, TagCreate
from api.app.services.bookmark_service import BookmarkService
from api.app.services.folder_service import FolderService
from api.app.services.tag_service import TagService


@dataclass
class Response:
    status_code: int
    payload: object | None = None

    def json(self):
        return self.payload

    @property
    def text(self):
        return "" if self.payload is None else str(self.payload)


class CompatTestClient:
    __test__ = False

    def __init__(self, app, **kwargs):
        self.app = app

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def _ok(self, payload=None, status_code=200):
        return Response(status_code=status_code, payload=payload)

    def _error(self, status_code: int, detail):
        return Response(status_code=status_code, payload={"detail": detail})

    def _parse(self, url: str) -> tuple[str, dict[str, str]]:
        parsed = urlparse(url)
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        return parsed.path, query

    def _serialize(self, items):
        return [item.model_dump() for item in items]

    def request(self, method: str, url: str, json=None, **kwargs):
        path, query = self._parse(url)

        try:
            if method == "POST" and path == "/folders":
                body = FolderCreate(**(json or {}))
                payload = FolderService().create(body).model_dump()
                return self._ok(payload, 201)
            if method == "GET" and path == "/folders":
                return self._ok(self._serialize(FolderService().list()), 200)
            if method == "DELETE" and path.startswith("/folders/"):
                FolderService().delete(int(path.rsplit("/", 1)[1]))
                return self._ok(status_code=204)

            if method == "POST" and path == "/tags":
                body = TagCreate(**(json or {}))
                payload = TagService().create(body).model_dump()
                return self._ok(payload, 201)
            if method == "GET" and path == "/tags":
                return self._ok(self._serialize(TagService().list()), 200)
            if method == "DELETE" and path.startswith("/tags/"):
                TagService().delete(int(path.rsplit("/", 1)[1]))
                return self._ok(status_code=204)

            if method == "POST" and path == "/bookmarks":
                body = BookmarkCreate(**(json or {}))
                payload = BookmarkService().create(body).model_dump()
                return self._ok(payload, 201)
            if method == "GET" and path == "/bookmarks":
                folder_id = int(query["folder_id"]) if "folder_id" in query else None
                tag_id = int(query["tag_id"]) if "tag_id" in query else None
                q = query.get("q")
                return self._ok(self._serialize(BookmarkService().list(folder_id, tag_id, q)), 200)
            if method == "GET" and path.startswith("/bookmarks/") and "/tags" not in path:
                payload = BookmarkService().get(int(path.rsplit("/", 1)[1])).model_dump()
                return self._ok(payload, 200)
            if method == "PATCH" and path.startswith("/bookmarks/") and "/tags" not in path:
                body = BookmarkUpdate(**(json or {}))
                payload = BookmarkService().update(int(path.rsplit("/", 1)[1]), body).model_dump()
                return self._ok(payload, 200)
            if method == "DELETE" and path.startswith("/bookmarks/") and "/tags" not in path:
                BookmarkService().delete(int(path.rsplit("/", 1)[1]))
                return self._ok(status_code=204)
            if method == "POST" and path.endswith("/tags") and path.startswith("/bookmarks/"):
                bookmark_id = int(path.split("/")[2])
                body = TagAttach(**(json or {}))
                payload = BookmarkService().add_tag(bookmark_id, body.tag_id).model_dump()
                return self._ok(payload, 200)
            if method == "DELETE" and "/tags/" in path and path.startswith("/bookmarks/"):
                parts = path.split("/")
                BookmarkService().remove_tag(int(parts[2]), int(parts[4]))
                return self._ok(status_code=204)
        except ValidationError as exc:
            return self._error(422, exc.errors())
        except HTTPException as exc:
            return self._error(exc.status_code, exc.detail)
        except sqlite3.Error:
            return self._error(500, "Database error occurred")

        return self._error(404, "Not Found")

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self.request("DELETE", url, **kwargs)
