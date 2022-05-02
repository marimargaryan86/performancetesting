import contextlib
import logging
import sys
from importlib import import_module, util
from typing import Any, Mapping, Optional, Sequence, Tuple, Type, Union

import sentry_sdk
import structlog
from dateutil import parser
from sentry_sdk import utils as sentry_utils
from sentry_sdk.integrations import logging as sentry_logging

Event = dict[str, Any]
Hint = dict[str, Any]
Integrations = Sequence[sentry_sdk.integrations.Integration]
_DEFAULT_TRACE_SAMPLE_RATE = 0.2
_LOGGER_KEY = "logger"
_LEVEL_KEY = "level"
_IGNORED_ERROR_CLASSES: Tuple[()] = ()


def log_to_sentry_processor(
    logger: Any,
    log_method: Any,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    level_name = event_dict.get(_LEVEL_KEY, "").lower()
    level = int(logging.getLevelName(level_name.upper()))

    if not level:
        return event_dict

    if level >= logging.ERROR:
        SentryLogger.log_event(event_dict, level_name)

    if level >= logging.INFO:
        SentryLogger.log_breadcrumb(event_dict, level_name)

    return event_dict


def sentry_trace_processor(
    logger: Any,
    log_method: Any,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    transaction = sentry_sdk.Hub.current.scope.transaction

    if transaction:
        event_dict["span_id"] = transaction.span_id
        event_dict["trace_id"] = transaction.trace_id

    return event_dict


class SentryLogger(object):
    _ignored_keys = (
        "event",
        "exc_info",
        _LEVEL_KEY,
        _LOGGER_KEY,
        "positional_args",
        "span_id",
        "timestamp",
        "trace_id",
    )
    _tag_keys: list[str] = []

    @classmethod
    def add_tag_keys(cls, tag_keys: Sequence[str]) -> None:
        cls._tag_keys.extend(tag_keys)

    @classmethod
    def log_breadcrumb(
        cls,
        event_dict: structlog.types.EventDict,
        level_name: str,
    ) -> None:
        hint: Hint = {}
        args = cls._get_args(event_dict, hint)

        sentry_sdk.Hub.current.add_breadcrumb(
            crumb={
                "ty": "log",
                _LEVEL_KEY: level_name,
                "category": event_dict.get(_LOGGER_KEY),
                "message": event_dict.get("event", "").format(*args),
                "timestamp": parser.parse(event_dict.get("timestamp", "")),
                "data": {},
            },
            hint=hint,
        )

    @classmethod
    def log_event(cls, event_dict: structlog.types.EventDict, level_name: str) -> None:
        hub = sentry_sdk.Hub.current

        if hub.client is None:
            return

        event, hint = cls._get_base_event_and_hint(hub.client.options, event_dict)
        event[_LEVEL_KEY] = level_name
        event[_LOGGER_KEY] = event_dict.get(_LOGGER_KEY)
        event["logentry"] = {
            "message": event_dict.get("event"),
            "params": cls._get_args(event_dict, hint),
        }
        event["extra"] = {
            event_key: event_value
            for event_key, event_value in event_dict.items()
            if event_key not in cls._ignored_keys
            and (not isinstance(event_key, str) or not event_key.startswith("_"))
        }
        event["tags"] = {
            key: event_dict[key] for key in cls._tag_keys if key in event_dict
        }
        hub.capture_event(event, hint=hint)

    @classmethod
    def _get_args(cls, event_dict: structlog.types.EventDict, hint: Hint) -> list[Any]:
        record: Optional[logging.LogRecord] = event_dict.get("_record")
        args = event_dict.get("positional_args", ())

        if record:
            args = record.args
            hint["log_record"] = record

        return args

    @classmethod
    def _get_base_event_and_hint(
        cls,
        client_options: Mapping[str, Any],
        event_dict: structlog.types.EventDict,
    ) -> Tuple[Event, Hint]:
        event: Event = {}
        hint: Hint = {}
        exc_info = event_dict.get("exc_info")

        if exc_info is True:
            exc_info = sys.exc_info()

        if exc_info is not None and exc_info[0] is not None:
            event, hint = sentry_utils.event_from_exception(
                exc_info,
                client_options=dict(client_options),
                mechanism={"type": "logging", "handled": True},
            )
        elif exc_info and exc_info[0] is None:
            event["threads"] = {
                "values": [
                    {
                        "stacktrace": sentry_utils.current_stacktrace(
                            client_options["with_locals"],
                        ),
                        "crashed": False,
                        "current": True,
                    },
                ],
            }

        return event, hint


def before_send(
    event: Mapping[str, Any],
    hint: Mapping[str, Any],
) -> Optional[dict[str, Any]]:
    exc_info = hint.get("exc_info")

    if not exc_info or not exc_info[0]:
        return dict(event)

    exception_type = _get_exception_type(exc_info[0])
    type_name = sentry_utils.get_type_name(exception_type)
    full_name = "{module}.{name}".format(
        module=sentry_utils.get_type_module(exception_type),
        name=type_name,
    )

    if full_name in _IGNORED_ERROR_CLASSES or type_name in _IGNORED_ERROR_CLASSES:
        return None

    return dict(event)


def _get_exception_type(
    exception: Union[Type[Exception], Exception],
) -> Type[Exception]:
    if isinstance(exception, Exception):
        return type(exception)

    return exception


def configure_sentry(
    additional_integrations: Optional[Integrations] = None,
    tag_keys: Optional[Sequence[str]] = None,
    **kwargs: Any,
) -> None:
    integrations: Integrations = []

    if additional_integrations:
        integrations = [*integrations, *additional_integrations]

    for integration_type in sentry_sdk.integrations.iter_default_integrations(False):
        if integration_type == sentry_logging.LoggingIntegration:
            continue

        with contextlib.suppress(sentry_sdk.integrations.DidNotEnable):
            integrations = [*integrations, integration_type()]

    if util.find_spec("httpx"):
        httpx_module = import_module("sentry_sdk.integrations.httpx")
        integrations = [*integrations, httpx_module.HttpxIntegration()]

    sentry_sdk.init(
        default_integrations=False,
        integrations=integrations,
        traces_sample_rate=kwargs.get("trace_sample_rate", _DEFAULT_TRACE_SAMPLE_RATE),
        before_send=before_send,
        in_app_include=["snowfall"],
        **kwargs,
    )

    if not tag_keys:
        tag_keys = []

    SentryLogger.add_tag_keys(tag_keys)
