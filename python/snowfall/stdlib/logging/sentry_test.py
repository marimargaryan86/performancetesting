from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from sentry_sdk import Transport, envelope

from snowfall.stdlib.logging import sentry, stdout

SentryEvents = list[dict[str, Any]]
Breadcrumbs = list[dict[str, Any]]


@pytest.fixture(name="breadcrumbs")
def fixture_breadcrumbs() -> SentryEvents:
    breadcrumbs: SentryEvents = []
    sentry.configure_sentry(
        environment="test",
        release="test",
        before_breadcrumb=lambda crumb, hint: breadcrumbs.append(crumb),
    )

    return breadcrumbs


class _MockTransport(Transport):
    def __init__(
        self,
        func: Callable[[Any], None],
    ) -> None:
        super().__init__()
        self._func = func

    def capture_envelope(self, event: envelope.Envelope) -> None:
        self._func(event)


@pytest.fixture(name="sentry_events")
def fixture_sentry_events() -> SentryEvents:
    caught_events: SentryEvents = []
    sentry.configure_sentry(
        environment="test",
        release="test",
        transport=_MockTransport(caught_events.append),
    )

    return caught_events


def test_breadcrumb_is_added(breadcrumbs: Breadcrumbs) -> None:
    stdout.configure_logger()
    logger = stdout.get_logger()
    logger.info("test")
    assert len(breadcrumbs) == 1
    breadcrumb = breadcrumbs[-1]
    assert breadcrumb["level"] == "info"


def test_event_is_logged(sentry_events: SentryEvents) -> None:
    stdout.configure_logger()
    logger = stdout.get_logger()
    logger.error("test")
    assert len(sentry_events) == 1
