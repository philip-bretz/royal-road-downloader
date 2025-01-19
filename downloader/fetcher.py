from abc import ABC, abstractmethod
from random import randrange
from requests_html import HTMLSession, HTML
from typing import Optional

import time

from downloader.chapter import Chapter
from downloader.constants import ROYAL_ROAD_URL
from downloader.fiction import Fiction
from downloader.log import getLogger


logger = getLogger(__name__)


class FetchFailed(Exception):
    pass


class FinalChapter(Exception):
    pass


MAX_CHAPTER = 10_000


def _rand_sleep() -> None:
    time.sleep(randrange(20, 50) / 100)


class ChapterFetcherBase(ABC):
    @abstractmethod
    def fetch_chapter_1(self) -> Chapter:
        ...
    
    @abstractmethod
    def fetch_next_chapter(self, current_chapter: Chapter) -> Chapter:
        ...

    def fetch(self, up_to_chapter: Optional[int] = None) -> list[Chapter]:
        if up_to_chapter is None:
            up_to_chapter = MAX_CHAPTER
        up_to_chapter = min(up_to_chapter, MAX_CHAPTER)
        chapters = [self.fetch_chapter_1()]
        for i in range(1, up_to_chapter):
            try:
                next_chapter = self.fetch_next_chapter(chapters[-1])
                chapters.append(next_chapter)
            except FinalChapter:
                return chapters
        return chapters


class ChapterFetcher(ChapterFetcherBase):
    def __init__(self, fiction: Fiction):
        self._fiction = fiction
        self._session = HTMLSession()

    def fetch(self, up_to_chapter: Optional[int] = None) -> list[Chapter]:
        logger.info(f"Fetching fiction {self._fiction.title}")
        chapters = super().fetch(up_to_chapter)
        logger.info(f"Fetching complete with {len(chapters)} chapters")
        return chapters

    def fetch_chapter_1(self) -> Chapter:
        try:
            home_page_response = self._session.get(self._fiction.home_page_url())
            chapter_1_url = self._chapter_1_url(home_page_response.html)
        except:
            raise FetchFailed(f"Fetch for fiction {self._fiction} failed at extraction Chapter 1 url from home page")
        try:
            return self._fetch_chapter_from_url(1, chapter_1_url)
        except:
            raise FetchFailed(f"Fetch for fiction {self._fiction} failed at extracting Chapter 1")

    def fetch_next_chapter(self, current_chapter: Chapter) -> Chapter:
        if current_chapter.next_chapter_url is None:
            raise FinalChapter
        try:
            return self._fetch_chapter_from_url(current_chapter.chapter_num + 1, current_chapter.next_chapter_url)
        except:
            raise FetchFailed(f"Fetch for fiction {self._fiction} failed at extracting Chapter {current_chapter.chapter_num + 1}")

    def _fetch_chapter_from_url(self, chapter_num: int, chapter_url: str) -> Chapter:
        _rand_sleep()
        chapter_response = self._session.get(chapter_url)
        return self._html_to_chapter(chapter_num, chapter_response.html)

    def _html_to_chapter(self, chapter_num: int, chapter_html: HTML) -> Chapter:
        title = (chapter_html.find('h1.font-white')[0]).text
        body = chapter_html.find('.chapter-inner',first=True).html
        author_notes_raw = chapter_html.find('.portlet-body.author-note')
        author_notes = [note.html for note in author_notes_raw]
        next_chapter_url_raw = chapter_html.find('[rel=next]')
        next_chapter_url = None if len(next_chapter_url_raw) == 0 else ROYAL_ROAD_URL + next_chapter_url_raw[0].attrs.get("href")
        logger.info(title)
        return Chapter(
            chapter_num=chapter_num,
            title=title,
            body=body,
            author_notes=author_notes,
            next_chapter_url=next_chapter_url,
        )

    def _chapter_1_url(self, home_page: HTML) -> str:
        if self._fiction.chapter_1_url is None:
            raise NotImplementedError("Chapter 1 url finding not yet implemented")
        return f"{self._fiction.home_page_url()}/chapter/{self._fiction.chapter_1_url}"
