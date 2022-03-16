import json
import logging
from typing import Any

import freezegun
import pytest
import structlog
from _pytest import capture  # noqa: WPS436

from snowfall.stdlib.logging import filtering, stdout


def _decode_log(capsys: capture.CaptureFixture[str]) -> dict[str, Any]:
    return json.loads(capsys.readouterr().out.strip())


@pytest.mark.asyncio
class TestStructlog(object):
    async def test_format_is_json(self, capsys: capture.CaptureFixture[str]) -> None:
        stdout.configure_logger()
        logger = structlog.get_logger("testing")
        logger.info("test")
        json_message = capsys.readouterr().out.strip()
        assert json.loads(json_message)

    @freezegun.freeze_time("2021-12-21 12:12:12.121212")
    @pytest.mark.parametrize(
        "field,expected",
        [
            ("event", "test"),
            ("level", "info"),
            ("logger", "testing"),
            ("source", "application"),
            ("timestamp", "2021-12-21T12:12:12.121212Z"),
        ],
    )
    async def test_event_is_set(
        self,
        capsys: capture.CaptureFixture[str],
        field: str,
        expected: str,
    ) -> None:
        stdout.configure_logger()
        logger = structlog.get_logger("testing")
        logger.info("test")
        json_message = _decode_log(capsys)
        assert json_message.get(field) == expected

    async def test_kwargs(self, capsys: capture.CaptureFixture[str]) -> None:
        stdout.configure_logger()
        logger = structlog.get_logger("testing")
        logger.info("test", field="testing")
        json_message = _decode_log(capsys)
        assert json_message.get("field") == "testing"

    async def test_bound_kwarg(self, capsys: capture.CaptureFixture[str]) -> None:
        stdout.configure_logger()
        logger = structlog.get_logger("testing")
        logger = logger.bind(field="testing")
        logger.info("test")
        json_message = _decode_log(capsys)
        assert json_message.get("field") == "testing"

    @pytest.mark.parametrize("field", filtering.SECRET_WORDS)
    async def test_secrets_are_masked(
        self,
        field: str,
        capsys: capture.CaptureFixture[str],
    ) -> None:
        stdout.configure_logger()
        logger = structlog.get_logger("testing")
        logger.info("test", **{field: "testing"})
        json_message = _decode_log(capsys)
        assert json_message.get(field) == filtering.FILTERED_WORD

    async def test_context_binding_call(
        self,
        capsys: capture.CaptureFixture[str],
    ) -> None:
        stdout.configure_logger()
        logger = structlog.get_logger("testing")

        with stdout.context_binding(field="testing"):
            logger.info("test")

        json_message = _decode_log(capsys)
        assert json_message.get("field") == "testing"

    async def test_context_binding_is_unset(
        self,
        capsys: capture.CaptureFixture[str],
    ) -> None:
        stdout.configure_logger()
        logger = structlog.get_logger("testing")

        with stdout.context_binding(field="testing"):
            logger.info("test")

        json_message = _decode_log(capsys)
        assert json_message.get("field") == "testing"
        logger.info("test")
        json_message = _decode_log(capsys)
        assert json_message.get("field") is None

    async def test_context_binding_manager(
        self,
        capsys: capture.CaptureFixture[str],
    ) -> None:
        stdout.configure_logger()
        logger = structlog.get_logger("testing")

        with stdout.context_binding() as context:
            context.bind(field="testing")
            logger.info("test")

        json_message = _decode_log(capsys)
        assert json_message.get("field") == "testing"

    async def test_nested_context_binding_manager(
        self,
        capsys: capture.CaptureFixture[str],
    ) -> None:
        stdout.configure_logger()
        logger = structlog.get_logger("testing")

        with stdout.context_binding(first="testing"):
            logger.info("test")
            first_message = _decode_log(capsys)

            with stdout.context_binding(second="testing again"):
                logger.info("test")

        second_message = _decode_log(capsys)
        assert first_message.get("first") == "testing"
        assert second_message.get("second") == "testing again"


class TestStandardLogger(object):
    @pytest.mark.parametrize(
        "level, below",
        [
            (logging.INFO, logging.DEBUG),
            (logging.WARN, logging.INFO),
            (logging.ERROR, logging.WARN),
            (logging.CRITICAL, logging.ERROR),
        ],
    )
    def test_log_level_is_set(self, level: int, below: int) -> None:
        stdout.configure_logger(level=level)
        logger = logging.getLogger("testing")
        assert logger.isEnabledFor(level)
        assert not logger.isEnabledFor(below)

    def test_format_is_json(self, capsys: capture.CaptureFixture[str]) -> None:
        stdout.configure_logger()
        logger = logging.getLogger("testing")
        logger.info("test")
        json_message = capsys.readouterr().out.strip()
        assert json.loads(json_message)

    @freezegun.freeze_time("2021-12-21 12:12:12.121212")
    @pytest.mark.parametrize(
        "field,expected",
        [
            ("event", "test"),
            ("level", "info"),
            ("logger", "testing"),
            ("source", "application"),
            ("timestamp", "2021-12-21T12:12:12.121212Z"),
        ],
    )
    def test_event_is_set(
        self,
        capsys: capture.CaptureFixture[str],
        field: str,
        expected: str,
    ) -> None:
        stdout.configure_logger()
        logger = logging.getLogger("testing")
        logger.info("test")
        json_message = _decode_log(capsys)
        assert json_message.get(field) == expected


def test_context_value_can_be_returned() -> None:
    structlog.contextvars.bind_contextvars(foo="bar")
    assert stdout.get_context_value("foo") == "bar"


def test_missing_context_value_is_none() -> None:
    assert stdout.get_context_value("baz") is None
