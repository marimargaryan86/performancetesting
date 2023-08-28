import datetime
import uuid
from collections.abc import Mapping, Sequence

import click
import pydantic
import pytest

from snowfall.stdlib.integration.click import parameters


def test_json_parameter_type() -> None:
    json_type = parameters.JSONParameterType()

    assert json_type.convert('{"foo": "bar"}', None, None) == {"foo": "bar"}
    assert repr(json_type) == "JSON"


def test_json_parameter_type_invalid() -> None:
    json_type = parameters.JSONParameterType()

    with pytest.raises(click.BadParameter):
        json_type.convert("{invalid}", None, None)


class _TestCallbackModel(pydantic.BaseModel):
    no_callback: int
    no_callback_list: list[bool]
    custom_callback: str = pydantic.Field(
        json_schema_extra={"callback": lambda *args: "foobar"},
    )


@pytest.fixture()
def callback_params() -> Mapping[str, click.Parameter]:
    return {
        parameter.name or "": parameter
        for parameter in parameters.create_from_pydantic_model(_TestCallbackModel)
    }


def test_validation_with_valid_value(
    callback_params: Mapping[str, click.Parameter],
) -> None:
    assert callback_params["no_callback"].callback is not None
    assert (
        callback_params["no_callback"].callback(
            click.Context(click.Command(None)),
            callback_params["no_callback"],
            123,
        )
        == 123
    )


def test_validation_with_invalid_value(
    callback_params: Mapping[str, click.Parameter],
) -> None:
    assert callback_params["no_callback"].callback is not None

    with pytest.raises(click.BadParameter):
        callback_params["no_callback"].callback(
            click.Context(click.Command(None)),
            callback_params["no_callback"],
            "foobar",
        )


def test_validation_with_invalid_list_value(
    callback_params: Mapping[str, click.Parameter],
) -> None:
    assert callback_params["no_callback_list"].callback is not None

    with pytest.raises(click.BadParameter):
        callback_params["no_callback_list"].callback(
            click.Context(click.Command(None)),
            callback_params["no_callback_list"],
            [123],
        )


def test_custom_callback(
    callback_params: Mapping[str, click.Parameter],
) -> None:
    assert callback_params["custom_callback"].callback is not None
    assert (
        callback_params["custom_callback"].callback(
            click.Context(click.Command(None)),
            callback_params["custom_callback"],
            "bazqux",
        )
        == "foobar"
    )


def test_custom_callback_with_invalid_value(
    callback_params: Mapping[str, click.Parameter],
) -> None:
    assert callback_params["custom_callback"].callback is not None

    with pytest.raises(click.BadParameter):
        callback_params["custom_callback"].callback(
            click.Context(click.Command(None)),
            callback_params["custom_callback"],
            ["foobar"],
        )


class _TestModel(pydantic.BaseModel):
    bool_option: bool
    dict_string_string_option_default: dict[str, str] = pydantic.Field(
        default_factory=lambda: {"foo": "bar"},
    )
    dict_option_default_factory: dict[str, str] = pydantic.Field(default_factory=dict)
    float_option: float
    integer_option: int
    list_string_option_default: list[str] = pydantic.Field(
        default_factory=lambda: ["foobar"],
    )
    sequence_string_option_default: Sequence[str] = ["foobar"]
    set_string_option_default: set[str] = pydantic.Field(
        default_factory=lambda: {"foobar"},
    )
    string_argument: str = pydantic.Field(json_schema_extra={"argument": True})
    string_option: str
    string_option_default: str = "foobar"
    string_option_with_help_text: str = pydantic.Field(description="foobar")
    string_option_hidden: str = pydantic.Field(json_schema_extra={"hidden": True})
    timedelta_option_default: datetime.timedelta = datetime.timedelta(seconds=45)
    tuple_string_option_default: tuple[str] = ("foobar",)
    uuid_option_default: uuid.UUID = uuid.UUID("12345678123456781234567812345678")


def test_create_from_empty_pydantic_model() -> None:
    assert not parameters.create_from_pydantic_model(pydantic.BaseModel)


def test_create_from_pydantic_model() -> None:
    expected = sorted(
        [
            parameter.to_info_dict()
            for parameter in (
                click.Option(
                    ["--bool-option"],
                    envvar="BOOL_OPTION",
                    is_flag=True,
                    required=True,
                ),
                click.Option(
                    ["--dict-string-string-option-default"],
                    default='{"foo":"bar"}',
                    envvar="DICT_STRING_STRING_OPTION_DEFAULT",
                    required=False,
                    type=parameters.JSONParameterType(),
                ),
                click.Option(
                    ["--dict-option-default-factory"],
                    default="{}",  # noqa: P103
                    envvar="DICT_OPTION_DEFAULT_FACTORY",
                    required=False,
                    type=parameters.JSONParameterType(),
                ),
                click.Option(
                    ["--float-option"],
                    envvar="FLOAT_OPTION",
                    required=True,
                    type=float,
                ),
                click.Option(
                    ["--integer-option"],
                    envvar="INTEGER_OPTION",
                    required=True,
                    type=int,
                ),
                click.Option(
                    ["--list-string-option-default"],
                    default=["foobar"],
                    envvar="LIST_STRING_OPTION_DEFAULT",
                    multiple=True,
                    required=False,
                ),
                click.Option(
                    ["--sequence-string-option-default"],
                    default=["foobar"],
                    envvar="SEQUENCE_STRING_OPTION_DEFAULT",
                    multiple=True,
                    required=False,
                ),
                click.Option(
                    ["--set-string-option-default"],
                    default=["foobar"],
                    envvar="SET_STRING_OPTION_DEFAULT",
                    multiple=True,
                    required=False,
                ),
                click.Argument(
                    ["string-argument"],
                    envvar="STRING_ARGUMENT",
                    required=True,
                ),
                click.Option(
                    ["--string-option"],
                    envvar="STRING_OPTION",
                    required=True,
                ),
                click.Option(
                    ["--string-option-with-help-text"],
                    envvar="STRING_OPTION_WITH_HELP_TEXT",
                    help="foobar",
                    required=True,
                ),
                click.Option(
                    ["--string-option-default"],
                    default="foobar",
                    envvar="STRING_OPTION_DEFAULT",
                    required=False,
                ),
                click.Option(
                    ["--string-option-hidden"],
                    envvar="STRING_OPTION_HIDDEN",
                    hidden=True,
                    required=True,
                ),
                click.Option(
                    ["--timedelta-option-default"],
                    default="PT45S",
                    envvar="TIMEDELTA_OPTION_DEFAULT",
                    required=False,
                ),
                click.Option(
                    ["--tuple-string-option-default"],
                    default=["foobar"],
                    envvar="TUPLE_STRING_OPTION_DEFAULT",
                    multiple=True,
                    required=False,
                ),
                click.Option(
                    ["--uuid-option-default"],
                    default="12345678-1234-5678-1234-567812345678",
                    envvar="UUID_OPTION_DEFAULT",
                    required=False,
                ),
            )
        ],
        key=lambda click_param: click_param["name"],
    )

    actual = sorted(
        [
            parameter.to_info_dict()
            for parameter in parameters.create_from_pydantic_model(_TestModel)
        ],
        key=lambda click_param: click_param["name"],
    )

    assert len(expected) == len(actual)

    for idx, _ in enumerate(expected):
        assert expected[idx] == actual[idx]
