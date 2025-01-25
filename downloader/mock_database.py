from downloader.fiction import Fiction


class MockDatabase:
    def __init__(self, saved_fictions: dict[str, Fiction]):
        for title in saved_fictions.keys():
            assert saved_fictions[title].title == title
        self._fictions = saved_fictions

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
