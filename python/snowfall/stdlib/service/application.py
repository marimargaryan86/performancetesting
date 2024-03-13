from __future__ import annotations

import asyncio
import contextlib
import dataclasses
from collections.abc import Awaitable, Callable
from typing import Annotated, Any, ClassVar, Generic, Protocol, TypeVar, cast

import click
import orjson
import pydantic
from prometheus_async.aio import web

from snowfall.stdlib.integration.click import parameters
from snowfall.stdlib.logging import sentry, stdout


class Settings(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="forbid",
        frozen=True,
    )


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


_MIN_PORT = 1
_MAX_PORT = 65535

AnyDsn = Annotated[str, pydantic.StringConstraints(pattern="^(memory|s3)://")]
NetworkPort = Annotated[int, pydantic.conint(ge=_MIN_PORT, le=_MAX_PORT)]


@dataclasses.dataclass(frozen=True)
class SentrySettings(object):
    additional_integrations: sentry.Integrations | None = None
    tag_keys: list[str] | None = None


class _GlobalSettings(Settings):
    debug_info: bool = pydantic.Field(
        default=False,
    )
    env_name: str = pydantic.Field(default="local", json_schema_extra={"hidden": True})
    json_output: bool = True
    log_level: str = "INFO"
    prometheus_port: int | None = None
    sentry_dsn: str = ""
    sentry_release: str | None = pydantic.Field(
        default=None,
        json_schema_extra={"hidden": True},
    )
    version: str = pydantic.Field(default="dev", json_schema_extra={"hidden": True})
    callbacks: ClassVar[parameters.Callbacks] = {
        "debug_info": _print_debug_info,
    }


@dataclasses.dataclass(frozen=True)
class Application(Generic[_Settings]):
    environment: str
    logger: stdout.Logger
    name: str
    settings: _Settings
    stack: contextlib.AsyncExitStack
    user_agent: str
    version: str


Callback = Callable[[Application[_Settings]], Awaitable[None]]


@dataclasses.dataclass(frozen=True)
class Command(Generic[_Settings]):
    name: str
    callback: Callback[_Settings]
    settings_class: type[_Settings]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Entrypoint(object):
    name: str
    _group: click.Group = dataclasses.field(init=False)
    cli_tool: bool = False
    sentry_settings: SentrySettings = dataclasses.field(
        default_factory=SentrySettings,
    )

    def __post_init__(self) -> None:
        super().__setattr__(  # noqa: WPS613
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

    def enter_with_commands(
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
    command.params = [
        *command.params,
        *parameters.create_from_pydantic_model(settings),
    ]


@click.pass_context
def _group(ctx: click.Context, /, **kwargs: Any) -> None:
    ctx.ensure_object(dict)
    ctx.obj["global_settings"] = _GlobalSettings.construct(**kwargs)


def _create_logger(
    entrypoint: Entrypoint,
    global_settings: _GlobalSettings,
) -> stdout.Logger:
    format_for_consoles = entrypoint.cli_tool or global_settings.env_name == "local"
    stdout.configure_logger(
        level=global_settings.log_level,
        format_as_json=global_settings.json_output and not format_for_consoles,
    )
    logger = stdout.get_logger()

    if not entrypoint.cli_tool:
        logger.info(
            "Application bootstrapped.",
            name=entrypoint.name,
            version=global_settings.version,
            environment=global_settings.env_name,
        )

    return logger


def _configure_sentry(
    application: Application[_Settings],
    entrypoint: Entrypoint,
    global_settings: _GlobalSettings,
) -> None:
    sentry.configure_sentry(
        dsn=global_settings.sentry_dsn,
        environment=global_settings.env_name,
        release=global_settings.sentry_release
        if global_settings.sentry_release
        else "{name}@{version}".format(
            name=entrypoint.name,
            version=global_settings.version,
        ),
        additional_integrations=entrypoint.sentry_settings.additional_integrations,
        tag_keys=entrypoint.sentry_settings.tag_keys,
    )

    if not entrypoint.cli_tool:
        application.logger.info(
            "Sentry configured.",
            dsn=global_settings.sentry_dsn,
        )


async def _async_wrapper(
    application: Application[_Settings],
    entrypoint: Entrypoint,
    global_settings: _GlobalSettings,
    command: Command[_Settings],
) -> None:
    if global_settings.sentry_dsn:
        _configure_sentry(application, entrypoint, global_settings)

    async with application.stack:
        tasks: list[Awaitable[None | web.MetricsHTTPServer]] = [
            command.callback(application),
        ]

        if global_settings.prometheus_port:
            tasks.append(
                web.start_http_server(port=global_settings.prometheus_port),
            )

        try:
            await asyncio.gather(*tasks)
        except Exception as err:
            application.logger.exception()
            raise SystemExit(1) from err


class _Command(Protocol):
    def __call__(self, ctx: click.Context, **kwargs: Any) -> None:
        """Service command protocol."""


def _command(
    command: Command[_Settings],
) -> _Command:
    @click.pass_context
    def decorator(ctx: click.Context, /, **kwargs: Any) -> None:
        ctx.ensure_object(dict)

        entrypoint: Entrypoint = ctx.obj["entrypoint"]
        global_settings: _GlobalSettings = ctx.obj["global_settings"]
        application = Application(
            environment=global_settings.env_name,
            logger=_create_logger(entrypoint, global_settings),
            name=entrypoint.name,
            settings=command.settings_class.construct(**kwargs),
            stack=contextlib.AsyncExitStack(),
            user_agent="{name}/{version} (+https://snowfalltravel.com/)".format(
                name=entrypoint.name,
                version=global_settings.version,
            ),
            version=global_settings.version,
        )

        asyncio.run(
            main=_async_wrapper(application, entrypoint, global_settings, command),
            debug=global_settings.env_name in {"local", "development"},
        )

    # need to cast because of dodgy type hinting in @click.pass_context
    return cast(_Command, decorator)
