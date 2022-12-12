from __future__ import annotations

import asyncio
import dataclasses
import inspect
from collections.abc import Sequence
from typing import (  # noqa: WPS235
    Any,
    Awaitable,
    Callable,
    Generic,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

import click
import pydantic
import structlog
from prometheus_async.aio import web
from pydantic.error_wrappers import ErrorWrapper

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


@dataclasses.dataclass(frozen=True)
class SentrySettings(object):
    additional_integrations: Optional[sentry.Integrations] = None
    tag_keys: Optional[list[str]] = None


class _GlobalSettings(Settings):
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
    sentry_settings: SentrySettings = SentrySettings()

    def enter_with_commands(  # noqa: WPS213, WPS211
        self,
        _cmd0: Command[_Settings0],
        _cmd1: Optional[Command[_Settings1]] = None,
        _cmd2: Optional[Command[_Settings2]] = None,
        _cmd3: Optional[Command[_Settings3]] = None,
        _cmd4: Optional[Command[_Settings4]] = None,
    ) -> None:
        group = click.Group(name=self.name, callback=_group)

        _add_parameters_from_settings(group, _GlobalSettings)

        command = click.Command(name=_cmd0.name, callback=_command(_cmd0))
        _add_parameters_from_settings(command, _cmd0.settings_class)
        group.add_command(command)  # noqa: WPS204

        if _cmd1:
            command = click.Command(name=_cmd1.name, callback=_command(_cmd1))
            _add_parameters_from_settings(command, _cmd1.settings_class)
            group.add_command(command)

        if _cmd2:
            command = click.Command(name=_cmd2.name, callback=_command(_cmd2))
            _add_parameters_from_settings(command, _cmd2.settings_class)
            group.add_command(command)

        if _cmd3:
            command = click.Command(name=_cmd3.name, callback=_command(_cmd3))
            _add_parameters_from_settings(command, _cmd3.settings_class)
            group.add_command(command)

        if _cmd4:
            command = click.Command(name=_cmd4.name, callback=_command(_cmd4))
            _add_parameters_from_settings(command, _cmd4.settings_class)
            group.add_command(command)

        group(
            obj={
                "entrypoint": self,
            },
        )


def _get_type(type_: type) -> type:
    if type_ == bool:
        return type_

    if type_ == int:
        return int

    if type_ == float:
        return float

    return str


def _validate_option(
    field: pydantic.fields.ModelField,
) -> Callable[[click.Context, click.Parameter, Any], Any]:
    def decorator(
        ctx: click.Context,
        param_def: click.Parameter,
        param_value: Any,
    ) -> Any:
        response = field.validate(param_value, {}, loc="")

        if response[1]:
            if isinstance(response[1], list):
                raise click.BadParameter(
                    message=str(cast(ErrorWrapper, response[1][0][0]).exc),
                    ctx=ctx,
                    param=param_def,
                )

            raise click.BadParameter(
                message=str(cast(ErrorWrapper, response[1]).exc),
                ctx=ctx,
                param=param_def,
            )

        return response[0]

    return decorator


def _create_parameter_from_model(
    arg: pydantic.fields.ModelField,
    types: Mapping[str, type],
) -> click.Parameter:
    arg_type = get_origin(types[arg.name]) or types[arg.name]

    if arg.field_info.extra.get("argument", False):
        return click.Argument(
            [arg.name],
            callback=_validate_option(arg),
            default=(
                None if arg.default == pydantic.fields.UndefinedType else arg.default
            ),
            envvar=arg.name.upper(),
            nargs=-1 if arg_type in {Sequence, list, set, tuple} else 1,
            required=bool(arg.required),
            type=_get_type(next(iter(get_args(types[arg.name])), arg_type)),
        )

    return click.Option(
        ["--{0}".format(arg.name.replace("_", "-"))],
        callback=_validate_option(arg),
        default=(None if arg.default == pydantic.fields.UndefinedType else arg.default),
        envvar=arg.name.upper(),
        help=arg.field_info.description,
        hidden=bool(arg.field_info.extra.get("hidden", False)),
        is_flag=arg_type == bool,
        multiple=arg_type in {Sequence, list, set, tuple},
        required=arg.required,
        show_default=True,
        show_envvar=True,
        type=_get_type(next(iter(get_args(types[arg.name])), arg_type)),
    )


def _add_parameters_from_settings(
    command: click.Command,
    settings: Type[Settings],
) -> None:
    args: list[pydantic.fields.ModelField] = list(settings.__fields__.values())
    types = get_type_hints(settings)

    for arg in args:
        command.params.append(_create_parameter_from_model(arg, types))


@click.pass_context
def _group(ctx: click.Context, **kwargs: Any) -> None:
    ctx.ensure_object(dict)

    ctx.obj["global_settings"] = _GlobalSettings.construct(
        **{kwarg_key: kwarg_value for kwarg_key, kwarg_value in kwargs.items()},
    )


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


def _command(  # noqa: WPS210
    command: Command[_Settings],
) -> Callable[[click.Context], None]:
    @click.pass_context
    def decorator(ctx: click.Context, **kwargs: Any) -> None:  # noqa: WPS210
        ctx.ensure_object(dict)

        entrypoint: Entrypoint = ctx.obj["entrypoint"]
        global_settings: _GlobalSettings = ctx.obj["global_settings"]
        application = Application(
            environment=global_settings.env_name,
            name=entrypoint.name,
            settings=command.settings_class.construct(
                **{kwarg_key: kwarg_value for kwarg_key, kwarg_value in kwargs.items()},
            ),
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
