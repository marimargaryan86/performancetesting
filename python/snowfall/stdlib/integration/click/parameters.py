from __future__ import annotations

import pathlib
from collections.abc import Callable, Mapping, Sequence
from typing import Any, cast, get_args, get_origin, get_type_hints

import click
import orjson
import pydantic

from snowfall.stdlib import sequence, types

_Callback = Callable[[click.Context, click.Parameter, Any], Any]


class JSONParameterType(click.ParamType):
    name = "json"

    def convert(
        self,
        input_value: Any,
        expected_param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> Any:
        input_value = input_value.strip()

        try:
            return orjson.loads(input_value)
        except orjson.JSONDecodeError:
            self.fail(
                "{value!r} is not valid JSON.".format(value=input_value),
                expected_param,
                ctx,
            )

    def __repr__(self) -> str:
        return "JSON"


def create_from_pydantic_model(
    model: type[pydantic.BaseModel],
) -> list[click.Parameter]:
    fields: list[pydantic.fields.ModelField] = list(model.__fields__.values())
    field_types = get_type_hints(model)

    return [_create_from_pydantic_field(field, field_types) for field in fields]


def _custom_callback(
    field: pydantic.fields.ModelField,
    callback: _Callback,
) -> _Callback:
    validator = _validate_option(field)

    def decorator(
        ctx: click.Context,
        param_def: click.Parameter,
        param_value: Any,
    ) -> Any:
        param_value = validator(ctx, param_def, param_value)

        return callback(ctx, param_def, param_value)

    return decorator


def _create_from_pydantic_field(
    arg: pydantic.fields.ModelField,
    arg_types: Mapping[str, type],
) -> click.Parameter:
    arg_type = get_origin(arg_types[arg.name]) or arg_types[arg.name]
    is_multi = arg_type in {Sequence, list, set, tuple}
    callback = arg.field_info.extra.get("callback")

    if arg.field_info.extra.get("argument", False):
        return click.Argument(
            [arg.name.replace("_", "-")],
            callback=callback if callback else _validate_option(arg),
            default=_get_parameter_default(arg),
            envvar=arg.name.upper(),
            nargs=-1 if is_multi else 1,
            required=bool(arg.required),
            type=_get_type(arg_types, arg.name, arg_type),
        )

    return click.Option(
        ["--{0}".format(arg.name.replace("_", "-"))],
        callback=callback if callback else _validate_option(arg),
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


def _get_type(
    arg_types: Mapping[str, type],
    name: str,
    type_: type,
) -> type | click.ParamType:
    if type_ == dict:
        return JSONParameterType()

    type_ = next(iter(get_args(arg_types[name])), type_)

    if type_ == bool:
        return type_

    if type_ == int:
        return int

    if type_ == float:
        return float

    return str


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
) -> _Callback:
    def decorator(
        ctx: click.Context,
        param_def: click.Parameter,
        param_value: Any,
    ) -> Any:
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
            (
                default
                if isinstance(default, bool | float | int | str)  # noqa: WPS221
                else str(default)
            )
            for default in arg.default
        ]

    if isinstance(arg.default, bool | float | int | str):
        return arg.default

    return str(arg.default)
