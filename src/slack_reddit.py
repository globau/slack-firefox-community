import argparse
import json
import logging
import re
import urllib.parse as url_parse
from datetime import datetime
from pathlib import Path
from typing import List, Set

import feedparser

import cli
import slack
from cli import logger
from rss import Post


def subreddit_type(arg: str) -> str:
    if m := re.search(r"^/r/([^/]+)/?$", arg):
        subreddit = m[1]
    elif m := re.search(r"^https://[^/]+/r/([^/]+)/?$", arg):
        subreddit = m[1]
    else:
        subreddit = arg
    if not re.search(r"^[a-zA-Z0-9_]+$", subreddit):
        raise argparse.ArgumentTypeError("Not a valid subreddit name")
    return subreddit


def webhook_type(arg: str) -> str:
    if arg == "DEBUG":
        return arg
    url = url_parse.urlparse(arg)
    if (
        url.scheme != "https"
        or url.hostname != "hooks.slack.com"
        or not url.path.startswith("/services/")
    ):
        raise argparse.ArgumentTypeError("Not a valid Slack 'Incoming Webhook' URL")
    return arg


def main() -> None:
    # command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("subreddit", type=subreddit_type, help="source subreddit")
    parser.add_argument(
        "webhook_url", type=webhook_type, help="slack incoming webhook url"
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("--quiet", "-q", action="store_true", help="less output")
    verbosity.add_argument("--debug", "-d", action="store_true", help="more output")
    args = parser.parse_args()
    if args.quiet:
        logger.setLevel(logging.ERROR)
    elif args.debug:
        logger.setLevel(logging.DEBUG)
    subreddit = args.subreddit

    # prepare state tracking
    state_path = Path(__file__).parent.parent / "state"
    state_path.mkdir(exist_ok=True)
    state_file = state_path / f"{subreddit}.json"
    try:
        with state_file.open() as f:
            published = json.load(f)
    except IOError:
        published = {}

    # fetch rss and posts
    logger.info(f"fetching r/{subreddit}")
    rss = feedparser.parse(f"https://reddit.com/r/{subreddit}.rss")
    posts: List[Post] = sorted(Post(entry) for entry in rss.entries)

    # find new posts
    current_posts: Set[str] = set()
    for post in posts:
        current_posts.add(post.id)
        if post.id in published:
            continue

        # post to slack
        slack.notify(args.webhook_url, post)

        # mark as done
        published[post.id] = datetime.utcnow().isoformat()
        with state_file.open(mode="w") as f:
            json.dump(published, f, indent=True, sort_keys=True)

    # remove stale state entries
    published_posts = set(published.keys())
    stale_posts = published_posts - current_posts
    if stale_posts:
        for post_id in stale_posts:
            del published[post_id]
        with state_file.open(mode="w") as f:
            json.dump(published, f, indent=True, sort_keys=True)


if __name__ == "__main__":
    cli.main(main)
