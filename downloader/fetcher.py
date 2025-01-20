from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import randrange
from requests_html import HTMLSession, HTML
from typing import Optional

import re
import time

from downloader.chapter import Chapter
from downloader.constants import ROYAL_ROAD_URL
from downloader.fiction import Fiction, FictionRequest
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


@dataclass(frozen=True)
class ParsedHomePageHeader:
    title: str
    author: str
    chapter_1_link: str
    author_link: str


class ChapterFetcher(ChapterFetcherBase):
    def __init__(self, fiction: FictionRequest):
        self._fiction_request = fiction
        self._session = HTMLSession()

    def fetch_details(self) -> Fiction:
        logger.info(f"Fetching fiction details for {self._fiction_request.title}")
        home_page_response = self._session.get(self._fiction_request.home_page_url())
        fiction = self._details_from_home_page_html(home_page_response.html)
        logger.info("Fetching complete")
        return fiction

    def fetch(self, up_to_chapter: Optional[int] = None) -> list[Chapter]:
        logger.info(f"Fetching fiction {self._fiction_request.title}")
        chapters = super().fetch(up_to_chapter)
        logger.info(f"Fetching complete with {len(chapters)} chapters")
        return chapters

    def fetch_chapter_1(self) -> Chapter:
        home_page_response = self._session.get(self._fiction_request.home_page_url())
        chapter_1_url = self._chapter_1_url(home_page_response.html)
        return self._fetch_chapter_from_url(1, chapter_1_url)

    def fetch_next_chapter(self, current_chapter: Chapter) -> Chapter:
        if current_chapter.next_chapter_url is None:
            raise FinalChapter
        return self._fetch_chapter_from_url(
            current_chapter.chapter_num + 1,
            current_chapter.next_chapter_url,
        )

    def _fetch_chapter_from_url(self, chapter_num: int, chapter_url: str) -> Chapter:
        _rand_sleep()
        chapter_response = self._session.get(chapter_url)
        return self._html_to_chapter(chapter_num, chapter_response.html)

    def _html_to_chapter(self, chapter_num: int, chapter_html: HTML) -> Chapter:
        # NOTE: improve parsing
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

    def _chapter_1_url(self, home_page_html: HTML) -> str:
        parsed_header = self._parse_home_page_header(home_page_html)
        return f"{ROYAL_ROAD_URL}/{parsed_header.chapter_1_link}"

    def _parse_chapter_html(self, chapter_html: HTML):
        raise NotImplementedError

    def _parse_home_page_header(self, home_page_html: HTML) -> ParsedHomePageHeader:
        # Fetch home page header div
        header_div = home_page_html.find(".row.fic-header", first=True)
        if header_div is None:
            raise FetchFailed(f"Unknown formatting for header div of {self._fiction_request.title}")
        # Parse header texts
        header_txts = header_div.text.split("\n")
        if len(header_txts) != 3:
            raise FetchFailed(f"Unknown formatting for header div of {self._fiction_request.title}")
        title = header_txts[0]
        author_match = re.search("^by .*", header_txts[1])
        if author_match is None:
            raise FetchFailed(f"Unknown formatting for author text of {self._fiction_request.title}")
        author = author_match.string[3:]
        # Parse header links
        header_links = list(header_div.links)
        if len(header_links) != 2:
            raise FetchFailed(f"Unknown formatting for header links of {self._fiction_request.title}")
        def _is_author_link(link: str) -> bool:
            return re.search("^/profile/.*", link) is not None
        def _is_ch_1_link(link: str) -> bool:
            return re.search("^/fiction/.*", link) is not None
        if _is_author_link(header_links[0]) and _is_ch_1_link(header_links[1]):
            author_link, ch_1_link = header_links
        elif _is_ch_1_link(header_links[0]) and _is_author_link(header_links[1]):
            ch_1_link, author_link = header_links
        else:
            raise FetchFailed(f"Unknown formatting for header links of {self._fiction_request.title}")
        return ParsedHomePageHeader(
            title=title,
            author=author,
            chapter_1_link=ch_1_link,
            author_link=author_link,
        )

    def _details_from_home_page_html(self, home_page_html: HTML) -> Fiction:
        description_div = home_page_html.find(".hidden-content", first=True)
        if description_div is None:
            raise FetchFailed(f"Unknown formatting for description of {self._fiction_request.title}")
        description = description_div.html
        parsed_header = self._parse_home_page_header(home_page_html)
        return Fiction(
            title=self._fiction_request.title,
            number=self._fiction_request.number,
            author=parsed_header.author,
            description=description,
        )
