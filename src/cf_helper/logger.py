import json
import logging
import os
import sys
import traceback as tb
from enum import StrEnum
from typing import Any


class _color(StrEnum):
    """https://stackoverflow.com/a/17303428"""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        rec: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "message": record.getMessage(),
            "level": record.levelname.lower(),
            "file": record.pathname,
            "location": f"{record.funcName}:{record.lineno}",
        }
        if hasattr(record, "extra"):
            rec["extra"] = getattr(record, "extra")
        if record.exc_info:
            exc_type, exc, stack = record.exc_info
            exc_name = exc_type.__name__ if exc_type else "UnknownError"
            rec["exception"] = {
                "name": exc_name,
                "value": str(exc),
                "stack": tb.format_exception(exc),
            }
        return json.dumps(rec)


class _ExtraAdapter(logging.LoggerAdapter):
    def __init__(self, logger, extra=None, merge_extra=False):
        super().__init__(logger, extra=extra)
        # self.merge_extra added in python 3.13
        self.merge_extra = merge_extra

    def process(self, msg, kwargs):
        if self.merge_extra and kwargs.get("extra") is not None:
            if self.extra is not None:
                kwargs["extra"] = {"extra": {**self.extra, **kwargs["extra"]}}
            else:
                kwargs["extra"] = {"extra": kwargs["extra"]}
        else:
            kwargs["extra"] = {"extra": self.extra}
        return msg, kwargs

    def attach_keys(self, **extra):
        if self.extra is None:
            self.extra = {}
        self.extra = {**self.extra, **extra}


def setup_logging(force: bool | None = None, color: bool = True):
    hdl = logging.StreamHandler(sys.stdout)
    if os.getenv("ENV") == "prod":
        hdl.setFormatter(_JsonFormatter())
    else:  # pragma no cover
        if color:
            fmt = (
                f"{_color.GREEN}%(levelname)-6s{_color.RESET}  "
                f"{_color.BLUE}%(asctime)s{_color.RESET} "
                f"[{_color.BOLD}%(funcName)s:%(lineno)d{_color.RESET}] %(message)s"
            )
        else:
            fmt = "%(levelname)-6s  %(asctime)s [%(funcName)s:%(lineno)d] %(message)s"
        hdl.setFormatter(logging.Formatter(fmt=fmt))
    logging.basicConfig(level=logging.DEBUG, handlers=[hdl], force=force)


logger = _ExtraAdapter(logging.getLogger(__name__), merge_extra=True)
