import logging
import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.database import init_db
from api.routers.bookmarks import router as bookmarks_router
from api.routers.folders import router as folders_router
from api.routers.settings import router as settings_router
from api.routers.tags import router as tags_router

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


logger = logging.getLogger(__name__)


app = FastAPI(title="Bookmark Manager API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(sqlite3.Error)
async def sqlite_exception_handler(request, exc):
    logger.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Database error occurred"})


@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}


app.include_router(bookmarks_router)
app.include_router(folders_router)
app.include_router(settings_router)
app.include_router(tags_router)


def main() -> None:
    import uvicorn

    uvicorn.run("api.main:app", reload=True)
