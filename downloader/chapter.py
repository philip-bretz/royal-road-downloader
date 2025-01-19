from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Chapter:
    chapter_num: int
    title: str
    body: str
    author_notes: list[str] = field(default_factory=list)
    next_chapter_url: Optional[str] = None
