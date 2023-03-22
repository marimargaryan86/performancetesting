import logging
from typing import Any, Callable, Sequence

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
        # todo: Add prometheus_level_processor,
        structlog.processors.TimeStamper(fmt="iso"),
    ]


def _get_after_processors() -> list[Processor]:
    return [
        structlog_sentry.SentryProcessor(event_level=logging.ERROR),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
