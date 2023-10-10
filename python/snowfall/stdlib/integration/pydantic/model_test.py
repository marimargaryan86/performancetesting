from collections.abc import Mapping
from typing import Any

import pydantic
import pytest

from snowfall.stdlib.integration.pydantic import model


class _TestModel(model.DefaultingBaseModel):
    default_value: str = "foo"
    union_value: str | int = 42
    none_value: str | None = pydantic.Field(alias="value", default=None)
    default_dict: dict[str, str] = pydantic.Field(default_factory=dict)
    default_list: list[str] = pydantic.Field(default_factory=list)
    none_list: list[str] | None = pydantic.Field(default_factory=list)


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {},
            {"default_value": "foo"},
        ),
        (
            {"default_value": None},
            {"default_value": "foo"},
        ),
        (
            {},
            {"union_value": 42},
        ),
        (
            {"union_value": None},
            {"union_value": 42},
        ),
        (
            {},
            {"none_value": None},
        ),
        (
            {"unknown": True},
            {"none_value": None},
        ),
        (
            {"value": None},
            {"none_value": None},
        ),
        (
            {"value": "foo"},
            {"none_value": "foo"},
        ),
        (
            {"default_dict": None},
            {"default_dict": {}},
        ),
        (
            {"default_dict": {"foo": "bar"}},
            {"default_dict": {"foo": "bar"}},
        ),
        (
            {"default_list": None},
            {"default_list": []},
        ),
        (
            {"default_list": ["foo"]},
            {"default_list": ["foo"]},
        ),
        (
            {"none_list": None},
            {"none_list": None},
        ),
    ],
)
def test_model_field_values(
    payload: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    test_model = _TestModel(**payload)
    for expected_key, expected_value in expected.items():
        assert test_model.model_dump()[expected_key] == expected_value
