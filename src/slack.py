import json
import sys
import urllib.request as url_request

from cli import logger
from rss import Post


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def notify(url: str, post: Post) -> None:
    payload = {
        "text": _escape(post.title),
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*<{post.link}|{_escape(post.title)}>*\n\n"
                        f"{_escape(post.content)}"
                    ),
                },
                "accessory": {
                    "type": "image",
                    "image_url": post.media,
                    "alt_text": "image",
                },
            },
            {
                "type": "divider",
            },
        ],
    }
    logger.debug(json.dumps(payload, indent=2, sort_keys=True))

    if url == "DEBUG":
        return

    try:
        req = url_request.Request(url, method="POST", data=json.dumps(payload).encode())
        url_request.urlopen(req)
    except OSError as e:
        # transient error, bail out but don't treat this as an error
        logger.info(f"failed to post to slack: {e}")
        sys.exit(0)
