from downloader.fiction import Fiction
from downloader.fetcher import ChapterFetcher
from downloader.renderer import HTMLRenderer

fiction = Fiction(
    title="Mother of Learning",
    number=21220,
)
fetcher = ChapterFetcher(fiction, update_mode=True)
chapters = fetcher.fetch(up_to_chapter=2)
renderer = HTMLRenderer()
#renderer.save_to_file(fiction, chapters)
