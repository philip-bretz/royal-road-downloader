from downloader.fiction import Fiction, FictionRequest
from downloader.fetcher import ChapterFetcher
from downloader.renderer import HTMLRenderer
from downloader.mock_database import MockDatabase
from fastapi import FastAPI
from typing import Optional

db = MockDatabase({
    "Delve": Fiction(title="Delve", number=25225),
    "Mother of Learning": Fiction(title="Mother of Learning", number=21220)
})
app = FastAPI(title="Royal Road Fiction Downloader")


@app.get("/fiction/{title}")
async def read_fiction(title: str):
    return db.read(title)

@app.get("/fictions/")
async def read_fictions(skip: int = 0, limit: int = 10):
    return db.view(skip, limit)

def _download(title: str, number: int, chapters: Optional[int]):
    fiction_request = FictionRequest(title=title, number=number)
    fetcher = ChapterFetcher(fiction_request)
    fiction_details = fetcher.fetch_details()
    db.create(fiction_details)
    chapters = fetcher.fetch(up_to_chapter=chapters)
    renderer = HTMLRenderer()
    renderer.save_to_file(fiction_details, chapters)
    return fiction_details

@app.get("/download/{title}/{number}")
async def download(title: str, number: int, chapters: Optional[int] = None):
    return _download(title, number, chapters)

@app.get("/download_from_title/{title}")
async def download(title: str, chapters: Optional[int] = None):
    fiction = db.read(title)
    if fiction is not None:
        return _download(title, fiction.number, chapters)
