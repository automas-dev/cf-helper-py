import json
import io
import pytest
from cf_helper.logger import _Logger
from freezegun import freeze_time


@freeze_time("2026-01-02 03:04:05.678")
def test_logger_log():
    sink = io.StringIO()

    logger = _Logger(sink)
    logger.log("info", "Hello world")

    assert json.loads(sink.getvalue()) == {
        "timestamp": "2026-01-02T03:04:05.678000",
        "message": "Hello world",
        "level": "info",
        "extra": {},
        "file": "TODO",
        "location": "TODO:TODO",
    }


@freeze_time("2026-01-02 03:04:05.678")
@pytest.mark.parametrize(
    "fn,level",
    [
        ("debug", "debug"),
        ("info", "info"),
        ("warn", "warn"),
        ("error", "error"),
        ("exception", "error"),
    ],
)
def test_logger_levels(fn, level):
    sink = io.StringIO()
    logger = _Logger(sink)
    getattr(logger, fn)("Hello world")
    assert json.loads(sink.getvalue())["level"] == level
