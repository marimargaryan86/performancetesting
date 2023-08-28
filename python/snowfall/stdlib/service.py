from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import inspect
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Annotated, Any, Generic, Protocol, TypeVar, cast

import click
import orjson
import pydantic
import pydantic_core
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


AnyDsn = Annotated[pydantic_core.Url, pydantic.UrlConstraints(host_required=False)]


@dataclasses.dataclass(frozen=True)
class SentrySettings(object):
    additional_integrations: sentry.Integrations | None = None
    tag_keys: list[str] | None = None


class _GlobalSettings(Settings):
    debug_info: bool = pydantic.Field(
        default=False,
        json_schema_extra={"callback": _print_debug_info},
    )
    env_name: str = pydantic.Field(default="local", json_schema_extra={"hidden": True})
    json_output: bool = True
    log_level: str = "INFO"
    prometheus_port: int | None = None
    sentry_dsn: str = ""
    version: str = pydantic.Field(default="dev", json_schema_extra={"hidden": True})


@dataclasses.dataclass(frozen=True)
class Application(Generic[_Settings]):
    environment: str
    name: str
    settings: _Settings
    user_agent: str
    version: str


@dataclasses.dataclass(frozen=True)
class AsyncApplication(Application[_Settings]):
    stack: contextlib.AsyncExitStack

    @classmethod
    @contextlib.asynccontextmanager
    async def from_application(
        cls,
        app: Application[_Settings],
    ) -> AsyncIterator[AsyncApplication[_Settings]]:
        async with contextlib.AsyncExitStack() as stack:
            yield AsyncApplication(
                stack=stack,
                environment=app.environment,
                name=app.name,
                settings=app.settings,
                user_agent=app.user_agent,
                version=app.version,
            )


SyncCallback = Callable[[Application[_Settings]], None]
AsyncCallback = Callable[[AsyncApplication[_Settings]], Awaitable[None]]
Callback = SyncCallback[_Settings] | AsyncCallback[_Settings]


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
    command.params = [
        *command.params,
        *parameters.create_from_pydantic_model(settings),
    ]


@click.pass_context
def _group(ctx: click.Context, /, **kwargs: Any) -> None:
    ctx.ensure_object(dict)
    ctx.obj["global_settings"] = _GlobalSettings.construct(**kwargs)


def _configure(
    entrypoint: Entrypoint,
    global_settings: _GlobalSettings,
) -> stdout.Logger:
    stdout.configure_logger(
        level=global_settings.log_level,
        format_as_json=global_settings.json_output and not entrypoint.cli_tool,
    )
    logger = stdout.get_logger()

    if not entrypoint.cli_tool:
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

        if not entrypoint.cli_tool:
            logger.info(
                "Sentry configured.",
                dsn=global_settings.sentry_dsn,
            )

    return logger


async def _async_wrapper(
    entrypoint: Entrypoint,
    global_settings: _GlobalSettings,
    application: Application[_Settings],
    callback: AsyncCallback[_Settings],
) -> None:
    logger = _configure(entrypoint, global_settings)

    async with AsyncApplication.from_application(application) as async_app:
        tasks: list[Awaitable[None | web.MetricsHTTPServer]] = [
            callback(async_app),
        ]

        if global_settings.prometheus_port:
            tasks.append(
                web.start_http_server(port=global_settings.prometheus_port),
            )

        try:
            await asyncio.gather(*tasks)
        except Exception as err:
            logger.exception()
            raise SystemExit(1) from err


def _sync_wrapper(
    entrypoint: Entrypoint,
    global_settings: _GlobalSettings,
    application: Application[_Settings],
    callback: SyncCallback[_Settings],
) -> None:
    logger = _configure(entrypoint, global_settings)

    if global_settings.prometheus_port:
        web.start_http_server_in_thread(port=global_settings.prometheus_port)

    try:
        callback(application)
    except Exception as err:
        logger.exception()
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
            name=entrypoint.name,
            settings=command.settings_class.construct(**kwargs),
            user_agent="{name}/{version} (+https://snowfalltravel.com/)".format(
                name=entrypoint.name,
                version=global_settings.version,
            ),
            version=global_settings.version,
        )

        if inspect.iscoroutinefunction(command.callback):
            asyncio.run(
                _async_wrapper(
                    entrypoint,
                    global_settings,
                    application,
                    command.callback,
                ),
            )
        else:
            _sync_wrapper(
                entrypoint,
                global_settings,
                application,
                cast(SyncCallback[_Settings], command.callback),
            )

    # need to cast because of dodgy type hinting in @click.pass_context
    return cast(_Command, decorator)
