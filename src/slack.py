import json
import sys
import urllib.request as url_request

from cli import logger
from feed import Post


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def notify(url: str, post: Post) -> None:
    # text has a limit of 3000 characters
    header = f"*<{post.link}|{_escape(post.title)}>*\n\n"
    text = f"{header}{_escape(post.content)}"
    if len(text) > 3000:
        length = 3000 - len(header) - 3 + 5
        while len(text) > 3000:
            length -= 5
            text = f"{header}{_escape(post.content[:length])}..."

    payload = {
        "text": _escape(post.title),
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
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
    except url_request.HTTPError as e:
        # transient error, bail out but don't treat this as an error
        logger.info(f"failed to post to slack: {e}")
        try:
            logger.info(e.read().decode())
        except Exception:  # noqa BLE001
            pass
        logger.info(json.dumps(payload, indent=2, sort_keys=True))
        sys.exit(0)
    except OSError as e:
        # transient error, bail out but don't treat this as an error
        logger.info(f"failed to post to slack: {e}")
        logger.info(json.dumps(payload, indent=2, sort_keys=True))
        sys.exit(0)
