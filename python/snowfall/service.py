from __future__ import annotations

import argparse
import asyncio
import dataclasses
from contextlib import contextmanager
from typing import Awaitable, Callable, Iterator, List, Optional, Sequence

import pydantic
from sentry_sdk import integrations

from snowfall.logging import sentry, stdout


class _SharedSettings(pydantic.BaseSettings):
    env_name: str = "local"
    log_level: str = "INFO"
    sentry_dsn: str = ""
    platform_name: str = "Junction"
    version: str = "dev"


@dataclasses.dataclass(frozen=True)
class _SentrySettings(object):
    additional_integrations: Optional[list[integrations.Integration]] = None
    tag_keys: Optional[list[str]] = None


@dataclasses.dataclass
class Task(object):
    command: str
    method: Callable[[RunnableService], Awaitable[None]]


class Service(object):
    def __init__(
        self,
        settings: _SharedSettings,
        sentry_settings: _SentrySettings,
        name: str,
    ):
        self._settings = settings
        self._name = name
        stdout.configure_logger(level=self._settings.log_level)

        if self._settings.sentry_dsn:
            sentry.configure_sentry(
                dsn=self._settings.sentry_dsn,
                environment=self.environment,
                release="{name}@{version}".format(
                    name=self._name,
                    version=self.version,
                ),
                additional_integrations=sentry_settings.additional_integrations,
                tag_keys=sentry_settings.tag_keys,
            )

    @property
    def environment(self) -> str:
        return self._settings.env_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def user_agent(self) -> str:
        return "{name}/{version} ({platform_name})".format(
            name=self._name,
            version=self._settings.version,
            platform_name=self._settings.platform_name,
        )

    @property
    def version(self) -> str:
        return self._settings.version


class RunnableService(Service):
    def __init__(
        self,
        settings: _SharedSettings,
        sentry_settings: _SentrySettings,
        name: str,
        tasks: Sequence[Task],
    ):
        super().__init__(settings, sentry_settings, name)

        self._cleanup_tasks: List[Awaitable[None]] = []
        self._parser = argparse.ArgumentParser()
        self._tasks = {task.command: task.method for task in tasks}

        self._parser.add_argument(
            "task",
            choices=self._tasks.keys(),
            type=str,
        )

    def add_cleanup_task(self, task: Awaitable[None]) -> None:
        self._cleanup_tasks.append(task)

    def run(self) -> None:
        if not self._tasks:
            raise RuntimeError("No tasks defined")

        parsed_args = self._parser.parse_args()

        with self._run() as loop:
            loop.run_until_complete(self._tasks[parsed_args.task](self))

    @contextmanager
    def _run(self) -> Iterator[asyncio.AbstractEventLoop]:
        loop = asyncio.get_event_loop()

        try:
            yield loop
        finally:
            if self._cleanup_tasks:
                loop.run_until_complete(*self._cleanup_tasks)

            loop.close()


def make_runnable_service(
    name: str,
    tasks: Sequence[Task],
    sentry_integrations: Optional[list[integrations.Integration]] = None,
    sentry_tag_keys: Optional[list[str]] = None,
) -> RunnableService:
    return RunnableService(
        settings=_SharedSettings(),
        name=name,
        tasks=tasks,
        sentry_settings=_SentrySettings(
            additional_integrations=sentry_integrations,
            tag_keys=sentry_tag_keys,
        ),
    )


def make_service(
    name: str,
    sentry_integrations: Optional[list[integrations.Integration]] = None,
    sentry_tag_keys: Optional[list[str]] = None,
) -> Service:
    return Service(
        settings=_SharedSettings(),
        name=name,
        sentry_settings=_SentrySettings(
            additional_integrations=sentry_integrations,
            tag_keys=sentry_tag_keys,
        ),
    )
