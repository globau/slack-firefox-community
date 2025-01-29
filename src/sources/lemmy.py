import time
from typing import Any

from cli import logger
from feed import Feed, Post


class LemmyPost(Post):
    def __init__(self, feed: Feed, entry: dict[str, Any]) -> None:
        media = "https://lemmy.ml/pictrs/image/fa6d9660-4f1f-4e90-ac73-b897216db6f3.png"

        super().__init__(
            feed=feed,
            identifier=entry["id"],
            published=time.mktime(entry["published_parsed"]),
            title=entry["title"],
            link=entry["link"],
            media=media,
            content="",
        )


class LemmyFeed(Feed):
    def __init__(self) -> None:
        super().__init__("lemmy-firefox")

    def posts(self) -> list[Post]:
        logger.info("fetching lemmy.ml/c/firefox")
        entries = self.fetch_entries("https://lemmy.ml/feeds/c/firefox.xml?sort=New")
        logger.info(f"  found {len(entries)} entries")
        return [LemmyPost(self, entry) for entry in entries]
