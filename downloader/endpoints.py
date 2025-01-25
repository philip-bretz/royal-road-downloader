from downloader.fetcher import ChapterFetcher
from downloader.fiction import (
    FictionTitleRequest,
    FictionRequest,
    Fiction,
)
from downloader.mock_database import MockDatabase


def get_fiction(fiction_request: FictionRequest):
    ...


def get_fiction_from_title(fiction_title_request: FictionTitleRequest, db: MockDatabase):
    fiction = db.read(fiction_title_request.title)
    if fiction is not None:
        return get_fiction(fiction.request())
