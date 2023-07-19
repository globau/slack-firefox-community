import re
import time
from typing import Any

import bs4
import feedparser

from cli import logger
from feed import Feed, Post


class RedditPost(Post):
    def __init__(self, feed: Feed, entry: dict[str, Any]) -> None:
        media = "https://www.redditstatic.com/new-icon.png"
        try:
            media = entry["media_thumbnail"][0]["url"]
        except (KeyError, IndexError):
            pass

        content: str = bs4.BeautifulSoup(entry["summary"], features="lxml").text
        content = re.sub(r"\[link] \[comments].*", "", content, flags=re.S)
        content = re.sub(r" +", " ", content)
        content = re.sub(r" (submitted by /)", "\n\n\\1", content)

        super().__init__(
            feed=feed,
            identifier=entry["id"],
            published=time.mktime(entry["published_parsed"]),
            title=entry["title"],
            link=entry["link"],
            media=media,
            content=content,
        )


class RedditFeed(Feed):
    def __init__(self) -> None:
        super().__init__("reddit-mozillafirefox")

    def posts(self) -> list[Post]:
        logger.info("fetching reddit.com/r/mozillafirefox")
        rss = feedparser.parse("https://reddit.com/r/mozillafirefox.rss")
        return [RedditPost(self, entry) for entry in rss.entries]
