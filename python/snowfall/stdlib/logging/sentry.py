from collections.abc import Sequence
from importlib import import_module, util
from typing import Any

import sentry_sdk
import structlog
from sentry_sdk.integrations import logging as sentry_logging

Integrations = Sequence[sentry_sdk.integrations.Integration]
_DEFAULT_PROFILES_SAMPLE_RATE = 1
_DEFAULT_TRACES_SAMPLE_RATE = 0.1


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


def configure_sentry(
    additional_integrations: Integrations | None = None,
    tag_keys: Sequence[str] | None = None,
    **kwargs: Any,
) -> None:
    integrations: Integrations = [
        sentry_logging.LoggingIntegration(event_level=None, level=None),
    ]

    if additional_integrations:
        integrations = [*integrations, *additional_integrations]

    sentry_sdk.init(
        default_integrations=True,
        auto_enabling_integrations=True,
        integrations=_with_additional_integrations(integrations),
        traces_sample_rate=kwargs.get(
            "traces_sample_rate",
            _DEFAULT_TRACES_SAMPLE_RATE,
        ),
        profiles_sample_rate=kwargs.get(
            "profiles_sample_rate",
            _DEFAULT_PROFILES_SAMPLE_RATE,
        ),
        in_app_include=["snowfall"],
        **kwargs,
    )


def _with_additional_integrations(integrations: Integrations) -> Integrations:
    if util.find_spec("pymongo"):
        pymongo_module = import_module("sentry_sdk.integrations.pymongo")
        integrations = [*integrations, pymongo_module.PyMongoIntegration()]

    return integrations
