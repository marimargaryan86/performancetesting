from __future__ import annotations

import pathlib
from collections.abc import Callable, Mapping, Sequence
from typing import Any, TypeGuard, TypeVar, cast, get_args, get_origin, get_type_hints

import click
import orjson
import pydantic
import pydantic_core

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
    fields: list[tuple[str, pydantic.fields.FieldInfo]] = list(
        model.model_fields.items(),
    )
    field_types = get_type_hints(model)

    return [
        _create_from_pydantic_field(name, field, field_types) for name, field in fields
    ]


def _custom_callback(
    field: pydantic.fields.FieldInfo,
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
    name: str,
    arg: pydantic.fields.FieldInfo,
    arg_types: Mapping[str, type],
) -> click.Parameter:
    arg_type = get_origin(arg_types[name]) or arg_types[name]
    is_multi = arg_type in {Sequence, list, set, tuple}
    extra = arg.json_schema_extra if isinstance(arg.json_schema_extra, dict) else {}
    callback = extra.get("callback")

    if extra.get("argument", False):
        return click.Argument(
            [name.replace("_", "-")],
            callback=(
                _custom_callback(arg, callback) if callback else _validate_option(arg)
            ),
            default=_get_parameter_default(arg),
            envvar=name.upper(),
            nargs=-1 if is_multi else 1,
            required=arg.is_required(),
            type=_get_type(arg_types, name, arg_type),
        )

    return click.Option(
        ["--{0}".format(name.replace("_", "-"))],
        callback=_custom_callback(arg, callback) if callback else _validate_option(arg),
        default=_get_parameter_default(arg),
        envvar=name.upper(),
        help=arg.description,
        hidden=bool(extra.get("hidden", False)),
        is_flag=arg_type == bool,
        multiple=is_multi,
        required=arg.is_required(),
        show_default=True,
        show_envvar=True,
        type=_get_type(arg_types, name, arg_type),
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


_ValueType = TypeVar("_ValueType")


def _validate_option(
    field: pydantic.fields.FieldInfo,
) -> _Callback:
    validator = pydantic.TypeAdapter(field.annotation)

    def decorator(
        ctx: click.Context,
        param_def: click.Parameter,
        param_value: _ValueType,
    ) -> _ValueType | pathlib.Path:
        try:
            response = cast(_ValueType, validator.validate_python(param_value))
        except pydantic.ValidationError as err:
            raise click.BadParameter(
                message=str(err),
                ctx=ctx,
                param=param_def,
            ) from err

        if isinstance(response, pathlib.Path):
            return response.expanduser()

        return response

    return decorator


_iterables = (list, set, tuple)


def _is_primitive(maybe_primitive: Any) -> TypeGuard[bool | float | int | str]:
    return isinstance(maybe_primitive, bool | float | int | str)


def _get_parameter_default(
    arg: pydantic.fields.FieldInfo,
) -> types.Primitive | list[types.Primitive] | None:
    resolved = arg.get_default(call_default_factory=True)

    if resolved is None or resolved == pydantic_core.PydanticUndefined:
        return None

    if isinstance(resolved, dict):
        return orjson.dumps(resolved).decode()

    if isinstance(resolved, _iterables) or sequence.is_a(resolved):
        return [
            (default if _is_primitive(default) else str(default))
            for default in resolved
        ]

    if _is_primitive(resolved):
        return resolved

    return str(resolved)
