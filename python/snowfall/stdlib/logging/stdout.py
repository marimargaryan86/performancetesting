import contextlib
import contextvars
import logging
import sys
from typing import Any, Iterator, Sequence

import orjson
import structlog

from snowfall.stdlib.logging import processors


def configure_logger(
    level: str | int | None = None,
    additional_processors: Sequence[processors.Processor] | None = None,
    wrapper_class: type[structlog.types.BindableLogger] | None = None,
) -> None:
    if not level:
        level = logging.INFO

    if not additional_processors:
        additional_processors = []

    if not wrapper_class:
        wrapper_class = structlog.stdlib.BoundLogger

    common_processors = processors.get_common_processors(additional_processors)
    structlog.configure(
        context_class=dict,
        cache_logger_on_first_use=True,
        wrapper_class=wrapper_class,
        processors=processors.get_all_processors(common_processors),
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    _configure_standard_logger(level, common_processors)


class LogContext(object):
    def __init__(self) -> None:
        self._keys: set[str] = set()

    def bind(self, **kwargs: Any) -> None:
        structlog.contextvars.bind_contextvars(**kwargs)

        self._keys.update(kwargs.keys())

    def unbind(self, *args: str) -> None:
        structlog.contextvars.unbind_contextvars(*args)
        self._keys.difference_update(args)

    def unbind_all(self) -> None:
        structlog.contextvars.unbind_contextvars(*self._keys)
        self._keys.clear()


def get_context_value(key: str) -> str | None:
    context: contextvars.Context = contextvars.copy_context()
    structlog_key = "{prefix}{key}".format(
        prefix=structlog.contextvars.STRUCTLOG_KEY_PREFIX,
        key=key,
    )

    for context_var, context_value in context.items():
        if context_var.name == structlog_key and context_value is not Ellipsis:
            return str(context_value)

    return None


@contextlib.contextmanager
def context_binding(**kwargs: Any) -> Iterator[LogContext]:
    """Return a new context.

    Can be used to bind log context variables and automatically unbind them
    after they have been used for logging.
    """
    log_context = LogContext()
    context = contextvars.copy_context()

    if kwargs:
        log_context.bind(**kwargs)

    try:
        yield log_context
    finally:
        log_context.unbind_all()

        for context_var, context_value in context.items():
            if _is_structlog_context(context, context_var):
                structlog_key = context_var.name[
                    len(structlog.contextvars.STRUCTLOG_KEY_PREFIX) :
                ]
                log_context.bind(**{structlog_key: context_value})


def _is_structlog_context(
    context: contextvars.Context,
    context_var: contextvars.ContextVar[Any],
) -> bool:
    return (
        context_var.name.startswith(structlog.contextvars.STRUCTLOG_KEY_PREFIX)
        and context[context_var] is not Ellipsis
    )


def _configure_standard_logger(
    level: str | int,
    common_processors: Sequence[processors.Processor],
) -> None:
    log_handler = _get_log_handler(common_processors)
    logging.basicConfig(
        format="%(message)s",  # noqa: WPS323
        level=level,
        handlers=[log_handler],
    )
    root_logger = logging.getLogger()
    root_logger.handlers = [log_handler]
    root_logger.setLevel(level)


def _dumps(*args: Any, **kwargs: Any) -> str:
    return orjson.dumps(*args, **kwargs).decode()


def _get_log_handler(
    common_processors: Sequence[processors.Processor],
) -> logging.Handler:
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(
            serializer=_dumps,
        ),
        foreign_pre_chain=common_processors,
    )
    log_handler.setFormatter(formatter)

    return log_handler
