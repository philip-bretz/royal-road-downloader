from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path
from typing import Optional

from downloader.fiction import Fiction
from downloader.download import download as download_core
from downloader.renderer import RenderFormat
from downloader.simple_database import SimpleDatabase

DB_FILENAME = Path(__file__).parent.joinpath("db_config/saved_fictions.csv")

db = SimpleDatabase({
    "Delve": Fiction(title="Delve", number=25225),
    "Mother of Learning": Fiction(title="Mother of Learning", number=21220)
})


@asynccontextmanager
async def lifespan(app: FastAPI):
    if DB_FILENAME.exists():
        loaded_db = SimpleDatabase.from_csv(DB_FILENAME)
        db.overwrite(loaded_db.fictions_dict())
    yield
    db.to_csv(DB_FILENAME)


app = FastAPI(title="Royal Road Fiction Downloader", lifespan=lifespan)


@app.get("/fiction/{title}")
async def read_fiction(title: str) -> Fiction | None:
    return db.read(title)

@app.get("/fictions/")
async def read_fictions(skip: int = 0, limit: int = 10) -> list[Fiction]:
    return db.view(skip, limit)

@app.get("/download/{title}/{number}")
async def download(title: str, number: int, chapters: Optional[int] = None, format: RenderFormat = RenderFormat.HTML) -> Fiction:
    return download_core(title, number, chapters, format, db)

@app.get("/download_from_title/{title}")
async def download(title: str, chapters: Optional[int] = None, format: RenderFormat = RenderFormat.HTML) -> Fiction | None:
    fiction = db.read(title)
    if fiction is not None:
        return download_core(title, fiction.number, chapters, format, db)
