from __future__ import annotations

import pathlib
from collections import abc
from typing import (  # noqa: WPS235
    Any,
    Callable,
    Mapping,
    NewType,
    Sequence,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

import click
import orjson
import pydantic

from snowfall.stdlib import sequence, types

JSON = NewType("JSON", str)


def create_from_pydantic_model(
    model: type[pydantic.BaseModel],
) -> list[click.Parameter]:
    fields: list[pydantic.fields.ModelField] = list(model.__fields__.values())
    field_types = get_type_hints(model)

    return [_create_from_pydantic_field(field, field_types) for field in fields]


def _create_from_pydantic_field(
    arg: pydantic.fields.ModelField,
    arg_types: Mapping[str, type],
) -> click.Parameter:
    arg_type = get_origin(arg_types[arg.name]) or arg_types[arg.name]
    is_multi = arg_type in {abc.Sequence, Sequence, list, set, tuple}

    if arg.field_info.extra.get("argument", False):
        return click.Argument(
            [arg.name.replace("_", "-")],
            callback=_validate_option(arg),
            default=_get_parameter_default(arg),
            envvar=arg.name.upper(),
            nargs=-1 if is_multi else 1,
            required=bool(arg.required),
            type=_get_type(arg_types, arg.name, arg_type),
        )

    return click.Option(
        ["--{0}".format(arg.name.replace("_", "-"))],
        callback=_validate_option(arg),
        default=_get_parameter_default(arg),
        envvar=arg.name.upper(),
        help=arg.field_info.description,
        hidden=bool(arg.field_info.extra.get("hidden", False)),
        is_flag=arg_type == bool,
        multiple=is_multi,
        required=arg.required,
        show_default=True,
        show_envvar=True,
        type=_get_type(arg_types, arg.name, arg_type),
    )


def _get_type(arg_types: Mapping[str, type], name: str, type_: type) -> type:
    if type_ == dict:
        return JSON

    type_ = next(iter(get_args(arg_types[name])), type_)

    if type_ == bool:
        return type_

    if type_ == int:
        return int

    if type_ == float:
        return float

    return str


def _parse_json(
    ctx: click.Context,
    param_def: click.Parameter,
    param_value: str,
) -> dict[types.Primitive, types.Primitive]:
    try:
        return orjson.loads(param_value)
    except orjson.JSONDecodeError as err:
        raise click.BadParameter(
            message=err.msg,
            ctx=ctx,
            param=param_def,
        ) from err


def _parse_pydantic_result(
    ctx: click.Context,
    param_def: click.Parameter,
    response: tuple[Any | None, Sequence[Any] | Any | None],
) -> Any:
    if response[1]:
        if isinstance(response[1], list):
            raise click.BadParameter(
                message=str(
                    cast(pydantic.error_wrappers.ErrorWrapper, response[1][0][0]).exc,
                ),
                ctx=ctx,
                param=param_def,
            )

        raise click.BadParameter(
            message=str(cast(pydantic.error_wrappers.ErrorWrapper, response[1]).exc),
            ctx=ctx,
            param=param_def,
        )

    if isinstance(response[0], pathlib.Path):
        return response[0].expanduser()

    return response[0]


def _validate_option(
    field: pydantic.fields.ModelField,
) -> Callable[[click.Context, click.Parameter, Any], Any]:
    def decorator(
        ctx: click.Context,
        param_def: click.Parameter,
        param_value: Any,
    ) -> Any:
        if param_def.type.name == "JSON":
            param_value = _parse_json(ctx, param_def, param_value)

        response = field.validate(param_value, {}, loc="")

        return _parse_pydantic_result(ctx, param_def, response)

    return decorator


_iterables = (list, set, tuple)


def _get_parameter_default(
    arg: pydantic.fields.ModelField,
) -> types.Primitive | list[types.Primitive] | None:
    if arg.default == pydantic.fields.UndefinedType or arg.default is None:
        return None

    if isinstance(arg.default, dict):
        return orjson.dumps(arg.default).decode()

    if isinstance(arg.default, _iterables) or sequence.is_a(arg.default):
        return [
            default if isinstance(default, (bool, float, int, str)) else str(default)
            for default in arg.default
        ]

    if isinstance(arg.default, (bool, float, int, str)):
        return arg.default

    return str(arg.default)
