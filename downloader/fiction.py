from dataclasses import dataclass
from typing import Optional

from downloader.constants import ROYAL_ROAD_FICTIONS_URL

@dataclass(frozen=True)
class Fiction:
    title: str
    number: int
    title_url: str
    chapter_1_url: Optional[str] = None

    base_url = ROYAL_ROAD_FICTIONS_URL
    def home_page_url(self) -> str:
        return f"{self.base_url}/{self.number}/{self.title_url}"
