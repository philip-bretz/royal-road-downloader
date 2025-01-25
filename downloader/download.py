from pathlib import Path
from typing import Optional

from downloader.fiction import FictionRequest, Fiction
from downloader.fetcher import ChapterFetcher
from downloader.renderer import HTMLRenderer, RenderFormat
from downloader.mock_database import MockDatabase

SAVE_DIR = Path(__file__).parent.parent.joinpath("downloads")


def download(title: str, number: int, chapters: Optional[int], format: RenderFormat, db: MockDatabase) -> Fiction:
    fiction_request = FictionRequest(title=title, number=number)
    fetcher = ChapterFetcher(fiction_request)
    fiction_details = fetcher.fetch_details()
    db.create(fiction_details)
    chapters = fetcher.fetch(up_to_chapter=chapters)
    match format:
        case RenderFormat.HTML:
            renderer = HTMLRenderer()
        case _:
            raise NotImplementedError
    renderer.save_to_file(fiction_details, chapters, save_dir=SAVE_DIR)
    return fiction_details
