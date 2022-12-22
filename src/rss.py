import functools
import re
import time
from typing import Any, Dict

import bs4

from cli import logger


@functools.total_ordering
class Post:
    def __init__(self, entry: Dict[str, Any]) -> None:
        logger.debug(entry)

        self.id: str = entry["id"]
        self.title: str = entry["title"]
        self.link: str = entry["link"]
        if "author_detail" in entry:
            self.author: str = entry["author_detail"]["name"]
        else:
            self.author = "[deleted]"
        self.published: float = time.mktime(entry["published_parsed"])

        self.media: str = "https://www.redditstatic.com/new-icon.png"
        try:
            self.media = entry["media_thumbnail"][0]["url"]
        except (KeyError, IndexError):
            pass

        self.content: str = bs4.BeautifulSoup(entry["summary"], features="lxml").text
        self.content = re.sub(r"\[link] \[comments].*", "", self.content, flags=re.S)
        self.content = re.sub(r" +", " ", self.content)
        self.content = re.sub(r" (submitted by /)", "\n\n\\1", self.content)

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Post)
        return self.id == other.id

    def __lt__(self, other: object) -> bool:
        assert isinstance(other, Post)
        return self.published < other.published

    def __repr__(self) -> str:
        return f"{self.id} {self.title}"
