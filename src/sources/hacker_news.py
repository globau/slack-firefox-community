import re
import time
from typing import Any

import feedparser

from cli import logger
from feed import Feed, Post


class HackerNewsPost(Post):
    def __init__(self, feed: Feed, entry: dict[str, Any]) -> None:
        super().__init__(
            feed=feed,
            identifier=entry["id"],
            published=time.mktime(entry["published_parsed"]),
            title=entry["title"],
            link=entry["link"],
            media="https://news.ycombinator.com/y18.svg",
            content="",
        )


def _include(entry: dict[str, Any]) -> bool:
    return re.search(r"\bfirefox\b", entry["title"], flags=re.I) is not None


class HackerNewsFeed(Feed):
    def __init__(self) -> None:
        super().__init__("hacker-news")

    def posts(self) -> list[Post]:
        logger.info("fetching hacker-news")
        rss = feedparser.parse("https://news.ycombinator.com/rss")
        return [HackerNewsPost(self, entry) for entry in rss.entries if _include(entry)]
