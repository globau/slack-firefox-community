import re
import time
import urllib.parse as url_parse
from typing import Any

from cli import logger
from feed import Feed, Post


class HackerNewsPost(Post):
    def __init__(self, feed: Feed, entry: dict[str, Any]) -> None:
        url = url_parse.urlparse(entry["comments"])
        qs = url_parse.parse_qs(url.query)
        super().__init__(
            feed=feed,
            identifier=qs["id"][0],
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
        entries = self.fetch_entries("https://news.ycombinator.com/rss")
        logger.info(f"  found {len(entries)} entries")
        return [HackerNewsPost(self, entry) for entry in entries if _include(entry)]
