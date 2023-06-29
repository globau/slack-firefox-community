import argparse
import logging
import urllib.parse as url_parse

import cli
import slack
from cli import logger
from sources.fedia import FediaFeed
from sources.reddit import RedditFeed


def webhook_type(arg: str) -> str:
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

    posts = []
    for feed in (RedditFeed(), FediaFeed()):
        posts.extend(feed.new_posts())

    for post in sorted(posts):
        print(post)

    for post in sorted(posts):
        slack.notify(args.webhook_url, post)
        feed.mark_as_notified(post)


if __name__ == "__main__":
    cli.main(main)
