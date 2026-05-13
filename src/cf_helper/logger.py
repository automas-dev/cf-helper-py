import json
import sys
import traceback as _tb
from copy import deepcopy
from datetime import datetime


class _Logger:
    def __init__(self, sink=sys.stdout):
        self.extra = {}
        self.sink = sink

    def attach_keys(self, **extra):
        self.extra.update(extra)

    def log(self, level, message, extra={}, exc_info: BaseException | None = None):
        record_extra = deepcopy(self.extra)
        record_extra.update(extra)
        record = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": level,
            "extra": record_extra,
            "file": "TODO",
            "location": "TODO:TODO",
        }
        if exc_info is not None:
            record["exception"] = {
                "name": type(exc_info).__name__,
                "value": str(exc_info),
                "stack": _tb.format_exception(exc_info),
            }
        message = json.dumps(record)
        self.sink.write(message + "\n")

    def debug(self, message, **extra):
        self.log("debug", message, extra)

    def info(self, message, **extra):
        self.log("info", message, extra)

    def warn(self, message, **extra):
        self.log("warn", message, extra)

    def error(self, message, **extra):
        self.log("error", message, extra)

    def exception(self, message, exec_info=None, **extra):
        self.log("error", message, extra)


logger = _Logger()
