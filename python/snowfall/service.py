from __future__ import annotations

import argparse
import asyncio
import dataclasses
from typing import Awaitable, Callable, Optional, Sequence

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
    method: Callable[[Service], Awaitable[None]]


class Service(object):
    def __init__(
        self,
        settings: _SharedSettings,
        sentry_settings: _SentrySettings,
        name: str,
        tasks: Optional[Sequence[Task]],
    ):
        self._settings = settings
        self._name = name
        self._tasks = {}
        self._parser = argparse.ArgumentParser()
        stdout.configure_logger(level=self._settings.log_level)

        if self._settings.sentry_dsn:
            sentry.configure_sentry(
                dsn=self._settings.sentry_dsn,
                environment=self.environment,
                release="{name}@{version}".format(
                    name=self.name,
                    version=self.version,
                ),
                additional_integrations=sentry_settings.additional_integrations,
                tag_keys=sentry_settings.tag_keys,
            )

        if tasks:
            self._tasks = {task.command: task.method for task in tasks}
            self._parser.add_argument(
                "task",
                choices=self._tasks.keys(),
                type=str,
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

    def run(self) -> None:
        if not self._tasks:
            raise RuntimeError("No tasks defined")

        parsed_args = self._parser.parse_args()
        asyncio.run(self._tasks[parsed_args.task](self))


def make_service(
    name: str,
    tasks: Optional[Sequence[Task]] = None,
    sentry_integrations: Optional[list[integrations.Integration]] = None,
    sentry_tag_keys: Optional[list[str]] = None,
) -> Service:
    return Service(
        settings=_SharedSettings(),
        name=name,
        tasks=tasks,
        sentry_settings=_SentrySettings(
            additional_integrations=sentry_integrations,
            tag_keys=sentry_tag_keys,
        ),
    )
