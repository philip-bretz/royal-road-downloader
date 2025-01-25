from downloader.fiction import Fiction
from downloader.download import download as download_core
from downloader.renderer import RenderFormat
from downloader.mock_database import MockDatabase
from fastapi import FastAPI
from typing import Optional

db = MockDatabase({
    "Delve": Fiction(title="Delve", number=25225),
    "Mother of Learning": Fiction(title="Mother of Learning", number=21220)
})
app = FastAPI(title="Royal Road Fiction Downloader")


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
