import json
import logging
import sys

from freezegun import freeze_time

from cf_helper.logger import _ExtraAdapter, _JsonFormatter, logger, setup_logging


@freeze_time("2026-01-02 03:04:05.678")
def test_json_formatter():
    fmt = _JsonFormatter()

    res = fmt.format(
        logging.LogRecord("name", logging.DEBUG, "path", 0, "msg", None, None)
    )

    assert json.loads(res) == {
        "timestamp": "2026-01-01 22:04:05,677",
        "message": "msg",
        "level": "debug",
        "file": "path",
        "location": "None:0",
    }


@freeze_time("2026-01-02 03:04:05.678")
def test_json_formatter_extra():
    fmt = _JsonFormatter()

    rec = logging.LogRecord("name", logging.DEBUG, "path", 0, "msg", None, None)
    setattr(rec, "extra", {"foo": "bar"})

    res = fmt.format(rec)

    assert json.loads(res) == {
        "timestamp": "2026-01-01 22:04:05,677",
        "message": "msg",
        "level": "debug",
        "file": "path",
        "location": "None:0",
        "extra": {"foo": "bar"},
    }


@freeze_time("2026-01-02 03:04:05.678")
def test_json_formatter_error():
    fmt = _JsonFormatter()

    res = fmt.format(
        logging.LogRecord(
            "name",
            logging.DEBUG,
            "path",
            0,
            "msg",
            None,
            (Exception, Exception("error"), None),
        )
    )

    assert json.loads(res) == {
        "timestamp": "2026-01-01 22:04:05,677",
        "message": "msg",
        "level": "debug",
        "file": "path",
        "location": "None:0",
        "exception": {
            "name": "Exception",
            "value": "error",
            "stack": ["Exception: error\n"],
        },
    }


def test_setup_logger():
    setup_logging(force=True)

    assert isinstance(logging.root.handlers[0], logging.StreamHandler)
    assert logging.root.handlers[0].stream is sys.stdout


def test_setup_logger_prod(monkeypatch):
    monkeypatch.setenv("ENV", "prod")

    setup_logging(force=True)

    assert isinstance(logging.root.handlers[0], logging.StreamHandler)
    assert logging.root.handlers[0].stream is sys.stdout
    assert isinstance(logging.root.handlers[0].formatter, _JsonFormatter)


def test_extra_adapter():
    adp = _ExtraAdapter(logging.root, extra={"foo": "bar"})

    _, kwargs = adp.process("", {})

    assert kwargs["extra"] == {"extra": {"foo": "bar"}}


def test_extra_adapter_merge():
    adp = _ExtraAdapter(logging.root, merge_extra=True, extra={"foo": "bar"})

    _, kwargs = adp.process("", {"extra": {"more": "baz"}})

    assert kwargs["extra"] == {"extra": {"foo": "bar", "more": "baz"}}


def test_extra_adapter_merge_no_extra():
    adp = _ExtraAdapter(logging.root, merge_extra=True)

    _, kwargs = adp.process("", {"extra": {"more": "baz"}})

    assert kwargs["extra"] == {"extra": {"more": "baz"}}


def test_extra_adapter_disable_merge():
    adp = _ExtraAdapter(logging.root, merge_extra=False, extra={"foo": "bar"})

    _, kwargs = adp.process("", {"extra": {"more": "baz"}})

    assert kwargs["extra"] == {"extra": {"foo": "bar"}}


def test_extra_adapter_append_keys():
    adp = _ExtraAdapter(logging.root, merge_extra=True)
    # Attach when self.extra is None
    adp.attach_keys(foo="bar")
    # Attach when self.extra is not None (branch coverage)
    adp.attach_keys(baz="bash")

    _, kwargs = adp.process("", {"extra": {"more": "baz"}})

    assert kwargs["extra"] == {"extra": {"foo": "bar", "baz": "bash", "more": "baz"}}


def test_logger():
    assert isinstance(logger, _ExtraAdapter)
    assert logger.merge_extra
