import logging
import sys
from collections.abc import Callable, Sequence
from typing import Any

import orjson
import structlog
import structlog_sentry

from snowfall.stdlib.logging import filtering, sentry

Processor = Callable[[Any, Any, structlog.types.EventDict], Any]


def default_source_processor(
    logger: Any,
    log_method: Any,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    if "source" not in event_dict:
        event_dict["source"] = "application"

    return event_dict


def filtering_processor(
    logger: Any,
    log_method: Any,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    return filtering.filter_secrets_dict(event_dict)


def get_common_processors(
    additional_processors: Sequence[Processor],
) -> list[Processor]:
    return [
        *_get_before_processors(),
        *additional_processors,
        *_get_after_processors(),
    ]


def get_all_processors(common_processors: Sequence[Processor]) -> list[Processor]:
    return [
        structlog.stdlib.filter_by_level,
        *common_processors,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]


def _get_before_processors() -> list[Processor]:
    return [
        structlog.contextvars.merge_contextvars,
        sentry.sentry_trace_processor,
        default_source_processor,
        filtering_processor,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]


def _get_after_processors() -> list[Processor]:
    return [
        structlog_sentry.SentryProcessor(event_level=logging.ERROR),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]


def _dumps(*args: Any, **kwargs: Any) -> str:
    return orjson.dumps(*args, **kwargs).decode()


def get_log_handler(
    common_processors: Sequence[Processor],
    *,
    format_as_json: bool,
) -> logging.Handler:
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=(
            structlog.processors.JSONRenderer(
                serializer=_dumps,
            )
            if format_as_json
            else structlog.dev.ConsoleRenderer()
        ),
        foreign_pre_chain=common_processors,
    )
    log_handler.setFormatter(formatter)

    return log_handler
