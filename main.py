from downloader.fiction import Fiction
from downloader.chapter_fetcher import ChapterFetcher

fiction = Fiction(
    "Mother of Learning",
    21220,
    "mother-of-learning",
    "301778/1-good-morning-brothe",
)
fetcher = ChapterFetcher(fiction)
chapters = fetcher.fetch(up_to_chapter=2)
print("done")
