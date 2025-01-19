from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from downloader.chapter import Chapter
from downloader.fiction import Fiction
from downloader.log import getLogger


logger = getLogger(__name__)


class RenderFailure(Exception):
    pass


class RendererBase(ABC):
    @abstractmethod
    def render(self, outfile, fiction: Fiction, chapters: list[Chapter]) -> None:
        ...

    def save_to_file(self, fiction: Fiction, chapters: list[Chapter], save_dir: Optional[str] = None) -> None:
        filename = f'{save_dir}/{fiction.title}.html' if save_dir is not None else f'{fiction.title}.html'
        with open(filename, "w+", encoding="utf-8") as outfile:
            self.render(outfile, fiction, chapters)
        outfile.close()


CSS = '''
.chapter-content table {
    background: #004b7a;
    margin: 10px auto;
    width: 90%;
    border: none;
    box-shadow: 1px 1px 1px rgba(0,0,0,.75);
    border-collapse: separate;
    border-spacing: 2px;
}
.chapter-content table td {
    color: #ccc;
}
'''


@dataclass(frozen=True)
class HTMLRendererSettings:
    stylesheet: str = CSS
    default_bottom_author_note: bool = True


class HTMLRenderer(RendererBase):
    def __init__(self, settings: HTMLRendererSettings = HTMLRendererSettings()):
        self._settings = settings

    def render(self, outfile, fiction: Fiction, chapters: list[Chapter]) -> None:
        logger.info(f"Rendering fiction {fiction.title} to HTML")
        book = f'<style>{self._settings.stylesheet}</style>'
        for chapter in chapters:
            book += self._chapter_html(chapter)
        outfile.write(book)
        logger.info("Rendering complete")

    def _chapter_html(self, chapter: Chapter) -> str:
        title = f'<h1 class=\"chapter\">{chapter.title}</h1>\n'
        top_author_note = ""
        bottom_author_note = ""
        match len(chapter.author_notes):
            case 0:
                pass
            case 1:
                note = f'<h3 class=\"author_note\"> Author note </h3>\n{chapter.author_notes[0]}'
                if self._settings.default_bottom_author_note:
                    bottom_author_note = note
                else:
                    top_author_note = note
            case 2:
                top_author_note = f'<h3 class=\"author_note\"> Author note </h3>\n{chapter.author_notes[0]}'
                bottom_author_note = f'<h3 class=\"author_note\"> Author note </h3>\n{chapter.author_notes[1]}'
            case _:
                raise RenderFailure(f"Invalid number of author notes")
        return f'{title}{top_author_note}{chapter.body}{bottom_author_note}'

