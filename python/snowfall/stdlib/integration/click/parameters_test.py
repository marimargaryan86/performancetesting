import uuid
from typing import Sequence

import click
import pydantic

from snowfall.stdlib.integration.click import parameters


class _TestModel(pydantic.BaseModel):
    bool_option: bool
    dict_string_string_option_default: dict[str, str] = {"foo": "bar"}
    float_option: float
    integer_option: int
    list_string_option_default: list[str] = ["foobar"]
    sequence_string_option_default: Sequence[str] = ["foobar"]
    set_string_option_default: set[str] = {"foobar"}
    string_argument: str = pydantic.Field(argument=True)
    string_option: str
    string_option_default: str = "foobar"
    string_option_with_help_text: str = pydantic.Field(description="foobar")
    string_option_hidden: str = pydantic.Field(hidden=True)
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
                    type=parameters.JSON,
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
