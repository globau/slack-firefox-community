import re
import time
from typing import Any

import bs4
import feedparser

from cli import logger
from feed import Feed, Post


class RedditPost(Post):
    def __init__(self, entry: dict[str, Any]) -> None:
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
            identifier=entry["id"],
            published=time.mktime(entry["published_parsed"]),
            title=entry["title"],
            link=entry["link"],
            media=media,
            content=content,
        )


class RedditFeed(Feed):
    def __init__(self) -> None:
        super().__init__("reddit-firefox")

    def posts(self) -> list[Post]:
        logger.info("fetching reddit.com/r/firefox")
        rss = feedparser.parse("https://reddit.com/r/firefox.rss")
        return [RedditPost(entry) for entry in rss.entries]
