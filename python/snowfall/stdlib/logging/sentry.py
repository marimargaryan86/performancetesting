from importlib import import_module, util
from typing import Any, Optional, Sequence

import sentry_sdk
import structlog
from sentry_sdk.integrations import logging as sentry_logging

Integrations = Sequence[sentry_sdk.integrations.Integration]
_DEFAULT_TRACE_SAMPLE_RATE = 0.05


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
    additional_integrations: Optional[Integrations] = None,
    tag_keys: Optional[Sequence[str]] = None,
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
        traces_sample_rate=kwargs.get("trace_sample_rate", _DEFAULT_TRACE_SAMPLE_RATE),
        in_app_include=["snowfall"],
        **kwargs,
    )


def _with_additional_integrations(integrations: Integrations) -> Integrations:
    if util.find_spec("httpx"):
        httpx_module = import_module("sentry_sdk.integrations.httpx")
        integrations = [*integrations, httpx_module.HttpxIntegration()]

    return integrations
