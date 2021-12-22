from typing import Any

import pytest
import structlog

from snowfall.logging import sentry, stdout

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


@pytest.fixture(name="sentry_events")
def fixture_sentry_events() -> SentryEvents:
    caught_events: SentryEvents = []
    sentry.configure_sentry(
        environment="test",
        release="test",
        transport=caught_events.append,
    )

    return caught_events


@pytest.mark.asyncio
async def test_breadcrumb_is_added(breadcrumbs: Breadcrumbs) -> None:
    stdout.configure_logger()
    logger = structlog.get_logger("testing")
    logger.info("test")
    assert len(breadcrumbs) == 1
    breadcrumb = breadcrumbs[-1]
    assert breadcrumb["category"] == "testing"
    assert breadcrumb["level"] == "info"


@pytest.mark.asyncio
async def test_event_is_logged(sentry_events: SentryEvents) -> None:
    stdout.configure_logger()
    logger = structlog.get_logger("testing")
    logger.error("test")
    assert len(sentry_events) == 1
