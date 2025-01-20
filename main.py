from downloader.fiction import FictionRequest
from downloader.fetcher import ChapterFetcher
from downloader.renderer import HTMLRenderer

fiction = FictionRequest(
    title="Mother of Learning",
    number=21220,
)
fetcher = ChapterFetcher(fiction)
fiction_details = fetcher.fetch_details()
chapters = fetcher.fetch(up_to_chapter=2)
renderer = HTMLRenderer()
print(fiction_details)
#renderer.save_to_file(fiction, chapters)
