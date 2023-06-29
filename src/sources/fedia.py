import time
from typing import Any

import feedparser

from cli import logger
from feed import Feed, Post


class FediaPost(Post):
    def __init__(self, entry: dict[str, Any]) -> None:
        super().__init__(
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
        rss = feedparser.parse("https://fedia.io/rss?magazine=firefox")
        return [FediaPost(entry) for entry in rss.entries]
