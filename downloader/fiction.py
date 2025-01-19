from dataclasses import dataclass
from typing import Optional

from downloader.constants import ROYAL_ROAD_URL

@dataclass(frozen=True)
class Fiction:
    title: str
    number: int
    author: str = ""

    def _fmt_title(self) -> str:
        return self.title.lower().replace(" ", "-")

    def relative_url(self) -> str:
        return f"fiction/{self.number}/{self._fmt_title()}"

    def home_page_url(self) -> str:
        return f"{ROYAL_ROAD_URL}/{self.relative_url()}"
