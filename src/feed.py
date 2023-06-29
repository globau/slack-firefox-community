import abc
import functools
import json
from datetime import datetime
from pathlib import Path


@functools.total_ordering
class Post:
    def __init__(
        self,
        *,
        feed: "Feed",
        identifier: str,
        published: float,
        title: str,
        link: str,
        media: str,
        content: str,
    ) -> None:
        self.feed = feed
        self.id = identifier
        self.published = published
        self.title = title
        self.link = link
        self.media = media
        self.content = content

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Post)
        return self.id == other.id

    def __lt__(self, other: object) -> bool:
        assert isinstance(other, Post)
        return self.published < other.published

    def __repr__(self) -> str:
        return f"{self.id} {self.title}"

    def mark_as_notified(self) -> None:
        self.feed.mark_as_notified(self)


class Feed:
    def __init__(self, identifier: str) -> None:
        self.id = identifier
        state_path = Path(__file__).parent.parent / "state"
        state_path.mkdir(exist_ok=True)
        self.state_file = state_path / f"{self.id}.json"

    @abc.abstractmethod
    def posts(self) -> list[Post]:
        pass

    def _load_published(self) -> dict[str, str]:
        try:
            with self.state_file.open() as f:
                return json.load(f)
        except OSError:
            return {}

    def _save_published(self, published: dict[str, str]) -> None:
        with self.state_file.open(mode="w") as f:
            json.dump(published, f, indent=True, sort_keys=True)

    def new_posts(self) -> list[Post]:
        published = self._load_published()

        # find new posts
        new_posts = []
        current_posts: set[str] = set()
        for post in self.posts():
            current_posts.add(post.id)
            if post.id not in published:
                new_posts.append(post)

        # remove stale state entries
        published_posts = set(published.keys())
        stale_posts = published_posts - current_posts
        if stale_posts:
            for post_id in stale_posts:
                del published[post_id]
            self._save_published(published)

        return new_posts

    def mark_as_notified(self, post: Post) -> None:
        published = self._load_published()
        published[post.id] = datetime.utcnow().isoformat()
        self._save_published(published)
