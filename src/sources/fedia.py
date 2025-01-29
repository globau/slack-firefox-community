import time
from typing import Any

from cli import logger
from feed import Feed, Post


class FediaPost(Post):
    def __init__(self, feed: Feed, entry: dict[str, Any]) -> None:
        super().__init__(
            feed=feed,
            identifier=entry["id"],
            published=time.mktime(entry["published_parsed"]),
            title=entry["title"],
            link=entry["link"],
            media="https://fedia.io/assets/icons/apple-touch-icon.png",
            content="",
        )


class FediaFeed(Feed):
    def __init__(self) -> None:
        super().__init__("fedia-firefox")

    def posts(self) -> list[Post]:
        logger.info("fetching fedia.io/m/firefox")
        entries = self.fetch_entries("https://fedia.io/rss?magazine=firefox")
        logger.info(f"  found {len(entries)} entries")
        return [FediaPost(self, entry) for entry in entries]
