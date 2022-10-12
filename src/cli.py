import logging
import os
import sys
import traceback
from typing import Callable

logger = logging.getLogger("slack-reddit")


class Error(Exception):
    pass


class _StreamHandler(logging.StreamHandler):  # type: ignore
    def handleError(self, record: logging.LogRecord) -> None:
        exc_info = sys.exc_info()[0]
        if exc_info and exc_info.__name__ == BrokenPipeError.__name__:
            sys.exit(0)
        super().handleError(record)


class _TextFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__("%(message)s")


class _AnsiFormatter(_TextFormatter):
    def __init__(self) -> None:
        super().__init__()
        self.log_colours = {
            "WARNING": "\033[34m",
            "ERROR": "\033[31m",
            "DEBUG": "\033[90m",
        }

    def format(self, record: logging.LogRecord) -> str:
        result = super().format(record)
        if record.levelname in self.log_colours:
            colour = self.log_colours.get(record.levelname, "")
            result = f"{colour}{result}\033[0m"
        return f"{result}\033[K"


def main(main_func: Callable) -> None:
    has_ansi = (
        (hasattr(sys.stdout, "isatty") and sys.stdout.isatty())
        or os.getenv("TERM", "") == "ANSI"
        or os.getenv("PYCHARM_HOSTED") == "1"
    ) and not (os.getenv("NOANSI") or os.getenv("NO_ANSI"))

    handler = _StreamHandler(sys.stdout)
    if has_ansi:
        handler.setFormatter(_AnsiFormatter())
    else:
        handler.setFormatter(_TextFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    try:
        main_func()

    except KeyboardInterrupt:
        # ^C should just exit
        sys.exit(1)

    except BrokenPipeError:
        # while technically an abnormal condition, it's expected (eg. piping to
        # `head` will close stdout).
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)

    except Error as e:
        # fatal errors without stacktraces
        logger.error(e)
        sys.exit(1)

    except (
        AssertionError,
        AttributeError,
        KeyError,
        IndexError,
        NameError,
        RuntimeError,
        TypeError,
    ) as e:
        # always show stack for coding issues
        logger.exception(e)
        sys.exit(1)

    except OSError as e:
        if logger.isEnabledFor(logging.DEBUG):
            logger.error(traceback.format_exc())
        else:
            if e.filename:
                # include filename/url/hostname in i/o errors
                logger.error(f"{e.strerror or e}: {e.filename}")
            else:
                logger.error(e.strerror or e)
        sys.exit(1)

    except Exception as e:  # pylint: disable=broad-except
        # only show stack when debugging
        if logger.isEnabledFor(logging.DEBUG):
            logger.exception(e)
        else:
            logger.error(f"{e.__class__.__name__}: {e}")
        sys.exit(1)
