import re
import time
from typing import Any

import feedparser

from cli import logger
from feed import Feed, Post


class LobstersPost(Post):
    def __init__(self, entry: dict[str, Any]) -> None:
        super().__init__(
            identifier=entry["id"],
            published=time.mktime(entry["published_parsed"]),
            title=entry["title"],
            link=entry["link"],
            media="https://news.ycombinator.com/y18.svg",
            content="",
        )


def _include(entry: dict[str, Any]) -> bool:
    return re.search(r"\bfirefox\b", entry["title"], flags=re.I) is not None


class LobstersFeed(Feed):
    def __init__(self) -> None:
        super().__init__("lobsters")

    def posts(self) -> list[Post]:
        logger.info("fetching lobsters")
        rss = feedparser.parse("https://lobste.rs/newest.rss")
        return [LobstersPost(entry) for entry in rss.entries if _include(entry)]
