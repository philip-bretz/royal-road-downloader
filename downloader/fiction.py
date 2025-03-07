from datetime import datetime
from pydantic import BaseModel, Field

from downloader.constants import ROYAL_ROAD_URL
from downloader.utils import utc_now


class FictionTitleRequest(BaseModel):
    title: str = Field(description="Title of fiction")


class FictionRequest(FictionTitleRequest):
    number: int = Field(description="Fiction index in Royal Road site")
    
    def _fmt_title(self) -> str:
        return self.title.lower().replace(" ", "-")

    def relative_url(self) -> str:
        return f"fiction/{self.number}/{self._fmt_title()}"

    def home_page_url(self) -> str:
        return f"{ROYAL_ROAD_URL}/{self.relative_url()}"


class Fiction(FictionRequest):
    author: str = Field(default="", description="Author name")
    last_updated: datetime = Field(default_factory=utc_now, description="Time (UTC) fiction information was last updated")
    description: str = Field(default="", description="Description of fiction")

    def request(self) -> FictionRequest:
        return FictionRequest(
            title=self.title,
            number=self.number,
        )
