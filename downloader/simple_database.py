from datetime import datetime

import numpy as np
import pandas as pd

from downloader.fiction import Fiction

TITLE = "title"
NUMBER = "number"
AUTHOR = "author"
LAST_UPDATED = "last_updated"
DESCRIPTION = "description"

DT_FORMAT = "%Y-%m-%d %H:%M:%S"

class SimpleDatabase:
    def __init__(self, saved_fictions: dict[str, Fiction]):
        for title in saved_fictions.keys():
            assert saved_fictions[title].title == title
        self._fictions = saved_fictions

    @classmethod
    def from_csv(cls, filename: str):
        df = pd.read_csv(filename)
        df.fillna("", inplace=True)
        rows = [df.iloc[i].to_dict() for i in range(len(df))]
        fictions = [
            Fiction(
                title=row[TITLE],
                number=row[NUMBER],
                author=row[AUTHOR],
                last_updated=datetime.strptime(row[LAST_UPDATED], DT_FORMAT),
                description=row[DESCRIPTION],
            ) for row in rows
        ]
        return cls({f.title: f for f in fictions})

    def to_csv(self, filename: str) -> None:
        fictions = list(self._fictions.values())
        data = {
            TITLE: [f.title for f in fictions],
            NUMBER: [f.number for f in fictions],
            AUTHOR: [f.author for f in fictions],
            LAST_UPDATED: [f.last_updated.strftime(DT_FORMAT) for f in fictions],
            DESCRIPTION: [f.description for f in fictions],
        }
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)

    def fictions_dict(self) -> dict[str, Fiction]:
        return self._fictions

    def overwrite(self, fictions: dict[str, Fiction]) -> None:
        self._fictions = fictions

    def create(self, fiction: Fiction) -> Fiction:
        self._fictions[fiction.title] = fiction
        return fiction

    def read(self, title: str) -> Fiction | None:
        return self._fictions.get(title)

    def update(self, fiction: Fiction) -> Fiction:
        self._fictions[fiction.title] = fiction
        return fiction

    def delete(self, title: str) -> None:
        if title in self._fictions.keys():
            del self._fictions[title]

    def view(self, skip: int = 0, limit: int = 10) -> list[Fiction]:
        fictions = list(self._fictions.values())
        return [fictions[i] for i in range(skip, skip + limit) if i < len(fictions)]
