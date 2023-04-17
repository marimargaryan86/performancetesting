from __future__ import annotations

import asyncio
import dataclasses
import inspect
from typing import (  # noqa: WPS235
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

import click
import orjson
import pydantic
import structlog
from prometheus_async.aio import web

from snowfall.stdlib.integration.click import parameters
from snowfall.stdlib.logging import sentry, stdout


class Settings(pydantic.BaseModel):
    class Config(object):
        allow_mutation = False


_Settings = TypeVar("_Settings", bound=Settings)
_Settings0 = TypeVar("_Settings0", bound=Settings)
_Settings1 = TypeVar("_Settings1", bound=Settings)
_Settings2 = TypeVar("_Settings2", bound=Settings)
_Settings3 = TypeVar("_Settings3", bound=Settings)
_Settings4 = TypeVar("_Settings4", bound=Settings)
_Settings5 = TypeVar("_Settings5", bound=Settings)


def _print_debug_info(
    ctx: click.Context,
    param_def: click.Parameter,
    param_value: Any,
) -> Any:
    if param_value is True:
        click.echo(orjson.dumps(ctx.to_info_dict()).decode())
        ctx.exit()


@dataclasses.dataclass(frozen=True)
class SentrySettings(object):
    additional_integrations: Optional[sentry.Integrations] = None
    tag_keys: Optional[list[str]] = None


class _GlobalSettings(Settings):
    debug_info: bool = pydantic.Field(default=False, callback=_print_debug_info)
    env_name: str = pydantic.Field(default="local", hidden=True)
    log_level: str = "INFO"
    prometheus_port: int | None = None
    sentry_dsn: str = ""
    version: str = pydantic.Field(default="dev", hidden=True)


@dataclasses.dataclass(frozen=True)
class Application(Generic[_Settings]):
    environment: str
    name: str
    settings: _Settings
    user_agent: str
    version: str


Callback = Union[
    Callable[[Application[_Settings]], None],
    Callable[[Application[_Settings]], Awaitable[None]],
]


@dataclasses.dataclass(frozen=True)
class Command(Generic[_Settings]):
    name: str
    callback: Callback[_Settings]
    settings_class: Type[_Settings]


@dataclasses.dataclass(frozen=True)
class Entrypoint(object):
    name: str
    _group: click.Group = dataclasses.field(init=False)
    sentry_settings: SentrySettings = SentrySettings()

    def __post_init__(self) -> None:
        object.__setattr__(  # noqa: WPS609
            self,
            "_group",
            click.Group(name=self.name, callback=_group),
        )
        _add_parameters_from_settings(self._group, _GlobalSettings)

    def add_command(self, cmd: Command[_Settings]) -> None:
        command = click.Command(name=cmd.name, callback=_command(cmd))
        _add_parameters_from_settings(command, cmd.settings_class)
        self._group.add_command(command)

    def enter(self) -> None:
        self._group(
            obj={
                "entrypoint": self,
            },
        )

    def enter_with_commands(  # noqa: WPS211
        self,
        _cmd0: Command[_Settings0],
        _cmd1: Command[_Settings1] | None = None,
        _cmd2: Command[_Settings2] | None = None,
        _cmd3: Command[_Settings3] | None = None,
        _cmd4: Command[_Settings4] | None = None,
        _cmd5: Command[_Settings5] | None = None,
    ) -> None:
        def wrapper(cmd: Command[_Settings] | None) -> None:
            if not cmd:
                return

            self.add_command(cmd)

        wrapper(_cmd0)
        wrapper(_cmd1)
        wrapper(_cmd2)
        wrapper(_cmd3)
        wrapper(_cmd4)
        wrapper(_cmd5)

        self.enter()


def _add_parameters_from_settings(
    command: click.Command,
    settings: type[Settings],
) -> None:
    for arg in parameters.create_from_pydantic_model(settings):
        command.params.append(arg)


@click.pass_context
def _group(ctx: click.Context, **kwargs: Any) -> None:
    ctx.ensure_object(dict)
    ctx.obj["global_settings"] = _GlobalSettings.construct(**kwargs)


def _configure(
    entrypoint: Entrypoint,
    global_settings: _GlobalSettings,
) -> None:
    stdout.configure_logger(level=global_settings.log_level)
    logger = structlog.get_logger(__name__)

    logger.info(
        "Application bootstrapped.",
        name=entrypoint.name,
        version=global_settings.version,
        environment=global_settings.env_name,
    )

    if global_settings.sentry_dsn:
        sentry.configure_sentry(
            dsn=global_settings.sentry_dsn,
            environment=global_settings.env_name,
            release="{name}@{version}".format(
                name=entrypoint.name,
                version=global_settings.version,
            ),
            additional_integrations=entrypoint.sentry_settings.additional_integrations,
            tag_keys=entrypoint.sentry_settings.tag_keys,
        )
        logger.info(
            "Sentry configured.",
            dsn=global_settings.sentry_dsn,
        )


def _command(
    command: Command[_Settings],
) -> Callable[[click.Context], None]:
    @click.pass_context
    def decorator(ctx: click.Context, **kwargs: Any) -> None:
        ctx.ensure_object(dict)

        entrypoint: Entrypoint = ctx.obj["entrypoint"]
        global_settings: _GlobalSettings = ctx.obj["global_settings"]
        application = Application(
            environment=global_settings.env_name,
            name=entrypoint.name,
            settings=command.settings_class.construct(**kwargs),
            user_agent="{name}/{version} (+https://snowfalltravel.com/)".format(
                name=entrypoint.name,
                version=global_settings.version,
            ),
            version=global_settings.version,
        )

        _configure(entrypoint, global_settings)

        if not inspect.iscoroutinefunction(command.callback):
            if global_settings.prometheus_port:
                web.start_http_server_in_thread(port=global_settings.prometheus_port)
            command.callback(application)
            return

        async def wrapper() -> None:
            tasks: list[Awaitable[None | web.MetricsHTTPServer]] = [
                cast(
                    Callable[[Application[_Settings]], Awaitable[None]],
                    command.callback,
                )(application),
            ]

            if global_settings.prometheus_port:
                tasks.append(
                    web.start_http_server(port=global_settings.prometheus_port),
                )

            await asyncio.gather(*tasks)

        asyncio.run(wrapper())

    return decorator
